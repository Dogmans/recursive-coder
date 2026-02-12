# Recursive Code Agent

A recursive code generation system using SmolAgents CodeAgent that decomposes complex tasks into subtasks, spawns child agents, and generates Python code hierarchically.

## Overview

The Recursive Code Agent works by:

1. **Loading a prompt**: Each agent reads its `prompt.txt` file (or prompts the user to create one)
2. **Decomposing tasks**: The agent analyzes the prompt and decides whether to handle it directly or decompose into subtasks
3. **Spawning children**: For complex subtasks, child agents are spawned in dedicated folders
4. **Generating code**: Each agent generates Python code (`solution.py`) and tests (`test_solution.py`)
5. **Validating**: Generated code is tested with pytest before being marked successful
6. **Importing**: Parent agents can import and call child agent functions via Python introspection

## Architecture

### Folder Structure

```
agents/
├── root/
│   ├── prompt.txt              # Main task
│   ├── solution.py             # Generated code for this level
│   ├── test_solution.py        # Tests for solution.py
│   ├── log.txt                 # General logging
│   ├── error.txt               # Error logs
│   └── task_subtask_name/
│       ├── prompt.txt          # Child's task
│       ├── solution.py         # Child's generated code
│       ├── test_solution.py    # Child's tests
│       ├── log.txt
│       ├── error.txt
│       └── task_sub_subtask_name/
│           └── ...
```

### Key Components

#### `RecursiveAgent` (recursive_agent.py)

Core agent class that:
- Manages prompt loading and task decomposition
- Creates and tracks child agents
- Handles code execution with timeouts
- Runs pytest for validation
- Provides logging via `AgentLogger`

**Key Methods:**
- `load_prompt()`: Load task from `prompt.txt` or prompt user
- `decompose_task()`: Analyze task complexity
- `create_child_agent()`: Spawn a child agent for a subtask
- `run_code_with_timeout()`: Execute Python with timeout protection
- `run_tests()`: Validate code with pytest
- `import_child_solution()`: Import child's `solution.py` module
- `execute()`: Main execution method

#### `AgentLogger` (logger.py)

Handles logging to both files and console:
- `log.txt`: General progress and info
- `error.txt`: Errors and failures
- Console output: Real-time aggregated logging from all agents

**Methods:**
- `info()`, `warning()`, `debug()`, `error()`, `critical()`
- `save_test_results()`, `load_test_results()`
- `get_error_summary()`, `get_log_summary()`

#### `RecursiveCodeAgent` (code_agent_integration.py)

Integration wrapper for SmolAgents CodeAgent that exposes:
- Task decomposition interface
- Child agent creation
- Solution submission and validation
- Child solution import and function discovery
- Function execution on child solutions

**Tools for CodeAgent:**
- `decompose_task`: Analyze task complexity and plan subtasks
- `create_subtask`: Spawn child agents in dedicated folders
- `submit_solution`: Save generated code and tests, run pytest validation
- `list_managed_agents`: List all child agents and their current status
- `get_child_steps`: View a child agent's execution log and progress
- `run_managed_agent`: Execute a child agent end-to-end, run its tests, and record the attempt
- `report_child_progress`: Check child status including errors and test results
- `get_child_diagnostics`: Deep inspection of a child — reads code, tests, errors, logs, and attempt history; runs a fresh pytest
- `retry_child_agent`: Iteratively re-run a failing child with augmented context (previous code, test failures, revised instructions)
- `reset_child_agent`: Destroy and recreate a child agent (optionally preserving attempt history)
- `merge_child_requirements`: Merge child `requirements.txt` into parent

### Configuration (config.py)

Centralized settings:
- **Timeouts**: DEFAULT_TIMEOUT (300s), MIN/MAX bounds
- **Recursion**: DEFAULT_RECURSION_DEPTH, MAX_RECURSION_DEPTH
- **Naming**: CHILD_FOLDER_PREFIX (`task_`)
- **Files**: PROMPT_FILE, SOLUTION_FILE, LOG_FILE, ERROR_FILE, TEST_RESULTS_FILE
- **System Prompt**: Template with placeholders for agent-specific settings

## Usage

### 1. Basic Setup

```bash
# Create the agents directory
mkdir -p agents/root

# Create initial prompt
echo "Your task description here" > agents/root/prompt.txt
```

### 2. Initialize Agent

