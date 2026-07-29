# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0

"""Provider dialect tests — offline, asserting on the request that would be
sent rather than sending one.

The regression these exist to keep caught: `--llm-provider openai` was
advertised in the help text but the code only special-cased "grok" for the
OpenAI wire shape, so "openai" silently posted Ollama-shaped JSON (options
dict, no Authorization header) at the remote endpoint. Any alias in
OPENAI_COMPATIBLE must get the OpenAI shape; everything else gets Ollama's.
"""

import pytest

from crystalcore.mind.companion import CrystalCore


class _Recorder:
    """Stands in for requests.post and records what would have been sent."""

    def __init__(self):
        self.url = None
        self.json = None
        self.headers = None

    def __call__(self, url, json=None, headers=None, timeout=None, stream=False):
        self.url = url
        self.json = json
        self.headers = headers or {}

        class _Resp:
            def raise_for_status(self):
                pass

            def json(self):
                # Shape a minimal valid body for whichever dialect was used.
                return {"choices": [{"message": {"content": "hi"}}],
                        "message": {"content": "hi"}}

        return _Resp()


def _companion(tmp_path, monkeypatch, provider, endpoint="https://example.test/v1/chat/completions"):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    return CrystalCore(memory_dir=str(tmp_path), llm_provider=provider,
                       llm_endpoint=endpoint, llm_model="some-model")


def test_openai_provider_sends_openai_shape(tmp_path, monkeypatch):
    """The bug: 'openai' used to fall into the Ollama branch."""
    c = _companion(tmp_path, monkeypatch, "openai")
    rec = _Recorder()
    monkeypatch.setattr("crystalcore.mind.companion.requests.post", rec)
    c._ollama_chat([{"role": "user", "content": "hello"}])
    assert "temperature" in rec.json, "OpenAI shape puts temperature at top level"
    assert "options" not in rec.json, "options dict is Ollama's shape"
    assert rec.json["model"] == "some-model", "OpenAI shape uses llm_model"
    assert rec.headers.get("Authorization") == "Bearer test-key"


@pytest.mark.parametrize("alias", ["openai-compatible", "xai", "groq",
                                   "together", "openrouter", "grok"])
def test_every_alias_gets_the_openai_dialect(tmp_path, monkeypatch, alias):
    c = _companion(tmp_path, monkeypatch, alias)
    assert c._dialect() == "openai"


def test_ollama_sends_ollama_shape_without_auth(tmp_path, monkeypatch):
    c = _companion(tmp_path, monkeypatch, "ollama",
                   endpoint="http://localhost:11434/api/chat")
    rec = _Recorder()
    monkeypatch.setattr("crystalcore.mind.companion.requests.post", rec)
    c._ollama_chat([{"role": "user", "content": "hello"}])
    assert "options" in rec.json, "Ollama shape nests temperature in options"
    assert rec.headers.get("Authorization") is None


def test_grok_alias_keeps_its_historical_default_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    c = CrystalCore(memory_dir=str(tmp_path), llm_provider="grok")
    assert "inference.do-ai.run" in c.llm_endpoint


def test_other_remote_aliases_refuse_to_guess_an_endpoint(tmp_path, monkeypatch):
    """Guessing a vendor URL would send conversation somewhere never chosen."""
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    with pytest.raises(ValueError, match="llm-endpoint"):
        CrystalCore(memory_dir=str(tmp_path), llm_provider="openai")
