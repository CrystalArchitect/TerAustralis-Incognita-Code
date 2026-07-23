# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: Apache-2.0

"""Self-test for Consent Transport — proves the sovereignty guarantees are real.

    python3 -m consent_transport.selftest

Every test here uses real TCP sockets and a real Noise handshake — no
mocking of the crypto or the network layer. If this passes, two agents on
a real network can actually talk to each other under these same rules.
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from .agent import StarlineAgent
from .fragment import MemoryFragment
from .identity import Identity
from .transport import Denied


def _two_agents():
    """Two agents in isolated temp directories — never touches real
    identity/peer files, and never collides with a concurrent test run."""
    d1 = tempfile.mkdtemp(prefix="starline_test_a_")
    d2 = tempfile.mkdtemp(prefix="starline_test_b_")
    return StarlineAgent(Path(d1)), StarlineAgent(Path(d2))


def _pair(a: StarlineAgent, b: StarlineAgent) -> None:
    """Manual pairing both directions — the deterministic path a QR-code
    exchange would also produce."""
    a.pair_manual(b.identity.sign_public_bytes.hex(), b.identity.dh_public_bytes.hex(), "b")
    b.pair_manual(a.identity.sign_public_bytes.hex(), a.identity.dh_public_bytes.hex(), "a")


def test_identity_roundtrip():
    d = Path(tempfile.mkdtemp(prefix="starline_test_id_"))
    path = d / "identity.json"
    original = Identity.generate()
    original.save(path)
    loaded = Identity.load(path)
    assert loaded.sign_public_bytes == original.sign_public_bytes
    assert loaded.dh_public_bytes == original.dh_public_bytes
    assert loaded.fingerprint == original.fingerprint
    # a signature made by the original must verify against the loaded public key
    sig = original.sign(b"prove it")
    from .identity import verify
    assert verify(loaded.sign_public_bytes, b"prove it", sig)


def test_fragment_sign_and_verify():
    identity = Identity.generate()
    frag = MemoryFragment(kind="episodic", content="first water", sender_fingerprint=identity.fingerprint)
    frag.sign(identity)
    assert frag.verify(identity.sign_public_bytes)
    # tampering with content after signing must break verification
    frag.content = "tampered"
    assert not frag.verify(identity.sign_public_bytes)


def test_denied_without_consent():
    a, b = _two_agents()
    _pair(a, b)
    b.add_local_fragment("episodic", "a memory only b holds")
    port = b.serve()
    try:
        try:
            a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)
            assert False, "must be denied before consent is granted"
        except Denied as exc:
            assert "consent" in str(exc)
    finally:
        b.stop_serving()


def test_granted_consent_allows_exchange():
    a, b = _two_agents()
    _pair(a, b)
    b.add_local_fragment("episodic", "a memory only b holds")
    b.grant(a.fingerprint)
    port = b.serve()
    try:
        results = a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)
        assert len(results) == 1
        assert results[0].content == "a memory only b holds"
        assert results[0].verify(bytes.fromhex(b.identity.sign_public_bytes.hex()))
    finally:
        b.stop_serving()


def test_revocation_takes_effect_next_request():
    a, b = _two_agents()
    _pair(a, b)
    b.add_local_fragment("episodic", "revocable memory")
    b.grant(a.fingerprint)
    port = b.serve()
    try:
        first = a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)
        assert len(first) == 1
        b.revoke(a.fingerprint)
        try:
            a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)
            assert False, "revocation must block the very next request"
        except Denied:
            pass
    finally:
        b.stop_serving()


def test_unpaired_peer_is_rejected():
    a, b = _two_agents()
    # deliberately NOT paired — b has never heard of a
    port = b.serve()
    try:
        from .peers import Peer
        fake_peer = Peer(
            fingerprint=b.fingerprint,  # dh key below still won't match any known-by-b entry from a's side... actually a doesn't need b paired to attempt; what matters is b doesn't know a
            sign_public_hex=b.identity.sign_public_bytes.hex(),
            dh_public_hex=b.identity.dh_public_bytes.hex(),
        )
        try:
            a.request_fragments(fake_peer, "127.0.0.1", port)
            assert False, "an agent b has never paired with must be rejected"
        except Denied as exc:
            assert "unpaired" in str(exc)
    finally:
        b.stop_serving()


def test_fragment_kind_and_since_filtering():
    a, b = _two_agents()
    _pair(a, b)
    b.add_local_fragment("episodic", "old event")
    cutoff = time.time()
    time.sleep(0.01)
    b.add_local_fragment("emotional", "new feeling")
    b.grant(a.fingerprint)
    port = b.serve()
    try:
        only_new = a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port, since=cutoff)
        assert len(only_new) == 1 and only_new[0].content == "new feeling"

        only_emotional = a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port, kinds=["emotional"])
        assert len(only_emotional) == 1 and only_emotional[0].kind == "emotional"
    finally:
        b.stop_serving()


def test_forged_fragment_is_rejected_by_receiver():
    """Even if a hostile responder sends fragments 'signed' by someone
    else, the client must drop anything that doesn't verify — the wire
    protocol trusts nobody, the client re-checks every signature itself."""
    a, b = _two_agents()
    _pair(a, b)
    b.grant(a.fingerprint)
    # Inject a fragment honestly signed by a different identity, then
    # relabel its attribution to claim it's from b — simulating a
    # compromised or malicious responder trying to pass off someone
    # else's content as its own. sender_fingerprint is itself covered by
    # the signature, so relabeling after signing breaks verification.
    impostor = Identity.generate()
    forged = MemoryFragment(kind="mythic", content="not really from b", sender_fingerprint=impostor.fingerprint)
    forged.sign(impostor)
    forged.sender_fingerprint = b.fingerprint  # forge the attribution after signing
    b._local_fragments.append(forged)
    b.add_local_fragment("mythic", "a real fragment from b")

    port = b.serve()
    try:
        results = a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)
        contents = [f.content for f in results]
        assert "a real fragment from b" in contents
        assert "not really from b" not in contents, "forged/unverifiable fragment must be dropped"
    finally:
        b.stop_serving()


def test_discovery_via_unicast_loopback():
    """Broadcast may be unavailable in sandboxed environments; this proves
    the announce/listen wire format works using loopback unicast, which
    exercises the identical code path a real LAN broadcast would."""
    a, b = _two_agents()
    import threading
    from . import discovery

    listener_result = []

    def listen():
        listener_result.extend(discovery.listen_for_peers(duration=1.5, bind_host="127.0.0.1"))

    t = threading.Thread(target=listen, daemon=True)
    t.start()
    time.sleep(0.2)
    a.announce(port=12345, label="agent-a", broadcast_addr="127.0.0.1")
    t.join(timeout=3)

    assert len(listener_result) == 1
    ann = listener_result[0]
    assert ann.fingerprint == a.fingerprint
    assert ann.tcp_port == 12345
    assert ann.label == "agent-a"


def main() -> int:
    tests = [
        test_identity_roundtrip,
        test_fragment_sign_and_verify,
        test_denied_without_consent,
        test_granted_consent_allows_exchange,
        test_revocation_takes_effect_next_request,
        test_unpaired_peer_is_rejected,
        test_fragment_kind_and_since_filtering,
        test_forged_fragment_is_rejected_by_receiver,
        test_discovery_via_unicast_loopback,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\n{len(tests)}/{len(tests)} passed. Sovereignty holds — no data moved without consent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
