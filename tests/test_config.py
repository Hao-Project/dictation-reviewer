"""Tests for config module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DEFAULT_OUTPUT_DIR


def test_default_output_dir_is_reviews_folder_in_project():
    project_root = Path(__file__).parent.parent
    assert DEFAULT_OUTPUT_DIR == project_root / "reviews"
