#!/usr/bin/env python3
"""skill_deps_check.py 的单测（stdlib unittest）。"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import skill_deps_check as sdc


def quiet_main(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = sdc.main(argv)
    return rc


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


CARD_MD = """# modules.md

## skill: alpha

- 职责: 测试用 skill
- 层: L1 工序
- 目录: skills/alpha/
- 触发面: 测试
- reads: 所在项目的 `docs/**`、`specs/**`；自身 `references/**`
- writes: 无
- 依赖:
  - skill: `beta`（外部）
  - script: `tools/runner.py`
  - data: `fixtures/**`
- Seam 与出厂集: fixtures/alpha/
- 边界: 无
"""


class ParseCardTest(unittest.TestCase):
    def test_parse_card_fields(self):
        cards = sdc.parse_cards(CARD_MD)
        card = cards["alpha"]
        self.assertEqual(card.skill_deps, {"beta": True})
        self.assertEqual(card.script_deps, ["tools/runner.py"])
        self.assertEqual(card.data_patterns, ["fixtures/**"])
        self.assertIn("docs/**", card.declared_patterns)
        self.assertIn("specs/**", card.declared_patterns)
        self.assertIn("fixtures/**", card.declared_patterns)

    def test_card_section_stops_at_next_heading(self):
        cards = sdc.parse_cards(CARD_MD + "\n## 边界规则\n\n| 禁止 | 例外 |\n")
        self.assertEqual(list(cards), ["alpha"])


class TokenExtractionTest(unittest.TestCase):
    def test_extracts_backticked_paths(self):
        text = "读 `docs/prd.md` 和 `references/x.md`，跑 `python3 tools/x.py` 命令"
        self.assertEqual(sdc.extract_path_tokens(text),
                         ["docs/prd.md", "references/x.md"])

    def test_skips_placeholder_url_command_prose(self):
        text = ("`tools/<名>` `https://x.io/a.md` `npx skills add a/b` "
                "`不适用（N/A + 理由）` `docs/adr/NNNN-<标题>.md`")
        self.assertEqual(sdc.extract_path_tokens(text), [])

    def test_extension_only_token(self):
        self.assertEqual(sdc.extract_path_tokens("见 `CONTEXT.md`"), ["CONTEXT.md"])


class RepoCase(unittest.TestCase):
    """搭临时单 skill 仓跑端到端。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "alpha"
        self.root.mkdir(parents=True)
        write(self.root / "SKILL.md", "---\nname: alpha\n---\n# alpha\n")
        write(self.root / "specs" / "modules.md", CARD_MD)
        write(self.root / "tools" / "runner.py", "# stub\n")

    def tearDown(self):
        self.tmp.cleanup()

    def violations(self):
        return sdc.run(self.root)["violations"]

    def test_clean_repo_passes(self):
        write(self.root / "SKILL.md",
              "读 `references/rule.md` 与被治理项目的 `docs/prd.md`；"
              "脚本 `tools/runner.py`。\n")
        write(self.root / "references" / "rule.md", "# 规约\n")
        report = sdc.run(self.root)
        self.assertEqual(report["status"], "pass", report["violations"])

    def test_undeclared_path_is_violation(self):
        write(self.root / "SKILL.md", "顺手读 `secret/plan.md`\n")
        # secret/ 不在已知区域 → 散文碎片跳过；用已知但未声明的区域试
        write(self.root / "SKILL.md", "顺手读 `tickets/99-x.md`\n")
        kinds = [v["kind"] for v in self.violations()]
        self.assertIn("undeclared", kinds)

    def test_dangling_own_reference_is_violation(self):
        write(self.root / "SKILL.md", "见 `references/not-exist.md`\n")
        kinds = [v["kind"] for v in self.violations()]
        self.assertIn("dangling", kinds)

    def test_cross_skill_private_reference_is_violation(self):
        beta = self.root.parent / "beta"
        write(beta / "SKILL.md", "---\nname: beta\n---\n")
        write(self.root / "SKILL.md", "模板见 `beta/references/private.md`\n")
        v = [v for v in self.violations() if v["kind"] == "cross-skill-private"]
        self.assertEqual(len(v), 1)

    def test_declared_skill_public_card_ok(self):
        beta = self.root.parent / "beta"
        write(beta / "SKILL.md", "---\nname: beta\n---\n")
        write(self.root / "SKILL.md", "调用 `beta/SKILL.md` 暴露的面\n")
        self.assertNotIn("cross-skill-private",
                         [v["kind"] for v in self.violations()])

    def test_undeclared_own_script_is_violation(self):
        write(self.root / "tools" / "evil.py", "# stub\n")
        write(self.root / "SKILL.md", "跑 `tools/evil.py`\n")
        kinds = [v["kind"] for v in self.violations()]
        self.assertIn("undeclared-script", kinds)

    def test_allowlist_exempts_with_reason(self):
        write(self.root / "SKILL.md", "模板见 `beta/references/private.md`\n")
        beta = self.root.parent / "beta"
        write(beta / "SKILL.md", "---\nname: beta\n---\n")
        write(self.root / ".skill-deps-allow",
              "beta/references/private.md  # 继承正文，票 02 收编\n")
        self.assertEqual(self.violations(), [])

    def test_allowlist_entry_without_reason_is_config_error(self):
        write(self.root / ".skill-deps-allow", "beta/references/private.md\n")
        with self.assertRaises(ValueError):
            sdc.run(self.root)

    def test_declared_script_must_exist(self):
        (self.root / "tools" / "runner.py").unlink()
        kinds = [v["kind"] for v in self.violations()]
        self.assertIn("missing-script", kinds)

    def test_dependency_cycle_detected(self):
        md = CARD_MD + """
## skill: gamma

- 职责: g
- 层: L1 工序
- 目录: skills/gamma/
- 触发面: t
- reads: 无
- writes: 无
- 依赖:
  - skill: `delta`
- Seam 与出厂集: 无
- 边界: 无

## skill: delta

- 职责: d
- 层: L1 工序
- 目录: skills/delta/
- 触发面: t
- reads: 无
- writes: 无
- 依赖:
  - skill: `gamma`
- Seam 与出厂集: 无
- 边界: 无
"""
        write(self.root / "specs" / "modules.md", md)
        kinds = [v["kind"] for v in self.violations()]
        self.assertIn("dependency-cycle", kinds)

    def test_missing_modules_md_fails(self):
        (self.root / "specs" / "modules.md").unlink()
        report = sdc.run(self.root)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["violations"][0]["kind"], "no-modules-md")

    def test_main_exit_codes(self):
        write(self.root / "SKILL.md", "见 `references/not-exist.md`\n")
        self.assertEqual(quiet_main(["--root", str(self.root), "--json"]), 1)
        (self.root / "references").mkdir(exist_ok=True)
        write(self.root / "references" / "not-exist.md", "# x\n")
        self.assertEqual(quiet_main(["--root", str(self.root), "--json"]), 0)


