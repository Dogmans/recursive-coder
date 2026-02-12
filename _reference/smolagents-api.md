# SmolAgents CodeAgent — Quick Reference

This is a summary of the SmolAgents framework so you know what tools and patterns are available to you.

## CodeAgent Basics

A `CodeAgent` writes and executes Python code to accomplish tasks. It can call tools, write files, run subprocesses, and manage state — all through generated code.

```python
from smolagents import CodeAgent, InferenceClientModel, DuckDuckGoSearchTool

agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=InferenceClientModel(model_id="..."),
    max_steps=30,
    verbosity_level=2,
    additional_authorized_imports=["subprocess", "pathlib", "json"],
)

result = agent.run("Your task description here")
```

## What CodeAgent Can Do

- **Write and execute Python code** in each step
- **Use tools** passed to it (web search, custom tools, etc.)
- **Import modules** listed in `additional_authorized_imports`
- **Maintain state** across steps (variables persist between code blocks)
- **Self-correct** — if code raises an exception, the agent sees the traceback and can fix it

## Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `tools` | List of tool instances available to the agent | `[]` |
| `model` | The LLM model to use for code generation | Required |
| `max_steps` | Maximum reasoning/execution steps | `6` |
| `verbosity_level` | 0=silent, 1=summary, 2=full | `1` |
| `additional_authorized_imports` | Python modules the agent is allowed to import | `[]` |
| `system_prompt` | Override the default system prompt | Built-in |

## Spawning Child Agents

You can create another CodeAgent inside your code to handle a subtask:

```python
from smolagents import CodeAgent

child = CodeAgent(
    tools=tools,       # Pass the same tools
    model=model,       # Pass the same model
    max_steps=10,
    verbosity_level=2,
    additional_authorized_imports=["subprocess", "pathlib", "json"],
)

result = child.run("Subtask description here")
```

The child agent is independent — it has its own step counter, its own state, and its own code execution context. Use this for complex, independent subtasks.

## Tools

Tools are Python functions decorated with `@tool`:

```python
from smolagents.tools import tool

@tool
def read_file(path: str) -> str:
    """Read a file and return its contents.

    Args:
        path: Path to the file to read.

    Returns:
        The file contents as a string.
    """
    return open(path).read()
```

Built-in tools:
- `DuckDuckGoSearchTool()` — web search
- `VisitWebpageTool()` — fetch webpage content

## Authorized Imports

By default, CodeAgent restricts imports for safety. To allow additional modules:

```python
agent = CodeAgent(
    additional_authorized_imports=[
        "subprocess", "pathlib", "json", "importlib",
        "inspect", "datetime", "re", "os", "sys",
    ],
    ...
)
```

The agent can then use these in its generated code blocks.

## Error Handling in CodeAgent

When the agent's generated code raises an exception:
1. The traceback is captured
2. The agent sees the error in its next step
3. It can write corrected code

This automatic retry loop means the agent can self-correct without external scaffolding. The `max_steps` parameter bounds total attempts.

## Model Options

```python
# GitHub Models / OpenAI / any OpenAI-compatible endpoint
from smolagents import OpenAIServerModel
model = OpenAIServerModel(
    model_id="gpt-4o",
    api_base="https://models.inference.ai.azure.com",
    api_key="ghp_...",
)

# HuggingFace Inference API
from smolagents import InferenceClientModel
model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct", token="hf_...")

# Local transformers model
from custom_model import DirectTransformersModel
model = DirectTransformersModel(model_id="microsoft/phi-3-mini-4k-instruct")
```
