"""Cryptographic identity — the only thing a Starline peer is.

No accounts, no usernames, no central registry. An identity is a keypair:
  * Ed25519 for signing (proves "this fragment / consent receipt is mine")
  * X25519 for the Noise handshake (proves "this connection is with me")

The private keys never leave the device. Losing the key file means losing
the identity — there is no recovery, by design; a recoverable key would
mean someone else could hold your recovery.
"""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

DEFAULT_IDENTITY_PATH = Path("starline_identity.json")


@dataclass
class Identity:
    """A local Starline identity: one signing keypair, one DH keypair."""

    signing_key: Ed25519PrivateKey
    dh_key: X25519PrivateKey

    @classmethod
    def generate(cls) -> "Identity":
        return cls(Ed25519PrivateKey.generate(), X25519PrivateKey.generate())

    @property
    def sign_public_bytes(self) -> bytes:
        return self.signing_key.public_key().public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )

    @property
    def dh_public_bytes(self) -> bytes:
        return self.dh_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    @property
    def fingerprint(self) -> str:
        """Short, human-shareable identifier — not secret, just a label."""
        return self.sign_public_bytes.hex()[:16]

    def sign(self, data: bytes) -> bytes:
        return self.signing_key.sign(data)

    def save(self, path: Path = DEFAULT_IDENTITY_PATH) -> None:
        """Write the private identity to disk, owner-read-only where the
        platform supports it. This file must never be committed to git —
        see .gitignore."""
        payload = {
            "signing_key": self.signing_key.private_bytes(
                Encoding.Raw, PrivateFormat.Raw, NoEncryption()
            ).hex(),
            "dh_key": self.dh_key.private_bytes(
                Encoding.Raw, PrivateFormat.Raw, NoEncryption()
            ).hex(),
        }
        path.write_text(json.dumps(payload))
        try:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass  # best-effort; not all platforms support POSIX perms

    @classmethod
    def load(cls, path: Path = DEFAULT_IDENTITY_PATH) -> "Identity":
        payload = json.loads(path.read_text())
        return cls(
            Ed25519PrivateKey.from_private_bytes(bytes.fromhex(payload["signing_key"])),
            X25519PrivateKey.from_private_bytes(bytes.fromhex(payload["dh_key"])),
        )

    @classmethod
    def load_or_generate(cls, path: Path = DEFAULT_IDENTITY_PATH) -> "Identity":
        if path.exists():
            return cls.load(path)
        identity = cls.generate()
        identity.save(path)
        return identity


def verify(sign_public_bytes: bytes, data: bytes, signature: bytes) -> bool:
    """Verify a signature against a raw Ed25519 public key. Returns False
    on any failure rather than raising — callers should treat unverified
    exactly like actively-forged, never as a crash."""
    try:
        Ed25519PublicKey.from_public_bytes(sign_public_bytes).verify(signature, data)
        return True
    except Exception:
        return False


def dh_public_from_bytes(raw: bytes) -> X25519PublicKey:
    return X25519PublicKey.from_public_bytes(raw)
