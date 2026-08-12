# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Configuration loader for CrystalBridge — reads profiles/<name>/bridge_config.json.

Guest grants carry two independent consent axes:
  - visibility scope (private|shared) — which visibility classes a guest may touch
  - memory types (episodic|semantic|reflective) — which memory *layers* a guest may touch

The memory structure *is* the taxonomy (no per-entry type field):
  summaries → episodic, notes+facts → semantic, reflections → reflective,
  conversation → working (never guest-readable).

Empty scope or empty types is absence of consent, not legacy full access.
Unknown type names fail loud at load ("Told, or stopped.").
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = SRC_ROOT / "profiles"

# Documented taxonomy only — no new memory classes.
KNOWN_MEMORY_TYPES = frozenset({"episodic", "semantic", "reflective"})


@dataclass
class GuestGrant:
    approved: bool
    tools: list[str] = field(default_factory=list)
    # Scope: which memory visibility classes this guest may read, and which
    # single class its teachings land in (the first entry). Empty means none —
    # absence of scope is absence of consent, not legacy full access.
    read_scope: list[str] = field(default_factory=list)
    write_scope: list[str] = field(default_factory=list)
    # Type-gates: which memory layers this guest may read / write.
    # subsets of {episodic, semantic, reflective}. Missing field → [] → refuse.
    read_types: list[str] = field(default_factory=list)
    write_types: list[str] = field(default_factory=list)
    # Provenance: SHA-256 hex of this guest's minted secret. Empty means no
    # provenance is configured, and the gate refuses — mint one with
    # `python -m crystalcore.bridge --mint-token <guest>`.
    token_hash: str = ""


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

    @property
    def revocations_path(self) -> Path:
        return self.profile_dir / "revocations.jsonl"

    @property
    def pending_path(self) -> Path:
        return self.profile_dir / "pending.jsonl"

    def guest(self, name: str) -> GuestGrant | None:
        return self.guests.get((name or "").strip().lower())

    @classmethod
    def load(cls, profile: str = "default") -> "BridgeConfig":
        profile_dir = PROFILES_DIR / profile
        config_path = profile_dir / "bridge_config.json"
        if not config_path.exists():
            raise FileNotFoundError(
                f"No bridge config at {config_path}. Copy "
                f"profiles/default/bridge_config.json to a new profile folder and "
                f"edit it, or pass --profile default."
            )
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        guests: dict[str, GuestGrant] = {}
        for name, grant in raw.get("guests", {}).items():
            read_types = list(grant.get("read_types", []))
            write_types = list(grant.get("write_types", []))
            for t in read_types + write_types:
                if t not in KNOWN_MEMORY_TYPES:
                    raise SystemExit(
                        f"CrystalBridge: unknown memory type '{t}' in guest "
                        f"'{name}' ({config_path}). Known types: "
                        f"{sorted(KNOWN_MEMORY_TYPES)}. Told, or stopped."
                    )
            guests[name.strip().lower()] = GuestGrant(
                approved=bool(grant.get("approved", False)),
                tools=list(grant.get("tools", [])),
                read_scope=list(grant.get("read_scope", [])),
                write_scope=list(grant.get("write_scope", [])),
                read_types=read_types,
                write_types=write_types,
                token_hash=str(grant.get("token_hash", "")),
            )
        return cls(
            profile=raw.get("profile", profile),
            human_name=raw.get("human_name", ""),
            interactive_approval=bool(raw.get("interactive_approval", False)),
            guests=guests,
            profile_dir=profile_dir,
        )
