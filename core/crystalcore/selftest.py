# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Self-test for CrystalBridge — the consent gate and the Lumina path.

    cd core && python3 -m crystalcore.selftest

Covers the two bugs this suite was written to catch and keep caught:

  1. bridge.py's LUMINA_PKG_DIR must resolve to Lumina's real package
     directory. It once pointed at core/apps/lumina/crystalcore, which
     does not exist (Lumina lives under vision/, not core/), so every
     tool that touches the companion — recall, teach, message — crashed
     at runtime. This suite fails loudly if that path ever stops
     resolving to a real directory.

  2. ConsentGate.check() enforces exactly two checks (guest-approval and
     tool-permission). Its docstring once claimed four. These tests pin
     the behavior the docstring now truthfully describes.

Stdlib-only except for `mcp`, which importing crystalcore.bridge
requires (see requirements-bridge.txt). The full Lumina-framework import
additionally needs vision-side deps (requests); where those aren't
installed, that one sub-check reports SKIP rather than failing — the
path check above already proves the fix without them.
"""

from __future__ import annotations

from pathlib import Path

from crystalcore.bridge import LUMINA_PKG_DIR, _load_lumina_framework
from crystalcore.config import BridgeConfig, GuestGrant
from crystalcore.gate import ConsentGate


def _gate(tools: list[str] | None = None, approved: bool = True) -> ConsentGate:
    """A ConsentGate over an in-memory config for one guest 'claude'.

    profile_dir points nowhere real on purpose — every check below passes
    audit=False, so the gate never writes, and the fake path is never touched.
    """
    config = BridgeConfig(
        profile="selftest",
        human_name="selftest",
        interactive_approval=False,
        guests={"claude": GuestGrant(approved=approved, tools=list(tools or []))},
        profile_dir=Path("/nonexistent-selftest-profile"),
    )
    return ConsentGate(config)


def test_lumina_pkg_dir_resolves_to_a_real_directory():
    """The regression test for bug #1: the path must exist on disk."""
    assert LUMINA_PKG_DIR.is_dir(), (
        f"LUMINA_PKG_DIR does not resolve to a real directory: {LUMINA_PKG_DIR}. "
        "Lumina's framework lives at vision/apps/lumina/crystalcore/ — if the "
        "repo layout moved, fix bridge.py's path math."
    )
    assert (LUMINA_PKG_DIR / "__init__.py").is_file(), (
        f"{LUMINA_PKG_DIR} exists but has no __init__.py — not an importable package."
    )


def test_lumina_framework_imports_and_exposes_lumina():
    """The end-to-end check for bug #1: the aliased import actually works.

    Skips (does not fail) when a vision-side dependency the framework
    imports at module level — currently `requests` — isn't installed, so
    a lightweight core-only environment can still run this suite. A path
    failure would surface as something other than a missing vision dep,
    and is NOT skipped.
    """
    try:
        framework = _load_lumina_framework()
    except ModuleNotFoundError as exc:
        vision_deps = {"requests", "flask"}
        if exc.name in vision_deps:
            print(
                f"  SKIP framework import — vision-side dep '{exc.name}' not "
                "installed (path check above already proves the fix)"
            )
            return
        raise
    assert hasattr(framework, "Lumina"), (
        "Lumina's framework imported but exposes no `Lumina` class."
    )


def test_approved_guest_with_allowed_tool_is_allowed():
    result = _gate(tools=["recall", "teach"]).check("claude", "recall", audit=False)
    assert result.allowed and result.decision == "allow"


def test_approved_guest_with_disallowed_tool_is_refused():
    result = _gate(tools=["recall"]).check("claude", "teach", audit=False)
    assert not result.allowed and result.decision == "refuse"


def test_status_is_always_allowed_for_an_approved_guest():
    """`status` is granted implicitly (gate.py's `| {"status"}`), even when
    it isn't in the guest's tool list."""
    result = _gate(tools=[]).check("claude", "status", audit=False)
    assert result.allowed, "status must be allowed for any approved guest"


def test_unknown_guest_is_refused():
    result = _gate(tools=["recall"]).check("stranger", "recall", audit=False)
    assert not result.allowed and result.decision == "refuse"


def test_present_but_unapproved_guest_is_refused():
    result = _gate(tools=["recall"], approved=False).check("claude", "recall", audit=False)
    assert not result.allowed and result.decision == "refuse"


def main() -> int:
    tests = [
        test_lumina_pkg_dir_resolves_to_a_real_directory,
        test_lumina_framework_imports_and_exposes_lumina,
        test_approved_guest_with_allowed_tool_is_allowed,
        test_approved_guest_with_disallowed_tool_is_refused,
        test_status_is_always_allowed_for_an_approved_guest,
        test_unknown_guest_is_refused,
        test_present_but_unapproved_guest_is_refused,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\n{len(tests)}/{len(tests)} passed. The gate keeps two doors, honestly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
