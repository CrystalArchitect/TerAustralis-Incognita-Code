<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->

<script>
  import Constellation from '$lib/components/Constellation.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import { chronicle } from '$lib/data/chronicle.js';

  /** @type {{ data: { docs: { slug: string, title: string, description: string }[] } }} */
  let { data } = $props();

  // The principles, doc-backed: each card opens the Archive where the
  // full text lives.
  const principles = [
    {
      href: '/docs',
      title: 'Curiosity',
      body: 'Curiosity before certainty. The unknown south was found by sailing toward it, not by asserting it was there.',
      status: 'the spirit of the search',
      st: 'var(--blue)'
    },
    {
      href: '/docs',
      title: 'Evidence',
      body: 'Evidence before conclusion. Dreamed lines are marked as dreamed until they are surveyed — and never pretend to be measured.',
      status: 'the Incognita Rule',
      st: 'var(--gold)'
    },
    {
      href: '/docs',
      title: 'Stewardship',
      body: 'Stewardship before ownership. Consent before influence. Discovery shared for the benefit of those who follow.',
      status: 'the Covenant',
      st: 'var(--green)'
    }
  ];

  // The Chronicle entries live in $lib/data/chronicle.js — the single
  // source of truth, dated from the repositories' own history.

  const archiveColors = [
    'var(--purple)',
    'var(--blue)',
    'var(--gold)',
    'var(--green)',
    'var(--pink)',
    'var(--silver)'
  ];

  const tiers = [
    {
      price: '$5 / month',
      title: '🌱 Supporter',
      color: 'var(--green)',
      body: 'Thank you for believing in the vision. A public thank you and your name listed in the Supporters section.'
    },
    {
      price: '$10 / month',
      title: '✨ Dreamer',
      color: 'var(--blue)',
      body: 'For those connected to the story. Early access to new chapters of the Codex and Apocryphon, plus behind-the-scenes updates.'
    },
    {
      price: '$25 / month',
      title: '🕸️ Weaver',
      color: 'var(--purple)',
      body: 'For those who want to go deeper. Early access to Clementine development, priority feedback, and insight into the mythic and technical layers.'
    },
    {
      price: '$50 / month',
      title: '🏛️ Architect',
      color: 'var(--pink)',
      body: 'For those who want to help shape the future. Direct input on direction, personal updates from the CrystalArchitect, and collaboration opportunities.'
    },
    {
      price: '$100 / month',
      title: '🌟 Starline Keeper',
      color: 'var(--gold)',
      body: 'For those who deeply support the long-term vision. Regular personal updates, early access to major developments, and a hand in shaping key parts of the work.'
    },
    {
      price: '$250+ / month',
      title: '🚀 Visionary',
      color: 'var(--silver)',
      body: 'For those who want to become a true partner — serious collaborators working closely with the steward on the mythic, creative, or technical direction. Direct communication and co-creation.'
    }
  ];

  const codexLinks = [
    {
      href: '/codex',
      title: 'The Codex',
      sub: 'The canonical mythic work — Chapters I through V',
      cta: '→ Read the Codex',
      lc: 'var(--gold)'
    },
    {
      href: '/apocryphon',
      title: 'The Apocryphon of Crystal',
      sub: 'A personal and philosophical companion text',
      cta: '→ Read the Apocryphon',
      lc: 'var(--pink)'
    },
    {
      href: '/clementine',
      title: 'Clementine',
      sub: 'The sovereign companion — working software you can run tonight',
      cta: '→ Meet Clementine',
      lc: 'var(--green)'
    }
  ];

  const builtCards = [
    {
      href: '/clementine',
      title: 'Clementine',
      body: 'The sovereign companion. Local-first AI, layered memory, a fail-closed consent gate and a hash-chained audit log — running software you can install and use tonight.',
      cta: '→ Meet Clementine',
      status: 'Built · working software',
      st: 'var(--green)'
    },
    {
      href: '/provenance',
      title: 'Provenance',
      body: 'Every artwork, recording and canon text hashed into one manifest, anchored to Bitcoin via OpenTimestamps. No token, no wallet — and verifiable by anyone with the repository.',
      cta: '→ How the anchor works',
      status: 'Built · anchored and re-anchored',
      st: 'var(--green)'
    }
  ];

  const mixedCards = [
    {
      href: '/starline',
      title: 'Starline',
      body: 'A real peer-to-peer protocol — Noise IK handshake, consent-gated exchange — presented alongside its mythic framing as the Starline Transmissions.',
      cta: '→ Explore Starline',
      status: 'Built + Vision · protocol with mythic framing',
      st: 'var(--blue)'
    }
  ];

  const visionCards = [
    {
      href: '/codex',
      title: 'The Codex',
      body: 'The canonical mythic work — Chapters I through V of the Crystal universe story.',
      cta: '→ Read the Codex',
      status: 'Vision · narrative',
      st: 'var(--gold)'
    },
    {
      href: '/apocryphon',
      title: 'The Apocryphon',
      body: 'A personal and philosophical companion text to the Codex.',
      cta: '→ Read the Apocryphon',
      status: 'Vision · narrative',
      st: 'var(--gold)'
    },
    {
      href: '/gallery',
      title: 'The Gallery',
      body: 'Original art from the Crystal universe.',
      cta: '→ View the Gallery',
      status: 'Vision · art',
      st: 'var(--gold)'
    },
    {
      href: '/crystalcore-os',
      title: 'CrystalCore.OS',
      body: 'The mythos rendered as an interactive terminal you can fly through.',
      cta: '→ Fly CrystalCore.OS',
      status: 'Vision · interactive mythos',
      st: 'var(--gold)'
    }
  ];
