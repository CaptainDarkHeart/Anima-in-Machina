"""AI DJ MCP Server — Traktor-first DJ tools for Claude.

Data hierarchy:
  PRIMARY  — Traktor's own analysis via collection.nml (BPM, beatgrid, key, gain)
  SECONDARY — librosa analysis of raw audio (energy envelope, breakdown detection)
"""

__version__ = "0.2.0"
