"""Unit tests for PyScope grader helpers + oracle 10/10.

Run: python3 -m unittest discover -s tests -v
     python3 graders/run_all.py
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "graders"))

from common import (  # noqa: E402
    extract_final_answer,
    grade_payload,
    list_tasks,
    load_json,
    parse_json_answer,
)


class ExtractFinalAnswerTests(unittest.TestCase):
    def test_prefix(self):
        self.assertEqual(
            extract_final_answer('noise\nFINAL_ANSWER: {"stdout": "x"}'),
            '{"stdout": "x"}',
        )

    def test_fenced_json_fallback(self):
        raw = '```json\n{"stdout": "z"}\n```'
        self.assertIn("stdout", extract_final_answer(raw))

    def test_empty(self):
        self.assertEqual(extract_final_answer(""), "")


class ParseAndGradeTests(unittest.TestCase):
    def test_exact_match(self):
        r = grade_payload('FINAL_ANSWER: {"stdout": "hi"}', {"stdout": "hi"})
        self.assertTrue(r["pass"], r)

    def test_newline_normalization(self):
        r = grade_payload('FINAL_ANSWER: {"stdout": "hi\\n"}', {"stdout": "hi"})
        self.assertTrue(r["pass"], r)
        r2 = grade_payload('FINAL_ANSWER: {"stdout": "hi"}', {"stdout": "hi\n"})
        self.assertTrue(r2["pass"], r2)

    def test_mismatch(self):
        r = grade_payload('FINAL_ANSWER: {"stdout": "a"}', {"stdout": "b"})
        self.assertFalse(r["pass"])

    def test_unparseable(self):
        r = grade_payload("no answer here", {"stdout": "x"})
        self.assertFalse(r["pass"])

    def test_parse_json_answer_object(self):
        self.assertEqual(
            parse_json_answer('FINAL_ANSWER: {"stdout": "ok"}'),
            {"stdout": "ok"},
        )


class OracleAndTaskShapeTests(unittest.TestCase):
    def test_ten_tasks(self):
        tasks = list_tasks()
        self.assertEqual(len(tasks), 10)
        for t in tasks:
            for name in ("prompt.md", "answer.json", "grade.py", "rationale.md", "task.json"):
                self.assertTrue((t / name).exists(), f"missing {t.name}/{name}")

    def test_oracle_ten_of_ten(self):
        for task in list_tasks():
            expected = load_json(task / "answer.json")
            fake = "FINAL_ANSWER: " + json.dumps(expected)
            result = grade_payload(fake, expected)
            self.assertTrue(result["pass"], f"{task.name}: {result}")

    def test_summary_matrix_matches_headline(self):
        """Guard against drifting README / results page numbers."""
        summary = load_json(ROOT / "results" / "summary.json")
        by = summary["by_model"]
        # Measured pass@1 means from the submitted 90-trial matrix (do not invent).
        expected = {
            "muse-wonder-1.0": 0.0667,
            "muse-spark-open-1026": 0.1333,
            "Beam-1.0-501B-A23B": 0.7667,
        }
        for model, want in expected.items():
            got = by[model]["pass_at_1_mean"]
            self.assertAlmostEqual(got, want, places=3, msg=model)
        self.assertEqual(summary.get("oracle"), "10/10")


if __name__ == "__main__":
    unittest.main()
