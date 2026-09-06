"""Human Approval Flow (M5): Manages confirmation gates for risky (YELLOW/RED) actions."""

import time
import uuid
from typing import Dict, Any, Optional
from app.models import RiskLevel


class HumanApprovalFlow:
    def __init__(self, default_timeout_sec: int = 60):
        self.default_timeout_sec = default_timeout_sec
        # pending_requests: {request_id: dict}
        self.pending_requests: Dict[str, Dict[str, Any]] = {}
        self.history: Dict[str, Dict[str, Any]] = {}

    def create_approval_request(
        self,
        capability: str,
        risk: RiskLevel,
        params: Dict[str, Any],
        initiated_by: str = "telegram_user"
    ) -> Dict[str, Any]:
        """Creates an approval challenge requiring interactive confirmation."""
        req_id = f"appr_{uuid.uuid4().hex[:8]}"
        now = time.time()

        req = {
            "request_id": req_id,
            "capability": capability,
            "risk": risk.value if hasattr(risk, 'value') else risk,
            "params": params,
            "initiated_by": initiated_by,
            "created_at": now,
            "expires_at": now + self.default_timeout_sec,
            "status": "PENDING"  # PENDING, APPROVED, DENIED, EXPIRED
        }

        self.pending_requests[req_id] = req
        return req

    def resolve_request(self, request_id: str, approved: bool, user_id: str) -> Optional[Dict[str, Any]]:
        req = self.pending_requests.get(request_id)
        if not req:
            return None

        # Check expiration
        if time.time() > req["expires_at"]:
            req["status"] = "EXPIRED"
            self.history[request_id] = self.pending_requests.pop(request_id)
            return req

        req["status"] = "APPROVED" if approved else "DENIED"
        req["resolved_by"] = user_id
        req["resolved_at"] = time.time()

        self.history[request_id] = self.pending_requests.pop(request_id)
        return req
