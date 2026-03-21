"""Craft MCP integration for fetching and writing notes.

This module provides functions that work when called from within Claude Code,
where MCP tools are available as callable functions. For standalone use,
fall back to file-based input.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from config import CORRECTIONS_ARCHIVE_DIR, CORRECTIONS_DIR, NOTES_ARCHIVE_DIR, NOTES_DIR, TIMESTAMP_FORMAT


def fetch_notes_from_file(filepath: str) -> list[str]:
    """Read notes from a text file, one note per line."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return [line.strip() for line in lines if line.strip()]


def fetch_notes_from_stdin() -> list[str]:
    """Read notes from stdin, one note per line."""
    lines = sys.stdin.read().strip().splitlines()
    return [line.strip() for line in lines if line.strip()]


def parse_blocks_response(response: dict | list) -> list[str]:
    """Extract text content from Craft blocks_get response.

    The response contains blocks with content fields. We extract
    non-empty text blocks.
    """
    notes = []

    if isinstance(response, dict):
        blocks = response.get("blocks", response.get("children", []))
    elif isinstance(response, list):
        blocks = response
    else:
        return notes

    for block in blocks:
        if isinstance(block, dict):
            content = block.get("content", "")
            if isinstance(content, list):
                # Content may be a list of text spans
                text = "".join(
                    span.get("text", "") if isinstance(span, dict) else str(span)
                    for span in content
                )
            elif isinstance(content, str):
                text = content
            else:
                text = str(content) if content else ""

            text = text.strip()
            if text:
                notes.append(text)

            # Recurse into children
            children = block.get("children", [])
            if children:
                notes.extend(parse_blocks_response(children))

    return notes


def save_notes(notes: list[str]) -> tuple[Path, Path]:
    """Save fetched notes to latest.txt and a timestamped archive copy.

    Returns (latest_path, archive_path).
    """
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    content = "\n".join(notes) + "\n"
    ts = datetime.now().strftime(TIMESTAMP_FORMAT)

    latest_path = NOTES_DIR / "latest_notes.txt"
    archive_path = NOTES_ARCHIVE_DIR / f"{ts}_notes.txt"

    latest_path.write_text(content, encoding="utf-8")
    archive_path.write_text(content, encoding="utf-8")

    print(f"Notes saved → {latest_path}")
    print(f"Notes archived → {archive_path}")

    return latest_path, archive_path


def save_corrections(corrections: list[dict], ts: str) -> tuple[Path, Path]:
    """Save corrections to latest_corrections.json and a timestamped archive copy.

    Returns (latest_path, archive_path).
    """
    CORRECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    CORRECTIONS_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    content = json.dumps(corrections, indent=2, ensure_ascii=False)

    latest_path = CORRECTIONS_DIR / "latest_corrections.json"
    archive_path = CORRECTIONS_ARCHIVE_DIR / f"{ts}_corrections.json"

    latest_path.write_text(content, encoding="utf-8")
    archive_path.write_text(content, encoding="utf-8")

    print(f"Corrections saved → {latest_path}")
    print(f"Corrections archived → {archive_path}")

    return latest_path, archive_path


def save_corrections_for_writeback(corrections: list[dict], output_path: str) -> None:
    """Save corrections JSON for later write-back to Craft."""
    Path(output_path).write_text(
        json.dumps(corrections, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# --- Instructions for Craft MCP usage from Claude Code ---
#
# When running inside Claude Code with Craft MCP connected, use these tools:
#
# 1. Fetch today's daily note:
#    blocks_get(date="today", format="json")
#
# 2. Search for a document by name:
#    documents_search(include="Dictated Notes")
#
# 3. Get blocks from a specific document:
#    blocks_get(id=document_id, format="json")
#
# 4. Write back corrected markdown:
#    markdown_add(markdown=corrected_text, position="end", date="today")
#    or
#    documents_create(documents=[{"title": "Corrected Notes"}])
#    then markdown_add(markdown=corrected_text, position="end", pageId=new_doc_id)
