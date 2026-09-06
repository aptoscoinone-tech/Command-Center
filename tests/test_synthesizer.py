"""Unit tests for Synthesizer (ADR-009)."""

from app.services.synthesizer import Synthesizer
from app.models import CapabilityResult


def test_synthesizer_health_output():
    result = CapabilityResult(
        capability="infrastructure.health.read",
        success=True,
        data={
            "server_id": "apricot",
            "status": "GREEN",
            "disk_used_percent": 55,
            "ram_free_mb": 1120,
            "active_services": ["nginx", "postgresql", "redis-server", "app-worker"]
        },
        execution_time_ms=12.5
    )

    text = Synthesizer.synthesize_deterministic("Как дела у apricot?", [result])
    assert "apricot" in text
    assert "55%" in text
    assert "1120 MB" in text
    assert "GREEN" in text or "🟢" in text


def test_synthesizer_error_output():
    result = CapabilityResult(
        capability="infrastructure.health.read",
        success=False,
        data={},
        error="Connection refused"
    )

    text = Synthesizer.synthesize_deterministic("Статус", [result])
    assert "Операция не выполнена" in text
    assert "Connection refused" in text


if __name__ == "__main__":
    test_synthesizer_health_output()
    test_synthesizer_error_output()
    print("All Synthesizer tests passed successfully!")
