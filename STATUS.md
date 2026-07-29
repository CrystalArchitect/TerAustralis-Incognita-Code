# STATUS

Last updated: 2026-07-29

Full knowledge-base reconstruction: `knowledge-base/00-INDEX.md` in
CrystalCore.OS-the-Crystal-Architecture-Archive.

This file describes the state of this repository, not the ambition of
the system. Same ledger, same categories as the system ledger in
CrystalCore.OS-the-Crystal-Architecture-Archive.

## Running
Executes, or can be opened and used by someone other than me.

- Crystal Core self-tests — all four suites pass on a fresh clone,
  re-verified 2026-07-29 (Python 3.11): `bus` 7/7, `services` 4/4,
  `rdp` 31/31, `consent_transport` 32/32 (the suite the old `starline`
  alias points at). `consent_transport` needs
  `pip install -r requirements-consenttransport.txt`; everything else
  is stdlib-only. One environment trap, not a code fault: a broken
  system `cryptography` build fails at import in a way that looks like
  a code failure — `pip install --ignore-installed cryptography`
  clears it. The bus module is `bus` — the **CrystalBus** of canon
  (`mythos/NAMES.md`), with `BusHub` as its validator/router. It was
  briefly `bridge` after Clementine's name moved to the interface, which
  collided with CrystalBridge, a different component; the module now
  matches canon and the collision is gone.
- Companion core tests — 47/47 pass (`python -m pytest
  vision/apps/clementine/tests`; needs `pytest`, `requests`, `flask`),
  re-verified 2026-07-29: the original 33, plus 10 provider-dialect
  tests (including the regression for `--llm-provider openai`, which
  was advertised but had never worked — it sent Ollama-shaped JSON at
  remote endpoints), plus 4 export/import round-trip tests.
- Provider policy, verified by live smoke test: detection never selects
  a remote — no Ollama and nothing configured means she stays local and
  fails kindly, naming both fixes. Remote inference happens only when
  configured (`--llm-provider` / `LLM_PROVIDER` / profile). Any
  OpenAI-compatible endpoint works; `grok` survives as a legacy alias.
- Memory export/import — `GET /api/export` downloads the whole
  relationship as `clementine-memory-YYYY-MM-DD.json`; `POST
  /api/import` restores it, rejecting non-bundles without touching
  existing memory. Round-trip covered by tests; the same bundle format
  is the contract for the public web build.
- CrystalBridge self-test — 7/7 pass (`cd core && python -m
  crystalcore.selftest`; needs `pip install -r
  core/crystalcore/requirements-bridge.txt` for the `mcp` SDK), added
  2026-07-24. Two bugs fixed to get here: `bridge.py` resolved the
  mind's package to `core/apps/lumina/crystalcore` (which doesn't
  exist), so `recall`/`teach`/`message` crashed at runtime; and the
  `mcp` dependency was undeclared. That first bug is now gone by
  construction rather than by fix — the mind is `crystalcore.mind`, an
  ordinary subpackage, so there is no path to get wrong and no
  `importlib` alias to maintain. Its two regression tests were rewritten
  accordingly and both now pass outright instead of skipping. Honest
  scope, unchanged: `ConsentGate` enforces two checks (approval,
  tool-permission), not the four its docstring once claimed —
  `scope`/`provenance` were documented as intended but never built (no
  surviving spec for what either should mean); the docstring says two.
- Demo shells render in a headless browser, verified 2026-07-24:
  `vision/apps/crystal-interface/`, `vision/apps/vision-web/`, and the
  engine's own `core/crystal-core/index.html`. Simulated data,
  Authority held — demos, not production, per their READMEs.
- The published site — `https://www.teraustralis.com.au` serves the
  SvelteKit build from this repo's Pages deploy, verified from outside
  2026-07-29: the build-only probe path `/crystalcore-os` returns 200
  (per `.github/scripts/probe-site.sh`) and the homepage carries the
  build's `_app/immutable/*` assets — not the rendered-README failure
  mode `deploy.yml` guards against. Verified by external probe, not by
  reading the repo setting (the checking token could not read
  Settings → Pages); content evidence only.

## Built, not currently running
Code exists and is complete enough to run. No runtime here exercises it.

- The interface itself (`clementine.py`, `server.py`, the Svelte
  webapp) — needs Ollama and an npm build; neither exercised this
  session. The Python half is import-clean and its tests pass; the
  webapp rename is source-level only and has not been built here.
