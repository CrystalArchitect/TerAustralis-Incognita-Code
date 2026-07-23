# Crystal Interface — the operator shell

The operator-facing **demo shell** for Crystal Vision / Core / Starline Budapest.
A single static copy — open it locally or serve it as static files (no build
step). The citizen-facing surface is the separate, slimmer
[`../vision-web`](../vision-web).

**🔭 Crystal universe — which repo is this?**  
Siblings: **crystalcore** = Crystal Core (protocol pack) · **the-crystal-vision** = The Crystal Vision (codex site + Lumina sovereign companion app) · **teraaustralis-incognita** = TerAustralis Incognita (narrative + CrystalBridge).  
**License:** CC BY-NC-ND 4.0 — see the [repo-root `LICENSE`](../../../LICENSE)

**Not production.** Every number is illustrative and **simulated in the browser**;
this shell makes **no backend calls**. Authority **HOLD**.

## Open

```bash
cd src/apps/crystal-interface
# any static server, or:
python -m http.server 8090
# → http://127.0.0.1:8090
```

Or open `index.html` directly in a browser.

## Panels

| Panel | Content |
|-------|---------|
| Home | Product map + stats |
| Twin | Layered canvas (water / energy / data / mobility) |
| Mesh | Sovereign nodes SVG |
| Pipeline | DECODE→…→UPGRADE interactive steps |
| Economics | Burn rate R, α, wallet demo |
| Starline | Corridor cards VIE/BTS/BER |
| Wallet | Citizen journey |
| Event log | Client-side activity |

## The real pipeline (separate — not wired to this shell)

This shell is static and simulated; it does not call a backend. The actual data
pipeline is a real, tested package in the monorepo and runs independently:

```bash
cd ../../crystal-core
python -m services.selftest      # the real ingest → decode → twin pipeline, with tests
```
