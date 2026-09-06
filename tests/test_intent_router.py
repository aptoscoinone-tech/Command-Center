"""Unit tests for Intent Router (M2.5)."""

import asyncio
from app.services.intent_router import IntentRouter
from app.models import RiskLevel


def test_intent_router_health_query():
    loop = asyncio.new_event_loop()
    res = loop.run_until_complete(IntentRouter.classify("Как дела у apricot?"))
    assert res.intent in ("infrastructure.health.read", "infrastructure.health.check")
    assert res.target_server == "apricot"
    assert res.risk == RiskLevel.GREEN
    assert "infrastructure.health.read" in res.required_capabilities


def test_intent_router_audit_query():
    loop = asyncio.new_event_loop()
    res = loop.run_until_complete(IntentRouter.classify("Проведи аудит apricot"))
    assert res.intent == "infrastructure.audit.execute"
    assert res.target_server == "apricot"
    assert res.risk == RiskLevel.YELLOW


def test_intent_router_disk_query():
    loop = asyncio.new_event_loop()
    res = loop.run_until_complete(IntentRouter.classify("Что с дисками?"))
    assert res.intent == "infrastructure.disk.check"
    assert res.risk == RiskLevel.GREEN


def test_intent_router_emergency_stop():
    loop = asyncio.new_event_loop()
    res = loop.run_until_complete(IntentRouter.classify("/stop_all"))
    assert res.intent == "emergency.stop"
    assert res.risk == RiskLevel.RED


if __name__ == "__main__":
    test_intent_router_health_query()
    test_intent_router_audit_query()
    test_intent_router_disk_query()
    test_intent_router_emergency_stop()
    print("All Intent Router tests passed successfully!")
