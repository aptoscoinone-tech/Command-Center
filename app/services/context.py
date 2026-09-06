"""Context Manager (M5): Retains dialogue history, user preferences, and target server focus."""

from typing import List, Dict, Any, Optional
from datetime import datetime


class ContextManager:
    def __init__(self, max_history: int = 15):
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
        self.last_target_server: str = "apricot"
        self.user_preferences: Dict[str, Any] = {
            "preferred_language": "ru",
            "verbose_mode": False
        }

    def add_interaction(self, user_msg: str, bot_msg: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if metadata and "target_server" in metadata:
            self.last_target_server = metadata["target_server"]

        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_msg,
            "bot": bot_msg,
            "metadata": metadata or {}
        })

        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_recent_context(self, n: int = 5) -> List[Dict[str, Any]]:
        return self.history[-n:]

    def get_current_focus_server(self) -> str:
        return self.last_target_server
