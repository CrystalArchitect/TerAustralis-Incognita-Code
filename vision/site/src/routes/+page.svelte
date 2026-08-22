<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->

<script>
  import Footer from '$lib/components/Footer.svelte';
</script>

<svelte:head>
  <title>TerAustralis Incognita</title>
  <meta
    name="description"
    content="Catch, analogue, local brain, Country. Southern industrial proposal. Berth not selected."
  />
</svelte:head>

<section class="hero node" style="--node:var(--gold)">
  <div class="eyebrow">TerAustralis Incognita · not a selected berth</div>
  <h1>Catch what we throw. Think here.</h1>
  <p class="lede">
    Recovery, refurbishment and fuel as a job on this continent. A local-first brain for delay — labelled, fail-closed, memory off the model. Country in the body of the work, not a footnote. Berth not selected. No is a complete answer.
  </p>
  <figure class="bleed">
    <img
      src="https://proposal.teraustralis.com.au/images/map-australia-night.jpg"
      width="1920"
      height="1427"
      alt="Australia at night — NASA Black Marble, Suomi NPP VIIRS, 2016 composite."
    />
    <figcaption>Gold is the grid. The dark is still Country.</figcaption>
  </figure>
  <nav class="quiet" aria-label="Sitting">
    <a href="https://proposal.teraustralis.com.au/">Sitting</a>
    <a href="https://proposal.teraustralis.com.au/16-catch.html">Catch</a>
    <a href="https://proposal.teraustralis.com.au/17-gate.html">Gate</a>
  </nav>
</section>

<section class="section node" id="split" style="--node:var(--green)">
  <h2>Built, and vision</h2>
  <p>Two piles. Not one.</p>
  <div class="cards">
    <a class="card" href="/clementine" style="--st:var(--green)">
      <h3>Clementine</h3>
      <p>Local-first companion. Fail-closed consent. Working software.</p>
      <span class="status">Built</span>
    </a>
    <a class="card" href="/provenance" style="--st:var(--green)">
      <h3>Provenance</h3>
      <p>Hashes anchored. No token. No wallet.</p>
      <span class="status">Built</span>
    </a>
    <a class="card" href="https://proposal.teraustralis.com.au/16-catch.html" style="--st:var(--gold)">
      <h3>Catch</h3>
      <p>Recover, refurbish, fuel. Pilbara proposed. Not selected.</p>
      <span class="status">Vision · industrial brief</span>
    </a>
    <a class="card" href="https://proposal.teraustralis.com.au/17-gate.html" style="--st:var(--gold)">
      <h3>Gate</h3>
      <p>CrystalCore as specified: a gate, not a grader.</p>
      <span class="status">Vision · design brief</span>
    </a>
  </div>
</section>

<section class="section node" id="more" style="--node:var(--silver)">
  <h2>Behind the porch</h2>
  <p>Codex, gallery, music, chronicle, archive — still here. Not the first sentence.</p>
  <p>
    <a class="btn btn-ghost" href="/docs">Archive</a>
    <a class="btn btn-ghost" href="/codex">Codex</a>
    <a class="btn btn-ghost" href="/gallery">Gallery</a>
    <a class="btn btn-ghost" href="/join">Join</a>
  </p>
</section>

<Footer />

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
    color: var(--muted, #9a958c);
  }
  .quiet {
    margin-top: 28px;
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }
  .quiet a {
    color: var(--ink, #e8e4dc);
    text-decoration: none;
    margin-right: 1.4em;
  }
  .quiet a:hover {
    text-decoration: underline;
  }
</style>
