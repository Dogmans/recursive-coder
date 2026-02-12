# Project Files Summary

## Core System Files

### `config.py`
Main configuration file with all settings:
- File naming conventions
- Timeout settings (DEFAULT_TIMEOUT, MIN_TIMEOUT, MAX_TIMEOUT)
- Recursion depth limits
- Logging configuration
- System prompt template
- Child folder naming prefix

### `logger.py`
Logging system with file and console output:
- `AgentLogger` class handles all logging
- Writes to `log.txt` and `error.txt`
- Console output with agent name prefixes
- Test result serialization
- Error summary retrieval

### `recursive_agent.py`
Core recursive agent implementation:
- `RecursiveAgent` class - main agent logic
- Prompt loading with user input fallback
- Task decomposition interface
- Child agent creation and management
- Code execution with timeout protection
- Pytest integration
- Function introspection via `inspect` module
- Child solution importing

### `code_agent_integration.py`
Integration layer for SmolAgents CodeAgent:
- `RecursiveCodeAgent` wrapper class
- Tool definitions for CodeAgent (`decompose_task`, `create_subtask`, `submit_solution`, `list_managed_agents`, `get_child_steps`, `run_managed_agent`, `report_child_progress`, `get_child_diagnostics`, `retry_child_agent`, `reset_child_agent`, `merge_child_requirements`)
- Attempt history tracking across child retries
- `get_child_diagnostics()`: deep inspection of child code, tests, errors, logs, and attempt history
- `retry_child_agent()`: iterative re-run of failing children with augmented prompts (previous code + test failures + parent guidance)
- `reset_child_agent()`: destroy and recreate a child, optionally preserving attempt history
- Solution submission and validation
- `create_codeagent_tools()` function to expose all 11 tools

## Documentation

### `README.md` (Comprehensive)
Complete documentation covering:
- Architecture overview
- Folder structure explanation
- Component descriptions
- Usage examples
- Code generation requirements
- Task decomposition strategy
- Timeout management
- Error handling
- Logging and monitoring
- Function discovery and execution
- Testing approach
- Installation and best practices
- Troubleshooting guide

### `QUICKSTART.md` (Getting Started)
Quick reference for rapid setup:
- 5-minute installation
- Basic examples
- Common tasks
- Folder structure conventions
- Timeout management
- Testing overview
- Troubleshooting quick fixes
- Next steps

### `config_template.py`
Template for advanced customization:
- All configuration options with comments
- Can be copied and modified
- Future extension points
- Advanced settings (profiling, parallel execution, etc.)

## Examples and Utilities

### `example_usage.py`
Simple initialization example:
- Shows basic agent setup
- Demonstrates `execute()` method
- Shows tool availability
- Good starting point for understanding the API

### `complete_example.py`
Comprehensive demonstration script:
- Agent creation walkthrough
- Child agent spawning
- Solution submission and validation
- Function discovery examples
- Logging demonstration
- CodeAgent integration example
- All in one runnable file

### `validate.py`
Validation and diagnostics script:
- Checks Python version (3.10+)
- Verifies dependencies
- Tests project structure
- Validates imports
- Tests agent creation
- Tests logger functionality
- Tests CodeAgent integration
- Reports overall system health

### `project_setup.py`
Initial setup script:
- Installs dependencies via `pip install -e .`
- Creates `agents/` directory
- Optionally creates initial task
- Runs validation
- Shows next steps

## Configuration Files

### `pyproject.toml`
Project metadata and dependencies:
- Build system configuration
- Project metadata (name, version, description)
- Dependencies: smol-agents, pytest, pytest-timeout, pydantic, requests
- Optional dev dependencies
- Tool configurations (pytest, black, ruff)

### `.gitignore`
Version control exclusions:
- Python build artifacts
- Virtual environments
- IDE configuration
- Agent directories and logs
- Temporary files

## Directory Structure After Setup

