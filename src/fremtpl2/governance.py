"""Machine-readable model governance statements."""

from src.fremtpl2 import DISCLAIMER

GOVERNANCE = {
    "scope": DISCLAIMER,
    "leakage_control": "Policy ID is used for splitting and joins only, never as a feature.",
    "frequency_offset": "Natural logarithm of policy exposure.",
    "severity_target": "Strictly positive claim amounts; large losses retained.",
    "premium_label": "Estimated technical claims cost, not a final customer premium.",
}
