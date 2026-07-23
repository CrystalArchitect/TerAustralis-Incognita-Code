# RDP – Recursive Dialogue Protocol

**Framework for multi-turn conversational reasoning with state persistence.**

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)

---

## Features

🎯 **Recursive reasoning** – Multi-turn context preservation  
💭 **State persistence** – Full dialogue history  
🔗 **Model agnostic** – Works with any LLM backend  
📝 **Structured output** – Typed responses with validation  
🔄 **Streaming support** – Real-time token output  

---

## Installation

```bash
pip install teraaustralis-rdp
```

Or install in development mode:

```bash
git clone https://github.com/CrystalArchitect/teraaustralis-incognita.git
cd teraaustralis-incognita/packages/rdp
pip install -e .
```

---

## Quick Start

### Basic Dialogue

```python
from teraaustralis.rdp import RDP

dialogue = RDP()
response = dialogue.query("What is emotional intelligence?")
print(response.text)

# Follow-up preserves context
follow_up = dialogue.query("How can I develop it?")
print(follow_up.text)
```

### With Custom Model

```python
from teraaustralis.rdp import RDP, ModelConfig

config = ModelConfig(
    provider="openai",
    model="gpt-4",
    temperature=0.7
)
dialogue = RDP(config=config)
```

---

## Documentation

- [Protocol Specification](docs/RDP-PROTOCOL.md)
- [API Reference](docs/API.md)
- [Model Configuration](docs/MODELS.md)
- [Contributing](CONTRIBUTING.md)

---

## License

**CC BY-NC-ND 4.0** – See [LICENSE.md](LICENSE.md) for details. (Superseded from AGPL v3 by [ADR-0010](../../docs/adr/ADR-0010.md).)

---

## Support

- 📧 **Issues**: https://github.com/CrystalArchitect/teraaustralis-incognita/issues
- 💬 **Discussions**: https://github.com/CrystalArchitect/teraaustralis-incognita/discussions
- 📚 **Docs**: https://teraaustralis.dev/rdp

---

*RDP: Reasoning Through Dialogue*
