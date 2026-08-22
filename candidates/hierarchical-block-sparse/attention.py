"""Candidate A — hierarchical block-sparse attention (development defaults)."""

from __future__ import annotations

import numpy as np

from benchmarks.bandwidth import Bandwidth
from benchmarks.config import CANDIDATE_A_DEV
from benchmarks.model import AttentionPrimitive, sdp_attention, split_heads


class HierarchicalBlockSparse(AttentionPrimitive):
    name = "candidate_a_hbs"
    independent = True

    def __init__(self, cfg: dict | None = None):
        self.cfg = dict(CANDIDATE_A_DEV if cfg is None else cfg)

    def select_and_attend(
        self,
        q: np.ndarray,
        k: np.ndarray,
        v: np.ndarray,
        query_positions: np.ndarray,
        bw: Bandwidth,
        layer: int,
    ) -> np.ndarray:
        block = int(self.cfg["block_size"])
        local_w = int(self.cfg["local_window"])
        n_sel = int(self.cfg["cross_block_selections"])
        t = k.shape[0]
        n_blocks = (t + block - 1) // block

        q_bar = q.mean(axis=0)
        token_scores = k @ q_bar
        bw.add("routing", token_scores.size)
        bw.add("index", n_blocks)

        block_scores = np.empty(n_blocks, dtype=np.float32)
        for b in range(n_blocks):
            sl = token_scores[b * block : min(t, (b + 1) * block)]
            block_scores[b] = float(sl.max())
        bw.add("routing", block_scores.size)

        q_block = int(query_positions[-1]) // block
        local = {min(n_blocks - 1, max(0, q_block + off)) for off in range(-local_w, 1)}
        k_take = min(n_sel, n_blocks)
        top = np.argpartition(block_scores, -k_take)[-k_take:]
        selected = sorted(set(int(x) for x in top) | local)
        bw.add("routing", len(selected))

        idx = []
        for b in selected:
            idx.extend(range(b * block, min(t, (b + 1) * block)))
        idx = np.asarray(idx, dtype=np.int32)
        ks = k[idx]
        vs = v[idx]
        bw.add("kv", ks.size + vs.size)
        return sdp_attention(split_heads(q), split_heads(ks), split_heads(vs), bw)
