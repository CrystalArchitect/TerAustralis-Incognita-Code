# Host Trust — Design Spec

Status: **wired for `consent_transport` persist.** CrystalBridge
(`write_json_atomic` / mint-token / private memory) is still open.
2026-08-25.

This document adds a missing trust boundary: **where code is running**.
ConsentGate already fail-closes on *who* is asking and *what* they may
touch. It did not classify the *host*. Shared vendor pools are therefore
invisible to the architecture, which is the hole this spec names.

It does **not** unshare a pooled sandbox. It does not replace a vendor
allocator. It does not mint a seventh OS. A classifier that cannot empty
the pool still refuses to treat the pool as Layer 0.

## Why this was written

The steward named a class of problem: execution on a **shared cloud
sandbox** (the vendor pool they call HADES — SpaceX/xAI shared
sandboxes). Capacity, tenancy, and session refusal on that pool are the
vendor's. CrystalCore cannot move that machine.

What the framework *can* do is stop pretending that pool is a sovereign
computer. Peers are already untrusted until grant
(`consent_transport`). Hosts were not. This spec puts hosts in the same
fail-closed family as provenance: **unverifiable or shared origin
refuses steward persist.**

HADES is a **steward name for a SHARED pool**. It is not a `HostClass`
value, not a module, and not a southern berth.

## Classes

| Class | Meaning | Steward persist |
|---|---|---|
| `local` | Machine the steward controls | allowed |
| `delegated` | Named runner the steward controls (e.g. self-hosted Actions) | allowed |
| `shared` | Vendor multi-tenant pool (GitHub-hosted CI, HADES-class sandboxes) | **refuse** |
| `unknown` | Origin not established | **refuse** |

Default with no signal is `unknown`, not `local`. Same law as
provenance: absence of evidence is not home.

## What refuses on `shared` / `unknown`

Durable steward material:

- identity mint
- consent-save
- token-mint
- fragment-persist
- private memory write
- peer-save

**Exception — ephemeral scratch.** Writes whose resolved path is under
`tempfile.gettempdir()` (or `$TMPDIR` / `$TEMP`) are allowed. GitHub-hosted
self-tests mint throwaway identities there. That is not a home.

**Hatch.** `CRYSTAL_HOST_ALLOW_EPHEMERAL=1` allows any path. It is an
explicit override, not a default, and it does not reclassify the host.

Public, reproducible, non-secret work may still run on `shared` (site
build, Lighthouse against a local build artifact, syntax, this
classifier's own tests). That does not make the host trusted.

## Classifier (implemented)

`core/crystal-core/host_trust/`

- Steward override: `CRYSTAL_HOST_CLASS=local|delegated|shared|unknown`
- If unset and `GITHUB_ACTIONS=true`:
  - `RUNNER_ENVIRONMENT=self-hosted` → `delegated`
  - otherwise → `shared`
- Else → `unknown`
- A value of `hades` / `HADES` is **not** a class; it classifies
  `unknown` (fail-closed), so a vendor nickname cannot mint a home.

Prove: `cd core/crystal-core && python3 -m host_trust.selftest`

## Wired (2026-08-25)

`require_steward_persist(operation, path)` is the choke. On
`shared` / `unknown` it raises `PermissionError` unless the path is
ephemeral or the hatch is set.

Called from:

- `consent_transport.identity.Identity.save` — `identity-mint`
- `consent_transport.consent._write_json_atomic` — `consent-save`
  (covers `ConsentEngine.save` and `TokenStore.save`)
- `consent_transport.peers.PeerStore.save` — `peer-save`

GitHub-hosted CI stays green because those suites write under the
process temp dir. A durable path (`/usr/...`, cwd, `$HOME`) on a pooled
box is the thing that must fail.

This is not a sixth ConsentGate door. Provenance is still *who*. Host
trust is *where*. The five guest doors do not move.

## Still open

- CrystalBridge `crystalcore.config.write_json_atomic` (mint-token,
  grants file, private memory). Import path is `core/`, not
  `crystal-core/`. Not this commit.
- Fragment persist and private memory write are named in
  `STEWARD_PERSIST` and not yet called from those writers.
- A self-hosted runner is a **path**, not a plug. Default CI stays
  GitHub-hosted. See [`docs/deployment/STEWARD-RUNNER.md`](deployment/STEWARD-RUNNER.md).

Until CrystalBridge is wired, that write path can still land durable
grants on a pool. The hole is named.

## Mapping

- ConsentGate provenance = *who*. Host trust = *where*.
- Southern Cross architecture Layer 0 (Ground) = `local` / `delegated`
  only. SHARED is not Ground.
- Layer 2 (`consent_transport`) stays the wire. Do not rename it HADES
  and do not stand up a second protocol.
- Vision/mythos (Atlas, Starlines geometry) must not claim this
  classifier as a celestial lock.
- Songline stays outside the system. Public `/starline` copy uses
  Starline.

## Explicitly does not contain

- A boot sequence that “replaces HADES”
- A claim that this Grok/chat session is local
- A claim that the vendor pool is now unshared
- Songline mapping
- H2, materials, or proposal-berth changes
- A switch of default CI onto a box the maintainer does not have
