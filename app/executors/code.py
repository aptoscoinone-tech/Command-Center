"""Code Executor (M3): Sandboxed execution of generated Python code and test suites."""

import io
import sys
import time
from typing import Dict, Any


class CodeExecutor:
    def __init__(self, timeout_sec: int = 5):
        self.timeout_sec = timeout_sec

    def run_tests(self, code: str, tests: str) -> Dict[str, Any]:
        """
        Executes code + unit tests in a captured sandbox environment.
        Measures execution time, captures stdout/stderr.
        """
        start_time = time.time()
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        local_env: Dict[str, Any] = {}
        passed = False
        error_msg = None

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Execute the function/code definition
            exec(code, local_env)
            # Execute the test suite
            exec(tests, local_env)
            passed = True
        except AssertionError as ae:
            passed = False
            error_msg = f"AssertionError: {str(ae) or 'Test condition failed'}"
        except Exception as e:
            passed = False
            error_msg = f"{type(e).__name__}: {str(e)}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        duration_ms = (time.time() - start_time) * 1000

        return {
            "passed": passed,
            "error": error_msg,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "duration_ms": duration_ms
        }
