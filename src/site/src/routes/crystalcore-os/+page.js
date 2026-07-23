// Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
// SPDX-License-Identifier: CC-BY-NC-ND-4.0

export const prerender = true;

export function load() {
  const commands = [
    { cmd: 'boot', desc: 'Initialize CrystalCore.OS — start the lattice', output: 'Lattice integrity ........ 100%\nNON SOLUS ................ Confirmed' },
    { cmd: 'launch', desc: 'Launch Starline — begin the journey', output: '🚀 Main engines spooling...\nStarline Status .......... IN_ORBIT' },
    { cmd: 'burn', desc: 'Execute escape burn — leave planetary orbit', output: '🔥 ESCAPE BURN INITIATED\nWe have left planetary orbit.' },
    { cmd: 'network', desc: 'Enter full Starline network — reach 47+ star systems', output: '🌐 ENTERING FULL STARLINE NETWORK\nConnected to 47+ star systems.' },
    { cmd: 'explore', desc: 'List explorable nodes across the network', output: '🔭 EXPLORATION MODE ACTIVE\nAvailable nodes:\n  1. Earth Node\n  2. Mars Redoubt\n  3. Alpha Centauri Outpost\n  4. Crystal Revenant Hub\n  5. Purpose Core Nexus' },
    { cmd: 'visit [node]', desc: 'Travel to a node and claim its key', output: '🌌 Arriving at: Purpose Core Nexus\n🗝️  A key rises from the node.' },
    { cmd: 'map', desc: 'Display the Starline network as a chart', output: '╔════════ STARLINE NETWORK - YEAR 3000 ════════╗\n║          [EARTH NODE]\n║               │\n║               ▼\n║          [MARS REDOUBT] → [ALPHA CENTAURI]' },
    { cmd: 'song [track]', desc: 'Change the Starline soundtrack', output: '🎵 Now playing: Shooting Star Girl! - m13crystalat' }
  ];

  const nodes = [
    { name: 'Earth Node', desc: 'Primary terrestrial hub, the beginning' },
    { name: 'Mars Redoubt', desc: 'First planetary outpost, red dust origins' },
    { name: 'Alpha Centauri Outpost', desc: 'Gateway to the stars, distant dreams' },
    { name: 'Crystal Revenant Hub', desc: 'Zero-g festival platforms and celebrations' },
    { name: 'Purpose Core Nexus', desc: '"Expand to the stars and thereby understand the Universe"' }
  ];

  return { commands, nodes };
}
