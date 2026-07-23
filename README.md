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

## Status: engine + vision landed, CI and Pages live here (Stage 2)

[`core/`](core/) holds **Crystal Core** — the protocol pack (with
Clementine), CrystalBridge, profiles, the mesh stub, and the TypeScript
SDK. [`vision/`](vision/) holds **Crystal Vision** — Lumina, voicebox, the
demo shells, and the public site. Both imported from the umbrella's canon
branch `claude/crystalcore-boot-visual-jau1bk` @ `32692fd` under the
approved Migration-Plan Stage 1 (PR 1 engine, PR 3 vision).

CI (`.github/workflows/ci.yml`) runs compileall, all four Crystal Core
self-tests, the mesh stub tests, and Lumina's test suite on every push —
mirroring the umbrella's old checks against these real paths, per
Migration-Plan Stage 2. The public site's Pages deploy
(`.github/workflows/deploy.yml`) and custom domain (`CNAME`) also moved
here, since `vision/site/` is where the site's source now lives — Pages
must live where the site lives. *(One-time manual step outstanding: a
repo admin needs to set Pages' source to "GitHub Actions" in this repo's
Settings → Pages; no API access from this session to do it directly.)*

Nothing else moves without the maintainer's explicit, per-stage approval
per the umbrella's
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
