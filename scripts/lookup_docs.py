"""
Given a code file path, find which doc sections describe it,
according to docs-map.json.

Usage:
    python scripts/lookup_docs.py src/example/hello.py
"""

import json
import sys
from pathlib import Path

MAP_FILE = Path(__file__).parent.parent / "docs-map.json"


def load_map() -> dict:
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_affected_docs(changed_file: str, doc_map: dict) -> list:
    return doc_map.get(changed_file, [])


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/lookup_docs.py <changed_file_path>")
        sys.exit(1)

    changed_file = sys.argv[1]
    doc_map = load_map()
    matches = find_affected_docs(changed_file, doc_map)

    if not matches:
        print(f"No docs mapped to '{changed_file}'.")
        return

    print(f"'{changed_file}' affects {len(matches)} doc section(s):")
    for match in matches:
        print(f"  - {match['doc']} -> \"{match['section']}\"")


if __name__ == "__main__":
    main()
