"""Candidate B — content-addressed hierarchical retrieval (development defaults).

Independent of Candidate A. Does not import A or A's results.
"""

from __future__ import annotations

import numpy as np

from benchmarks.bandwidth import Bandwidth
from benchmarks.config import CANDIDATE_B_DEV
from benchmarks.model import AttentionPrimitive, sdp_attention, split_heads


class ContentAddressedRetrieval(AttentionPrimitive):
    name = "candidate_b_car"
    independent = True

    def __init__(self, cfg: dict | None = None):
        self.cfg = dict(CANDIDATE_B_DEV if cfg is None else cfg)

    def select_and_attend(
        self,
        q: np.ndarray,
        k: np.ndarray,
        v: np.ndarray,
        query_positions: np.ndarray,
        bw: Bandwidth,
        layer: int,
    ) -> np.ndarray:
        leaf = int(self.cfg["leaf_block"])
        group = int(self.cfg["group_size"])
        n_ret = int(self.cfg["retrieved_blocks"])
        t = k.shape[0]
        n_leaves = (t + leaf - 1) // leaf
        n_groups = (n_leaves + group - 1) // group

        q_bar = q.mean(axis=0)
        token_scores = k @ q_bar
        bw.add("routing", token_scores.size)

        leaf_scores = np.empty(n_leaves, dtype=np.float32)
        for b in range(n_leaves):
            sl = token_scores[b * leaf : min(t, (b + 1) * leaf)]
            leaf_scores[b] = float(sl.max())
        bw.add("index", leaf_scores.size)

        group_scores = np.empty(n_groups, dtype=np.float32)
        for g in range(n_groups):
            sl = leaf_scores[g * group : min(n_leaves, (g + 1) * group)]
            group_scores[g] = float(sl.max())
        bw.add("index", group_scores.size)
        bw.add("routing", group_scores.size)

        g_k = min(max(1, (n_ret + group - 1) // group), n_groups)
        top_g = np.argpartition(group_scores, -g_k)[-g_k:]
        cand = []
        for g in top_g:
            cand.extend(range(int(g) * group, min(n_leaves, (int(g) + 1) * group)))
        cand = np.asarray(sorted(set(int(x) for x in cand)), dtype=np.int32)
        l_scores = leaf_scores[cand]
        take = min(n_ret, cand.size)
        top_l = cand[np.argpartition(l_scores, -take)[-take:]]
        bw.add("routing", l_scores.size)

        idx = []
        for b in sorted(int(x) for x in top_l):
            idx.extend(range(b * leaf, min(t, (b + 1) * leaf)))
        idx = np.asarray(idx, dtype=np.int32)
        ks = k[idx]
        vs = v[idx]
        bw.add("kv", ks.size + vs.size)
        return sdp_attention(split_heads(q), split_heads(ks), split_heads(vs), bw)
