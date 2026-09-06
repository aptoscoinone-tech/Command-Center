"""Health Model Service: Aggregates remote server status and health indicators."""

from typing import Dict, Any
from app.executors.ssh import SSHExecutor
from app.services.circuit_breaker import CircuitBreaker


class HealthModel:
    @classmethod
    async def get_server_health(cls, server_id: str) -> Dict[str, Any]:
        """Collects genuine machine facts for a single server and computes health status."""
        circuit = CircuitBreaker.get_instance()
        if not circuit.can_execute(server_id):
            return {
                "server_id": server_id,
                "status": "RED",
                "error": f"Circuit breaker is OPEN for {server_id}",
                "circuit_state": circuit.get_state(server_id).value
            }

        success, facts, failure_type, error_msg = await SSHExecutor.execute_forced_command(
            server_id=server_id,
            command_key="health"
        )

        if not success:
            if failure_type:
                circuit.record_failure(server_id, failure_type, error_msg or "")
            return {
                "server_id": server_id,
                "status": "RED",
                "error": error_msg or "Failed to collect health metrics",
                "circuit_state": circuit.get_state(server_id).value
            }

        circuit.record_success(server_id)

        # Health state calculation
        disk_used = facts.get("disk_used_percent", 50)
        cpu_load = facts.get("cpu_load_1m", 0.5)
        ram_free = facts.get("ram_free_mb", 1024)

        if disk_used > 90 or cpu_load > 4.0 or ram_free < 100:
            status = "RED"
        elif disk_used > 75 or cpu_load > 2.0 or ram_free < 300:
            status = "YELLOW"
        else:
            status = "GREEN"

        facts["status"] = status
        facts["circuit_state"] = circuit.get_state(server_id).value
        return facts

    @classmethod
    async def get_all_servers_health(cls) -> Dict[str, Dict[str, Any]]:
        results = {}
        for s in ["apricot", "mimic"]:
            results[s] = await cls.get_server_health(s)
        return results
