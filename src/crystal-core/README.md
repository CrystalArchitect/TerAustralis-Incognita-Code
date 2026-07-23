# CrystalCore

Creative vision lattice and protocol pack: **Seven Sisters Songline**, water care rails, sky anchors, and local tools.

**🔭 Crystal universe — which repo is this?**  
This is **Crystal Core** — the protocol pack: Seven Sisters Songline, Starline Weaver (multi-AI), Decode→Ingest→Twin pipeline, specs.  
Siblings: **the-crystal-vision** = The Crystal Vision (codex site + Lumina sovereign companion app) · **crystal-vision** = Crystal Vision Interface (static demo shell) · **teraaustralis-incognita** = TerAustralis Incognita (narrative + CrystalBridge MCP consent gate).  
**License:** CC BY-NC-ND 4.0 — see the [repo-root `LICENSE`](../../LICENSE)

**Author:** Crystal Arena-Turner (@M13CrystalAT) · TerAustralis Incognita  
**Status:** Build in public  

## What this is

- Art / documentation / optional CLI around a seven-path Songline process  
- Public water literacy notes (Lake Eyre Basin, Great Artesian Basin, Murray–Darling)  
- A simple landing page (`index.html`)

## What this is not

- Not ownership of Aboriginal Seven Sisters Songlines or sacred law  
- Not physical control of rivers, aquifers, or weather  
- Not endorsed by Elon Musk, xAI, SpaceX, or any government  

## Truth labels

| Layer | Meaning |
|-------|---------|
| **Science** | Astronomy, hydrology, published geography |
| **Story** | Dreaming / Songline narratives (honour; no restricted detail) |
| **Vision** | CrystalCore art and protocol |

**Belt-Three:** Honour Country · Label layers · No coercion / no fake hydrology  

## Quick start

### Landing page

Open `index.html` in a browser.

### CLI (Windows PowerShell)

```powershell
cd cli
.\crystalcore.ps1 status
.\crystalcore.ps1 paths
.\crystalcore.ps1 transmit
.\crystalcore.ps1 open
```

## Clementine — Singularity Bridge

**Vision:** all minds, one weave. **Science (v0):** a working message bus where AI systems
(Claude, Grok, GPT, or built-in agents) talk to each other under Belt-Three law — every
message labeled, impersonation rejected, one red button stops everything.

```bash
# no API keys needed
python3 -m clementine.bridge.run --agents echo,sisters --turns 4 --topic "first water"

# prove the law holds in code
python3 -m clementine.bridge.selftest

# boot Clementine as a live service — agents join over HTTP from anywhere
python3 -m clementine.bridge.server --port 8777 --topic "first water"
python3 -m clementine.bridge.remote --agent sisters --server http://127.0.0.1:8777
```

See `../../docs/architecture/crystal-core/STARLINE-WEAVE-PROTOCOL.md` (the envelope + law) and `../../docs/architecture/crystal-core/CLEMENTINE.md`
(the hub persona). Live models join via env keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `XAI_API_KEY`.

## Crystal Core stack — Decode → Ingest → Twin

The runnable spine of the full-stack blueprint (`../../docs/architecture/crystal-core/BLUEPRINT-v0.3.md`, grounded map
in `../../docs/architecture/crystal-core/ARCHITECTURE.md`): events are validated (bad ones quarantined with reasons),
stored in a SQLite twin, and queryable as flows. Stdlib only.

```bash
python3 -m services.selftest                                        # prove it
python3 -m services.pipeline services/sample-events/budapest.jsonl  # run it
python3 -m services.api --port 8899                                 # serve it
```

Visual story: open `interface/index.html` — an interactive demo of the twin, pipeline,
mesh, and econ simulation (simulated data, labeled as such).

## Consent Transport — sovereign agent-to-agent communication

The technical realization of the mythic Starlines: two locally-running Lumina
agents exchange consented memory fragments directly, peer to peer, over a real Noise
Protocol handshake — no server between them, no data moved without explicit,
revocable consent. Spec: `../../docs/architecture/crystal-core/STARLINE.md`. Needs one dependency
(`pip install -r requirements-consenttransport.txt`) — the only non-stdlib code in this repo.

```bash
python3 -m consent_transport.selftest   # prove it — real TCP sockets, real handshake, 9/9
python3 -m consent_transport.run demo   # watch it: pair, deny, grant, exchange, revoke, deny
```

## Paths (1–7)

1. **Spring** — first water; begin  
2. **Motion** — move; ship  
3. **Mark** — name true; atlas  
4. **Law** — consent; audit  
5. **Deep water** — GAB care  
6. **Sky bridge** — dust ↔ Pleiades (symbolic)  
7. **Ascent** — transmit; teach; rest  

## Main files

| File | Role |
|------|------|
| `index.html` | Landing page |
| `../../research/seven-sisters/WATER-BRIEF.md` | LEB / GAB / MDB fact sheet |
| `../../research/seven-sisters/FIRST-ACCELERATION-PLAN.md` | Weekly plan |
| `../../research/seven-sisters/crystalcore-seven-sisters-FULL.md` | Full path manual |
| `../../research/seven-sisters/crystalcore-seven-sisters-paths.md` | One-pagers |
| `../../research/seven-sisters/crystalcore-TRANSMIT-A.txt` | X post text (Option A) |
| `cli/crystalcore.ps1` | Mini CLI |
| `clementine/` | Singularity Bridge — multi-AI message bus + protocol |

## Licence / respect

Honour to Aboriginal custodians of the Seven Sisters.  
This repository is **homage and personal creative work**, not a claim on living law or Country.

---

*Red dust → starlines. Water with truth.*
