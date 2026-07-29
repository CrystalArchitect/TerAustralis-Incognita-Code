# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Put both halves of the app on `sys.path` for the tests.

Two roots are needed: this app's own directory, so `server` and
`clementine` import; and `core/`, so `crystalcore.mind` — the mind these
tests exercise — imports.

There is no longer a second package named `crystalcore` to disambiguate
against. The mind moved out of vision/apps/ into the one CrystalCore
package, which is what retired the importlib alias in bridge.py.
"""

import pathlib
import sys

APP_DIR = pathlib.Path(__file__).resolve().parents[1]
CORE_DIR = pathlib.Path(__file__).resolve().parents[4] / "core"

for path in (CORE_DIR, APP_DIR):
    sys.path.insert(0, str(path))
