# Clementine · Voice

A phone-reachable Clementine you talk to. One static HTML file, no build step,
no server — published with the site at **`/clementine-voice/`**.

Tap the big button, talk, and she answers out loud. Turn on **Hands-free** and
she listens again after each reply, so a conversation costs one tap total
rather than one per turn. Typing is still there, demoted to a button.

It exists because the local Clementine webapp cannot be reached from a phone
with no machine to run it on. That is not a defect in the local app — it is
what local-first means. This shell makes the opposite trade deliberately.

## Where the audio goes

Three paths, three different answers. The page has a **Where audio goes**
button that says this too, because "it's private" would be a claim that is
only true of some of it.

| Part | Where it happens | Leaves the device? |
|---|---|---|
| Clementine speaking | your phone's installed voices | **no** |
| The talk button | your browser's speech recognition | **probably — see below** |
| The keyboard's 🎤 key | iOS system dictation | **no** — never reaches this page |
| Your words → the model | your configured endpoint | **yes**, always |

**Speaking** uses `speechSynthesis` filtered to `localService` voices only —
the same promise `vision/apps/clementine/webapp/src/lib/voice.js` makes. With
no on-device voice she stays silent rather than fall back to a network one.

**The talk button** uses the browser's built-in `SpeechRecognition`. In Chrome
that sends audio to Google. In Safari it is Apple's recogniser, and whether it
runs on-device or on Apple's servers is **not something this page can
determine** — so it is described as leaving the device, rather than assumed
not to. If that matters, use the keyboard key instead: slower, and the one
whose answer is clean.

Both routes end the same way: the transcribed text goes to your endpoint.

## Setup

Tap **Setup** once: an OpenAI-compatible base URL, a key, a model, and a voice.
The key lives in this browser's `localStorage` and goes only to that endpoint —
no server of ours is in the path. `companion.py` already abstracts the same
dialect, so nothing here locks you to a provider.

## Known limits

- **CORS decides whether a provider works.** The page calls the endpoint
  straight from the browser and some providers refuse a web origin. The error
  is shown in full and names CORS, because on a phone that text is the only
  diagnostic there is. A provider that refuses needs a proxy, which needs a
  server, which this deliberately does not have.
- **A key in `localStorage` is only as private as the phone.**
- **Untested on real iOS.** Verified in mobile-emulated Chromium with a mock
  recogniser and a stub endpoint — there is no iPhone in the build container.
  Safari differs from Chromium in exactly the places that matter here (speech
  permissions, voice availability, autoplay rules). Treat the behaviour as
  expected, not confirmed, until it has been tapped once.
- Hands-free turns itself off when a request fails, so a broken endpoint
  cannot put it in a listen/fail loop.
- No streaming: a reply arrives complete, then is spoken.

## Verified

In a 390×844 mobile context, against a stub OpenAI-compatible endpoint and a
mock recogniser driving the real code path:

- tap → recogniser starts, button shows a live state
- interim words appear greyed, are replaced by the final transcript, and the
  final result auto-sends without another tap
- **hands-free relistens after the reply finishes speaking** (recogniser start
  count rises across a turn on its own)
- microphone-denied produces named guidance (iOS Settings → Safari →
  Microphone) and switches hands-free off rather than looping
- a reply containing `<img src=x onerror=…>` renders as literal text — no
  element created, no script run
- no horizontal overflow; header and talk button stay in view; only the
  transcript scrolls
