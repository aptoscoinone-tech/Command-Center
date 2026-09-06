"""Planner: Converts classified intent into concrete ExecutionPlan steps."""

import uuid
from typing import Dict, Any
from app.models import IntentResult, ExecutionPlan, ExecutionPlanStep, RiskLevel


class Planner:
    @staticmethod
    def plan(intent: IntentResult) -> ExecutionPlan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        steps = []

        if intent.intent in ("infrastructure.health.read", "infrastructure.health.check"):
            server = intent.target_server or "apricot"
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:6]}",
                    capability="infrastructure.health.read",
                    params={"server_id": server},
                    risk=RiskLevel.GREEN,
                    requires_approval=False
                )
            )

        elif intent.intent == "infrastructure.health.read_all":
            for s in ["apricot", "peach", "berry"]:
                steps.append(
                    ExecutionPlanStep(
                        step_id=f"step_{uuid.uuid4().hex[:6]}",
                        capability="infrastructure.health.read",
                        params={"server_id": s},
                        risk=RiskLevel.GREEN,
                        requires_approval=False
                    )
                )

        elif intent.intent == "infrastructure.audit.execute":
            server = intent.target_server or "apricot"
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:6]}",
                    capability="infrastructure.audit.execute",
                    params={"server_id": server, "deep_scan": True},
                    risk=RiskLevel.YELLOW,
                    requires_approval=False
                )
            )

        elif intent.intent == "infrastructure.disk.check":
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:6]}",
                    capability="infrastructure.disk.check",
                    params={"server_id": intent.target_server},
                    risk=RiskLevel.GREEN,
                    requires_approval=False
                )
            )

        elif intent.intent == "infrastructure.circuit.status":
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:6]}",
                    capability="infrastructure.circuit.status",
                    params={},
                    risk=RiskLevel.GREEN,
                    requires_approval=False
                )
            )

        elif intent.intent == "code.task.generate_and_review":
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:6]}",
                    capability="code.task.generate_and_review",
                    params={"prompt": intent.params.get("raw_query", "")},
                    risk=RiskLevel.YELLOW,
                    requires_approval=False
                )
            )

        elif intent.intent == "research.web.investigate":
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:6]}",
                    capability="research.web.investigate",
                    params={"query": intent.params.get("raw_query", "")},
                    risk=RiskLevel.GREEN,
                    requires_approval=False
                )
            )

        elif intent.intent == "system.snapshot.get":
            # Compose multi-capability snapshot
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_health",
                    capability="infrastructure.health.read",
                    params={"server_id": "all"},
                    risk=RiskLevel.GREEN
                )
            )
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_circuit",
                    capability="infrastructure.circuit.status",
                    params={},
                    risk=RiskLevel.GREEN
                )
            )
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_disk",
                    capability="infrastructure.disk.check",
                    params={},
                    risk=RiskLevel.GREEN
                )
            )

        else:
            # Fallback single step
            steps.append(
                ExecutionPlanStep(
                    step_id=f"step_{uuid.uuid4().hex[:6]}",
                    capability="infrastructure.health.read",
                    params={"server_id": intent.target_server or "apricot"},
                    risk=RiskLevel.GREEN
                )
            )

        return ExecutionPlan(plan_id=plan_id, intent=intent.intent, steps=steps)
