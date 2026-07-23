# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""The peer store — every agent Starline has ever been introduced to.

Not secret in the cryptographic sense (public keys are, by definition,
public) but private in the social sense: this file is your address book.
It stays local, is gitignored, and is never synced anywhere by Starline
itself.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_PEERS_PATH = Path("starline_peers.json")


@dataclass
class Peer:
    fingerprint: str          # Ed25519 public key, hex, truncated — display id
    sign_public_hex: str      # full Ed25519 public key, hex
    dh_public_hex: str        # full X25519 public key, hex
    label: str = ""           # human-given name, e.g. "Sam's Lumina"
    consented: bool = False   # has the human approved fragment exchange with this peer?


class PeerStore:
    """Load/save/query the local peer list. Adding a peer here is the
    'pairing' step — it does NOT grant consent by itself; consent.py
    handles that separately and explicitly."""

    def __init__(self, path: Path = DEFAULT_PEERS_PATH):
        self.path = path
        self.peers: dict[str, Peer] = {}
        if path.exists():
            raw = json.loads(path.read_text())
            self.peers = {fp: Peer(**p) for fp, p in raw.items()}

    def save(self) -> None:
        self.path.write_text(json.dumps({fp: asdict(p) for fp, p in self.peers.items()}, indent=2))

    def add(self, sign_public_hex: str, dh_public_hex: str, label: str = "") -> Peer:
        fingerprint = sign_public_hex[:16]
        peer = self.peers.get(fingerprint)
        if peer is None:
            peer = Peer(fingerprint, sign_public_hex, dh_public_hex, label)
            self.peers[fingerprint] = peer
        else:
            peer.label = label or peer.label
        self.save()
        return peer

    def get(self, fingerprint: str) -> Peer | None:
        return self.peers.get(fingerprint)

    def is_known(self, fingerprint: str) -> bool:
        return fingerprint in self.peers

    def find_by_dh(self, dh_public_hex: str) -> Peer | None:
        """Look up a peer by the X25519 key seen in a Noise handshake —
        that's the only identity a responder has until it maps it back
        to a paired peer record."""
        for peer in self.peers.values():
            if peer.dh_public_hex == dh_public_hex:
                return peer
        return None

    def list(self) -> list[Peer]:
        return list(self.peers.values())
