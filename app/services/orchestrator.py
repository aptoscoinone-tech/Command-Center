"""Orchestrator: Executes plans sequentially, invokes genuine services, and gathers Machine Facts."""

import time
from typing import Dict, Any, List
from app.models import (
    ExecutionPlan,
    CapabilityResult,
    FailureType,
    RiskLevel
)
from app.services.policy_engine import PolicyEngine
from app.services.health_model import HealthModel
from app.services.circuit_breaker import CircuitBreaker
from app.services.disk_monitor import DiskMonitor
from app.services.system_snapshot import SystemSnapshotService
from app.executors.ssh import SSHExecutor
from app.workers.audit import AuditWorker
from app.workers.code import CodeWorker
from app.workers.web_search import WebSearchWorker


class Orchestrator:
    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
        self.circuit_breaker = CircuitBreaker.get_instance()

    async def execute_step(
        self,
        step_capability: str,
        params: Dict[str, Any],
        risk: RiskLevel
    ) -> CapabilityResult:
        start_time = time.time()
        server_id = params.get("server_id", "apricot")

        # 1. Policy check (Kill Switch & Risk constraints)
        allowed, reason, fail_type = self.policy_engine.check_execution_allowed(
            capability=step_capability,
            risk=risk
        )
        if not allowed:
            return CapabilityResult(
                capability=step_capability,
                success=False,
                data={},
                error=reason,
                failure_type=fail_type or FailureType.POLICY_VIOLATION,
                execution_time_ms=(time.time() - start_time) * 1000
            )

        # 2. Real service execution (No hardcoded server profiles)
        try:
            if step_capability in ("infrastructure.health.read", "infrastructure.health.check"):
                facts = await HealthModel.get_server_health(server_id)
                if facts.get("error") and facts.get("status") == "RED":
                    return CapabilityResult(
                        capability=step_capability,
                        success=False,
                        data=facts,
                        error=facts.get("error"),
                        failure_type=FailureType.TRANSIENT,
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                return CapabilityResult(
                    capability=step_capability,
                    success=True,
                    data=facts,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability == "infrastructure.health.read_all":
                all_facts = await HealthModel.get_all_servers_health()
                return CapabilityResult(
                    capability=step_capability,
                    success=True,
                    data=all_facts,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability == "infrastructure.audit.execute":
                audit_data = await AuditWorker.run(server_id)
                success = audit_data.get("success", True)
                return CapabilityResult(
                    capability=step_capability,
                    success=success,
                    data=audit_data,
                    error=audit_data.get("error") if not success else None,
                    failure_type=FailureType.SECURITY if not success else None,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability == "infrastructure.disk.check":
                disk_data = await DiskMonitor.check_disk(server_id)
                success = disk_data.get("status") != "ERROR"
                return CapabilityResult(
                    capability=step_capability,
                    success=success,
                    data=disk_data,
                    error=disk_data.get("error") if not success else None,
                    failure_type=FailureType.TRANSIENT if not success else None,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability == "infrastructure.circuit.status":
                circuit_data = self.circuit_breaker.get_all_statuses()
                return CapabilityResult(
                    capability=step_capability,
                    success=True,
                    data={"circuits": circuit_data},
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability == "system.snapshot.get":
                snapshot_data = await SystemSnapshotService.get_snapshot()
                return CapabilityResult(
                    capability=step_capability,
                    success=True,
                    data=snapshot_data,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability == "code.task.generate_and_review":
                prompt = params.get("prompt", params.get("raw_query", ""))
                res = await CodeWorker.run_task(prompt)
                return CapabilityResult(
                    capability=step_capability,
                    success=res.get("test_result", {}).get("passed", True),
                    data=res,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability == "research.web.investigate":
                query = params.get("query", params.get("raw_query", ""))
                res = await WebSearchWorker.investigate(query)
                return CapabilityResult(
                    capability=step_capability,
                    success=True,
                    data=res,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            elif step_capability.startswith("ssh."):
                cmd_key = params.get("command_key", "health")
                success, ssh_facts, fail_type, err_msg = await SSHExecutor.execute_forced_command(
                    server_id=server_id,
                    command_key=cmd_key
                )
                return CapabilityResult(
                    capability=step_capability,
                    success=success,
                    data=ssh_facts,
                    error=err_msg,
                    failure_type=fail_type,
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            # Generic capability execution
            return CapabilityResult(
                capability=step_capability,
                success=True,
                data={"status": "executed", "params": params},
                execution_time_ms=(time.time() - start_time) * 1000
            )

        except Exception as e:
            return CapabilityResult(
                capability=step_capability,
                success=False,
                data={},
                error=str(e),
                failure_type=FailureType.TRANSIENT,
                execution_time_ms=(time.time() - start_time) * 1000
            )

    async def execute_plan(self, plan: ExecutionPlan) -> List[CapabilityResult]:
        results: List[CapabilityResult] = []
        for step in plan.steps:
            res = await self.execute_step(step.capability, step.params, step.risk)
            results.append(res)
            # Stop sequence on policy violation
            if not res.success and res.failure_type == FailureType.POLICY_VIOLATION:
                break
        return results
