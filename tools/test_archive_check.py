#!/usr/bin/env python3
"""archive_check.py 的单测（stdlib unittest，合成仓走目录回退路径）。"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import archive_check as ac


def quiet_main(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = ac.main(argv)
    return rc

LAYOUT = {
    "version": 1,
    "profiles": {
        "skill-repo": {
            "description": "测试",
            "dirs": [
                {"path": "", "purpose": "根", "patterns": ["SKILL.md", ".archive-allow"],
                 "producer": "t"},
                {"path": "specs", "purpose": "t",
                 "patterns": ["modules.md", "archive-registry.json"],
                 "producer": "t"},
                {"path": "references", "purpose": "t",
                 "patterns": ["*.md", "*.json"], "producer": "t"},
                {"path": "tickets", "purpose": "t", "patterns": ["*.md"],
                 "nameRegex": "^\\d{2}-.+\\.md$", "producer": "t"},
                {"path": "lessons", "purpose": "t", "patterns": ["*.md"],
                 "producer": "t"},
                {"path": "fixtures", "purpose": "t", "patterns": ["*/**"],
                 "producer": "t"},
                {"path": "docs", "purpose": "t", "patterns": ["adr/*.md", "*.html", "*.png", "*.json"],
                 "producer": "t"},
            ],
        }
    },
}

REGISTRY = {
    "version": 1,
    "artifacts": [
        {"type": "skill-card", "pathPatterns": ["specs/modules.md"],
         "requiredFields": ["职责", "依赖"], "status": None},
        {"type": "ticket", "pathPatterns": ["tickets/*.md"],
         "requiredFields": ["Status"],
         "status": {"field": "Status", "values": ["todo", "doing", "done"],
                    "flippedBy": "L0"}},
        {"type": "lesson", "pathPatterns": ["lessons/*.md"],
         "requiredFields": ["做了什么", "取舍", "坑"], "status": None},
        {"type": "fixture", "pathPatterns": ["fixtures/*/assertions.json"],
         "requiredFields": ["assertions"], "status": None},
        {"type": "adr", "pathPatterns": ["docs/adr/*.md"],
         "requiredFields": ["状态", "日期", "结论"],
         "status": {"field": "状态", "values": ["提案", "已采纳"],
                    "flippedBy": "L0"}},
        {"type": "diagram", "pathPatterns": ["docs/*.html", "docs/*.png", "docs/*.json"],
         "requiredFields": [], "status": None},
    ],
}

CARD = "## skill: demo\n\n- 职责: x\n- 依赖:\n  - skill: `a`（外部）\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class RepoCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root / "SKILL.md", "---\nname: demo\n---\n")
        write(self.root / "references" / "repo-layout.json", json.dumps(LAYOUT))
        write(self.root / "specs" / "archive-registry.json", json.dumps(REGISTRY))
        write(self.root / "specs" / "modules.md", CARD)
        write(self.root / "tickets" / "01-x.md", "# 票\nStatus: done\n")
        write(self.root / "lessons" / "01-x.md", "# 日志\n## 做了什么\n## 取舍\n## 坑\n")

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        return ac.run(self.root)

    def kinds(self):
        return [v["kind"] for v in self.check()["violations"]]

    def test_clean_repo_passes(self):
        report = self.check()
        self.assertEqual(report["status"], "pass", report["violations"])
        self.assertEqual(report["profile"], "skill-repo")

    def test_unregistered_dir(self):
        write(self.root / "stray" / "x.md", "x")
        self.assertIn("unregistered-dir", self.kinds())

    def test_root_file_pattern_mismatch(self):
        write(self.root / "random.txt", "x")
        self.assertIn("pattern-mismatch", self.kinds())

    def test_ticket_name_discipline(self):
        write(self.root / "tickets" / "abc.md", "Status: done\n")
        self.assertIn("name-mismatch", self.kinds())

    def test_ticket_missing_status(self):
        write(self.root / "tickets" / "02-y.md", "# 无状态票\n")
        self.assertIn("missing-field", self.kinds())

    def test_ticket_bad_status_value(self):
        write(self.root / "tickets" / "02-y.md", "Status: 已完成\n")
        self.assertIn("bad-status", self.kinds())

    def test_lesson_missing_sections(self):
        write(self.root / "lessons" / "02-y.md", "# 只有标题\n")
        self.assertIn("missing-field", self.kinds())

    def test_adr_status_value_checked(self):
        write(self.root / "docs" / "adr" / "0001-x.md",
              "# ADR\n状态: 瞎写\n日期: 2026-09-17\n结论: x\n")
        self.assertIn("bad-status", self.kinds())

    def test_fixture_empty_assertions_rejected(self):
        write(self.root / "fixtures" / "demo" / "assertions.json",
              json.dumps({"assertions": []}))
        self.assertIn("missing-field", self.kinds())

    def test_skill_card_missing_field(self):
        write(self.root / "specs" / "modules.md", "## skill: demo\n\n- 职责: x\n")
        self.assertIn("missing-field", self.kinds())

    def test_allowlist_exempts(self):
        write(self.root / "docs" / "map.svg", "<svg/>")
        self.assertIn("pattern-mismatch", self.kinds())
        write(self.root / ".archive-allow", "docs/map.*  # archify 产物，待登记\n")
        report = self.check()
        self.assertEqual(report["status"], "pass", report["violations"])
        self.assertEqual(report["exempted"][0]["reason"], "archify 产物，待登记")

    def test_binary_artifact_without_fields_passes(self):
        # 图表交付物（png 等二进制）无字段要求时不得因读文本崩溃/误报
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / "docs" / "map.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe binary")
        self.assertEqual(self.check()["status"], "pass", self.check()["violations"])

    def test_binary_artifact_with_fields_is_violation(self):
        registry = {"version": 1, "artifacts": [
            {"type": "strict-doc", "pathPatterns": ["docs/*.png"],
             "requiredFields": ["标题"], "status": None},
        ]}
        write(self.root / "specs" / "archive-registry.json", json.dumps(registry))
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / "docs" / "map.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe binary")
        kinds = [v["kind"] for v in ac.run(self.root)["violations"]]
        self.assertIn("missing-field", kinds)

    def test_allowlist_without_reason_is_config_error(self):
        write(self.root / ".archive-allow", "docs/map.html\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_exclude_dirs_skipped(self):
        write(self.root / "__pycache__" / "x.pyc", "x")
        write(self.root / ".git" / "config", "x")  # 无真实 git 仓时也不查
        write(self.root / "specs" / ".DS_Store", "x")
        self.assertEqual(self.check()["status"], "pass")

    def test_main_exit_codes_and_json(self):
        self.assertEqual(quiet_main(["--root", str(self.root), "--json"]), 0)
        write(self.root / "stray" / "x.md", "x")
        self.assertEqual(quiet_main(["--root", str(self.root), "--json"]), 1)

    def test_unknown_profile_is_config_error(self):
        with self.assertRaises(ValueError):
            ac.run(self.root, profile="nope")


if __name__ == "__main__":
    unittest.main()
