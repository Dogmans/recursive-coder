# AGENTS.md — Recursive Code Agent

## What This Project Does
Prompt-driven recursive code agent using SmolAgents CodeAgent. A thin launcher loads a system prompt and task, then the agent self-scaffolds everything: writes code, runs tests, creates subfolders, spawns child agents.

## Dev Environment
- Runtime: Python 3.10+
- Package manager: pip
- Setup: `pip install -e .[smol]`

## Commands
| Action  | Command                    |
|---------|----------------------------|
| Install | `pip install -e .[smol]`   |
| Run     | `python run.py`            |
| Lint    | `ruff check .`             |
| Format  | `black .`                  |

## Project Structure
```
run.py              # Thin launcher — creates CodeAgent, loads prompt, runs
prompt.md           # System prompt — output conventions, testing, decomposition, retry
config.py           # Minimal config — model ID, paths, env vars
custom_model.py     # Local HuggingFace model wrapper (DirectTransformersModel)
_reference/         # Grounding docs auto-loaded into agent context
  smolagents-api.md # SmolAgents CodeAgent API reference
agents/root/        # Agent working directory
  prompt.txt        # User's task description
pyproject.toml      # Dependencies and tool config
.env.example        # Environment variable template
```

## Architecture
| Component | File | Role |
|-----------|------|------|
| Launcher | `run.py` | Creates CodeAgent, loads prompt.md + _reference/*.md + task, calls `.run()` |
| System prompt | `prompt.md` | Tells agent how to structure output, test, decompose, retry, log |
| Reference docs | `_reference/*.md` | API docs and conventions injected into agent context |
| Model wrapper | `custom_model.py` | Local HuggingFace model with quantization support |
| Config | `config.py` | Model ID, paths — all overridable via env vars |

## Code Style
- Python 3.10+ with type hints on all functions
- Google-style docstrings
- `black` formatting, `ruff` linting
- 100 char line length

## Testing
The agent writes and runs its own tests (pytest) as part of execution. There are no framework-level tests — the agent IS the test runner.

## Pitfalls
- `agents/root/prompt.txt` must exist before running — the launcher won't prompt interactively
- `custom_model.py` requires `torch` and `transformers` — install via `pip install -e .[smol]`
- The agent's working directory is `agents/root/` — it writes files relative to there
- Reference docs must be `.md` files in `_reference/` to be auto-loaded
