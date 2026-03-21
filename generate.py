#!/usr/bin/env python3
"""CLI entry point for dictation-reviewer.

Fetches Siri-dictated notes, generates AI corrections, and produces
an interactive HTML review page.
"""

import argparse
import json
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from config import DEFAULT_DOCUMENT, DEFAULT_MODEL, DEFAULT_OUTPUT_DIR, default_output_filename
from corrections import generate_corrections
from craft_client import fetch_notes_from_file, fetch_notes_from_stdin
from template import build_html


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dictation Reviewer — correct Siri-dictated notes with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Input options
    input_group = parser.add_argument_group("Input options")
    input_group.add_argument(
        "--source",
        choices=["file", "stdin", "craft"],
        default="file",
        help="Where to read notes from (default: file)",
    )
    input_group.add_argument(
        "--input", "-i",
        dest="input_file",
        help="Path to text file (one note per line)",
    )
    input_group.add_argument(
        "--document",
        default=DEFAULT_DOCUMENT,
        help=f'Craft document name to fetch (default: "{DEFAULT_DOCUMENT}")',
    )

    # Correction options
    corr_group = parser.add_argument_group("Correction options")
    corr_group.add_argument(
        "--corrections-file", "-c",
        help="Load pre-generated corrections JSON (skip AI)",
    )
    corr_group.add_argument(
        "--save-corrections",
        help="Save generated corrections to JSON for reuse",
    )
    corr_group.add_argument(
        "--book-title",
        default="",
        help="Audiobook title for better AI context",
    )
    corr_group.add_argument(
        "--topic",
        default="",
        help='Topic hint for the AI (e.g. "evolutionary psychology")',
    )
    corr_group.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})",
    )

    # Output options
    out_group = parser.add_argument_group("Output options")
    out_group.add_argument(
        "--output", "-o",
        help="Output HTML path (default: YYYYMMDD_HHMM_review.html)",
    )
    out_group.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to save output files",
    )
    out_group.add_argument(
        "--title",
        default="Dictation Review",
        help="Custom title for the review page",
    )

    # Automation
    auto_group = parser.add_argument_group("Automation")
    auto_group.add_argument(
        "--schedule",
        choices=["daily", "hourly"],
        help="Run on a schedule (creates a launchd plist or cron job)",
    )
    auto_group.add_argument(
        "--auto-open",
        action="store_true",
        help="Open HTML in browser after generation",
    )

    # Write-back
    wb_group = parser.add_argument_group("Write-back")
    wb_group.add_argument(
        "--write-back-craft",
        action="store_true",
        help="Save final reviewed .md back to Craft (requires MCP)",
    )

    return parser.parse_args()


def fetch_notes(args: argparse.Namespace) -> list[str]:
    """Fetch notes based on the selected source."""
    if args.source == "file":
        if not args.input_file:
            print("Error: --input/-i required when --source is 'file'", file=sys.stderr)
            sys.exit(1)
        notes = fetch_notes_from_file(args.input_file)

    elif args.source == "stdin":
        notes = fetch_notes_from_stdin()

    elif args.source == "craft":
        print(
            "Craft MCP source requires running inside Claude Code with Craft MCP connected.\n"
            "Use Claude Code to fetch notes, then pass them via --input or --corrections-file.\n"
            "Alternatively, use: --source file --input notes.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    if not notes:
        print("Error: No notes found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(notes)} notes.")
    return notes


def setup_schedule(args: argparse.Namespace) -> None:
    """Set up a scheduled task using launchd (macOS)."""
    interval = 3600 if args.schedule == "hourly" else 86400
    script_path = Path(__file__).resolve()
    plist_name = "com.dictation-reviewer.scheduled"
    plist_path = Path.home() / "Library" / "LaunchAgents" / f"{plist_name}.plist"

    cmd_args = [sys.executable, str(script_path)]
    if args.input_file:
        cmd_args.extend(["--input", args.input_file])
    if args.source:
        cmd_args.extend(["--source", args.source])
    cmd_args.extend(["--output-dir", args.output_dir, "--auto-open"])

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{plist_name}</string>
    <key>ProgramArguments</key>
    <array>
        {"".join(f"<string>{a}</string>" for a in cmd_args)}
    </array>
    <key>StartInterval</key>
    <integer>{interval}</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""

    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_text(plist_content)
    subprocess.run(["launchctl", "load", str(plist_path)], check=True)
    print(f"Scheduled task installed: {plist_path}")
    print(f"Running every {args.schedule}. Unload with: launchctl unload {plist_path}")


def main() -> None:
    args = parse_args()

    # Handle scheduling setup
    if args.schedule:
        setup_schedule(args)
        return

    # Fetch notes
    notes = fetch_notes(args)

    # Generate or load corrections
    corrections = generate_corrections(
        notes=notes,
        corrections_file=args.corrections_file,
        book_title=args.book_title,
        topic=args.topic,
        model=args.model,
    )

    # Save corrections if requested
    if args.save_corrections:
        save_path = Path(args.save_corrections)
        save_path.write_text(
            json.dumps(corrections, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Corrections saved to: {save_path}")

    # Build HTML
    html_content = build_html(corrections, title=args.title)

    # Determine output path
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_path = output_dir / args.output
    else:
        output_path = output_dir / default_output_filename("html")

    output_path.write_text(html_content, encoding="utf-8")
    print(f"Review page saved to: {output_path}")

    # Auto-open
    if args.auto_open:
        webbrowser.open(f"file://{output_path.resolve()}")

    # Write-back reminder
    if args.write_back_craft:
        print(
            "Note: Write-back to Craft requires running inside Claude Code with MCP.\n"
            "Use the markdown_add tool to write back the reviewed content."
        )


if __name__ == "__main__":
    main()
