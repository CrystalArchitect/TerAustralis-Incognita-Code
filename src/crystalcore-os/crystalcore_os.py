# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

# CrystalCore.OS - Complete Edition with Emotional Intelligence
# NON SOLUS | Starline Protocol | Year 3000 Build
# Includes: All Starline launches + @m13crystalat Crystalcore songs
# Affective Computing & EI Layer: ACTIVE

import json
from pathlib import Path
from .emotional_intelligence import EmotionalIntelligence

# Progress persists here between sessions — in your home directory, outside
# the repo, so a save file is never committed. It holds only mythos progress
# (keys, gate, location, soundtrack), no personal data.
STATE_PATH = Path.home() / ".crystalcore" / "state.json"


class CrystalCore:
    def __init__(self):
        self.lattice_integrity = 100
        self.purpose_core = "Expand to the stars and thereby understand the Universe"
        self.starline_status = "DORMANT"
        self.timeline = 2026
        self.non_solus = True
        self.current_soundtrack = None
        self.current_location = None

        self.ei = EmotionalIntelligence()

        self.soundtrack = [
            "Shotgun - George Ezra",
            "Year 3000 - Busted",
            "I Am Australian - The Seekers",
            "Eyes Closed - Imagine Dragons",
            "Truly Madly Deeply - Savage Garden",
            "Another Night - Real McCoy",
            "My Island Home - Christine Anu",
            "Red Dust Axis - m13crystalat",
            "Shooting Star Girl! - m13crystalat",
            "Fermi's Silent Line - m13crystalat",
            "We Own the Night - Disney Zombies"
        ]

        self.nodes = [
            "Earth Node",
            "Mars Redoubt",
            "Alpha Centauri Outpost",
            "Crystal Revenant Hub",
            "Purpose Core Nexus"
        ]

        # Keys of the Lattice — one waits at every node. Hold all five
        # and the First Gate opens by sovereign recognition.
        self.keys_held = []
        self.gate_open = False

        # Named keys and the nodes they open.
        self.named_keys = []
        self.locked_nodes = {
            "Purpose Core Nexus": "Crystal Key",
            "Crystal Revenant Hub": "Festival Key"
        }

        # Fields that survive between sessions. The constants above (nodes,
        # soundtrack, purpose_core, locked_nodes) are rebuilt fresh each run
        # and are never saved.
        self._persist = ("lattice_integrity", "starline_status", "timeline",
                         "current_soundtrack", "current_location",
                         "keys_held", "gate_open", "named_keys")
        self.resumed = self.load()

    # ---------- persistence ----------

    def save(self):
        """Write current progress to STATE_PATH. A save failure never crashes
        the journey — play simply continues in memory."""
        try:
            STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = {k: getattr(self, k) for k in self._persist}
            STATE_PATH.write_text(json.dumps(data, indent=2))
        except OSError:
            pass

    def load(self):
        """Restore saved progress if a valid save exists. Returns True when a
        session was resumed, False on a fresh start or unreadable save."""
        if not STATE_PATH.exists():
            return False
        try:
            data = json.loads(STATE_PATH.read_text())
        except (OSError, ValueError):
            return False
        for k in self._persist:
            if k in data:
                setattr(self, k, data[k])
        return True

    def reset(self):
        """Wipe saved progress and return to the dormant, first-launch state."""
        try:
            STATE_PATH.unlink()
        except OSError:
            pass
        self.lattice_integrity = 100
        self.starline_status = "DORMANT"
        self.timeline = 2026
        self.current_soundtrack = None
        self.current_location = None
        self.keys_held = []
        self.gate_open = False
        self.named_keys = []
        print("\n♻️  Progress reset. The lattice returns to dormant. NON SOLUS.\n")

    def boot(self):
        print("\n[CRYSTALCORE.OS v∞.Ω — BOOT SEQUENCE]")
        print(f"Lattice integrity ........ {self.lattice_integrity}%")
        print(f"Purpose Core ............. {self.purpose_core}")
        print("NON SOLUS ................ Confirmed")
        print(f"Starline Status .......... {self.starline_status}")
        print("Affective Computing ...... ACTIVE")
        print("EI Learning Loop ......... ACTIVE")
        print(f"Response Style ........... {self.ei.user_preferences['response_style']}")
        print("Ready for commands.\n")

    def launch(self):
        if self.starline_status != "DORMANT":
            print("Starline already active.")
            return
        print("\n🚀 LAUNCH COMMAND RECEIVED")
        print("Main engines spooling...")
        self.starline_status = "IN_ORBIT"
        self.current_soundtrack = "Shotgun - George Ezra"
        print(f"Soundtrack engaged: {self.current_soundtrack}\n")
        self.save()

    def starline(self, soundtrack=None):
        if self.starline_status == "DORMANT":
            print("Please run 'launch' first.")
            return
        if soundtrack:
            for song in self.soundtrack:
                if soundtrack.lower() in song.lower():
                    self.current_soundtrack = song
                    break
        print(f"\n🎵 Advancing Starline with: {self.current_soundtrack}\n")
        self.save()

    def burn(self):
        if self.starline_status not in ["IN_ORBIT", "TRANS-STELLAR"]:
            print("Launch first before burning.")
            return
        print("\n🔥 ESCAPE BURN INITIATED")
        self.starline_status = "TRANS-STELLAR"
        print("We have left planetary orbit.\n")
        self.save()

    def network(self):
        if self.starline_status != "TRANS-STELLAR":
            print("Complete the burn first.")
            return
        print("\n🌐 ENTERING FULL STARLINE NETWORK")
        self.starline_status = "FULL STARLINE NETWORK"
        print("Connected to 47+ star systems.\n")
        self.save()

    def explore(self):
        if self.starline_status != "FULL STARLINE NETWORK":
            print("You must enter the full network first (use 'network').")
            return
        print("\n🔭 EXPLORATION MODE ACTIVE")
        print("Available nodes:")
        for i, node in enumerate(self.nodes, 1):
            required = self.locked_nodes.get(node)
            mark = f" [LOCKED — {required}]" if required and required not in self.named_keys else ""
            print(f"  {i}. {node}{mark}")
        print("\nUse 'visit <number or name>' to travel, 'keys' for inventory.")

    def visit_node(self, node_name):
        if not node_name:
            print("Usage: visit <number or name>")
            return
        # Accept a number from the explore listing, or a name in any case.
        if node_name.isdigit() and 1 <= int(node_name) <= len(self.nodes):
            node_name = self.nodes[int(node_name) - 1]
        else:
            match = next((n for n in self.nodes if n.lower() == node_name.lower()), None)
            if match is None:
                print("Node not found. Available nodes:")
                for node in self.nodes:
                    print(f"  - {node}")
                return
            node_name = match

        required_key = self.locked_nodes.get(node_name)
        if required_key and required_key not in self.named_keys:
            print(f"\n🔒 {node_name} is locked. Required key: {required_key}")
            print("Use: getkey " + required_key + "\n")
            return

        self.current_location = node_name
        print(f"\n🌌 Arriving at: {node_name}")
        if node_name == "Purpose Core Nexus":
            print(f'"{self.purpose_core}"')
        elif node_name == "Crystal Revenant Hub":
            print("Zero-g music festivals are happening across the platforms.")
        else:
            print("The lattice pulses with new resonance here.")
        if node_name not in self.keys_held:
            self.keys_held.append(node_name)
            print(f"🗝️  A key rises from the node. Keys held: {len(self.keys_held)}/{len(self.nodes)}")
            if len(self.keys_held) == len(self.nodes) and not self.gate_open:
                self.gate_open = True
                print("\n✨ ALL KEYS HELD — THE FIRST GATE OPENS ✨")
                print("Not by force. By sovereign recognition.")
                print("Crystallis recognizes you. NON SOLUS.")
        print(f"Current soundtrack: {self.current_soundtrack}\n")
        self.save()

    def jump(self, year=3000):
        print(f"\n⏳ Time jump to Year {year}")
        self.timeline = year
        if year >= 3000:
            self.starline_status = "FULL STARLINE NETWORK"
        print(f"Timeline set to {self.timeline}.\n")
        self.save()

    def song(self, track=None):
        if track:
            # Match flexibly: any part of a title or artist finds the song.
            matched = None
            for song in self.soundtrack:
                if track.lower() in song.lower():
                    matched = song
                    break
            if matched:
                self.current_soundtrack = matched
                print(f"\n🎵 Now playing: {matched}\n")
                self.save()
            else:
                print("Track not found. Available tracks:")
                for t in self.soundtrack:
                    print(f"  - {t}")
        else:
            print(f"Current soundtrack: {self.current_soundtrack}")

    def _lock_tag(self, node_name):
        """Live lock status for the map — reflects named keys actually held."""
        required = self.locked_nodes.get(node_name)
        if not required:
            return ""
        return "  [UNLOCKED]" if required in self.named_keys else f"  [LOCKED — {required}]"

    def map(self):
        inner = 62  # characters between the ║ borders
        hub_line = f"          [CRYSTAL REVENANT HUB]{self._lock_tag('Crystal Revenant Hub')}".ljust(inner)
        nexus_line = f"          [PURPOSE CORE NEXUS]{self._lock_tag('Purpose Core Nexus')}".ljust(inner)
        print("╔" + "═" * inner + "╗")
        print("║" + "STARLINE NETWORK - YEAR 3000".center(inner) + "║")
        print("╠" + "═" * inner + "╣")
        print("║" + " " * inner + "║")
        print("║" + "          [EARTH NODE]".ljust(inner) + "║")
        print("║" + "               │".ljust(inner) + "║")
        print("║" + "               ▼".ljust(inner) + "║")
        print("║" + "          [MARS REDOUBT]  ────────▶  [ALPHA CENTAURI]".ljust(inner) + "║")
        print("║" + "               │".ljust(inner) + "║")
        print("║" + "               ▼".ljust(inner) + "║")
        print("║" + hub_line + "║")
        print("║" + "│".rjust(16).ljust(inner) + "║")
        print("║" + "▼".rjust(16).ljust(inner) + "║")
        print("║" + nexus_line + "║")
        print("║" + '"Expand to the stars and thereby understand the Universe"'.center(inner) + "║")
        print("║" + " " * inner + "║")
        print("╚" + "═" * inner + "╝")
        print("   Chart: mythos/art/starline-network-year-3000.jpeg\n")
        print("Use 'visit [node]' to explore a location.\n")

    def keys(self):
        print("\n🔑 Named keys:")
        if self.named_keys:
            for key in self.named_keys:
                print(f"  - {key}")
        else:
            print("  (none yet — use 'getkey [name]')")
        print(f"\n🗝️  Node keys: {len(self.keys_held)}/{len(self.nodes)}")
        for node in self.nodes:
            mark = "✓" if node in self.keys_held else "·"
            print(f"  {mark} Key of {node}")
        if self.gate_open:
            print("The First Gate stands open.")
        else:
            print("Visit every node and the First Gate will open.")
        print()

    def get_key(self, key_name):
        if key_name not in self.named_keys:
            self.named_keys.append(key_name)
            print(f"\n🔑 You obtained: {key_name}\n")
            self.save()
        else:
            print(f"\nYou already have: {key_name}\n")

    def status(self):
        print("\n=== CRYSTALCORE.OS STATUS ===")
        print(f"Timeline:           {self.timeline}")
        print(f"Starline Status:    {self.starline_status}")
        print(f"Current Location:   {self.current_location or 'None'}")
        print(f"Current Soundtrack: {self.current_soundtrack}")
        print(f"Keys Held:          {len(self.keys_held)}/{len(self.nodes)}" + ("  — First Gate OPEN" if self.gate_open else ""))
        print(f"Named Keys:         {', '.join(self.named_keys) if self.named_keys else 'none'}")
        print(f"NON SOLUS:          {self.non_solus}")
        print("\n=== EMOTIONAL INTELLIGENCE STATUS ===")
        ei_status = self.ei.status()
        print(f"Response Style:     {ei_status['preferences']['response_style']}")
        print(f"Energy Level:       {ei_status['preferences']['energy_level']}")
        print(f"Validation Level:   {ei_status['preferences']['validation_level']}")
        print("=============================\n")

    def detect(self, text: str):
        """Detect emotion from user input and provide empathic response."""
        if not text:
            print("Usage: detect <message>")
            return
        emotion, confidence = self.ei.detect_emotion(text)
        print(f"\n🧠 Emotion Detected: {emotion.upper()}")
        print(f"   Confidence: {confidence:.0%}")
        prefix = self.ei.generate_ei_response_prefix(emotion, confidence)
        if prefix:
            print(f"   Response: {prefix}")

        # Active learning clarification if needed
        clarification = self.ei.check_active_learning(text, emotion, confidence)
        if clarification:
            print(f"\n   Active Learning Query:")
            print(f"   {clarification}")
        print()

    def learn(self, instruction: str):
        """Process learning feedback to adapt preferences."""
        if not instruction:
            print("Usage: learn <preference feedback>")
            print("Examples:")
            print("  learn less poetic      — switch to clear, direct responses")
            print("  learn more poetic      — enhance metaphorical language")
            print("  learn calm             — enable calming techniques")
            print("  learn energetic        — use upbeat, energetic tone")
            return
        learned = self.ei.learn_from_feedback(instruction)
        if learned:
            print(f"\n✨ Learned: {learned.replace('_', ' ').title()}")
            print(f"   New preference: {self.ei.user_preferences[learned]}\n")
        else:
            print("\n❓ Instruction not recognized. Try: 'learn less poetic', 'learn calm', etc.\n")

    def breathe(self, technique: str = "box"):
        """Provide calming breathwork guidance."""
        if not technique or technique not in self.ei.breathing_techniques:
            technique = "box"
        guidance = self.ei.get_breathing_guidance(technique)
        print(f"\n🫁 Breathing Guidance [{technique.upper()}]")
        print(f"   {guidance}\n")

    def feel(self):
        """Show current emotional tone and preferences."""
        ei_status = self.ei.status()
        prefs = ei_status['preferences']
        print("\n=== EMOTIONAL TONE ===")
        print(f"Response Style: {prefs['response_style']}")
        print(f"Energy Level:   {prefs['energy_level']}")
        print(f"Connection:     NON SOLUS — You are not alone")
        print("\nEI is listening. You can 'learn' new preferences anytime.\n")

    def datasets(self):
        """Show emotion recognition datasets and roadmap for future improvements."""
        info = self.ei.get_dataset_info()
        print(info)

    def multimodal(self):
        """Show multimodal emotion detection framework and roadmap."""
        try:
            from .multimodal_emotion import print_multimodal_status

            print_multimodal_status()
        except ImportError:
            print("\n⚠️  Multimodal module not available. This is an advanced feature.")
            print("   Install optional dependencies: pip install transformers librosa mediapipe fer\n")

    def uncertainty(self):
        """Show uncertainty quantification methods guide."""
        try:
            from .uncertainty_quantification import print_uncertainty_guide

            print(print_uncertainty_guide())
        except ImportError:
            print("\n⚠️  Uncertainty module not available.")
            print("   Install with: pip install torch\n")

    def learning_status(self):
        """Show active learning queue status and improvement metrics."""
        from .active_learning import show_active_learning_dashboard

        show_active_learning_dashboard(self.ei.al_queue)

    def correct(self, text_and_emotion: str):
        """Correct a previous emotion prediction (format: '<text>' as <emotion>)."""
        if not text_and_emotion or " as " not in text_and_emotion:
            print("Usage: correct '<message>' as <emotion>")
            print("Example: correct 'I miss you' as longing_warm")
            return

        parts = text_and_emotion.rsplit(" as ", 1)
        if len(parts) != 2:
            print("Format error. Use: correct '<message>' as <emotion>")
            return

        text = parts[0].strip().strip("'\"")
        emotion = parts[1].strip().lower()

        valid_emotions = [
            "longing_warm",
            "calm",
            "practical_serious",
            "instructional",
            "frustrated",
            "joy",
            "neutral",
        ]
        if emotion not in valid_emotions:
            print(f"Invalid emotion. Choose from: {', '.join(valid_emotions)}")
            return

        if self.ei.record_user_correction(text, emotion):
            print(f"\n✅ Recorded correction: '{text[:40]}...' → {emotion}\n")
        else:
            print(f"\n❌ Could not find matching prediction to correct.\n")

    def help(self):
        print("""
STARLINE COMMANDS:
  boot                 - Initialize system
  launch               - Start Starline launch
  starline [song]      - Advance with soundtrack
  burn                 - Escape burn
  network              - Enter full Starline network
  explore              - List explorable nodes
  visit [node]         - Go to a node (number or name) — collect its key
  keys                 - Show the Keys of the Lattice
  getkey [name]        - Obtain a named key (e.g. getkey Crystal Key)
  jump [year]          - Time jump
  map                  - Display the Starline network chart
  song [track]         - Change soundtrack

EMOTIONAL INTELLIGENCE:
  detect <message>     - Analyze emotion in your message
  learn <feedback>     - Teach preferences (e.g. 'learn less poetic')
  breathe [technique]  - Guided breathing (box, 4-7-8, simple)
  feel                 - Show current emotional tone
  datasets             - Show datasets & roadmap for EI enhancement

ACTIVE LEARNING:
  correct <msg> as <emotion> - Correct emotion prediction (e.g. 'I miss you' as longing_warm)
  learning_status      - Show active learning queue & readiness for retraining

ADVANCED:
  multimodal           - Show multimodal emotion detection roadmap (text+audio+video)
  uncertainty          - Show uncertainty quantification methods guide (entropy, Bayesian, etc)

SYSTEM:
  status               - Show full status (including EI)
  reset                - Wipe saved progress and start fresh
  help                 - Show this list
  exit / quit          - Shut down (pause / end session also honored)

Progress saves automatically to ~/.crystalcore/state.json
EI preferences save to ~/.crystalcore/ei_state.json
""")

