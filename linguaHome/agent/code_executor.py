"""
LinguaHome Code Executor

Safely executes LLM-generated Python code for smart home control.
"""

import sys
import io
import traceback
from typing import Tuple, Optional
from contextlib import redirect_stdout, redirect_stderr
import signal
from pathlib import Path

# Add src directory to Python path for rh_sensors imports
_src_path = Path(__file__).parent.parent.parent / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))


class TimeoutError(Exception):
    """Code execution timeout."""
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")


# Whitelisted modules for safe execution
ALLOWED_MODULES = {
    # rh_sensors modules
    "rh_sensors",
    "rh_sensors.db",
    "rh_sensors.db.access",
    "rh_sensors.db.resolver",
    "rh_sensors.homecentre_actuators",
    "rh_sensors.homecentre_sensors",
    
    # Standard library (safe subset)
    "datetime",
    "time",
    "json",
    "math",
    "statistics",
    "collections",
    "functools",
    "itertools",
}

# Forbidden patterns in generated code
FORBIDDEN_PATTERNS = [
    "import os",
    "import subprocess",
    "import shutil",
    "import socket",
    "import urllib",
    "import requests",
    "__import__",
    "exec(",
    "eval(",
    "open(",
    "file(",
    "compile(",
    "globals(",
    "locals(",
    "vars(",
    "delattr(",
    "setattr(",
    "getattr(",
]


class CodeExecutor:
    """
    Executes LLM-generated Python code in a controlled environment.
    """
    
    def __init__(self, timeout: int = 30, safe_mode: bool = True):
        self.timeout = timeout
        self.safe_mode = safe_mode
        self._setup_namespace()
    
    def _setup_namespace(self) -> dict:
        """Create the execution namespace with allowed imports."""
        namespace = {
            "__builtins__": {
                # Safe builtins only
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "any": any,
                "all": all,
                "isinstance": isinstance,
                "type": type,
                "True": True,
                "False": False,
                "None": None,
            }
        }
        
        # Try to import real rh_sensors, fallback to mock
        try:
            from rh_sensors.db.access import Sensors
            from rh_sensors.homecentre_actuators import ZWaveHomeActuator
            from rh_sensors.homecentre_sensors import ZWaveHomeSensor
            from rh_sensors.db.resolver import StateResolver
            
            namespace["Sensors"] = Sensors
            namespace["ZWaveHomeActuator"] = ZWaveHomeActuator
            namespace["ZWaveHomeSensor"] = ZWaveHomeSensor
            namespace["StateResolver"] = StateResolver
            self._using_mock = False
        except (ImportError, ModuleNotFoundError) as e:
            # Use mock sensors instead
            try:
                from linguaHome.mock_sensors import Sensors, ZWaveHomeActuator, ZWaveHomeSensor
                namespace["Sensors"] = Sensors
                namespace["ZWaveHomeActuator"] = ZWaveHomeActuator
                namespace["ZWaveHomeSensor"] = ZWaveHomeSensor
                self._using_mock = True
            except ImportError:
                print(f"Warning: Could not import sensors (neither real nor mock): {e}")
                self._using_mock = True
        
        # Import datetime for convenience
        from datetime import datetime, timedelta
        namespace["datetime"] = datetime
        namespace["timedelta"] = timedelta
        
        import json
        namespace["json"] = json
        
        return namespace
    
    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code for safety before execution.
        
        Returns:
            (is_safe, error_message)
        """
        if not self.safe_mode:
            return True, None
        
        # Check for forbidden patterns
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in code:
                return False, f"Forbidden pattern detected: {pattern}"
        
        # Basic syntax check
        try:
            compile(code, "<generated>", "exec")
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        return True, None
    
    def execute(self, code: str) -> Tuple[bool, str, str]:
        """
        Execute the given Python code.
        
        Args:
            code: Python code to execute
            
        Returns:
            (success, stdout, stderr)
        """
        # Validate first
        is_safe, error = self.validate_code(code)
        if not is_safe:
            return False, "", f"Code validation failed: {error}"
        
        # Capture stdout/stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create fresh namespace
        namespace = self._setup_namespace()
        
        try:
            # Set timeout (Unix only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout)
            
            # Execute with captured output
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)
            
            # Clear alarm
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()
            
            return True, stdout, stderr
            
        except TimeoutError:
            return False, "", f"Execution timed out after {self.timeout} seconds"
        except Exception as e:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            error_msg = traceback.format_exc()
            return False, stdout_capture.getvalue(), error_msg
    
    def extract_code_from_response(self, llm_response: str) -> Optional[str]:
        """
        Extract Python code from LLM response.
        Handles ```python ... ``` blocks.
        """
        # Look for ```python ... ``` blocks
        if "```python" in llm_response:
            start = llm_response.find("```python") + len("```python")
            end = llm_response.find("```", start)
            if end > start:
                return llm_response[start:end].strip()
        
        # Look for ``` ... ``` blocks (generic)
        if "```" in llm_response:
            parts = llm_response.split("```")
            if len(parts) >= 3:
                return parts[1].strip()
        
        return None


# Singleton instance
_executor: Optional[CodeExecutor] = None


def get_executor(timeout: int = 30, safe_mode: bool = True) -> CodeExecutor:
    """Get or create the code executor instance."""
    global _executor
    if _executor is None:
        _executor = CodeExecutor(timeout=timeout, safe_mode=safe_mode)
    return _executor


if __name__ == "__main__":
    # Test the executor
    executor = CodeExecutor(safe_mode=True)
    
    # Test 1: Simple print
    success, stdout, stderr = executor.execute('print("Hello, LinguaHome!")')
    print(f"Test 1: success={success}, output={stdout.strip()}")
    
    # Test 2: Sensor query (will fail without database)
    code = """
from rh_sensors.db.access import Sensors
sensors = Sensors()
print(f"Found {len(sensors.findSensors())} sensors")
"""
    success, stdout, stderr = executor.execute(code)
    print(f"Test 2: success={success}, output={stdout.strip() if stdout else stderr[:100]}")
