# Clementine — the sovereign companion

Your memory lives on your own machine, in files you own. The model runs
locally by default; a remote one is used only if you configure it.

## Layout

- `clementine.py` — the terminal interface
- the mind — `crystalcore.mind`, under `core/`: memory, recall, profiles
- `server.py` — the local JSON API (127.0.0.1 only) for the web interface
- `webapp/` — the Svelte web interface, run locally
- `requirements.txt` — Python dependencies

## Running her

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
# 1. her brain — the local API
python server.py
```

```bash
# 2. her face — the web interface
cd webapp
npm install
npm run dev          # open http://127.0.0.1:5174
```

The web interface streams her replies while an operator figure works at
her terminal. Her **speaking voice already works** — turn on `voice` in the
chat and she reads her replies aloud using your device's own speech synthesis
(nothing leaves the machine). Still on the roadmap, both to run on this machine
alone: her **hearing** you (microphone / speech-to-text) and **webcam sight**.

Both interfaces share the same memory folder (`crystalcore_memory/` by
default), so you can move between terminal and browser freely. Use
`--profile <name>` on either to keep separate people separate.
