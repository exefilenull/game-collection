"""Unit tests for tools/link_walkthrough_note.py.

These tests operate exclusively on throwaway JSON files created under the
scratchpad directory (never under the repository's real ``data/`` files).
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRATCHPAD = Path(
    r"C:\Users\T\AppData\Local\Temp\claude\c--Users-T-source-game-collection"
    r"\d11161b5-ecfd-4115-b17c-5bfe477362a5\scratchpad"
)
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "tools" / "link_walkthrough_note.py"

TITLE_A = "バイオハザード7 レジデント イービル☑"
TITLE_B = "サンプルタイトルB"

SAMPLE_DATA = {
    "category": "SIE",
    "hardware_name": {
        "PlayStation4": [
            {
                "soft_title": TITLE_A,
                "collected_new": True,
                "collected_old": False,
                "walkthrough_note_path": "",
            },
            {
                "soft_title": TITLE_B,
                "collected_new": False,
                "collected_old": False,
                "walkthrough_note_path": "",
            },
        ]
    },
}


def write_json(path, data, newline_style="\n", trailing_newline=True):
    """Write ``data`` as JSON with a chosen newline style and trailing state.

    The real ``data/*.json`` files are inconsistent on both properties: 10
    of the 12 category files use CRLF line endings with NO trailing
    newline, while the other 2 (``data/1_nintendo.json``,
    ``data/8_sie.json``) use bare LF WITH a trailing newline. Tests default
    to the LF/trailing-newline shape for backward compatibility with
    existing cases, but dedicated tests below exercise the CRLF/no-trailing
    shape explicitly, since it is the more common real-data shape.
    """
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if newline_style != "\n":
        text = text.replace("\n", newline_style)
    if trailing_newline:
        text += newline_style
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def read_raw(path):
    with open(path, "rb") as fh:
        return fh.read()


class LinkWalkthroughNoteTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(dir=str(SCRATCHPAD), prefix="link_test_")
        self.data_file = Path(self.tmpdir) / "sample.json"
        write_json(self.data_file, SAMPLE_DATA)
        self.original_bytes = read_raw(self.data_file)

    def run_script(self, hardware, title, note_path):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--file",
                str(self.data_file),
                "--hardware",
                hardware,
                "--title",
                title,
                "--path",
                note_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_no_match_errors_and_leaves_file_unchanged(self):
        result = self.run_script("PlayStation4", "存在しないタイトル", "game_notes/x.html")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(read_raw(self.data_file), self.original_bytes)

    def test_multiple_matches_errors_and_leaves_file_unchanged(self):
        data = json.loads(self.original_bytes.decode("utf-8"))
        dup = dict(data["hardware_name"]["PlayStation4"][0])
        data["hardware_name"]["PlayStation4"].append(dup)
        write_json(self.data_file, data)
        before = read_raw(self.data_file)

        result = self.run_script("PlayStation4", TITLE_A, "game_notes/x.html")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(read_raw(self.data_file), before)

    def test_single_match_sets_path_without_touching_others(self):
        note_path = "game_notes/SIE/PlayStation4/バイオハザード7.html"

        result = self.run_script("PlayStation4", TITLE_A, note_path)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(self.data_file, encoding="utf-8") as fh:
            data = json.load(fh)
        target = data["hardware_name"]["PlayStation4"][0]
        other = data["hardware_name"]["PlayStation4"][1]
        self.assertEqual(target["walkthrough_note_path"], note_path)
        self.assertEqual(target["collected_new"], True)
        self.assertEqual(other, SAMPLE_DATA["hardware_name"]["PlayStation4"][1])

    def test_already_set_is_skipped_without_overwrite(self):
        data = json.loads(self.original_bytes.decode("utf-8"))
        data["hardware_name"]["PlayStation4"][0]["walkthrough_note_path"] = "game_notes/existing.html"
        write_json(self.data_file, data)
        before = read_raw(self.data_file)

        result = self.run_script("PlayStation4", TITLE_A, "game_notes/new.html")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(read_raw(self.data_file), before)

    def test_format_preserved_after_write_lf_with_trailing_newline(self):
        # self.data_file was written by setUp with the LF + trailing-newline
        # shape (matches data/1_nintendo.json and data/8_sie.json).
        self.run_script(
            "PlayStation4",
            TITLE_A,
            "game_notes/SIE/PlayStation4/バイオハザード7.html",
        )

        raw = read_raw(self.data_file)
        self.assertNotIn(b"\r\n", raw)
        self.assertNotIn(b"\\u2611", raw)
        text = raw.decode("utf-8")
        self.assertTrue(text.endswith("\n"), "expected trailing newline to be preserved")
        self.assertIn('\n    "PlayStation4": [\n', text)

    def test_format_preserved_after_write_crlf_without_trailing_newline(self):
        # Matches the more common real-data shape: 10 of the 12
        # data/*.json files use CRLF line endings and end with a bare "}"
        # with no trailing newline (e.g. data/10_casio.json).
        crlf_file = Path(self.tmpdir) / "sample_crlf_no_trailing_newline.json"
        write_json(crlf_file, SAMPLE_DATA, newline_style="\r\n", trailing_newline=False)
        before = read_raw(crlf_file)
        self.assertFalse(before.endswith(b"\n"))
        self.assertIn(b"\r\n", before)
        lf_count_before = before.count(b"\n")
        crlf_count_before = before.count(b"\r\n")
        self.assertEqual(
            lf_count_before, crlf_count_before, "fixture should be pure CRLF, no lone LF"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--file",
                str(crlf_file),
                "--hardware",
                "PlayStation4",
                "--title",
                TITLE_A,
                "--path",
                "game_notes/SIE/PlayStation4/バイオハザード7.html",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        raw = read_raw(crlf_file)
        self.assertFalse(
            raw.endswith(b"\n"),
            "no-trailing-newline files must stay without a trailing newline",
        )
        self.assertTrue(raw.endswith(b"}"))
        lf_count_after = raw.count(b"\n")
        crlf_count_after = raw.count(b"\r\n")
        self.assertEqual(
            lf_count_after,
            crlf_count_after,
            "every line ending in the output must remain CRLF (no lone LF introduced)",
        )
        self.assertGreater(crlf_count_after, 0)
        text = raw.decode("utf-8")
        self.assertIn('\r\n    "PlayStation4": [\r\n', text)
        with open(crlf_file, encoding="utf-8") as fh:
            data = json.load(fh)
        target = data["hardware_name"]["PlayStation4"][0]
        self.assertEqual(
            target["walkthrough_note_path"],
            "game_notes/SIE/PlayStation4/バイオハザード7.html",
        )


if __name__ == "__main__":
    unittest.main()
