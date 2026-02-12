"""Logging utilities for recursive code agent."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class AgentLogger:
    """Logger for agent operations with both file and console output."""

    _COLOR_MAP = {
        "INFO": "\x1b[36m",
        "WARNING": "\x1b[33m",
        "DEBUG": "\x1b[35m",
        "ERROR": "\x1b[31m",
        "CRITICAL": "\x1b[31;1m",
    }
    _COLOR_RESET = "\x1b[0m"

    def __init__(self, agent_dir: Path, agent_name: str = "Agent"):
        self.agent_dir = Path(agent_dir)
        self.agent_name = agent_name
        self.log_file = self.agent_dir / "log.txt"
        self.error_file = self.agent_dir / "error.txt"
        self.test_results_file = self.agent_dir / "test_results.json"
        
        # Ensure directory exists
        self.agent_dir.mkdir(parents=True, exist_ok=True)

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now().isoformat()

    def _write_log(self, file_path: Path, level: str, message: str, console: bool = True):
        """Write log entry to file and optionally console."""
        timestamp = self._get_timestamp()
        log_entry = f"[{timestamp}] [{level:8s}] {message}\n"
        
        # Write to file
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # Write to console
        if console:
            prefix = f"[{self.agent_name}] "
            use_color = os.getenv("AGENT_COLOR", "").strip().lower() in {"1", "true", "yes"}
            if use_color and level in self._COLOR_MAP:
                colored = f"{self._COLOR_MAP[level]}{prefix}{log_entry.rstrip()}{self._COLOR_RESET}"
                print(colored, file=sys.stdout)
            else:
                print(prefix + log_entry.rstrip(), file=sys.stdout)

    def info(self, message: str, console: bool = True):
        """Log info message."""
        self._write_log(self.log_file, "INFO", message, console)

    def warning(self, message: str, console: bool = True):
        """Log warning message."""
        self._write_log(self.log_file, "WARNING", message, console)

    def debug(self, message: str, console: bool = False):
        """Log debug message."""
        self._write_log(self.log_file, "DEBUG", message, console)

    def error(self, message: str, console: bool = True):
        """Log error message to error file."""
        self._write_log(self.error_file, "ERROR", message, console)

    def critical(self, message: str, console: bool = True):
        """Log critical error message."""
        self._write_log(self.error_file, "CRITICAL", message, console)

    def save_test_results(self, results: dict):
        """Save test results as JSON."""
        with open(self.test_results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    def load_test_results(self) -> Optional[dict]:
        """Load test results from JSON."""
        if not self.test_results_file.exists():
            return None
        with open(self.test_results_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_error_summary(self) -> str:
        """Get summary of errors from error file."""
        if not self.error_file.exists():
            return ""
        with open(self.error_file, "r", encoding="utf-8") as f:
            return f.read()

    def get_log_summary(self) -> str:
        """Get summary of logs from log file."""
        if not self.log_file.exists():
            return ""
        with open(self.log_file, "r", encoding="utf-8") as f:
            return f.read()
