# TerAustralis Incognita — Code

The code companion to [TeraAustralis-Incognita](https://github.com/CrystalArchitect/TeraAustralis-Incognita),
which holds the project's documentation, ADRs, governance, licensing policy,
mythos content, and archives. This repository holds the runnable code: the
CrystalBridge MCP server, the Crystal Core application line, the v1.0 runtime,
the consent transport, the apps, the site source, and the distributable
`teraaustralis.*` packages.

Imported wholesale from `teraustralis-incognita-code.tar.gz` on 2026-07-23.
An earlier, diverged line of this code — the 2026-07-17 local-machine
snapshot — remains preserved in the main repository under
`archive/2026/local-snapshot-2026-07-17/`.

## Layout

| Path | What it is |
|---|---|
| `src/crystalcore/` | **CrystalBridge** — a fail-closed MCP server that lets a guest AI (Claude, Grok, Cursor, …) meet Lumina with only the access you've explicitly granted. The packaged project (`pyproject.toml`, entry point `crystalbridge`). Partially reconstructed — see its README's provenance note. |
| `src/crystal-core/` | Consolidated application line: Clementine (terminal companion + bridge), CLI, `consent_transport` (peer-to-peer transport, formerly "Starline"), interface, RDP (append-only record), services — each with self-tests. |
| `src/runtime/` | v1.0 runtime — coordinator, config, API, event bus, registry, logging, plugins. |
| `src/node/mesh/` | libp2p-shaped in-process mesh transport stub (Phase 1; gossipsub/noise/yamux planned). |
| `src/crystalcore-os/` | ML and emotional-intelligence experiments (training pipeline, multimodal emotion, uncertainty quantification). |
| `src/apps/` | Applications: `lumina` (core + webapp + tests), `crystal-interface`, `vision-web`, `voicebox`. |
| `src/site/` | Svelte/Vite source for teraustralis.com.au, including the art assets. |
| `src/sdk/typescript/` | TypeScript SDK. |
| `src/profiles/` | Default profiles (e.g. `bridge_config.json`). |
| `packages/` | Distributable `teraaustralis.*` namespace packages: consent-transport, crystalbridge, crystalcore-ei, lumina, mythos, rdp, starline. |
| `tests/` | Repo-level suite: runtime (e2e, integration, contract, coordinator, registry) and the mesh stub. |
| `scripts/maintenance/check.sh` | The full local check battery (compileall + every self-test + test suites). |

## Getting started

Python ≥ 3.11.

```bash
pip install -r requirements-bridge.txt   # mcp + pytest
python3 -m pytest                        # repo-level suites (runtime + mesh)
bash scripts/maintenance/check.sh        # full battery
```

Verified at import time (2026-07-23): 78 repo-level tests, 16 Lumina tests,
and the Clementine-bridge (7/7), services (4/4), RDP (31/31), and
consent-transport (9/9) self-tests all pass. One known wrinkle: `check.sh`
invokes the consent-transport suite through the deprecated `starline` alias,
which the `-m` runner rejects on newer Pythons — run
`python3 -m consent_transport.selftest` from `src/crystal-core/` directly.

To work on CrystalBridge itself:

```bash
pip install -e ".[dev]"
crystalbridge --help        # or: python3 -m crystalcore
```

## License

All code and specifications are licensed **CC BY-NC-ND 4.0** — see
[`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). In short: attribution required,
non-commercial use only, no derivative redistribution; commercial use
requires explicit permission from the copyright holder
(Crystal Arena-Turner, TerAustralis Incognita). This is the project's uniform
license per ADR-0010 in the main repository, where the full licensing policy
(`LICENSING.md`) lives. Third-party acknowledgments are in
[`docs/ATTRIBUTIONS.md`](docs/ATTRIBUTIONS.md).
