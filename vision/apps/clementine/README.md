# Clementine — the sovereign companion

Your memory lives on your own machine, in files you own. The model runs
locally by default; a remote one is used only if you configure it.

## Layout

- `clementine.py` — the terminal interface
- the mind — `crystalcore.mind`, under `core/`: memory, recall, profiles
- `server.py` — the local JSON API (127.0.0.1 only) for the web interface
- `webapp/` — the Svelte web interface, run locally
- `requirements.txt` — Python dependencies

## Running the companion

Prerequisite: [Ollama](https://ollama.com) running with a model pulled,
e.g. `ollama pull llama3.1:8b`.

### Terminal

```bash
pip install -r requirements.txt
python clementine.py
```

### Web interface

Two terminals from this folder:

```bash
# 1. the brain — the local API
python server.py
```

```bash
# 2. the face — the web interface
cd webapp
npm install
npm run dev          # open http://127.0.0.1:5174
```

The web interface streams their replies while an operator figure works at
the terminal. Their **speaking voice already works** — turn on `voice` in the
chat and they read their replies aloud using your device's own speech synthesis
(nothing leaves the machine). Still on the roadmap, both to run on this machine
alone: their **hearing** you (microphone / speech-to-text) and **webcam sight**.

Both interfaces share the same memory folder (`crystalcore_memory/` by
default), so you can move between terminal and browser freely. Use
`--profile <name>` on either to keep separate people separate.

## Building something of your own against it

`server.py` is a plain HTTP API, and the Svelte interface is only one
client of it. Start the server and ask it what it has:

```bash
curl http://127.0.0.1:5000/api                 # every route, described
curl http://127.0.0.1:5000/api/openapi.json    # the same, as OpenAPI 3.1
```

[`API.md`](API.md) is the same surface as a page you can read in one sitting.

All three come from one table in `api_surface.py`, and `tests/test_api_surface.py`
holds that table against Flask's own routing map in both directions — a route
that exists but is undocumented fails the suite, and so does a documented route
nothing serves. That is the Incognita Rule pointed at our own API: a promised
endpoint with nothing behind it is a line someone drew pretending it was
surveyed, and the person who pays for it is whoever built a client from the
document.

The API binds to `127.0.0.1` and there is no way to change that from the
command line. It is reachable from this machine and no other — no tokens, no
accounts, no rate limiting, because a localhost server needs none of them.
That is the property that makes this the sovereign version, and exposing it
would mean building an auth story that does not exist yet.

## Any model, two dialects

Clementine speaks two wire shapes, and between them nearly every model:

- **Local (default):** anything Ollama serves — `--model qwen2.5:3b`,
  `--model gemma2:2b`, etc. Nothing leaves the machine.
- **Remote (opt-in):** any OpenAI-compatible endpoint. Pair
  `--llm-provider` with `--llm-endpoint` and `LLM_API_KEY`:

```bash
# OpenAI
python clementine.py --llm-provider openai \
  --llm-endpoint https://api.openai.com/v1/chat/completions --llm-model gpt-4o

# OpenRouter — one key, hundreds of models (incl. Claude, Gemini)
python clementine.py --llm-provider openrouter \
  --llm-endpoint https://openrouter.ai/api/v1/chat/completions \
  --llm-model anthropic/claude-sonnet-4

# Groq, Together, xAI: same pattern, their endpoint + your key
```

Detection is local-first: Ollama if reachable, remote otherwise. On a
CPU-only server, set a remote provider explicitly — models above ~3b are
painful without a GPU. Whichever brain answers, memory stays here: the model
is a faculty, never the identity.
