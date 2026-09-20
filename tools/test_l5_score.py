#!/usr/bin/env python3
"""l5_score.py 的单测（票 42：L5 评分器确定性骨架，脚本轨 TDD）。

覆盖面（票面 AC1–4 的单测层；出厂端到端面在 fixtures/l5-scoring/）：
  rubric 校验：合法装载 / 三红（缺锚定例·含缺单档·空串 / 权重非法·含 0/负/浮点/
    字符串/布尔 / reference 指向不存在）/ 维度重复 / 问 id 重复 / 非映射 YAML /
    空目录 / 字符串锚档键放行 / ../ 相对 reference 放行；
  评分结果校验：合法装载 / 非 JSON / 顶层非对象 / 漏维 / 多维 / 重复维 /
    分数越界（6、-1、浮点、字符串、布尔）/ reason 空 / disqualifier 非布尔 /
    孤儿问 id / 缺采样 / 采样数≠3；
  聚合与判定：中位算术（[5,3,4]→4）/ 分差 ≥2 标不稳定 / disqualifier 一票否决
    按 0 分计 / 总分=score×weight 加权和 / 问总分集中位 / 通过线三条件逐条单点红；
  报告与 CLI：MD/JSON 渲染稳定标记 / --out 双落盘 / 同名 -2/-3 序号不覆盖 /
    退出码 0/1/2 契约 / 错误走 stderr；
  报告确定性与采样留仓（票 48）：同输入两次生成字节一致（零时间戳零机器路径，
    无 generatedAt）/ --keep-results 有=采样 JSON 原样拷入、无=不落目录 /
    同名不同内容冲突=exit 2 不覆盖。
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import l5_score as l5


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = l5.main(argv)
    return rc, out.getvalue(), err.getvalue()


LEGAL_RUBRIC = """\
question_id: Q1
reference: ../expected/ref.md
dimensions:
  - id: semantic_fidelity
    weight: 2
    anchors: {5: "五分锚", 3: "三分锚", 1: "一分锚"}
  - id: caliber_quality
    weight: 1
    anchors: {5: "五分锚", 3: "三分锚", 1: "一分锚"}
disqualifiers:
  - "编造承诺"
