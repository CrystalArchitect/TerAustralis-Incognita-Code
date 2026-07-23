# Consent Transport – Privacy-Respecting Data Protocol

**End-to-end encrypted communication for consent-driven systems.**

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)

---

## Features

🔐 **End-to-end encryption** – No cleartext transmission  
✅ **Consent verification** – Explicit opt-in enforcement  
📋 **Audit trails** – Full compliance logging  
🔄 **Transport agnostic** – HTTP, gRPC, or custom transports  
📊 **Interoperable** – Works with any consent framework  

---

## Installation

```bash
pip install teraaustralis-consent-transport
```

Or install in development mode:

```bash
git clone https://github.com/CrystalArchitect/teraaustralis-incognita.git
cd teraaustralis-incognita/packages/consent-transport
pip install -e .
```

---

## Quick Start

### Transport Server

```python
from teraaustralis.consent_transport import ConsentTransport

transport = ConsentTransport()
transport.start_server(port=5000)
```

### Client

```python
from teraaustralis.consent_transport import ConsentClient

client = ConsentClient("https://transport.example.com")
message = client.send_encrypted(
    recipient="user@example.com",
    payload={"action": "share_data"},
    consent_token="ct_12345"
)
```

---

## Documentation

- [Transport Specification](docs/TRANSPORT-SPEC.md)
- [Consent Verification](docs/CONSENT-VERIFICATION.md)
- [Encryption Details](docs/ENCRYPTION.md)
- [Contributing](CONTRIBUTING.md)

---

## License

**CC BY-NC-ND 4.0** – See [LICENSE.md](LICENSE.md) for details. (Superseded from AGPL v3 by [ADR-0010](../../docs/adr/ADR-0010.md).)

---

## Support

- 📧 **Issues**: https://github.com/CrystalArchitect/teraaustralis-incognita/issues
- 📚 **Docs**: https://teraaustralis.dev/consent-transport

---

*Consent Transport: Privacy Without Compromise*
