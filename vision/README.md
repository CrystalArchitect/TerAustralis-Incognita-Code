# Crystal Vision — the user-facing application

Per the boundary charter
([`Project-Boundaries.md`](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/governance/Project-Boundaries.md),
[`ADR-0011`](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/adr/ADR-0011.md)),
this area holds Crystal Vision: user-facing applications, interfaces, and the companion. Crystal Vision may depend on Crystal Core; Crystal Core never imports Crystal Vision.

| Path | Component |
|---|---|
| `apps/lumina/` | **Lumina** — sovereign AI companion, Ollama-backed (local-first, memory-aware, configurable LLM provider) · terminal, Flask API, Svelte webapp, browser voice · embedded CrystalCore Framework · test suites (core, integration, performance, end-to-end) |
| `apps/voicebox/` | Voice layer HTTP server (TTS/STT interfaces) |
| `apps/crystal-interface/` | **Demo shell** — simulated data, Authority held (not production) |
| `apps/vision-web/` | **Demo shell** — simulated data, Authority held (not production) |
| `site/` | teraustralis.com.au — SvelteKit public frontend (prerendered, static hosting) |

## Prove it

```bash
# From the vision/apps/lumina directory (tests embedded)
cd vision/apps/lumina
python -m pytest tests/
```

All four embedded test suites pass in this layout (test_core, test_integration, test_performance, test_end_to_end).

## The dependency rule

**Crystal Vision may depend on Crystal Core; Crystal Core never imports Crystal Vision.** Vision apps that need Core features import them explicitly (e.g., Lumina imports its own embedded Framework). Core services reach Vision data *by configured data path at runtime* — the bridge serves the companion without importing it.

---

Imported from the umbrella repository's branch
`claude/crystalcore-boot-visual-jau1bk` @ `32692fd` (Migration-Plan
Stage 1, PR 2 — user-facing app). Directory names preserved; `src/apps/` became `apps/` and `src/site/` became `site/`.
