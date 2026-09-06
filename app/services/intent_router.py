"""Intent Router: Rule-based pre-filter with OpenRouter LLM fallback for user query classification."""

import json
import os
import re
from typing import Any, Dict, List, Optional
from app.models import IntentResult, RiskLevel


class IntentRouter:
    KNOWN_SERVERS: List[str] = ["apricot", "mimic"]

    @classmethod
    def load_known_servers(cls) -> List[str]:
        """Dynamically load target servers from config/remotes.yaml."""
        remotes_path = os.path.join(os.getcwd(), "config", "remotes.yaml")
        if not os.path.exists(remotes_path):
            return cls.KNOWN_SERVERS

        try:
            try:
                import yaml
                with open(remotes_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "servers" in data:
                        servers = list(data["servers"].keys())
                        if servers:
                            cls.KNOWN_SERVERS = servers
                            return servers
            except ImportError:
                # Fallback line-based parser if PyYAML is not present
                servers = []
                in_servers_block = False
                with open(remotes_path, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith("servers:"):
                            in_servers_block = True
                            continue
                        if in_servers_block:
                            if line.startswith("  ") and not line.startswith("    ") and ":" in stripped:
                                s_name = stripped.split(":")[0].strip()
                                if s_name and not s_name.startswith("#"):
                                    servers.append(s_name)
                            elif line and not line.startswith(" ") and not line.startswith("#"):
                                in_servers_block = False
                if servers:
                    cls.KNOWN_SERVERS = servers
                    return servers
        except Exception:
            pass

        return cls.KNOWN_SERVERS

    @classmethod
    def get_intent_classifier_model(cls) -> Dict[str, Any]:
        """Reads LLM configuration for intent_classifier from config/models.yaml."""
        models_path = os.path.join(os.getcwd(), "config", "models.yaml")
        config = {
            "primary": "google/gemma-4-12b-it",
            "fallback": "google/gemini-3.8-flash",
            "timeout_sec": 10,
            "max_tokens": 500
        }
        if not os.path.exists(models_path):
            return config

        try:
            try:
                import yaml
                with open(models_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "models" in data and "intent_classifier" in data["models"]:
                        config.update(data["models"]["intent_classifier"])
                        return config
            except ImportError:
                pass
        except Exception:
            pass

        return config

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
            r"(проведи аудит|сделай аудит|полный аудит|аудит|audit)\s*([a-zA-Z0-9_-]+)?",
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
        cls.load_known_servers()
        text_lower = text.lower()
        for s in cls.KNOWN_SERVERS:
            if s.lower() in text_lower:
                return s

        # Regex search for word after keyword
        match = re.search(r"(?:сервер[а-я]?|у|для|на)\s+([a-zA-Z0-9_-]+)", text_lower)
        if match:
            candidate = match.group(1).lower()
            for s in cls.KNOWN_SERVERS:
                if s.lower() == candidate:
                    return s
        return None

    @classmethod
    async def _classify_via_openrouter(cls, user_text: str) -> Optional[IntentResult]:
        """LLM Fallback using OpenRouter API with models from config/models.yaml."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return None

        model_cfg = cls.get_intent_classifier_model()
        primary_model = model_cfg.get("primary", "google/gemma-4-12b-it")
        timeout_sec = model_cfg.get("timeout_sec", 10)

        prompt = (
            f"You are the intent router for server fleet management ({', '.join(cls.KNOWN_SERVERS)}).\n"
            f"User query: '{user_text}'\n\n"
            f"Classify into JSON format:\n"
            f'{{"intent": "infrastructure.health.read|infrastructure.audit.execute|infrastructure.disk.check|infrastructure.circuit.status|system.snapshot.get|code.task.generate_and_review|research.web.investigate|general.query", '
            f'"risk": "GREEN|YELLOW|RED", '
            f'"server": "apricot|mimic|null", '
            f'"required_capabilities": ["..."]}}'
        )

        try:
            import urllib.request
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://command-center.local",
                "X-Title": "Command Center v2.0"
            }
            payload = {
                "model": primary_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.1
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                result_data = json.loads(resp.read().decode("utf-8"))
                content = result_data["choices"][0]["message"]["content"]
                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    risk_str = parsed.get("risk", "GREEN")
                    risk_level = RiskLevel.GREEN
                    if risk_str == "YELLOW":
                        risk_level = RiskLevel.YELLOW
                    elif risk_str == "RED":
                        risk_level = RiskLevel.RED

                    target_s = parsed.get("server")
                    if target_s not in cls.KNOWN_SERVERS:
                        target_s = cls.KNOWN_SERVERS[0]

                    return IntentResult(
                        intent=parsed.get("intent", "general.query"),
                        risk=risk_level,
                        required_capabilities=parsed.get("required_capabilities", []),
                        target_server=target_s,
                        params={"raw_query": user_text, "server_id": target_s},
                        confidence=0.88,
                        classification_method="openrouter_llm_fallback"
                    )
        except Exception:
            pass

        return None

    @classmethod
    async def classify(cls, user_text: str, llm_client: Optional[Any] = None) -> IntentResult:
        """Classify user text using rule-based pre-filter or OpenRouter LLM fallback."""
        cls.load_known_servers()
        cleaned_text = user_text.strip().lower()
        target_server = cls._extract_server(user_text)

        # 1. Fast Rule-Based Matcher
        for pattern, intent, risk, caps in cls.RULES:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                server = target_server
                if not server and match.lastindex and match.lastindex >= 2:
                    potential = match.group(2)
                    if potential and potential.lower() in [s.lower() for s in cls.KNOWN_SERVERS]:
                        server = potential.lower()

                resolved_server = server if server in cls.KNOWN_SERVERS else cls.KNOWN_SERVERS[0]

                return IntentResult(
                    intent=intent,
                    risk=risk,
                    required_capabilities=caps,
                    target_server=resolved_server,
                    params={"raw_query": user_text, "server_id": resolved_server},
                    confidence=0.98,
                    classification_method="rule_based"
                )

        # 2. OpenRouter LLM Fallback
        openrouter_res = await cls._classify_via_openrouter(user_text)
        if openrouter_res:
            return openrouter_res

        # 3. Default fallback
        fallback_server = target_server or cls.KNOWN_SERVERS[0]
        return IntentResult(
            intent="general.query",
            risk=RiskLevel.GREEN,
            required_capabilities=[],
            target_server=fallback_server,
            params={"raw_query": user_text, "server_id": fallback_server},
            confidence=0.5,
            classification_method="rule_based"
        )
