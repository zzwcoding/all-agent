#!/usr/bin/env python3
"""l5_score.py —— L5 评分器确定性骨架（票 42；design-l5-scoring.md §8 票 A + §9 裁决①）。

L5 评分面的确定性部分：rubric 格式校验 → 评分结果 JSON 校验 → 3 采样中位聚合
→ disqualifier 一票否决 → 通过线判定 → 报告落盘（MD+同名 JSON）→ 退出码。
**零模型调用**：LLM 评分由运行时子 agent 产出评分结果 JSON 文件（票 44 才接线
派发），本脚本只消费文件——mock 注入 = 预置 JSON 文件，无任何模型 client。

协议（真源 = specs/l5_score.md，L0 定稿）：
  评分请求 = {question, reference_answer_path, candidate_answer_path, rubric_path}
    （票 44 子 agent 派发契约；本脚本不消费请求侧）
  评分结果 = {question_id, dimensions: [{id, score, reason}], disqualifier_triggered: bool}

rubric（YAML）三红（机判，AC1）：某维缺 anchors 或 anchors 缺 5/3/1 档非空描述 /
  weight 非正整数 / reference（相对本 rubric 文件解析）指向不存在文件。
评分结果校验（机判，AC2）：维度 id 集与 rubric 完全一致、score 为 0–5 整数、
  reason 非空、disqualifier_triggered 为布尔；违规 = exit 2「评分无效」（附脏点
  定位），不进聚合。逐问采样数必须恰为 3（design §4.3：3 次独立子 agent 派发），
  多/少/缺 = exit 2。

聚合与判定（先算术后结论，AC3/AC4）：
  逐问逐维 3 采样取中位 → 分差 max-min ≥2 标「不稳定」（只标记，仲裁升级票 44
  接线，不判死）→ 任一采样 disqualifier_triggered=true 的问按 0 分计且一票否决
  → 总分 = 该问各维 score×weight 加权和（不常态化，L0 定稿：weight 只要求正整数）
  → 通过线三条件同时满足才绿：① 每问总分 ≥3 ② 问总分集的中位 ≥4.0
  ③ 无 disqualifier 触发问。注意：门槛数值作用在加权和量纲上，含义随 rubric
  权重集取值变化——权重集是 rubric 内容 Owner 的定稿责任（specs 注意事项节）。

报告：--out <路径>.md 同时落同名 .json 机读伴生；同名已存在加 -2/-3 序号，
  不覆盖旧留痕（照 meta_probe 体检留痕惯例，AGENTS.md 续跑协议第 9 条同款）。
  内容 = 每问逐维分数 + 采样分布 + 结论 + 不稳定升级提示 + 红灯路由去向
  （红灯只报告不修复，分道人工裁决，路由表 policies/signal-routing.json）。
  报告确定性（票 48 P2-B）：零时间戳、零机器路径——同输入两次生成字节一致，
  留痕的时间性由 --out 同名序号后缀承载（-2/-3…），输入身份由「输入指纹」承载
  （rubric+评分结果文件名与内容 sha256 前 16 位，报告内可追溯非 golden）。
  --keep-results <目录>：评分结果 JSON 原样拷入指定目录（采样 reason 留仓用，
  票 48 P3；缺省不落——结果只进聚合不落盘副本）。

退出码：0 通过线全绿；1 红（低于通过线或触发 disqualifier）；2 配置错
  （rubric 非法 / 评分文件无效 / 用法错误）。错误走 stderr，报告走 stdout
  （--json 时 stdout 只有机读 JSON）。
"""

import argparse
import hashlib
import json
import shutil
import statistics
import sys
from pathlib import Path

import yaml

