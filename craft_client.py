"""Craft MCP integration for fetching notes.

Provides functions for reading notes from a file, stdin, or parsing Craft MCP
blocks_get responses. Saving/archiving is handled by note-manager.
"""

import sys
from pathlib import Path


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
