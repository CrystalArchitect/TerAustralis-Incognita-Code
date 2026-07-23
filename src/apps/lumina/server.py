# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""
Lumina — local API server.

The JSON backend for the Svelte web interface in webapp/. Runs only on
your own machine (bound to 127.0.0.1, never exposed). Shares the same
brain and memory folder as the terminal version (lumina.py), so you
can switch between them freely. Nothing leaves your device.

    pip install -r requirements.txt
    python server.py                    # API at http://127.0.0.1:5000

Then, in another terminal, start the web interface:

    cd webapp && npm install && npm run dev
"""

import argparse
from pathlib import Path

from flask import Flask, Response, jsonify, request

from crystalcore import (Lumina, delete_profile, list_profiles,
                         profile_dir, profile_meta)
from crystalcore import profiles as _profiles


def _profile_of(companion: Lumina) -> str:
    p = Path(companion.memory_dir)
    return p.name if p.parent == Path(_profiles.PROFILES_DIR) else "default"


def create_app(companion: Lumina) -> Flask:
    app = Flask(__name__)
    holder = {"c": companion}  # swapped in place when the profile changes

    @app.after_request
    def allow_local_webapp(resp):
        # The Svelte dev server (vite) runs on another localhost port.
        # Only ever localhost origins — sovereignty means local only.
        origin = request.headers.get("Origin", "")
        if origin.startswith("http://127.0.0.1:") or origin.startswith("http://localhost:"):
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return resp

    @app.route("/api/<path:_any>", methods=["OPTIONS"])
    def preflight(_any):
        return ("", 204)

    @app.get("/api/status")
    def status():
        c = holder["c"]
        return jsonify({
            "name": c.personality.name or "Lumina",
            "avatar": c.personality.avatar,
            "model": c.model,
            "profile": _profile_of(c),
            "human_name": c.personality.human_name,
            "last_seen": c.time_since_last(),
        })

    @app.post("/api/chat/stream")
    def chat_stream():
        message = ((request.get_json(silent=True) or {}).get("message") or "").strip()
        if not message:
            return jsonify({"error": "empty message"}), 400
        return Response(holder["c"].chat_stream(message),
                        mimetype="text/plain; charset=utf-8",
                        headers={"X-Accel-Buffering": "no"})

    @app.get("/api/memories")
    def memories():
        c = holder["c"]
        facts = [{"handle": k, "text": f"{k}: {v['value']}",
                  "tags": v.get("tags") or []}
                 for k, v in c.memory.facts.items()]
        notes = [{"handle": f"n{i}", "text": n["text"],
                  "tags": n.get("tags") or []}
                 for i, n in enumerate(c.memory.notes, 1)]
        reflections = [{"handle": f"r{i}", "text": r["text"], "tags": []}
                       for i, r in enumerate(c.memory.reflections, 1)]
        return jsonify({"facts": facts, "notes": notes,
                        "reflections": reflections})

    @app.post("/api/reflect")
    def reflect():
        return jsonify({"insights": holder["c"].reflect()})

    @app.post("/api/teach")
    def teach():
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        key = (data.get("key") or "").strip()
        if not text:
            return jsonify({"ok": False, "error": "empty"}), 400
        if key:
            holder["c"].remember_fact(key, text)
        else:
            holder["c"].remember(text)
        return jsonify({"ok": True})

    @app.post("/api/forget")
    def forget():
        handle = ((request.get_json(silent=True) or {}).get("handle") or "").strip()
        forgotten = holder["c"].forget(handle)
        return jsonify({"ok": bool(forgotten), "forgotten": forgotten})

    @app.get("/api/profile")
    def profile_get():
        c = holder["c"]
        current = _profile_of(c)
        names = list_profiles()
        if current not in names:
            names = [current] + names
        profiles = []
        for n in names:
            if n == current:
                profiles.append({"profile": n,
                                 "avatar": c.personality.avatar,
                                 "description": c.personality.description,
                                 "name": c.personality.name,
                                 "model": c.model})
            elif n == "default":
                profiles.append({"profile": n, "avatar": "",
                                 "description": "", "name": "", "model": ""})
            else:
                profiles.append(profile_meta(n))
        return jsonify({"current": current, "profiles": profiles})

    @app.post("/api/profile/meta")
    def profile_meta_set():
        data = request.get_json(silent=True) or {}
        c = holder["c"]
        if "avatar" in data:
            c.personality.avatar = str(data["avatar"]).strip()[:8]
        if "description" in data:
            c.personality.description = str(data["description"]).strip()[:200]
        if "model" in data and str(data["model"]).strip():
            c.set_model(str(data["model"]))
        if data.get("choose_name"):
            chosen = c.choose_own_name()
            if not chosen:
                return jsonify({"ok": False,
                                "error": "she couldn't settle on a name — try again"})
            c.save()
            return jsonify({"ok": True, "name": chosen})
        c.save()
        return jsonify({"ok": True})

    @app.post("/api/profile/delete")
    def profile_delete():
        name = ((request.get_json(silent=True) or {}).get("profile") or "").strip()
        if name == _profile_of(holder["c"]):
            return jsonify({"ok": False,
                            "error": "switch away before deleting the active profile"}), 400
        return jsonify({"ok": delete_profile(name)})

    @app.post("/api/profile")
    def profile_switch():
        name = ((request.get_json(silent=True) or {}).get("profile") or "").strip()
        try:
            target = profile_dir(name)
        except ValueError:
            return jsonify({"ok": False, "error": "invalid name"}), 400
        old = holder["c"]
        holder["c"] = Lumina(model=old.model, memory_dir=target,
                                 embed_model=old.embed_model)
        c = holder["c"]
        return jsonify({"ok": True, "profile": _profile_of(c),
                        "name": c.personality.name or "Lumina"})

    return app


def main():
    parser = argparse.ArgumentParser(
        description="Lumina's local API server (127.0.0.1 only).")
    parser.add_argument("--model", default="llama3.1:8b",
                        help="Ollama model tag (same choices as the CLI).")
    parser.add_argument("--memory-dir", default="lumina_memory",
                        help="Her memory folder (shared with the CLI).")
    parser.add_argument("--profile", default="",
                        help="Named profile (separate person, separate memory).")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    if args.profile:
        args.memory_dir = profile_dir(args.profile)

    companion = Lumina(model=args.model, memory_dir=args.memory_dir)
    app = create_app(companion)
    name = companion.personality.name or "Lumina"
    print(f"{name}'s API is at http://127.0.0.1:{args.port}")
    print("Start the web interface with: cd webapp && npm run dev")
    print("Local only — nothing leaves this device. Ctrl+C to say goodnight.")
    # Never bind beyond localhost, never enable the debugger: sovereignty
    # means this server is reachable from this machine alone.
    app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
