"""AI-powered correction generation for dictated notes.

Supports two modes:
- Mode A: Claude API via Anthropic Python SDK (for automation)
- Mode B: Load pre-generated corrections from JSON (for Claude Code interactive use)
"""

import hashlib
import json
import sys
from pathlib import Path

from config import CACHE_DIR, CUSTOM_DICTIONARY_PATH, DEFAULT_MODEL

SYSTEM_PROMPT = """\
You are a correction assistant for Siri-dictated notes taken while listening to audiobooks.

Siri frequently produces transcription errors including:
- Wrong homophones ("maid" → "mate", "racial" → "ratio")
- Mangled proper nouns ("King C" → "Kinsey", "King selection" → "Kin selection")
- Run-on sentences and missing punctuation
- Filler words and false starts
- Garbled phrases ("Iran three" → "in a study", "I don't listen experimentation" → "at least in experimentation")
- Wrong word forms ("reproductivity" → "reproductive", "attractable" → "attractive")

Known Siri error patterns (apply these automatically):
| Siri dictated | Correct |
|---|---|
| "racial" | "ratio" (waist-to-hip ratio) |
| "maid" | "mate" |
| "King C" | "Kinsey" (Alfred Kinsey) |
| "King selection" | "Kin selection" |
| "non-gave" | "non-gay" |
| "made preference" | "mate preference" |
| "Iran three" | "in a study" |
| "reproductivity" | "reproductive" |
| "attractable" | "attractive" |
| "I don't listen experimentation" | "at least in experimentation" |

You will receive all the notes together — use context from neighboring notes to disambiguate errors.

Generate three correction levels for EACH note:

1. **Minimal Fixes** — Fix only mis-dictated words and grammar errors. Keep original sentence structure and flow intact.
2. **Light Cleanup** — Fix errors, break into logical paragraphs, remove obvious redundancy.
3. **Full Polish** — Fix errors, reorganize for clarity and readability, remove all redundancy. Professional prose.

{context_hint}
{dictionary_hint}

Respond with a JSON array. Each element must have exactly these keys:
- "original": the raw dictated text (unchanged)
- "minimal": corrected version — minimal fixes only
- "light": corrected version — light cleanup
- "polish": corrected version — fully polished

Return ONLY the JSON array, no other text.
"""


def load_custom_dictionary() -> dict[str, str]:
    """Load the custom dictionary of known Siri errors."""
    if CUSTOM_DICTIONARY_PATH.exists():
        return json.loads(CUSTOM_DICTIONARY_PATH.read_text(encoding="utf-8"))
    return {}


def apply_dictionary(notes: list[str], dictionary: dict[str, str]) -> list[str]:
    """Apply custom dictionary replacements to notes."""
    result = []
    for note in notes:
        corrected = note
        for wrong, right in dictionary.items():
            corrected = corrected.replace(wrong, right)
        result.append(corrected)
    return result


def compute_cache_key(notes: list[str], book_title: str = "", topic: str = "") -> str:
    """Compute a hash key for caching API results."""
    content = json.dumps({"notes": notes, "book_title": book_title, "topic": topic}, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def load_cached(cache_key: str) -> list[dict] | None:
    """Load cached corrections if available."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    return None


def save_to_cache(cache_key: str, corrections: list[dict]) -> None:
    """Save corrections to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    cache_file.write_text(json.dumps(corrections, indent=2, ensure_ascii=False), encoding="utf-8")


def load_corrections_from_file(filepath: str) -> list[dict]:
    """Load pre-generated corrections from a JSON file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: Corrections file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def build_system_prompt(book_title: str = "", topic: str = "") -> str:
    """Build the system prompt with optional context hints."""
    context_parts = []
    if book_title:
        context_parts.append(f"The audiobook being listened to is: \"{book_title}\".")
    if topic:
        context_parts.append(f"The topic/subject area is: {topic}.")
    context_hint = " ".join(context_parts) if context_parts else ""

    dictionary = load_custom_dictionary()
    if dictionary:
        dict_lines = [f'  "{k}" → "{v}"' for k, v in dictionary.items()]
        dictionary_hint = "Additional known corrections from user dictionary:\n" + "\n".join(dict_lines)
    else:
        dictionary_hint = ""

    return SYSTEM_PROMPT.format(context_hint=context_hint, dictionary_hint=dictionary_hint)


def generate_corrections_api(
    notes: list[str],
    book_title: str = "",
    topic: str = "",
    model: str = DEFAULT_MODEL,
) -> list[dict]:
    """Generate corrections using the Anthropic API.

    Requires ANTHROPIC_API_KEY environment variable.
    """
    try:
        import anthropic
    except ImportError:
        print("Error: 'anthropic' package not installed. Run: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    # Check cache first
    cache_key = compute_cache_key(notes, book_title, topic)
    cached = load_cached(cache_key)
    if cached is not None:
        print(f"Using cached corrections (key: {cache_key})")
        return cached

    client = anthropic.Anthropic()
    system_prompt = build_system_prompt(book_title, topic)

    user_message = "Here are the dictated notes to correct:\n\n"
    for i, note in enumerate(notes, 1):
        user_message += f"{i}. {note}\n"

    print(f"Generating corrections for {len(notes)} notes using {model}...")

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = response.content[0].text.strip()

    # Parse JSON from response (handle possible markdown code fences)
    if response_text.startswith("```"):
        lines = response_text.splitlines()
        # Remove first and last lines (code fences)
        lines = [l for l in lines if not l.startswith("```")]
        response_text = "\n".join(lines)

    try:
        corrections = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing AI response as JSON: {e}", file=sys.stderr)
        print(f"Raw response:\n{response_text}", file=sys.stderr)
        sys.exit(1)

    # Validate structure
    for item in corrections:
        if not all(k in item for k in ("original", "minimal", "light", "polish")):
            print("Error: AI response missing required fields.", file=sys.stderr)
            sys.exit(1)

    # Cache results
    save_to_cache(cache_key, corrections)
    print(f"Corrections generated and cached (key: {cache_key})")

    return corrections


def generate_corrections(
    notes: list[str],
    corrections_file: str | None = None,
    book_title: str = "",
    topic: str = "",
    model: str = DEFAULT_MODEL,
) -> list[dict]:
    """Generate or load corrections.

    If corrections_file is provided, load from file.
    Otherwise, use the Claude API.
    """
    if corrections_file:
        corrections = load_corrections_from_file(corrections_file)
        # Validate that corrections match notes count
        if len(corrections) != len(notes):
            print(
                f"Warning: {len(corrections)} corrections but {len(notes)} notes. "
                "Counts don't match.",
                file=sys.stderr,
            )
        return corrections

    return generate_corrections_api(notes, book_title, topic, model)
