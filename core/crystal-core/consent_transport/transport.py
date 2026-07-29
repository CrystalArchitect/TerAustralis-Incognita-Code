# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""TCP transport — where the Noise handshake meets a real socket.

Binds to 127.0.0.1 by default, same rule as everything else in this repo
that opens a port (the Starline Weaver server does the same). Exposing this
beyond localhost/LAN is an explicit operator choice, not a default.
"""

from __future__ import annotations

import socket
import struct
import threading
import time

from . import protocol
from .consent import ConsentEngine
from .fragment import MemoryFragment
from .identity import Identity
from .noise import HandshakeFailed, HandshakeState, StaticKeypair
from .peers import Peer, PeerStore

DEFAULT_PORT = 8890

# An IK handshake message is tiny and fixed-shape: 96 bytes for the
# initiator's (e, encrypted s, encrypted payload), 48 for the responder's.
# Anything claiming more than this is not a handshake. This is the one
# read that happens before we know who the peer is, so it gets the
# tightest bound in the module — an unauthenticated stranger must never
# be able to size our allocations.
MAX_HANDSHAKE_LEN = 4096

# How long an unauthenticated connection may keep a worker thread before
# we hang up, and how many such connections may be in flight at once.
# Without these a peer that opens a socket and then says nothing holds a
# thread forever, and enough of them exhaust the server.
HANDSHAKE_TIMEOUT = 10.0
MAX_CONCURRENT_CONNECTIONS = 32


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise protocol.ProtocolError("connection closed mid-frame")
        buf += chunk
    return bytes(buf)


def _send_raw(sock: socket.socket, data: bytes) -> None:
    sock.sendall(struct.pack(">I", len(data)) + data)


def _recv_raw(sock: socket.socket, max_len: int = MAX_HANDSHAKE_LEN) -> bytes:
    (length,) = struct.unpack(">I", _recv_exact(sock, 4))
    if length > max_len:
        raise protocol.ProtocolError("peer announced an oversized handshake frame")
    return _recv_exact(sock, length)


def _static_keypair(identity: Identity) -> StaticKeypair:
    return StaticKeypair(identity.dh_key, identity.dh_public_bytes)


class Denied(Exception):
    """The responder is aware of the request and declined it — distinct
    from a network or handshake failure."""


FragmentProvider = "Callable[[list[str], float, str], list[MemoryFragment]]"


class StarlineServer:
    """Responder role: accepts connections, authenticates the peer via the
    pinned Noise handshake, and serves requests only for peers who are
    both known (paired) and consented — checked fresh on every request,
    so a mid-session revoke takes effect on the very next connection."""

    def __init__(
        self,
        identity: Identity,
        peer_store: PeerStore,
        consent_engine: ConsentEngine,
        fragment_provider,
        host: str = "127.0.0.1",
        port: int = DEFAULT_PORT,
        token_store=None,
    ):
        self.identity = identity
        self.peer_store = peer_store
        self.consent_engine = consent_engine
        self.fragment_provider = fragment_provider
        # Optional second gate. The boolean engine answers "may this peer
        # ask at all"; a TokenStore answers the narrower question the
        # Consent Token schema specifies -- may they have *this kind*,
        # right now, under a token that has not expired or been revoked.
        # Both must say yes. Omitted, the server behaves exactly as before,
        # which is why every existing deployment keeps working.
        #
        # No wire change is needed for this: the issuer holds its own
        # tokens and checks them before releasing anything, the same shape
        # as the consent check above it.
        self.token_store = token_store
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._slots = threading.BoundedSemaphore(MAX_CONCURRENT_CONNECTIONS)

    def start(self) -> int:
        """Bind and begin serving in a background thread. Returns the
        bound port (useful when port=0 asks the OS to pick one)."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(5)
        self.port = self._sock.getsockname()[1]
        self._thread = threading.Thread(target=self._serve_loop, daemon=True)
        self._thread.start()
        return self.port

    def stop(self) -> None:
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
        if self._thread:
            self._thread.join(timeout=2)

    def _serve_loop(self) -> None:
        while not self._stop.is_set():
            try:
                conn, _addr = self._sock.accept()
            except OSError:
                return
            # Refuse rather than queue when every slot is busy: a caller
            # that is turned away retries, a caller parked on a semaphore
            # is indistinguishable from the flood that parked it.
            if not self._slots.acquire(blocking=False):
                conn.close()
                continue
            conn.settimeout(HANDSHAKE_TIMEOUT)
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn: socket.socket) -> None:
        try:
            hs = HandshakeState(
                initiator=False, local_static=_static_keypair(self.identity), remote_static=None
            )
            msg1 = _recv_raw(conn)
            hs.read_message(msg1)
            msg2 = hs.write_message(b"")
            _send_raw(conn, msg2)

            c1, c2 = hs.split()  # c1 = initiator->responder, c2 = responder->initiator
            recv_cs, send_cs = c1, c2

            peer = self.peer_store.find_by_dh(hs.rs.hex())
            frame = protocol.recv_frame(conn, recv_cs)

            if peer is None:
                protocol.send_frame(conn, send_cs, protocol.denied("unpaired peer"))
                return
            if frame.get("type") != "request":
                protocol.send_frame(conn, send_cs, protocol.denied("expected a request"))
                return
            if not self.consent_engine.is_granted(peer.fingerprint):
                protocol.send_frame(conn, send_cs, protocol.denied("consent not granted"))
                return

            items = self.fragment_provider(frame.get("kinds", []), frame.get("since", 0.0), peer.fingerprint)

            if self.token_store is not None:
                # Filter by what a live token actually admits, per fragment.
                # Filtering rather than refusing the whole request: a peer
                # holding a token for one kind should get that kind, not a
                # blanket denial because they also asked for another.
                allowed = []
                for frag in items:
                    if self.token_store.is_authorized(peer.sign_public_hex, frag.kind):
                        allowed.append(frag)
                if not allowed and items:
                    try:
                        self.token_store.authorize(peer.sign_public_hex)
                        reason = "no token admits the requested kinds"
                    except Exception as exc:
                        reason = str(exc)
                    protocol.send_frame(conn, send_cs, protocol.denied(reason))
                    return
                items = allowed

            protocol.send_frame(conn, send_cs, protocol.fragments([f.to_dict() for f in items]))
        except (HandshakeFailed, protocol.ProtocolError, OSError):
            pass  # a failed/hostile connection just gets dropped, no diagnostic leak
        finally:
            conn.close()
            self._slots.release()