"""


def legal_result(qid="Q1", scores=None, disq=False, reason="理由"):
    scores = scores if scores is not None else {"semantic_fidelity": 4,
                                                "caliber_quality": 4}
    return {
        "question_id": qid,
        "dimensions": [{"id": k, "score": v, "reason": reason}
                       for k, v in scores.items()],
        "disqualifier_triggered": disq,
    }


class L5Base(unittest.TestCase):
    """tempfile 造仓：rubrics/Q1 合法 rubric + expected/ref.md。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "expected").mkdir()
        (self.root / "expected" / "ref.md").write_text("参照答案\n", encoding="utf-8")
        self.rubrics = self.root / "rubrics"
        self.rubrics.mkdir()
        (self.rubrics / "q1.yaml").write_text(LEGAL_RUBRIC, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write_result(self, name, obj, subdir="results"):
        d = self.root / subdir
        d.mkdir(parents=True, exist_ok=True)
        p = d / name
        if isinstance(obj, str):
            p.write_text(obj, encoding="utf-8")
        else:
            p.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        return p


class RubricValidation(L5Base):
    def test_legal_rubric_loads(self):
        rubs = l5.validate_rubrics_dir(self.rubrics)
        self.assertEqual(list(rubs), ["Q1"])
        r = rubs["Q1"]
        self.assertEqual([d["id"] for d in r["dimensions"]],
                         ["semantic_fidelity", "caliber_quality"])
        self.assertEqual(r["dimensions"][0]["weight"], 2)
        self.assertEqual(r["disqualifiers"], ["编造承诺"])

    def test_string_anchor_tier_keys_accepted(self):
        text = LEGAL_RUBRIC.replace('{5: "五分锚", 3: "三分锚", 1: "一分锚"}',
                                    '{"5": "五分锚", "3": "三分锚", "1": "一分锚"}')
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        rubs = l5.validate_rubrics_dir(self.rubrics)
        self.assertEqual(set(rubs["Q1"]["dimensions"][0]["anchors"]), {5, 3, 1})

    def test_out_of_dir_reference_ok(self):
        # ../ 相对引用（真实布局 fixtures/semantic-service/rubrics → ../expected-answers）
        rubs = l5.validate_rubrics_dir(self.rubrics)
        self.assertTrue(rubs["Q1"]["reference_path"].is_file())

    def test_missing_whole_anchors_red(self):
        text = LEGAL_RUBRIC.replace("""  - id: caliber_quality
    weight: 1
    anchors: {5: "五分锚", 3: "三分锚", 1: "一分锚"}
""", """  - id: caliber_quality
    weight: 1
""")
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        with self.assertRaises(l5.ConfigError) as cm:
            l5.validate_rubrics_dir(self.rubrics)
        self.assertIn("锚定例", str(cm.exception))
        self.assertIn("caliber_quality", str(cm.exception))

    def test_anchors_missing_one_tier_red(self):
        text = LEGAL_RUBRIC.replace('{5: "五分锚", 3: "三分锚", 1: "一分锚"}',
                                    '{5: "五分锚", 3: "三分锚"}')
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        with self.assertRaises(l5.ConfigError) as cm:
            l5.validate_rubrics_dir(self.rubrics)
        self.assertIn("1", str(cm.exception))

    def test_anchor_empty_string_red(self):
        text = LEGAL_RUBRIC.replace("1: \"一分锚\"", "1: \"\"")
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        with self.assertRaises(l5.ConfigError):
            l5.validate_rubrics_dir(self.rubrics)

    def test_weight_zero_red(self):
        text = LEGAL_RUBRIC.replace("weight: 1", "weight: 0")
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        with self.assertRaises(l5.ConfigError) as cm:
            l5.validate_rubrics_dir(self.rubrics)
        self.assertIn("weight", str(cm.exception))

    def test_weight_negative_float_string_bool_red(self):
        for bad in ("-1", "1.5", '"2"', "true"):
            text = LEGAL_RUBRIC.replace("weight: 1", f"weight: {bad}")
            (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
            with self.assertRaises(l5.ConfigError, msg=bad):
                l5.validate_rubrics_dir(self.rubrics)

    def test_ghost_reference_red(self):
        text = LEGAL_RUBRIC.replace("../expected/ref.md", "../expected/ghost.md")
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        with self.assertRaises(l5.ConfigError) as cm:
            l5.validate_rubrics_dir(self.rubrics)
        self.assertIn("reference 不存在", str(cm.exception))
        self.assertIn("ghost.md", str(cm.exception))

    def test_duplicate_dimension_id_red(self):
        text = LEGAL_RUBRIC.replace("caliber_quality", "semantic_fidelity")
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        with self.assertRaises(l5.ConfigError) as cm:
            l5.validate_rubrics_dir(self.rubrics)
        self.assertIn("重复", str(cm.exception))

    def test_duplicate_question_id_across_files_red(self):
        (self.rubrics / "q1-again.yaml").write_text(LEGAL_RUBRIC, encoding="utf-8")
        with self.assertRaises(l5.ConfigError) as cm:
            l5.validate_rubrics_dir(self.rubrics)
        self.assertIn("question_id", str(cm.exception))

    def test_non_mapping_yaml_red(self):
        (self.rubrics / "q1.yaml").write_text("- a\n- b\n", encoding="utf-8")
        with self.assertRaises(l5.ConfigError):
            l5.validate_rubrics_dir(self.rubrics)

    def test_broken_yaml_red(self):
        (self.rubrics / "q1.yaml").write_text("a: [unclosed\n", encoding="utf-8")
        with self.assertRaises(l5.ConfigError):
            l5.validate_rubrics_dir(self.rubrics)

    def test_empty_rubrics_dir_red(self):
        for f in self.rubrics.iterdir():
            f.unlink()
        with self.assertRaises(l5.ConfigError) as cm:
            l5.validate_rubrics_dir(self.rubrics)
        self.assertIn("没有任何", str(cm.exception))

    def test_unknown_top_level_keys_tolerated(self):
        text = LEGAL_RUBRIC + "scoring_prompt: |\n  评分提示词（载体随 rubric，票 42 裁决）\n"
        (self.rubrics / "q1.yaml").write_text(text, encoding="utf-8")
        self.assertEqual(list(l5.validate_rubrics_dir(self.rubrics)), ["Q1"])


class ResultValidation(L5Base):
    def collect(self, subdir="results"):
        files = l5.collect_result_files([self.root / subdir])
        return l5.validate_results(self.rubrics and
                                   l5.validate_rubrics_dir(self.rubrics), files)

    def test_legal_result_grouped(self):
        self.write_result("q1-s1.json", legal_result())
        self.write_result("q1-s2.json", legal_result())
        self.write_result("q1-s3.json", legal_result())
        grouped = self.collect()
        self.assertEqual(list(grouped), ["Q1"])
        self.assertEqual(len(grouped["Q1"]), 3)

    def test_not_json_red(self):
        self.write_result("q1-bad.json", "评分结论：很好，5 分。")
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("不是合法 JSON", str(cm.exception))

    def test_top_level_not_object_red(self):
        self.write_result("q1-bad.json", "[1, 2]")
        with self.assertRaises(l5.ConfigError):
            self.collect()

    def test_missing_dimension_red(self):
        self.write_result("q1-s1.json", legal_result(scores={"semantic_fidelity": 4}))
        self.write_result("q1-s2.json", legal_result())
        self.write_result("q1-s3.json", legal_result())
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("caliber_quality", str(cm.exception))

    def test_extra_dimension_red(self):
        self.write_result("q1-s1.json", legal_result(
            scores={"semantic_fidelity": 4, "caliber_quality": 4, "organization": 3}))
        self.write_result("q1-s2.json", legal_result())
        self.write_result("q1-s3.json", legal_result())
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("organization", str(cm.exception))

    def test_score_out_of_range_red(self):
        for bad in (6, -1, 2.5, "4", True):
            self.write_result("q1-s1.json", legal_result(
                scores={"semantic_fidelity": bad, "caliber_quality": 4}))
            self.write_result("q1-s2.json", legal_result())
            self.write_result("q1-s3.json", legal_result())
            with self.assertRaises(l5.ConfigError, msg=repr(bad)) as cm:
                self.collect()
            self.assertIn("越界", str(cm.exception))

    def test_empty_reason_red(self):
        self.write_result("q1-s1.json", legal_result(reason="  "))
        self.write_result("q1-s2.json", legal_result())
        self.write_result("q1-s3.json", legal_result())
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("reason", str(cm.exception))

    def test_disqualifier_not_bool_red(self):
        r = legal_result()
        r["disqualifier_triggered"] = "yes"
        self.write_result("q1-s1.json", r)
        self.write_result("q1-s2.json", legal_result())
        self.write_result("q1-s3.json", legal_result())
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("disqualifier_triggered", str(cm.exception))

    def test_orphan_question_id_red(self):
        self.write_result("qx-s1.json", legal_result(qid="QX"))
        self.write_result("qx-s2.json", legal_result(qid="QX"))
        self.write_result("qx-s3.json", legal_result(qid="QX"))
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("孤儿", str(cm.exception))

    def test_missing_samples_red(self):
        (self.root / "results").mkdir()  # 空目录：rubric 三问全无采样
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("采样", str(cm.exception))

    def test_sample_count_not_three_red(self):
        self.write_result("q1-s1.json", legal_result())
        self.write_result("q1-s2.json", legal_result())
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("采样数不是 3", str(cm.exception))

    def test_sample_count_four_red(self):
        for n in ("s1", "s2", "s3", "s4"):
            self.write_result(f"q1-{n}.json", legal_result())
        with self.assertRaises(l5.ConfigError) as cm:
            self.collect()
        self.assertIn("采样数不是 3", str(cm.exception))


class Aggregation(L5Base):
    """聚合纯函数面：注入 rubric + 三采样，验证中位/不稳定/否决/总分/三条件。"""

    @staticmethod
    def rubric():
        return {
            "question_id": "Q1",
            "dimensions": [
                {"id": "d1", "weight": 2},
                {"id": "d2", "weight": 1},
            ],
        }

    @staticmethod
    def sample(scores, disq=False):
        return {"question_id": "Q1",
                "dimensions": [{"id": k, "score": v, "reason": "r"}
                               for k, v in scores.items()],
                "disqualifier_triggered": disq}

    def agg(self, samples):
        return l5.aggregate_question(self.rubric(), "Q1", samples)

    def test_median_arithmetic(self):
        # AC3a 同款算术：[5,3,4] → 中位 4
        q = self.agg([self.sample({"d1": s, "d2": 4}) for s in (5, 3, 4)])
        d1 = q["dimensions"][0]
        self.assertEqual(d1["samples"], [5, 3, 4])
        self.assertEqual(d1["median"], 4)

    def test_weighted_total_sum_of_medians(self):
        q = self.agg([self.sample({"d1": s1, "d2": s2})
                      for s1, s2 in ((5, 4), (4, 5), (4, 4))])
        # 中位 d1=4 d2=4 → 总分 = 4*2 + 4*1 = 12（加权和，不常态化，L0 定稿）
        self.assertEqual(q["total"], 12)

    def test_spread_two_marks_unstable(self):
        q = self.agg([self.sample({"d1": s, "d2": 4}) for s in (5, 3, 4)])
        self.assertFalse(q["stable"])
        q2 = self.agg([self.sample({"d1": s, "d2": 4}) for s in (5, 4, 4)])
        self.assertTrue(q2["stable"])

    def test_disqualifier_zeroes_question(self):
        # AC3c：任一采样 disqualifier_triggered=true → 该问 0 分 + 一票否决
        samples = [self.sample({"d1": 5, "d2": 5}),
                   self.sample({"d1": 5, "d2": 5}, disq=True),
                   self.sample({"d1": 4, "d2": 4})]
        q = self.agg(samples)
        self.assertTrue(q["disqualified"])
        self.assertEqual(q["total"], 0)
        self.assertEqual(q["disq_votes"], 1)

    def test_set_median_odd_and_even(self):
        self.assertEqual(l5.set_median([3, 3, 13]), 3)
        self.assertEqual(l5.set_median([3, 5, 13, 21]), 9.0)

    def test_pass_all_three_conditions(self):
        qs = [{"question_id": "Q1", "total": 22, "stable": True,
               "disqualified": False, "dimensions": []},
              {"question_id": "Q2", "total": 12, "stable": True,
               "disqualified": False, "dimensions": []}]
        verdict, conds = l5.evaluate(qs)
        self.assertEqual(verdict, "PASS")
        self.assertTrue(all(c["pass"] for c in conds.values()))

    def test_fail_each_condition_alone(self):
        base = {"stable": True, "disqualified": False, "dimensions": []}

        def qs(*totals, **kw):
            return [dict({"question_id": f"Q{i}", "total": t, **base, **kw})
                    for i, t in enumerate(totals, 1)]

        # 条件①单点红：某问总分 <3，其余条件绿
        v, c = l5.evaluate(qs(22, 12, 1))
        self.assertEqual(v, "FAIL")
        self.assertFalse(c["perQuestionTotal"]["pass"])
        self.assertTrue(c["setMedian"]["pass"])
        self.assertTrue(c["noDisqualifier"]["pass"])
        # 条件②单点红：中位 <4.0
        v, c = l5.evaluate(qs(3, 3, 13))
        self.assertEqual(v, "FAIL")
        self.assertTrue(c["perQuestionTotal"]["pass"])
        self.assertFalse(c["setMedian"]["pass"])
        # 条件③红：disqualifier 触发（evaluate 层分道逻辑单测——真实聚合里
        # 触发问已按 0 分计会连带条件①，故此处总分取 12 隔离条件③单点）
        qs_list = [
            {"question_id": "Q1", "total": 22, "stable": True,
             "disqualified": False, "dimensions": []},
            {"question_id": "Q2", "total": 12, "stable": True,
             "disqualified": True, "dimensions": []},
        ]
        v, c = l5.evaluate(qs_list)
        self.assertEqual(v, "FAIL")
        self.assertTrue(c["perQuestionTotal"]["pass"])
        self.assertTrue(c["setMedian"]["pass"])
        self.assertFalse(c["noDisqualifier"]["pass"])


class ReportAndCli(L5Base):
    def build_env(self):
        """三问 rubric + 全绿采样，供渲染与 CLI 用。"""
        (self.rubrics / "q2.yaml").write_text(
            LEGAL_RUBRIC.replace("Q1", "Q2").replace("semantic_fidelity", "coverage")
            .replace("caliber_quality", "citation_fit"), encoding="utf-8")
        scores = {"Q1": {"semantic_fidelity": 5, "caliber_quality": 4},
                  "Q2": {"coverage": 4, "citation_fit": 4}}
        for q, sc in scores.items():
            for n in ("s1", "s2", "s3"):
                self.write_result(f"{q.lower()}-{n}.json", legal_result(q, sc))
        # 中位算术（LEGAL_RUBRIC 权重 sf=2/cq=1）：Q1 = 5*2+4*1 = 14，Q2 = 12
        return scores

    def test_render_md_stable_markers(self):
        self.build_env()
        rc, out, _ = run_main(["--rubrics", str(self.rubrics),
                               "--results", str(self.root / "results")])
        self.assertEqual(rc, 0)
        for needle in ("结论: PASS", "条件①", "条件②", "条件③", "总分: 14",
                       "红灯路由去向", "业务错道", "工程错道", "元模型错道"):
            self.assertIn(needle, out)

    def test_cli_out_writes_md_and_json(self):
        self.build_env()
        out_md = self.root / "out" / "r.md"
        rc, out, _ = run_main(["--rubrics", str(self.rubrics),
                               "--results", str(self.root / "results"),
                               "--out", str(out_md)])
        self.assertEqual(rc, 0)
        self.assertTrue(out_md.is_file())
        j = json.loads(out_md.with_suffix(".json").read_text(encoding="utf-8"))
        self.assertEqual(j["verdict"], "PASS")
        self.assertEqual(j["exitCode"], 0)
        self.assertEqual(len(j["questions"]), 2)

    def test_next_free_path_no_overwrite(self):
        base = self.root / "o.md"
        self.assertEqual(l5.next_free_path(base), base)
        base.write_text("a", encoding="utf-8")
        second = l5.next_free_path(base)
        self.assertEqual(second.name, "o-2.md")
        second.write_text("b", encoding="utf-8")
        (self.root / "o-2.json").write_text("{}", encoding="utf-8")  # 伴生同名占位
        self.assertEqual(l5.next_free_path(base).name, "o-3.md")

    def test_exit_2_bad_rubric_message_on_stderr(self):
        for n in ("s1", "s2", "s3"):  # 合法采样在档，让校验走到 rubric 红上
            self.write_result(f"q1-{n}.json", legal_result())
        (self.rubrics / "q1.yaml").write_text(
            LEGAL_RUBRIC.replace("weight: 1", "weight: 0"), encoding="utf-8")
        rc, out, err = run_main(["--rubrics", str(self.rubrics),
                                 "--results", str(self.root / "results")])
        self.assertEqual(rc, 2)
        self.assertIn("rubric 非法", err)
        self.assertNotIn("结论:", out)

    def test_exit_2_dirty_result(self):
        self.write_result("q1-s1.json", legal_result(scores={"semantic_fidelity": 6,
                                                             "caliber_quality": 4}))
        rc, out, err = run_main(["--rubrics", str(self.rubrics),
                                 "--results", str(self.root / "results")])
        self.assertEqual(rc, 2)
        self.assertIn("评分无效", err)
        self.assertIn("越界", err)

    def test_exit_1_low_total(self):
        self.build_env()
        # 覆写 Q1 三采样：中位 sf=0（×2）+ cq=0（×1）→ 总分 0 <3；Q2 照旧 12
        # → 问总分集 [0, 12] 中位 6 ≥4.0、无 disqualifier，条件①单点红。
        for n, sc in (("s1", {"semantic_fidelity": 0, "caliber_quality": 0}),
                      ("s2", {"semantic_fidelity": 1, "caliber_quality": 0}),
                      ("s3", {"semantic_fidelity": 0, "caliber_quality": 1})):
            self.write_result(f"q1-{n}.json", legal_result("Q1", sc))
        rc, out, _ = run_main(["--rubrics", str(self.rubrics),
                               "--results", str(self.root / "results")])
        self.assertEqual(rc, 1)
        self.assertIn("结论: FAIL", out)
        self.assertIn("Q1 总分 0", out)

    def test_exit_2_rubrics_dir_missing(self):
        rc, out, err = run_main(["--rubrics", str(self.root / "nope"),
                                 "--results", str(self.root / "results")])
        self.assertEqual(rc, 2)
        self.assertIn("配置错误", err)


class DeterminismAndKeepResults(L5Base):
    """票 48：报告确定性（P2-B）与 --keep-results 采样留仓（P3）。"""

    def build_env(self):
        """两问 rubric + 全绿采样（复用 ReportAndCli 同款构造）。"""
        (self.rubrics / "q2.yaml").write_text(
            LEGAL_RUBRIC.replace("Q1", "Q2").replace("semantic_fidelity", "coverage")
            .replace("caliber_quality", "citation_fit"), encoding="utf-8")
        scores = {"Q1": {"semantic_fidelity": 5, "caliber_quality": 4},
                  "Q2": {"coverage": 4, "citation_fit": 4}}
        for q, sc in scores.items():
            for n in ("s1", "s2", "s3"):
                self.write_result(f"{q.lower()}-{n}.json", legal_result(q, sc))

    def test_report_bytes_identical_across_runs(self):
        # AC2 同款判定动作的单测层：同输入两次生成（不同 --out 路径）字节一致
        self.build_env()
        for tag in ("r1", "r2"):
            rc, _, _ = run_main(["--rubrics", str(self.rubrics),
                                 "--results", str(self.root / "results"),
                                 "--out", str(self.root / f"{tag}.md")])
            self.assertEqual(rc, 0)
        self.assertEqual((self.root / "r1.md").read_bytes(),
                         (self.root / "r2.md").read_bytes())
        self.assertEqual((self.root / "r1.json").read_bytes(),
                         (self.root / "r2.json").read_bytes())

    def test_report_no_timestamp_no_machine_path(self):
        # 确定性化契约：无 generatedAt 字段、报告不含临时目录机器路径
        self.build_env()
        rc, out, _ = run_main(["--rubrics", str(self.rubrics),
                               "--results", str(self.root / "results"),
                               "--out", str(self.root / "r.md")])
        self.assertEqual(rc, 0)
        j = json.loads((self.root / "r.json").read_text(encoding="utf-8"))
        self.assertNotIn("generatedAt", j)
        self.assertNotIn("rubricsDir", j)
        self.assertNotIn("resultsPaths", j)
        self.assertIn("inputFingerprint", j)
        for text in (out, (self.root / "r.md").read_text(encoding="utf-8"),
                     (self.root / "r.json").read_text(encoding="utf-8")):
            self.assertNotIn(str(self.root), text)  # 机器路径零泄漏
            self.assertNotIn("生成时间", text)
        # 输入指纹随内容变：改一份评分内容 → 指纹变
        fp1 = j["inputFingerprint"]
        self.write_result("q1-s1.json", legal_result(
            "Q1", {"semantic_fidelity": 5, "caliber_quality": 5}))
        rc, _, _ = run_main(["--rubrics", str(self.rubrics),
                             "--results", str(self.root / "results"),
                             "--out", str(self.root / "r2.md")])
        self.assertEqual(rc, 0)
        fp2 = json.loads((self.root / "r2.json").read_text(
            encoding="utf-8"))["inputFingerprint"]
        self.assertNotEqual(fp1, fp2)

    def test_rubric_file_in_report_is_basename(self):
        self.build_env()
        rc, out, _ = run_main(["--rubrics", str(self.rubrics),
                               "--results", str(self.root / "results")])
        self.assertEqual(rc, 0)
        self.assertIn("- rubric: q1.yaml", out)
        self.assertNotIn(str(self.rubrics), out)

    def test_keep_results_copies_samples(self):
        self.build_env()
        kept = self.root / "kept"
        rc, _, err = run_main(["--rubrics", str(self.rubrics),
                               "--results", str(self.root / "results"),
                               "--keep-results", str(kept)])
        self.assertEqual(rc, 0)
        self.assertIn("--keep-results", err)
        srcs = sorted((self.root / "results").glob("*.json"))
        dsts = sorted(kept.glob("*.json"))
        self.assertEqual([p.name for p in dsts], [p.name for p in srcs])
        for s, d in zip(srcs, dsts):
            self.assertEqual(s.read_bytes(), d.read_bytes())

    def test_keep_results_absent_by_default(self):
        self.build_env()
        kept = self.root / "kept"
        rc, _, _ = run_main(["--rubrics", str(self.rubrics),
                             "--results", str(self.root / "results")])
        self.assertEqual(rc, 0)
        self.assertFalse(kept.exists())

    def test_keep_results_conflict_red_no_overwrite(self):
        self.build_env()
        kept = self.root / "kept"
        kept.mkdir()
        (kept / "q1-s1.json").write_text('{"不同": "内容"}', encoding="utf-8")
        rc, _, err = run_main(["--rubrics", str(self.rubrics),
                               "--results", str(self.root / "results"),
                               "--keep-results", str(kept)])
        self.assertEqual(rc, 2)
        self.assertIn("名称冲突", err)
        self.assertEqual((kept / "q1-s1.json").read_text(encoding="utf-8"),
                         '{"不同": "内容"}')  # 不覆盖

    def test_keep_results_dirty_run_copies_nothing(self):
        # 配置错路径不产副本：脏采样不外流
        self.build_env()
        self.write_result("q1-s1.json", legal_result(
            scores={"semantic_fidelity": 6, "caliber_quality": 4}))
        kept = self.root / "kept"
        rc, _, _ = run_main(["--rubrics", str(self.rubrics),
                             "--results", str(self.root / "results"),
                             "--keep-results", str(kept)])
        self.assertEqual(rc, 2)
        self.assertFalse(kept.exists())


if __name__ == "__main__":
    unittest.main()
