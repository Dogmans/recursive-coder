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

# ── Provider configuration ──────────────────────────────────────────
# Supported providers: "github", "huggingface", "openai", "local"
PROVIDER = os.getenv("SMOL_PROVIDER", "huggingface").strip().lower()

# Model ID — meaning depends on provider (see .env.example)
MODEL_ID = os.getenv("SMOL_MODEL_ID", "Qwen/Qwen2.5-Coder-32B-Instruct")

# Provider-specific defaults
PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "github": {
        "api_base": "https://models.inference.ai.azure.com",
        "token_env": "GITHUB_TOKEN",
        "default_model": "gpt-4o",
    },
    "huggingface": {
        "api_base": "",  # uses InferenceClientModel (no base URL needed)
        "token_env": "HF_TOKEN",
        "default_model": "Qwen/Qwen2.5-Coder-32B-Instruct",
    },
    "openai": {
        "api_base": "https://api.openai.com/v1",
        "token_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
    "local": {
        "api_base": "",
        "token_env": "",
        "default_model": "microsoft/phi-3-mini-4k-instruct",
    },
}

# Resolved values
_defaults = PROVIDER_DEFAULTS.get(PROVIDER, PROVIDER_DEFAULTS["huggingface"])
API_BASE = os.getenv("SMOL_API_BASE", _defaults["api_base"])
API_TOKEN = os.getenv(_defaults["token_env"], "") if _defaults["token_env"] else ""
if not MODEL_ID or MODEL_ID == "Qwen/Qwen2.5-Coder-32B-Instruct":
    # Only override with provider default when the user hasn't explicitly set one
    MODEL_ID = os.getenv("SMOL_MODEL_ID", _defaults["default_model"])

# Agent behaviour
MAX_STEPS = int(os.getenv("SMOL_MAX_STEPS", "30"))
QUANTIZE = os.getenv("SMOL_QUANTIZE", "true").lower() in {"1", "true", "yes"}