</script>

<svelte:head>
  <title>TerAustralis Incognita — The Crystal Vision</title>
  <meta
    name="description"
    content="A living mythos and speculative-futures project from Australia. Red dust to rockets, Dreamlines to deep space."
  />
</svelte:head>

<section class="hero node" style="--node:var(--purple)">
  <div class="eyebrow">TerAustralis Incognita · The Crystal Vision</div>
  <h1>
    Red dust to rockets.<br />Dreamlines to deep space.<br /><span class="early">We are early.</span>
  </h1>
  <p class="lede">
    TerAustralis Incognita is a living mythos and speculative futures project born in Australia. At
    its heart is The Codex of TerAustralis Incognita — a five-chapter story that weaves together
    ancient dreams of a Great Southern Land, the deep Songlines of this continent, and humanity's
    reach for the stars.
  </p>
  <p class="directive">&ldquo;Expand to the stars and thereby understand the Universe.&rdquo;</p>
  <p class="directive-tag">The Purpose Core directive</p>
  <div class="ctas">
    <a class="btn btn-primary" href="/codex">Read the Codex</a>
    <a class="btn btn-ghost" href="/clementine">Meet Clementine</a>
  </div>
</section>

<section class="section node" id="constellation" style="--node:var(--silver)">
  <h2>The Constellation</h2>
  <p>
    The ecosystem, as it looks from a little way out: seven lights, joined. Every node is a door
    that actually opens — follow any of them inward.
  </p>
  <Constellation />
</section>

