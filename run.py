"""Thin launcher for the recursive code agent.

Creates a CodeAgent, loads the prompt, and runs it.
The agent self-scaffolds everything else.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding for Rich/smolagents Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from dotenv import load_dotenv

load_dotenv()


def _load_model():
    """Load the model based on SMOL_PROVIDER setting.

    Supported providers (set via SMOL_PROVIDER env var):
        github      – GitHub Models (OpenAI-compatible, needs GITHUB_TOKEN)
        huggingface – HF Inference API (needs HF_TOKEN)
        openai      – OpenAI API (needs OPENAI_API_KEY)
        local       – Local HuggingFace model on GPU/CPU

    Returns:
        (model, model_id) tuple for CodeAgent.
    """
    from config import PROVIDER, MODEL_ID, API_BASE, API_TOKEN, QUANTIZE

    if PROVIDER == "local":
        from custom_model import DirectTransformersModel

        print(f"Loading local model: {MODEL_ID} (quantize={QUANTIZE})")
        return DirectTransformersModel(model_id=MODEL_ID, quantize=QUANTIZE), MODEL_ID

    if PROVIDER == "huggingface":
        from smolagents import InferenceClientModel

        if not API_TOKEN:
            print("HF_TOKEN not set. Get a free token at https://huggingface.co/settings/tokens")
            print("Add to .env:  HF_TOKEN=hf_...")
            sys.exit(1)

        print(f"Using HF Inference API: {MODEL_ID}")
        return InferenceClientModel(model_id=MODEL_ID, token=API_TOKEN), MODEL_ID

    # github / openai / any OpenAI-compatible endpoint
    if PROVIDER in {"github", "openai"}:
        from smolagents import OpenAIServerModel

        if not API_TOKEN:
            token_var = "GITHUB_TOKEN" if PROVIDER == "github" else "OPENAI_API_KEY"
            print(f"{token_var} not set. Add it to your .env file.")
            sys.exit(1)

        base = API_BASE or (
            "https://models.inference.ai.azure.com"
            if PROVIDER == "github"
            else "https://api.openai.com/v1"
        )
        print(f"Using {PROVIDER} endpoint: {base}")
        print(f"Model: {MODEL_ID}")
        return (
            OpenAIServerModel(model_id=MODEL_ID, api_base=base, api_key=API_TOKEN),
            MODEL_ID,
        )

    print(f"Unknown provider '{PROVIDER}'. Use one of: github, huggingface, openai, local")
    sys.exit(1)


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
