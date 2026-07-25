"""
CI entry point: compare two git refs, find any doc sections that look
stale as a result, and write a Markdown report for a PR comment.

Usage:
    python scripts/ci_check.py <base_ref> <head_ref> <output_file>
"""

import sys

from check_staleness import check_staleness
from find_stale_candidates import get_changed_files
from lookup_docs import find_affected_docs, load_map


def build_report(base_ref: str, head_ref: str) -> str:
    changed_files = get_changed_files(base_ref, head_ref)
    doc_map = load_map()

    findings = []
    for changed_file in changed_files:
        for match in find_affected_docs(changed_file, doc_map):
            result = check_staleness(changed_file, match["doc"], match["section"])
            if result["stale"]:
                findings.append((changed_file, match, result))

    if not findings:
        return ""

    lines = ["## \U0001F916 Doc Staleness Check", ""]
    for changed_file, match, result in findings:
        lines.append(f"### ⚠️ `{match['doc']}` — \"{match['section']}\"")
        lines.append(f"Changed file: `{changed_file}`")
        lines.append("")
        lines.append(f"**Why it's stale:** {result['reason']}")
        lines.append("")
        lines.append("**Suggested fix:**")
        lines.append("```markdown")
        lines.append(result["suggested_fix"])
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 4:
        print("Usage: python scripts/ci_check.py <base_ref> <head_ref> <output_file>")
        sys.exit(1)

    base_ref, head_ref, output_file = sys.argv[1], sys.argv[2], sys.argv[3]
    report = build_report(base_ref, head_ref)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    if report:
        print(f"Found stale docs. Report written to {output_file}.")
    else:
        print("No stale docs found.")


if __name__ == "__main__":
    main()
