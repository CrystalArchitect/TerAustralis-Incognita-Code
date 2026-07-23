<script>
  /** Streaming chat with the local model via the Flask API. */
  import { voiceSupported, listVoices, onVoicesChanged, speak, stopSpeaking } from './voice.js';

  let { name = 'Lumina', onStateChange = () => {} } = $props();

  let messages = $state([]);
  let draft = $state('');
  let busy = $state(false);
  let logEl;
  let controller = null;

  let voiceOn = $state(localStorage.getItem('lumina.voice') === 'on');
  let voiceName = $state(localStorage.getItem('lumina.voiceName') || '');
  let voices = $state(listVoices());
  onVoicesChanged(() => (voices = listVoices()));
  let spoken = 0; // chars of the current reply already sent to speech

  function toggleVoice() {
    voiceOn = !voiceOn;
    localStorage.setItem('lumina.voice', voiceOn ? 'on' : 'off');
    if (!voiceOn) stopSpeaking();
  }

  function pickVoice(e) {
    voiceName = e.target.value;
    localStorage.setItem('lumina.voiceName', voiceName);
  }

  // Speak complete sentences as they stream in; on final, speak the remainder.
  function speakNew(text, final = false) {
    if (!voiceOn) return;
    const pending = text.slice(spoken);
    if (final) {
      if (pending.trim()) speak(pending, voiceName);
      spoken = text.length;
      return;
    }
    const re = /[.!?…]+["')”]?(\s|$)/g;
    let end = -1;
    let m;
    while ((m = re.exec(pending))) end = m.index + m[0].length;
    if (end > 0) {
      speak(pending.slice(0, end), voiceName);
      spoken += end;
    }
  }

  function scrollLog() {
    if (logEl) logEl.scrollTop = logEl.scrollHeight;
  }

  function stop() {
    if (controller) controller.abort();
    stopSpeaking();
  }

  async function send(event) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || busy) return;
    draft = '';
    messages.push({ who: 'you', text });
    const reply = $state({ who: 'her', text: '' });
    messages.push(reply);
    busy = true;
    onStateChange('thinking');
    controller = new AbortController();
    stopSpeaking();
    spoken = 0;
    setTimeout(scrollLog, 0);
    try {
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
        signal: controller.signal
      });
      if (!res.ok || !res.body) throw new Error('offline');
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let first = true;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (first) {
          first = false;
          onStateChange('speaking');
        }
        reply.text += dec.decode(value, { stream: true });
        speakNew(reply.text);
        scrollLog();
      }
      speakNew(reply.text, true);
    } catch (err) {
      if (err.name === 'AbortError') {
        reply.text += reply.text ? ' — [stopped]' : '[stopped]';
      } else {
        reply.text =
          '[I can\u2019t reach my local brain. Is server.py running, and is Ollama awake?]';
      }
    }
    busy = false;
    controller = null;
    onStateChange('idle');
  }

  function onKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      // CJK IME safety: don't submit mid-composition
      if (e.isComposing || e.keyCode === 229) return;
      e.preventDefault();
      send(e);
    }
  }
</script>

<section class="chat" aria-label="Conversation">
  <div class="log" bind:this={logEl}>
    {#if messages.length === 0}
      <div class="empty">
        <p class="prompt-line">{'>'} say something to wake her</p>
        <p class="hint">She runs entirely on this machine. Nothing you say leaves it.</p>
      </div>
    {/if}
    {#each messages as m, i (i)}
      <div class={`msg ${m.who}`}>
        {#if m.who === 'her'}
          <span class="speaker">{name}</span>
        {/if}
        <p>{m.text}{#if m.who === 'her' && busy && i === messages.length - 1}<span class="caret" aria-hidden="true"></span>{/if}</p>
      </div>
    {/each}
  </div>

  {#if voiceSupported()}
    <div class="voicebar">
      <button
        type="button"
        class="voice"
        class:on={voiceOn}
        onclick={toggleVoice}
        aria-pressed={voiceOn}
      >voice {voiceOn ? 'on' : 'off'}</button>
      {#if voiceOn && voices.length > 0}
        <select value={voiceName} onchange={pickVoice} aria-label="Her voice">
          <option value="">default voice</option>
          {#each voices as v (v.name)}
            <option value={v.name}>{v.name}</option>
          {/each}
        </select>
      {/if}
      {#if voiceOn}
        <span class="voicehint">spoken by this browser — nothing leaves the machine</span>
      {/if}
    </div>
  {/if}

  <form class="composer" onsubmit={send}>
    <textarea
      rows="1"
      placeholder="Say something…"
      bind:value={draft}
      onkeydown={onKeydown}
      aria-label="Your message"
    ></textarea>
    {#if busy}
      <button type="button" class="stop" onclick={stop}>Stop</button>
    {:else}
      <button type="submit" disabled={!draft.trim()}>Send</button>
    {/if}
  </form>
</section>

<style>
  .chat {
    display: flex;
    flex-direction: column;
    min-height: 0;
    flex: 1;
  }

  .log {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .empty {
    margin: auto;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .prompt-line {
    font-family: var(--mono);
    color: var(--green);
    font-size: 0.95rem;
  }
  .hint {
    color: var(--muted);
    font-size: 0.85rem;
  }

  .msg {
    max-width: 68ch;
    padding: 10px 14px;
    border-radius: 12px;
    line-height: 1.55;
    white-space: pre-wrap;
  }
  .msg.you {
    background: #141420;
    align-self: flex-end;
  }
  .msg.her {
    background: var(--panel);
    border: 1px solid var(--line);
    align-self: flex-start;
  }
  .speaker {
    display: block;
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--purple);
    margin-bottom: 4px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .caret {
    display: inline-block;
    width: 8px;
    height: 1em;
    margin-left: 2px;
    vertical-align: text-bottom;
    background: var(--green);
    animation: blink 0.9s steps(1) infinite;
  }
  @keyframes blink {
    50% { opacity: 0; }
  }

  .composer {
    display: flex;
    gap: 10px;
    padding: 14px 20px;
    border-top: 1px solid var(--line);
  }
  textarea {
    flex: 1;
    resize: none;
    background: #0d0d18;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: var(--sans);
    line-height: 1.4;
  }
  textarea:focus {
    outline: 2px solid var(--purple);
    outline-offset: -1px;
  }
  button {
    cursor: pointer;
    background: var(--purple);
    color: #050208;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 18px;
  }
  button:disabled {
    opacity: 0.45;
    cursor: default;
  }
  button.stop {
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    font-weight: 400;
  }

  .voicebar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 20px 0;
  }
  button.voice {
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 400;
    padding: 4px 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  button.voice.on {
    color: var(--green);
    border-color: var(--green);
  }
  .voicebar select {
    background: #0d0d18;
    color: var(--muted);
    border: 1px solid var(--line);
    border-radius: 6px;
    font-family: var(--mono);
    font-size: 0.72rem;
    padding: 4px 6px;
    max-width: 40%;
  }
  .voicehint {
    color: var(--muted);
    font-size: 0.72rem;
  }

  @media (prefers-reduced-motion: reduce) {
    .caret { animation: none; }
  }
</style>
