// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: CC-BY-NC-ND-4.0

// Single source of truth for the homepage Chronicle — accepted from the
// Phase I architecture plan. Dated from the repositories' own history:
// survey, not legend. Every entry must stay verifiable in the Archive.

/**
 * @typedef {Object} ChronicleEntry
 * @property {string} when - ISO date, as recorded in repo history
 * @property {string} what - the milestone, one breath
 * @property {string} note - the detail, still checkable
 * @property {string} tl - timeline accent (CSS custom property)
 */

/** @type {ChronicleEntry[]} */
export const chronicle = [
  {
    when: '2026-07-14',
    what: 'First light',
    note: 'The Crystal Vision repository opens — the oldest commit anywhere in the portfolio.',
    tl: 'var(--purple)'
  },
  {
    when: '2026-07-15',
    what: 'The companion is born',
    note: 'Lumina arrives (first named Clementine): local-first, layered memory, sovereignty by design.',
    tl: 'var(--green)'
  },
  {
    when: '2026-07-17',
    what: 'The snapshot is saved',
    note: 'The last capture from the founding laptop is preserved; the three earliest repositories are sealed as provenance.',
    tl: 'var(--silver)'
  },
  {
    when: '2026-07-21',
    what: 'The great renaming',
    note: 'Lumina and the Starline Weaver take their true names.',
    tl: 'var(--blue)'
  },
  {
    when: '2026-07-23',
    what: 'Boundaries adopted',
    note: 'ADR-0011 splits the work honestly: the umbrella keeps canon and governance; the engine and this site move to the code repository.',
    tl: 'var(--gold)'
  },
  {
    when: '2026-07-24',
    what: 'The archaeology',
    note: 'All six repositories surveyed with an identical battery — every claim tiered by evidence, corrections recorded.',
    tl: 'var(--pink)'
  },
  {
    when: '2026-07-27',
    what: 'The terminal flies',
    note: 'CrystalCore.OS boots from a fresh clone — boot, network, broadcast, priority channel — and the Chronicle itself begins.',
    tl: 'var(--purple)'
  }
];
