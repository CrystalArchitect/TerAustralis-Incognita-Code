<!-- Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita) -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

<script>
  /**
   * Her future senses. Note: her *speaking* voice already works today — toggle
   * "voice" in the chat (on-device speech synthesis). What's still on the roadmap
   * is the other direction: her *hearing* you (microphone) and *seeing* you
   * (webcam). These controls hint at what's coming without pretending it works.
   */
</script>

<div class="senses" aria-label="Upcoming senses">
  <button type="button" disabled title="Soon: speak to her and she'll hear you — microphone stays on this device. (She can already speak back today: turn on 'voice' in the chat.)">
    <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true">
      <rect x="7" y="2.5" width="6" height="10" rx="3" />
      <path d="M4 10 a6 6 0 0 0 12 0" />
      <path d="M10 16 v2" />
    </svg>
    <span>Hearing</span>
    <em>soon</em>
  </button>
  <button type="button" disabled title="Soon: she'll see you through your webcam — sight that never leaves this machine">
    <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true">
      <rect x="2" y="5" width="11" height="10" rx="2" />
      <path d="M13 9 l5 -3 v8 l-5 -3" />
    </svg>
    <span>Sight</span>
    <em>soon</em>
  </button>
  <p class="whisper">
    She can already speak to you — turn on <strong>voice</strong> in the chat. Still
    to come: hearing your voice and seeing your face, both living on this machine alone.
  </p>
</div>

<style>
  .senses {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  button {
    display: flex;
    align-items: center;
    gap: 7px;
    background: transparent;
    border: 1px dashed var(--line);
    border-radius: 999px;
    color: var(--muted);
    padding: 7px 14px;
    font-size: 0.82rem;
    cursor: not-allowed;
  }
  button svg {
    color: var(--purple);
    opacity: 0.8;
  }
  button em {
    font-style: normal;
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--green);
    border: 1px solid rgba(52, 211, 153, 0.3);
    border-radius: 4px;
    padding: 1px 5px;
    letter-spacing: 0.08em;
  }

  .whisper {
    flex-basis: 100%;
    text-align: center;
    color: var(--muted);
    font-size: 0.74rem;
    line-height: 1.5;
    max-width: 34ch;
    margin: 0 auto;
    text-wrap: pretty;
  }
</style>
