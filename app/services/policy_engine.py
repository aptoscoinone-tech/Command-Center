"""Policy Engine: Enforces Kill Switch states, risk boundaries, and Circuit Breaker gates."""

from typing import Tuple, Optional
from app.models import KillSwitchState, RiskLevel, FailureType


class PolicyEngine:
    _instance: Optional["PolicyEngine"] = None

    def __init__(self, initial_kill_switch: KillSwitchState = KillSwitchState.NORMAL):
        self.kill_switch_state = initial_kill_switch

    @classmethod
    def get_instance(cls) -> "PolicyEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_kill_switch(self, new_state: KillSwitchState) -> None:
        self.kill_switch_state = new_state

    def check_execution_allowed(
        self,
        capability: str,
        risk: RiskLevel,
        is_circuit_open: bool = False
    ) -> Tuple[bool, Optional[str], Optional[FailureType]]:
        """
        Validates if a capability execution is permitted under current system policies.
        Returns: (is_allowed, denial_reason, failure_classification)
        """
        # 1. EMERGENCY_STOP: All capabilities blocked
        if self.kill_switch_state == KillSwitchState.EMERGENCY_STOP:
            return (
                False,
                "Policy Denied: Kill Switch is engaged (EMERGENCY_STOP). All operations halted.",
                FailureType.POLICY_VIOLATION
            )

        # 2. READ_ONLY: YELLOW and RED capabilities blocked
        if self.kill_switch_state == KillSwitchState.READ_ONLY:
            if risk in (RiskLevel.YELLOW, RiskLevel.RED):
                return (
                    False,
                    f"Policy Denied: System is in READ_ONLY mode. Cannot execute {risk} capability '{capability}'.",
                    FailureType.POLICY_VIOLATION
                )

        # 3. Circuit Breaker gate
        if is_circuit_open and capability != "infrastructure.health.read":
            return (
                False,
                "Circuit Breaker: Target server circuit is OPEN. Fast failing to prevent cascade.",
                FailureType.TRANSIENT
            )

        return True, None, None
