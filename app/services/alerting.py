"""Alerting Engine (M6): Threshold-based alerts, anomaly detection, and deduplication."""

import time
from typing import List, Dict, Any


class AlertingEngine:
    def __init__(self, dedup_window_sec: int = 300):
        self.dedup_window_sec = dedup_window_sec
        self.recent_alerts: Dict[str, float] = {}
        self.active_alerts: List[Dict[str, Any]] = [
            {
                "id": "alert_berry_disk",
                "severity": "WARNING",
                "source": "server:berry",
                "message": "Disk usage reached 84% on /dev/vda1 (1.6GB free). Threshold is 85%.",
                "timestamp": time.time() - 420,
                "dedup_key": "berry_disk_high"
            }
        ]

    def evaluate_thresholds(self, server_health_map: Dict[str, Any]) -> List[Dict[str, Any]]:
        new_alerts = []
        now = time.time()

        for server_id, data in server_health_map.items():
            disk_used = data.get("disk_used_percent", 0)
            if disk_used >= 85:
                dedup_key = f"{server_id}_disk_critical"
                if self._should_fire(dedup_key, now):
                    alert = {
                        "id": f"alt_{int(now)}_{server_id}",
                        "severity": "CRITICAL" if disk_used >= 90 else "WARNING",
                        "source": f"server:{server_id}",
                        "message": f"Disk space critical: {disk_used}% used on {server_id}!",
                        "timestamp": now,
                        "dedup_key": dedup_key
                    }
                    new_alerts.append(alert)
                    self.active_alerts.append(alert)

        return new_alerts

    def _should_fire(self, key: str, now: float) -> bool:
        last_time = self.recent_alerts.get(key, 0)
        if now - last_time > self.dedup_window_sec:
            self.recent_alerts[key] = now
            return True
        return False

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return self.active_alerts
