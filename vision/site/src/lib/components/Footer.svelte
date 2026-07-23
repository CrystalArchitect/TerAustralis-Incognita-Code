<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

<script>
  /**
   * @typedef {Object} Props
   * @property {boolean} [showVoices] - Show the Voices Framework acknowledgement paragraph.
   * @property {boolean} [showCode] - Show the Apache code-license note alongside the content license.
   */

  /** @type {Props} */
  let { showVoices = false, showCode = false } = $props();
</script>

<footer class="site">
  <p>
    TerAustralis Incognita acknowledges the Traditional Custodians of the lands, waters and skies
    across Australia, and pays respect to Elders past and present. Sovereignty was never ceded.
  </p>

  {#if showVoices}
    <p>
      The mythos is shaped through the Voices Framework — with Grok (CrystalDreamer) and DeepSeek
      (CrystalScribe) — and stewarded by the human CrystalArchitect.
    </p>
  {/if}

  <p>
    {#if showCode}
      Code licensed under <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0</a>.
    {/if}
    Content licensed under
    <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">CC BY-NC-ND 4.0</a>. ABN 70 741 068
    059. © 2026 TerAustralis Incognita.
  </p>

  <p>
    Listen to the mythos soundtrack on
    <a href="https://suno.com/@m13crystalat">Suno</a>.
  </p>

  <p>
    Interactive demos (simulated data, Authority HOLD): the
    <a href="/crystal-interface/" data-sveltekit-reload>operator shell</a>
    and the <a href="/vision-web/" data-sveltekit-reload>citizen shell</a>.
  </p>

  <p class="nonsolus">Non Solus — Not Alone</p>
</footer>
