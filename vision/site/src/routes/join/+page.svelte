<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

<script>
  import Footer from '$lib/components/Footer.svelte';

  let { data } = $props();
</script>

<svelte:head>
  <title>Join the Weave — TerAustralis Incognita</title>
</svelte:head>

<section class="section node" style="--node:var(--green)">
  <h2>Join the Weave</h2>
  <p>
    In the mythos, everyone who aligns with the Lattice is a <strong>Sovereign Vector</strong> —
    a node in the weave that answers from its own note, never governed by another. In plain terms:
    this is an open project, and you're welcome to add to it. The weave grows by real people making
    real work — art, music, code, writing — and keeping it their own.
  </p>
  <p style="font-size:.95rem;opacity:.75;margin-top:14px">
    "Sovereign Vector" is Vision-layer language; joining is a real, ordinary thing — contribute,
    connect, or support, through the channels below. Nothing here signs you up for anything, and
    nothing moves without your say.
  </p>
</section>

<section class="section node" style="--node:var(--blue)">
  <h2>Ways to take part</h2>
  <div class="cards">
    {#each data.ways as way (way.href)}
      <a class="card" href={way.href} style="--st:{way.st}" target="_blank" rel="noopener noreferrer">
        <h3>{way.title}</h3>
        <p>{way.body}</p>
        <span class="status">{way.cta}</span>
      </a>
    {/each}
  </div>
</section>

<section class="section node" style="--node:var(--gold)">
  <h2>Sovereign Vectors</h2>
  <p>
    The people whose work is woven in — credited by their own handle, for what they actually made.
    Listed with permission; being here implies no affiliation or endorsement, only credit.
  </p>
  <div class="cards">
    {#each data.vectors as v (v.handle)}
      <a class="card" href={v.href} style="--st:{v.st}" target="_blank" rel="noopener noreferrer">
        <h3>{v.handle}</h3>
        <p>{v.work}</p>
      </a>
    {/each}
  </div>
  <p style="font-size:.95rem;opacity:.75;margin-top:22px">
    Want your name here? Add something to the weave and say so — you're credited by the handle you
    choose, for the work you made, and only if you want to be listed.
  </p>
</section>

<Footer />
