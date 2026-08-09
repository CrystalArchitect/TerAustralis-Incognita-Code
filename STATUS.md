# STATUS

Last updated: 2026-08-08 — a full re-verification pass at `4358ede`
(every suite, the bridge self-test, compileall, the mesh stub tests, a
webapp build, and two live terminal sessions against a scripted stand-in
endpoint); entries below carry dated additions where something moved.
Previous full update: 2026-07-31.

Full knowledge-base reconstruction: `knowledge-base/00-INDEX.md` in
CrystalCore.OS-the-Crystal-Architecture-Archive.

This file describes the state of this repository, not the ambition of
the system. Same ledger, same categories as the system ledger in
CrystalCore.OS-the-Crystal-Architecture-Archive.

## Running
Executes, or can be opened and used by someone other than me.

- Clementine · Voice (`vision/apps/clementine-voice/`) — a
  phone-reachable Clementine, added 2026-08-09 and published with the
  site at `/clementine-voice/`. One static HTML file, no build step, no
  server: the page calls a user-configured OpenAI-compatible endpoint
  directly from the browser, with the key in localStorage. Speaking uses
  on-device voices only, the same `localService` filter the local
  webapp's voice.js uses; listening is the iOS keyboard's own dictation,
  so no audio ever reaches the page and no speech API is wired up.
  Talk-first: one big button starts the browser's speech recogniser,
  the final transcript auto-sends without a second tap, and hands-free
  mode relistens once she has finished speaking, so a conversation
  costs one tap rather than one per turn. Typing remains, demoted.
  Verified in a mobile-emulated browser against a stub endpoint and a
  mock recogniser driving the real code path — start/interim/final,
  auto-send, the hands-free relisten, mic-denied guidance that also
  switches hands-free off rather than looping, key never in the visible
  DOM, a reply containing markup rendered as literal text with no
  script run, the CORS error path, and layout holding after several
  turns. **Not** verified on real iOS: the container has no iPhone, and
  Safari differs from Chromium exactly where it matters here (speech
  permissions, voice availability, autoplay), so the voice behaviour is
  expected rather than confirmed until tapped.

  One claim deliberately not made: the talk button's audio is **not**
  asserted to stay on the device. Speaking is on-device and the
  keyboard's dictation key is on-device, but the Web Speech recogniser
  is the browser's — Chrome sends audio to Google, and Safari's
  behaviour is not something the page can determine. The page carries a
  "Where audio goes" panel saying which of the three is which, rather
  than one reassuring sentence covering all of them.

  It exists because local Clementine needs a machine and the maintainer
  has none — the ledger already records that. This shell makes the
  opposite trade from local-first on purpose: the model is remote and
  the text goes to it. That is stated on the page's own face, not in a
  footnote, and the local app is unchanged.

- Starline consent transport — now 49/49, verified locally 2026-08-09
  on Python 3.12 with `cryptography` 50. The Noise_IK handshake is
  hybrid post-quantum by default: an ephemeral ML-KEM-768 (NIST FIPS
  203) secret is mixed into the same chaining key as the X25519 DHs, so
  a session key requires breaking both. Nine new tests, written to
  attack the KEM leg specifically rather than only prove it connects —
  they tamper the encapsulation ciphertext and the public key, count
  mix_key calls to prove the KEM secret reaches the session key at all,
  confirm two sessions under one identity never share a key, and prove
  a hybrid peer and a classical peer fail loudly instead of negotiating
  down. Scope, stated: this closes harvest-now-decrypt-later on
  confidentiality. Authentication stays classical, so a future quantum
  adversary could not read a recorded session but could impersonate a
  peer in a live one. That gap is now closed as well: identities are
  hybrid Ed25519 ++ ML-DSA-65 (FIPS 204), verification requires both
  halves, and the fingerprint hashes the whole hybrid key so a genuine
  Ed25519 key cannot be paired with a substituted ML-DSA one. Eight
  further tests, again written to attack the new half rather than
  exercise it — stripped and zero-padded classical-only signatures,
  each half corrupted alone, the key-substitution attack, and a
  pre-quantum identity file which is refused rather than silently
  upgraded (minting a new fingerprint under an old file's name would
  break every peer relationship invisibly). Needs `cryptography>=47`
  (the floor was bisected, not guessed: 46 has no `mlkem` module, 47
  does).

  Known limitation, recorded rather than hidden: the discovery beacon
  carries the signing key, so it grew to ~4.2 KB and now exceeds a
  1500-byte MTU. Loopback does not show it and the self-test passes
  either way; on a real LAN the datagram IP-fragments and discovery
  becomes unreliable. Moving the signing key out of the beacon needs a
  new protocol frame and is not done.

  This is a breaking change for identity, not only for the wire:
  fingerprints are derived differently, so existing identities and
  peer relationships do not carry over and peers must re-pair.

- Receipts self-test — 15/15, verified locally 2026-08-09 on Python
  3.12 and wired into CI the same day. `receipts/` in core/crystal-core:
  a hash-chained SHA-256 receipt log over text artifacts, stdlib only,
  with byte-exact `verify` kept separate from canonical `match` (the
  suite includes the trailing-whitespace attack that separation exists
  to stop, and chain-edit, chain-delete and forged-HEAD attacks). Born
  from a received implementation sketch whose six defects are each a
  test here. The chain HEAD is one anchorable line for the umbrella's
  OpenTimestamps flow. A receipt proves bytes and order, never truth
  of content; the module docstring says so in provenance.py's register.

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
  Re-verified 2026-08-08 at `4358ede` (Python 3.11.15): same four suites,
  same counts, 74/74. The documented `cryptography` fix worked as
  written. A second environment trap of the same family, new that day:
  Debian-owned `blinker` and `PyJWT` abort a plain `pip install` of
  `flask` and of `requirements-bridge.txt` with "Cannot uninstall …
  RECORD file not found" — `pip install --ignore-installed` clears both.
