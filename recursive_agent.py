"""Recursive code agent using SmolAgents CodeAgent."""

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from logger import AgentLogger
import config


class RecursiveAgent:
    """A recursive agent that decomposes tasks and spawns child agents."""

    def __init__(
        self,
        agent_dir: Path,
        agent_name: str = "RecursiveAgent",
        timeout_seconds: int = config.DEFAULT_TIMEOUT,
        max_retries: int = config.DEFAULT_MAX_RETRIES,
        recursion_depth: int = 0,
        max_recursion_depth: int = config.DEFAULT_RECURSION_DEPTH,
    ):
        """Initialize the recursive agent.
        
        Args:
            agent_dir: Working directory for this agent
            agent_name: Name for logging purposes
            timeout_seconds: Timeout for code execution
            max_retries: Maximum retry attempts for code generation
            recursion_depth: Current recursion depth
            max_recursion_depth: Maximum recursion depth allowed
        """
        self.agent_dir = Path(agent_dir)
        self.agent_name = agent_name
        self.timeout_seconds = max(
            config.MIN_TIMEOUT,
            min(timeout_seconds, config.MAX_TIMEOUT)
        )
        self.max_retries = max_retries
        self.recursion_depth = recursion_depth
        self.max_recursion_depth = max_recursion_depth
        
        self.prompt_file = self.agent_dir / config.PROMPT_FILE
        self.solution_file = self.agent_dir / config.SOLUTION_FILE
        self.test_file = self.agent_dir / "test_solution.py"
        self.requirements_file = self.agent_dir / config.REQUIREMENTS_FILE
        
        self.logger = AgentLogger(self.agent_dir, agent_name)
        self.child_agents: Dict[str, RecursiveAgent] = {}
        
        self.logger.info(f"Initialized {agent_name} at {agent_dir}")

    def load_prompt(self) -> str:
        """Load the prompt from prompt.txt. If not found, prompt user to create it.
        
        Returns:
            The prompt text
        """
        if self.prompt_file.exists():
            with open(self.prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read().strip()
            self.logger.info(f"Loaded prompt from {self.prompt_file}")
            return prompt
        else:
            self.logger.info(f"No prompt.txt found at {self.agent_dir}")
            print(f"\n{'='*60}")
            print(f"Agent: {self.agent_name}")
            print(f"Location: {self.agent_dir}")
            print(f"{'='*60}")
            print("No prompt.txt found. Please enter the task/prompt for this agent:")
            print("(Enter multiple lines. Type 'END' on a new line to finish)\n")
            
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            
            prompt = "\n".join(lines).strip()
            
            # Save prompt
            self.prompt_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt)
            
            self.logger.info(f"Created prompt.txt with user input")
            return prompt

    def decompose_task(self, prompt: str) -> Dict[str, Any]:
        """Decompose the task into subtasks.
        
        This should be called via CodeAgent to decompose the prompt.
        For now, returns a structure indicating whether to proceed or decompose.
        
        Args:
            prompt: The task prompt to decompose
            
        Returns:
            Dictionary with decomposition strategy
        """
        self.logger.info(f"Analyzing task complexity and decomposition strategy")
        
        # Placeholder - actual decomposition happens via CodeAgent
        return {
            "prompt": prompt,
            "recursion_depth": self.recursion_depth,
            "should_decompose": self.recursion_depth < self.max_recursion_depth,
            "timeout_for_children": max(
                self.timeout_seconds // 2,
                config.MIN_TIMEOUT
            ),
        }

    def _create_system_prompt(self) -> str:
        """Create the system prompt for this agent.
        
        Returns:
            System prompt with agent-specific settings
        """
        return config.SYSTEM_PROMPT_TEMPLATE.format(
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            recursion_depth=self.recursion_depth,
            CHILD_FOLDER_PREFIX=config.CHILD_FOLDER_PREFIX,
        )

    def create_child_agent(
        self,
        child_name: str,
        task_description: str,
        expected_timeout: Optional[int] = None,
    ) -> "RecursiveAgent":
        """Create a child agent for a subtask.
        
        Args:
            child_name: Descriptive name for the subtask (will be prefixed)
            task_description: Task description to go in child's prompt.txt
            expected_timeout: Timeout for child execution
            
        Returns:
            The created child agent
        """
        # Sanitize child name
        safe_name = re.sub(r"[^a-z0-9_]", "_", child_name.lower())
        child_folder_name = f"{config.CHILD_FOLDER_PREFIX}{safe_name}"
        child_dir = self.agent_dir / child_folder_name
        child_dir.mkdir(parents=True, exist_ok=True)
        
        # Create child prompt
        child_timeout = expected_timeout or max(
            self.timeout_seconds // 2,
            config.MIN_TIMEOUT
        )
        
        child_prompt = f"""Task: {task_description}

## Instructions:
- This is a subtask of a larger decomposition
- Your generated code will be called by the parent agent
- Ensure all functions have complete type hints and docstrings
- Write tests in test_solution.py using pytest
    - If you use non-stdlib dependencies, list them in requirements.txt (one per line)
- Log all activity to log.txt and errors to error.txt
- If this task needs further decomposition, create child agents in {config.CHILD_FOLDER_PREFIX}<name>/ folders

## Parent Context:
- Parent task is at: {self.agent_dir}
- Your task should integrate with parent's code
- Return types must be explicitly documented
"""
        
        # Save child prompt
        child_prompt_file = child_dir / config.PROMPT_FILE
        with open(child_prompt_file, "w", encoding="utf-8") as f:
            f.write(child_prompt)
        
        # Create child agent
        child_agent = RecursiveAgent(
            agent_dir=child_dir,
            agent_name=f"{self.agent_name}::{child_folder_name}",
            timeout_seconds=child_timeout,
            max_retries=self.max_retries,
            recursion_depth=self.recursion_depth + 1,
            max_recursion_depth=self.max_recursion_depth,
        )
        
        self.child_agents[child_folder_name] = child_agent
        self.logger.info(
            f"Created child agent: {child_folder_name} "
            f"(timeout: {child_timeout}s, depth: {self.recursion_depth + 1})"
        )
        
        return child_agent

    def _read_requirements_file(self, file_path: Path) -> List[str]:
        """Read a requirements.txt file and return cleaned lines.

        Args:
            file_path: Path to requirements.txt

        Returns:
            List of requirement lines
        """
        if not file_path.exists():
            return []

        requirements = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                requirements.append(stripped)

        return requirements

    def collect_child_requirements(self) -> List[str]:
        """Collect requirements from all child agent folders under this agent.

        Returns:
            List of unique requirement lines
        """
        requirements: List[str] = []
        seen = set()

        if not self.agent_dir.exists():
            return requirements

        for child_dir in self.agent_dir.iterdir():
            if not child_dir.is_dir():
                continue

            req_file = child_dir / config.REQUIREMENTS_FILE
            for req in self._read_requirements_file(req_file):
                if req not in seen:
                    seen.add(req)
                    requirements.append(req)

        return requirements

    def merge_child_requirements(self, include_self: bool = True) -> List[str]:
        """Merge child requirements into this agent's requirements.txt.

        Args:
            include_self: Include existing requirements.txt in this agent

        Returns:
            The merged list of requirements
        """
        merged: List[str] = []
        seen = set()

        if include_self:
            for req in self._read_requirements_file(self.requirements_file):
                if req not in seen:
                    seen.add(req)
                    merged.append(req)

        for req in self.collect_child_requirements():
            if req not in seen:
                seen.add(req)
                merged.append(req)

        if merged:
            with open(self.requirements_file, "w", encoding="utf-8") as f:
                f.write("\n".join(merged) + "\n")
            self.logger.info(
                f"Merged {len(merged)} requirements into {self.requirements_file}"
            )
        else:
            self.logger.info("No child requirements found to merge")

        return merged

    def run_code_with_timeout(self, code: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute Python code with timeout protection.
        
        Args:
            code: Python code to execute
            timeout: Timeout in seconds (defaults to self.timeout_seconds)
            
        Returns:
            Dictionary with execution results
        """
        timeout = timeout or self.timeout_seconds
        
        try:
            # Write code to temporary file
            temp_script = self.agent_dir / "_temp_exec.py"
            with open(temp_script, "w", encoding="utf-8") as f:
                f.write(code)
            
            self.logger.debug(f"Executing code with {timeout}s timeout")
            
            # Execute with timeout
            result = subprocess.run(
                [sys.executable, str(temp_script)],
                cwd=str(self.agent_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            # Clean up
            temp_script.unlink()
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            self.logger.error(f"Code execution timed out after {timeout}s")
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "returncode": -1,
            }
        except Exception as e:
            self.logger.error(f"Error executing code: {str(e)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def run_tests(self) -> Dict[str, Any]:
        """Run pytest on test_solution.py.
        
        Returns:
            Dictionary with test results
        """
        if not self.test_file.exists():
            self.logger.warning("No test_solution.py found, skipping tests")
            return {
                "success": True,
                "tests_found": False,
                "message": "No test file found",
            }
        
        self.logger.info("Running pytest on test_solution.py")
        
        try:
            import importlib.util

            pytest_args = [
                sys.executable,
                "-m",
                "pytest",
                str(self.test_file),
                "-v",
                f"--timeout={config.PYTEST_TIMEOUT}",
                "--tb=short",
            ]

            if importlib.util.find_spec("pytest_jsonreport") is not None:
                pytest_args.extend(
                    [
                        "--json-report",
                        f"--json-report-file={self.agent_dir / 'pytest_report.json'}",
                    ]
                )

            result = subprocess.run(
                pytest_args,
                cwd=str(self.agent_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            
            success = result.returncode == 0
            
            if success:
                self.logger.info("All tests passed")
            else:
                self.logger.error(f"Tests failed with return code {result.returncode}")
                self.logger.error(f"Test output:\n{result.stdout}\n{result.stderr}")
            
            return {
                "success": success,
                "tests_found": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            self.logger.error(f"Testing timed out after {self.timeout_seconds}s")
            return {
                "success": False,
                "tests_found": True,
                "message": "Testing timed out",
                "stderr": "Pytest timed out",
            }
        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return {
                "success": False,
                "tests_found": True,
                "message": f"Error running tests: {str(e)}",
                "stderr": str(e),
            }

    def execute(self) -> Dict[str, Any]:
        """Main execution method for the agent.
        
        This loads the prompt, and would typically orchestrate the CodeAgent
        for task decomposition and code generation.
        
        Returns:
            Execution results
        """
        self.logger.info(f"Starting agent execution (depth: {self.recursion_depth})")
        
        try:
            # Load prompt
            prompt = self.load_prompt()
            
            # Log prompt
            self.logger.info(f"Processing prompt: {prompt[:100]}...")
            
            # Create system prompt
            system_prompt = self._create_system_prompt()
            
            return {
                "success": True,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "agent_dir": str(self.agent_dir),
                "recursion_depth": self.recursion_depth,
                "message": "Agent ready for CodeAgent integration",
            }
        except Exception as e:
            self.logger.critical(f"Unexpected error in execute: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }

    def import_child_solution(self, child_folder_name: str):
        """Import and return a child agent's solution module.
        
        Args:
            child_folder_name: Name of child folder
            
        Returns:
            Imported module or None if import failed
        """
        if child_folder_name not in self.child_agents:
            self.logger.error(f"Child agent '{child_folder_name}' not found")
            return None
        
        child_agent = self.child_agents[child_folder_name]
        
        # Check if solution exists
        if not child_agent.solution_file.exists():
            self.logger.error(f"Solution file not found for {child_folder_name}")
            return None
        
        # Check for errors
        error_summary = child_agent.logger.get_error_summary()
        if error_summary:
            self.logger.warning(
                f"Child {child_folder_name} had errors:\n{error_summary}"
            )
        
        # Import the solution module
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"{self.agent_name}_{child_folder_name}",
                child_agent.solution_file,
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.logger.info(f"Successfully imported solution from {child_folder_name}")
            return module
        except Exception as e:
            self.logger.error(f"Failed to import child solution: {str(e)}")
            return None

    def get_child_function_info(self, child_folder_name: str) -> Dict[str, Any]:
        """Get information about functions in a child's solution.
        
        Args:
            child_folder_name: Name of child folder
            
        Returns:
            Dictionary with function signatures and docstrings
        """
        module = self.import_child_solution(child_folder_name)
        if module is None:
            return {}
        
        import inspect
        
        functions = {}
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith("_"):
                sig = inspect.signature(obj)
                doc = inspect.getdoc(obj) or "No documentation"
                
                functions[name] = {
                    "signature": str(sig),
                    "docstring": doc,
                    "annotations": dict(obj.__annotations__),
                }
        
        return functions
