"""Multi-Step Planner (M5): Decomposes complex operational workflows into DAG steps."""

import uuid
from typing import List
from app.models import ExecutionPlan, ExecutionPlanStep, RiskLevel


class MultiStepPlanner:
    @staticmethod
    def plan_workflow(goal: str, target_server: str = "apricot") -> ExecutionPlan:
        plan_id = f"mplan_{uuid.uuid4().hex[:8]}"
        steps: List[ExecutionPlanStep] = []

        # Step 1: Pre-flight health check
        step_1_id = f"step_preflight_{uuid.uuid4().hex[:4]}"
        steps.append(
            ExecutionPlanStep(
                step_id=step_1_id,
                capability="infrastructure.health.read",
                params={"server_id": target_server},
                risk=RiskLevel.GREEN,
                depends_on=[]
            )
        )

        # Step 2: Deep Audit (depends on Step 1)
        step_2_id = f"step_audit_{uuid.uuid4().hex[:4]}"
        steps.append(
            ExecutionPlanStep(
                step_id=step_2_id,
                capability="infrastructure.audit.execute",
                params={"server_id": target_server, "deep_scan": True},
                risk=RiskLevel.YELLOW,
                depends_on=[step_1_id]
            )
        )

        # Step 3: Disk verification (parallel or sequential)
        step_3_id = f"step_disk_{uuid.uuid4().hex[:4]}"
        steps.append(
            ExecutionPlanStep(
                step_id=step_3_id,
                capability="infrastructure.disk.check",
                params={"server_id": target_server},
                risk=RiskLevel.GREEN,
                depends_on=[step_1_id]
            )
        )

        return ExecutionPlan(plan_id=plan_id, intent="multi_step_workflow", steps=steps)
