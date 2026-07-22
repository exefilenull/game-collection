"""Unit tests for tools/find_missing_walkthrough_notes.py

These tests use small in-memory dummy JSON-like dicts only; they never read
the real data/*.json files.

Run with:
    /c/Python313/python -m unittest tools/test_find_missing_walkthrough_notes.py -v
"""
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import find_missing_walkthrough_notes as fmwn  # noqa: E402


def make_data(hardware_name_dict):
    return {"category": "DummyCategory", "hardware_name": hardware_name_dict}


class IterTargetRecordsTests(unittest.TestCase):
    def test_not_started_play_status_is_excluded(self):
        data = make_data({
            "DummyHW": [
                {"soft_title": "GameA", "play_status": "not_started"},
            ]
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [])

    def test_missing_play_status_key_is_excluded(self):
        data = make_data({
            "DummyHW": [
                {"soft_title": "GameB"},
            ]
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [])

    def test_playing_status_without_note_path_is_included(self):
        data = make_data({
            "DummyHW": [
                {"soft_title": "GameC", "play_status": "playing"},
            ]
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [
            {"file": "data/dummy.json", "hardware": "DummyHW", "soft_title": "GameC"},
        ])

    def test_cleared_status_without_note_path_is_included(self):
        data = make_data({
            "DummyHW": [
                {"soft_title": "GameD", "play_status": "cleared"},
            ]
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [
            {"file": "data/dummy.json", "hardware": "DummyHW", "soft_title": "GameD"},
        ])

    def test_already_linked_record_is_excluded_even_if_playing(self):
        data = make_data({
            "DummyHW": [
                {
                    "soft_title": "GameE",
                    "play_status": "playing",
                    "walkthrough_note_path": "game_notes/Dummy/DummyHW/GameE.html",
                },
            ]
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [])

    def test_already_linked_record_is_excluded_even_if_cleared(self):
        data = make_data({
            "DummyHW": [
                {
                    "soft_title": "GameF",
                    "play_status": "cleared",
                    "walkthrough_note_path": "game_notes/Dummy/DummyHW/GameF.html",
                },
            ]
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [])

    def test_empty_string_note_path_does_not_exclude(self):
        data = make_data({
            "DummyHW": [
                {"soft_title": "GameG", "play_status": "playing", "walkthrough_note_path": ""},
            ]
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [
            {"file": "data/dummy.json", "hardware": "DummyHW", "soft_title": "GameG"},
        ])

    def test_record_missing_soft_title_is_skipped_without_crash(self):
        data = make_data({
            "DummyHW": [
                {"play_status": "playing"},  # malformed: no soft_title key
                {"soft_title": "GameH", "play_status": "playing"},
            ]
        })
        stderr_buf = io.StringIO()
        with contextlib.redirect_stderr(stderr_buf):
            results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [
            {"file": "data/dummy.json", "hardware": "DummyHW", "soft_title": "GameH"},
        ])
        # A warning should have been emitted to stderr for the malformed record.
        self.assertIn("soft_title", stderr_buf.getvalue())

    def test_real_world_malformed_record_shape_is_skipped(self):
        # Mirrors a malformed record shape actually observed in data/8_sie.json
        # (uses "soft_title:" with a trailing colon instead of "soft_title").
        data = make_data({
            "DummyHW": [
                {
                    "soft_title:": "",
                    "collected_new": False,
                    "collected_old": False,
                    "game_cleared": False,
                    "dont_collect": False,
                    "game_category:": "",
                    "release_day": "2020-09-08",
                },
            ]
        })
        stderr_buf = io.StringIO()
        with contextlib.redirect_stderr(stderr_buf):
            results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(results, [])

    def test_multiple_hardware_groups_are_all_scanned(self):
        data = make_data({
            "HW1": [{"soft_title": "GameI", "play_status": "playing"}],
            "HW2": [{"soft_title": "GameJ", "play_status": "cleared"}],
        })
        results = list(fmwn.iter_target_records(data, "data/dummy.json"))
        self.assertEqual(
            sorted(results, key=lambda r: r["soft_title"]),
            [
                {"file": "data/dummy.json", "hardware": "HW1", "soft_title": "GameI"},
                {"file": "data/dummy.json", "hardware": "HW2", "soft_title": "GameJ"},
            ],
        )


class MainSmokeTests(unittest.TestCase):
    """Exercises the full file-reading pipeline against a temporary fake data dir."""

    def test_main_reads_json_files_from_directory_and_prints_json_lines(self):
        import glob
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            data_dir = os.path.join(tmp_dir, "data")
            os.makedirs(data_dir)
            fake_path = os.path.join(data_dir, "1_dummy.json")
            with open(fake_path, "w", encoding="utf-8") as fh:
                json.dump(
                    make_data({
                        "DummyHW": [
                            {"soft_title": "GameK", "play_status": "playing"},
                            {"soft_title": "GameL", "play_status": "not_started"},
                        ]
                    }),
                    fh,
                    ensure_ascii=False,
                    indent=2,
                )

            files = fmwn.find_data_files(data_dir)
            self.assertEqual(len(files), 1)

            stdout_buf = io.StringIO()
            with contextlib.redirect_stdout(stdout_buf):
                fmwn.run(data_dir)

            lines = [line for line in stdout_buf.getvalue().splitlines() if line.strip()]
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertEqual(record["soft_title"], "GameK")
            self.assertEqual(record["hardware"], "DummyHW")


if __name__ == "__main__":
    unittest.main()