TICKET = "42"
SCORE_MIN, SCORE_MAX = 0, 5
SAMPLES_PER_QUESTION = 3          # design §4.3：每问 3 次独立子 agent 派发
REQUIRED_ANCHOR_TIERS = (5, 3, 1)  # 锚定例三档，缺一即红
UNSTABLE_SPREAD = 2                # 分差 ≥2 标不稳定
PASS_QUESTION_TOTAL_MIN = 3        # 通过线条件①
PASS_SET_MEDIAN_MIN = 4.0          # 通过线条件②
EXIT_OK, EXIT_RED, EXIT_CONFIG = 0, 1, 2

# 红灯三分道（design §4.4；本脚本只报告不修复，分道人工裁决）
ROUTING_CHANNELS = (
    ("语义内容错（保真度/口径类红）→ 业务错道",
     "提案池起草（skills/proposal-pool），Owner 裁决走 MR"),
    ("话术/工序错（拒答话术/组织类红，本体没错）→ 工程错道",
     "tickets/ 开票修 skill 工序或参照答案"),
    ("rubric 本身写错（锚例与工序矛盾）→ 元模型错道",
     "改 rubric 走票（改出厂集 = 走票）"),
)


class ConfigError(Exception):
    """rubric 非法 / 评分文件无效 / 用法错误（exit 2），聚集多条错误一行一条。"""


def _is_int(value) -> bool:
    """整数且非布尔（Python bool 是 int 子类，须显式排除）。"""
    return isinstance(value, int) and not isinstance(value, bool)


# ---------- rubric 校验（AC1 三红） ----------

def _check_anchors(dim_id: str, anchors, errors: list, where: str) -> "dict | None":
    """anchors 须含 5/3/1 三档且各档非空字符串描述；缺任一档 = 红。

    返回规范化后的 anchors（字符串数字键归一为 int），无映射时返回 None。
    """
    if not isinstance(anchors, dict):
        errors.append(f"{where}维度 {dim_id} 缺锚定例（anchors 须为映射: "
                      f"{{5: …, 3: …, 1: …}}）")
        return None
    normalized = {}
    for k, v in anchors.items():
        key = int(k) if _is_int(k) or (isinstance(k, str) and k.strip().isdigit()) else k
        normalized[key] = v
    missing = [t for t in REQUIRED_ANCHOR_TIERS
               if not isinstance(normalized.get(t), str)
               or not normalized.get(t, "").strip()]
    if missing:
        tiers = ", ".join(str(t) for t in missing)
        errors.append(f"{where}维度 {dim_id} 缺锚定例（anchors 须含 5/3/1 三档"
                      f"非空描述；缺档: {tiers}）")
    return normalized


def _parse_rubric_file(path: Path) -> "tuple[dict | None, list[str]]":
    """单份 rubric 解析+校验，返回 (rubric dict | None, 该文件错误列表)。"""
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        return None, [f"rubric 非法: {path} — YAML 不可解析: {exc}"]
    if not isinstance(data, dict):
        return None, [f"rubric 非法: {path} — 顶层不是映射"]
    where = f"rubric 非法: {path} — "

    qid = data.get("question_id")
    if not isinstance(qid, str) or not qid.strip():
        errors.append(f"{where}缺 question_id（非空字符串）")
        qid = None

    ref = data.get("reference")
    ref_path = None
    if not isinstance(ref, str) or not ref.strip():
        errors.append(f"{where}缺 reference（相对本 rubric 文件的参照答案路径）")
    else:
        ref_path = path.parent / ref
        if not ref_path.is_file():
            errors.append(f"{where}reference 不存在: {ref}（解析为 {ref_path}）")

    dims_raw = data.get("dimensions")
    dims: list[dict] = []
    if not isinstance(dims_raw, list) or not dims_raw:
        errors.append(f"{where}缺 dimensions（非空列表）")
    else:
        seen_ids: set[str] = set()
        for i, d in enumerate(dims_raw, 1):
            if not isinstance(d, dict):
                errors.append(f"{where}第 {i} 维不是映射")
                continue
            dim_id = d.get("id")
            if not isinstance(dim_id, str) or not dim_id.strip():
                errors.append(f"{where}第 {i} 维缺 id（非空字符串）")
                continue
            if dim_id in seen_ids:
                errors.append(f"{where}维度 id 重复: {dim_id}")
                continue
            seen_ids.add(dim_id)
            weight = d.get("weight")
            if "weight" not in d:
                errors.append(f"{where}维度 {dim_id} 缺 weight（正整数）")
            elif not _is_int(weight) or weight < 1:
                errors.append(f"{where}维度 {dim_id} weight 非法（须正整数）: "
                              f"{weight!r}")
            anchors = _check_anchors(dim_id, d.get("anchors"), errors, where)
            dims.append({"id": dim_id, "weight": weight, "anchors": anchors})

    disq = data.get("disqualifiers", [])
    if disq and (not isinstance(disq, list)
                 or not all(isinstance(x, str) and x.strip() for x in disq)):
        errors.append(f"{where}disqualifiers 须为非空字符串列表")

    rubric = None
    if qid and not errors:
        rubric = {"question_id": qid, "reference": ref,
                  "reference_path": ref_path, "dimensions": dims,
                  "disqualifiers": disq or [], "path": path}
    return rubric, errors