class StarlineClient:
    """Initiator role: connects to a known, pinned peer and requests
    fragments. The Noise handshake itself is the authentication — if the
    peer on the other end doesn't hold the private key matching the
    pinned dh_public_hex, the handshake fails before any request is sent."""

    def __init__(self, identity: Identity):
        self.identity = identity

    def request_fragments(
        self, peer: Peer, host: str, port: int, kinds: list[str], since: float = 0.0, timeout: float = 5.0
    ) -> list[MemoryFragment]:
        sock = socket.create_connection((host, port), timeout=timeout)
        try:
            hs = HandshakeState(
                initiator=True,
                local_static=_static_keypair(self.identity),
                remote_static=bytes.fromhex(peer.dh_public_hex),
            )
            msg1 = hs.write_message(b"")
            _send_raw(sock, msg1)
            msg2 = _recv_raw(sock)
            hs.read_message(msg2)  # raises HandshakeFailed if this isn't really `peer`

            c1, c2 = hs.split()
            send_cs, recv_cs = c1, c2

            protocol.send_frame(sock, send_cs, protocol.request(kinds, since))
            reply = protocol.recv_frame(sock, recv_cs)

            if reply.get("type") == "denied":
                raise Denied(reply.get("reason", "denied"))
            if reply.get("type") != "fragments":
                raise protocol.ProtocolError(f"unexpected reply type {reply.get('type')!r}")

            results = []
            for raw in reply.get("fragments", []):
                frag = MemoryFragment.from_dict(raw)
                if not frag.verify(bytes.fromhex(peer.sign_public_hex)):
                    continue  # drop anything that doesn't verify — never trust unverified content
                results.append(frag)
            return results
        finally:
            sock.close()
