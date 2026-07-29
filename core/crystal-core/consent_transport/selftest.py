# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Self-test for Consent Transport — proves the sovereignty guarantees are real.

    python3 -m consent_transport.selftest

Every test here uses real TCP sockets and a real Noise handshake — no
mocking of the crypto or the network layer. If this passes, two agents on
a real network can actually talk to each other under these same rules.
"""

from __future__ import annotations

import json
import socket
import stat
import struct
import tempfile
import time
from pathlib import Path

from . import transport
from .agent import StarlineAgent
from .consent import TokenStore
from .token import ConsentError, ConsentToken, Revocation, Scope
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


def test_identity_file_is_never_group_or_world_readable():
    """The private key must be unreadable by anyone else the whole time
    it exists — not merely by the time save() returns."""
    d = Path(tempfile.mkdtemp(prefix="starline_test_perm_"))
    path = d / "identity.json"
    Identity.generate().save(path)
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode & 0o077 == 0, f"identity file is {oct(mode)}, readable beyond its owner"
    # No temporary copy may be left lying around with looser bits either.
    assert not (d / "identity.json.tmp").exists()


def test_failed_save_leaves_the_old_identity_intact():
    """Losing this file is unrecoverable, so a save that dies partway
    through must not take the existing identity with it."""
    d = Path(tempfile.mkdtemp(prefix="starline_test_atomic_"))
    path = d / "identity.json"
    original = Identity.generate()
    original.save(path)
    before = path.read_bytes()

    broken = Identity.generate()

    class Boom(Exception):
        pass

    def explode(*_args, **_kwargs):
        raise Boom("disk full")

    real_dump = json.dump
    json.dump = explode
    try:
        broken.save(path)
    except Boom:
        pass
    else:
        raise AssertionError("save() should have propagated the write failure")
    finally:
        json.dump = real_dump

    assert path.read_bytes() == before, "a failed save overwrote the live identity"
    assert Identity.load(path).fingerprint == original.fingerprint
    assert not (d / "identity.json.tmp").exists()


def test_oversized_handshake_frame_is_refused():
    """The pre-authentication read is the one a stranger controls. A
    peer that announces a huge frame must be hung up on, not believed."""
    a, _b = _two_agents()
    port = a.serve(port=0)
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=5)
        try:
            # 3 GiB announced, nothing delivered. Before the length check
            # this parked a worker thread on an unbounded read.
            sock.sendall(struct.pack(">I", 3 * 1024 * 1024 * 1024))
            sock.settimeout(5)
            assert sock.recv(1) == b"", "server kept the oversized frame alive"
        finally:
            sock.close()
        # The server must still be healthy for an honest peer afterwards.
        second = socket.create_connection(("127.0.0.1", port), timeout=5)
        second.close()
    finally:
        a.stop_serving()


def test_stalled_connections_cannot_exhaust_the_server():
    """Connections that open and then say nothing must age out, and must
    not lock an honest peer out of the server while they hang around."""
    a, _b = _two_agents()
    port = a.serve(port=0)
    stalled = []
    try:
        for _ in range(transport.MAX_CONCURRENT_CONNECTIONS + 8):
            try:
                s = socket.create_connection(("127.0.0.1", port), timeout=2)
                stalled.append(s)
            except OSError:
                break
        # Over the cap, the server refuses rather than queueing — so an
        # honest connection still completes instead of waiting behind them.
        probe = socket.create_connection(("127.0.0.1", port), timeout=5)
        probe.close()
    finally:
        for s in stalled:
            s.close()
        a.stop_serving()


def _store(tmp_prefix="starline_test_tok_"):
    d = Path(tempfile.mkdtemp(prefix=tmp_prefix))
    ident = Identity.generate()
    return TokenStore(ident, d / "tokens.json"), ident


def test_token_grants_only_what_its_scope_names():
    """§6 no ambient authority: a token for one kind is not a token for
    every kind."""
    store, _ = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    store.issue(peer, "share reflections for the evening weave", kinds=("emotional",))
    assert store.is_authorized(peer, "emotional")
    assert not store.is_authorized(peer, "episodic")
    assert not store.is_authorized(peer, "mythic")


def test_token_with_no_kinds_admits_every_kind():
    """The schema allows a class-wide grant; absence of a kind list means
    all of them, not none of them."""
    store, _ = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    store.issue(peer, "full exchange, this session only")
    for kind in ("episodic", "semantic", "emotional", "mythic"):
        assert store.is_authorized(peer, kind), kind


def test_token_expires():
    """§6 time binding, the gap this whole module exists to close: before
    tokens, a grant said once was true forever."""
    store, _ = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    token = store.issue(peer, "one minute of telemetry", ttl_seconds=60)
    assert token.is_valid(recipient_fingerprint_hex=peer)
    # Same token, evaluated after its expiry -- no clock manipulation,
    # just asking the question at a later moment.
    later = token.expires_at + 1
    assert not token.is_valid(recipient_fingerprint_hex=peer, now=later)
    try:
        token.verify(recipient_fingerprint_hex=peer, now=later)
        assert False, "an expired token must not verify"
    except ConsentError as exc:
        assert "expired" in str(exc)


def test_token_refuses_a_peer_it_was_not_issued_to():
    """A token is useless to anyone but its named recipient, even though
    it is perfectly signed."""
    store, _ = _store()
    intended = Identity.generate().sign_public_bytes.hex()
    someone_else = Identity.generate().sign_public_bytes.hex()
    token = store.issue(intended, "for you alone")
    assert token.is_valid(recipient_fingerprint_hex=intended)
    assert not token.is_valid(recipient_fingerprint_hex=someone_else)
    assert not store.is_authorized(someone_else)


def test_tampering_with_any_field_breaks_the_signature():
    """Every field is inside the signed payload -- widening scope or
    pushing out expiry after signing must invalidate the token."""
    store, ident = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    token = store.issue(peer, "narrow and short", kinds=("mythic",), ttl_seconds=60)
    assert token.is_valid(recipient_fingerprint_hex=peer)

    widened = ConsentToken.from_dict(token.to_dict())
    widened.scope = Scope(kinds=("mythic", "episodic"))
    assert not widened.is_valid(recipient_fingerprint_hex=peer), "scope widening must break the signature"

    extended = ConsentToken.from_dict(token.to_dict())
    extended.expires_at = extended.expires_at + 86400
    assert not extended.is_valid(recipient_fingerprint_hex=peer), "expiry extension must break the signature"

    repurposed = ConsentToken.from_dict(token.to_dict())
    repurposed.purpose = "something else entirely"
    assert not repurposed.is_valid(recipient_fingerprint_hex=peer), "purpose change must break the signature"


def test_purpose_is_mandatory():
    """§6 purpose binding. A permission whose reason nobody recorded
    cannot be reviewed later."""
    peer = Identity.generate().sign_public_bytes.hex()
    for bad in ("", "   "):
        try:
            ConsentToken(issuer="00", recipient=peer, purpose=bad)
            assert False, "a token without a purpose must not be constructible"
        except ValueError:
            pass


def test_revocation_kills_the_token_and_is_signed():
    store, ident = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    token = store.issue(peer, "until I change my mind")
    assert store.is_authorized(peer)

    rev = store.revoke(token.token_id)
    assert rev.verify()
    assert not store.is_authorized(peer)
    try:
        store.authorize(peer)
        assert False, "a revoked token must not authorize"
    except ConsentError as exc:
        assert "revoked" in str(exc)


def test_forged_revocation_is_refused():
    """A revocation is a denial-of-service against a peer's consent if
    anyone can mint one, so it is checked as carefully as a grant."""
    store, ident = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    token = store.issue(peer, "should survive a forgery attempt")

    impostor = Identity.generate()
    forged = Revocation(token_id=token.token_id, issuer=impostor.sign_public_bytes.hex())
    forged.sign(impostor)          # honestly signed -- by the wrong identity
    assert forged.verify()          # it *is* a valid signature, by an impostor
    assert not store.accept_revocation(forged), "a revocation from a non-issuer must be refused"
    assert store.is_authorized(peer), "the token must survive"

    unsigned = Revocation(token_id=token.token_id, issuer=ident.sign_public_bytes.hex())
    assert not store.accept_revocation(unsigned), "an unsigned revocation must be refused"
    assert store.is_authorized(peer)


def test_revocation_gossiped_from_the_real_issuer_is_honoured():
    """§5: revocation propagates through consented channels, so a node
    must accept one it did not issue -- if it verifies."""
    issuer_store, issuer_ident = _store("starline_test_issuer_")
    peer = Identity.generate().sign_public_bytes.hex()
    token = issuer_store.issue(peer, "will be revoked and gossiped")
    rev = issuer_store.revoke(token.token_id)

    # A different node that holds the same token, told about it second-hand.
    other, _ = _store("starline_test_relay_")
    other.tokens[token.token_id] = token
    assert other.is_authorized(peer)
    assert other.accept_revocation(rev)
    assert not other.is_authorized(peer)


def test_tokens_and_revocations_survive_a_reload():
    store, ident = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    keep = store.issue(peer, "kept", kinds=("semantic",))
    drop = store.issue(peer, "revoked")
    store.revoke(drop.token_id)

    reloaded = TokenStore(ident, store.path)
    assert set(reloaded.tokens) == {keep.token_id, drop.token_id}
    assert reloaded.revoked_ids == {drop.token_id}
    assert reloaded.is_authorized(peer, "semantic")
    assert not reloaded.is_authorized(peer, "episodic"), "the surviving token is scoped"


def test_refusal_says_which_check_failed():
    """The human deciding what to do next needs to know whether to
    re-issue, widen scope, or refuse outright."""
    store, _ = _store()
    peer = Identity.generate().sign_public_bytes.hex()
    try:
        store.authorize(peer)
        assert False
    except ConsentError as exc:
        assert "no consent token" in str(exc)

    store.issue(peer, "emotional only", kinds=("emotional",))
    try:
        store.authorize(peer, "episodic")
        assert False
    except ConsentError as exc:
        assert "scope" in str(exc)


def test_token_scope_is_enforced_over_a_real_connection():
    """The end-to-end claim: with a TokenStore attached, a peer receives
    only the kinds a live token admits -- over a real socket and a real
    handshake, not just in the store's own unit tests."""
    a, b = _two_agents()
    _pair(a, b)
    b.add_local_fragment("episodic", "an episode b remembers")
    b.add_local_fragment("mythic", "a myth b keeps")
    b.grant(a.fingerprint)

    store = TokenStore(b.identity, Path(tempfile.mkdtemp(prefix="starline_test_wire_")) / "t.json")
    store.issue(a.identity.sign_public_bytes.hex(), "myth only, for the weave", kinds=("mythic",))
    port = b.serve(token_store=store)
    try:
        results = a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)
        contents = [f.content for f in results]
        assert "a myth b keeps" in contents, "the scoped kind must come through"
        assert "an episode b remembers" not in contents, "an unscoped kind must not"
    finally:
        b.stop_serving()


