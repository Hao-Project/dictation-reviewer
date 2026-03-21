"""Configuration and defaults for dictation-reviewer."""

import os
from datetime import datetime
from pathlib import Path

# Default document name to fetch from Craft
DEFAULT_DOCUMENT = "Dictated Notes"

# Default output directory
DEFAULT_OUTPUT_DIR = Path.cwd()

# AI model for corrections
DEFAULT_MODEL = "claude-sonnet-4-6"

# Custom dictionary path
CUSTOM_DICTIONARY_PATH = Path(__file__).parent / "custom_dictionary.json"

# Cache directory for API responses
CACHE_DIR = Path(__file__).parent / ".cache"

# Notes storage directories
NOTES_DIR = Path(__file__).parent / "notes"
NOTES_ARCHIVE_DIR = NOTES_DIR / "archive"

# Corrections storage directories
CORRECTIONS_DIR = Path(__file__).parent / "corrections"
CORRECTIONS_ARCHIVE_DIR = CORRECTIONS_DIR / "archive"

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


def get_api_key() -> str | None:
    """Get the Anthropic API key from environment."""
    return os.environ.get("ANTHROPIC_API_KEY")
