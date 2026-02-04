"""Integration with SmolAgents CodeAgent for task decomposition and code generation."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import textwrap

from recursive_agent import RecursiveAgent
import config


class RecursiveCodeAgent:
    """Wrapper integrating SmolAgents CodeAgent with RecursiveAgent."""

    def __init__(self, agent: RecursiveAgent):
        """Initialize with a RecursiveAgent instance.
        
        Args:
            agent: RecursiveAgent instance to manage
        """
        self.agent = agent

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
        
        return {
            "child_name": subtask_name,
            "child_dir": str(child_agent.agent_dir),
            "child_prompt_file": str(child_agent.prompt_file),
            "expected_return_type": expected_return_type,
            "child_ready": True,
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

    def get_child_solution(self, child_name: str) -> Optional[Any]:
        """Get and import a child agent's solution module.
        
        Args:
            child_name: Name of the child folder
            
        Returns:
            Imported module or None
        """
        # Sanitize the name to match what was created
        import re
        safe_name = re.sub(r"[^a-z0-9_]", "_", child_name.lower())
        child_folder_name = f"{config.CHILD_FOLDER_PREFIX}{safe_name}"
        
        return self.agent.import_child_solution(child_folder_name)

    def get_child_info(self, child_name: str) -> Dict[str, Any]:
        """Get detailed information about a child's solution.
        
        Args:
            child_name: Name of the child folder
            
        Returns:
            Function signatures and docstrings
        """
        import re
        safe_name = re.sub(r"[^a-z0-9_]", "_", child_name.lower())
        child_folder_name = f"{config.CHILD_FOLDER_PREFIX}{safe_name}"
        
        return self.agent.get_child_function_info(child_folder_name)

    def execute_child_function(
        self,
        child_name: str,
        function_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a function from a child agent's solution.
        
        Args:
            child_name: Name of the child folder
            function_name: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Execution results
        """
        try:
            module = self.get_child_solution(child_name)
            if module is None:
                return {
                    "success": False,
                    "error": f"Could not import child solution for {child_name}",
                }
            
            func = getattr(module, function_name, None)
            if func is None:
                return {
                    "success": False,
                    "error": f"Function {function_name} not found in {child_name}",
                }
            
            result = func(*args, **kwargs)
            
            self.agent.logger.info(
                f"Successfully executed {child_name}.{function_name}"
            )
            
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            self.agent.logger.error(
                f"Error executing child function: {str(e)}"
            )
            return {
                "success": False,
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
        "get_child_solution": recursive_code_agent.get_child_solution,
        "get_child_info": recursive_code_agent.get_child_info,
        "execute_child_function": recursive_code_agent.execute_child_function,
        "report_child_progress": recursive_code_agent.report_child_progress,
        "merge_child_requirements": recursive_code_agent.merge_child_requirements,
    }
