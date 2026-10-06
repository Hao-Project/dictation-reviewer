"""Configuration and defaults for dictation-reviewer."""

from datetime import datetime
from pathlib import Path

# Default output directory for generated review pages
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "reviews"

# Custom dictionary path
CUSTOM_DICTIONARY_PATH = Path(__file__).parent / "custom_dictionary.json"

# Cache directory for API responses
CACHE_DIR = Path(__file__).parent / ".cache"

# Correction levels
CORRECTION_LEVELS = ["minimal", "light", "polish"]

# Timestamp format for output filenames
TIMESTAMP_FORMAT = "%Y%m%d_%H%M"


def default_output_filename(ext: str = "html") -> str:
    """Generate a default output filename with current timestamp."""
    ts = datetime.now().strftime(TIMESTAMP_FORMAT)
    if ext == "html":
        return f"{ts}_review.html"
    return f"{ts}.{ext}"