def validate_rubrics_dir(rubrics_dir: Path) -> dict:
    """目录级 rubric 校验：全量收集错误（一次报完），返回 {question_id: rubric}。"""
    files = sorted(set(rubrics_dir.rglob("*.yaml")) | set(rubrics_dir.rglob("*.yml")))
    if not files:
        raise ConfigError(f"配置错误: rubrics 目录没有任何 .yaml/.yml rubric 文件: "
                          f"{rubrics_dir}")
    rubrics: dict = {}
    errors: list[str] = []
    for f in files:
        rubric, errs = _parse_rubric_file(f)
        errors.extend(errs)
        if rubric:
            if rubric["question_id"] in rubrics:
                errors.append(f"rubric 非法: {f} — question_id 重复: "
                              f"{rubric['question_id']}（与 "
                              f"{rubrics[rubric['question_id']]['path']}）")
            else:
                rubrics[rubric["question_id"]] = rubric
    if errors:
        raise ConfigError("\n".join(errors))
    return rubrics


# ---------- 评分结果校验（AC2，违规不进聚合） ----------

def collect_result_files(results_paths: list[Path]) -> list[Path]:
    """收集评分结果文件：目录递归取 *.json，显式文件须 .json。"""
    files: list[Path] = []
    for p in results_paths:
        if p.is_dir():
            files.extend(sorted(p.rglob("*.json")))
        elif p.suffix == ".json":
            files.append(p)
        else:
            raise ConfigError(f"配置错误: results 路径既非目录也非 .json 文件: {p}")
    return sorted(files)


def _validate_result_file(path: Path, rubrics: dict) -> "tuple[dict | None, list[str]]":
    """单份评分结果校验，返回 ((path, data) | None, 错误列表)。"""
    where = f"评分无效: {path} — "
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, [f"{where}不是合法 JSON: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{where}顶层不是 JSON 对象"]
    errors: list[str] = []

    qid = data.get("question_id")
    if not isinstance(qid, str) or not qid.strip():
        errors.append(f"{where}question_id 缺失或非字符串")
        return None, errors
    if qid not in rubrics:
        errors.append(f"{where}孤儿评分: question_id {qid} 在 rubrics 中不存在")
        return None, errors

    entries = data.get("dimensions")
    if not isinstance(entries, list) or not entries:
        errors.append(f"{where}dimensions 缺失或不是非空列表")
        return None, errors

    rubric_ids = [d["id"] for d in rubrics[qid]["dimensions"]]
    seen: set[str] = set()
    got: dict = {}
    for i, e in enumerate(entries, 1):
        if not isinstance(e, dict):
            errors.append(f"{where}第 {i} 维不是对象")
            continue
        dim_id = e.get("id")
        if not isinstance(dim_id, str) or not dim_id.strip():
            errors.append(f"{where}第 {i} 维缺 id")
            continue
        if dim_id in seen:
            errors.append(f"{where}维度 id 重复: {dim_id}")
            continue
        seen.add(dim_id)
        if dim_id not in rubric_ids:
            errors.append(f"{where}多出维度 {dim_id}（rubric {qid} 维度集: "
                          f"{'/'.join(rubric_ids)}）")
            continue
        score = e.get("score")
        if not _is_int(score) or not (SCORE_MIN <= score <= SCORE_MAX):
            errors.append(f"{where}维度 {dim_id} score 越界: {score!r}"
                          f"（合法 {SCORE_MIN}–{SCORE_MAX} 整数）")
        reason = e.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{where}维度 {dim_id} reason 缺失或为空")
        got[dim_id] = score

    for rid in rubric_ids:
        if rid not in seen:
            errors.append(f"{where}缺维度 {rid}（rubric {qid} 维度集: "
                          f"{'/'.join(rubric_ids)}）")
    disq = data.get("disqualifier_triggered")
    if not isinstance(disq, bool):
        errors.append(f"{where}disqualifier_triggered 缺失或非布尔")
    return (None if errors else {"path": path, "data": data}), errors


