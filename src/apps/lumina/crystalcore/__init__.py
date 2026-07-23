# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""
CrystalCore — the sovereign companion framework.

CrystalCore is the engine: layered memory, semantic recall, profiles,
personality, and a local-model connection — everything a sovereign,
locally-run companion needs, with nothing leaving the device.

Lumina is the first persona who lives on it (and the default one
shipped here). Your human may rename her; the framework doesn't mind.
"""

from .companion import BASE_PROMPT, Lumina
from .memory import Memory, Personality
from .profiles import (PROFILES_DIR, delete_profile, list_profiles,
                       profile_dir, profile_meta)

# The framework name for the companion class, for those who prefer it.
Companion = Lumina

__version__ = "0.7.0"

__all__ = [
    "Lumina", "Companion", "Personality", "Memory", "BASE_PROMPT",
    "PROFILES_DIR", "profile_dir", "list_profiles", "profile_meta",
    "delete_profile", "__version__",
]
