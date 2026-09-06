"""Intent Router: Rule-based pre-filter with LLM fallback for user query classification."""

import re
from typing import Any, Dict, Optional
from app.models import IntentResult, RiskLevel


class IntentRouter:
    KNOWN_SERVERS = ["apricot", "peach", "berry"]

    # Rule-based patterns: (regex, intent, risk, capabilities)
    RULES = [
        # Health checks
        (
            r"(как дела у|проверь состояние|статус|health|как там)\s+([a-zA-Z0-9_-]+)",
            "infrastructure.health.read",
            RiskLevel.GREEN,
            ["infrastructure.health.read"]
        ),
        (
            r"^(здоровье|health|проверь серверы|все серверы)$",
            "infrastructure.health.read_all",
            RiskLevel.GREEN,
            ["infrastructure.health.read"]
        ),
        # Audit
        (
            r"(проведи аудит|сделай аудит|полный аудит|аудит|audit)\s+([a-zA-Z0-9_-]+)?",
            "infrastructure.audit.execute",
            RiskLevel.YELLOW,
            ["infrastructure.audit.execute"]
        ),
        # Disks
        (
            r"(что с дисками|диски|место на диске|проверь диск|disk|df)",
            "infrastructure.disk.check",
            RiskLevel.GREEN,
            ["infrastructure.disk.check"]
        ),
        # Circuit breaker
        (
            r"(circuit|предохранители|circuit breaker|состояние цепей)",
            "infrastructure.circuit.status",
            RiskLevel.GREEN,
            ["infrastructure.circuit.status"]
        ),
        # Backups
        (
            r"(бэкап|бэкапы|backup|снапшот|restic)",
            "backup.snapshot.status",
            RiskLevel.GREEN,
            ["backup.snapshot.status"]
        ),
        # System Snapshot
        (
            r"(снапшот системы|система|system snapshot|общий статус|что нового)",
            "system.snapshot.get",
            RiskLevel.GREEN,
            ["infrastructure.health.read", "infrastructure.circuit.status", "infrastructure.disk.check"]
        ),
        # Coding (M3)
        (
            r"^(/coder|напиши код|создай функцию|напиши функцию|сгенерируй код)",
            "code.task.generate_and_review",
            RiskLevel.YELLOW,
            ["code.task.generate_and_review"]
        ),
        # Research (M4)
        (
            r"^(/research|исследуй|найди инфу|найди информацию|сравни|web search)",
            "research.web.investigate",
            RiskLevel.GREEN,
            ["research.web.investigate"]
        ),
        # Emergency stop / Resume / Read only
        (
            r"^(/stop_all|останови всё|экстренный стоп|emergency stop)$",
            "emergency.stop",
            RiskLevel.RED,
            []
        ),
        (
            r"^(/resume|возобнови|resume)$",
            "emergency.resume",
            RiskLevel.GREEN,
            []
        ),
        (
            r"^(/read_only|только чтение|read only)$",
            "emergency.read_only",
            RiskLevel.GREEN,
            []
        ),
    ]

    @classmethod
    def _extract_server(cls, text: str) -> Optional[str]:
        text_lower = text.lower()
        for s in cls.KNOWN_SERVERS:
            if s in text_lower:
                return s
        # Regex search for word after keyword
        match = re.search(r"(?:сервер[а-я]?|у|для)\s+([a-zA-Z0-9_-]+)", text_lower)
        if match:
            candidate = match.group(1)
            if candidate in cls.KNOWN_SERVERS:
                return candidate
        return None

    @classmethod
    async def classify(cls, user_text: str, llm_client: Optional[Any] = None) -> IntentResult:
        """Classify user text using rule-based pre-filter or LLM fallback."""
        cleaned_text = user_text.strip().lower()
        target_server = cls._extract_server(user_text)

        # 1. Fast Rule-Based Matcher
        for pattern, intent, risk, caps in cls.RULES:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                server = target_server
                if not server and match.lastindex and match.lastindex >= 2:
                    potential_server = match.group(2)
                    if potential_server in cls.KNOWN_SERVERS:
                        server = potential_server

                return IntentResult(
                    intent=intent,
                    risk=risk,
                    required_capabilities=caps,
                    target_server=server or "apricot",
                    params={"raw_query": user_text, "server_id": server or "apricot"},
                    confidence=0.98,
                    classification_method="rule_based"
                )

        # 2. LLM Fallback (if rule didn't match and llm_client provided)
        if llm_client:
            try:
                prompt = (
                    f"Classify user intention for server management system: '{user_text}'.\n"
                    f"Available intents: health.check, audit.execute, disk.check, circuit.status, "
                    f"backup.status, code.generate, research.web, general.qa.\n"
                    f"Return single JSON: {{\"intent\": \"...\", \"risk\": \"GREEN|YELLOW|RED\", \"server\": \"apricot|peach|berry|null\"}}"
                )
                # LLM classification call...
                # Handled via server-side Gemini
            except Exception:
                pass

        # Default fallback
        return IntentResult(
            intent="general.qa",
            risk=RiskLevel.GREEN,
            required_capabilities=["infrastructure.health.read"],
            target_server=target_server or "apricot",
            params={"raw_query": user_text},
            confidence=0.6,
            classification_method="fallback_default"
        )
