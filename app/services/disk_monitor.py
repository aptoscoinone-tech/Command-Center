"""Disk Monitor Service: Monitors storage consumption across the server fleet."""

from typing import Dict, Any
from app.executors.ssh import SSHExecutor
from app.services.circuit_breaker import CircuitBreaker


class DiskMonitor:
    WARNING_THRESHOLD_PERCENT = 80
    CRITICAL_THRESHOLD_PERCENT = 90

    @classmethod
    async def check_disk(cls, server_id: str) -> Dict[str, Any]:
        circuit = CircuitBreaker.get_instance()
        if not circuit.can_execute(server_id):
            return {
                "server_id": server_id,
                "status": "ERROR",
                "error": f"Circuit breaker is OPEN for {server_id}"
            }

        success, facts, failure_type, error_msg = await SSHExecutor.execute_forced_command(
            server_id=server_id,
            command_key="disk"
        )
        if not success:
            if failure_type:
                circuit.record_failure(server_id, failure_type, error_msg or "")
            return {
                "server_id": server_id,
                "status": "ERROR",
                "error": error_msg or "Failed to query disk metrics"
            }

        circuit.record_success(server_id)
        used_pct = facts.get("disk_used_percent", 0)
        free_gb = facts.get("disk_free_gb", 0.0)
        mount = facts.get("disk_mount", "/dev/sda1")

        if used_pct >= cls.CRITICAL_THRESHOLD_PERCENT:
            health_status = "CRITICAL"
        elif used_pct >= cls.WARNING_THRESHOLD_PERCENT:
            health_status = "WARNING"
        else:
            health_status = "HEALTHY"

        return {
            "server_id": server_id,
            "mount": mount,
            "used_percent": used_pct,
            "free_gb": free_gb,
            "status": health_status
        }

    @classmethod
    async def check_all_disks(cls) -> Dict[str, Dict[str, Any]]:
        results = {}
        for s in ["apricot", "mimic"]:
            results[s] = await cls.check_disk(s)
        return results
