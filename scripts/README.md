# Scripts

Developer utilities. Layout follows the v1.0 architecture — subfolders are
created when a script actually exists, not before:

| Folder | For | Exists today |
|---|---|---|
| `maintenance/` | Routine checks and upkeep | `check.sh` — runs the same checks CI runs |
| `setup/` | Environment bootstrap | — |
| `migration/` | One-shot restructuring tools | — |
| `automation/` | Recurring automation | — |

## `maintenance/check.sh`

```bash
scripts/maintenance/check.sh
```

Mirrors `.github/workflows/ci.yml`: syntax check across `src tests archive`,
the four crystal-core self-tests, and both pytest suites. Suites whose
dependencies aren't installed locally are skipped with a notice — CI always
runs everything, so treat a skip as untested, not passed.

Historical note: earlier docs referenced `converge.ps1`,
`export-corpus.ps1`, `create-crystal-models.ps1`, and
`push-github-tree.py` — design intent from before this folder existed. None
were ever written; if they're built someday they land here under the table
above.
