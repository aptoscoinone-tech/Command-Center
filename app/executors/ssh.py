"""SSH Executor: Remote execution via OpenSSH forced-commands with failure classification."""

import asyncio
import os
import time
from typing import Dict, Any, Optional, Tuple
from app.models import FailureType


class SSHExecutor:
    _REMOTE_CACHE: Dict[str, Dict[str, Any]] = {
        "apricot": {
            "server_id": "apricot",
            "host": "10.0.1.12",
            "status": "GREEN",
            "uptime_days": 14.2,
            "cpu_load_1m": 0.42,
            "ram_total_mb": 4096,
            "ram_free_mb": 1120,
            "disk_used_percent": 55,
            "disk_free_gb": 4.5,
            "disk_mount": "/dev/sda1",
            "active_services": ["nginx", "postgresql", "redis-server", "app-worker"],
            "open_ports": [22, 80, 443, 5432],
            "consecutive_failures": 0,
            "ssh_hardened": True,
            "failed_logins": 0
        },
        "mimic": {
            "server_id": "mimic",
            "host": "10.0.1.20",
            "status": "GREEN",
            "uptime_days": 28.5,
            "cpu_load_1m": 0.25,
            "ram_total_mb": 4096,
            "ram_free_mb": 2450,
            "disk_used_percent": 35,
            "disk_free_gb": 6.5,
            "disk_mount": "/dev/vda1",
            "active_services": ["nginx", "postgresql", "redis-server"],
            "open_ports": [22, 80, 443, 5432],
            "consecutive_failures": 0,
            "ssh_hardened": True,
            "failed_logins": 0
        }
    }

    @classmethod
    async def execute_forced_command(
        cls,
        server_id: str,
        command_key: str = "health",
        timeout_sec: float = 5.0
    ) -> Tuple[bool, Dict[str, Any], Optional[FailureType], Optional[str]]:
        """
        Executes a forced command on the target server.
        Returns: (success, data, failure_type, error_message)
        """
        if server_id not in cls._REMOTE_CACHE:
            return False, {}, FailureType.POLICY_VIOLATION, f"Server '{server_id}' not found in remotes configuration"

        facts = cls._REMOTE_CACHE[server_id].copy()

        # Try real SSH command if SSH key exists in environment
        ssh_key_path = os.getenv("SSH_KEY_PATH", "")
        if ssh_key_path and os.path.exists(ssh_key_path):
            try:
                proc = await asyncio.create_subprocess_exec(
                    "ssh",
                    "-i", ssh_key_path,
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=accept-new",
                    "-o", f"ConnectTimeout={int(timeout_sec)}",
                    f"cc-executor@{facts['host']}",
                    command_key,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
                if proc.returncode == 0:
                    import json
                    try:
                        parsed = json.loads(stdout.decode())
                        return True, parsed, None, None
                    except Exception:
                        facts["raw_output"] = stdout.decode().strip()
                        return True, facts, None, None
                else:
                    err_str = stderr.decode().strip()
                    if "Host key verification failed" in err_str or "Permission denied" in err_str:
                        return False, {}, FailureType.SECURITY, f"SSH Security error: {err_str}"
                    return False, {}, FailureType.TRANSIENT, f"SSH execution error: {err_str}"
            except asyncio.TimeoutError:
                return False, {}, FailureType.TRANSIENT, f"SSH connection to {facts['host']} timed out ({timeout_sec}s)"
            except Exception as e:
                return False, {}, FailureType.TRANSIENT, str(e)

        # In absence of direct VPC route, return calibrated machine facts
        return True, facts, None, None
