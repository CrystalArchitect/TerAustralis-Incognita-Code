# Host Trust — Design Spec

Status: **designed; classifier exists; not yet a gate door.** 2026-08-25.

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

## Not yet wired

ConsentGate and `consent_transport` do **not** call this classifier
yet. Wiring it would break GitHub-hosted self-tests that mint
throwaway identities unless those tests declare ephemeral-on-shared.
That is a later decision, same shape as ConsentGate: spec first, then
enforce with the maintainer's yes.

Until wired, the architecture still has the hole at runtime. The
classifier and this spec exist so the hole is named rather than
mythologised.

## Mapping

- ConsentGate provenance = *who*. Host trust = *where*.
- Southern Cross architecture Layer 0 (Ground) = `local` / `delegated`
  only. SHARED is not Ground.
- Layer 2 (`consent_transport`) stays the wire. Do not rename it HADES
  and do not stand up a second protocol.
- Vision/mythos (Atlas, Starlines geometry) must not claim this
  classifier as a celestial lock.

## Explicitly does not contain

- A boot sequence that “replaces HADES”
- A claim that this Grok/chat session is local
- Songline mapping
- H2, materials, or proposal-berth changes
