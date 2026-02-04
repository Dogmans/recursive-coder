"""
Complete example demonstrating recursive code agent with SmolAgents CodeAgent.

This example shows how to integrate the recursive agent system with SmolAgents.
In practice, you would replace the model_id with your actual model.
"""

import sys
import json
from pathlib import Path
from typing import Optional

# Uncomment when smol_agents is installed
# from smol_agents import CodeAgent

from recursive_agent import RecursiveAgent
from code_agent_integration import RecursiveCodeAgent, create_codeagent_tools
import config


def setup_root_agent(task_description: Optional[str] = None) -> RecursiveAgent:
    """Set up and initialize the root agent.
    
    Args:
        task_description: Optional task to write to prompt.txt
        
    Returns:
        Initialized RecursiveAgent
    """
    # Create root agent directory
    root_dir = config.AGENTS_DIR / "root"
    root_dir.mkdir(parents=True, exist_ok=True)
    
    # If task provided, create prompt.txt
    if task_description:
        prompt_file = root_dir / config.PROMPT_FILE
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(task_description)
    
    # Create agent
    agent = RecursiveAgent(
        agent_dir=root_dir,
        agent_name="RootAgent",
        timeout_seconds=config.DEFAULT_TIMEOUT,
        max_retries=config.DEFAULT_MAX_RETRIES,
    )
    
    return agent


def demonstrate_agent_creation():
    """Demonstrate creating and configuring a recursive agent."""
    
    print("\n" + "="*70)
    print("RECURSIVE CODE AGENT - DEMONSTRATION")
    print("="*70 + "\n")
    
    # Example task
    example_task = """
Create a Python module for data transformation and validation.

The module should have:
1. A function to load data from JSON
2. A function to validate data against a schema
3. A function to transform/clean the data
4. A function to export results

Each function should be thoroughly tested.
"""
    
    print("Setting up root agent with example task...")
    agent = setup_root_agent(example_task.strip())
    
    # Execute agent initialization
    result = agent.execute()
    
    if not result["success"]:
        print(f"Error: {result.get('error')}")
        return None
    
    print(f"\n✓ Root agent initialized")
    print(f"  Location: {agent.agent_dir}")
    print(f"  Prompt saved: {agent.prompt_file}")
    
    return agent


def demonstrate_child_creation(agent: RecursiveAgent):
    """Demonstrate creating child agents."""
    
    print("\n" + "-"*70)
    print("CREATING CHILD AGENTS")
    print("-"*70 + "\n")
    
    # Create first child
    child1 = agent.create_child_agent(
        child_name="JSON Data Loader",
        task_description="Implement a function to load and parse JSON data with error handling",
        expected_timeout=120,
    )
    print(f"✓ Created child agent: {child1.agent_dir.name}")
    
    # Create second child
    child2 = agent.create_child_agent(
        child_name="Data Validator",
        task_description="Implement validation logic to check data against a schema",
        expected_timeout=120,
    )
    print(f"✓ Created child agent: {child2.agent_dir.name}")
    
    # Create third child
    child3 = agent.create_child_agent(
        child_name="Data Transformer",
        task_description="Implement data transformation and cleaning functions",
        expected_timeout=150,
    )
    print(f"✓ Created child agent: {child3.agent_dir.name}")
    
    return [child1, child2, child3]


def demonstrate_solution_submission(agent: RecursiveAgent):
    """Demonstrate submitting and validating a solution."""
    
    print("\n" + "-"*70)
    print("SOLUTION SUBMISSION AND VALIDATION")
    print("-"*70 + "\n")
    
    # Example solution code
    solution_code = '''"""Data transformation and validation module."""

import json
from typing import Any, Dict, List


def load_json_data(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_schema(data: Dict[str, Any], schema: Dict[str, str]) -> bool:
    """Validate data against a schema.
    
    Args:
        data: Data to validate
        schema: Schema with type requirements
        
    Returns:
        True if valid, False otherwise
    """
    for key, expected_type in schema.items():
        if key not in data:
            return False
        if not isinstance(data[key], eval(expected_type)):
            return False
    return True


def transform_data(raw_data: List[Dict]) -> List[Dict]:
    """Transform and clean data.
    
    Args:
        raw_data: Raw input data
        
    Returns:
        Transformed data with cleaned values
    """
    transformed = []
    for item in raw_data:
        clean_item = {k: str(v).strip() for k, v in item.items()}
        transformed.append(clean_item)
    return transformed


def export_results(data: List[Dict], output_file: str) -> bool:
    """Export results to a JSON file.
    
    Args:
        data: Data to export
        output_file: Output file path
        
    Returns:
        True if successful
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False
'''
    
    # Example test code
    test_code = '''"""Tests for solution module."""

import pytest
import json
import tempfile
import os
from solution import (
    load_json_data,
    validate_schema,
    transform_data,
    export_results,
)


def test_load_json_data():
    """Test JSON loading."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"key": "value"}, f)
        temp_file = f.name
    
    try:
        data = load_json_data(temp_file)
        assert data == {"key": "value"}
    finally:
        os.unlink(temp_file)


def test_validate_schema():
    """Test schema validation."""
    data = {"name": "test", "age": 30}
    schema = {"name": "str", "age": "int"}
    assert validate_schema(data, schema) is True


def test_transform_data():
    """Test data transformation."""
    raw = [{"name": "  John  ", "city": "NYC  "}]
    result = transform_data(raw)
    assert result[0]["name"] == "John"
    assert result[0]["city"] == "NYC"


def test_export_results():
    """Test exporting results."""
    data = [{"id": 1, "value": "test"}]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        success = export_results(data, temp_file)
        assert success is True
        
        with open(temp_file, 'r') as f:
            exported = json.load(f)
        assert exported == data
    finally:
        os.unlink(temp_file)
'''
    
    # Submit solution
    print("Submitting example solution...")
    wrapper = RecursiveCodeAgent(agent)
    result = wrapper.submit_solution(solution_code, test_code)
    
    print(f"\nSubmission result:")
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    if result["success"]:
        print(f"  ✓ Solution validated and tests passed!")
    else:
        test_results = result.get("test_results", {})
        print(f"  ✗ Test details: {test_results.get('stderr', 'Unknown error')}")
    
    return result


