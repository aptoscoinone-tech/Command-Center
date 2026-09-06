"""Memory System (M5): Persistent key-value and semantic facts memory store."""

from typing import Dict, Any, List, Optional
import time


class MemorySystem:
    def __init__(self):
        # In-memory fact storage (synced with SQLite/Postgres in production)
        self.facts: Dict[str, Any] = {
            "server:apricot:role": "Primary production backend running aiogram + postgresql",
            "server:apricot:ip": "10.0.1.12",
            "server:peach:role": "Replica PostgreSQL with streaming replication",
            "server:berry:role": "Edge proxy with Wireguard & Caddy",
            "backup:schedule": "Daily restic incremental at 03:00 UTC",
            "restore_test:schedule": "Monthly automated restore test on 1st Sunday",
            "kill_switch:policy": "Only admin can toggle between NORMAL and READ_ONLY"
        }

    def store_fact(self, key: str, value: Any) -> None:
        self.facts[key] = value

    def search_facts(self, query: str) -> List[Dict[str, Any]]:
        """Keyword / semantic matching for user context retrieval."""
        results = []
        tokens = query.lower().split()
        for k, v in self.facts.items():
            content = f"{k} {v}".lower()
            if any(t in content for t in tokens):
                results.append({"key": k, "fact": v})
        return results