```python
from pathlib import Path
from recursive_agent import RecursiveAgent
from code_agent_integration import RecursiveCodeAgent, create_codeagent_tools
import config

# Create root agent
agent = RecursiveAgent(
    agent_dir=Path("agents/root"),
    agent_name="RootAgent"
)

# Create CodeAgent integration
code_agent_wrapper = RecursiveCodeAgent(agent)

# Get tools for CodeAgent
tools = create_codeagent_tools(code_agent_wrapper)

# Execute
result = agent.execute()
```

### 3. Integration with SmolAgents CodeAgent

```python
from smol_agents import CodeAgent

# Your CodeAgent setup
agent = CodeAgent(
    tools=tools,  # From create_codeagent_tools()
    model_id="gpt-4",  # or your model
    verbosity_level=2,
    system_prompt=code_agent_wrapper.get_system_prompt(),
)

# Execute with task
response = agent.run(code_agent_wrapper.get_user_prompt())
```

## Code Generation Requirements

### solution.py Structure

Each `solution.py` must follow these conventions:

```python
"""Module docstring describing what this component does."""

def descriptive_function_name(param1: str, param2: int) -> dict:
    """Function with complete documentation.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value with type info
    """
    # Implementation
    return {"result": "value"}


def another_function() -> list:
    """Another public function."""
    return []


def _helper_function():
    """Private helper (starts with underscore)."""
    pass
```

### requirements.txt Convention

If a child agent uses non-stdlib dependencies, it should write a local requirements.txt (one dependency per line) in its own folder. The parent should merge these into its own requirements.txt so it can install all dependencies before importing or testing child code.

Parent merge example:
```python
merged = agent.merge_child_requirements()
print(merged)
```

### test_solution.py Structure

Tests must be pytest-compatible:

```python
"""Tests for solution module."""

import pytest
from solution import descriptive_function_name


def test_descriptive_function_name():
    """Test the main function."""
    result = descriptive_function_name("test", 42)
    assert isinstance(result, dict)
    assert "result" in result


@pytest.mark.timeout(10)
def test_timeout_example():
    """Test with timeout."""
    # Test implementation
    pass
```

## Task Decomposition Strategy

Agents should decompose based on:

1. **Complexity**: If a subtask is complex, spawn a child agent
2. **Dependencies**: Logically independent tasks should be children
3. **Return Types**: Child functions should have clear, documented return types
4. **Depth**: Stop decomposing at max recursion depth

Example decomposition logic:
```
Main Task: "Build a web scraper and analyzer"
  ├── Subtask 1: "Web scraping module" → task_web_scraper/
  └── Subtask 2: "Data analysis module" → task_data_analyzer/

Subtask 1 "Web scraping module":
  ├── Subtask 1.1: "HTML parsing" → task_html_parser/
  └── Subtask 1.2: "URL fetching" → task_url_fetcher/
```

## Timeout Management

- **Default timeout**: 300 seconds per agent
- **Min timeout**: 30 seconds
- **Max timeout**: 3600 seconds
- **Parent to child**: Parents estimate child complexity and set timeout in child's prompt

Example in parent code:
```python
child = agent.create_child_agent(
    child_name="complex_subtask",
    task_description="...",
    expected_timeout=600  # 10 minutes for complex task
)
```

## Error Handling & Iterative Refinement

### Error Files

Each agent creates:
- **error.txt**: All errors, failures, timeouts
- **log.txt**: Progress, info, warnings

### Error Detection

Parent agents check child status:
```python
progress = code_agent_wrapper.report_child_progress("subtask_name")
if progress["has_errors"]:
    error_msg = progress["error_summary"]
    # Handle error — see Retry Pattern below
```

### Retry Pattern (Diagnose → Retry → Escalate)

When a child agent fails, the parent follows a structured recovery loop:

1. **Diagnose** — call `get_child_diagnostics(child_name)` to inspect the child's code, test output, error log, and full attempt history.
2. **Retry** — call `retry_child_agent(child_name, revised_instructions, max_retries=3)` which rebuilds the prompt with previous code + test failures + parent guidance, then re-runs the child.
3. **Escalate** — if retries are exhausted, call `reset_child_agent(child_name, preserve_history=True)` for a clean slate (keeping history), or absorb the subtask into the parent.