def demonstrate_function_discovery(agent: RecursiveAgent):
    """Demonstrate discovering and calling child functions."""
    
    print("\n" + "-"*70)
    print("FUNCTION DISCOVERY")
    print("-"*70 + "\n")
    
    # First, ensure there's a solution in the agent
    wrapper = RecursiveCodeAgent(agent)
    
    # Get information about functions (example)
    print("Functions available in root agent's solution.py:")
    solution_file = agent.solution_file
    if solution_file.exists():
        import inspect
        import importlib.util
        
        try:
            spec = importlib.util.spec_from_file_location("solution", solution_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and not name.startswith("_"):
                    sig = inspect.signature(obj)
                    print(f"\n  ✓ {name}{sig}")
                    doc = inspect.getdoc(obj)
                    if doc:
                        # Print first line of docstring
                        first_line = doc.split('\n')[0]
                        print(f"    {first_line}")
        except Exception as e:
            print(f"  (Could not introspect: {e})")
    else:
        print("  (No solution.py yet)")


def demonstrate_logging(agent: RecursiveAgent):
    """Demonstrate logging output."""
    
    print("\n" + "-"*70)
    print("LOGGING AND MONITORING")
    print("-"*70 + "\n")
    
    print(f"Log file location: {agent.logger.log_file}")
    print(f"Error file location: {agent.logger.error_file}")
    
    # Show recent logs
    log_content = agent.logger.get_log_summary()
    if log_content:
        print(f"\nRecent log entries:")
        lines = log_content.split('\n')[-5:]
        for line in lines:
            if line.strip():
                print(f"  {line}")
    
    error_content = agent.logger.get_error_summary()
    if error_content:
        print(f"\nRecent errors:")
        lines = error_content.split('\n')[-3:]
        for line in lines:
            if line.strip():
                print(f"  {line}")


def demonstrate_codeagent_integration():
    """Demonstrate how to integrate with SmolAgents CodeAgent."""
    
    print("\n" + "="*70)
    print("CODEAGENT INTEGRATION EXAMPLE")
    print("="*70 + "\n")
    
    print("""
To integrate with SmolAgents CodeAgent, you would do:

```python
from smol_agents import CodeAgent
from code_agent_integration import RecursiveCodeAgent, create_codeagent_tools
from recursive_agent import RecursiveAgent

# Set up your recursive agent
agent = RecursiveAgent(agent_dir=Path("agents/root"))
wrapper = RecursiveCodeAgent(agent)

# Create tools for CodeAgent
tools = create_codeagent_tools(wrapper)

# Initialize CodeAgent with the tools
code_agent = CodeAgent(
    tools=tools,
    model_id="gpt-4-turbo",  # or your model
    verbosity_level=2,
    system_prompt=wrapper.get_system_prompt(),
)

# Execute the task
user_prompt = wrapper.get_user_prompt()
response = code_agent.run(user_prompt)
```

Available tools for CodeAgent:
  • decompose_task: Analyze task complexity
  • create_subtask: Spawn child agents  
  • submit_solution: Save and validate code
  • get_child_solution: Import child's module
  • get_child_info: Introspect child functions
  • execute_child_function: Call child functions
  • report_child_progress: Check child status
""")


def main():
    """Run the demonstration."""
    
    try:
        # Set up root agent
        agent = demonstrate_agent_creation()
        if not agent:
            return 1
        
        # Demonstrate child creation
        children = demonstrate_child_creation(agent)
        
        # Demonstrate solution submission
        demonstrate_solution_submission(agent)
        
        # Demonstrate function discovery
        demonstrate_function_discovery(agent)
        
        # Demonstrate logging
        demonstrate_logging(agent)
        
        # Demonstrate CodeAgent integration
        demonstrate_codeagent_integration()
        
        print("\n" + "="*70)
        print("DEMONSTRATION COMPLETE")
        print("="*70)
        print(f"\nAgent workspace: {agent.agent_dir}")
        print("Next steps:")
        print("  1. Review README.md for full documentation")
        print("  2. Install smol_agents: pip install smol-agents")
        print("  3. Integrate with your CodeAgent instance")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
