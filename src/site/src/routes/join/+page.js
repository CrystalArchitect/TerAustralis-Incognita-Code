// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: CC-BY-NC-ND-4.0

export const prerender = true;

export function load() {
  // Real ways to take part — the site is static, so "joining" means
  // contributing through channels that actually exist.
  const ways = [
    {
      title: 'Contribute',
      body: 'Fixes, features, art, mythos — the whole project is open on GitHub. Add something and open a pull request.',
      href: 'https://github.com/CrystalArchitect/teraaustralis-incognita',
      cta: '→ Open the repo',
      st: 'var(--green)'
    },
    {
      title: 'Share & connect',
      body: 'Making work in this vein? Tag it, share it, and reach out — the conversation is open.',
      href: 'https://x.com/m13crystalat',
      cta: '→ On X',
      st: 'var(--blue)'
    },
    {
      title: 'Add to the Starline Transmissions',
      body: 'The soundtrack is a living thing. New voices and tracks are welcome.',
      href: 'https://suno.com/@m13crystalat',
      cta: '→ On Suno',
      st: 'var(--pink)'
    },
    {
      title: 'Support the vision',
      body: 'Back the work directly so it can keep being built in the open.',
      href: 'https://patreon.com/CrystalCore91',
      cta: '→ On Patreon',
      st: 'var(--gold)'
    }
  ];

  // Contributors, credited by their own handle for work they actually made —
  // listed with their permission. Seeded with the founder; add others only with
  // their okay. No affiliation or endorsement is implied by being listed.
  const vectors = [
    {
      handle: '@M13CrystalAT',
      href: 'https://x.com/m13crystalat',
      work: 'CrystalArchitect — the mythos, the Codex, the art, and the whole vision.',
      st: 'var(--purple)'
    },
    {
      handle: '@m13crystalat',
      href: 'https://suno.com/@m13crystalat',
      work: 'Original music — the Starline Transmissions soundtrack.',
      st: 'var(--pink)'
    }
  ];

  return { ways, vectors };
}
