"""
Find which doc sections MIGHT be stale, based on which code files changed
between two git refs.

Usage:
    python scripts/find_stale_candidates.py             # uncommitted changes vs last commit
    python scripts/find_stale_candidates.py main HEAD    # changes between two branches/commits
"""

import subprocess
import sys

from lookup_docs import load_map, find_affected_docs


def get_changed_files(base_ref: str = "HEAD", head_ref: str | None = None) -> list:
    """Return a list of file paths changed between two git refs.

    If head_ref is None, this compares base_ref against your current
    uncommitted working directory changes instead of another commit.
    """
    if head_ref is None:
        args = ["git", "diff", "--name-only", base_ref]
    else:
        args = ["git", "diff", "--name-only", base_ref, head_ref]

    result = subprocess.run(args, capture_output=True, text=True, check=True)
    files = result.stdout.strip().splitlines()
    return [f for f in files if f]  # drop any blank lines


def main():
    if len(sys.argv) == 1:
        base_ref, head_ref = "HEAD", None
    elif len(sys.argv) == 3:
        base_ref, head_ref = sys.argv[1], sys.argv[2]
    else:
        print("Usage: python scripts/find_stale_candidates.py [base_ref head_ref]")
        sys.exit(1)

    changed_files = get_changed_files(base_ref, head_ref)

    if not changed_files:
        print("No changed files found.")
        return

    doc_map = load_map()
    found_any = False

    for changed_file in changed_files:
        matches = find_affected_docs(changed_file, doc_map)
        if matches:
            found_any = True
            print(f"'{changed_file}' changed -> check:")
            for match in matches:
                print(f"  - {match['doc']} -> \"{match['section']}\"")

    if not found_any:
        print(f"{len(changed_files)} file(s) changed, but none are mapped to docs.")


if __name__ == "__main__":
    main()