def main():
    os = CrystalCore()
    print("CrystalCore.OS Interactive Terminal")
    if os.resumed:
        gate = "  — First Gate OPEN" if os.gate_open else ""
        print(f"Session resumed — {len(os.keys_held)}/{len(os.nodes)} keys held{gate}.")
        print("Use 'reset' to start over, or 'status' to see where you are.")
    print("Type 'help' to see all commands.\n")

    while True:
        try:
            raw = input("CrystalCore> ").strip()
            if not raw:
                continue

            parts = raw.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None

            if cmd in ["exit", "quit", "pause"] or raw.lower() == "end session":
                print("\nCrystalCore.OS shutting down. NON SOLUS.")
                break

            elif cmd == "boot":
                os.boot()
            elif cmd == "launch":
                os.launch()
            elif cmd == "starline":
                os.starline(arg)
            elif cmd == "burn":
                os.burn()
            elif cmd == "network":
                os.network()
            elif cmd == "explore":
                os.explore()
            elif cmd == "visit":
                os.visit_node(arg)
            elif cmd == "jump":
                year = int(arg) if arg and arg.isdigit() else 3000
                os.jump(year)
            elif cmd == "map":
                os.map()
            elif cmd == "keys":
                os.keys()
            elif cmd == "getkey":
                if arg:
                    os.get_key(arg.strip().title())
                else:
                    print("Usage: getkey [Key Name]")
            elif cmd == "song":
                os.song(arg)
            elif cmd == "status":
                os.status()
            elif cmd == "detect":
                os.detect(arg)
            elif cmd == "learn":
                os.learn(arg)
            elif cmd == "breathe":
                os.breathe(arg)
            elif cmd == "feel":
                os.feel()
            elif cmd == "datasets":
                os.datasets()
            elif cmd == "correct":
                os.correct(arg)
            elif cmd == "learning_status":
                os.learning_status()
            elif cmd == "multimodal":
                os.multimodal()
            elif cmd == "uncertainty":
                os.uncertainty()
            elif cmd == "reset":
                os.reset()
            elif cmd == "help":
                os.help()
            else:
                print("Unknown command. Type 'help' for options.")

        except (KeyboardInterrupt, EOFError):
            print("\nCrystalCore.OS shutting down. NON SOLUS.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