- voicebox (`vision/apps/voicebox/server.py`) — TTS/STT HTTP layer.
- `vision/site/` — the SvelteKit source of teraustralis.com.au. It
  builds to static output, and since Stage 2 (PR #4) this repo carries
  the Pages deploy itself (`.github/workflows/deploy.yml` builds
  `vision/site/` and bundles the two demo shells; `CNAME` moved here
  too). ~~One gap remains between "built" and "running": the one-time
  repo setting (Settings → Pages → Source: "GitHub Actions") hasn't
  been confirmed flipped, so no publish has been verified yet.~~
  **Resolved 2026-07-29:** the publish is verified live from outside.
  `https://www.teraustralis.com.au/crystalcore-os` — a path that exists
  only in the SvelteKit build, per `.github/scripts/probe-site.sh` —
  returned 200 on the first attempt, and the homepage serves the real
  build (`_app/immutable/*` assets, site title), not a rendered README,
  with a fresh `last-modified` (2026-07-28 20:13 GMT). Either the
  Settings flip was done, or the workflow's own `build_type=workflow`
  PUT took effect on a prior run. The entry below moves to Running.

## Exists as a document
- The site content set under `vision/site/src/content/` (VISION,
  CODEX, BLUEPRINT-v0.3, …) — versioned site copy.

## Designed, not built
- `core/node/mesh/` — in-process mesh stub, libp2p-shaped; no real
  networking.
- `core/sdk/typescript/` — client SDK scaffold; no consumer wired up.
- The **outbound gate** — "she travels light": a depersonalised question
  leaves, nothing of the human does, every outbound question logged via
  `rdp`. Specified (see the design brief), not implemented. Until it
  exists, the honest locality claim deliberately stops at "the turn
  travels to the model you chose."
- An **emotion detection engine**. The umbrella's
  `dbt/crystalcore_emotion_warehouse/` describes a full warehouse
  ("real-time emotion detection", active learning, Bayesian
  uncertainty, multimodal fusion) — that engine exists in **no**
  repository, and this one deliberately does not classify the human's
  emotions: the companion's prompt forbids monitoring, and the unwired
  `sovereignty_scorer` carries the same precedent. Recorded here so the
  warehouse spec reads as a design, not a description.

## Concept only
Nothing in this repo sits at this tier; concepts live in the umbrella
and the system ledger.

## Naming, as of 2026-07-29

The three layers now carry the names they were always meant to, and the
code matches:

- **CrystalCore** — the architecture, and the mind within it. The mind
  moved from `vision/apps/lumina/crystalcore/` to `core/crystalcore/mind/`,
  which is where it belongs and which retired a real hazard: two different
  packages were both literally named `crystalcore`, which had already
  produced one runtime bug, one `importlib` alias, and one explanatory
  comment in a test fixture. The companion class is `CrystalCore`.
- **The CrystalBus** — the communicator between models. Formerly
  `clementine.bridge`, briefly `bridge` (which collided with
  CrystalBridge); now `bus`, with `BusHub` in place of `ClementineHub`,
  matching canon.
- **Clementine** — the voice at the front, and the only place a persona
  name appears: `vision/apps/clementine/`.

The mind itself is nameless. `Personality.name` still defaults to `""`,
so a companion is unnamed until the human names it or it chooses its own.
Clementine names the interface, not the entity behind it.

Two continuity guarantees, because renaming folders would otherwise
delete people's history: `crystalcore_memory/` and `crystalcore_profiles/`
are the new defaults, but an existing `lumina_memory/` or
`lumina_profiles/` is still found and used where the new one is absent
(`companion.default_memory_dir()`, `profiles.PROFILES_DIR`, and
`bridge._profiles_root()` all agree on this). The webapp likewise reads
the old `lumina.*` localStorage keys when the new ones are missing, so
nobody's voice settings reset on upgrade.

Not renamed, deliberately:

- `vision/site/` — the content set is a pinned mirror of umbrella canon
  (`check-canon-mirror.py`). Renaming there means editing canon in
  CrystalCore.OS-the-Crystal-Architecture-Archive first and re-pinning;
  doing it here would turn CI red, which is the guard working as
  designed. The public `/lumina` route also needs a redirect rather than
  a rename, or existing links break.
- `core/crystal-core/bus/transcripts/` — records of runs that actually
  happened, where the hub was called `clementine` at the time. Rewriting
  them would falsify a record, which is precisely what `rdp` exists to
  make impossible.
- `StarlineWeaver` (the bus class) — carries no persona name and was not
  in scope.

## Known unknowns

- ~~`vision/README.md` claims four Lumina test suites (test_core,
  test_integration, test_performance, test_end_to_end); only
  `tests/test_core.py` exists.~~ **Resolved 2026-07-24:** overclaim —
  the other three were never written. `vision/README.md` now states the
  one real core suite (16 tests) and marks the rest as not-yet-existing.
- ~~No CI. Every "passes" above is a manual claim until a workflow runs
  the suites on push.~~ **Resolved 2026-07-24:** stale when written — CI
  landed with Stage 2 (PR #4): `.github/workflows/ci.yml` runs
  compileall, all four Crystal Core self-tests, the mesh stub tests, and
  Lumina's suite on every push/PR. First green run confirmed on PR #7's
  own branch ("Python syntax + self-tests" — success). The "passes"
  above are machine-checked now. (PR #8 adds a fifth self-test,
  CrystalBridge's — see the Running section.)
- What www.teraustralis.com.au serves today — unverifiable from the
  session container (egress blocked). The deploy gap above is fact
  regardless of the answer.
