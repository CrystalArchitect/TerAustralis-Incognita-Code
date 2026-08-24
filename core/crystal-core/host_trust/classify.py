# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0
"""Classify the execution host. Fail-closed when origin cannot be established.

Steward override: CRYSTAL_HOST_CLASS=local|delegated|shared|unknown
Heuristics only run when that variable is unset.
"""

from __future__ import annotations

import os
from enum import Enum


class HostClass(str, Enum):
    LOCAL = "local"
    DELEGATED = "delegated"
    SHARED = "shared"
    UNKNOWN = "unknown"


_ALLOWED = {c.value: c for c in HostClass}

# Operations that must not land durable steward material on a pool.
STEWARD_PERSIST = frozenset(
    {
        "identity-mint",
        "consent-save",
        "token-mint",
        "fragment-persist",
        "memory-private-write",
    }
)


def classify(env: dict[str, str] | None = None) -> HostClass:
    e = os.environ if env is None else env
    raw = (e.get("CRYSTAL_HOST_CLASS") or "").strip().lower()
    if raw:
        return _ALLOWED.get(raw, HostClass.UNKNOWN)
    if e.get("GITHUB_ACTIONS") == "true":
        runner = (e.get("RUNNER_ENVIRONMENT") or "").strip().lower()
        if runner == "self-hosted":
            return HostClass.DELEGATED
        return HostClass.SHARED
    return HostClass.UNKNOWN


def refuse_steward_persist(
    host: HostClass | None = None,
    *,
    env: dict[str, str] | None = None,
) -> bool:
    """True when durable steward material must not be written."""
    if host is None:
        host = classify(env)
    return host in (HostClass.SHARED, HostClass.UNKNOWN)
