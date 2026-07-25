"""
Pull one markdown section (a heading and everything under it, until the
next heading of the same or higher level) out of a doc file.
"""

from pathlib import Path


def project_path(doc_path: str) -> Path:
    return Path(__file__).parent.parent / doc_path


def find_section_bounds(lines: list, heading: str) -> tuple:
    """Return (start, end) line indices of the section under `heading`."""
    start = None
    start_level = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#") and stripped.lstrip("#").strip() == heading:
            start = i
            start_level = len(stripped) - len(stripped.lstrip("#"))
            break

    if start is None:
        raise ValueError(f"Heading '{heading}' not found")

    end = len(lines)
    for i in range(start + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            if level <= start_level:
                end = i
                break

    return start, end


def extract_section(doc_path: str, heading: str) -> str:
    lines = project_path(doc_path).read_text(encoding="utf-8").splitlines()
    start, end = find_section_bounds(lines, heading)
    return "\n".join(lines[start:end]).strip()
