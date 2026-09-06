"""Circuit Breaker Service (ADR-013): Per-server failure tracking and circuit state management."""

import time
from typing import Dict, Any, Optional
from app.models import CircuitState, FailureType


class CircuitBreaker:
    _instance: Optional["CircuitBreaker"] = None

    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        # server_id -> {"state": CircuitState, "failures": int, "last_failure_time": float, "last_error": str}
        self._circuits: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> "CircuitBreaker":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_server(self, server_id: str) -> Dict[str, Any]:
        if server_id not in self._circuits:
            self._circuits[server_id] = {
                "state": CircuitState.CLOSED,
                "failures": 0,
                "last_failure_time": 0.0,
                "last_error": None,
                "successes_in_probe": 0
            }
        return self._circuits[server_id]

    def get_state(self, server_id: str) -> CircuitState:
        c = self._ensure_server(server_id)
        now = time.time()
        # If OPEN and recovery timeout passed, transition to HALF_OPEN
        if c["state"] == CircuitState.OPEN:
            if now - c["last_failure_time"] >= self.recovery_timeout_sec:
                c["state"] = CircuitState.HALF_OPEN
                c["successes_in_probe"] = 0
        return c["state"]

    def can_execute(self, server_id: str) -> bool:
        state = self.get_state(server_id)
        return state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    def record_success(self, server_id: str) -> None:
        c = self._ensure_server(server_id)
        if c["state"] == CircuitState.HALF_OPEN:
            c["successes_in_probe"] += 1
            if c["successes_in_probe"] >= 2:
                c["state"] = CircuitState.CLOSED
                c["failures"] = 0
                c["last_error"] = None
        elif c["state"] == CircuitState.CLOSED:
            c["failures"] = max(0, c["failures"] - 1)

    def record_failure(self, server_id: str, failure_type: FailureType, error_msg: str = "") -> None:
        """
        ADR-013 Classification:
        - TRANSIENT: Increments circuit failure counter.
        - SECURITY: Alert immediately, do NOT count in circuit breaker.
        - LOCAL_RESOURCE: Alert host limits, do NOT count.
        - POLICY_VIOLATION: Kill switch/rule block, do NOT count.
        """
        c = self._ensure_server(server_id)
        c["last_error"] = error_msg
        c["last_failure_time"] = time.time()

        if failure_type == FailureType.TRANSIENT:
            c["failures"] += 1
            if c["failures"] >= self.failure_threshold:
                c["state"] = CircuitState.OPEN
        elif c["state"] == CircuitState.HALF_OPEN:
            # Any failure during half-open pushes back to OPEN
            c["state"] = CircuitState.OPEN

    def get_status(self, server_id: str) -> Dict[str, Any]:
        c = self._ensure_server(server_id)
        current_state = self.get_state(server_id)
        return {
            "server_id": server_id,
            "state": current_state.value,
            "failures_in_window": c["failures"],
            "last_error": c["last_error"],
            "last_failure_time": c["last_failure_time"] if c["last_failure_time"] > 0 else None
        }

    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        return {server_id: self.get_status(server_id) for server_id in self._circuits.keys()}