```python
# 1. Diagnose
diag = code_agent_wrapper.get_child_diagnostics("task_parser")
print(diag["test_output"])       # Latest pytest output
print(diag["attempt_history"])   # All previous attempts

# 2. Retry with guidance
result = code_agent_wrapper.retry_child_agent(
    child_name="task_parser",
    revised_instructions="Fix the off-by-one error in parse_line(). "
                         "The delimiter should split on commas, not spaces.",
    max_retries=3
)

if result["success"]:
    print("Child recovered!")
else:
    # 3. Escalate — full reset or absorb
    code_agent_wrapper.reset_child_agent("task_parser", preserve_history=True)
```

Each attempt is recorded in `attempt_history` so the parent (and descendant retries) have full visibility into what was tried and why it failed.

### Timeout Detection

Timeouts are caught by:
1. `subprocess.TimeoutExpired` exception in `run_code_with_timeout()`
2. `pytest-timeout` plugin for test execution
3. Each timeout is logged to `error.txt`

## Logging and Monitoring

### Console Output

Each agent logs to console with prefix:
```
[AgentName] [2024-02-04T12:34:56.789123] [INFO    ] Message here
[RootAgent::task_subtask] [2024-02-04T12:34:57.123456] [ERROR   ] Error message
```

### File Logs

Access logs via:
```python
agent.logger.get_log_summary()      # Last log entries
agent.logger.get_error_summary()    # All errors
```

### Aggregated Monitoring

All agents write to console, so you can:
```bash
python example_usage.py 2>&1 | tee full_run.log
```

## Function Discovery and Execution

### Discovering Child Functions

```python
from recursive_agent import RecursiveAgent

agent = RecursiveAgent(agent_dir="agents/root")
functions = agent.get_child_function_info("task_subtask")

# functions = {
#     "process_data": {
#         "signature": "(items: list) -> dict",
#         "docstring": "Processes items...",
#         "annotations": {"items": list, "return": dict}
#     }
# }
```

### Calling Child Functions

```python
result = code_agent_wrapper.execute_child_function(
    child_name="subtask_name",
    function_name="process_data",
    items=[1, 2, 3]
)

if result["success"]:
    output = result["result"]
```

## Testing

### Running Tests

Each agent's `test_solution.py` is validated with pytest:
```bash
pytest agents/root/test_solution.py -v --timeout=60
```

### Test Results

Test results saved to `test_results.json`:
```python
test_results = agent.logger.load_test_results()
```

## Installation

```bash
# Install dependencies
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Example: Complete Workflow

See `example_usage.py` for a complete initialization example:

```bash
python example_usage.py
```

This will:
1. Create `agents/root/` directory
2. Prompt for task if no `prompt.txt` exists
3. Initialize the root agent
4. Show system prompt and available tools
5. Be ready for CodeAgent integration

## Best Practices

1. **Clear task descriptions**: Write specific, unambiguous prompts
2. **Type hints everywhere**: Use complete type hints in all functions
3. **Docstrings required**: Every function needs a docstring
4. **Test coverage**: Write comprehensive tests for validation
5. **Timeout estimation**: Set realistic timeouts based on task complexity
6. **Error handling**: Log errors clearly for parent visibility
7. **Modular functions**: Each function should do one thing well
8. **Return type clarity**: Ensure return types match what parent expects
9. **Never silently accept failure**: Always diagnose a failing child before moving on
10. **Use the retry loop**: Call `get_child_diagnostics` → `retry_child_agent` → `reset_child_agent` rather than giving up on first failure
11. **Provide revised instructions**: When retrying, tell the child *what went wrong* and *how to fix it* — don't just re-run blindly

## Troubleshooting

### Child Agent Not Found

Check that child folder was created with correct naming:
- Format: `task_<lowercase_alphanumeric>`
- Example: `task_data_processor`

### Import Errors

Ensure child's `solution.py`:
1. Has valid Python syntax
2. All imports are in scope
3. Functions are defined at module level

### Timeout Issues

- Increase `timeout_seconds` in child creation
- Check for infinite loops in generated code
- Verify pytest tests complete within `PYTEST_TIMEOUT`

### Missing Test Results

Ensure `test_solution.py` exists and pytest is installed:
```bash
pip install pytest pytest-timeout
```

## Future Enhancements

- [x] Iterative retry loop with attempt history
- [x] Child diagnostics and deep inspection
- [ ] Parallel child agent execution
- [ ] Caching of intermediate results
- [ ] Agent checkpointing and resume
- [ ] Web UI for monitoring
- [ ] Distributed agent execution
- [ ] Custom tool system for agents
