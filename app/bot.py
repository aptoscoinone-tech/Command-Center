"""Telegram Bot Handlers (Aiogram 3): Conversational control plane + emergency slash commands."""

from typing import Any
from app.services.intent_router import IntentRouter
from app.services.planner import Planner
from app.services.orchestrator import Orchestrator
from app.services.synthesizer import Synthesizer
from app.services.policy_engine import PolicyEngine
from app.services.dashboard import DashboardGenerator
from app.models import KillSwitchState

# Conceptual mock for Aiogram 3 router and decorators
class MockTelegramRouter:
    def __init__(self, policy_engine: PolicyEngine, orchestrator: Orchestrator):
        self.policy_engine = policy_engine
        self.orchestrator = orchestrator

    async def handle_conversational_message(self, text: str, user_id: str = "123456") -> str:
        """
        Conversational Handler (M2.5):
        1. Classify intent via IntentRouter
        2. Plan execution steps via Planner
        3. Execute via Orchestrator (with Policy checks)
        4. Synthesize human-readable response via Synthesizer
        """
        intent = await IntentRouter.classify(text)
        plan = Planner.plan(intent)
        facts = await self.orchestrator.execute_plan(plan)
        answer = Synthesizer.synthesize_deterministic(text, facts)
        return answer

    async def handle_slash_command(self, command: str, args: str = "") -> str:
        cmd = command.strip().lower()

        if cmd == "/stop_all":
            self.policy_engine.set_kill_switch(KillSwitchState.EMERGENCY_STOP)
            return "🛑 EMERGENCY STOP активирован! Все capabilities заблокированы. Выполнение любых команд остановлено."

        elif cmd == "/resume":
            self.policy_engine.set_kill_switch(KillSwitchState.NORMAL)
            return "✅ Режим NORMAL восстановлен. Все разрешённые capabilities активны."

        elif cmd == "/read_only":
            self.policy_engine.set_kill_switch(KillSwitchState.READ_ONLY)
            return "🔒 Режим READ_ONLY включён. Изменяющие (YELLOW/RED) capabilities заблокированы."

        elif cmd == "/snapshot":
            return await self.handle_conversational_message("снапшот системы")

        elif cmd == "/health":
            return await self.handle_conversational_message("здоровье")

        elif cmd == "/circuit":
            return await self.handle_conversational_message("circuit breaker")

        elif cmd == "/disk":
            return await self.handle_conversational_message("диски")

        elif cmd == "/dashboard":
            metrics = {
                "host_metrics": {"cpu_percent": 18, "ram_used_mb": 1840, "ram_total_mb": 4096, "disk_used_percent": 84},
                "performance": {"avg_latency_ms": 4.2, "p95_latency_ms": 8.1},
                "error_classification": {"TRANSIENT": 0, "SECURITY": 0, "LOCAL_RESOURCE": 0, "POLICY_VIOLATION": 0}
            }
            return DashboardGenerator.generate_ascii_dashboard(
                metrics,
                {},
                self.policy_engine.kill_switch_state.value
            )

        return f"Неизвестная команда: {command}. Введите свободный текст или /help."