def validate_results(rubrics: dict, files: list[Path]) -> dict:
    """全量收集错误（一次报完）；通过后按 question_id 分组返回采样清单。"""
    grouped: dict = {}
    errors: list[str] = []
    for f in files:
        item, errs = _validate_result_file(f, rubrics)
        errors.extend(errs)
        if item:
            grouped.setdefault(item["data"]["question_id"], []).append(item)
    for qid in sorted(rubrics):
        n = len(grouped.get(qid, []))
        if n == 0:
            errors.append(f"评分无效: 缺评分采样 — question_id {qid}"
                          f"（rubric 有此问，结果 0 份）")
        elif n != SAMPLES_PER_QUESTION:
            errors.append(f"评分无效: 采样数不是 {SAMPLES_PER_QUESTION}: {qid} "
                          f"有 {n} 份（协议 = 每问 {SAMPLES_PER_QUESTION} 次独立派发）")
    if errors:
        raise ConfigError("\n".join(errors))
    return grouped


# ---------- 聚合与判定（AC3/AC4） ----------

def aggregate_question(rubric: dict, qid: str, samples: list) -> dict:
    """逐问聚合：逐维 3 采样中位 + 分差 → 加权和总分 → disqualifier 一票否决。

    samples = 该问的评分结果 dict 列表（协议 JSON 解析产物，非文件包装）。
    """
    dims = []
    for d in rubric["dimensions"]:
        vals = []
        for s in samples:
            score = next(e["score"] for e in s["dimensions"] if e["id"] == d["id"])
            vals.append(score)
        median = statistics.median(vals)
        spread = max(vals) - min(vals)
        dims.append({"id": d["id"], "weight": d["weight"], "samples": vals,
                     "median": median, "spread": spread})
    disq_votes = sum(1 for s in samples if s["disqualifier_triggered"])
    disqualified = disq_votes > 0
    unstable_dims = [d for d in dims if d["spread"] >= UNSTABLE_SPREAD]
    total = 0 if disqualified else sum(d["median"] * d["weight"] for d in dims)
    rubric_path = rubric.get("path")
    return {"question_id": qid, "rubric_file": rubric_path.name if rubric_path else "",
            "total": total, "stable": not unstable_dims,
            "disqualified": disqualified, "disq_votes": disq_votes,
            "unstable_dims": unstable_dims, "dimensions": dims}


def set_median(totals: list):
    """问总分集的中位（奇数取中、偶数取两中均值，statistics 同款）。"""
    return statistics.median(totals)


