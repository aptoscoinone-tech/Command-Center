"""Integration tests for aiogram 3 bot handlers and service integration."""

import asyncio
from app.bot import (
    router,
    cmd_stop_all,
    cmd_resume,
    cmd_read_only,
    cmd_health,
    cmd_circuit,
    cmd_disks,
    cmd_snapshot,
    handle_conversational_message,
    Message
)
from app.models import KillSwitchState
from app.services.policy_engine import PolicyEngine


class MockTelegramMessage:
    def __init__(self, text: str):
        self.text = text
        self.responses = []

    async def answer(self, text: str, parse_mode: str = None):
        self.responses.append(text)
        return self


def test_emergency_slash_commands():
    loop = asyncio.new_event_loop()
    engine = PolicyEngine.get_instance()

    # /stop_all
    msg1 = MockTelegramMessage("/stop_all")
    loop.run_until_complete(cmd_stop_all(msg1))
    assert engine.kill_switch_state == KillSwitchState.EMERGENCY_STOP
    assert "EMERGENCY STOP" in msg1.responses[0]

    # /resume
    msg2 = MockTelegramMessage("/resume")
    loop.run_until_complete(cmd_resume(msg2))
    assert engine.kill_switch_state == KillSwitchState.NORMAL
    assert "NORMAL" in msg2.responses[0]

    # /read_only
    msg3 = MockTelegramMessage("/read_only")
    loop.run_until_complete(cmd_read_only(msg3))
    assert engine.kill_switch_state == KillSwitchState.READ_ONLY
    assert "READ_ONLY" in msg3.responses[0]

    # Restore to normal
    engine.set_kill_switch(KillSwitchState.NORMAL)


def test_conversational_health_query():
    loop = asyncio.new_event_loop()
    PolicyEngine.get_instance().set_kill_switch(KillSwitchState.NORMAL)

    msg = MockTelegramMessage("Как дела у apricot?")
    answer = loop.run_until_complete(handle_conversational_message(msg))
    assert "apricot" in answer
    assert "GREEN" in answer or "🟢" in answer
    assert "55%" in answer
    assert len(msg.responses) == 1


def test_conversational_audit_query():
    loop = asyncio.new_event_loop()
    PolicyEngine.get_instance().set_kill_switch(KillSwitchState.NORMAL)

    msg = MockTelegramMessage("Проведи аудит apricot")
    answer = loop.run_until_complete(handle_conversational_message(msg))
    assert "Audit complete" in answer or "apricot" in answer
    assert "SSH" in answer
    assert len(msg.responses) == 1


def test_diagnostic_commands():
    loop = asyncio.new_event_loop()
    msg_h = MockTelegramMessage("/health")
    loop.run_until_complete(cmd_health(msg_h))
    assert "apricot" in msg_h.responses[0]
    assert "mimic" in msg_h.responses[0]

    msg_c = MockTelegramMessage("/circuit")
    loop.run_until_complete(cmd_circuit(msg_c))
    assert "Circuit" in msg_c.responses[0]

    msg_d = MockTelegramMessage("/disks")
    loop.run_until_complete(cmd_disks(msg_d))
    assert "Дисковое" in msg_d.responses[0]

    msg_s = MockTelegramMessage("/snapshot")
    loop.run_until_complete(cmd_snapshot(msg_s))
    assert "снапшот" in msg_s.responses[0].lower()


if __name__ == "__main__":
    test_emergency_slash_commands()
    test_conversational_health_query()
    test_conversational_audit_query()
    test_diagnostic_commands()
    print("All Bot & Service integration tests passed successfully!")
