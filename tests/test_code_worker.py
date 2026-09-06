"""Unit tests for Code Worker (M3)."""

import asyncio
from app.workers.code import CodeWorker
from app.executors.code import CodeExecutor


def test_code_executor_sandbox():
    executor = CodeExecutor()
    code = "def add(a, b): return a + b"
    tests = "assert add(2, 3) == 5\nassert add(-1, 1) == 0"
    res = executor.run_tests(code, tests)
    assert res["passed"] is True
    assert res["error"] is None


def test_code_worker_full_flow():
    worker = CodeWorker()
    loop = asyncio.new_event_loop()
    res = loop.run_until_complete(worker.handle_coder_task("Парсинг логов nginx"))
    assert "parse_nginx_logs" in res["code"]
    assert res["test_result"]["passed"] is True
    assert res["review"]["is_secure"] is True


if __name__ == "__main__":
    test_code_executor_sandbox()
    test_code_worker_full_flow()
    print("All Code Worker tests passed successfully!")
