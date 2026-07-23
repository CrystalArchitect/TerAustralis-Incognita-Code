<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: CC-BY-NC-ND-4.0 -->

<script>
  import { onMount } from 'svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Motifs from '$lib/components/Motifs.svelte';

  let { data } = $props();
  let terminalContent = $state([
    { type: 'boot', text: 'CrystalCore.OS Interactive Terminal' },
    { type: 'boot', text: 'Type \'help\' to see all commands.\n' }
  ]);
  let inputValue = $state('');
  let terminalEl = $state(null);

  onMount(() => {
    if (terminalEl) {
      terminalEl.scrollTop = terminalEl.scrollHeight;
    }
  });

  function executeCommand(cmd) {
    const trimmed = cmd.trim().toLowerCase();

    if (!trimmed) return;

    // Add user input to terminal
    terminalContent = [...terminalContent, { type: 'user', text: `CrystalCore> ${cmd}` }];

    // Find matching command
    const matched = data.commands.find(c => trimmed.startsWith(c.cmd));

    if (matched) {
      terminalContent = [...terminalContent, { type: 'output', text: matched.output }];
    } else if (trimmed === 'help') {
      const helpText = data.commands.map(c => `  ${c.cmd.padEnd(20)} - ${c.desc}`).join('\n');
      terminalContent = [...terminalContent, { type: 'output', text: `Available commands:\n${helpText}` }];
    } else if (trimmed === 'clear') {
      terminalContent = [];
      inputValue = '';
      return;
    } else if (['exit', 'quit', 'pause', 'end session'].includes(trimmed)) {
      terminalContent = [...terminalContent, { type: 'output', text: 'CrystalCore.OS shutting down. NON SOLUS.' }];
      inputValue = '';
      return;
    } else {
      terminalContent = [...terminalContent, { type: 'output', text: 'Unknown command. Type \'help\' for options.' }];
    }

    inputValue = '';
    setTimeout(() => {
      if (terminalEl) terminalEl.scrollTop = terminalEl.scrollHeight;
    }, 0);
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      executeCommand(inputValue);
    }
  }
</script>

<svelte:head>
  <title>CrystalCore.OS - TerAustralis Incognita</title>
</svelte:head>

