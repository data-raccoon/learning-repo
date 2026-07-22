"""Dependency-free reference capability proxy.

This module demonstrates application-layer policy enforcement.  It is NOT an
OS sandbox and must not execute hostile code in-process.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import queue
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit


class Denied(Exception):
    """The request failed closed at the policy enforcement point."""


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class AuditEvent:
    kind: str
    decision: str
    subject: str
    tool: str
    reason: str
    capability_id: str
    at: int
    details: Mapping[str, Any] = field(default_factory=dict)


class MemoryAuditSink:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def emit(self, event: AuditEvent) -> None:
        self.events.append(event)


class CapabilityIssuer:
    """Issues compact HMAC capabilities for this educational example.

    Production deployments should use a managed issuer, rotation, revocation,
    asymmetric keys where appropriate, and protected key storage.
    """

    def __init__(self, signing_key: bytes, issuer: str = "example-issuer") -> None:
        if len(signing_key) < 32:
            raise ValueError("signing_key must contain at least 32 bytes")
        self._key = signing_key
        self.issuer = issuer

    def issue(
        self,
        *,
        subject: str,
        audience: str,
        tools: list[str],
        path_roots: list[str] | None = None,
        egress: list[str] | None = None,
        ttl_seconds: int = 60,
        max_calls: int = 1,
        max_input_bytes: int = 4096,
        max_output_bytes: int = 4096,
        timeout_ms: int = 1000,
        budget_units: int = 1,
        now: int | None = None,
    ) -> str:
        if not 1 <= ttl_seconds <= 300:
            raise ValueError("ttl_seconds must be between 1 and 300")
        issued_at = int(time.time() if now is None else now)
        claims = {
            "iss": self.issuer,
            "sub": subject,
            "aud": audience,
            "iat": issued_at,
            "exp": issued_at + ttl_seconds,
            "jti": uuid.uuid4().hex,
            "tools": sorted(set(tools)),
            "path_roots": path_roots or [],
            "egress": egress or [],
            "limits": {
                "max_calls": max_calls,
                "max_input_bytes": max_input_bytes,
                "max_output_bytes": max_output_bytes,
                "timeout_ms": timeout_ms,
                "budget_units": budget_units,
            },
        }
        body = _b64encode(_canonical_json(claims))
        signature = _b64encode(hmac.new(self._key, body.encode("ascii"), hashlib.sha256).digest())
        return f"{body}.{signature}"


class CapabilityVerifier:
    def __init__(self, signing_key: bytes, *, issuer: str, audience: str) -> None:
        self._key = signing_key
        self.issuer = issuer
        self.audience = audience

    def verify(self, token: str, *, now: int | None = None) -> dict[str, Any]:
        try:
            body, supplied = token.split(".", 1)
            expected = _b64encode(hmac.new(self._key, body.encode("ascii"), hashlib.sha256).digest())
            if not hmac.compare_digest(supplied, expected):
                raise Denied("invalid signature")
            claims = json.loads(_b64decode(body))
        except Denied:
            raise
        except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
            raise Denied("malformed capability") from exc

        current = int(time.time() if now is None else now)
        if claims.get("iss") != self.issuer:
            raise Denied("wrong issuer")
        if claims.get("aud") != self.audience:
            raise Denied("wrong audience")
        if not isinstance(claims.get("exp"), int) or current >= claims["exp"]:
            raise Denied("expired capability")
        if not isinstance(claims.get("iat"), int) or claims["iat"] > current + 5:
            raise Denied("invalid issued-at time")
        required = ("sub", "jti", "tools", "path_roots", "egress", "limits")
        if any(name not in claims for name in required):
            raise Denied("incomplete capability")
        return claims


_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)((?:api[_-]?key|password|secret|token)\s*[:=]\s*)[^\s,;]+"),
)


def redact(value: Any) -> Any:
    """Redact common secret shapes before output or audit persistence."""
    if isinstance(value, str):
        for pattern in _SECRET_PATTERNS:
            value = pattern.sub(r"\1[REDACTED]", value)
        return value
    if isinstance(value, Mapping):
        return {
            key: "[REDACTED]" if str(key).lower() in {
                "authorization", "api_key", "apikey", "password", "secret", "token"
            } else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    return value


@dataclass(frozen=True)
class ToolContext:
    subject: str
    capability_id: str
    deadline_monotonic: float


Tool = Callable[[Mapping[str, Any], ToolContext], Any]


class CapabilityToolProxy:
    """Deny-by-default reference monitor for named tool calls."""

    def __init__(self, verifier: CapabilityVerifier, audit: MemoryAuditSink) -> None:
        self._verifier = verifier
        self._audit = audit
        self._tools: dict[str, tuple[Tool, int]] = {}
        self._usage: dict[str, dict[str, int]] = {}
        self._lock = threading.Lock()

    def register(self, name: str, handler: Tool, *, cost_units: int = 1) -> None:
        if cost_units < 0:
            raise ValueError("cost_units cannot be negative")
        self._tools[name] = (handler, cost_units)

    def execute(self, capability: str, tool: str, arguments: Mapping[str, Any]) -> Any:
        claims: dict[str, Any] = {}
        try:
            claims = self._verifier.verify(capability)
            self._authorize(capability, claims, tool, arguments)
            handler, cost = self._tools[tool]
            self._reserve(claims, cost)
            timeout_ms = self._positive_limit(claims, "timeout_ms")
            context = ToolContext(
                subject=claims["sub"],
                capability_id=claims["jti"],
                deadline_monotonic=time.monotonic() + timeout_ms / 1000,
            )
            result = self._call_with_timeout(handler, arguments, context, timeout_ms)
            safe_result = redact(result)
            output_size = len(_canonical_json(safe_result))
            if output_size > self._positive_limit(claims, "max_output_bytes"):
                raise Denied("output size limit exceeded")
            self._record("tool_call", "allow", claims, tool, "authorized", {"output_bytes": output_size})
            return safe_result
        except Denied as exc:
            self._record("tool_call", "deny", claims, tool, str(exc), {})
            raise
        except Exception as exc:
            self._record("tool_call", "deny", claims, tool, "invalid request or result", {})
            raise Denied("invalid tool request or result") from exc

    def _authorize(
        self, capability: str, claims: Mapping[str, Any], tool: str, arguments: Mapping[str, Any]
    ) -> None:
        if tool not in self._tools or tool not in claims["tools"]:
            raise Denied("tool is not allowed")
        if self._contains(arguments, capability):
            raise Denied("capability token passthrough is forbidden")
        if len(_canonical_json(arguments)) > self._positive_limit(claims, "max_input_bytes"):
            raise Denied("input size limit exceeded")
        if "path" in arguments:
            self._check_path(str(arguments["path"]), claims["path_roots"])
        if "url" in arguments:
            self._check_egress(str(arguments["url"]), claims["egress"])

    @staticmethod
    def _contains(value: Any, needle: str) -> bool:
        if isinstance(value, str):
            return needle in value
        if isinstance(value, Mapping):
            return any(CapabilityToolProxy._contains(v, needle) for v in value.values())
        if isinstance(value, (list, tuple)):
            return any(CapabilityToolProxy._contains(v, needle) for v in value)
        return False

    @staticmethod
    def _check_path(candidate: str, roots: list[str]) -> None:
        target = Path(candidate).resolve(strict=False)
        allowed = False
        for raw_root in roots:
            root = Path(raw_root).resolve(strict=False)
            if target == root or root in target.parents:
                allowed = True
                break
        if not allowed:
            raise Denied("path is outside allowed roots")

    @staticmethod
    def _check_egress(url: str, allowlist: list[str]) -> None:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise Denied("egress URL is not an allowed HTTPS destination")
        try:
            port = parsed.port or 443
        except ValueError as exc:
            raise Denied("invalid egress port") from exc
        destination = f"{parsed.hostname.lower()}:{port}"
        if destination not in {entry.lower() for entry in allowlist}:
            raise Denied("egress destination is not allowed")

    def _reserve(self, claims: Mapping[str, Any], cost: int) -> None:
        with self._lock:
            usage = self._usage.setdefault(claims["jti"], {"calls": 0, "budget": 0})
            if usage["calls"] + 1 > self._positive_limit(claims, "max_calls"):
                raise Denied("call limit exceeded")
            if usage["budget"] + cost > self._positive_limit(claims, "budget_units"):
                raise Denied("budget limit exceeded")
            usage["calls"] += 1
            usage["budget"] += cost

    @staticmethod
    def _positive_limit(claims: Mapping[str, Any], name: str) -> int:
        value = claims.get("limits", {}).get(name)
        if not isinstance(value, int) or value < 0:
            raise Denied(f"invalid {name} limit")
        return value

    @staticmethod
    def _call_with_timeout(handler: Tool, arguments: Mapping[str, Any], context: ToolContext, timeout_ms: int) -> Any:
        replies: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)

        def invoke() -> None:
            try:
                replies.put((True, handler(arguments, context)))
            except Exception as exc:  # tool errors do not bypass the proxy
                replies.put((False, exc))

        threading.Thread(target=invoke, daemon=True, name="example-tool-call").start()
        try:
            ok, value = replies.get(timeout=timeout_ms / 1000)
        except queue.Empty as exc:
            raise Denied("tool timeout exceeded") from exc
        if not ok:
            raise Denied("tool failed") from value
        return value

    def _record(
        self,
        kind: str,
        decision: str,
        claims: Mapping[str, Any],
        tool: str,
        reason: str,
        details: Mapping[str, Any],
    ) -> None:
        self._audit.emit(AuditEvent(
            kind=kind,
            decision=decision,
            subject=str(claims.get("sub", "unknown")),
            tool=tool,
            reason=redact(reason),
            capability_id=str(claims.get("jti", "unknown")),
            at=int(time.time()),
            details=redact(details),
        ))
