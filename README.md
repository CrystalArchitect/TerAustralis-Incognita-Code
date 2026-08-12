# TerAustralis Incognita — Code

Engineering repository for **TerAustralis Incognita**. Canon, ADRs, and
mythos live in
[`TerAustralis-Incognita`](https://github.com/CrystalArchitect/TerAustralis-Incognita).
The name is **TerAustralis** — one *a* ([ADR-0007](https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/docs/adr/ADR-0007.md)).

**Crystal Vision may depend on Crystal Core; Crystal Core never imports Crystal Vision.**

## What is here (surveyed, 2026-08-12)

| Path | What it is |
|---|---|
| [`core/crystalcore/`](core/crystalcore/) | CrystalBridge + five-door `ConsentGate` (guest / stdio) |
| [`core/crystal-core/consent_transport/`](core/crystal-core/consent_transport/) | Starline P2P: Noise IK + ML-KEM-768, hybrid identity, tokens |
| [`core/crystal-core/`](core/crystal-core/) | Bus, RDP, receipts, services |
| [`vision/`](vision/) | Public site source, demo shells, voice page |
| [`docs/CONSENT-GATE-SPEC.md`](docs/CONSENT-GATE-SPEC.md) | Gate spec — **implemented**, not a draft |

The flagship companion that actually gates model calls is
[`Clementine-ai-companion`](https://github.com/CrystalArchitect/Clementine-ai-companion).
`vision/apps/clementine/` here is a pointer, not that runtime.

`LICENSE` is in the tree (CC-BY-NC-ND-4.0 on these modules). Pages deploy
lives here (`vision/site/` + `.github/workflows/deploy.yml`).

## Self-tests (this tip)

```
cd core && python3 -m crystalcore.selftest
cd core/crystal-core && PYTHONPATH=. python3 -m consent_transport.selftest
```

Counts move; `STATUS.md` is the ledger. Do not trust a number in a PR
body over a run against `main`.

## Two consent surfaces

- **Guest gate** — record `pending.jsonl` *before* evaluate; a failed
  write **refuses**.
- **Starline** — evaluate, then ask-log, then reply; a failed *ask-log*
  write still replies (policy lock). Failed *token spend* write **denies**.

Connection lifetime budget is 10s monotonic (`CONNECTION_BUDGET`).
Default bind is `127.0.0.1`.

---

*Non Solus.*