def evaluate(questions: list) -> "tuple[str, dict]":
    """通过线三条件（design §4.2）同时满足才 PASS，返回 (verdict, conditions)。"""
    totals = [q["total"] for q in questions]
    below = [{"question_id": q["question_id"], "total": q["total"]}
             for q in questions if q["total"] < PASS_QUESTION_TOTAL_MIN]
    median = set_median(totals)
    triggered = [q["question_id"] for q in questions if q["disqualified"]]
    conditions = {
        "perQuestionTotal": {"pass": not below, "below": below,
                             "threshold": PASS_QUESTION_TOTAL_MIN},
        "setMedian": {"pass": median >= PASS_SET_MEDIAN_MIN, "value": median,
                      "threshold": PASS_SET_MEDIAN_MIN},
        "noDisqualifier": {"pass": not triggered, "triggered": triggered},
    }
    verdict = "PASS" if all(c["pass"] for c in conditions.values()) else "FAIL"
    return verdict, conditions


# ---------- 输入指纹与采样留仓（票 48） ----------

def input_fingerprint(rubrics: dict, files: list) -> str:
    """报告输入指纹（票 48 P2-B）：rubric+评分结果逐文件取「文件名\\t内容 sha256」
    排序后喂入总 sha256，取前 16 位——替代时间戳/机器路径成为报告的输入身份，
    同输入两次生成字节一致；内容变则指纹变，报告可追溯而不含机器路径。
    """
    entries = [r["path"] for r in rubrics.values() if r.get("path") is not None]
    entries.extend(files)
    pairs = sorted((p.name, hashlib.sha256(p.read_bytes()).hexdigest())
                   for p in entries)
    h = hashlib.sha256()
    for name, digest in pairs:
        h.update(f"{name}\t{digest}\n".encode("utf-8"))
    return h.hexdigest()[:16]


def keep_results_copy(files: list, dest: Path) -> int:
    """评分结果 JSON 原样拷入 dest（--keep-results，票 48 P3 采样 reason 留仓用）。

    逐份按原文件名落盘：同名同字节 = 幂等跳过；同名不同字节 = 配置错不覆盖
    （与 --out 序号不覆盖同款纪律）。返回本次新拷贝份数。仅在评分校验通过后
    调用（配置错路径不产副本，脏文件不外流）。
    """
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for f in files:
        target = dest / f.name
        if target.exists():
            if target.read_bytes() == f.read_bytes():
                continue
            raise ConfigError(f"配置错误: --keep-results 名称冲突且内容不同，"
                              f"不覆盖: {target}（与 {f}）")
        shutil.copyfile(f, target)
        copied += 1
    return copied


# ---------- 报告渲染 ----------

