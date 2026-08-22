# H2 experiments

Methodology is locked at V0.1. This directory runs the execution sequence
from `docs/H2/GOVERNANCE.md`. It must not modify production CrystalCore.

## Reference-fidelity test (32k / 64k)

Development partition only. Final seed family is refused by the runner.

```
python3 experiments/run_reference_fidelity.py --selftest
python3 experiments/run_reference_fidelity.py
```

Independent systems: `reference`, `candidate_a`, `candidate_b`.
Each writes `results/reference-fidelity-32k-64k/<system>.json` before
assembly. Candidates do not read each other's files.

**No performance claims.** The 1M dual gate is not evaluated here.
