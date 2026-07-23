# TerAustralis Incognita — Code

Reserved engineering repository for the **TerAustralis Incognita** project
family, per the umbrella repository's boundary charter
([`Project-Boundaries.md`](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/governance/Project-Boundaries.md),
adopted by
[`ADR-0011`](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/adr/ADR-0011.md)
— both land with umbrella PR
[#48](https://github.com/CrystalArchitect/TerAustralis-Incognita/pull/48)).

The name is **TerAustralis** — one 'a', matching the maintainer's
registered trading name
([`ADR-0007`](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/adr/ADR-0007.md));
this README's original one-line heading carried the old double-a drift.

## Status: empty by design

No code lives here yet, deliberately. Code arrives only via an approved
stage of the umbrella's
[`Migration-Plan.md`](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/governance/Migration-Plan.md)
(see its Stage 1) — nothing moves without the maintainer's explicit,
per-stage approval. Until then, the canonical description of the code tree
is the umbrella's
[SystemMap](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/architecture/SystemMap.md#where-the-code-actually-lives).

## What will live here (pending that approval)

- **Crystal Core** — the engine: runtime, protocols, APIs, shared
  libraries (the CrystalCore Framework, the protocol pack with Clementine
  as a named logical component, CrystalBridge, the mesh stub, the SDK).
- **Crystal Vision** — the user-facing application built on Crystal Core,
  with **Lumina**, the flagship sovereign companion, wholly within it.

Whether both live here as two top-level areas or split into separate
repositories is the Migration Plan's Stage 3 decision point. The
dependency rule either way: **Crystal Vision may depend on Crystal Core;
Crystal Core never imports Crystal Vision.**

## What will never live here

Governance, ADRs, architecture canon, and the mythos — those stay in the
umbrella repository,
[`TerAustralis-Incognita`](https://github.com/CrystalArchitect/TerAustralis-Incognita).

*A `LICENSE` file is deliberately deferred to the first code-import stage
(registered in the Migration Plan); until code lands, there is nothing
here to license beyond this notice.*

---

*Non Solus.*