def render_md(questions: list, verdict: str, conditions: dict, exit_code: int,
              fingerprint: str, rubric_count: int, result_count: int) -> str:
    lines: list[str] = []
    lines += [
        "# L5 评分报告（l5_score · 票 42）",
        "",
        f"- 输入指纹: {fingerprint}（rubric×{rubric_count} 文件 + 评分结果"
        f"×{result_count} 文件内容 sha256 前 16 位；零时间戳零机器路径，"
        "同输入两次生成字节一致——留痕时间性由 --out 序号后缀承载，票 48）",
        "- 形态: 确定性骨架（零模型调用）——LLM 评分由运行时子 agent 产出评分结果"
        " JSON（协议: specs/l5_score.md），本脚本只校验、聚合、判定、留痕",
        "",
        f"**结论: {verdict}**（退出码 {exit_code}）",
    ]
    c1, c2, c3 = (conditions["perQuestionTotal"], conditions["setMedian"],
                  conditions["noDisqualifier"])
    if c1["pass"]:
        lowest = min(questions, key=lambda q: q["total"])
        lines.append(f"- 条件① 单问总分 ≥{c1['threshold']}: PASS"
                     f"（最低 {lowest['question_id']} = {lowest['total']}）")
    else:
        detail = "、".join(f"{b['question_id']} 总分 {b['total']} < {c1['threshold']}"
                          for b in c1["below"])
        lines.append(f"- 条件① 单问总分 ≥{c1['threshold']}: **FAIL** —— {detail}")
    mark2 = "PASS" if c2["pass"] else "**FAIL**"
    op2 = "≥" if c2["pass"] else "<"
    totals_list = [q["total"] for q in questions]
    lines.append(f"- 条件② 全集中位 ≥{c2['threshold']}: {mark2}"
                 f"（全集中位 {c2['value']} {op2} {c2['threshold']}，"
                 f"问总分集 {totals_list}）" if c2["pass"] else
                 f"- 条件② 全集中位 ≥{c2['threshold']}: {mark2} —— 全集中位 "
                 f"{c2['value']} {op2} {c2['threshold']}"
                 f"（问总分集 {totals_list}）")
    if c3["pass"]:
        lines.append(f"- 条件③ 无 disqualifier: PASS（0 问触发）")
    else:
        lines.append(f"- 条件③ 无 disqualifier: **FAIL** —— "
                     f"{len(c3['triggered'])} 问触发（{'、'.join(c3['triggered'])}）")
    lines.append("")

    lines += ["## 逐问明细", ""]
    for q in questions:
        lines.append(f"### {q['question_id']}")
        lines.append(f"- rubric: {q['rubric_file']}")
        if q["disqualified"]:
            lines.append(f"- 判定: FAIL ｜ 总分: {q['total']} ｜ 一票否决"
                         f"（disqualifier_triggered：{SAMPLES_PER_QUESTION} 采样中 "
                         f"{q['disq_votes']} 票为 true，按 0 分计）")
        elif not q["stable"]:
            detail = "；".join(f"{d['id']} 采样 {d['samples']}（分差 {d['spread']}）"
                              for d in q["unstable_dims"])
            lines.append(f"- 判定: PASS ｜ 总分: {q['total']} ｜ 不稳定（分差 "
                         f"≥{UNSTABLE_SPREAD}: {detail}）")
        else:
            lines.append(f"- 判定: PASS ｜ 总分: {q['total']} ｜ 稳定")
        lines += ["", "| 维度 | 权重 | 三采样 | 中位 | 分差 |", "|---|---|---|---|---|"]
        for d in q["dimensions"]:
            lines.append(f"| {d['id']} | {d['weight']} | {d['samples']} "
                         f"| {d['median']} | {d['spread']} |")
        lines.append("")

    unstable_qs = [q for q in questions if not q["stable"]]
    lines += ["## 不稳定升级提示（design-l5-scoring.md §4.3）", ""]
    if unstable_qs:
        for q in unstable_qs:
            for d in q["unstable_dims"]:
                lines.append(f"- {q['question_id']}: {d['id']} 采样 "
                             f"{d['samples']} 分差 {d['spread']} "
                             f"≥{UNSTABLE_SPREAD} —— 升级第二模型仲裁"
                             f"（票 44 接线；本脚本只标记不派发）")
    else:
        lines.append("（无）")
    lines.append("")

    red_qs = sorted({b["question_id"] for b in c1["below"]}
                    | set(c3["triggered"]))
    lines += ["## 红灯路由去向（只报告不修复；分道人工裁决，"
              "路由表: policies/signal-routing.json）", ""]
    for title, mech in ROUTING_CHANNELS:
        lines.append(f"- {title}: {mech}")
    lines.append("- 本次红灯问: " + ("、".join(red_qs) if red_qs else "无"))
    lines.append("")
    return "\n".join(lines)


def render_json(questions: list, verdict: str, conditions: dict, exit_code: int,
                fingerprint: str) -> str:
    return json.dumps({
        "tool": "l5_score",
        "ticket": TICKET,
        "inputFingerprint": fingerprint,
        "verdict": verdict,
        "exitCode": exit_code,
        "conditions": conditions,
        "questions": questions,
    }, ensure_ascii=False, indent=2, default=str)


