# H2 experiments

Methodology is locked at V0.1. This directory runs the execution sequence
from `docs/H2/GOVERNANCE.md`. It must not modify production CrystalCore.

## 1. Reference-fidelity test (32k / 64k) — recorded

```
python3 experiments/run_reference_fidelity.py --selftest
python3 experiments/run_reference_fidelity.py
```

## 2. Development sweep — not a configuration freeze

```
python3 experiments/run_dev_sweep.py --selftest
python3 experiments/run_dev_sweep.py
```

Independent systems: `reference`, `candidate_a`, `candidate_b`.
Development partition only. Final seed family is refused.
Receiver fidelity is the ranking axis. Bandwidth is recorded, not gated.

**No performance claims. No 1M dual-gate decision. No configuration freeze.**
Every report includes an Interpretation Boundary.
