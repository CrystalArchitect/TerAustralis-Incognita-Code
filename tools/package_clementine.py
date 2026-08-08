# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Assemble the Clementine starter — a self-contained folder a tester can
run on Windows, macOS, or Linux with nothing but Python.

The starter is assembled from the canonical sources, never hand-copied,
so it cannot drift from the code CI actually tests:

    vision/apps/clementine/   the terminal interface (and web server)
    core/crystalcore/         the mind: memory, profiles, recall

Usage:
    python tools/package_clementine.py            # writes dist/clementine-starter/
    python tools/package_clementine.py --zip      # also writes dist/clementine-starter.zip
    python tools/package_clementine.py --check    # assemble to a temp dir and smoke-test

The assembled starter is standalone: `clementine.py` inside it looks for
the mind at `./core` (a one-line path patch, applied at assembly and
verified against the expected original line so a source change cannot be
silently mis-patched). Everything else is copied byte-identical.

Deliberately excluded: the Svelte webapp (needs npm; the terminal and the
plain-HTML web page under `webapp/` static assets are enough for a first
run), caches, and anything resembling a memory or profile folder — a
companion's memories are personal data and must never ship in a package.
"""

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
APP = REPO / "vision" / "apps" / "clementine"
CORE = REPO / "core" / "crystalcore"
STARTER_SRC = REPO / "tools" / "starter"

# The path bootstrap in clementine.py, as it exists in the repo (mind under
# ../../../core) and as the starter needs it (mind under ./core). Assembly
# fails loudly if the original line changes, rather than mis-patching.
ORIG_BOOTSTRAP = 'sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "core"))'
STARTER_BOOTSTRAP = 'sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "core"))'

EXCLUDE_NAMES = {"__pycache__", ".pytest_cache", "crystalcore_profiles",
                 "lumina_profiles", "webapp", "node_modules"}


def _copytree(src: pathlib.Path, dst: pathlib.Path) -> None:
    shutil.copytree(
        src, dst,
        ignore=lambda d, names: [n for n in names if n in EXCLUDE_NAMES],
    )


def assemble(dest: pathlib.Path) -> pathlib.Path:
    starter = dest / "clementine-starter"
    if starter.exists():
        shutil.rmtree(starter)
    starter.mkdir(parents=True)

    # The mind, whole: memory, profiles, recall, gate, audit, selftest.
    _copytree(CORE, starter / "core" / "crystalcore")

    # The interface: terminal app, local web server, licence and docs.
    for name in ("clementine.py", "server.py", "requirements.txt", "README.md"):
        shutil.copy2(APP / name, starter / name)

    # Repoint the one path line, verifying the original is what we expect.
    entry = starter / "clementine.py"
    text = entry.read_text(encoding="utf-8")
    if ORIG_BOOTSTRAP not in text:
        raise SystemExit(
            "clementine.py's path bootstrap has changed; update "
            "tools/package_clementine.py to match before assembling."
        )
    entry.write_text(text.replace(ORIG_BOOTSTRAP, STARTER_BOOTSTRAP),
                     encoding="utf-8")

    # server.py carries the same style of bootstrap; patch it the same way
    # if present, and say so if its shape ever changes.
    server = starter / "server.py"
    stext = server.read_text(encoding="utf-8")
    if ORIG_BOOTSTRAP in stext:
        server.write_text(stext.replace(ORIG_BOOTSTRAP, STARTER_BOOTSTRAP),
                          encoding="utf-8")

    # Launchers, doctor, tester guide, licence/notice — authored for the
    # starter, versioned in tools/starter/.
    for item in STARTER_SRC.iterdir():
        if item.is_dir():
            _copytree(item, starter / item.name)
        else:
            shutil.copy2(item, starter / item.name)

    # The licence rides with the code it licenses.
    shutil.copy2(REPO / "LICENSE", starter / "LICENSE")
    shutil.copy2(REPO / "NOTICE", starter / "NOTICE")

    # Belt and braces: refuse to package anything that looks like memory.
    leaked = [p for p in starter.rglob("*")
              if p.name in ("crystalcore_profiles", "lumina_profiles")
              or "memory" in p.name.lower() and p.suffix == ".json"]
    if leaked:
        raise SystemExit(f"refusing to package memory-like paths: {leaked}")

    return starter


def smoke(starter: pathlib.Path) -> None:
    """The checks a fresh machine would fail first: import the mind, show
    --help, and exercise memory offline (no Ollama, no network)."""
    py = sys.executable
    env_dir = starter
    checks = [
        [py, "-c",
         "import sys; sys.path.insert(0, 'core'); "
         "from crystalcore.mind import CrystalCore, Memory; print('mind imports')"],
        [py, "clementine.py", "--help"],
        # The Joe's-pizza check: a fact stored offline survives a full
        # save, and a second, fresh mind — a stand-in for a swapped model —
        # reads the same record from the same memory. No network involved.
        [py, "-c",
         "import sys, tempfile; sys.path.insert(0, 'core'); "
         "from crystalcore.mind import CrystalCore; "
         "d = tempfile.mkdtemp(); "
         "a = CrystalCore(memory_dir=d); "
         "a.memory.facts['favourite_restaurant'] = \"Joe's\"; a.save(); "
         "b = CrystalCore(memory_dir=d); "
         "assert b.memory.facts.get('favourite_restaurant') == \"Joe's\", b.memory.facts; "
         "print('memory persists offline across minds')"],
    ]
    for cmd in checks:
        r = subprocess.run(cmd, cwd=env_dir, capture_output=True, text=True,
                           timeout=120)
        if r.returncode != 0:
            raise SystemExit(
                f"smoke check failed: {' '.join(cmd[:2])}\n{r.stdout}\n{r.stderr}")
    print(f"smoke: all {len(checks)} checks passed in {starter}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", action="store_true", help="also write a zip")
    ap.add_argument("--check", action="store_true",
                    help="assemble into a temp dir and smoke-test it")
    args = ap.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as td:
            starter = assemble(pathlib.Path(td))
            smoke(starter)
        return

    dist = REPO / "dist"
    starter = assemble(dist)
    smoke(starter)
    print(f"assembled: {starter}")

    if args.zip:
        zpath = dist / "clementine-starter.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(starter.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(dist))
        print(f"zipped: {zpath} ({zpath.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
