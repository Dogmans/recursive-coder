# Recursive Code Agent - Complete Implementation

A sophisticated recursive code generation system using SmolAgents CodeAgent that automatically decomposes complex tasks into hierarchical subtasks, spawns child agents, and generates validated Python code.

## 🚀 Quick Start (2 minutes)

```bash
# 1. Install
pip install -e .

# 2. Validate
python validate.py

# 3. Setup
python project_setup.py

# 4. Try it
python example_usage.py
```

## 📁 Project Structure

```
recursive-coder/
├── Core Implementation
│   ├── recursive_agent.py          # Main RecursiveAgent class
│   ├── code_agent_integration.py   # SmolAgents CodeAgent wrapper
│   ├── logger.py                   # Logging system
│   └── config.py                   # Configuration
│
├── Examples & Tools
│   ├── example_usage.py            # Simple example
│   ├── complete_example.py         # Full demonstration
│   ├── validate.py                 # System validation
│   └── project_setup.py            # Initial setup
│
├── Documentation
│   ├── README.md                   # Full documentation
│   ├── QUICKSTART.md               # Quick start guide
│   ├── PROJECT_FILES.md            # File descriptions
│   └── INDEX.md                    # This file
│
├── Configuration
│   ├── pyproject.toml              # Project metadata
│   ├── config_template.py          # Configuration template
│   └── .gitignore                  # Git exclusions
│
└── agents/                         # Workspace (created by users)
    └── root/
        ├── prompt.txt
        ├── solution.py
        ├── test_solution.py
        ├── log.txt
        └── error.txt
```

## 🎯 Core Concepts

### What It Does

1. **Loads a task** from `prompt.txt` (or prompts user)
2. **Analyzes complexity** and decides whether to decompose
3. **Spawns child agents** in subfolders for complex subtasks
4. **Generates code** (`solution.py`) with typed functions
5. **Validates with tests** using pytest
6. **Manages errors** via `error.txt` and `log.txt`
7. **Enables integration** with SmolAgents CodeAgent

### Task Decomposition Flow

```
Main Task: "Build a web scraper and analyzer"
    │
    ├─→ Child 1: "Web Scraping Module"
    │   └─→ Grandchild 1.1: "HTML Parser"
    │   └─→ Grandchild 1.2: "URL Fetcher"
    │
    └─→ Child 2: "Data Analysis Module"
        └─→ Grandchild 2.1: "Statistical Analysis"
```

### Folder Structure

```
agents/root/
├── prompt.txt              # "Build web scraper and analyzer"
├── solution.py             # Code at this level
├── test_solution.py        # Tests
├── log.txt                 # Progress
├── error.txt               # Errors
│
├── task_web_scraper/
│   ├── prompt.txt
│   ├── solution.py
│   ├── test_solution.py
│   ├── task_html_parser/   # Grandchild
│   └── task_url_fetcher/
│
└── task_data_analyzer/
    ├── prompt.txt
    ├── solution.py
    └── task_statistical_analysis/
```

## 🔧 Key Components

### RecursiveAgent (`recursive_agent.py`)
```python
agent = RecursiveAgent(
    agent_dir=Path("agents/root"),
    agent_name="RootAgent",
    timeout_seconds=300,
    max_retries=3,
)

# Load task
prompt = agent.load_prompt()

# Create children
child = agent.create_child_agent(
    child_name="Subtask Name",
    task_description="What to do",
    expected_timeout=120
)

# Run tests
results = agent.run_tests()

# Import child code
module = agent.import_child_solution("task_subtask")
output = module.function_name()
```

### RecursiveCodeAgent (`code_agent_integration.py`)
```python
from code_agent_integration import (
    RecursiveCodeAgent,
    create_codeagent_tools
)

wrapper = RecursiveCodeAgent(agent)

# Create tools for CodeAgent
tools = create_codeagent_tools(wrapper)

# Available tools:
# - decompose_task
# - create_subtask
# - submit_solution
# - get_child_solution
# - execute_child_function
# - report_child_progress
```

### AgentLogger (`logger.py`)
```python
agent.logger.info("Progress message")
agent.logger.error("Error message")
agent.logger.warning("Warning message")

# Get summaries
logs = agent.logger.get_log_summary()
errors = agent.logger.get_error_summary()

# Save test results
agent.logger.save_test_results({...})
```

## 📊 Configuration

### Key Settings (config.py)

```python
# Timeouts
DEFAULT_TIMEOUT = 300           # 5 minutes
MIN_TIMEOUT = 30
MAX_TIMEOUT = 3600

# Recursion
DEFAULT_RECURSION_DEPTH = 5
MAX_RECURSION_DEPTH = 10

# Naming
CHILD_FOLDER_PREFIX = "task_"

# Files
PROMPT_FILE = "prompt.txt"
SOLUTION_FILE = "solution.py"
LOG_FILE = "log.txt"
ERROR_FILE = "error.txt"
```