GOV_CARD_MD = """# modules.md

## skill: alpha

- 职责: 测试用 skill
- 层: L1 工序
- 目录: skills/alpha/
- 触发面: 测试
- reads: 无
- writes: 无
- 依赖:
  - skill: `beta`（外部）
- Seam 与出厂集: 无
- 边界: 无
"""


class GovernedProjectCase(unittest.TestCase):
    """All-agent 实例化差异：无 skill 判注不判死；已规划脚本=警告。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "proj"
        self.root.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_skills_passes_with_note(self):
        write(self.root / "specs" / "modules.md", GOV_CARD_MD)
        report = sdc.run(self.root)
        self.assertEqual(report["status"], "pass", report["violations"])
        self.assertIn("票 05", report.get("note", ""))

    def test_planned_script_is_warning_not_violation(self):
        write(self.root / "specs" / "modules.md", CARD_MD + "\n"
              "## 脚本清单（L3）\n\n"
              "| 脚本 | 职责 | 状态 |\n|---|---|---|\n"
              "| `tools/runner.py` | 未落盘 | 一期建（票 04） |\n")
        report = sdc.run(self.root)
        self.assertEqual(report["status"], "pass", report["violations"])
        self.assertEqual([w["kind"] for w in report["warnings"]],
                         ["planned-script"])

    def test_unregistered_missing_script_still_violation(self):
        write(self.root / "specs" / "modules.md", CARD_MD)  # 无脚本清单登记
        report = sdc.run(self.root)
        self.assertEqual(report["status"], "fail")
        self.assertIn("missing-script", [v["kind"] for v in report["violations"]])


if __name__ == "__main__":
    unittest.main()