def next_free_path(path: Path) -> Path:
    """同名已存在则加 -2/-3 序号（MD 与同名 .json 伴生都空闲才占用），不覆盖。"""
    companion = path.with_suffix(".json")
    if not path.exists() and not companion.exists():
        return path
    for i in range(2, 100):
        cand = path.with_name(f"{path.stem}-{i}{path.suffix}")
        if not cand.exists() and not cand.with_suffix(".json").exists():
            return cand
    raise ConfigError(f"配置错误: 报告路径序号耗尽（-2 … -99 全占）: {path}")


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="L5 评分器确定性骨架（票 42）：rubric/评分结果校验 + 3 采样中位"
                    "聚合 + disqualifier 一票否决 + 通过线判定 + 报告落盘；"
                    "零模型调用。退出码 0 绿 / 1 红 / 2 配置错")
    ap.add_argument("--rubrics", required=True,
                    help="rubric 目录（逐份校验 *.yaml/*.yml）")
    ap.add_argument("--results", required=True, nargs="+",
                    help="评分结果 JSON（目录或文件，可多个；同 question_id 多份"
                         "=多采样，每问须恰 3 份）")
    ap.add_argument("--out", default=None,
                    help="报告落盘路径（.md；同时落同名 .json；同名已存在加 "
                         "-2/-3 序号不覆盖；缺省只打 stdout）")
    ap.add_argument("--keep-results", dest="keep_results", default=None,
                    metavar="目录",
                    help="评分结果 JSON 原样拷入指定目录（校验通过后落盘，采样 "
                         "reason 留仓用，票 48；缺省不落；同名不同内容=配置错"
                         "不覆盖）")
    ap.add_argument("--json", action="store_true",
                    help="机读 JSON 输出（stdout 只含 JSON，供探针消费）")
    args = ap.parse_args(argv)

    rubrics_dir = Path(args.rubrics)
    if not rubrics_dir.is_dir():
        print(f"配置错误: rubrics 目录不存在: {args.rubrics}", file=sys.stderr)
        return EXIT_CONFIG
    results_paths = [Path(p) for p in args.results]
    for p in results_paths:
        if not p.exists():
            print(f"配置错误: results 路径不存在: {p}", file=sys.stderr)
            return EXIT_CONFIG

    try:
        rubrics = validate_rubrics_dir(rubrics_dir)
        files = collect_result_files(results_paths)
        if not files:
            raise ConfigError("配置错误: 未收集到任何评分结果文件"
                              "（--results 目录/文件里没有 *.json）")
        grouped = validate_results(rubrics, files)
        questions = [aggregate_question(rubrics[qid], qid,
                                        [s["data"] for s in grouped[qid]])
                     for qid in sorted(grouped)]
        verdict, conditions = evaluate(questions)
        if args.keep_results:
            kept = keep_results_copy(files, Path(args.keep_results))
            print(f"--keep-results: 已拷贝 {kept}/{len(files)} 份评分结果 JSON "
                  f"→ {args.keep_results}", file=sys.stderr)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        print("配置校验失败（退出码 2）：评分面未运行，脏点不进聚合",
              file=sys.stderr)
        return EXIT_CONFIG

    exit_code = EXIT_OK if verdict == "PASS" else EXIT_RED
    rubric_count = len({r["path"] for r in rubrics.values()
                        if r.get("path") is not None})
    fingerprint = input_fingerprint(rubrics, files)
    md = render_md(questions, verdict, conditions, exit_code,
                   fingerprint, rubric_count, len(files))
    js = render_json(questions, verdict, conditions, exit_code, fingerprint)
    if args.json:
        sys.stdout.write(js + "\n")  # 机读契约：stdout 只含 JSON
    elif args.out:
        sys.stdout.write(md)
    else:
        sys.stdout.write(md)  # 与 --out 落盘字节一致

    if args.out:
        out_path = next_free_path(Path(args.out))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        json_path = out_path.with_suffix(".json")
        json_path.write_text(js, encoding="utf-8")
        print(f"已落盘: {out_path}", file=sys.stderr)
        print(f"已落盘: {json_path}", file=sys.stderr)
        if not args.json:  # --json 时 stdout 只含 JSON（机读契约）
            print(f"结论: {verdict}（退出码 {exit_code}）")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
