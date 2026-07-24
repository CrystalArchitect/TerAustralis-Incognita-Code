<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->

<script>
  import Avatar from './lib/Avatar.svelte';
  import Chat from './lib/Chat.svelte';
  import Senses from './lib/Senses.svelte';

  let presence = $state('idle'); // idle | thinking | speaking
  let name = $state('Lumina');
  let model = $state('');
  let profile = $state('');
  let online = $state(null); // null=checking, true, false

  async function loadStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error();
      const data = await res.json();
      name = data.name || 'Lumina';
      model = data.model || '';
      profile = data.profile || '';
      online = true;
    } catch {
      online = false;
    }
  }
  loadStatus();
</script>

<header>
  <div class="who">
    <b>{name}</b>
    <span class="sub">sovereign companion</span>
  </div>
  <div class="status" role="status">
    {#if online === true}
      <span class="chip ok">{model}{profile && profile !== 'default' ? ` · ${profile}` : ''}</span>
    {:else if online === false}
      <span class="chip down" title="Start her with: python server.py">brain offline</span>
      <button class="retry" onclick={loadStatus}>retry</button>
    {:else}
      <span class="chip">waking…</span>
    {/if}
    <span class="chip">local · 127.0.0.1</span>
  </div>
</header>

<main>
  <aside class="presence">
    <Avatar state={presence} {name} />
    <Senses />
  </aside>
  <Chat {name} onStateChange={(s) => (presence = s)} />
</main>

<footer>
  Everything on this page stays on your device. Her memory lives in a local
  folder you own. Non solus.
</footer>

<style>
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 14px 20px;
    border-bottom: 1px solid var(--line);
  }
  .who b {
    color: var(--purple);
    font-size: 1.05rem;
  }
  .who .sub {
    color: var(--muted);
    font-size: 0.85rem;
    margin-left: 8px;
  }
  .status {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .chip {
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--muted);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 3px 10px;
  }
  .chip.ok {
    color: var(--green);
    border-color: rgba(52, 211, 153, 0.3);
  }
  .chip.down {
    color: #f0a5a5;
    border-color: rgba(240, 165, 165, 0.3);
  }
  .retry {
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 999px;
    color: var(--muted);
    font-size: 0.72rem;
    padding: 3px 10px;
    cursor: pointer;
  }

  main {
    flex: 1;
    display: flex;
    min-height: 0;
  }

  .presence {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 20px;
    width: 340px;
    flex-shrink: 0;
    padding: 24px;
    border-right: 1px solid var(--line);
  }

  footer {
    padding: 10px 20px;
    color: var(--muted);
    font-size: 0.78rem;
    border-top: 1px solid var(--line);
  }

  @media (max-width: 760px) {
    main {
      flex-direction: column;
      overflow-y: auto;
    }
    .presence {
      width: 100%;
      border-right: none;
      border-bottom: 1px solid var(--line);
      padding: 16px;
    }
  }
</style>
