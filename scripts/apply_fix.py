"""
If a doc section is stale, write Claude's suggested fix to a new git branch
and commit it there -- never touching the branch you started on.

Usage:
    python scripts/apply_fix.py <changed_file> <doc_file> <section_heading>
"""

import subprocess
import sys

from check_staleness import check_staleness
from replace_section import replace_section


def run_git(*args: str) -> None:
    subprocess.run(["git", *args], check=True)


def apply_fix(changed_file: str, doc_file: str, heading: str) -> None:
    result = check_staleness(changed_file, doc_file, heading)

    if not result["stale"]:
        print("Doc section is still accurate -- nothing to do.")
        return

    print(f"Stale doc detected: {result['reason']}")

    original_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    safe_name = doc_file.replace("/", "-").replace(".", "-")
    fix_branch = f"auto-fix-docs-{safe_name}"

    run_git("checkout", "-b", fix_branch)
    try:
        replace_section(doc_file, heading, result["suggested_fix"])
        run_git("add", doc_file)
        run_git("commit", "-m", f"docs: update '{heading}' in {doc_file} after code change")
        print(f"Fix committed to branch '{fix_branch}'.")
        print(f"Push it and open a PR with: git push -u origin {fix_branch}")
    finally:
        run_git("checkout", original_branch)


def main():
    if len(sys.argv) != 4:
        print("Usage: python scripts/apply_fix.py <changed_file> <doc_file> <section_heading>")
        sys.exit(1)

    apply_fix(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
