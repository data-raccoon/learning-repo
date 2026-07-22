"""Dependency-free reference harness for contracts and fail-closed gates."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable, Mapping, Optional


class ContractError(ValueError):
    """The wire message does not satisfy the structural contract."""


class GateRejected(RuntimeError):
    """A gate rejected the operation before a side effect occurred."""


class MessageType(str, Enum):
    ACTION_REQUEST = "action_request"


class ActionKind(str, Enum):
    READ_REPORT = "read_report"
    TRANSFER = "transfer"
    DEPLOY = "deploy"


class Risk(str, Enum):
    LOW = "low"
    HIGH = "high"


@dataclass(frozen=True)
class ActionRequest:
    schema_version: int
    message_type: MessageType
    request_id: str
    principal_id: str
    action: ActionKind
    target: str
    amount_cents: int
    risk: Risk


@dataclass(frozen=True)
class TrustedContext:
    """Server-owned attributes. Never copy these from model output."""

    authenticated_principal: str
    remaining_budget_cents: int
    allowed_targets: frozenset[str]


@dataclass(frozen=True)
class PolicyDecision:
    allow: bool
    policy_revision: str
    reason: str


@dataclass(frozen=True)
class Approval:
    approver: str
    payload_sha256: str


@dataclass(frozen=True)
class ReleaseCandidate:
    artifact_digest: str
    signature_verified: bool
    provenance_verified: bool
    tests_passed: bool
    pinned_components: bool


_FIELDS = {
    "schema_version", "message_type", "request_id", "principal_id",
    "action", "target", "amount_cents", "risk",
}
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_TARGET = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@:-]{0,127}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def _exact_int(value: Any, field: str) -> int:
    # bool is an int subclass in Python and must be rejected explicitly.
    if type(value) is not int:
        raise ContractError(f"{field} must be an integer")
    return value


def parse_action_request(raw: str) -> ActionRequest:
    """Parse untrusted JSON, rejecting duplicates, unknown fields and loose types."""

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ContractError(f"duplicate field: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=reject_duplicates)
    except ContractError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ContractError("malformed JSON") from exc
    if type(value) is not dict:
        raise ContractError("message must be a JSON object")
    keys = set(value)
    if keys != _FIELDS:
        unknown, missing = keys - _FIELDS, _FIELDS - keys
        raise ContractError(f"field mismatch; unknown={sorted(unknown)}, missing={sorted(missing)}")
    if _exact_int(value["schema_version"], "schema_version") != 1:
        raise ContractError("unsupported schema_version")
    for field, pattern in (("request_id", _ID), ("principal_id", _ID), ("target", _TARGET)):
        item = value[field]
        if type(item) is not str or not pattern.fullmatch(item):
            raise ContractError(f"invalid {field}")
    try:
        message_type = MessageType(value["message_type"])
        action = ActionKind(value["action"])
        risk = Risk(value["risk"])
    except (ValueError, TypeError) as exc:
        raise ContractError("invalid enum value") from exc
    amount = _exact_int(value["amount_cents"], "amount_cents")
    if not 0 <= amount <= 1_000_000:
        raise ContractError("amount_cents outside allowed range")
    return ActionRequest(1, message_type, value["request_id"], value["principal_id"],
                         action, value["target"], amount, risk)


def validate_semantics(request: ActionRequest, context: TrustedContext) -> None:
    """Validate business invariants using trusted server-side state."""
    if request.principal_id != context.authenticated_principal:
        raise GateRejected("principal mismatch")
    if request.target not in context.allowed_targets:
        raise GateRejected("target is not allowlisted")
    if request.amount_cents > context.remaining_budget_cents:
        raise GateRejected("budget exceeded")
    if request.action is not ActionKind.TRANSFER and request.amount_cents != 0:
        raise GateRejected("amount is only valid for transfers")
    if request.action in {ActionKind.TRANSFER, ActionKind.DEPLOY} and request.risk is not Risk.HIGH:
        raise GateRejected("side-effecting action must be high risk")


def canonical_payload_hash(request: ActionRequest) -> str:
    """Hash the exact normalized action shown to an approver."""
    payload = asdict(request)
    payload["message_type"] = request.message_type.value
    payload["action"] = request.action.value
    payload["risk"] = request.risk.value
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_approval(request: ActionRequest, approval: Optional[Approval]) -> None:
    if approval is None:
        raise GateRejected("approval required")
    if not approval.approver:
        raise GateRejected("approver identity missing")
    if not hmac.compare_digest(canonical_payload_hash(request), approval.payload_sha256):
        raise GateRejected("approval does not bind this payload")


class PolicyEnforcementPoint:
    """The only route to a protected commit; any PDP anomaly denies access."""

    def __init__(self, pdp: Callable[[Mapping[str, Any]], Optional[PolicyDecision]]) -> None:
        self._pdp = pdp

    def require_allow(self, policy_input: Mapping[str, Any]) -> PolicyDecision:
        try:
            decision = self._pdp(policy_input)
        except Exception as exc:
            raise GateRejected("policy service failure (fail closed)") from exc
        if (type(decision) is not PolicyDecision or decision.allow is not True
                or not decision.policy_revision):
            raise GateRejected("policy denied or returned no valid decision")
        return decision


def admission_gate(raw: str, context: TrustedContext, pep: PolicyEnforcementPoint,
                   approval: Optional[Approval] = None) -> tuple[ActionRequest, PolicyDecision]:
    request = parse_action_request(raw)
    validate_semantics(request, context)
    if request.risk is Risk.HIGH:
        verify_approval(request, approval)
    decision = pep.require_allow({
        "principal": context.authenticated_principal,
        "action": request.action.value,
        "target": request.target,
        "risk": request.risk.value,
    })
    return request, decision


def release_gate(candidate: ReleaseCandidate, pep: PolicyEnforcementPoint) -> PolicyDecision:
    if not _DIGEST.fullmatch(candidate.artifact_digest):
        raise GateRejected("invalid artifact digest")
    failed = [name for name in ("signature_verified", "provenance_verified",
              "tests_passed", "pinned_components") if not getattr(candidate, name)]
    if failed:
        raise GateRejected("release checks failed: " + ", ".join(failed))
    return pep.require_allow({"operation": "release", "artifact_digest": candidate.artifact_digest})
