# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""CrystalBridge — the MCP stdio server that lets a guest AI meet the companion.

Reconstructed spec: the original `docs/CRYSTALBRIDGE.md` design doc was lost
along with the machine this project was first built on. This file's shape is
inferred from `src/crystalcore/gate.py` (the consent gate it must call before
doing anything), `docs/guides/MCP-Guest.md` / `docs/guides/Access.md` (the CLI and env var
contract guests already assume: `python -m crystalcore.bridge --profile
<name>`, guest identity via the CRYSTALBRIDGE_GUEST env var), and
`src/profiles/default/bridge_config.json` (the config shape). `recall` and
`teach` are deliberately thin, obvious wrappers around the mind's existing
memory methods rather than new memory logic of their own — this file grants
*access* to the mind, it doesn't reimplement it.

Every tool call passes through ConsentGate.check() first. Nothing runs for a
guest who isn't approved for that specific tool.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from crystalcore.config import BridgeConfig
from crystalcore.gate import ConsentGate
from crystalcore.mind import CrystalCore
from crystalcore.mind import profiles as mind_profiles

SRC_ROOT = Path(__file__).resolve().parent.parent          # core/
REPO_ROOT = SRC_ROOT.parent                                 # repo root (parent of core/ and vision/)
# The front-of-house interface. The mind is a sibling subpackage of this
# one now, so it is a plain import above; only the *memory* it reads still
# lives beside the interface, and that is what this path is for.
APP_DIR = REPO_ROOT / "vision" / "apps" / "clementine"


def _profiles_root() -> Path:
    """The profiles folder, anchored to the interface rather than to cwd.

    Mirrors the mind's own legacy fallback so the bridge and a human at the
    terminal always reach the same memory, including on installs that still
    carry the older folder name.
    """
    new = APP_DIR / mind_profiles.DEFAULT_PROFILES_DIR.name
    legacy = APP_DIR / mind_profiles.LEGACY_PROFILES_DIR.name
    if not new.exists() and legacy.exists():
        return legacy
    return new


class Bridge:
    """Holds the one companion instance this bridge process gives guests
    limited, gated access to."""

    def __init__(self, config: BridgeConfig, guest: str):
        self.config = config
        self.guest = guest
        self.gate = ConsentGate(config)
        self._companion = None

    def refuse(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = self.gate.check(self.guest, tool, arguments)
        return None if result.allowed else result.as_refusal_payload()

    @property
    def companion(self):
        """The companion, loaded lazily so `status` doesn't need Ollama.

        The mind's own `profiles.profile_dir()` resolves relative to the
        *calling process's* working directory. This bridge runs from
        `core/`, a different cwd than the terminal interface uses
        (`cd vision/apps/clementine && python3 clementine.py`), so the path
        is built explicitly and anchored to the interface — otherwise the
        bridge would open a second, empty profile dir wherever it happened
        to be launched from, instead of the memory the human actually sees.
        """
        if self._companion is None:
            safe_name = "".join(
                c for c in self.config.profile if c.isalnum() or c in "-_ "
            ).strip()
            memory_dir = _profiles_root() / safe_name
            self._companion = CrystalCore(memory_dir=str(memory_dir))
        return self._companion


def build_server(bridge: Bridge) -> FastMCP:
    mcp = FastMCP("crystalbridge")

    @mcp.tool()
    def status() -> dict[str, Any]:
        """Who you are to this bridge, and what you're allowed to do."""
        refusal = bridge.refuse("status", {})
        if refusal:
            return refusal
        grant = bridge.config.guest(bridge.guest)
        return {
            "ok": True,
            "guest": bridge.guest,
            "profile": bridge.config.profile,
            "tools": grant.tools if grant else [],
        }

    @mcp.tool()
    def recall(query: str = "") -> dict[str, Any]:
        """Recall what the companion remembers, optionally filtered by a query."""
        refusal = bridge.refuse("recall", {"query": query})
        if refusal:
            return refusal
        memory_text = bridge.companion._memory_block(query)
        return {"ok": True, "memory": memory_text or "(nothing remembered yet)"}

    @mcp.tool()
    def teach(text: str) -> dict[str, Any]:
        """Teach the companion something to remember permanently."""
        refusal = bridge.refuse("teach", {"text": text})
        if refusal:
            return refusal
        bridge.companion.remember(text)
        return {"ok": True, "remembered": text}

    @mcp.tool()
    def message(text: str) -> dict[str, Any]:
        """Leave a message for the human. Recorded, but not automatically
        folded into the companion's memory — that's what `teach` is for."""
        refusal = bridge.refuse("message", {"text": text})
        if refusal:
            return refusal
        from crystalcore.audit import append_audit

        append_audit(
            bridge.config.profile_dir / "messages.jsonl",
            guest=bridge.guest,
            tool="message",
            arguments={"text": text},
            decision="delivered",
        )
        return {"ok": True, "delivered": True}

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(prog="crystalcore.bridge")
    parser.add_argument("--profile", default="default")
    args = parser.parse_args()

    guest = os.environ.get("CRYSTALBRIDGE_GUEST", "")
    config = BridgeConfig.load(args.profile)
    bridge = Bridge(config, guest)
    server = build_server(bridge)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
