#!/usr/bin/env python3
"""List game records that need a walkthrough note.

Reads every category file under ``data/*.json`` (read-only) and, for each
hardware group's game records, prints one JSON Lines record per game that:

  * has a ``play_status`` other than ``"not_started"`` (a missing
    ``play_status`` key is treated as ``"not_started"``), AND
  * does not already have a non-empty ``walkthrough_note_path``.

Each output line has the shape::

    {"file": "data/8_sie.json", "hardware": "PlayStation4", "soft_title": "..."}

Records that are missing the ``soft_title`` key (malformed data observed in
the wild) are skipped with a warning on stderr instead of crashing the scan.

This script performs no writes; it only reads ``data/*.json``.

Usage:
    python tools/find_missing_walkthrough_notes.py

No command-line arguments are required. Run from the repository root so the
relative ``data/`` path resolves correctly.
"""
import json
import sys
from pathlib import Path

DEFAULT_DATA_DIR = "data"


def find_data_files(data_dir=DEFAULT_DATA_DIR):
    """Return the sorted list of category JSON files under ``data_dir``."""
    return sorted(Path(data_dir).glob("*.json"))


def iter_target_records(data, file_label):
    """Yield target record dicts for a single parsed category JSON document.

    ``data`` is the parsed top-level dict (expected to contain a
    ``hardware_name`` mapping of hardware name -> list of game record dicts).
    ``file_label`` is the string to use as the ``file`` field in the output
    (e.g. ``"data/8_sie.json"``).
    """
    hardware_map = data.get("hardware_name", {}) if isinstance(data, dict) else {}
    for hardware, records in hardware_map.items():
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict) or "soft_title" not in record:
                print(
                    f"Warning: skipping record without 'soft_title' in "
                    f"{file_label} [{hardware}]: {record!r}",
                    file=sys.stderr,
                )
                continue

            play_status = record.get("play_status") or "not_started"
            if play_status == "not_started":
                continue

            if record.get("walkthrough_note_path"):
                continue

            yield {
                "file": file_label,
                "hardware": hardware,
                "soft_title": record["soft_title"],
            }


def run(data_dir=DEFAULT_DATA_DIR):
    """Scan all category JSON files under ``data_dir`` and print JSON Lines."""
    for path in find_data_files(data_dir):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Warning: failed to read {path}: {exc}", file=sys.stderr)
            continue

        file_label = path.as_posix()
        for target in iter_target_records(data, file_label):
            print(json.dumps(target, ensure_ascii=False))


def main():
    run(DEFAULT_DATA_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
