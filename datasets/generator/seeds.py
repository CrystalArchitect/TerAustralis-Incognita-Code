"""Pre-registered seed families. Final family stays untouched."""

from __future__ import annotations

import hashlib

from benchmarks.config import DEV_CORPUS_SEED, FINAL_CORPUS_SEED, VAL_CORPUS_SEED

PARTITION_SEEDS = {
    "development": DEV_CORPUS_SEED,
    "validation": VAL_CORPUS_SEED,
    "final": FINAL_CORPUS_SEED,
}


def u32(*parts: object) -> int:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
        h.update(b"|")
    return int.from_bytes(h.digest()[:4], "big")


def item_seed(partition: str, length: int, index: int) -> int:
    if partition == "final":
        raise RuntimeError("final seed family is locked until the immutable final test")
    base = PARTITION_SEEDS[partition]
    return u32(base, length, index, partition)
