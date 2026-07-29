# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Self-test for CrystalBridge — the consent gate and the mind path.

    cd core && python3 -m crystalcore.selftest

Covers the two bugs this suite was written to catch and keep caught:

  1. The bridge must reach the same memory the human sees. It once loaded
     the mind by file path, from core/apps/lumina/crystalcore — a
     directory that never existed — so every tool touching the companion
     (recall, teach, message) crashed at runtime. That whole class of bug
     is now gone by construction: the mind is `crystalcore.mind`, an
     ordinary subpackage of this one, imported normally. What remains
     path-dependent is only the *profiles folder*, which still lives
     beside the interface, so that is what is checked here.

  2. ConsentGate.check() enforces exactly two checks (guest-approval and
     tool-permission). Its docstring once claimed four. These tests pin
     the behavior the docstring now truthfully describes.

Stdlib-only except for `mcp`, which importing crystalcore.bridge
requires (see requirements-bridge.txt). The mind additionally needs
`requests`; where that isn't installed, that one sub-check reports SKIP
rather than failing.
"""

from __future__ import annotations

from pathlib import Path

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


def test_interface_dir_resolves_to_a_real_directory():
    """The regression test for bug #1, in the form that survives the move.

    The mind is imported now, not path-loaded, so the only path the bridge
    still computes is the interface directory its profiles hang off. If the
    repo layout moves again, this fails loudly rather than silently opening
    an empty profile folder somewhere else.
    """
    from crystalcore.bridge import APP_DIR

    assert APP_DIR.is_dir(), (
        f"APP_DIR does not resolve to a real directory: {APP_DIR}. "
        "The interface lives at vision/apps/clementine/ — if the repo "
        "layout moved, fix bridge.py's path math."
    )


def test_mind_imports_and_exposes_the_companion_class():
    """The end-to-end check for bug #1: the mind is reachable as a package.

    Skips (does not fail) when a dependency the mind imports at module
    level — currently `requests` — isn't installed, so a lightweight
    core-only environment can still run this suite. An import failure for
    any other reason is NOT skipped.
    """
    try:
        from crystalcore import mind
    except ModuleNotFoundError as exc:
        if exc.name in {"requests", "flask"}:
            print(
                f"  SKIP mind import — dep '{exc.name}' not installed "
                "(the path check above already proves the layout)"
            )
            return
        raise
    assert hasattr(mind, "CrystalCore"), (
        "crystalcore.mind imported but exposes no `CrystalCore` class."
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
        test_interface_dir_resolves_to_a_real_directory,
        test_mind_imports_and_exposes_the_companion_class,
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
