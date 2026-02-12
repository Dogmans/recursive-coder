"""Thin launcher for the recursive code agent.

Creates a CodeAgent, loads the prompt, and runs it.
The agent self-scaffolds everything else.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _load_model():
    """Load the model — API by default, local if SMOL_RUN_LOCAL=true."""
    model_id = os.getenv("SMOL_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct")
    run_local = os.getenv("SMOL_RUN_LOCAL", "false").strip().lower() in {"1", "true", "yes"}

    if run_local:
        from custom_model import DirectTransformersModel

        quantize = os.getenv("SMOL_QUANTIZE", "true").lower() in {"1", "true", "yes"}
        print(f"Loading local model: {model_id} (quantize={quantize})")
        return DirectTransformersModel(model_id=model_id, quantize=quantize), model_id

    # Default: HF Inference API (free tier, needs HF_TOKEN)
    from smolagents import InferenceClientModel

    token = os.getenv("HF_TOKEN")
    if not token:
        print("HF_TOKEN not set. Get a free token at https://huggingface.co/settings/tokens")
        print("Add to .env:  HF_TOKEN=hf_...")
        sys.exit(1)

    print(f"Using HF Inference API: {model_id}")
    return InferenceClientModel(model_id=model_id, token=token), model_id


def main() -> int:
    """Launch the CodeAgent with the system prompt and task."""

    try:
        from smolagents import CodeAgent, DuckDuckGoSearchTool
    except ImportError:
        print("smolagents not installed. Run: pip install -e .[smol]")
        return 1

    # --- Resolve paths ---
    root = Path(__file__).parent
    agents_dir = root / "agents" / "root"
    agents_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = agents_dir / "prompt.txt"
    if not prompt_file.exists():
        print(f"No task found. Create {prompt_file} with your task description.")
        return 1

    task = prompt_file.read_text(encoding="utf-8").strip()
    system_prompt = (root / "prompt.md").read_text(encoding="utf-8").strip()

    # --- Load reference docs into context (if they exist) ---
    reference_dir = root / "_reference"
    reference_context = ""
    if reference_dir.is_dir():
        for ref_file in sorted(reference_dir.glob("*.md")):
            reference_context += f"\n\n---\n## Reference: {ref_file.stem}\n\n"
            reference_context += ref_file.read_text(encoding="utf-8").strip()

    # --- Model setup ---
    try:
        model, model_id = _load_model()
    except Exception as exc:
        print(f"Model load failed: {exc}")
        return 1

    # --- Build and run agent ---
    full_prompt = f"{system_prompt}{reference_context}\n\n---\n## Your Task\n\n{task}"

    agent = CodeAgent(
        tools=[DuckDuckGoSearchTool()],
        model=model,
        max_steps=int(os.getenv("SMOL_MAX_STEPS", "30")),
        verbosity_level=2,
        additional_authorized_imports=[
            "subprocess", "pathlib", "json", "importlib",
            "inspect", "datetime", "re", "os", "sys",
            "requests", "urllib", "http", "io",
        ],
    )

    print("\n" + "=" * 70)
    print("STARTING CODE AGENT")
    print("=" * 70)
    print(f"Model : {model_id}")
    print(f"Task  : {task[:120]}...")
    print(f"Workdir: {agents_dir}")
    print("=" * 70 + "\n")

    result = agent.run(full_prompt)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
