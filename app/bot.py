"""Telegram Bot Handlers (Aiogram 3): Conversational control plane + emergency slash commands."""

import asyncio
from typing import Any, Dict, Optional

# Aiogram 3 Imports with graceful fallback for headless environments
try:
    from aiogram import Router, F
    from aiogram.filters import Command
    from aiogram.types import Message
except ImportError:
    # Minimal type and decorator stubs if aiogram is not installed in the execution environment
    class FilterStub:
        def __invert__(self):
            return self
        def __and__(self, other):
            return self
        def startswith(self, prefix: str):
            return self

    class FStub:
        text = FilterStub()

    F = FStub()

    class Command:
        def __init__(self, command_name: str):
            self.command_name = command_name

    class MessageStub:
        def __init__(self, text: str = "", chat_id: int = 123456):
            self.text = text
            self.chat = type("Chat", (), {"id": chat_id})
            self.responses = []

        async def answer(self, text: str, parse_mode: Optional[str] = None):
            self.responses.append(text)
            return self

    Message = MessageStub

    class Router:
        def __init__(self, name: str = "default"):
            self.name = name
            self._handlers = []

        def message(self, *filters, **kwargs):
            def decorator(func):
                self._handlers.append((filters, func))
                return func
            return decorator

from app.models import KillSwitchState
from app.services.intent_router import IntentRouter
from app.services.planner import Planner
from app.services.orchestrator import Orchestrator
from app.services.synthesizer import Synthesizer
from app.services.policy_engine import PolicyEngine
from app.services.health_model import HealthModel
from app.services.circuit_breaker import CircuitBreaker
from app.services.disk_monitor import DiskMonitor
from app.services.stale_detector import StaleDetector
from app.services.system_snapshot import SystemSnapshotService


# Aiogram 3 Router instance
router = Router(name="command_center_bot")


# ==========================================
# Emergency Slash Command Handlers
# ==========================================

@router.message(Command("stop_all"))
async def cmd_stop_all(message: Message) -> None:
    """Immediate Emergency Stop: locks down all capabilities."""
    policy_engine = PolicyEngine.get_instance()
    policy_engine.set_kill_switch(KillSwitchState.EMERGENCY_STOP)
    await message.answer(
        "🛑 EMERGENCY STOP активирован! Все capabilities заблокированы. Выполнение любых команд остановлено."
    )


@router.message(Command("resume"))
async def cmd_resume(message: Message) -> None:
    """Restores system to NORMAL execution mode."""
    policy_engine = PolicyEngine.get_instance()
    policy_engine.set_kill_switch(KillSwitchState.NORMAL)
    await message.answer(
        "✅ Режим NORMAL восстановлен. Все разрешённые capabilities активны."
    )


@router.message(Command("read_only"))
async def cmd_read_only(message: Message) -> None:
    """Restricts system to safe read-only queries."""
    policy_engine = PolicyEngine.get_instance()
    policy_engine.set_kill_switch(KillSwitchState.READ_ONLY)
    await message.answer(
        "🔒 Режим READ_ONLY включён. Изменяющие (YELLOW/RED) capabilities заблокированы."
    )


# ==========================================
# Diagnostic & Fleet Slash Handlers
# ==========================================

@router.message(Command("health"))
async def cmd_health(message: Message) -> None:
    """Queries HealthModel for real-time health across all servers."""
    health_data = await HealthModel.get_all_servers_health()
    lines = ["🖥️ <b>Состояние серверов:</b>"]
    for s_name, data in health_data.items():
        st = data.get("status", "UNKNOWN")
        icon = "🟢" if st == "GREEN" else ("🟡" if st == "YELLOW" else "🔴")
        lines.append(
            f"• {icon} <b>{s_name}</b>: {st}, Uptime {data.get('uptime_days', 0)}d, "
            f"Диск {data.get('disk_used_percent', 0)}%, CPU {data.get('cpu_load_1m', 0)}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("circuit"))
async def cmd_circuit(message: Message) -> None:
    """Queries CircuitBreaker for all managed circuits."""
    circuits = CircuitBreaker.get_instance().get_all_statuses()
    lines = ["⚡ <b>Состояние Circuit Breakers:</b>"]
    for s_name, c in circuits.items():
        icon = "🟢" if c["state"] == "CLOSED" else ("🟡" if c["state"] == "HALF_OPEN" else "🔴")
        lines.append(f"• {icon} <b>{s_name}</b>: {c['state']} ({c['failures_in_window']} ошибок в окне)")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("disks"))
@router.message(Command("disk"))
async def cmd_disks(message: Message) -> None:
    """Queries DiskMonitor for disk utilization."""
    disks = await DiskMonitor.check_all_disks()
    lines = ["💾 <b>Дисковое пространство:</b>"]
    for s_name, d in disks.items():
        icon = "🟢" if d["status"] == "HEALTHY" else ("🟡" if d["status"] == "WARNING" else "🔴")
        lines.append(f"• {icon} <b>{s_name}</b> ({d.get('mount', '/')}): {d.get('used_percent', 0)}% занято ({d.get('free_gb', 0)}GB свободно)")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("stale"))
async def cmd_stale(message: Message) -> None:
    """Queries StaleDetector for metric freshness."""
    stale_info = await StaleDetector.check_all()
    lines = ["⏱️ <b>Свежесть метрик (Stale Detector):</b>"]
    for s_name, info in stale_info.items():
        icon = "🟢" if not info["is_stale"] else "🔴"
        lines.append(f"• {icon} <b>{s_name}</b>: {info['status']} ({info['age_seconds']}s назад)")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("snapshot"))
async def cmd_snapshot(message: Message) -> None:
    """Aggregates all services via SystemSnapshotService."""
    snapshot = await SystemSnapshotService.get_snapshot()
    healthy_icon = "🟢" if snapshot.get("overall_healthy") else "🟡"
    lines = [
        f"{healthy_icon} <b>Системный снапшот:</b>",
        f"• Серверов под управлением: {len(snapshot.get('servers', {}))}",
        f"• Общий статус: {'ЗДОРОВ' if snapshot.get('overall_healthy') else 'ТРЕБУЕТ ВНИМАНИЯ'}",
        f"• Предохранители: {len(snapshot.get('circuits', {}))} активны",
        f"• Свежесть: проверено"
    ]
    await message.answer("\n".join(lines), parse_mode="HTML")


# ==========================================
# Conversational Message Handler (M2.5)
# ==========================================

@router.message(F.text & ~F.text.startswith("/"))
async def handle_conversational_message(message: Message) -> str:
    """
    Conversational Message Pipeline:
    1. Classify intent via IntentRouter (rule-based + OpenRouter LLM fallback)
    2. Plan execution steps via Planner
    3. Execute via Orchestrator (real services + Policy Engine validation)
    4. Synthesize human-readable response via Synthesizer
    """
    text = (message.text or "").strip()
    policy_engine = PolicyEngine.get_instance()
    orchestrator = Orchestrator(policy_engine)

    # 1. Intent classification
    intent = await IntentRouter.classify(text)

    # 2. Execution planning
    plan = Planner.plan(intent)

    # 3. Execution on genuine services (No hardcoded mock facts)
    facts = await orchestrator.execute_plan(plan)

    # 4. Synthesis (ADR-009: Machine facts source of truth)
    answer = Synthesizer.synthesize_deterministic(text, facts)

    # 5. Reply
    await message.answer(answer)
    return answer
