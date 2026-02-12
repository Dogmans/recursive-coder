"""Minimal configuration — model and paths only.

Everything else is handled by the agent via the system prompt (prompt.md).
"""

import os
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(__file__).parent
AGENTS_DIR = WORKSPACE_ROOT / "agents"
REFERENCE_DIR = WORKSPACE_ROOT / "_reference"
PROMPT_FILE = WORKSPACE_ROOT / "prompt.md"

# Model (overridable via environment)
MODEL_ID = os.getenv("SMOL_MODEL_ID", "microsoft/phi-3-mini-4k-instruct")
QUANTIZE = os.getenv("SMOL_QUANTIZE", "true").lower() in {"1", "true", "yes"}
MAX_STEPS = int(os.getenv("SMOL_MAX_STEPS", "30"))
