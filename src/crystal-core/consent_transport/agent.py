# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""StarlineAgent — the one class most callers actually need.

Wraps identity, peers, consent, and transport into the small set of verbs
a companion (or a human, via a CLI) actually performs: be discoverable,
pair with someone, grant or revoke them, ask them for fragments, or serve
fragments to whoever asks and is allowed to have them.
"""

from __future__ import annotations

from pathlib import Path

from . import discovery
from .consent import ConsentEngine
from .discovery import Announcement
from .fragment import MemoryFragment
from .identity import Identity
from .peers import Peer, PeerStore
from .transport import Denied, StarlineClient, StarlineServer


class StarlineAgent:
    def __init__(self, state_dir: Path = Path(".")):
        state_dir = Path(state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        self.identity = Identity.load_or_generate(state_dir / "starline_identity.json")
        self.peers = PeerStore(state_dir / "starline_peers.json")
        self.consent = ConsentEngine(self.identity, state_dir / "starline_consent.json")
        self._server: StarlineServer | None = None
        self._local_fragments: list[MemoryFragment] = []  # in-memory demo store; a real
        # companion would back this with its own persistent memory (e.g. Lumina's
        # memory.json), filtered through whatever the human has approved for sharing.

    # ---------- identity ----------

    @property
    def fingerprint(self) -> str:
        return self.identity.fingerprint

    # ---------- pairing (discovery -> known peer, no consent yet) ----------

    def announce(self, port: int, label: str = "", broadcast_addr: str = "255.255.255.255") -> None:
        discovery.announce_once(self.identity, port, label, broadcast_addr)

    def discover(self, duration: float = 2.0, bind_host: str = "0.0.0.0") -> list[Announcement]:
        return discovery.listen_for_peers(duration, bind_host, own_fingerprint=self.fingerprint)

    def pair(self, announcement: Announcement, label: str = "") -> Peer:
        return self.peers.add(
            announcement.sign_public_hex, announcement.dh_public_hex, label or announcement.label
        )

    def pair_manual(self, sign_public_hex: str, dh_public_hex: str, label: str = "") -> Peer:
        """Pairing via a QR code / pasted key rather than LAN discovery."""
        return self.peers.add(sign_public_hex, dh_public_hex, label)

    # ---------- consent (paired -> allowed to actually exchange) ----------

    def grant(self, fingerprint: str) -> None:
        if not self.peers.is_known(fingerprint):
            raise ValueError("cannot grant consent to an unpaired peer")
        self.consent.grant(fingerprint)

    def revoke(self, fingerprint: str) -> None:
        self.consent.revoke(fingerprint)

    # ---------- local memory (what this agent is willing to serve at all) ----------

    def add_local_fragment(self, kind: str, content: str) -> MemoryFragment:
        frag = MemoryFragment(kind=kind, content=content, sender_fingerprint=self.fingerprint)
        frag.sign(self.identity)
        self._local_fragments.append(frag)
        return frag

    def _provide_fragments(self, kinds: list[str], since: float, requester_fingerprint: str) -> list[MemoryFragment]:
        # requester_fingerprint is available here for per-peer filtering rules,
        # e.g. a future policy of "only share 'mythic' fragments with this peer" —
        # deliberately not implemented yet; v1 shares everything a peer is
        # consented for, filtered only by kind and timestamp.
        return [
            f for f in self._local_fragments
            if (not kinds or f.kind in kinds) and f.ts >= since
        ]

    # ---------- serving ----------

    def serve(self, host: str = "127.0.0.1", port: int = 0) -> int:
        self._server = StarlineServer(
            self.identity, self.peers, self.consent, self._provide_fragments, host, port
        )
        return self._server.start()

    def stop_serving(self) -> None:
        if self._server:
            self._server.stop()
            self._server = None

    # ---------- requesting ----------

    def request_fragments(
        self, peer: Peer, host: str, port: int, kinds: list[str] | None = None, since: float = 0.0
    ) -> list[MemoryFragment]:
        client = StarlineClient(self.identity)
        return client.request_fragments(peer, host, port, kinds or [], since)
