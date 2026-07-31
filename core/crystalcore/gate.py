# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Fail-closed consent gate - door before the house."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

from crystalcore.audit import append_audit
from crystalcore.config import BridgeConfig


def token_hash(secret: str) -> str:
    """SHA-256 hex of a guest secret — what bridge_config.json stores."""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


@dataclass
class GateResult:
    allowed: bool
    reason: str
    decision: str  # allow | refuse | refuse-provenance | refuse-scope
    check: str = ""  # stage that decided: provenance | approval | permission | scope | ok

    def as_refusal_payload(self) -> dict[str, Any]:
        return {
            "ok": False,
            "refusal": True,
            "reason": self.reason,
            "decision": self.decision,
            "check": self.check,
        }


class ConsentGate:
    """Four checks, fail-closed, in this order:

    1. Provenance — does the presented token prove this is really the
       named guest? No stored hash, no token, or a mismatch all refuse.
       Origin that cannot be established is treated exactly like absent
       consent; there is no fallback to the later checks.
    2. Approval — is the guest approved at all.
    3. Permission — may it call this specific tool.
    4. Scope — applied where a tool touches memory (`require_scope`):
       which visibility classes a grant may read, and which it writes into.

    Spec: docs/CONSENT-GATE-SPEC.md. Provenance here is launcher
    authentication — possession of a per-guest minted secret — stated as
    exactly that, not cryptographic identity of a remote model.
    """

    def __init__(self, config: BridgeConfig):
        self.config = config

    def check(
        self,
        guest: str,
        tool: str,
        arguments: dict[str, Any] | None = None,
        *,
        token: str = "",
        audit: bool = True,
    ) -> GateResult:
        guest = (guest or "").strip().lower()
        tool = (tool or "").strip().lower()
        arguments = arguments or {}

        grant = self.config.guest(guest)
        if grant is None or not grant.approved:
            result = GateResult(
                allowed=False,
                reason=f"guest '{guest or '(missing)'}' is not approved",
                decision="refuse",
                check="approval",
            )
            if audit:
                self._log(guest or "(missing)", tool, arguments, result,
                          token_verified=False)
            return result

        # Provenance runs before anything the grant permits: the later
        # checks are meaningless against an unverified name.
        if not grant.token_hash:
            result = GateResult(
                allowed=False,
                reason=(f"guest '{guest}' has no provenance configured — "
                        "mint a token (--mint-token) before this guest can act"),
                decision="refuse-provenance",
                check="provenance",
            )
            if audit:
                self._log(guest, tool, arguments, result, token_verified=False)
            return result
        if not token or not hmac.compare_digest(token_hash(token), grant.token_hash):
            result = GateResult(
                allowed=False,
                reason=(f"provenance for guest '{guest}' could not be "
                        "established — token missing or wrong"),
                decision="refuse-provenance",
                check="provenance",
            )
            if audit:
                self._log(guest, tool, arguments, result, token_verified=False)
            return result

        allowed_tools = set(grant.tools) | {"status"}
        if tool not in allowed_tools:
            result = GateResult(
                allowed=False,
                reason=f"guest '{guest}' has no permission for tool '{tool}'",
                decision="refuse",
                check="permission",
            )
            if audit:
                self._log(guest, tool, arguments, result, token_verified=True)
            return result

        result = GateResult(allowed=True, reason="ok", decision="allow", check="ok")
        if audit:
            self._log(guest, tool, arguments, result, token_verified=True)
        return result

    def require_scope(
        self,
        guest: str,
        tool: str,
        kind: str,  # "read" | "write"
        arguments: dict[str, Any] | None = None,
        *,
        audit: bool = True,
    ) -> GateResult:
        """The fourth check, for tools that touch memory. An empty scope
        list is absence of consent: the guest may reach the tool's door but
        finds nothing behind it, and the refusal says so rather than
        returning a silently empty result. Call only after check() allowed."""
        guest = (guest or "").strip().lower()
        grant = self.config.guest(guest)
        scope = (grant.read_scope if kind == "read" else grant.write_scope) if grant else []
        if not scope:
            result = GateResult(
                allowed=False,
                reason=(f"guest '{guest}' has no {kind} scope — no memory "
                        "class is shared with it"),
                decision="refuse-scope",
                check="scope",
            )
            if audit:
                self._log(guest, tool, arguments or {}, result, token_verified=True)
            return result
        return GateResult(allowed=True, reason="ok", decision="allow", check="ok")

    def _log(
        self,
        guest: str,
        tool: str,
        arguments: dict[str, Any],
        result: GateResult,
        *,
        token_verified: bool,
    ) -> None:
        safe_args = dict(arguments)
        for key in ("text", "query"):
            if key in safe_args and isinstance(safe_args[key], str) and len(safe_args[key]) > 200:
                safe_args[key] = safe_args[key][:200] + "..."
        append_audit(
            self.config.audit_path,
            guest=guest,
            tool=tool,
            arguments=safe_args,
            decision=result.decision,
            reason=result.reason,
            detail={
                "check": result.check,
                "provenance": {
                    "token_verified": token_verified,
                    "transport": "stdio",
                },
            },
        )
