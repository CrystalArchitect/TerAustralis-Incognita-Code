# H2 Extreme-Context Primitive — Experimental Branch

**Status:** Validation recorded · configs not frozen · no performance claims  
**Methodology:** Fully frozen  
**Performance claims:** Prohibited until final test

This branch is isolated experimental work only. It must not modify production CrystalCore architecture.

Locked methodology:

* [`docs/H2/SPEC-V0.1.md`](docs/H2/SPEC-V0.1.md)
* [`docs/H2/DATASET-PROTOCOL-V0.1.md`](docs/H2/DATASET-PROTOCOL-V0.1.md)
* [`docs/H2/GOVERNANCE.md`](docs/H2/GOVERNANCE.md)

Execution:

1. 32k/64k reference-fidelity — recorded under [`results/reference-fidelity-32k-64k/`](results/reference-fidelity-32k-64k/)
2. Development sweep — recorded under [`results/dev-sweep-v0.1/`](results/dev-sweep-v0.1/). **Not a configuration freeze.**
3. Validation — recorded under [`results/validation-v0.1/`](results/validation-v0.1/). **Not a configuration freeze.** Not a 1M dual-gate decision.

---

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
| [`docs/H2/`](docs/H2/) | H2 extreme-context primitive — locked V0.1 methodology (this branch only) |

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
