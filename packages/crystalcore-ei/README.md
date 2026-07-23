# CrystalCore.OS – Emotional Intelligence System

**Production-grade emotional intelligence with Bayesian uncertainty and active learning.**

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)

---

## Features

🧠 **Bayesian uncertainty** – Epistemic vs. aleatoric confidence quantification  
🎯 **Active learning** – Intelligent feedback collection on uncertain predictions  
🎭 **28-label emotion detection** – GoEmotions framework + EI hierarchy mapping  
📊 **Data warehouse integration** – dbt models for production analytics  
📈 **Calibrated scores** – Reliability metrics across all predictions  

---

## Installation

```bash
pip install teraaustralis-ei
```

Licensed CC BY-NC-ND 4.0, non-commercial — see `## Licensing` below.

---

## Quick Start

### Basic Emotion Detection

```python
from teraaustralis.ei import EmotionalIntelligence

ei = EmotionalIntelligence()
result = ei.predict("I'm feeling overwhelmed by all the changes")

print(f"Primary emotion: {result.primary_emotion}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Uncertainty: {result.uncertainty}")
```

### With Active Learning

```python
from teraaustralis.ei import ActiveLearner

learner = ActiveLearner()

# Get predictions with uncertainty
predictions = learner.predict_batch(texts)

# Get most uncertain samples for review
uncertain_samples = learner.get_uncertain_samples(k=10)

# Provide feedback
for sample, true_label in review_feedback:
    learner.update(sample, true_label)
```

### Data Warehouse Integration

```python
from teraaustralis.ei import EmotionalIntelligence
from teraaustralis.ei.dbt_integration import DbtDataExporter

ei = EmotionalIntelligence()
exporter = DbtDataExporter()

# Export predictions to warehouse
exporter.export_prediction(
    text="Sample text",
    emotion="joy",
    confidence=0.92,
    uncertainty=0.08
)

# Export active learning samples
exporter.export_active_learning_sample(
    text="Uncertain text",
    model_prediction="sad",
    confidence=0.45
)
```

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Bayesian Uncertainty Guide](docs/UNCERTAINTY.md)
- [Active Learning Framework](docs/ACTIVE_LEARNING.md)
- [dbt Warehouse Integration](docs/DBT_WAREHOUSE_INTEGRATION.md)
- [Contributing](CONTRIBUTING.md)

---

## Licensing

**CC BY-NC-ND 4.0** — non-commercial use, attribution required, no
derivative redistribution. See [LICENSE.md](LICENSE.md) for details.
(Superseded from the earlier MIT-non-commercial / paid-commercial dual
model by [ADR-0010](../../docs/adr/ADR-0010.md); `COMMERCIAL_LICENSE.md`
and `LICENSING.md` at the repo root are marked accordingly rather than
deleted.)

For commercial use, contact the copyright holder — see
[`docs/ATTRIBUTIONS.md`](../../docs/ATTRIBUTIONS.md).

---

## Support

- 📧 **Issues**: https://github.com/CrystalArchitect/teraaustralis-incognita/issues
- 💬 **Discussions**: https://github.com/CrystalArchitect/teraaustralis-incognita/discussions
- 📚 **Docs**: https://teraaustralis.dev/ei

---

## Commercial Licensing

For commercial use or licensing inquiries:
📧 Contact: **ei-commercial@teraaustralis.dev**

---

*CrystalCore.OS EI: Emotional Intelligence at Scale*
