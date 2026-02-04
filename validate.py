"""
Validation script to ensure the recursive agent system is properly installed.
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version is 3.10+."""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (requires 3.10+)")
        return False


def check_dependencies():
    """Check required dependencies are installed."""
    print("Checking dependencies...", end=" ")
    
    required = [
        "pathlib",
        "json",
        "subprocess",
        "inspect",
    ]
    
    optional = [
        "smol_agents",
        "pytest",
    ]
    
    missing = []
    for pkg in optional:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    
    if not missing:
        print("✓ All optional packages installed")
        return True
    else:
        print(f"⚠ Missing optional: {', '.join(missing)}")
        print("  Install with: pip install -e .")
        return False


def check_project_structure():
    """Check project files exist."""
    print("Checking project structure...", end=" ")
    
    required_files = [
        "config.py",
        "logger.py",
        "recursive_agent.py",
        "code_agent_integration.py",
        "pyproject.toml",
        "README.md",
        "QUICKSTART.md",
    ]
    
    missing = []
    for f in required_files:
        if not Path(f).exists():
            missing.append(f)
    
    if not missing:
        print("✓ All core files present")
        return True
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        return False


def check_imports():
    """Test that all modules can be imported."""
    print("Testing imports...", end=" ")
    
    try:
        import config
        import logger
        import recursive_agent
        import code_agent_integration
        
        print("✓ All modules importable")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_agent_creation():
    """Test basic agent creation."""
    print("Testing agent creation...", end=" ")
    
    try:
        from pathlib import Path
        from recursive_agent import RecursiveAgent
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = RecursiveAgent(
                agent_dir=Path(tmpdir),
                agent_name="TestAgent"
            )
            
            if agent.agent_dir.exists():
                print("✓ Agent can be created")
                return True
            else:
                print("✗ Agent directory not created")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_logger():
    """Test logger functionality."""
    print("Testing logger...", end=" ")
    
    try:
        from pathlib import Path
        from logger import AgentLogger
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(Path(tmpdir), "TestLogger")
            logger.info("Test message")
            
            if logger.log_file.exists():
                print("✓ Logger works")
                return True
            else:
                print("✗ Log file not created")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_codeagent_integration():
    """Test CodeAgent integration."""
    print("Testing CodeAgent integration...", end=" ")
    
    try:
        from pathlib import Path
        from recursive_agent import RecursiveAgent
        from code_agent_integration import RecursiveCodeAgent, create_codeagent_tools
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            agent = RecursiveAgent(agent_dir=Path(tmpdir))
            wrapper = RecursiveCodeAgent(agent)
            tools = create_codeagent_tools(wrapper)
            
            if isinstance(tools, dict) and len(tools) > 0:
                print(f"✓ {len(tools)} tools available")
                return True
            else:
                print("✗ No tools created")
                return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_example_files():
    """Check example files exist."""
    print("Checking example files...", end=" ")
    
    examples = [
        "example_usage.py",
        "complete_example.py",
    ]
    
    missing = []
    for f in examples:
        if not Path(f).exists():
            missing.append(f)
    
    if not missing:
        print("✓ All examples present")
        return True
    else:
        print(f"⚠ Missing examples: {', '.join(missing)}")
        return False


def main():
    """Run all validation checks."""
    
    print("\n" + "="*60)
    print("RECURSIVE CODE AGENT - VALIDATION")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Imports", check_imports),
        ("Agent Creation", test_agent_creation),
        ("Logger", test_logger),
        ("CodeAgent Integration", test_codeagent_integration),
        ("Examples", check_example_files),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"RESULTS: {passed}/{total} checks passed\n")
    
    if passed == total:
        print("✓ System is ready to use!")
        print("\nNext steps:")
        print("  1. Read QUICKSTART.md for getting started")
        print("  2. Run: python example_usage.py")
        print("  3. Run: python complete_example.py")
        return 0
    else:
        print("✗ Some checks failed. See above for details.\n")
        print("To fix:")
        print("  1. Ensure Python 3.10+ is installed")
        print("  2. Install dependencies: pip install -e .")
        print("  3. Check all files are present")
        return 1


if __name__ == "__main__":
    sys.exit(main())