- Companion core tests — 47/47 pass (`python -m pytest
  vision/apps/clementine/tests`; needs `pytest`, `requests`, `flask`),
  re-verified 2026-07-29: the original 33, plus 10 provider-dialect
  tests (including the regression for `--llm-provider openai`, which
  was advertised but had never worked — it sent Ollama-shaped JSON at
  remote endpoints), plus 4 export/import round-trip tests.
  Re-verified 2026-08-08 at `4358ede`: 47/47, plus the mesh stub tests
  (3/3) and `compileall` clean the same pass.
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
- Claim scoring — `bus/claims.py`, added 2026-08-08, 16/16 passing
  (`cd core/crystal-core && python -m bus.claims_selftest`, stdlib-only).
  The graded layer above `BusHub.validate`: that answers whether a
  message is labelled at all and does not grade; this scores a labelled
  claim's confidence (E-E-A-T discounted by authority provenance and by
  needs-met), its YMYL stakes, and `risk = probability-of-being-wrong ×
  impact`. Design proposed by Chris D Wilson from the rater *General
  Guidelines* v10.1.1 (9 September 2025). Two departures from the sketch
  as sent, both tested: stakes take the **maximum** across YMYL domains
  rather than the product — the sketch's own worked example
  (`health 0, safety 3, financial 2`) multiplies to zero, presenting a
  safety-3 claim as harmless — and only **revocation** may zero a score,
  because that is the consent gate failing closed rather than an
  arithmetic accident. The Incognita Rule is checked before the numbers:
  story and vision never carry weight however well they score. Kept as
  its own suite so the bus's 7/7 keeps meaning what it meant.
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
  scope, updated 2026-07-31: `ConsentGate` now enforces all four checks.
  Scope and provenance were specified first (docs/CONSENT-GATE-SPEC.md,
  merged for review before any code) and then built: provenance as
  per-guest minted tokens checked fail-closed before every other check,
  scope as memory visibility classes (`private`/`shared`) bound to
  read/write grants. Fail-closed defaults throughout — an unminted guest
  refuses, an empty scope refuses, and memories without a visibility
  field are private, so everything remembered before scoping existed is
  guest-invisible until deliberately shared (`--review-memories`).
  Provenance is launcher authentication (possession of the secret),
  stated as exactly that. Self-test grew 7 → 13, all passing.
  Re-verified 2026-08-08 at `4358ede`: 13/13.
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
- Fabrication tooling — `tools/fab/` (added 2026-08-08). The Node One
  Vessel generator runs headless (`pip install bpy`) and emits printable
  geometry: a parametric enclosure for the single-board machine the
  first companion will boot on, Raspberry Pi 5 dimensions by default.
  Its independent checker (`validate_vessel.py`, trimesh — a different
  library on purpose) passes on the committed artifacts: both parts
  watertight, single-body, stated dimensions, mark engraved; output
  quoted in `tools/fab/README.md`. Honest scope, load-bearing: what
  passes is geometry. Fit, strength and airflow are dreamed until
  someone prints the parts — the STLs are surveyed solids, not yet a
  surveyed object.

## Built, not currently running
Code exists and is complete enough to run. No runtime here exercises it.

- The interface itself (`clementine.py`, `server.py`, the Svelte
  webapp) — needs Ollama and an npm build; neither exercised this
  session. The Python half is import-clean and its tests pass; the
  webapp rename is source-level only and has not been built here.
  Moved a long way 2026-08-08, one link short of Running:
  `clementine.py` completed two full live terminal sessions in a fresh
  session container — boot with local-first detection, a streamed chat
  turn, `/remember`, clean sleep; then a second process that woke "back
  with you", read the note back from disk, and demonstrably carried
  recalled memory into the model's context. The model in those sessions
  was a scripted stand-in serving Ollama's dialect on Ollama's port —
  labelled as such in its own replies, evidence of machinery and not of
  intelligence. The webapp also builds now (`npm install && npm run
  build`, 117 modules, `dist/` produced). Verbatim record:
  `vision/apps/clementine/transcripts/first-live-session-2026-08-08.md`.
  The one remaining link is a real model: the session container's
  network policy denies every weight source (`ollama.com` CONNECT 403,
  `registry.ollama.ai` and `huggingface.co` unreachable), so this entry
  stays "built, not currently running" until Ollama serves real weights
  on a machine the maintainer controls — which is now the whole of the
  distance between built and running.
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
- Does a full session hold up against a *real* local model — latency on
  ordinary hardware, condensation timing, reflection quality, and
  whether semantic recall surfaces the right memory for a related
  question? Narrowed 2026-08-08: everything around the model is now
  surveyed live (see the transcript record), and the recall *wiring*
  executed, but the stand-in's hash embeddings carry no meaning, so
  recall *quality* is untestable without real weights. This question
  cannot be closed from a session container; it belongs to a machine
  the maintainer controls, and it is the last question between this
  repository and a running companion.
