# CrystalBridge

MCP consent gate for guest access to companion memory.

See repository docs for full architecture.

## Config

Guest grants in `profiles/<name>/bridge_config.json`.

Add a guest by adding a key under `guests`. Nothing is granted by default.

### Durable revoke / reinstate

```bash
python3 -m crystalcore --revoke claude --reason "session ended"
python3 -m crystalcore --reinstate claude --reason "restored"
```

Appends to `profiles/<name>/revocations.jsonl` (latest wins). No restart.
Reinstate restores the standing grant; it mints no token.

### Memory type-gates

`read_types` / `write_types` are subsets of `{episodic, semantic, reflective}`
(summaries / notes+facts / reflections). Working memory is never guest-readable.
Missing type fields load as `[]` and refuse (breaking, fail-closed). Unknown
type names stop startup. Default profile migrates full guests to all three
read types + semantic write; restricted reads semantic only.

`pending.jsonl` records each ask before evaluation (`status: received`).
`interactive_approval` remains a reserved hook.

## Prove it

```bash
cd core && python3 -m crystalcore.selftest
```
