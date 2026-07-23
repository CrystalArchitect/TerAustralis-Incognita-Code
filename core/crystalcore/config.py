# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: Apache-2.0

"""Configuration loader for CrystalBridge — reads src/profiles/<name>/bridge_config.json.

Reconstructed spec: there is no design doc for this file (it was lost when the
project moved off the machine it was written on). The shape below is inferred
from the only two things that constrain it — `src/crystalcore/gate.py`, which
expects a `BridgeConfig` with a `.guest(name)` lookup and a `.audit_path`, and
the existing `src/profiles/default/bridge_config.json` on disk.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = SRC_ROOT / "profiles"


@dataclass
class GuestGrant:
    approved: bool
    tools: list[str] = field(default_factory=list)


@dataclass
class BridgeConfig:
    profile: str
    human_name: str
    interactive_approval: bool
    guests: dict[str, GuestGrant]
    profile_dir: Path

    @property
    def audit_path(self) -> Path:
        return self.profile_dir / "audit.jsonl"

    def guest(self, name: str) -> GuestGrant | None:
        return self.guests.get((name or "").strip().lower())

    @classmethod
    def load(cls, profile: str = "default") -> "BridgeConfig":
        profile_dir = PROFILES_DIR / profile
        config_path = profile_dir / "bridge_config.json"
        if not config_path.exists():
            raise FileNotFoundError(
                f"No bridge config at {config_path}. Copy "
                f"src/profiles/default/bridge_config.json to a new profile folder and "
                f"edit it, or pass --profile default."
            )
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        guests = {
            name.strip().lower(): GuestGrant(
                approved=bool(grant.get("approved", False)),
                tools=list(grant.get("tools", [])),
            )
            for name, grant in raw.get("guests", {}).items()
        }
        return cls(
            profile=raw.get("profile", profile),
            human_name=raw.get("human_name", ""),
            interactive_approval=bool(raw.get("interactive_approval", False)),
            guests=guests,
            profile_dir=profile_dir,
        )
