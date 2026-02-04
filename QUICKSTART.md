# Quick Start Guide

Get started with the Recursive Code Agent in 5 minutes.

## 1. Installation

```bash
# Navigate to the project directory
cd /path/to/recursive-coder

# Install dependencies
pip install -e .

# Verify installation
python -c "import recursive_agent; print('✓ Installation successful')"
```

## 2. Run the Example

```bash
# Run the complete example
python complete_example.py

# This will:
# - Create agents/root/ directory
# - Demonstrate agent creation
# - Show child agent spawning
# - Validate example code
# - Display available tools
```

## 3. Create Your First Agent

```python
from pathlib import Path
from recursive_agent import RecursiveAgent

# Create agent
agent = RecursiveAgent(
    agent_dir=Path("agents/my_task"),
    agent_name="MyAgent"
)

# Execute (will prompt for task if no prompt.txt exists)
result = agent.execute()
print(result)
```

## 4. Integrate with SmolAgents CodeAgent

```python
from recursive_agent import RecursiveAgent
from code_agent_integration import RecursiveCodeAgent, create_codeagent_tools

# Create agent and wrapper
agent = RecursiveAgent(agent_dir=Path("agents/root"))
wrapper = RecursiveCodeAgent(agent)

# Get tools for CodeAgent
tools = create_codeagent_tools(wrapper)

# Now use with your CodeAgent:
# code_agent = CodeAgent(tools=tools, ...)
```

## 5. Key Files and Directories

After running an agent, you'll have:

```
agents/root/
├── prompt.txt           # Your task description
├── solution.py          # Generated code
├── test_solution.py     # Generated tests
├── log.txt             # Execution logs
├── error.txt           # Error logs (if any)
└── task_subtask/       # Child agents
    ├── prompt.txt
    ├── solution.py
    └── ...
```

## Common Tasks

### View Agent Logs

```python
agent.logger.get_log_summary()       # All logs
agent.logger.get_error_summary()     # Errors only
```

### Import Child's Code

```python
module = agent.import_child_solution("task_subtask")
result = module.process_data([1, 2, 3])
```

### Discover Functions in Child

```python
functions = agent.get_child_function_info("task_subtask")
for func_name, func_info in functions.items():
    print(f"{func_name}: {func_info['signature']}")
```

### Create a Subtask

```python
child = agent.create_child_agent(
    child_name="Data Processor",
    task_description="Process and validate data",
    expected_timeout=120
)
```

### Merge Child Dependencies

If a child uses non-stdlib dependencies, it should write requirements.txt in its own folder. The parent can merge all child requirements into its own requirements.txt:

```python
merged = agent.merge_child_requirements()
print(merged)
```

## Folder Structure Conventions

- **Folder names**: Use `task_<descriptive_name>` for child agents
- **Solution file**: Always `solution.py` with typed functions
- **Tests file**: `test_solution.py` with pytest tests
- **Logs**: `log.txt` for info, `error.txt` for errors

Example valid names:
- `task_data_processor`
- `task_api_handler`
- `task_validation_logic`

## Timeout Management

Set appropriate timeouts based on task complexity:

```python
# Quick subtask (1-2 minutes)
child1 = agent.create_child_agent(
    child_name="quick_task",
    task_description="...",
    expected_timeout=120  # 2 minutes
)

# Complex subtask (5-10 minutes)
child2 = agent.create_child_agent(
    child_name="complex_task",
    task_description="...",
    expected_timeout=600  # 10 minutes
)
```

## Testing Generated Code

The system automatically validates code with pytest:

```bash
# View test results for an agent
cat agents/root/log.txt | grep -i test
cat agents/root/test_results.json
```

## Troubleshooting

### "No module named 'solution'"

Child solution.py might have syntax errors. Check:
```
agents/root/task_subtask/error.txt
agents/root/task_subtask/log.txt
```

### Import fails

Ensure all imports in `solution.py` are installed:
```bash
pip install required-package
```

### Timeout errors

Increase timeout in child creation:
```python
child = agent.create_child_agent(
    ...,
    expected_timeout=900  # 15 minutes instead of 5
)
```

### Function not found

Verify function names match exactly (case-sensitive):
```python
# Check available functions
funcs = agent.get_child_function_info("task_subtask")
print(funcs.keys())

# Then call with correct name
module = agent.import_child_solution("task_subtask")
result = module.correct_function_name()
```

## Next Steps

1. **Read the full README.md** for comprehensive documentation
2. **Check complete_example.py** for detailed usage patterns
3. **Explore config.py** to customize settings
4. **Review recursive_agent.py** for the API reference

## Getting Help

### Enable Debug Logging

```python
agent.logger.debug("Debug message", console=True)
```

### Check File System

```bash
tree agents/  # View folder structure (Unix/Mac)
# or
dir /s /B agents\  # Windows
```

### Monitor Logs in Real-time

```bash
tail -f agents/root/log.txt
tail -f agents/root/error.txt
```

## Next Integration: SmolAgents

Once you're familiar with the basics, integrate with SmolAgents:

```bash
pip install smol-agents
```

Then see the "Integration with SmolAgents CodeAgent" section in README.md
