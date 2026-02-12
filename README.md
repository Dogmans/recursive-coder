# Recursive Code Agent

A prompt-driven recursive code agent powered by SmolAgents CodeAgent. Give it a task, and it decomposes, codes, tests, and self-corrects — with minimal scaffolding.

## Philosophy

The model is the engine. The code is just a bootstrap. The agent:
- Reads a system prompt ([prompt.md](prompt.md)) that describes conventions and strategies
- Reads grounding docs from `_reference/` for API knowledge
- Self-scaffolds everything else: folder creation, file I/O, test execution, retry loops, child agent spawning

There is no coded retry loop, no tool registry, no wrapper classes. The agent writes its own scaffolding as needed.

## Quick Start

```bash
# 1. Install
pip install -e .[smol]

# 2. Create a task
mkdir -p agents/root
echo "Build a CSV parser that handles quoted fields and returns list[dict]" > agents/root/prompt.txt

# 3. Configure model (edit .env or set env vars)
cp .env.example .env
# Edit SMOL_MODEL_ID if desired

# 4. Run
python run.py
```

## Project Structure

```
recursive-coder/
├── run.py              # Thin launcher (~80 lines)
├── prompt.md           # System prompt — the product
├── config.py           # Model ID, paths, env vars
├── custom_model.py     # Local HuggingFace model wrapper
├── _reference/         # Grounding docs the agent reads
│   └── smolagents-api.md
├── pyproject.toml      # Dependencies
├── .env.example        # Environment variable template
├── agents/             # Working directory (agent creates everything inside)
│   └── root/
│       └── prompt.txt  # Your task goes here
├── README.md           # This file
└── AGENTS.md           # Instructions for AI coding agents
```

## How It Works

1. **`run.py`** creates a SmolAgents `CodeAgent` with the system prompt + reference docs + task
2. The agent reads `prompt.md` which tells it how to structure output, write tests, and handle failures
3. The agent reads `_reference/*.md` for API knowledge (SmolAgents, coding conventions)
4. The agent works in `agents/root/`, creating `solution.py`, `test_solution.py`, running pytest, and iterating
5. For complex tasks, the agent creates `task_*/` subdirectories and optionally spawns child CodeAgents

## Configuration

All configuration is via environment variables (or `.env` file).

### Provider selection

Set `SMOL_PROVIDER` to choose your model endpoint:

| Provider | `SMOL_PROVIDER` | Token env var | Example `SMOL_MODEL_ID` |
|----------|----------------|---------------|-------------------------|
| GitHub Models | `github` | `GITHUB_TOKEN` | `gpt-4o`, `o3-mini`, `DeepSeek-R1` |
| HuggingFace | `huggingface` | `HF_TOKEN` | `Qwen/Qwen2.5-Coder-32B-Instruct` |
| OpenAI | `openai` | `OPENAI_API_KEY` | `gpt-4o`, `o3-mini` |
| Local GPU | `local` | — | `microsoft/phi-3-mini-4k-instruct` |

### Switching providers

Edit your `.env`:

```bash
# Use GitHub Models
SMOL_PROVIDER=github
SMOL_MODEL_ID=gpt-4o
GITHUB_TOKEN=ghp_...

# Or HuggingFace
SMOL_PROVIDER=huggingface
SMOL_MODEL_ID=Qwen/Qwen2.5-Coder-32B-Instruct
HF_TOKEN=hf_...
```

### All variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SMOL_PROVIDER` | `huggingface` | Model endpoint: `github`, `huggingface`, `openai`, `local` |
| `SMOL_MODEL_ID` | *(per provider)* | Model name/ID |
| `SMOL_API_BASE` | *(per provider)* | Override the default API base URL |
| `SMOL_MAX_STEPS` | `30` | Max reasoning steps for the agent |
| `SMOL_QUANTIZE` | `true` | Use float16/quantization (local only) |

## The System Prompt

[prompt.md](prompt.md) is the core of this project. It tells the agent:

- **Output structure**: What files to create and how to format code
- **Testing discipline**: Write tests, run them, fix failures
- **Decomposition**: When and how to create subtask subfolders
- **Child agents**: How to spawn independent CodeAgent instances for subtasks
- **Self-correction**: Read errors, diagnose, fix, re-run
- **Logging**: Append to `log.txt` and `error.txt`

The agent follows these conventions because the prompt tells it to — not because code enforces them.

## Reference Documents

Drop `.md` files into `_reference/` and they'll be included in the agent's context automatically. Use this for:

- API documentation the agent needs
- Coding conventions for your team
- Domain-specific knowledge
- Architecture constraints

Currently included:
- `smolagents-api.md` — SmolAgents CodeAgent API reference

## Customizing

### Change the model

```bash
# Switch to a different GitHub Models model
export SMOL_PROVIDER=github
export SMOL_MODEL_ID=o3-mini
python run.py
```

### Change agent behavior

Edit `prompt.md`. That's it. Want stricter testing? Add rules. Want different file structure? Change the conventions. Want no decomposition? Remove that section.

### Add domain knowledge

Create `_reference/your-topic.md` and it's automatically picked up.

### Use a custom OpenAI-compatible endpoint

```bash
export SMOL_PROVIDER=openai
export SMOL_API_BASE=http://localhost:11434/v1   # e.g. Ollama
export SMOL_MODEL_ID=llama3
export OPENAI_API_KEY=unused
python run.py
```

## What Got Removed (and Why)

The previous version had ~2000 lines of Python scaffolding:
- `recursive_agent.py` — folder management, child spawning, test running
- `code_agent_integration.py` — tool wrappers, retry loops, attempt history
- `logger.py` — file logging abstraction

All of this is now handled by the agent itself via the system prompt. A CodeAgent can `Path.mkdir()`, `subprocess.run(["pytest", ...])`, and track state in variables. Pre-built tools were a token optimization, not a capability requirement.

## Development

```bash
# Install dev dependencies
pip install -e .[dev]

# Format
black .

# Lint
ruff check .
```
