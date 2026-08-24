# Copyright 2026 Crystal Arena-Turner (TerAustralis Incognita)
# SPDX-License-Identifier: CC-BY-NC-ND-4.0
"""Host trust — classify where code is running. Not a seventh OS.

See docs/HOST-TRUST.md. Steward persist refuses on SHARED and UNKNOWN.
This package classifies; it is not yet wired into ConsentGate or
consent_transport. HADES is a vendor pool name, not a class here.
"""

from .classify import HostClass, classify, refuse_steward_persist

__all__ = ["HostClass", "classify", "refuse_steward_persist"]
