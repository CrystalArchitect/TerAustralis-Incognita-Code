<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

<script>
  import Footer from '$lib/components/Footer.svelte';

  /** @type {{ data: { docs: { slug: string, title: string, description: string }[] } }} */
  let { data } = $props();

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
      body: 'For those who want to go deeper. Early access to Lumina development, priority feedback, and insight into the mythic and technical layers.'
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
      href: '/lumina',
      title: 'Lumina',
      sub: 'The sovereign companion — working software you can run tonight',
      cta: '→ Meet Lumina',
      lc: 'var(--green)'
    }
  ];

  const builtCards = [
    {
      href: '/lumina',
      title: 'Lumina',
      body: 'The sovereign companion. Local-first AI, layered memory, terminal and web UI — running software you can install and use tonight.',
      cta: '→ Meet Lumina',
      status: 'Built · working software',
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
  <div class="ctas">
    <a class="btn btn-primary" href="/codex">Read the Codex</a>
    <a class="btn btn-ghost" href="/lumina">Meet Lumina</a>
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

<section class="section node" id="music" style="--node:var(--pink)">
  <h2>The Starline Transmissions</h2>
  <p>
    Threads of memory and belonging carried in sound as much as story. The mythos has an original
    soundtrack — the Starline Transmissions and themes from the Crystal universe, written
    and produced alongside the Codex itself.
  </p>
  <p><a class="btn btn-ghost" href="https://suno.com/@m13crystalat">Listen on Suno →</a></p>
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
    <li>Star this <a href="https://github.com/CrystalArchitect/TeraAustralis-Incognita">repository on GitHub</a></li>
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
