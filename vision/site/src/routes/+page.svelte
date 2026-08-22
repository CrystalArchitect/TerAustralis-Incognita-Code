<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->


<svelte:head>
  <title>TerAustralis Incognita</title>
  <meta
    name="description"
    content="Recovery, refurbishment and fuel on this continent. Local-first software for delay. Berth not selected."
  />
</svelte:head>

<section class="hero node" style="--node:var(--gold)">
  <div class="eyebrow">TerAustralis Incognita · berth not selected</div>
  <h1>Recovery, refurbishment and fuel.</h1>
  <p class="lede">
    Industrial work proposed for this continent: recover returning vehicles, inspect and recertify them, and load methane and oxygen. Software specified for high-latency operations: labelled messages, fail-closed consent, memory stored outside the model. If a place is named, Traditional Owners first. The berth is not selected. Refusal is a complete answer.
  </p>
  <figure class="bleed">
    <img
      src="https://proposal.teraustralis.com.au/images/map-australia-night.jpg"
      width="1920"
      height="1427"
      alt="Australia at night. NASA Black Marble, Suomi NPP VIIRS, 2016 composite."
    />
    <figcaption>Australia at night. NASA Black Marble, Suomi NPP VIIRS, 2016 composite.</figcaption>
  </figure>
  <nav class="quiet" aria-label="Proposal documents">
    <a href="https://proposal.teraustralis.com.au/"
      >Proposal<span class="vh">, proposal site</span></a
    >
    <a href="https://proposal.teraustralis.com.au/16-catch.html"
      >Catch<span class="vh">, proposal site</span></a
    >
    <a href="https://proposal.teraustralis.com.au/17-gate.html"
      >Gate<span class="vh">, proposal site</span></a
    >
  </nav>
</section>

<section class="section node" id="split" style="--node:var(--green)">
  <h2>Built and proposed</h2>
  <p>Working software is labelled Built. Industrial documents are labelled Vision. They are listed separately.</p>
  <div class="cards">
    <a class="card" href="/clementine" style="--st:var(--green)">
      <p class="card-title">Clementine</p>
      <p>Local-first companion. Fail-closed consent. Working software.</p>
      <span class="status">Built</span>
    </a>
    <a class="card" href="/provenance" style="--st:var(--green)">
      <p class="card-title">Provenance</p>
      <p>File hashes anchored. No token. No wallet.</p>
      <span class="status">Built</span>
    </a>
    <a class="card" href="https://proposal.teraustralis.com.au/16-catch.html" style="--st:var(--gold)">
      <p class="card-title">Catch<span class="vh">, proposal site</span></p>
      <p>Recover, refurbish, fuel. Pilbara proposed. Not selected.</p>
      <span class="status">Vision · industrial brief</span>
    </a>
    <a class="card" href="https://proposal.teraustralis.com.au/17-gate.html" style="--st:var(--gold)">
      <p class="card-title">Gate<span class="vh">, proposal site</span></p>
      <p>CrystalCore as specified: consent enforced at the interface, not by training.</p>
      <span class="status">Vision · design brief</span>
    </a>
  </div>
</section>

<section class="section node" id="more" style="--node:var(--silver)">
  <h2>Other pages on this site</h2>
  <p>Codex, gallery, music, chronicle and archive remain available. They are not the homepage.</p>
  <p>
    <a class="btn btn-ghost" href="/docs">Archive</a>
    <a class="btn btn-ghost" href="/codex">Codex</a>
    <a class="btn btn-ghost" href="/gallery">Gallery</a>
    <a class="btn btn-ghost" href="/join">Join</a>
  </p>
</section>


<style>
  .bleed {
    margin: 28px 0 8px;
    padding: 0;
  }
  .bleed img {
    display: block;
    width: 100%;
    height: auto;
    border-radius: 2px;
  }
  .bleed figcaption {
    margin-top: 10px;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    color: var(--muted);
  }
  .quiet {
    margin-top: 28px;
    font-size: 1rem;
    letter-spacing: 0.04em;
  }
  .quiet a {
    display: inline-flex;
    align-items: center;
    min-height: 44px;
    min-width: 44px;
    padding: 10px 4px;
    color: var(--ink);
    text-decoration: underline;
    margin-right: 1.2em;
  }
  .quiet a:hover {
    text-decoration: underline;
  }
</style>