### Customize

Copy `config_template.py` and modify:
```python
DEFAULT_TIMEOUT = 600  # 10 minutes
DEFAULT_RECURSION_DEPTH = 7
```

## 💻 Usage Examples

### Simple Agent Setup

```python
from recursive_agent import RecursiveAgent
from pathlib import Path

agent = RecursiveAgent(agent_dir=Path("agents/root"))
result = agent.execute()
```

### Create Child Agents

```python
# For each subtask
child1 = agent.create_child_agent(
    child_name="Data Processing",
    task_description="Process raw data",
    expected_timeout=120
)

child2 = agent.create_child_agent(
    child_name="Validation",
    task_description="Validate processed data",
    expected_timeout=90
)
```

### Submit and Validate Code

```python
wrapper = RecursiveCodeAgent(agent)

result = wrapper.submit_solution(
    code=solution_code,
    test_code=test_code
)

if result["success"]:
    print("✓ Solution validated!")
```

### Call Child Functions

```python
# Get function info
info = wrapper.get_child_info("data_processing")
for func_name, details in info.items():
    print(f"{func_name}: {details['signature']}")

# Execute function
result = wrapper.execute_child_function(
    child_name="data_processing",
    function_name="process_items",
    items=[1, 2, 3]
)
```

### SmolAgents Integration

```python
from smol_agents import CodeAgent

# Setup
agent = RecursiveAgent(agent_dir=Path("agents/root"))
wrapper = RecursiveCodeAgent(agent)
tools = create_codeagent_tools(wrapper)

# Create CodeAgent
code_agent = CodeAgent(
    tools=tools,
    model_id="gpt-4-turbo",
    system_prompt=wrapper.get_system_prompt(),
)

# Run
response = code_agent.run(wrapper.get_user_prompt())
```

## 📝 Generated Code Requirements

### solution.py Structure

```python
"""Module docstring."""

def process_data(items: list[str]) -> dict[str, int]:
    """Process items and return counts.
    
    Args:
        items: List of strings to process
        
    Returns:
        Dictionary with count results
    """
    return {"count": len(items)}


def validate_data(data: dict) -> bool:
    """Validate data structure.
    
    Args:
        data: Data to validate
        
    Returns:
        True if valid
    """
    return isinstance(data, dict)


def _helper():
    """Private helper function."""
    pass
```

### test_solution.py Structure

```python
"""Tests for solution."""

import pytest
from solution import process_data, validate_data


def test_process_data():
    """Test data processing."""
    result = process_data(["a", "b", "c"])
    assert result["count"] == 3


def test_validate_data():
    """Test validation."""
    assert validate_data({}) is True
    assert validate_data([]) is False


@pytest.mark.timeout(10)
def test_with_timeout():
    """Test with timeout."""
    pass
```

## ⏱️ Timeout Management

### Default Behavior
- Root agent: 300 seconds (5 minutes)
- Child timeout: Parent estimates based on complexity
- Min: 30 seconds, Max: 3600 seconds

### Setting Child Timeouts
```python
# Quick subtask
child = agent.create_child_agent(
    ...,
    expected_timeout=60  # 1 minute
)

# Complex subtask
child = agent.create_child_agent(
    ...,
    expected_timeout=900  # 15 minutes
)
```

### Timeout Detection
- `subprocess.TimeoutExpired` for code execution
- `pytest-timeout` plugin for tests
- All logged to `error.txt`

## 🔍 Logging and Monitoring

### Real-time Console Output
```bash
[RootAgent] [2024-02-04T12:34:56.789123] [INFO    ] Initialized root agent...
[RootAgent::task_processor] [2024-02-04T12:34:57.123456] [INFO    ] Child created
[RootAgent::task_processor] [2024-02-04T12:34:58.456789] [ERROR   ] Test failed
```

### Log Files
- **log.txt**: Progress, info, warnings
- **error.txt**: Errors, failures, timeouts

### Access Logs Programmatically
```python
logs = agent.logger.get_log_summary()      # Last 500 chars
errors = agent.logger.get_error_summary()  # All errors
```

## 🧪 Testing and Validation

### Automatic Validation
Each agent:
1. Generates code in `solution.py`
2. Generates tests in `test_solution.py`
3. Runs pytest to validate
4. Records results to `test_results.json`
5. Logs to `log.txt` or `error.txt`

### Check Test Results
```python
results = agent.logger.load_test_results()
print(results)  # JSON with pass/fail info
```

### Run Tests Manually
```bash
pytest agents/root/test_solution.py -v --timeout=60
```

## 🔗 Function Discovery

