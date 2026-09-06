"""Stale Detector Service: Detects unrefreshed metrics and unresponsive services."""

import time
from typing import Dict, Any


class StaleDetector:
    STALE_THRESHOLD_SECONDS = 300.0  # 5 minutes

    # server_id -> last_seen_timestamp
    _last_seen: Dict[str, float] = {
        "apricot": time.time(),
        "mimic": time.time()
    }

    @classmethod
    def mark_seen(cls, server_id: str) -> None:
        cls._last_seen[server_id] = time.time()

    @classmethod
    async def is_stale(cls, server_id: str) -> bool:
        last = cls._last_seen.get(server_id, 0.0)
        return (time.time() - last) > cls.STALE_THRESHOLD_SECONDS

    @classmethod
    async def check_server(cls, server_id: str) -> Dict[str, Any]:
        last = cls._last_seen.get(server_id, 0.0)
        age = time.time() - last
        stale = age > cls.STALE_THRESHOLD_SECONDS
        return {
            "server_id": server_id,
            "is_stale": stale,
            "age_seconds": round(age, 1),
            "status": "STALE" if stale else "FRESH"
        }

    @classmethod
    async def check_all(cls) -> Dict[str, Dict[str, Any]]:
        return {s: await cls.check_server(s) for s in ["apricot", "mimic"]}