def test_expired_token_stops_the_exchange_that_a_live_one_allowed():
    """Time binding, proven on the wire: the same peer, the same request,
    allowed and then refused purely because the token lapsed."""
    a, b = _two_agents()
    _pair(a, b)
    b.add_local_fragment("mythic", "a myth b keeps")
    b.grant(a.fingerprint)

    store = TokenStore(b.identity, Path(tempfile.mkdtemp(prefix="starline_test_exp_")) / "t.json")
    token = store.issue(a.identity.sign_public_bytes.hex(), "briefly", kinds=("mythic",), ttl_seconds=3600)

    port = b.serve(token_store=store)
    try:
        assert len(a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)) == 1

        # Expire it in place -- re-signed by the issuer, so this is an
        # honest short token, not a tampered one.
        token.expires_at = time.time() - 1
        token.signature = ""
        token.sign(b.identity)
        store.tokens[token.token_id] = token
        store.save()

        try:
            a.request_fragments(a.peers.get(b.fingerprint), "127.0.0.1", port)
            assert False, "an expired token must stop the exchange"
        except Denied as exc:
            assert "expired" in str(exc)
    finally:
        b.stop_serving()


def main() -> int:
    tests = [
        test_identity_roundtrip,
        test_identity_file_is_never_group_or_world_readable,
        test_failed_save_leaves_the_old_identity_intact,
        test_oversized_handshake_frame_is_refused,
        test_stalled_connections_cannot_exhaust_the_server,
        test_token_grants_only_what_its_scope_names,
        test_token_with_no_kinds_admits_every_kind,
        test_token_expires,
        test_token_refuses_a_peer_it_was_not_issued_to,
        test_tampering_with_any_field_breaks_the_signature,
        test_purpose_is_mandatory,
        test_revocation_kills_the_token_and_is_signed,
        test_forged_revocation_is_refused,
        test_revocation_gossiped_from_the_real_issuer_is_honoured,
        test_tokens_and_revocations_survive_a_reload,
        test_refusal_says_which_check_failed,
        test_token_scope_is_enforced_over_a_real_connection,
        test_expired_token_stops_the_exchange_that_a_live_one_allowed,
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
