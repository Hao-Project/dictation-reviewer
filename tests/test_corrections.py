"""Tests for corrections module."""

import json
import sys
import tempfile
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from corrections import (
    apply_dictionary,
    build_system_prompt,
    compute_cache_key,
    load_corrections_from_file,
    load_custom_dictionary,
)


def test_load_custom_dictionary():
    d = load_custom_dictionary()
    assert isinstance(d, dict)
    assert "King C" in d
    assert d["King C"] == "Kinsey"


def test_apply_dictionary():
    dictionary = {"King C": "Kinsey", "maid": "mate"}
    notes = ["King C was a researcher", "The maid preference"]
    result = apply_dictionary(notes, dictionary)
    assert result[0] == "Kinsey was a researcher"
    assert result[1] == "The mate preference"


def test_compute_cache_key_deterministic():
    notes = ["test note 1", "test note 2"]
    key1 = compute_cache_key(notes, "Book A", "topic")
    key2 = compute_cache_key(notes, "Book A", "topic")
    assert key1 == key2


def test_compute_cache_key_differs():
    notes = ["test note"]
    key1 = compute_cache_key(notes, "Book A")
    key2 = compute_cache_key(notes, "Book B")
    assert key1 != key2


def test_load_corrections_from_file():
    corrections = [
        {"original": "test", "minimal": "test.", "light": "Test.", "polish": "A test."}
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(corrections, f)
        f.flush()
        loaded = load_corrections_from_file(f.name)
    assert loaded == corrections


def test_build_system_prompt_with_context():
    prompt = build_system_prompt(book_title="The Selfish Gene", topic="evolutionary biology")
    assert "The Selfish Gene" in prompt
    assert "evolutionary biology" in prompt


def test_build_system_prompt_without_context():
    prompt = build_system_prompt()
    assert "Siri-dictated" in prompt
