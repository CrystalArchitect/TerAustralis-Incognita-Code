# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: Apache-2.0

"""Consent & revocation — nothing moves without this saying yes, first.

Every grant is a signed receipt held locally by the human's own agent —
not by a third party, not by the peer. Revocation is honest about its own
limits: it stops FUTURE requests from a peer immediately. It cannot delete
what a peer already legitimately received before revocation — that data
is now theirs, on their own sovereign device, and forcing its deletion
would violate the same sovereignty principle that protects you. Say this
plainly to the human rather than implying a stronger guarantee.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from . import identity as identity_mod

DEFAULT_CONSENT_PATH = Path("starline_consent.json")


@dataclass
class ConsentReceipt:
    peer_fingerprint: str
    granted: bool          # True = granted, False = revoked
    ts: float
    signature: str = ""    # signed by the local identity — proves *we* decided this

    def _signable_bytes(self) -> bytes:
        payload = {"peer_fingerprint": self.peer_fingerprint, "granted": self.granted, "ts": self.ts}
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def sign(self, identity: identity_mod.Identity) -> "ConsentReceipt":
        self.signature = identity.sign(self._signable_bytes()).hex()
        return self


class ConsentEngine:
    """The human-facing gate. Nothing in transport.py or protocol.py may
    send a fragment to a peer without ConsentEngine.is_granted() being
    true for that peer at the moment of sending."""

    def __init__(self, identity: identity_mod.Identity, path: Path = DEFAULT_CONSENT_PATH):
        self.identity = identity
        self.path = path
        self.receipts: list[ConsentReceipt] = []
        if path.exists():
            raw = json.loads(path.read_text())
            self.receipts = [ConsentReceipt(**r) for r in raw]

    def save(self) -> None:
        self.path.write_text(json.dumps([asdict(r) for r in self.receipts], indent=2))

    def grant(self, peer_fingerprint: str) -> ConsentReceipt:
        receipt = ConsentReceipt(peer_fingerprint, granted=True, ts=time.time()).sign(self.identity)
        self.receipts.append(receipt)
        self.save()
        return receipt

    def revoke(self, peer_fingerprint: str) -> ConsentReceipt:
        receipt = ConsentReceipt(peer_fingerprint, granted=False, ts=time.time()).sign(self.identity)
        self.receipts.append(receipt)
        self.save()
        return receipt

    def is_granted(self, peer_fingerprint: str) -> bool:
        """Most recent receipt for this peer wins. No receipt = no consent —
        the default is always closed, never open."""
        relevant = [r for r in self.receipts if r.peer_fingerprint == peer_fingerprint]
        if not relevant:
            return False
        return max(relevant, key=lambda r: r.ts).granted

    def history_for(self, peer_fingerprint: str) -> list[ConsentReceipt]:
        return [r for r in self.receipts if r.peer_fingerprint == peer_fingerprint]
