# ConsentGate: Scope and Provenance — Design Spec (Draft for Review)

Status: **draft — decisions pending with the maintainer.** No code changes
accompany this document. It exists so the definitions can be argued with
before anything is built.

## Why now

`core/crystalcore/gate.py` enforces two checks, fail-closed: is the guest
approved at all, and is it approved for this specific tool. Both work and
both are tested. The other two checks — scope and provenance — are
documented as intended in `vision/site/src/content/ARCHITECTURE.md` and
explicitly *not implemented*, per the gate's own docstring: no spec for
what either should concretely mean survived the loss of the original
design docs.

As of 2026-07-31 the public Technical Brief
(proposal.teraustralis.com.au/05-technical-brief.html) states that
CrystalCore's contribution is "consent as an enforced runtime primitive
rather than a privacy posture." Approval plus a tool allowlist is ordinary
authorization; any RBAC system has it. Scope and provenance are the two
checks that would make the public claim true. Under the Incognita Rule the
gap resolves one of two ways — build them, or amend the claim. This spec
is the first half of building them.

## What the code does today (the two holes, precisely)

**Hole 1 — identity is self-asserted.** The bridge reads guest identity
from the `CRYSTALBRIDGE_GUEST` environment variable
(`core/crystalcore/bridge.py`, `main()`). Whoever launches the process
types the name. Nothing distinguishes Claude launched by the maintainer
from any process that sets `CRYSTALBRIDGE_GUEST=claude`. Approval attaches
to a name, and the name is free.

**Hole 2 — `recall` reaches everything.** Memory is a single store per
profile (`memory.json`). An approved guest's `recall` runs
`_memory_block(query)` over the whole of it — including memories formed in
private conversation between the human and the companion that were never
addressed to any guest. Consent to *talk to* the companion is currently
consent to *read its life*.

Scope closes hole 2. Provenance closes hole 1.

## Definitions

### Scope

> **Scope is consent bounded by what a grant may touch, not merely which
> tool it may call.** Concretely: memories carry a visibility class, and a
> grant names the classes it may read and the classes it may write into.

Mechanism:

- Every memory entry gains a `visibility` field. Two classes at first,
  deliberately no more: `private` (default for everything the companion
  learns in conversation with its human) and `shared` (explicitly marked
  by the human, or taught by a guest through the bridge).
- `GuestGrant` gains `read_scope: list[str]` and `write_scope: list[str]`
  (class names).
- `recall` filters the store to classes in the guest's `read_scope`
  *before* semantic search runs — not after, so nothing outside scope can
  influence even the shape of a result.
- `teach` writes into exactly one class, the first entry of `write_scope`;
  a guest is never able to write `private` memories.
- A grant with an empty or absent scope list can read/write **nothing**
  beyond `status`. Fail-closed: absence of scope is absence of consent,
  not legacy full access.

