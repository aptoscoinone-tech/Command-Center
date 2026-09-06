"""Unit tests for Orchestrator & Policy Engine."""

import asyncio
from app.services.orchestrator import Orchestrator
from app.services.policy_engine import PolicyEngine
from app.services.planner import Planner
from app.models import IntentResult, RiskLevel, KillSwitchState, FailureType


def test_orchestrator_normal_execution():
    policy = PolicyEngine(KillSwitchState.NORMAL)
    orch = Orchestrator(policy)

    intent = IntentResult(
        intent="infrastructure.health.read",
        risk=RiskLevel.GREEN,
        required_capabilities=["infrastructure.health.read"],
        target_server="apricot"
    )
    plan = Planner.plan(intent)

    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(orch.execute_plan(plan))

    assert len(results) == 1
    assert results[0].success is True
    assert results[0].data["server_id"] == "apricot"
    assert results[0].data["status"] == "GREEN"


def test_orchestrator_kill_switch_blocking():
    policy = PolicyEngine(KillSwitchState.EMERGENCY_STOP)
    orch = Orchestrator(policy)

    intent = IntentResult(
        intent="infrastructure.health.read",
        risk=RiskLevel.GREEN,
        required_capabilities=["infrastructure.health.read"]
    )
    plan = Planner.plan(intent)

    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(orch.execute_plan(plan))

    assert len(results) == 1
    assert results[0].success is False
    assert results[0].failure_type == FailureType.POLICY_VIOLATION
    assert "Kill Switch" in results[0].error


if __name__ == "__main__":
    test_orchestrator_normal_execution()
    test_orchestrator_kill_switch_blocking()
    print("All Orchestrator tests passed successfully!")