```
recursive-coder/
├── pyproject.toml           # Project config
├── config.py               # Main configuration
├── config_template.py      # Configuration template
├── logger.py               # Logging system
├── recursive_agent.py      # Core agent class
├── code_agent_integration.py # CodeAgent integration
├── README.md              # Full documentation
├── QUICKSTART.md          # Quick start guide
├── example_usage.py       # Simple example
├── complete_example.py    # Full demonstration
├── validate.py            # Validation script
├── project_setup.py      # Setup script
├── .gitignore            # Git exclusions
│
└── agents/                # Agent workspace (created by users)
    ├── root/              # Root agent
    │   ├── prompt.txt
    │   ├── solution.py
    │   ├── test_solution.py
    │   ├── log.txt
    │   ├── error.txt
    │   └── task_subtask/
    │       ├── prompt.txt
    │       ├── solution.py
    │       └── ...
    │
    └── (other agent workspaces)
```

## Getting Started Order

1. **Setup**
   ```bash
   python project_setup.py
   ```

2. **Validation**
   ```bash
   python validate.py
   ```

3. **Learning**
   - Read `QUICKSTART.md`
   - Run `python example_usage.py`
   - Run `python complete_example.py`

4. **Deep Dive**
   - Read `README.md`
   - Examine `config.py` for customization
   - Study `recursive_agent.py` for API details
   - Check `code_agent_integration.py` for CodeAgent integration

5. **Integration**
   - Install smol-agents: `pip install smol-agents`
   - Use `RecursiveCodeAgent` and `create_codeagent_tools()`
   - Follow CodeAgent integration example in README

## Key Concepts

### File Organization
- **prompt.txt**: Task description for each agent
- **solution.py**: Generated code with typed functions
- **test_solution.py**: Pytest tests for solution.py
- **log.txt**: Progress and info messages
- **error.txt**: Failures and errors

### Naming Conventions
- **Folders**: `task_<descriptive_name>` (lowercase, underscores)
- **Functions**: Descriptive names, publicly accessible without underscore prefix
- **Private functions**: Start with underscore `_`

### Execution Flow
1. Load prompt from `prompt.txt`
2. Decompose into subtasks (or decide not to)
3. Create child agents if needed
4. Generate `solution.py` with typed functions
5. Generate `test_solution.py` with pytest tests
6. Run tests and validate
7. If child fails: diagnose → retry with guidance → escalate
8. Parent imports and calls child functions

### Timeout Strategy
- Parents estimate child complexity
- Set timeout when creating child: `expected_timeout=seconds`
- Minimum 30s, maximum 3600s
- Configurable per-agent for flexibility

### Error Handling
- Child fails → errors written to `error.txt`
- Parent diagnoses child with `get_child_diagnostics()`
- Parent retries child with `retry_child_agent()` (up to max_retries)
- Each attempt recorded in `attempt_history` with code, test output, and errors
- Timeouts caught and logged
- Test failures recorded and reported
- If retries exhausted: `reset_child_agent()` with `preserve_history=True`, or parent absorbs the task

## File Dependencies

```
recursive_agent.py
├── depends on: config.py, logger.py
└── imports: pathlib, subprocess, sys, inspect, json

code_agent_integration.py
├── depends on: recursive_agent.py, config.py
└── imports: recursive_agent, config

logger.py
├── depends on: config.py
└── imports: json, pathlib, datetime, sys

example_usage.py
├── depends on: recursive_agent.py, code_agent_integration.py, config.py
└── imports: smol_agents (optional)

complete_example.py
├── depends on: recursive_agent.py, code_agent_integration.py, config.py
└── imports: smol_agents (optional)
```

## Extending the System

To add features:
1. **New agent tools**: Add method to `RecursiveCodeAgent`, expose in `create_codeagent_tools()`
2. **New logging**: Add methods to `AgentLogger`
3. **New configuration**: Add to `config.py`
4. **New commands**: Add to `recursive_agent.py` methods

All components are designed to be extensible without breaking existing code.

## License & Usage

- Recursive Code Agent system
- Built for task decomposition and code generation
- Integrates with SmolAgents CodeAgent
- Fully documented and exemplified
- Ready for production use with customization
