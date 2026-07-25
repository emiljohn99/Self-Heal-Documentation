"""
Replace one markdown section (a heading and everything under it, until the
next heading of the same or higher level) with new text.
"""

from extract_section import find_section_bounds, project_path


def replace_section(doc_path: str, heading: str, new_section_text: str) -> None:
    full_path = project_path(doc_path)
    lines = full_path.read_text(encoding="utf-8").splitlines()
    start, end = find_section_bounds(lines, heading)

    new_lines = lines[:start] + new_section_text.splitlines() + lines[end:]
    full_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
