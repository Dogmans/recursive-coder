"""Integration with SmolAgents CodeAgent for task decomposition and code generation."""

import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
import traceback

from recursive_agent import RecursiveAgent
import config


class RecursiveCodeAgent:
    """Wrapper integrating SmolAgents CodeAgent with RecursiveAgent."""

    def __init__(self, agent: RecursiveAgent, model: Optional[Any] = None):
        """Initialize with a RecursiveAgent instance.
        
        Args:
            agent: RecursiveAgent instance to manage
            model: Optional SmolAgents model instance to reuse for child runs
        """
        self.agent = agent
        self.model = model
        self.managed_agents: List[Any] = []
        self.managed_registry: Dict[str, Dict[str, Any]] = {}
        self.managed_agent_steps: Dict[str, List[Dict[str, Any]]] = {}

    def _resolve_managed_name(self, child_name: str) -> Optional[str]:
        import re

        if child_name in self.managed_registry:
            return child_name

        safe_name = re.sub(r"[^a-z0-9_]", "_", child_name.lower())
        child_folder_name = f"{config.CHILD_FOLDER_PREFIX}{safe_name}"
        if child_folder_name in self.managed_registry:
            return child_folder_name

        return None

    def _make_step_callback(self, managed_name: str):
        def callback(step: Any) -> None:
            entry: Dict[str, Any] = {"type": step.__class__.__name__}
            for attr in (
                "thought",
                "action",
                "code",
                "tool_name",
                "tool_call",
                "observation",
                "error",
                "result",
            ):
                if hasattr(step, attr):
                    value = getattr(step, attr)
                    if value is not None:
                        entry[attr] = str(value)[:2000]

            steps = self.managed_agent_steps.setdefault(managed_name, [])
            steps.append(entry)
            if len(steps) > 200:
                del steps[: len(steps) - 200]

        return callback

    def get_system_prompt(self) -> str:
        """Get the system prompt that guides the CodeAgent.
        
        Returns:
            System prompt for CodeAgent
        """
        return self.agent._create_system_prompt()

    def get_user_prompt(self) -> str:
        """Get the user prompt (task) for the CodeAgent.
        
        Returns:
            User prompt loaded from prompt.txt
        """
        return self.agent.load_prompt()

    def decompose_task(self, prompt: str) -> Dict[str, Any]:
        """Request task decomposition.
        
        This would be called by CodeAgent after analyzing the prompt.
        
        Args:
            prompt: The task prompt
            
        Returns:
            Decomposition strategy
        """
        return self.agent.decompose_task(prompt)

    def create_subtask(
        self,
        subtask_name: str,
        subtask_description: str,
        expected_return_type: Optional[str] = None,
        expected_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Signal creation of a subtask/child agent.
        
        This would be called by CodeAgent when it decides to decompose.
        
        Args:
            subtask_name: Name of the subtask
            subtask_description: Description of what the subtask should do
            expected_return_type: Expected return type annotation
            expected_timeout: Expected timeout for the subtask
            
        Returns:
            Information about the created child agent
        """
        child_agent = self.agent.create_child_agent(
            child_name=subtask_name,
            task_description=subtask_description,
            expected_timeout=expected_timeout,
        )

        managed_name = child_agent.agent_name.split("::")[-1]

        registry_entry = {
            "child_name": subtask_name,
            "managed_name": managed_name,
            "child_dir": str(child_agent.agent_dir),
            "prompt_file": str(child_agent.prompt_file),
            "description": None,
            "has_managed_agent": False,
            "agent": None,
        }

        if self.model is not None:
            try:
                from smolagents import CodeAgent
                from smolagents.tools import tool

                child_wrapper = RecursiveCodeAgent(child_agent, model=self.model)
                child_tools = create_codeagent_tools(child_wrapper)

                allowed_tool_names = {
                    "decompose_task",
                    "create_subtask",
                    "submit_solution",
                    "report_child_progress",
                    "merge_child_requirements",
                }

                wrapped_tools = [
                    tool(fn)
                    for name, fn in child_tools.items()
                    if name in allowed_tool_names
                ]

                description = (
                    f"Managed agent for subtask '{subtask_name}' in "
                    f"{child_agent.agent_dir}"
                )

                managed_agent = CodeAgent(
                    tools=wrapped_tools,
                    model=self.model,
                    max_steps=10,
                    verbosity_level=2,
                    name=managed_name,
                    description=description,
                    instructions=child_wrapper.get_system_prompt(),
                    step_callbacks=[self._make_step_callback(managed_name)],
                )

                self.managed_agents.append(managed_agent)
                registry_entry["description"] = description
                registry_entry["has_managed_agent"] = True
                registry_entry["agent"] = managed_agent
            except Exception as exc:
                self.agent.logger.error(
                    f"Failed to register managed agent {managed_name}: {exc}"
                )

        self.managed_registry[managed_name] = registry_entry
        
        return {
            "child_name": subtask_name,
            "child_dir": str(child_agent.agent_dir),
            "child_prompt_file": str(child_agent.prompt_file),
            "expected_return_type": expected_return_type,
            "child_ready": True,
            "managed_agent_name": managed_name,
        }

    def list_managed_agents(self) -> Dict[str, Any]:
        """List managed agents created under this parent.

        Returns:
            Registry information for managed agents
        """
        agents = []
        for managed_name, info in self.managed_registry.items():
            agents.append(
                {
                    "managed_name": managed_name,
                    "child_name": info.get("child_name"),
                    "child_dir": info.get("child_dir"),
                    "prompt_file": info.get("prompt_file"),
                    "description": info.get("description"),
                    "has_managed_agent": info.get("has_managed_agent"),
                    "steps_count": len(self.managed_agent_steps.get(managed_name, [])),
                }
            )

        return {
            "count": len(agents),
            "agents": agents,
        }

    def get_child_steps(self, child_name: str, limit: int = 50) -> Dict[str, Any]:
        """Return recent step summaries for a managed child agent.

        Args:
            child_name: Child or managed agent name
            limit: Number of recent steps to return

        Returns:
            Step summaries
        """
        managed_name = self._resolve_managed_name(child_name)
        if not managed_name:
            return {
                "success": False,
                "error": f"Managed agent {child_name} not found",
            }

        steps = self.managed_agent_steps.get(managed_name, [])
        return {
            "success": True,
            "managed_name": managed_name,
            "steps_count": len(steps),
            "steps": steps[-limit:],
        }

    def run_managed_agent(
        self,
        child_name: str,
        task: str,
        additional_args: Optional[Dict[str, Any]] = None,
        max_steps: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Run a managed child agent with a new task.

        Args:
            child_name: Child or managed agent name
            task: Task for the managed agent
            additional_args: Optional arguments to pass to the run
            max_steps: Optional override for max steps

        Returns:
            Execution result
        """
        managed_name = self._resolve_managed_name(child_name)
        if not managed_name:
            return {
                "success": False,
                "error": f"Managed agent {child_name} not found",
            }

        agent_entry = self.managed_registry.get(managed_name, {})
        managed_agent = agent_entry.get("agent")
        if managed_agent is None:
            return {
                "success": False,
                "error": f"Managed agent {managed_name} is not initialized",
            }

        child_agent = self.agent.child_agents.get(managed_name)
        prompt_text = ""
        prompt_path = agent_entry.get("prompt_file")
        if child_agent and child_agent.prompt_file.exists():
            prompt_text = child_agent.prompt_file.read_text(encoding="utf-8").strip()
        elif prompt_path:
            prompt_file = Path(prompt_path)
            if prompt_file.exists():
                prompt_text = prompt_file.read_text(encoding="utf-8").strip()

        if prompt_text and task.strip():
            full_task = prompt_text + "\n\n" + task.strip()
        else:
            full_task = prompt_text or task

        try:
            result = managed_agent.run(
                full_task,
                additional_args=additional_args,
                max_steps=max_steps,
            )
        except Exception as exc:
            self.agent.logger.error(f"Managed agent {managed_name} run failed: {exc}")
            self.agent.logger.error(
                "Managed agent run stack trace:\n" + traceback.format_exc()
            )
            return {
                "success": False,
                "error": str(exc),
            }

        solution_file = child_agent.solution_file if child_agent else None
        test_file = child_agent.test_file if child_agent else None
        if solution_file and not solution_file.exists():
            return {
                "success": False,
                "error": f"Managed agent {managed_name} did not write solution.py",
            }
        if test_file and not test_file.exists():
            return {
                "success": False,
                "error": f"Managed agent {managed_name} did not write test_solution.py",
            }

        agent_entry["last_result"] = result
        return {
            "success": True,
            "managed_name": managed_name,
            "result": result,
        }

    def reset_child_agent(
        self,
        child_name: str,
        new_prompt: str,
        expected_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Delete and recreate a child agent with a new prompt.

        Args:
            child_name: Child name to reset
            new_prompt: New prompt content for the child
            expected_timeout: Optional timeout override

        Returns:
            Reset status
        """
        import re

        safe_name = re.sub(r"[^a-z0-9_]", "_", child_name.lower())
        child_folder_name = f"{config.CHILD_FOLDER_PREFIX}{safe_name}"

        child_agent = self.agent.child_agents.get(child_folder_name)
        if child_agent:
            if child_agent.agent_dir.exists():
                shutil.rmtree(child_agent.agent_dir, ignore_errors=True)
            self.agent.child_agents.pop(child_folder_name, None)

        registry_entry = self.managed_registry.pop(child_folder_name, None)
        if registry_entry and registry_entry.get("agent") is not None:
            self.managed_agents = [
                agent
                for agent in self.managed_agents
                if agent is not registry_entry.get("agent")
            ]

        self.managed_agent_steps.pop(child_folder_name, None)

        recreated = self.create_subtask(
            subtask_name=child_name,
            subtask_description=new_prompt,
            expected_timeout=expected_timeout,
        )

        return {
            "success": True,
            "child_name": child_name,
            "managed_agent_name": recreated.get("managed_agent_name"),
            "child_dir": recreated.get("child_dir"),
            "prompt_file": recreated.get("child_prompt_file"),
        }

    def submit_solution(self, code: str, test_code: Optional[str] = None) -> Dict[str, Any]:
        """Submit and validate the generated solution code.
        
        Args:
            code: The solution.py code to save and validate
            test_code: Optional test_solution.py code
            
        Returns:
            Results of validation
        """
        try:
            # Save solution
            with open(self.agent.solution_file, "w", encoding="utf-8") as f:
                f.write(code)
            self.agent.logger.info("Saved solution.py")
            
            # Save tests if provided
            if test_code:
                with open(self.agent.test_file, "w", encoding="utf-8") as f:
                    f.write(test_code)
                self.agent.logger.info("Saved test_solution.py")
            
            # Run tests
            test_results = self.agent.run_tests()
            
            if test_results["success"]:
                self.agent.logger.info("Solution validated successfully")
                return {
                    "success": True,
                    "message": "Solution saved and validated",
                    "test_results": test_results,
                }
            else:
                self.agent.logger.error("Solution validation failed")
                return {
                    "success": False,
                    "message": "Solution failed validation",
                    "test_results": test_results,
                }
        except Exception as e:
            self.agent.logger.error(f"Error submitting solution: {str(e)}")
            return {
                "success": False,
                "message": f"Error saving solution: {str(e)}",
                "error": str(e),
            }

    def report_child_progress(self, child_name: str) -> Dict[str, Any]:
        """Check progress and status of a child agent.
        
        Args:
            child_name: Name of the child folder
            
        Returns:
            Status information
        """
        import re
        safe_name = re.sub(r"[^a-z0-9_]", "_", child_name.lower())
        child_folder_name = f"{config.CHILD_FOLDER_PREFIX}{safe_name}"
        
        if child_folder_name not in self.agent.child_agents:
            return {
                "status": "not_found",
                "error": f"Child agent {child_name} not found",
            }
        
        child_agent = self.agent.child_agents[child_folder_name]
        
        return {
            "status": "exists",
            "child_dir": str(child_agent.agent_dir),
            "solution_exists": child_agent.solution_file.exists(),
            "tests_exist": child_agent.test_file.exists(),
            "has_errors": child_agent.logger.error_file.exists()
            and len(child_agent.logger.get_error_summary()) > 0,
            "error_summary": child_agent.logger.get_error_summary()[:500],
            "log_summary": child_agent.logger.get_log_summary()[-500:],
        }

    def merge_child_requirements(self, include_self: bool = True) -> Dict[str, Any]:
        """Merge child requirements into this agent's requirements.txt.

        Args:
            include_self: Whether to include existing parent requirements.txt

        Returns:
            Merge results
        """
        merged = self.agent.merge_child_requirements(include_self=include_self)
        return {
            "merged_count": len(merged),
            "requirements": merged,
            "requirements_file": str(self.agent.requirements_file),
        }


def create_codeagent_tools(recursive_code_agent: RecursiveCodeAgent) -> Dict[str, Callable]:
    """Create tool functions for SmolAgents CodeAgent.
    
    These tools expose RecursiveCodeAgent methods to the CodeAgent.
    
    Args:
        recursive_code_agent: RecursiveCodeAgent instance
        
    Returns:
        Dictionary of tool functions
    """
    return {
        "decompose_task": recursive_code_agent.decompose_task,
        "create_subtask": recursive_code_agent.create_subtask,
        "submit_solution": recursive_code_agent.submit_solution,
        "list_managed_agents": recursive_code_agent.list_managed_agents,
        "get_child_steps": recursive_code_agent.get_child_steps,
        "run_managed_agent": recursive_code_agent.run_managed_agent,
        "reset_child_agent": recursive_code_agent.reset_child_agent,
        "report_child_progress": recursive_code_agent.report_child_progress,
        "merge_child_requirements": recursive_code_agent.merge_child_requirements,
    }
