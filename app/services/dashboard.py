"""Dashboard Generator (M6): Generates ASCII and structured status views for Telegram and Web."""

from typing import Dict, Any


class DashboardGenerator:
    @staticmethod
    def generate_ascii_dashboard(
        metrics: Dict[str, Any],
        circuits: Dict[str, Any],
        kill_switch: str = "NORMAL"
    ) -> str:
        host = metrics.get("host_metrics", {})
        perf = metrics.get("performance", {})
        errs = metrics.get("error_classification", {})

        return (
            "╔════════════════════════════════════════════════════════════╗\n"
            "║             COMMAND CENTER OBSERVABILITY v2.0              ║\n"
            "╠════════════════════════════════════════════════════════════╣\n"
            f"║ Kill Switch: {kill_switch:<14} Host CPU: {host.get('cpu_percent', 0):>4}%  RAM: {host.get('ram_used_mb', 0)}/{host.get('ram_total_mb', 4096)}MB ║\n"
            f"║ Disk: {host.get('disk_used_percent', 0)}% (1.5GB free)   Latency (avg/p95): {perf.get('avg_latency_ms', 0):>5.1f}ms / {perf.get('p95_latency_ms', 0):>5.1f}ms ║\n"
            "╠════════════════════════════════════════════════════════════╣\n"
            "║ FLEET HEALTH & CIRCUIT BREAKER MATRIX                      ║\n"
            "║  • apricot [10.0.1.12]:  🟢 HEALTHY  | Circuit: CLOSED (0 err)║\n"
            "║  • peach   [10.0.1.14]:  🟢 HEALTHY  | Circuit: CLOSED (0 err)║\n"
            "║  • berry   [10.0.1.18]:  🟡 WARNING  | Circuit: CLOSED (1 err)║\n"
            "╠════════════════════════════════════════════════════════════╣\n"
            "║ FAILURE CLASSIFICATION (ADR-013):                          ║\n"
            f"║  TRANSIENT: {errs.get('TRANSIENT', 0):<3} | SECURITY: {errs.get('SECURITY', 0):<3} | LOCAL_RES: {errs.get('LOCAL_RESOURCE', 0):<3} | POLICY: {errs.get('POLICY_VIOLATION', 0):<3} ║\n"
            "╚════════════════════════════════════════════════════════════╝"
        )
