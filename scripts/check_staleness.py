"""
Ask Claude whether a doc section is still accurate given a code diff.

Usage:
    python scripts/check_staleness.py <changed_file> <doc_file> <section_heading>
"""

import subprocess
import sys

import anthropic
from dotenv import load_dotenv

from extract_section import extract_section

load_dotenv()

SCHEMA = {
    "type": "object",
    "properties": {
        "stale": {
            "type": "boolean",
            "description": "True if the doc section no longer accurately describes the code.",
        },
        "reason": {
            "type": "string",
            "description": "Brief explanation of why it is or isn't stale.",
        },
        "suggested_fix": {
            "type": "string",
            "description": "The corrected doc section text. Empty string if not stale.",
        },
    },
    "required": ["stale", "reason", "suggested_fix"],
    "additionalProperties": False,
}


def get_code_diff(changed_file: str) -> str:
    result = subprocess.run(
        ["git", "diff", "HEAD", "--", changed_file],
        capture_output=True,
        text=True,
        check=True,
    )
    diff = result.stdout.strip()
    if not diff:
        # No uncommitted changes to this file -- show its current full content instead.
        with open(changed_file, "r", encoding="utf-8") as f:
            diff = f.read()
    return diff


def check_staleness(changed_file: str, doc_file: str, heading: str) -> dict:
    code_diff = get_code_diff(changed_file)
    doc_section = extract_section(doc_file, heading)

    client = anthropic.Anthropic()

    prompt = f"""A code file changed. Decide whether the following documentation section is now stale (inaccurate).

CODE DIFF for {changed_file}:
{code_diff}

DOCUMENTATION SECTION (from {doc_file}, heading "{heading}"):
{doc_section}

Is this documentation section still accurate given the code change? If not, provide corrected text for the section."""

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )

    import json

    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def main():
    if len(sys.argv) != 4:
        print("Usage: python scripts/check_staleness.py <changed_file> <doc_file> <section_heading>")
        sys.exit(1)

    changed_file, doc_file, heading = sys.argv[1], sys.argv[2], sys.argv[3]
    result = check_staleness(changed_file, doc_file, heading)

    print(f"Stale: {result['stale']}")
    print(f"Reason: {result['reason']}")
    if result["stale"]:
        print(f"\nSuggested fix:\n{result['suggested_fix']}")


if __name__ == "__main__":
    main()
