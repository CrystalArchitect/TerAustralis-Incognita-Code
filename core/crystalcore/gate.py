# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Fail-closed consent gate - door before the house."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crystalcore.audit import append_audit
from crystalcore.config import BridgeConfig


def token_hash(secret: str) -> str:
    """SHA-256 hex of a guest secret — what bridge_config.json stores."""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_args(arguments: dict[str, Any]) -> dict[str, Any]:
    safe_args = dict(arguments)
    for key in ("text", "query"):
        if key in safe_args and isinstance(safe_args[key], str) and len(safe_args[key]) > 200:
            safe_args[key] = safe_args[key][:200] + "..."
    return safe_args


@dataclass
class GateResult:
    allowed: bool
    reason: str
    decision: str
    check: str = ""
    request_id: str = ""

    def as_refusal_payload(self) -> dict[str, Any]:
        return {
            "ok": False,
            "refusal": True,
            "reason": self.reason,
            "decision": self.decision,
            "check": self.check,
            "request_id": self.request_id,
        }


def read_revocation_ledger(path: Path) -> tuple[dict[str, str], bool]:
    if not path.exists():
        return {}, True
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}, False
    latest: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return {}, False
        guest = str(row.get("guest", "")).strip().lower()
        action = str(row.get("action", "")).strip().lower()
        if not guest or action not in ("revoke", "reinstate"):
            return {}, False
        latest[guest] = action
    return latest, True


def append_revocation(
    path: Path, *, guest: str, action: str, reason: str = "", by: str = "human",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": _now(),
        "guest": guest.strip().lower(),
        "action": action,
        "reason": reason,
        "by": by,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_pending(
    path: Path, *, request_id: str, guest: str, tool: str,
    arguments: dict[str, Any], status: str = "received",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": _now(),
        "id": request_id,
        "guest": guest,
        "tool": tool,
        "arguments": _safe_args(arguments),
        "status": status,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


class ConsentGate:
    """Five checks, fail-closed: revocation, approval, provenance, permission, scope."""

    def __init__(self, config: BridgeConfig):
        self.config = config

    def check(
        self, guest: str, tool: str, arguments: dict[str, Any] | None = None,
        *, token: str = "", audit: bool = True,
    ) -> GateResult:
        guest = (guest or "").strip().lower()
        tool = (tool or "").strip().lower()
        arguments = arguments or {}
        request_id = f"req-{secrets.token_hex(6)}"

        if audit:
            try:
                append_pending(
                    self.config.pending_path, request_id=request_id,
                    guest=guest or "(missing)", tool=tool,
                    arguments=arguments, status="received",
                )
            except OSError:
                pass

        latest, ledger_ok = read_revocation_ledger(self.config.revocations_path)
        if not ledger_ok:
            result = GateResult(
                allowed=False,
                reason="revocation ledger is unreadable — refusing all guests until it is fixed",
                decision="refuse-revoked", check="revocation", request_id=request_id,
            )
            if audit:
                self._log(guest or "(missing)", tool, arguments, result, token_verified=False)
            return result
        if guest and latest.get(guest) == "revoke":
            result = GateResult(
                allowed=False, reason=f"guest '{guest}' is revoked",
                decision="refuse-revoked", check="revocation", request_id=request_id,
            )
            if audit:
                self._log(guest, tool, arguments, result, token_verified=False)
            return result

        grant = self.config.guest(guest)
        if grant is None or not grant.approved:
            result = GateResult(
                allowed=False,
                reason=f"guest '{guest or '(missing)'}' is not approved",
                decision="refuse", check="approval", request_id=request_id,
            )
            if audit:
                self._log(guest or "(missing)", tool, arguments, result, token_verified=False)
            return result

        if not grant.token_hash:
            result = GateResult(
                allowed=False,
                reason=(f"guest '{guest}' has no provenance configured — "
                        "mint a token (--mint-token) before this guest can act"),
                decision="refuse-provenance", check="provenance", request_id=request_id,
            )
            if audit:
                self._log(guest, tool, arguments, result, token_verified=False)
            return result
        if not token or not hmac.compare_digest(token_hash(token), grant.token_hash):
            result = GateResult(
                allowed=False,
                reason=(f"provenance for guest '{guest}' could not be "
                        "established — token missing or wrong"),
                decision="refuse-provenance", check="provenance", request_id=request_id,
            )
            if audit:
                self._log(guest, tool, arguments, result, token_verified=False)
            return result

        allowed_tools = set(grant.tools) | {"status"}
        if tool not in allowed_tools:
            result = GateResult(
                allowed=False,
                reason=f"guest '{guest}' has no permission for tool '{tool}'",
                decision="refuse", check="permission", request_id=request_id,
            )
            if audit:
                self._log(guest, tool, arguments, result, token_verified=True)
            return result

        result = GateResult(
            allowed=True, reason="ok", decision="allow", check="ok", request_id=request_id,
        )
        if audit:
            self._log(guest, tool, arguments, result, token_verified=True)
        return result

    def require_scope(
        self, guest: str, tool: str, kind: str,
        arguments: dict[str, Any] | None = None, *,
        audit: bool = True, request_id: str = "",
    ) -> GateResult:
        guest = (guest or "").strip().lower()
        grant = self.config.guest(guest)
        scope = (grant.read_scope if kind == "read" else grant.write_scope) if grant else []
        types = (grant.read_types if kind == "read" else grant.write_types) if grant else []

        if not types:
            result = GateResult(
                allowed=False,
                reason=(f"guest '{guest}' has no memory types granted — "
                        f"no {kind} types are shared with it"),
                decision="refuse-scope", check="scope", request_id=request_id,
            )
            if audit:
                self._log(guest, tool, arguments or {}, result, token_verified=True)
            return result

        if not scope:
            result = GateResult(
                allowed=False,
                reason=(f"guest '{guest}' has no {kind} scope — no memory "
                        "class is shared with it"),
                decision="refuse-scope", check="scope", request_id=request_id,
            )
            if audit:
                self._log(guest, tool, arguments or {}, result, token_verified=True)
            return result

        if kind == "write" and "semantic" not in types:
            result = GateResult(
                allowed=False,
                reason=(f"guest '{guest}' cannot write memory — "
                        "'semantic' is not in write_types (notes are the "
                        "semantic layer)"),
                decision="refuse-scope", check="scope", request_id=request_id,
            )
            if audit:
                self._log(guest, tool, arguments or {}, result, token_verified=True)
            return result

        return GateResult(
            allowed=True, reason="ok", decision="allow", check="ok", request_id=request_id,
        )

    def _log(
        self, guest: str, tool: str, arguments: dict[str, Any], result: GateResult,
        *, token_verified: bool,
    ) -> None:
        detail: dict[str, Any] = {
            "check": result.check,
            "request_id": result.request_id,
            "provenance": {"token_verified": token_verified, "transport": "stdio"},
        }
        append_audit(
            self.config.audit_path, guest=guest, tool=tool,
            arguments=_safe_args(arguments), decision=result.decision,
            reason=result.reason, detail=detail,
        )
