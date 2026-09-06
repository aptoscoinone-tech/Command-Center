"""Unit tests for Capability Registry & Execution Planning."""

from app.services.intent_router import IntentRouter
from app.services.planner import Planner
from app.models import IntentResult, RiskLevel


def test_planner_single_step():
    intent = IntentResult(
        intent="infrastructure.health.read",
        risk=RiskLevel.GREEN,
        required_capabilities=["infrastructure.health.read"],
        target_server="apricot"
    )
    plan = Planner.plan(intent)
    assert len(plan.steps) == 1
    assert plan.steps[0].capability == "infrastructure.health.read"
    assert plan.steps[0].params["server_id"] == "apricot"


def test_planner_multi_server_snapshot():
    intent = IntentResult(
        intent="system.snapshot.get",
        risk=RiskLevel.GREEN,
        required_capabilities=["infrastructure.health.read"]
    )
    plan = Planner.plan(intent)
    assert len(plan.steps) >= 3
    caps = [s.capability for s in plan.steps]
    assert "infrastructure.health.read" in caps
    assert "infrastructure.circuit.status" in caps
    assert "infrastructure.disk.check" in caps


if __name__ == "__main__":
    test_planner_single_step()
    test_planner_multi_server_snapshot()
    print("All Planner & Registry tests passed successfully!")
