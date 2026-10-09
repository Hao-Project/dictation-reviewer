"""Tests for template module."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from template import build_html


SAMPLE_CORRECTIONS = [
    {
        "original": "The maid preference varies",
        "minimal": "The mate preference varies.",
        "light": "Mate preference varies.",
        "polish": "Mate preferences vary across populations.",
    },
    {
        "original": "King C studied this",
        "minimal": "Kinsey studied this.",
        "light": "Kinsey studied this topic.",
        "polish": "Alfred Kinsey conducted research on this topic.",
    },
]


def test_build_html_returns_string():
    html = build_html(SAMPLE_CORRECTIONS)
    assert isinstance(html, str)


def test_build_html_self_contained():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "<style>" in html
    assert "<script>" in html
    assert "<!DOCTYPE html>" in html


def test_build_html_contains_corrections():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "The maid preference varies" in html
    assert "King C studied this" in html


def test_build_html_contains_all_levels():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "Minimal" in html
    assert "Light" in html
    assert "Polish" in html


def test_build_html_custom_title():
    html = build_html(SAMPLE_CORRECTIONS, title="My Book Notes")
    assert "My Book Notes" in html


def test_build_html_has_keyboard_shortcuts():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "Keyboard" in html
    assert "Enter" in html


def test_build_html_has_dark_mode():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "darkToggle" in html
    assert ".dark" in html


def test_build_html_has_progress_bar():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "progressBar" in html


def test_build_html_has_export():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "Copy Markdown" in html
    assert "Download as .md" in html


def test_corrections_json_embedded():
    html = build_html(SAMPLE_CORRECTIONS)
    # The corrections should be valid JSON embedded in the page
    assert "CORRECTIONS" in html


def test_build_html_shows_complete_and_diff_versions():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "Complete versions" in html
    assert "Changes vs. original" in html
    assert "diffWords(item.original, opt.text)" in html


def test_build_html_has_delete_option():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "Delete this entry" in html
    assert "selectOption(${i}, 'delete')" in html
    assert "kept = state.items.filter(it => !isDeleted(it))" in html


def test_build_html_has_unconfirm():
    html = build_html(SAMPLE_CORRECTIONS)
    assert "function unconfirmCard" in html
    assert "Unconfirm" in html
