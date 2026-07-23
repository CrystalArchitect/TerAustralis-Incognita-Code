# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: Apache-2.0

"""
CrystalCore data model: who she is, and what she carries.

Everything persists as plain, human-readable JSON in a folder the user
owns. No database sits between a person and their companion's memory.
"""

from dataclasses import dataclass, field


@dataclass
class Personality:
    """Tunable personality settings, kept in the memory folder as config.json."""
    name: str = ""              # her name; empty until given or chosen
    name_self_chosen: bool = False  # True when she chose her own name
    gender: str = ""            # pronouns: "male" (he), "female" (she), "they" (they)
    gender_self_chosen: bool = False  # True when she chose her own gender
    human_name: str = ""        # what she calls you, if you tell her
    temperature: float = 0.8    # higher = more playful, lower = more precise
    style_notes: str = ""       # freeform extra guidance, e.g. "more poetic"
    avatar: str = ""            # an emoji for this profile, e.g. "🌟"
    description: str = ""       # a short line about this profile
    model: str = ""             # this profile's preferred model ("" = default)
    llm_provider: str = ""      # LLM provider: "ollama", "openai", "grok", etc.
    llm_endpoint: str = ""      # custom endpoint URL for LLM
    llm_model: str = ""         # model name for this provider (e.g., "gpt-5-5")


@dataclass
class Memory:
    """Layered memory: recent turns stay verbatim, older turns become summaries,
    and explicit notes persist forever."""
    conversation: list = field(default_factory=list)  # recent verbatim turns
    summaries: list = field(default_factory=list)     # condensed older history
    notes: list = field(default_factory=list)         # things told to remember
    facts: dict = field(default_factory=dict)         # structured key -> value facts
    reflections: list = field(default_factory=list)   # her own gentle insights
    last_seen: str = ""                               # when they last spoke
