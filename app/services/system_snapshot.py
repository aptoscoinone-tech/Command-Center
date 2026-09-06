"""System Snapshot Service: Aggregates fleet health, circuits, disks, and freshness."""

import time
from typing import Dict, Any
from app.services.health_model import HealthModel
from app.services.circuit_breaker import CircuitBreaker
from app.services.disk_monitor import DiskMonitor
from app.services.stale_detector import StaleDetector


class SystemSnapshotService:
    @classmethod
    async def get_snapshot(cls) -> Dict[str, Any]:
        """Collects an integrated snapshot across all monitored services."""
        health = await HealthModel.get_all_servers_health()
        circuits = CircuitBreaker.get_instance().get_all_statuses()
        disks = await DiskMonitor.check_all_disks()
        stale = await StaleDetector.check_all()

        all_green = all(h.get("status") == "GREEN" for h in health.values())
        all_circuits_closed = all(c.get("state") == "CLOSED" for c in circuits.values())

        return {
            "timestamp": time.time(),
            "overall_healthy": all_green and all_circuits_closed,
            "servers": health,
            "circuits": circuits,
            "disks": disks,
            "stale": stale
        }
