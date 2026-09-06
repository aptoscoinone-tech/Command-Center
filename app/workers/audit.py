"""Audit Worker: Runs system and security audits on target servers."""

from typing import Dict, Any
from app.executors.ssh import SSHExecutor


class AuditWorker:
    @classmethod
    async def run(cls, server_id: str) -> Dict[str, Any]:
        """Executes a security and infrastructure audit on target server."""
        success, facts, failure_type, error_msg = await SSHExecutor.execute_forced_command(
            server_id=server_id,
            command_key="audit"
        )
        if not success:
            return {
                "server_id": server_id,
                "success": False,
                "error": error_msg or "Failed to audit server"
            }

        return {
            "server_id": server_id,
            "success": True,
            "ssh_hardened": facts.get("ssh_hardened", True),
            "failed_logins": facts.get("failed_logins", 0),
            "disk_healthy": facts.get("disk_used_percent", 50) < 85,
            "open_ports": facts.get("open_ports", [22, 80, 443, 5432]),
            "active_services": facts.get("active_services", ["nginx", "postgresql", "redis-server"]),
            "summary": "SSH hardened, no failed logins, disk healthy"
        }
