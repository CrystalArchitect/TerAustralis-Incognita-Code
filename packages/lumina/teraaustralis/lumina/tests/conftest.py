"""Make the local `crystalcore` package importable and unambiguous.

The repo root has a *different* package also named `crystalcore` (the
CrystalBridge ConsentGate), and the root pytest config puts the repo root on
`pythonpath`. Inserting this app's directory at the front of `sys.path` ensures
`import crystalcore` resolves to Lumina's framework here, not the bridge.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
