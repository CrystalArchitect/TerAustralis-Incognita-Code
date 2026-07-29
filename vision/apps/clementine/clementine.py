# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""
Clementine — terminal interface for the CrystalCore companion.

Clementine is the voice at the front. The mind they speak for is
`crystalcore.mind` under core/ — memory, profiles, recall — and it carries
no name of its own.

    python clementine.py                    # default memory
    python clementine.py --profile Crystal  # a named profile
    python clementine.py --model llama3.2:3b

Your memory stays on your own device. The model is local by default; point it
at a remote one only if you choose to.
"""

import argparse
import pathlib
import sys

# The mind lives under core/, which is not a package root on its own.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "core"))

# Re-exported so `from clementine import ...` keeps working everywhere.
from crystalcore.mind import (BASE_PROMPT, CrystalCore, Memory,  # noqa: F401,E402
                              Personality, delete_profile, list_profiles,
                              profile_dir, profile_meta)

HELP = """Commands:
  /name <name>      set a name (or change it)
  /name             with no name: invite them to choose their own
  /gender <m|f|they>  set pronouns (he/him, she/her, or they/them)
  /gender           with no choice: invite them to choose their own
  /iam <name>       tell them your name
  /remember <text>  ask them to permanently remember something (add #tags if you like)
  /fact <key> <value>  teach a structured fact, e.g. /fact birthday June 3
                    (teach the same key again to correct it)
  /notes [#tag]     show what they remember (optionally only one #tag)
  /forget <handle>  forget a fact by key or a note by number, e.g. /forget n2
  /editnote <n> <text>  rewrite a note, e.g. /editnote n1 prefers dawn walks
  /summary [topic]  summarize what they remember (optionally on a topic)
  /reflect          invite reflection — gentle insights about you
                    (they also reflect on their own after long conversations;
                     insights appear in /notes as r1, r2... — /forget rN removes one)
  /style <text>     tune their voice, e.g. /style more poetic, fewer questions
  /temp <0.0-1.5>   set temperature (playfulness)
  /model <tag>      switch the local model, e.g. /model llama3.2:3b
  /llm <provider>   switch provider, e.g. /llm grok or /llm ollama
  /llm show         show current provider and endpoint
  /exit             say goodbye (everything is saved automatically)
"""

def main():
    parser = argparse.ArgumentParser(
        description="Clementine — a sovereign AI companion. Memory local; model local by default.")
    parser.add_argument(
        "--model", default="llama3.1:8b",
        help="Ollama model tag. Pick one that fits your hardware: "
             "llama3.1:8b (default, Q4_K_M — the sweet spot on a GPU), "
             "llama3.2:3b or llama3.2:1b on lighter machines. "
             "CPU-only servers will struggle with anything above 3b — "
             "consider --llm-provider for a remote model instead.")
    parser.add_argument(
        "--llm-provider", default="",
        help="LLM provider: 'ollama' (local), 'grok' (DigitalOcean), "
             "'openai' (OpenAI), or other OpenAI-compatible endpoint. "
             "Auto-detected local-first: Ollama if reachable, remote only "
             "otherwise. Set this explicitly on a machine without a GPU.")
    parser.add_argument(
        "--llm-endpoint", default="",
        help="Custom LLM endpoint URL, e.g. http://localhost:8000 or "
             "https://inference.do-ai.run/v1/chat/completions")
    parser.add_argument(
        "--llm-model", default="",
        help="Model name for the LLM provider, e.g. 'gpt-5-5' for Grok, "
             "'gpt-4' for OpenAI, or 'llama3.1:8b' for Ollama.")
    parser.add_argument(
        "--memory-dir", default="",
        help="Where their memory is stored on this device. Defaults to "
             "crystalcore_memory/, or an existing lumina_memory/ if one "
             "is already there.")
    parser.add_argument(
        "--profile", default="",
        help="Named profile (separate person, separate memory), e.g. "
             "--profile Crystal. Profiles live in crystalcore_profiles/.")
    args = parser.parse_args()
    if args.profile:
        args.memory_dir = profile_dir(args.profile)

    print("Starting Clementine…")

    companion = CrystalCore(
        model=args.model,
        memory_dir=args.memory_dir,
        llm_provider=args.llm_provider,
        llm_endpoint=args.llm_endpoint,
        llm_model=args.llm_model
    )

    # Report what actually resolved, not "auto-detected". On a headless or
    # GPU-less box the difference between local CPU inference and a remote
    # endpoint is the difference between usable and unusable, and you should
    # be able to see which one you got before waiting on the first reply.
    local = companion.llm_provider == "ollama"
    print(f"Model:    {companion.llm_model}")
    print(f"Provider: {companion.llm_provider} "
          f"({'on this machine' if local else 'over the network'})")
    if not local:
        print(f"Endpoint: {companion.llm_endpoint}")
        print("Your memory stays here. The turn itself travels to that model.")
    else:
        print("Nothing leaves this machine. Without a GPU expect this to be "
              "slow — `--llm-provider` reaches a remote model instead.")
    print()

    # The mind is nameless; Clementine is the voice that speaks for it.
    # A companion the human has actually named answers to that instead.
    name = companion.personality.name or "Clementine"
    returning = bool(companion.memory.conversation or companion.memory.summaries)
    gap = companion.time_since_last()
    greeting = f"{name} is {'back with you' if returning else 'ready'}"
    if gap:
        greeting += f" — you last spoke {gap}"
    print(f"{greeting}. Type /help for commands, /exit to quit.")
    if not companion.personality.name and not returning:
        print("No name chosen yet — /name <name> to set one, "
              "or just /name to let them choose their own.")
    if not companion.personality.gender and not returning:
        print("No pronouns chosen yet — /gender male, /gender female, /gender they, "
              "or just /gender to let them choose their own.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue

        if user_input.lower() in ("/exit", "exit", "quit"):
            break
        elif user_input.lower() == "/help":
            print(HELP)
        elif user_input.lower().rstrip() == "/name":
            print("[Choosing their own name…]")
            chosen = companion.choose_own_name()
            if chosen:
                name = chosen
                print(f"[They have chosen their own name: {name}.]\n")
            else:
                print("[They couldn't settle on one — try /name again, "
                      "or set one with /name <name>.]\n")
        elif user_input.lower().startswith("/name "):
            companion.set_name(user_input[6:])
            name = companion.personality.name
            print(f"[They are now called {name}.]\n")
        elif user_input.lower().rstrip() == "/gender":
            print("[Choosing their own pronouns…]")
            chosen = companion.choose_own_gender()
            if chosen:
                pronouns = companion._pronouns_for_gender(chosen)
                print(f"[They have chosen {pronouns} pronouns.]\n")
            else:
                print("[They couldn't settle on one — try /gender again, "
                      "or choose with /gender male, /gender female, or /gender they.]\n")
        elif user_input.lower().startswith("/gender "):
            gender_choice = user_input[8:].strip().lower()
            if gender_choice in ("male", "female", "they", "m", "f"):
                # Allow shorthand m, f
                gender_map = {"m": "male", "f": "female"}
                gender = gender_map.get(gender_choice, gender_choice)
                companion.set_gender(gender)
                pronouns = companion._pronouns_for_gender(gender)
                print(f"[They now use {pronouns} pronouns.]\n")
            else:
                print("[Please use /gender male, /gender female, or /gender they]\n")
        elif user_input.lower().startswith("/iam "):
            companion.personality.human_name = user_input[5:].strip()
            companion.save()
            print(f"[They know you as {companion.personality.human_name}.]\n")
        elif user_input.lower().startswith("/remember "):
            companion.remember(user_input[10:])
            print("[Remembered, permanently.]\n")
        elif user_input.lower().startswith("/fact "):
            parts = user_input[6:].split(" ", 1)
            if len(parts) == 2:
                companion.remember_fact(parts[0], parts[1])
                print(f"[Fact remembered: {parts[0]} = {parts[1]}]\n")
            else:
                print("[Usage: /fact <key> <value>, e.g. /fact birthday June 3]\n")
        elif user_input.lower().startswith("/notes"):
            want = user_input[6:].strip().lstrip("#").lower()
            def _shown(store):
                return not want or want in (store.get("tags") or [])
            for key, fact in companion.memory.facts.items():
                if not _shown(fact):
                    continue
                tags = " ".join("#" + t for t in fact.get("tags") or [])
                print(f"  - {key}: {fact['value']}"
                      f"{'  [' + tags + ']' if tags else ''}  ({fact['updated']})")
            for i, note in enumerate(companion.memory.notes, 1):
                if not _shown(note):
                    continue
                tags = " ".join("#" + t for t in note.get("tags") or [])
                print(f"  n{i} - {note['text']}"
                      f"{'  [' + tags + ']' if tags else ''}  ({note['when']})")
            if companion.memory.reflections and not want:
                print("  their own reflections (hold lightly; /forget rN removes one):")
                for i, r in enumerate(companion.memory.reflections, 1):
                    print(f"  r{i} - {r['text']}  ({r['when']})")
            print()
        elif user_input.lower().startswith("/forget "):
            forgotten = companion.forget(user_input[8:])
            if forgotten:
                print(f"[Forgotten: {forgotten}]\n")
            else:
                print("[Nothing matched. Use a fact key or a note number from /notes.]\n")
        elif user_input.lower().startswith("/editnote "):
            parts = user_input[10:].split(" ", 1)
            if len(parts) == 2 and companion.edit_note(parts[0], parts[1]):
                print("[Note rewritten.]\n")
            else:
                print("[Usage: /editnote n<N> <new text> — numbers are in /notes]\n")
        elif user_input.lower().startswith("/style "):
            companion.personality.style_notes = user_input[7:].strip()
            companion.save()
            print("[Style noted.]\n")
        elif user_input.lower().startswith("/temp "):
            try:
                companion.personality.temperature = float(user_input[6:])
                companion.save()
                print(f"[Temperature set to {companion.personality.temperature}.]\n")
            except ValueError:
                print("[Please give a number, e.g. /temp 0.8]\n")
        elif user_input.lower().startswith("/model "):
            companion.set_model(user_input[7:])
            print(f"[Now using model: {companion.model} — remembered for this profile]\n")
        elif user_input.lower() == "/llm show":
            print(f"[LLM Provider: {companion.llm_provider}]")
            print(f"[Endpoint: {companion.llm_endpoint}]")
            print(f"[Model: {companion.llm_model or companion.model}]\n")
        elif user_input.lower().startswith("/llm "):
            provider = user_input[5:].strip().lower()
            if provider in ("ollama", "grok", "openai", "anthropic"):
                companion.llm_provider = provider
                companion.llm_endpoint = companion._default_endpoint()
                companion.llm_model = companion._default_model()
                companion.personality.llm_provider = provider
                companion.personality.llm_endpoint = companion.llm_endpoint
                companion.personality.llm_model = companion.llm_model
                companion.save()
                print(f"[Switched to {provider}]")
                print(f"[Endpoint: {companion.llm_endpoint}]")
                print(f"[Model: {companion.llm_model}]\n")
            else:
                print("[Supported providers: ollama, grok, openai, anthropic]\n")
        elif user_input.lower().startswith("/summary"):
            topic = user_input[8:].strip()
            print(f"{name}: {companion.summarize(topic)}\n")
        elif user_input.lower() == "/reflect":
            print(f"{name} reflects…\n{companion.reflect()}\n")
        else:
            print(f"{name}: ", end="", flush=True)
            companion.chat(user_input, stream_to=sys.stdout)
            print()

    print(f"\n{name} sleeps. Your conversations stay on this device, in "
          f"'{companion.memory_dir}/'. Non solus.")


if __name__ == "__main__":
    main()