What scope is *not*, in this design: per-tool argument pattern matching
(brittle, and semantic recall makes argument filtering meaningless — the
query isn't where the exposure happens, the store is).

### Provenance

> **Provenance is evidence, checked at execution time, that a request
> actually comes from the party the grant names — and refusal when that
> evidence cannot be established.** Unverifiable origin is treated exactly
> like absent consent.

Mechanism (v1, honest about its limits):

- Each guest entry in `bridge_config.json` gains a `token_hash` (SHA-256).
  The maintainer mints a per-guest secret once (helper command:
  `python -m crystalcore.bridge --mint-token <guest>`), puts the hash in
  the config, and gives the secret to that guest's launcher configuration
  only.
- The bridge reads `CRYSTALBRIDGE_TOKEN` alongside `CRYSTALBRIDGE_GUEST`.
  `ConsentGate.check()` verifies the token against the stored hash before
  either existing check runs. No token, wrong token, or no stored hash →
  refuse, with a distinct audit decision (`refuse-provenance`).
- The audit record (`audit.jsonl`) gains a `provenance` block: whether the
  token verified, plus the transport (`stdio`) — so the append-only log
  can answer "who was that really?" after the fact.

This is launcher authentication, not cryptographic identity of a remote
model — a static secret proves possession of the secret, nothing more. It
is stated as exactly that. The upgrade path (per-session challenge,
signed requests over the mesh when a real transport exists) is noted in
the fail-safe tie-in below and left unbuilt until the transport it would
authenticate exists. Claiming more now would be the overclaim this
project's own rules forbid.

**Fail-safe tie-in.** The First Principles define fail-safe as local
isolation. Provenance is where that becomes enforceable at the gate: a
request whose origin cannot be established *at the moment of execution*
refuses — it does not degrade to the two-check path, and there is no
"assume the last known identity" fallback. When a future transport is
intermittent, this is the check that makes link loss produce silence
instead of trust.

## Check order

1. **Provenance** — is this really the named guest? (refuse-provenance)
2. **Approval** — is the guest approved at all? (existing)
3. **Permission** — may it call this tool? (existing)
4. **Scope** — applied inside the tool: read filtering for `recall`,
   write class for `teach`. (refuse-scope when a tool needs a scope the
   grant lacks entirely)

Provenance runs first because the later checks are meaningless against an
unverified name. `GateResult` gains a `check` field naming which stage
refused, so audit and tests can distinguish the four.

## Migration and compatibility

- **Existing memories** predate the `visibility` field. On first load
  they are classed `private`. This is a behavior change: guests that
  could previously recall everything will recall nothing until the human
  shares or re-teaches. That is the fail-closed default working as
  designed, and it is the single most user-visible consequence of this
  spec. A one-time interactive helper
  (`--review-memories`) lets the human mark entries `shared` in bulk.
- **Existing configs** lack `token_hash` and scope lists. Under this
  spec those guests refuse at provenance until tokens are minted — one
  command per guest, a one-time cost. The alternative (enforce only when
  configured) would make the public claim false for every default
  install, so it is rejected.
- `crystalcore_memory` / `lumina_memory` continuity guarantees are
  unaffected; `visibility` is an additive field with a defined default.

## Testing

The gate's suite is `crystalcore/selftest.py` — 23 plain-function tests
(`cd core && python3 -m crystalcore.selftest`), covering the five checks,
fail-closed defaults, the revocation ledger (runtime effect, restart
survival, reinstatement, corrupt-ledger refuse-all), the pending record
(written before evaluation, survives a mid-gate crash, request id joins
ask to answer), and the type dimension (empty types refuse, unserved
layers refuse honestly, unknown names stop startup, layers beyond
semantic never reach guests). An earlier revision of this section cited
suite counts that never matched the file; this one was corrected against
the real suite on 2026-08-12.

## Records beside the profile

- `audit.jsonl` — every decision, allow and refuse alike, append-only.
- `pending.jsonl` — every ask, written **before** evaluation, with a
  `request_id` the decision line repeats. The `status` field (`received`
  today) is where a future hold-for-approval mode will live.
- `revocations.jsonl` — consent withdrawal as an append-only ledger:
  `{timestamp, guest, action: revoke|reinstate, reason, by}`, latest
  record per guest wins, read on every check. Unreadable ⇒ refuse all.

## Decisions needed before code

1. **Two visibility classes or named partitions?** ~~This spec says two
   (`private`/`shared`) on the argument that classes you can't explain in
   one sentence won't be used correctly. Named partitions (e.g.
   per-project) are a compatible later extension.~~ **Decided, 2026-08-12:**
   two visibility classes stay, and the compatible extension arrived as a
   second, orthogonal dimension — memory *types* (`episodic` / `semantic`
   / `reflective`, the documented taxonomy), enforced at `require_scope`
   and empty-refuses like everything else. Only the semantic layer is
   served to guests today, because only it has per-entry visibility
   consent; a type grant for an unserved layer refuses with a reason
   rather than returning silence.
2. **Strict provenance from day one?** This spec says yes — all guests
   need minted tokens immediately, breaking zero-config guest setups
   once, deliberately. The alternative makes enforcement optional and
   the public claim false by default.
3. **Private-by-default migration?** This spec says yes — existing
   memories become guest-invisible until reviewed. It is the honest
   default and the disruptive one; it needs the maintainer's explicit
   yes, not a quiet landing in a diff.
