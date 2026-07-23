# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: Apache-2.0

"""Append-only audit log for CrystalBridge."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_audit(
    audit_path: Path,
    *,
    guest: str,
    tool: str,
    arguments: dict[str, Any] | None,
    decision: str,
    reason: str = "",
    detail: dict[str, Any] | None = None,
) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": _now(),
        "guest": guest,
        "tool": tool,
        "arguments": arguments or {},
        "decision": decision,
        "reason": reason,
    }
    if detail:
        record["detail"] = detail
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_audit(audit_path: Path) -> list[dict[str, Any]]:
    if not audit_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows
