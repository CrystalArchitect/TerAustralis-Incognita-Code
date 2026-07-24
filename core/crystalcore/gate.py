# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Fail-closed consent gate - door before the house."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from crystalcore.audit import append_audit
from crystalcore.config import BridgeConfig


@dataclass
class GateResult:
    allowed: bool
    reason: str
    decision: str  # allow | refuse

    def as_refusal_payload(self) -> dict[str, Any]:
        return {
            "ok": False,
            "refusal": True,
            "reason": self.reason,
            "decision": self.decision,
        }


class ConsentGate:
    """Two checks, fail-closed: is the guest approved at all, and is it
    approved for this specific tool.

    Scope and provenance checks were once documented here as intended
    (and still are in vision/site/src/content/ARCHITECTURE.md), but were
    never implemented — no spec for what either should concretely mean
    survives anywhere in this repository, and GuestGrant has no field to
    hang them on. Implementing them is a separate, deliberate design task
    with the maintainer, not a correction of this docstring.
    """

    def __init__(self, config: BridgeConfig):
        self.config = config

    def check(
        self,
        guest: str,
        tool: str,
        arguments: dict[str, Any] | None = None,
        *,
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
            )
            if audit:
                self._log(guest or "(missing)", tool, arguments, result)
            return result

        allowed_tools = set(grant.tools) | {"status"}
        if tool not in allowed_tools:
            result = GateResult(
                allowed=False,
                reason=f"guest '{guest}' has no permission for tool '{tool}'",
                decision="refuse",
            )
            if audit:
                self._log(guest, tool, arguments, result)
            return result

        result = GateResult(allowed=True, reason="ok", decision="allow")
        if audit:
            self._log(guest, tool, arguments, result)
        return result

    def _log(
        self,
        guest: str,
        tool: str,
        arguments: dict[str, Any],
        result: GateResult,
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
        )