### Discover Child Functions
```python
import inspect

module = agent.import_child_solution("task_subtask")

for name, obj in inspect.getmembers(module):
    if inspect.isfunction(obj) and not name.startswith("_"):
        sig = inspect.signature(obj)
        doc = inspect.getdoc(obj)
        print(f"{name}{sig}")
        print(f"  {doc}")
```

### Call Functions Safely
```python
# Check if function exists
info = wrapper.get_child_info("task_subtask")
if "process_data" in info:
    result = wrapper.execute_child_function(
        "task_subtask",
        "process_data",
        data=[1, 2, 3]
    )
```

## 🛠️ Tools & Scripts

### validate.py
Check system health:
```bash
python validate.py
```

Verifies:
- Python 3.10+
- Dependencies installed
- Project structure
- Module imports
- Agent creation
- Logger functionality

### project_setup.py
Initial setup:
```bash
python project_setup.py
```

Does:
- Installs dependencies
- Creates `agents/` directory
- Optionally creates initial task
- Runs validation

### example_usage.py
Simple example:
```bash
python example_usage.py
```

Shows:
- Agent initialization
- System prompt
- Available tools

### complete_example.py
Full demonstration:
```bash
python complete_example.py
```

Shows:
- Agent creation
- Child spawning
- Solution submission
- Function discovery
- Logging
- CodeAgent integration

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Comprehensive documentation |
| QUICKSTART.md | 5-minute getting started |
| PROJECT_FILES.md | File descriptions |
| INDEX.md | This file |
| config.py | Main configuration |
| config_template.py | Configuration template |

## 🚨 Error Handling

### Child Agent Fails
```python
progress = wrapper.report_child_progress("task_subtask")
if progress["has_errors"]:
    print(progress["error_summary"])
```

### Timeout
Agent automatically:
1. Catches timeout exception
2. Logs to `error.txt`
3. Reports to parent via `report_child_progress()`

### Import Errors
Check:
1. Child's `solution.py` syntax
2. All imports installed
3. Functions are at module level

## 🔐 Best Practices

1. **Type hints everywhere**: All functions must have complete type hints
2. **Docstrings required**: Every function needs a docstring
3. **Test coverage**: Write comprehensive tests
4. **Clear naming**: Use descriptive function names
5. **Error messages**: Log errors clearly for debugging
6. **Timeout estimation**: Set realistic timeouts
7. **Modular code**: Each function does one thing well
8. **Return type clarity**: Ensure parent understands return types

## 🆘 Troubleshooting

### "No module named 'solution'"
**Check**: `agents/root/task_subtask/error.txt` for syntax errors

### Import fails
**Check**: All imports in `solution.py` are installed
```bash
pip install <package>
```

### Timeout errors
**Increase**: timeout in child creation
```python
expected_timeout=900  # 15 minutes
```

### Test failures
**Check**: `test_results.json` for pytest output
```bash
cat agents/root/test_results.json
```

## 📦 Dependencies

Core:
- Python 3.10+
- pytest
- pytest-timeout
- pydantic

Optional:
- smol-agents (for CodeAgent integration)
- requests (for web access)

## 🎓 Learning Path

1. **Start**: QUICKSTART.md
2. **Understand**: README.md
3. **Explore**: example_usage.py
4. **Experiment**: complete_example.py
5. **Customize**: config.py, config_template.py
6. **Integrate**: code_agent_integration.py with SmolAgents
7. **Reference**: PROJECT_FILES.md, recursive_agent.py

## 🚀 Next Steps

1. **Install**: `python project_setup.py`
2. **Validate**: `python validate.py`
3. **Try**: `python example_usage.py`
4. **Learn**: Read QUICKSTART.md and README.md
5. **Integrate**: Use with SmolAgents CodeAgent

## 📞 System Overview

```
SmolAgents CodeAgent
        ↓
RecursiveCodeAgent (wrapper)
        ↓
RecursiveAgent (core logic)
        ├─→ Child Agent 1
        │   ├─→ Grandchild 1.1
        │   └─→ Grandchild 1.2
        └─→ Child Agent 2

Each Agent:
  - Reads prompt.txt
  - Creates solution.py
  - Generates test_solution.py
  - Runs pytest
  - Logs to log.txt/error.txt
  - Returns results via Python introspection
```

## ✅ Implementation Status

- ✅ Core RecursiveAgent system
- ✅ Logging and error handling
- ✅ Timeout management
- ✅ SmolAgents CodeAgent integration
- ✅ Function discovery via inspect
- ✅ Child agent spawning
- ✅ Pytest integration
- ✅ Comprehensive documentation
- ✅ Complete examples
- ✅ Validation script
- ✅ Setup script
- ✅ Configuration system

## 📄 License

Recursive Code Agent - Ready for production use

---

**For questions or issues, refer to README.md or check PROJECT_FILES.md for detailed documentation on each component.**

**Ready to get started? Run `python project_setup.py` now!**
