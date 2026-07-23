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

## Status: engine landed (Stage 1, PR 1)

[`core/`](core/) holds **Crystal Core** — the protocol pack (with
Clementine), CrystalBridge, profiles, the mesh stub, and the TypeScript
SDK — imported from the umbrella's canon branch
`claude/crystalcore-boot-visual-jau1bk` @ `32692fd` under the approved
Migration-Plan Stage 1 (engine first). All four self-test suites pass in
this layout (see [`core/README.md`](core/README.md) to run them).
`vision/` (Lumina, the shells, and the site/terminal placement decisions)
arrives via PR 2. Nothing else moves without the maintainer's explicit,
per-stage approval per the umbrella's
[`Migration-Plan.md`](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/governance/Migration-Plan.md).

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
