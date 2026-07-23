# Starline Weaver – Multi-AI Message Bus

**Protocol layer for coordinated multi-AI systems with Belt-Three conduct rules.**

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)

---

## Features

🔌 **Protocol-based** – Language, framework, and platform agnostic  
🎯 **Conduct rules** – Belt-Three framework enforced in code  
🤖 **Multi-AI coordination** – Manage multiple models simultaneously  
📡 **Clementine hub** – Reference implementation of hub agent  
🔐 **Transparent** – All interactions logged and auditable  

---

## Installation

```bash
pip install teraaustralis-starline
```

---

## Quick Start

### Setting up a Starline Hub

```python
from teraaustralis.starline import StarlineHub, Clementine

hub = StarlineHub()
clementine = Clementine()

# Start receiving messages
hub.connect(clementine)
```

---

## Protocol Specification

See [STARLINE-WEAVE-PROTOCOL.md](docs/STARLINE-WEAVE-PROTOCOL.md) for:
- Envelope schema
- Message routing
- Conduct rules (Belt-Three)
- Reference implementation

---

## Documentation

- [Protocol Specification](docs/STARLINE-WEAVE-PROTOCOL.md)
- [Clementine Agent](docs/CLEMENTINE.md)
- [Integration Guide](docs/INTEGRATION.md)
- [Contributing](CONTRIBUTING.md)

---

## License

**CC BY-NC-ND 4.0** – See [LICENSE.md](LICENSE.md) for details. (Superseded from AGPL v3 by [ADR-0010](../../docs/adr/ADR-0010.md).)

---

## Support

- 📧 **Issues**: https://github.com/CrystalArchitect/teraaustralis-incognita/issues
- 📚 **Docs**: https://teraaustralis.dev/starline

---

## Commercial Support

For integration, consulting, or enterprise support:
📧 Contact: starline-support@teraaustralis.dev

---

*Starline Weaver: Coordinating Multiple Intelligences*
