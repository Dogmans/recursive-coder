"""Run the RecursiveCodeAgent with smolagents CodeAgent."""

import os
import signal
import sys
import traceback

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

import config
from recursive_agent import RecursiveAgent
from code_agent_integration import RecursiveCodeAgent, create_codeagent_tools


def main() -> int:
    """Run CodeAgent using the prompt in agents/root/prompt.txt."""
    try:
        from smolagents import CodeAgent, InferenceClientModel, DuckDuckGoSearchTool
        from smolagents.tools import tool
    except Exception as exc:
        print(
            "smolagents is not installed. Install with: "
            "pip install -e .[smol]"
        )
        print(f"Import error: {exc}")
        return 1

    # Create root agent
    agent_dir = config.AGENTS_DIR / "root"
    agent_dir.mkdir(parents=True, exist_ok=True)

    agent = RecursiveAgent(
        agent_dir=agent_dir,
        agent_name="RootAgent",
        timeout_seconds=1800,  # Increased to 30 minutes for slow model inference
        max_retries=config.DEFAULT_MAX_RETRIES,
    )

    def handle_sigint(signum, frame) -> None:
        agent.logger.error(f"Received SIGINT (signal {signum}).")

    signal.signal(signal.SIGINT, handle_sigint)

    # Add web search tool for external info
    smol_tools = [DuckDuckGoSearchTool()]

    # Wrap local callables into SmolAgents Tool objects
    # Exclude tools with varargs that lack type hints for smolagents
    allowed_tool_names = {
        "decompose_task",
        "create_subtask",
        "submit_solution",
        "list_managed_agents",
        "get_child_steps",
        "run_managed_agent",
        "reset_child_agent",
        "get_child_diagnostics",
        "retry_child_agent",
        "report_child_progress",
        "merge_child_requirements",
    }

    # Load environment variables from .env if present
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass

    # Model selection - use local model with GPU+CPU split
    run_local = os.getenv("SMOL_RUN_LOCAL", "true").strip().lower() in {"1", "true", "yes"}
    model_id = os.getenv("SMOL_MODEL_ID")

    if not model_id:
        model_id = "microsoft/phi-3-mini-4k-instruct"
    
    try:
        from custom_model import DirectTransformersModel
        model = DirectTransformersModel(model_id=model_id, quantize=True)
    except Exception as e:
        print(f"Local model load failed: {e}")
        return 1

    wrapper = RecursiveCodeAgent(agent, model=model)
    tools = create_codeagent_tools(wrapper)
    wrapped_tools = [tool(fn) for name, fn in tools.items() if name in allowed_tool_names]

    code_agent = CodeAgent(
        tools=[*smol_tools, *wrapped_tools],
        model=model,
        max_steps=10,
        verbosity_level=2,  # Show step-by-step progress
        managed_agents=wrapper.managed_agents,
    )
    
    # Add system prompt to the initial message
    system_prompt = wrapper.get_system_prompt()

    prompt = wrapper.get_user_prompt()
    directive = (
        "\n\nYou must generate code for this task and call the tool "
        "`submit_solution(code, test_code)` to write solution.py and test_solution.py "
        "in your agent folder. Use requirements.txt for any non-stdlib deps."
    )
    
    print("\n" + "="*70)
    print("STARTING CODE AGENT")
    print("="*70)
    print(f"Prompt: {prompt[:100]}...")
    print("="*70 + "\n")

    full_prompt = system_prompt + "\n\n" + prompt + directive
    result = code_agent.run(full_prompt)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
