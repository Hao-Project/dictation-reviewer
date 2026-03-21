"""Tests for craft_client module."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from craft_client import fetch_notes_from_file, parse_blocks_response


def test_fetch_notes_from_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Note one\nNote two\n\nNote three\n")
        f.flush()
        notes = fetch_notes_from_file(f.name)
    assert notes == ["Note one", "Note two", "Note three"]


def test_fetch_notes_from_file_strips_whitespace():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("  spaced note  \n  another  \n")
        f.flush()
        notes = fetch_notes_from_file(f.name)
    assert notes == ["spaced note", "another"]


def test_parse_blocks_response_dict():
    response = {
        "blocks": [
            {"content": "Hello world"},
            {"content": ""},
            {"content": "Second note"},
        ]
    }
    notes = parse_blocks_response(response)
    assert notes == ["Hello world", "Second note"]


def test_parse_blocks_response_list():
    response = [
        {"content": "Note A"},
        {"content": "Note B"},
    ]
    notes = parse_blocks_response(response)
    assert notes == ["Note A", "Note B"]


def test_parse_blocks_response_with_spans():
    response = [
        {"content": [{"text": "Hello "}, {"text": "world"}]},
    ]
    notes = parse_blocks_response(response)
    assert notes == ["Hello world"]


def test_parse_blocks_response_with_children():
    response = [
        {
            "content": "Parent",
            "children": [
                {"content": "Child 1"},
                {"content": "Child 2"},
            ],
        },
    ]
    notes = parse_blocks_response(response)
    assert notes == ["Parent", "Child 1", "Child 2"]
