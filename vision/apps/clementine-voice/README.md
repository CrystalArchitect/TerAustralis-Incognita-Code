# Clementine · Voice

A phone-reachable Clementine. One static HTML file, no build step, no server —
published with the site at **`/clementine-voice/`**.

It exists because the local Clementine webapp cannot be reached from a phone
with no machine to run it on. That is not a defect in the local app: it is what
local-first means. This shell makes the opposite trade deliberately, and says
so on its own front page rather than in a footnote.

## What runs where

| Part | Where it runs | Leaves the device? |
|---|---|---|
| Speaking (TTS) | your phone's installed voices | **no** |
| Listening (STT) | the iOS keyboard's dictation key | **no** — never reaches this page |
| The model | whatever endpoint you configure | **yes** — your text is sent there |
| Your API key | this browser's `localStorage` | only to that endpoint |

There is no server of ours in the path. The page calls your endpoint directly.

## Voice

**Speaking** uses `speechSynthesis`, filtered to `localService` voices only —
the same promise `vision/apps/clementine/webapp/src/lib/voice.js` makes. If a
device has no on-device voice, it stays silent rather than fall back to a
network voice and quietly break that.

**Listening** needs no code and no API. The microphone key on the iOS keyboard
dictates into the text field, on-device. That is why there is no record button
here: adding the browser's `SpeechRecognition` API would ship your audio to a
speech server in most browsers, which is exactly what the table above says does
not happen.

iOS will not speak until speech has been started inside a user gesture, so the
first tap primes it with an empty utterance. Without that, the first reply is
silently swallowed.

## Setup

Tap **Setup** once and give it three things: an OpenAI-compatible base URL, a
key, and a model name. Anything speaking that dialect works — the project's own
`companion.py` already abstracts the same way, so nothing here locks you to one
provider.

## Known limits

- **CORS decides whether a provider works.** The page calls the endpoint
  straight from the browser, and some providers refuse requests from a web
  origin. When that happens the error is shown in full with a note naming CORS,
  because on a phone that text is the only diagnostic available. A provider
  that refuses needs a proxy, which would mean a server, which this
  deliberately does not have.
- **A key in `localStorage` is only as private as the device.** Any script on
  this origin could read it; that is the whole origin, so keep the page's
  contents trusted. A shared or public phone is the wrong place for it.
- **Untested on real iOS.** The behaviour above is what the specs and the
  existing `voice.js` imply, verified in mobile-emulated Chromium — not on an
  actual iPhone, because the build container has none. Treat the voice
  behaviour as expected rather than confirmed until it has been tapped once.
- No streaming: a reply appears when it is complete.

## Verified

Against a stub OpenAI-compatible endpoint, in a 390×844 mobile context:
the full turn (auth header, model, message history), key persistence,
key absent from the visible DOM, a model reply containing
`<img src=x onerror=…>` rendered as literal text with no element created and
no script run, the error path naming CORS, no horizontal overflow, and — after
several turns — the header, banner and composer all staying in view with only
the transcript scrolling.
