# CrystalBridge

A fail-closed MCP server that lets a guest AI (Claude, Grok, Cursor, ...)
meet Lumina — with only the access you've explicitly granted it.

**Provenance note:** `config.py` and `bridge.py` were rebuilt from scratch —
the machine this project was originally written on is gone, and with it the
design doc (`docs/CRYSTALBRIDGE.md`) that would have specified this
precisely. What's here was reconstructed from `gate.py` (which was intact),
the sample `src/profiles/default/bridge_config.json`, and the CLI/env-var
contract already assumed by `docs/guides/MCP-Guest.md` and `docs/guides/Access.md`. Treat
`recall`/`teach`/`message` as a first pass, not settled design.

## How it works

Every tool call passes through `ConsentGate.check()` before anything runs.
Four checks, fail-closed: is the guest approved at all, is it approved for
*this* tool, and (implicitly, via `gate.py`) every decision is written to an
append-only audit log — allowed and refused calls alike.

```
guest calls a tool
      │
      ▼
ConsentGate.check(guest, tool, arguments)
      │
  ┌───┴────┐
refused   allowed
  │         │
  ▼         ▼
return    run the tool, then
refusal   log the decision
payload
```

## Running it

```bash
cd TeraAustralis-Incognita   # repo root — matters, see note below
pip install -r requirements-bridge.txt
CRYSTALBRIDGE_GUEST=claude python3 -m crystalcore.bridge --profile default
```

`CRYSTALBRIDGE_GUEST` identifies who's connecting for the life of the
process — one guest per bridge invocation, matching how MCP stdio servers
are normally launched (once per client). `--profile` selects which
`src/profiles/<name>/bridge_config.json` to load, and also which of Lumina's
own profiles (`src/apps/lumina/lumina_profiles/<name>/`) to give access
to — the two share a name on purpose, so a bridge profile always points at
one specific Lumina.

**Run it from the repo root.** Lumina's own memory-directory resolution
is relative to the calling process's working directory, which would silently
point the bridge at a different (empty) memory location than the one you use
day to day. `bridge.py` works around this by resolving the path explicitly
relative to `src/apps/lumina/` rather than trusting the relative helper —
see the comment on `Bridge.companion` if you're touching that code.

## Config: `src/profiles/<name>/bridge_config.json`

```json
{
  "profile": "default",
  "human_name": "crystal",
  "interactive_approval": false,
  "guests": {
    "claude": { "approved": true, "tools": ["status", "recall", "teach", "message"] },
    "restricted": { "approved": true, "tools": ["status", "recall"] }
  }
}
```

Add a guest by adding a key under `guests`. Revoke access by setting
`"approved": false` or removing the entry — nothing is granted by default.
`interactive_approval` is read but not yet acted on by anything (reserved
for a future "ask before allowing" mode).

## Tools

| Tool | What it does | Touches Lumina's memory? |
|---|---|---|
| `status` | Reports the calling guest's identity and granted tools | No |
| `recall` | Returns what Lumina remembers, optionally filtered by a query (wraps her existing `_memory_block`) | Read-only |
| `teach` | Tells Lumina something to remember permanently (wraps her existing `remember`) | Writes |
| `message` | Leaves a note for the human | No — written to `src/profiles/<name>/messages.jsonl`, deliberately **not** folded into Lumina's memory automatically |

`message` is kept separate from `teach` on purpose: a note left by a guest
AI shouldn't silently become one of Lumina's permanent memories without
a human choosing that.

## Audit trail

Every decision — allowed or refused — is appended to
`src/profiles/<name>/audit.jsonl`, one JSON object per line: timestamp, guest,
tool, arguments (long text fields truncated), decision, reason. Guest
messages land in the separate `src/profiles/<name>/messages.jsonl`. Neither file
is committed to git (see `.gitignore`) — they're real conversation content,
not config.
