// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: CC-BY-NC-ND-4.0

export const prerender = true;

// The catalogue mirrors mythos/music/README.md in the umbrella repository —
// the source of truth for every fact here, including the honest gaps.
// One row per *recording*, not per song: a work can have more than one take.
const REPO = 'https://github.com/CrystalArchitect/TerAustralis-Incognita/blob/main/mythos/music';

export function load() {
  const tracks = [
    { file: 'red-dust-axis.mp3', work: 'Red Dust Axis', canon: 'ignition song', length: '3:35', generated: '2026-05-02', plan: 'free tier — before Pro began 7 May', commercial: false },
    { file: 'shooting-star-girl-2026-05-04.mp3', work: 'Shooting Star Girl (first take)', canon: 'ignition song', length: '2:15', generated: '2026-05-04', plan: 'free tier — before Pro began 7 May', commercial: false },
    { file: 'wire-skull-memory.mp3', work: 'Wire Skull Memory', canon: 'standalone, in canon', length: '2:16', generated: '2026-05-07', plan: 'Pro — same day the plan began', commercial: true },
    { file: 'fermis-silent-line.mp3', work: "Fermi's Silent Line", canon: 'ignition song', length: '4:34', generated: '2026-05-10', plan: 'Pro', commercial: true },
    { file: 'safari-chains.mp3', work: 'Safari Chains', canon: 'not in canon', length: '3:14', generated: '2026-05-10', plan: 'Pro', commercial: true },
    { file: 'different-parts.mp3', work: 'Different Parts', canon: 'not in canon', length: '3:39', generated: '2026-07-17', plan: 'free tier — Pro ended 6 June', commercial: false },
    { file: 'id-lay-it-all-down.mp3', work: "I'd Lay It All Down", canon: 'not in canon', length: '4:15', generated: '2026-07-21', plan: 'free tier — Pro ended 6 June', commercial: false },
    { file: null, work: 'Look What You Made Me Do', canon: 'not in canon · removed 2026-07-31', length: '3:52', generated: '2026-07-21', plan: 'free tier — Pro ended 6 June', commercial: false, removed: true },
    { file: 'starline-rivers.mp3', work: 'Starline Rivers', canon: 'not in canon · shares its name with canon art', length: '4:24', generated: '2026-07-21', plan: 'free tier — Pro ended 6 June', commercial: false },
    { file: 'shooting-star-girl-2026-07-30.mp3', work: 'Shooting Star Girl (second take)', canon: 'ignition song', length: '3:34', generated: '2026-07-30', plan: 'free tier — Pro ended 6 June', commercial: false },
    { file: 'dead-but-came-back-to-life.mp3', work: 'Dead But Came Back to Life', canon: 'not in canon', length: '3:20', generated: '2026-07-31', plan: 'free tier — Pro ended 6 June', commercial: false }
  ];

  return {
    tracks: tracks.map((t) => ({ ...t, url: t.file ? `${REPO}/${t.file}` : null }))
  };
}
