"""Run the RecursiveCodeAgent with smolagents CodeAgent."""

import os
import sys
from pathlib import Path

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
        timeout_seconds=config.DEFAULT_TIMEOUT,
        max_retries=config.DEFAULT_MAX_RETRIES,
    )

    wrapper = RecursiveCodeAgent(agent)
    tools = create_codeagent_tools(wrapper)

    # Add web search tool for external info
    smol_tools = [DuckDuckGoSearchTool()]

    # Wrap local callables into SmolAgents Tool objects
    # Exclude tools with varargs that lack type hints for smolagents
    allowed_tool_names = {
        "decompose_task",
        "create_subtask",
        "submit_solution",
        "get_child_solution",
        "get_child_info",
        "report_child_progress",
        "merge_child_requirements",
    }

    wrapped_tools = [tool(fn) for name, fn in tools.items() if name in allowed_tool_names]

    # Load environment variables from .env if present
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass

    # Model selection
    run_local = os.getenv("SMOL_RUN_LOCAL", "false").strip().lower() in {"1", "true", "yes"}
    model_id = os.getenv("SMOL_MODEL_ID")

    if run_local:
        if not model_id:
            model_id = "mistralai/Mistral-7B-Instruct-v0.1"
        try:
            # Use custom direct Transformers model to bypass SmolAgents auto-detection issues
            from custom_model import DirectTransformersModel
            model = DirectTransformersModel(model_id=model_id, quantize=False)  # Disable quantization for now
        except Exception as e:
            print(f"Local model load failed: {e}")
            print("Falling back to hosted model. Set HF_TOKEN to use hosted inference.")
            return 1
    else:
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not hf_token:
            print(
                "Missing Hugging Face token. Set HF_TOKEN or HUGGINGFACEHUB_API_TOKEN "
                "(or run `hf auth login`) before running."
            )
            return 1
        if model_id:
            model = InferenceClientModel(model_id=model_id, token=hf_token)
        else:
            model = InferenceClientModel(token=hf_token)

    code_agent = CodeAgent(
        tools=[*smol_tools, *wrapped_tools],
        model=model,
    )

    prompt = wrapper.get_user_prompt()
    directive = (
        "\n\nYou must generate code for this task and call the tool "
        "`submit_solution(code, test_code)` to write solution.py and test_solution.py "
        "in your agent folder. Use requirements.txt for any non-stdlib deps."
    )
    result = code_agent.run(prompt + directive)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
