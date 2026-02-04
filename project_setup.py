#!/usr/bin/env python
"""
Project setup script for initializing the recursive code agent system.
Prepares the workspace and validates installation.
"""

import sys
import subprocess
from pathlib import Path


def install_dependencies() -> bool:
    """Install project dependencies."""
    print("Installing dependencies...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("Dependencies installed successfully")
            return True
        else:
            print("Failed to install dependencies")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False


def create_agents_directory() -> bool:
    """Create the agents directory."""
    print("Creating agents directory...", end=" ")

    agents_dir = Path("agents")
    agents_dir.mkdir(exist_ok=True)

    print(f"{agents_dir}/")
    return True


def create_initial_task() -> bool:
    """Optionally create an initial task."""
    print("\nWould you like to create an initial task? (y/n): ", end="")

    try:
        response = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nSkipping initial task creation")
        return False

    if response != "y":
        return False

    root_dir = Path("agents/root")
    root_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = root_dir / "prompt.txt"
    if prompt_file.exists():
        print(f"Prompt already exists at {prompt_file}")
        return False

    print("Enter your task description (type 'END' on a new line to finish):\n")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled")
            return False

    task = "\n".join(lines).strip()

    if not task:
        print("No task provided")
        return False

    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(task)

    print(f"Task saved to {prompt_file}")
    return True


def run_validation() -> bool:
    """Run validation checks."""
    print("\nRunning validation checks...\n")

    try:
        result = subprocess.run(
            [sys.executable, "validate.py"],
            capture_output=False,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running validation: {e}")
        return False


def show_next_steps() -> None:
    """Show next steps."""
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60 + "\n")

    print("Next steps:")
    print("  1. Read QUICKSTART.md for getting started")
    print("  2. Review README.md for full documentation")
    print("  3. Run examples:")
    print("       python example_usage.py")
    print("       python complete_example.py")
    print("\nUseful commands:")
    print("  # Validate installation anytime")
    print("  python validate.py")
    print("\n  # View your task")
    print("  cat agents/root/prompt.txt")
    print("\n  # View logs")
    print("  tail -f agents/root/log.txt")
    print()


def main() -> int:
    """Run setup."""

    print("\n" + "=" * 60)
    print("RECURSIVE CODE AGENT - SETUP")
    print("=" * 60 + "\n")

    # Check if already in a git repo
    if not Path(".git").exists() and not Path("pyproject.toml").exists():
        print("Warning: This doesn't look like the recursive-coder directory")
        print("Make sure you're in the recursive-coder project root\n")

    # Install dependencies
    if not install_dependencies():
        print("\nSetup failed at dependency installation")
        return 1

    # Create directories
    print()
    if not create_agents_directory():
        return 1

    # Create initial task
    create_initial_task()

    # Run validation
    print()
    if not run_validation():
        print("\nSetup completed but validation failed")
        print("Please check the errors above")
        return 1

    # Show next steps
    show_next_steps()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
