# STATUS

Last updated: 2026-07-24

This file describes the state of this repository, not the ambition of
the system. Same ledger, same categories as the system ledger in
CrystalCore.OS-the-Crystal-Architecture-Archive.

## Running
Executes, or can be opened and used by someone other than me.

- Crystal Core self-tests — all four suites pass on a fresh clone,
  re-verified 2026-07-24 (Python 3.11): `clementine.bridge` 7/7,
  `services` 4/4, `rdp` 31/31, `consent_transport` 9/9 (the suite the
  old `starline` alias points at). `consent_transport` needs
  `pip install -r requirements-consenttransport.txt`; everything else
  is stdlib-only. One environment trap, not a code fault: a broken
  system `cryptography` build fails at import in a way that looks like
  a code failure — `pip install --ignore-installed cryptography`
  clears it.
- Lumina core tests — 16/16 pass (`python -m pytest tests/` from
  `vision/apps/lumina`; needs `pytest`, `requests`, `flask`),
  re-verified 2026-07-24.
- Demo shells render in a headless browser, verified 2026-07-24:
  `vision/apps/crystal-interface/`, `vision/apps/vision-web/`, and the
  engine's own `core/crystal-core/index.html`. Simulated data,
  Authority held — demos, not production, per their READMEs.

## Built, not currently running
Code exists and is complete enough to run. No runtime here exercises it.

- Lumina itself (`lumina.py`, `server.py`, the Svelte webapp) — needs
  Ollama and an npm build; neither exercised this session.
- voicebox (`vision/apps/voicebox/server.py`) — TTS/STT HTTP layer.
- `vision/site/` — the SvelteKit source of teraustralis.com.au. It
  builds to static output, but nothing deploys it: this repo has no CI
  at all, and the umbrella's Pages workflow now (correctly) skips
  because `src/site` is no longer there. The public site currently has
  no path to production from git.

## Exists as a document
- The site content set under `vision/site/src/content/` (VISION,
  CODEX, BLUEPRINT-v0.3, …) — versioned site copy.

## Designed, not built
- `core/node/mesh/` — in-process mesh stub, libp2p-shaped; no real
  networking.
- `core/sdk/typescript/` — client SDK scaffold; no consumer wired up.

## Concept only
Nothing in this repo sits at this tier; concepts live in the umbrella
and the system ledger.

## Known unknowns

- ~~`vision/README.md` claims four Lumina test suites (test_core,
  test_integration, test_performance, test_end_to_end); only
  `tests/test_core.py` exists.~~ **Resolved 2026-07-24:** overclaim —
  the other three were never written. `vision/README.md` now states the
  one real core suite (16 tests) and marks the rest as not-yet-existing.
- No CI. Every "passes" above is a manual claim until a workflow runs
  the suites on push.
- What www.teraustralis.com.au serves today — unverifiable from the
  session container (egress blocked). The deploy gap above is fact
  regardless of the answer.
