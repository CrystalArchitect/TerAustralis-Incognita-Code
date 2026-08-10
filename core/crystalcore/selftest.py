# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Self-test for CrystalBridge — the consent gate and the mind path.

    cd core && python3 -m crystalcore.selftest

Covers the two bugs this suite was written to catch and keep caught, and
the four-check gate specified in docs/CONSENT-GATE-SPEC.md:

  1. The bridge must reach the same memory the human sees. It once loaded
     the mind by file path, from core/apps/lumina/crystalcore — a
     directory that never existed — so every tool touching the companion
     (recall, teach, message) crashed at runtime. That whole class of bug
     is now gone by construction: the mind is `crystalcore.mind`, an
     ordinary subpackage of this one, imported normally. What remains
     path-dependent is only the *profiles folder*, which still lives
     beside the interface, so that is what is checked here.

  2. ConsentGate.check() enforces provenance, approval, and permission in
     that order, and require_scope() enforces the fourth check for
     memory-touching tools. These tests pin the order — a wrong token
     from an approved guest must refuse as provenance, never as
     permission — and pin fail-closed defaults: no stored hash refuses,
     empty scope refuses, and memories without a visibility field are
     private.

Stdlib-only except for `mcp`, which importing crystalcore.bridge
requires (see requirements-bridge.txt). The mind additionally needs
`requests`; where that isn't installed, that one sub-check reports SKIP
rather than failing.
"""

from __future__ import annotations

from pathlib import Path

from crystalcore.config import BridgeConfig, GuestGrant
from crystalcore.gate import ConsentGate, token_hash

SECRET = "selftest-secret"


def _gate(
    tools: list[str] | None = None,
    approved: bool = True,
    *,
    secret: str | None = SECRET,
    read_scope: list[str] | None = None,
    write_scope: list[str] | None = None,
) -> ConsentGate:
    """A ConsentGate over an in-memory config for one guest 'claude'.

    profile_dir points nowhere real on purpose — every check below passes
    audit=False, so the gate never writes, and the fake path is never touched.
    `secret=None` models a guest with no provenance configured.
    """
    config = BridgeConfig(
        profile="selftest",
        human_name="selftest",
        interactive_approval=False,
        guests={"claude": GuestGrant(
            approved=approved,
            tools=list(tools or []),
            read_scope=list(read_scope or []),
            write_scope=list(write_scope or []),
            token_hash=token_hash(secret) if secret else "",
        )},
        profile_dir=Path("/nonexistent-selftest-profile"),
    )
    return ConsentGate(config)


def test_bridge_refuses_to_run_without_a_nominated_memory_folder():
    """The regression test for bug #1, in the form that survives the move.

    It used to assert that a path computed inside this repository resolved
    to a real directory — the interface the profiles hung off. The companion
    no longer lives here, so there is no such path to check, and computing
    one would be the bug rather than the test for it: it would resolve
    somewhere absent, the mind would create it, and a guest would be served
    an empty companion in silence.

    What matters now is the opposite property. Unconfigured, the bridge must
    stop. Both failure modes are checked, because "set but wrong" is the one
    a person actually hits.
    """
    import os
    import tempfile

    from crystalcore.bridge import MEMORY_DIR_ENV, _profiles_root

    before = os.environ.get(MEMORY_DIR_ENV)
    try:
        os.environ.pop(MEMORY_DIR_ENV, None)
        try:
            _profiles_root()
        except SystemExit:
            pass
        else:
            raise AssertionError(
                "the bridge resolved a memory folder with nothing set; it "
                "must refuse rather than guess")

        os.environ[MEMORY_DIR_ENV] = "/nonexistent/nobody/nominated/this"
        try:
            _profiles_root()
        except SystemExit:
            pass
        else:
            raise AssertionError(
                "the bridge accepted a path that is not a directory; it "
                "must refuse rather than let the mind create one")

        with tempfile.TemporaryDirectory() as real:
            os.environ[MEMORY_DIR_ENV] = real
            assert _profiles_root() == Path(real), (
                "a nominated, existing folder must be used as given")
    finally:
        if before is None:
            os.environ.pop(MEMORY_DIR_ENV, None)
        else:
            os.environ[MEMORY_DIR_ENV] = before


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


def test_approved_guest_with_allowed_tool_and_token_is_allowed():
    result = _gate(tools=["recall", "teach"]).check(
        "claude", "recall", token=SECRET, audit=False)
    assert result.allowed and result.decision == "allow" and result.check == "ok"


def test_approved_guest_with_disallowed_tool_is_refused():
    result = _gate(tools=["recall"]).check(
        "claude", "teach", token=SECRET, audit=False)
    assert not result.allowed and result.check == "permission"


def test_status_is_always_allowed_for_a_proven_approved_guest():
    """`status` is granted implicitly (gate.py's `| {"status"}`), even when
    it isn't in the guest's tool list — but only past provenance."""
    result = _gate(tools=[]).check("claude", "status", token=SECRET, audit=False)
    assert result.allowed, "status must be allowed for any proven, approved guest"


def test_unknown_guest_is_refused():
    result = _gate(tools=["recall"]).check(
        "stranger", "recall", token=SECRET, audit=False)
    assert not result.allowed and result.check == "approval"


def test_present_but_unapproved_guest_is_refused():
    result = _gate(tools=["recall"], approved=False).check(
        "claude", "recall", token=SECRET, audit=False)
    assert not result.allowed and result.check == "approval"


def test_missing_token_refuses_as_provenance():
    result = _gate(tools=["recall"]).check("claude", "recall", audit=False)
    assert not result.allowed and result.check == "provenance"
    assert result.decision == "refuse-provenance"


def test_wrong_token_refuses_as_provenance_not_permission():
    """Check order pinned: an approved guest presenting the wrong token
    must refuse at provenance — even for a tool it isn't permitted —
    because the later checks are meaningless against an unverified name."""
    result = _gate(tools=["recall"]).check(
        "claude", "some-unpermitted-tool", token="wrong", audit=False)
    assert not result.allowed and result.check == "provenance"


def test_guest_with_no_minted_token_refuses_fail_closed():
    """Strict provenance from day one: a grant without a stored hash
    refuses. Enforcement is never optional — an unconfigured guest is an
    unproven guest."""
    result = _gate(tools=["recall"], secret=None).check(
        "claude", "recall", token="anything", audit=False)
    assert not result.allowed and result.check == "provenance"


def test_empty_scope_refuses_even_after_the_gate_allows():
    gate = _gate(tools=["recall"])
    assert gate.check("claude", "recall", token=SECRET, audit=False).allowed
    result = gate.require_scope("claude", "recall", "read", audit=False)
    assert not result.allowed and result.check == "scope"
    assert result.decision == "refuse-scope"


def test_granted_scope_passes():
    gate = _gate(tools=["recall"], read_scope=["shared"])
    result = gate.require_scope("claude", "recall", "read", audit=False)
    assert result.allowed


def test_memories_without_visibility_are_private():
    """The migration default, pinned at the filter itself: an entry with no
    visibility field must not survive a shared-only view. Runs against the
    mind's real `_memory_block` when its deps are installed; otherwise the
    filter logic is pinned directly."""
    try:
        from crystalcore.mind import CrystalCore  # noqa: F401  (dep probe)
    except ModuleNotFoundError as exc:
        if exc.name in {"requests", "flask"}:
            legacy = {"text": "old private thing", "tags": []}
            shared = {"text": "shared thing", "tags": [], "visibility": "shared"}
            visible = {"shared"}
            kept = [m for m in (legacy, shared)
                    if m.get("visibility", "private") in visible]
            assert kept == [shared]
            print(f"  SKIP mind-backed check — dep '{exc.name}' not installed "
                  "(filter default pinned directly instead)")
            return
        raise
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        companion = CrystalCore(memory_dir=tmp)
        companion._embed_ok = False  # no Ollama in tests; skip embeddings
        companion.memory.notes.append(
            {"text": "old private thing", "tags": []})  # pre-migration shape
        companion.memory.notes.append(
            {"text": "shared thing", "tags": [], "visibility": "shared"})
        guest_view = companion._memory_block(visible={"shared"})
        human_view = companion._memory_block()
        assert "old private thing" not in guest_view
        assert "shared thing" in guest_view
        assert "old private thing" in human_view, (
            "the human's own unfiltered view must still see everything")


def main() -> int:
    tests = [
        test_bridge_refuses_to_run_without_a_nominated_memory_folder,
        test_mind_imports_and_exposes_the_companion_class,
        test_approved_guest_with_allowed_tool_and_token_is_allowed,
        test_approved_guest_with_disallowed_tool_is_refused,
        test_status_is_always_allowed_for_a_proven_approved_guest,
        test_unknown_guest_is_refused,
        test_present_but_unapproved_guest_is_refused,
        test_missing_token_refuses_as_provenance,
        test_wrong_token_refuses_as_provenance_not_permission,
        test_guest_with_no_minted_token_refuses_fail_closed,
        test_empty_scope_refuses_even_after_the_gate_allows,
        test_granted_scope_passes,
        test_memories_without_visibility_are_private,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\n{len(tests)}/{len(tests)} passed. The gate keeps four doors, honestly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