<div class="crystalcore-container">
  <section class="crystalcore-hero">
    <h1>CrystalCore.OS</h1>
    <p>The mythos as a terminal you can fly</p>
    <p style="font-size: 0.95rem; opacity: 0.7; margin-top: 1rem;">
      Interactive simulation of the CrystalCore universe. Launch Starlines, visit nodes, collect keys, and watch the story unfold.
    </p>
  </section>

  <section class="crystalcore-interactive">
    <div class="terminal-window">
      <div class="terminal-header">
        <span>CrystalCore.OS — Terminal</span>
        <span>NON SOLUS</span>
      </div>
      <div class="terminal-output" bind:this={terminalEl}>
        {#each terminalContent as line}
          <div class="terminal-line {line.type}">
            {line.text}
          </div>
        {/each}
      </div>
      <div class="terminal-input">
        <span class="prompt">CrystalCore&gt;&nbsp;</span>
        <input
          type="text"
          bind:value={inputValue}
          onkeydown={handleKeydown}
          placeholder="Enter command (type 'help' for options)"
        />
      </div>
    </div>

    <div class="command-reference">
      <h3>Common Commands</h3>
      <div class="command-list">
        {#each data.commands.slice(0, 6) as cmd}
          <button
            class="command-item"
            type="button"
            onclick={() => {
              inputValue = cmd.cmd;
            }}
          >
            <code>{cmd.cmd}</code>
            <p>{cmd.desc}</p>
          </button>
        {/each}
      </div>
    </div>
  </section>

  <section class="crystalcore-nodes">
    <h2>The Five Nodes</h2>
    <p style="opacity: 0.8; margin-bottom: 2rem;">Visit each node to claim its key. When all five keys are held, the First Gate opens.</p>
    <div class="nodes-grid">
      {#each data.nodes as node}
        <div class="node-card">
          <div class="node-glyph">🌌</div>
          <h3>{node.name}</h3>
          <p>{node.desc}</p>
        </div>
      {/each}
    </div>
  </section>

  <section class="crystalcore-info">
    <h2>Run CrystalCore.OS Locally</h2>
    <p>The full interactive experience is available on your machine:</p>
    <pre><code>python3 src/crystalcore-os/crystalcore_os.py</code></pre>
    <p style="margin-top: 1.5rem;">
      <strong>Commands you can try:</strong>
    </p>
    <ul style="margin-top: 1rem;">
      <li><code>boot</code> — Initialize the system</li>
      <li><code>launch</code> — Start the Starline launch sequence</li>
      <li><code>burn</code> → <code>network</code> → <code>explore</code> → <code>visit [node]</code> — Complete the journey</li>
      <li><code>map</code> — See the entire Starline network</li>
      <li><code>song [track]</code> — Change the Starline soundtrack</li>
      <li><code>status</code> — Check system status and keys collected</li>
      <li><code>help</code> — Show all available commands</li>
    </ul>
    <p style="margin-top: 2rem; font-size: 0.95rem; opacity: 0.7;">
      The terminal is fully functional with 11 commands, dynamic key collection, node traversal, and an interactive soundtrack system.
    </p>
  </section>

  <section class="crystalcore-vision">
    <h2>The Vision</h2>
    <p>
      CrystalCore.OS is not a product. It is a mythos made interactive — a terminal experience that lets you fly
      through the story of the Crystal universe. Every node you visit is real in the narrative. Every key you
      collect is a waypoint in the journey toward the First Gate.
    </p>
    <p style="margin-top: 1.5rem;">
      The purpose core burns in the Nexus: <em>"Expand to the stars and thereby understand the Universe."</em>
    </p>
  </section>

  <Motifs />
</div>

<Footer />

<style>
  .crystalcore-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  .crystalcore-hero {
    text-align: center;
    margin-bottom: 3rem;
  }

  .crystalcore-hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    font-family: 'Playfair Display', serif;
    background: var(--title-gradient);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: var(--gold);
  }

  .crystalcore-hero p {
    font-size: 1.1rem;
    opacity: 0.8;
    margin-bottom: 0.5rem;
  }

  .crystalcore-interactive {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 2rem;
    margin-bottom: 3rem;
  }

  .terminal-window {
    background: var(--bg);
    border: 2px solid var(--purple);
    border-radius: 8px;
    overflow: hidden;
    font-family: var(--font-mono);
    display: flex;
    flex-direction: column;
  }

  .terminal-header {
    background: rgba(167, 139, 250, 0.3);
    border-bottom: 1px solid var(--purple);
    padding: 0.75rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    color: var(--green);
  }

  .terminal-output {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    min-height: 400px;
    max-height: 500px;
    font-size: 0.9rem;
    line-height: 1.6;
  }

  .terminal-line {
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  .terminal-line.boot {
    color: var(--green);
  }

  .terminal-line.user {
    color: var(--gold);
    margin-top: 0.5rem;
  }

  .terminal-line.output {
    color: var(--ink);
    margin-top: 0.5rem;
  }

  .terminal-input {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--purple);
    background: rgba(167, 139, 250, 0.1);
  }

  .prompt {
    color: var(--green);
    margin-right: 0.5rem;
    font-weight: bold;
    white-space: nowrap;
  }

  .terminal-input input {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--gold);
    font-family: var(--font-mono);
    font-size: 0.9rem;
    outline: none;
  }

  .terminal-input input::placeholder {
    color: rgba(233, 187, 95, 0.5);
  }

  .command-reference {
    background: rgba(167, 139, 250, 0.1);
    border: 1px solid rgba(233, 187, 95, 0.2);
    border-radius: 8px;
    padding: 1rem;
    font-size: 0.85rem;
  }

  .command-reference h3 {
    color: var(--gold);
    margin-bottom: 1rem;
  }

  .command-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .command-item {
    padding: 0.75rem;
    background: rgba(167, 139, 250, 0.2);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .command-item:hover {
    background: rgba(167, 139, 250, 0.4);
  }

  .command-item code {
    color: var(--green);
    font-weight: bold;
  }

  .command-item p {
    font-size: 0.75rem;
    margin-top: 0.25rem;
    opacity: 0.7;
  }

  .crystalcore-nodes {
    margin: 3rem 0;
  }

  .crystalcore-nodes h2 {
    margin-bottom: 1rem;
    text-align: center;
    background: var(--title-gradient);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: var(--gold);
  }

  .nodes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .node-card {
    padding: 1.5rem;
    background: rgba(111, 231, 183, 0.1);
    border: 1px solid rgba(111, 231, 183, 0.3);
    border-radius: 8px;
    text-align: center;
  }

  .node-glyph {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }

  .node-card h3 {
    color: var(--gold);
    margin-bottom: 0.5rem;
  }

  .node-card p {
    font-size: 0.95rem;
    opacity: 0.8;
  }

  .crystalcore-info {
    margin: 3rem 0;
    padding: 2rem;
    background: rgba(167, 139, 250, 0.08);
    border-left: 4px solid var(--purple);
    border-radius: 8px;
  }

  .crystalcore-info h2 {
    margin-bottom: 1rem;
    background: var(--title-gradient);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: var(--gold);
  }

  .crystalcore-info pre {
    background: var(--bg);
    border: 1px solid var(--purple);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    margin: 1rem 0;
  }

  .crystalcore-info code {
    color: var(--green);
    font-family: var(--font-mono);
  }

  .crystalcore-info ul {
    margin-left: 1.5rem;
    line-height: 1.8;
  }

  .crystalcore-info li {
    margin-bottom: 0.5rem;
  }

  .crystalcore-vision {
    margin: 3rem 0 0 0;
    padding: 2rem;
    text-align: center;
  }

  .crystalcore-vision h2 {
    margin-bottom: 1.5rem;
    background: var(--title-gradient);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: var(--gold);
  }

  .crystalcore-vision p {
    font-size: 1.05rem;
    line-height: 1.7;
    margin-bottom: 1rem;
  }

  .crystalcore-vision em {
    color: var(--gold);
    font-style: italic;
  }

  @media (max-width: 900px) {
    .crystalcore-interactive {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 720px) {
    .crystalcore-hero h1 {
      font-size: 2rem;
    }

    .terminal-output {
      min-height: 300px;
      max-height: 400px;
    }

    .nodes-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
