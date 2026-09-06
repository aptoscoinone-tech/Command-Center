"""Data models and enums for Command Center."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class KillSwitchState(str, Enum):
    NORMAL = "NORMAL"
    READ_ONLY = "READ_ONLY"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class RiskLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class FailureType(str, Enum):
    TRANSIENT = "TRANSIENT"            # SSH timeout, temporary network drop -> counted in Circuit Breaker
    SECURITY = "SECURITY"              # Host key mismatch, auth failure -> alert immediately, do not count
    LOCAL_RESOURCE = "LOCAL_RESOURCE"  # Disk full on CC host, OOM -> alert, do not count
    POLICY_VIOLATION = "POLICY_VIOLATION" # Kill switch blocks action -> do not count


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Healthy, requests pass
    OPEN = "OPEN"          # Failing, fast fail
    HALF_OPEN = "HALF_OPEN"# Probing with lightweight probe


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class IntentResult:
    intent: str
    risk: RiskLevel
    required_capabilities: List[str]
    target_server: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    classification_method: str = "rule_based"  # "rule_based" or "llm_fallback"


@dataclass
class ExecutionPlanStep:
    step_id: str
    capability: str
    params: Dict[str, Any]
    risk: RiskLevel
    depends_on: List[str] = field(default_factory=list)
    requires_approval: bool = False


@dataclass
class ExecutionPlan:
    plan_id: str
    intent: str
    steps: List[ExecutionPlanStep]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MachineFacts:
    server_id: str
    timestamp: str
    facts: Dict[str, Any]
    raw_output: Optional[str] = None
    source: str = "ssh_forced_command"


@dataclass
class CapabilityResult:
    capability: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    failure_type: Optional[FailureType] = None
    execution_time_ms: float = 0.0
