#!/usr/bin/env python3
"""Link a generated walkthrough note HTML file to its game record.

Given a category JSON file under ``data/*.json``, a hardware name, a game
title (matched exactly against ``soft_title``), and a walkthrough note path,
this script locates the single matching record and sets its
``walkthrough_note_path`` field to the given path, then writes the whole
file back in place.

Safety rules:

  * If zero records match the given hardware/title pair, nothing is written
    and the script exits with a non-zero status.
  * If two or more records match, nothing is written and the script exits
    with a non-zero status (hardware + title is expected to be unique).
  * If the single matching record already has a non-empty
    ``walkthrough_note_path``, it is left untouched (not overwritten) and the
    script reports a skip and exits with status 0 (idempotent, not an
    error).
  * Otherwise the record's ``walkthrough_note_path`` is set and the entire
    file is rewritten using the same format as the existing data files:
    UTF-8, ``ensure_ascii=False``, 2-space indent, and whichever line-ending
    convention (CRLF or LF) and trailing-newline state the original file
    already used. No other record or field is modified.

    Note: the 12 real ``data/*.json`` files are NOT uniform on line endings
    -- 10 of them use CRLF and only 2 (``data/1_nintendo.json``,
    ``data/8_sie.json``) use bare LF -- and 10 of the 12 have no trailing
    newline at all. This script detects both properties per-file from the
    raw bytes and reproduces them exactly, rather than assuming one style.

Usage:
    python tools/link_walkthrough_note.py --file data/8_sie.json \\
        --hardware PlayStation4 \\
        --title "バイオハザード7 レジデント イービル☑" \\
        --path "game_notes/SIE/PlayStation4/バイオハザード7 レジデント イービル.html"
"""
import argparse
import json
import sys
from pathlib import Path


def _ensure_utf8_stdio():
    """Force stdout/stderr to UTF-8 so titles with symbols outside the
    active Windows console code page (e.g. cp932), such as "☑", don't
    crash the script when printed."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


class LinkError(Exception):
    """Raised for input errors that must abort without writing anything."""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Set walkthrough_note_path for a single game record."
    )
    parser.add_argument(
        "--file", required=True, help="Path to the data/*.json category file"
    )
    parser.add_argument(
        "--hardware", required=True, help="Hardware name key under hardware_name"
    )
    parser.add_argument(
        "--title", required=True, help="soft_title to match exactly"
    )
    parser.add_argument(
        "--path", required=True, help="walkthrough_note_path value to write"
    )
    return parser.parse_args(argv)


def find_matching_records(data, hardware, title):
    """Return the list of records under ``hardware`` whose soft_title == title."""
    hardware_map = data.get("hardware_name", {}) if isinstance(data, dict) else {}
    records = hardware_map.get(hardware, [])
    if not isinstance(records, list):
        return []
    return [
        record
        for record in records
        if isinstance(record, dict) and record.get("soft_title") == title
    ]


def link_note(file_path, hardware, title, note_path):
    """Perform the link operation for a single record.

    Returns a tuple ``(status, message)`` where ``status`` is either
    ``"linked"`` or ``"skipped"``. Raises ``LinkError`` on any condition
    that must abort without writing anything (file missing/unreadable, zero
    matches, or multiple matches).
    """
    path = Path(file_path)
    if not path.is_file():
        raise LinkError(f"File not found: {file_path}")

    try:
        raw_bytes = path.read_bytes()
        data = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LinkError(f"Failed to read {file_path}: {exc}") from exc

    # Preserve the original file's exact newline convention and
    # trailing-newline state. The real data/*.json files are inconsistent:
    # most use CRLF with no trailing newline, a couple use bare LF with a
    # trailing newline. Rewriting must not change either property.
    newline_style = "\r\n" if b"\r\n" in raw_bytes else "\n"
    had_trailing_newline = raw_bytes.endswith(b"\n")

    matches = find_matching_records(data, hardware, title)

    if len(matches) == 0:
        raise LinkError(
            f"No record found matching hardware={hardware!r} title={title!r} "
            f"in {file_path}"
        )
    if len(matches) >= 2:
        raise LinkError(
            f"Found {len(matches)} records matching hardware={hardware!r} "
            f"title={title!r} in {file_path}; refusing to write "
            "(hardware + title must be unique)"
        )

    record = matches[0]
    existing = record.get("walkthrough_note_path")
    if existing:
        return "skipped", (
            f"Skipped (already linked): hardware={hardware!r} title={title!r} "
            f"in {file_path} already has walkthrough_note_path={existing!r}"
        )

    record["walkthrough_note_path"] = note_path

    text = json.dumps(data, ensure_ascii=False, indent=2)
    if newline_style != "\n":
        text = text.replace("\n", newline_style)
    if had_trailing_newline:
        text += newline_style

    # newline="" disables any further newline translation so the exact
    # bytes chosen above are what get written, regardless of platform.
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

    return "linked", (
        f"Linked: hardware={hardware!r} title={title!r} in {file_path} "
        f"-> {note_path}"
    )


def main(argv=None):
    _ensure_utf8_stdio()
    args = parse_args(argv)
    try:
        _status, message = link_note(args.file, args.hardware, args.title, args.path)
    except LinkError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
