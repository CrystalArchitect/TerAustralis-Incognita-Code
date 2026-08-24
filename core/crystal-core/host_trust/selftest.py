# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0
"""Self-test for host trust classification.

    python3 -m host_trust.selftest

Does not mint identities. Does not talk to a network. Does not unshare
a vendor pool. HADES is not a HostClass.
"""

from __future__ import annotations

from .classify import HostClass, classify, refuse_steward_persist


def test_override_local():
    assert classify({"CRYSTAL_HOST_CLASS": "local"}) is HostClass.LOCAL
    assert refuse_steward_persist(env={"CRYSTAL_HOST_CLASS": "local"}) is False


def test_override_shared():
    assert classify({"CRYSTAL_HOST_CLASS": "shared"}) is HostClass.SHARED
    assert refuse_steward_persist(env={"CRYSTAL_HOST_CLASS": "shared"}) is True


def test_override_delegated():
    assert classify({"CRYSTAL_HOST_CLASS": "delegated"}) is HostClass.DELEGATED
    assert refuse_steward_persist(env={"CRYSTAL_HOST_CLASS": "delegated"}) is False


def test_unknown_when_unset():
    assert classify({}) is HostClass.UNKNOWN
    assert refuse_steward_persist(env={}) is True


def test_garbage_override_is_unknown():
    assert classify({"CRYSTAL_HOST_CLASS": "hades"}) is HostClass.UNKNOWN
    assert classify({"CRYSTAL_HOST_CLASS": "HADES"}) is HostClass.UNKNOWN


def test_github_hosted_is_shared():
    env = {"GITHUB_ACTIONS": "true", "RUNNER_ENVIRONMENT": "github-hosted"}
    assert classify(env) is HostClass.SHARED
    assert refuse_steward_persist(env=env) is True


def test_github_actions_without_runner_env_is_shared():
    assert classify({"GITHUB_ACTIONS": "true"}) is HostClass.SHARED


def test_self_hosted_runner_is_delegated():
    env = {"GITHUB_ACTIONS": "true", "RUNNER_ENVIRONMENT": "self-hosted"}
    assert classify(env) is HostClass.DELEGATED
    assert refuse_steward_persist(env=env) is False


def test_override_beats_github_heuristic():
    env = {
        "GITHUB_ACTIONS": "true",
        "RUNNER_ENVIRONMENT": "github-hosted",
        "CRYSTAL_HOST_CLASS": "local",
    }
    assert classify(env) is HostClass.LOCAL


def main() -> int:
    tests = [
        test_override_local,
        test_override_shared,
        test_override_delegated,
        test_unknown_when_unset,
        test_garbage_override_is_unknown,
        test_github_hosted_is_shared,
        test_github_actions_without_runner_env_is_shared,
        test_self_hosted_runner_is_delegated,
        test_override_beats_github_heuristic,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  ok  {t.__name__}")
        except Exception as exc:
            failed += 1
            print(f"  FAIL  {t.__name__}: {exc}")
    print(f"{len(tests) - failed}/{len(tests)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