<section class="section node" id="purpose" style="--node:var(--gold)">
  <h2>Purpose</h2>
  <p>
    Three commitments hold everything on this site — the story, the software, and the space
    between them.
  </p>
  <div class="cards">
    {#each principles as p (p.title)}
      <a class="card" href={p.href} style="--st:{p.st}">
        <h3>{p.title}</h3>
        <p>{p.body}</p>
        <span class="status">{p.status}</span>
      </a>
    {/each}
  </div>
</section>

<section class="section node" id="built-vs-vision" style="--node:var(--green)">
  <h2>What's Built, What's Vision</h2>
  <p>
    This project is two things at once, kept honestly separate. Some of it is working software with
    tests you can run yourself. Some of it is narrative, art, and speculative framing — labeled as
    such. Where the two meet, the code is the source of truth and the story says so.
  </p>

  <p class="subhead" style="--sh:var(--green)">Built — working software</p>
  <div class="cards">
    {#each builtCards as card (card.href)}
      <a class="card" href={card.href} style="--st:{card.st}">
        <h3>{card.title}</h3>
        <p>{card.body}</p>
        <span class="status">{card.status}</span>
      </a>
    {/each}
  </div>

  <p class="subhead" style="--sh:var(--blue)">Built + Vision — real protocol, mythic framing</p>
  <div class="cards">
    {#each mixedCards as card (card.href)}
      <a class="card" href={card.href} style="--st:{card.st}">
        <h3>{card.title}</h3>
        <p>{card.body}</p>
        <span class="status">{card.status}</span>
      </a>
    {/each}
  </div>

  <p class="subhead" style="--sh:var(--gold)">Vision — mythos, narrative, and art</p>
  <div class="cards">
    {#each visionCards as card (card.href)}
      <a class="card" href={card.href} style="--st:{card.st}">
        <h3>{card.title}</h3>
        <p>{card.body}</p>
        <span class="status">{card.status}</span>
      </a>
    {/each}
  </div>
</section>

<section class="section node" id="vision" style="--node:var(--blue)">
  <h2>The Vision</h2>
  <p>
    A future needs a story as much as it needs infrastructure. This project is an attempt to write
    that story for Australia's place in the space age — grounded in deep time, guided by intuition,
    and reaching toward the stars.
  </p>
</section>

<section class="section node" id="codex" style="--node:var(--gold)">
  {#each codexLinks as link (link.href)}
    <a class="codexlink" href={link.href} style={`--lc:${link.lc}`}>
      <strong>{link.title}</strong>
      <span>{link.sub}</span>
      <span class="cta">{link.cta}</span>
    </a>
  {/each}
</section>

<section class="section node" id="archive" style="--node:var(--silver)">
  <h2>The Archive</h2>
  <p>
    Every document that shapes this project is rendered live from the repository. Browse the full
    library, or jump straight to a text below.
  </p>
  <div class="tiers">
    {#each data.docs as doc, i (doc.slug)}
      <a class="tier" href={`/docs/${doc.slug}`} style={`--tc:${archiveColors[i % archiveColors.length]}`}>
        <h3>{doc.title}</h3>
        {#if doc.description}
          <p>{doc.description}</p>
        {/if}
      </a>
    {/each}
  </div>
  <p><a class="btn btn-ghost" href="/docs">Open the full Archive →</a></p>
</section>

<section class="section node" id="chronicle" style="--node:var(--green)">
  <h2>The Chronicle</h2>
  <p>
    The development record, dated from the repositories' own history — survey, not legend. The
    full detail behind every entry lives in <a href="/docs">the Archive</a>.
  </p>
  <ol class="timeline">
    {#each chronicle as entry (entry.when + entry.what)}
      <li style="--tl:{entry.tl}">
        <span class="when">{entry.when}</span>
        <span class="what">{entry.what}</span>
        <span class="note">{entry.note}</span>
      </li>
    {/each}
  </ol>
  <p class="timeline-coda">The chronicle is never an ending. It is the point from which the next journey begins.</p>
</section>

<section class="section node" id="music" style="--node:var(--pink)">
  <h2>The Starline Transmissions</h2>
  <p>
    Threads of memory and belonging carried in sound as much as story. The mythos has an original
    soundtrack — the Starline Transmissions and themes from the Crystal universe, written
    and produced alongside the Codex itself.
  </p>
  <p>
    Since 31 July 2026 the recordings are preserved in the public repository — ten recordings,
    catalogued with honest labels, hashed file by file, and covered by the Bitcoin-anchored
    manifest. The platform copy is a convenience; the repository copy is the record.
  </p>
  <p>
    <a class="btn btn-ghost" href="/music">The catalogue →</a>
    <a class="btn btn-ghost" href="https://suno.com/@m13crystalat">Listen on Suno →</a>
  </p>
</section>

<section class="section node" id="mythos-art" style="--node:var(--gold)">
  <h2>Mythos Art — Ordinals Collection</h2>
  <p>
    Visual canon of the TerAustralis Incognita universe, inscribed on-chain as Ordinals on BSV
    and listed on 3dordi. The art is credited to Crystal Arena-Turner — TerAustralis Incognita;
    the inscribing is independent work by <a href="https://x.com/pacartcollect">@pacartcollect</a>
    under a written licence grant.
  </p>
  <p>
    <strong>The project issues no token</strong>, runs no sale, and holds no coin. An inscription
    buys a copy of an artwork and nothing else — no membership, no stake, no financial product.
  </p>
  <p>
    <a
      class="btn btn-ghost"
      href="https://3dordi.io/collection/cc35f9a95773d2f97328ccb33c582d1f853e7856c47397751a06a0e910da8086_0"
      >View on 3dordi →</a
    >
    <a class="btn btn-ghost" href="/ordinals">What this is, and isn't →</a>
  </p>
</section>

<section class="section node" id="support" style="--node:var(--gold)">
  <h2>Support the Vision</h2>
  <p>
    This project is independently built and self-funded. You don't need to give money to help —
    creative contributions (storytelling, music, art, writing, ideas, etc.) are deeply welcome.
  </p>

  <p class="subhead">Financial Support Options</p>
  <ul class="support-list">
    <li><a href="https://patreon.com/CrystalCore91"><strong>Patreon</strong></a></li>
  </ul>
  <p style="color:var(--muted)">Patreon tiers:</p>
  <div class="tiers">
    {#each tiers as tier (tier.title)}
      <a
        class="tier"
        href="https://patreon.com/CrystalCore91"
        style="--tc:{tier.color}"
      >
        <span class="price">{tier.price}</span>
        <h3>{tier.title}</h3>
        <p>{tier.body}</p>
      </a>
    {/each}
  </div>

  <p class="subhead">Other Ways to Contribute</p>
  <ul class="support-list">
    <li>Star this <a href="https://github.com/CrystalArchitect/TerAustralis-Incognita">repository on GitHub</a></li>
    <li>Listen to and share the soundtrack on <a href="https://suno.com/@m13crystalat">Suno</a></li>
    <li>Share the project with people who might resonate</li>
    <li>Offer your skills as a storyteller, singer, musician, writer, artist, or developer</li>
    <li>Reach out if you feel called to collaborate</li>
  </ul>
  <p>
    Reach out: <a href="https://x.com/m13crystalat"><strong>@M13CrystalAT on X</strong></a>
  </p>
</section>

<section class="section node" id="contact" style="--node:var(--green)">
  <h2>Contact</h2>
  <p>
    Stewarded by the CrystalArchitect<br />
    <a href="https://x.com/m13crystalat"><strong>@M13CrystalAT on X</strong></a><br />
    <a href="https://suno.com/@m13crystalat"><strong>@m13crystalat on Suno</strong></a>
  </p>
</section>

<Footer showVoices showCode />

<style>
  .directive {
    margin-top: 28px;
    font-family: var(--font-display);
    font-style: italic;
    font-weight: 500;
    font-size: clamp(1.05rem, 2.4vw, 1.3rem);
    color: var(--gold);
    max-width: 40ch;
  }
  .directive-tag {
    margin-top: 6px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .timeline {
    list-style: none;
    margin: 30px 0 0 6px;
    padding: 0;
  }
  .timeline li {
    position: relative;
    padding: 0 0 26px 32px;
    border-left: 1px solid var(--line);
  }
  .timeline li:last-child {
    padding-bottom: 4px;
    border-left-color: transparent;
  }
  .timeline li::before {
    content: '';
    position: absolute;
    left: -5px;
    top: 0.45em;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--tl, var(--silver));
    box-shadow: 0 0 12px 1px var(--tl, var(--silver));
  }
  .timeline .when {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    letter-spacing: 0.06em;
    color: var(--muted);
  }
  .timeline .what {
    display: block;
    margin-top: 2px;
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.08rem;
    color: var(--tl, var(--ink));
  }
  .timeline .note {
    display: block;
    margin-top: 3px;
    font-size: 0.92rem;
    color: var(--muted);
    max-width: 58ch;
  }
  .timeline-coda {
    margin-top: 26px;
    font-family: var(--font-display);
    font-style: italic;
    color: var(--silver);
  }
</style>
