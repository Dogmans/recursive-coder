"""Example usage of the recursive code agent."""

import sys
from pathlib import Path
from recursive_agent import RecursiveAgent
from code_agent_integration import RecursiveCodeAgent, create_codeagent_tools
import config


def main():
    """Main entry point for the recursive agent."""
    
    # Create top-level agent
    agent_dir = config.AGENTS_DIR / "root"
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    agent = RecursiveAgent(
        agent_dir=agent_dir,
        agent_name="RootAgent",
        timeout_seconds=config.DEFAULT_TIMEOUT,
        max_retries=config.DEFAULT_MAX_RETRIES,
    )
    
    # Create CodeAgent integration
    code_agent_wrapper = RecursiveCodeAgent(agent)
    
    # Execute the agent
    result = agent.execute()
    
    if result["success"]:
        print(f"\n{'='*60}")
        print(f"Agent initialized successfully")
        print(f"{'='*60}")
        print(f"Working directory: {agent_dir}")
        print(f"Prompt file: {agent.prompt_file}")
        print(f"Solution file: {agent.solution_file}")
        print(f"\nSystem Prompt:\n{'-'*60}")
        print(result["system_prompt"])
        print(f"{'-'*60}\n")
        print(f"Agent is ready for CodeAgent integration.")
        print(f"Use the provided tools in code_agent_integration.py")
        print(f"Available tools:")
        tools = create_codeagent_tools(code_agent_wrapper)
        for tool_name in tools:
            print(f"  - {tool_name}")
        
        return 0
    else:
        print(f"Error initializing agent: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
