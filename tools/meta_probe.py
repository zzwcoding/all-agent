#!/usr/bin/env python3
"""meta_probe.py —— 元循环探针（票 28 建；票 29 增第 10 项与豁免复核并入，PRD F14）。

一键确定性体检：十项探针全部只读现有闸与文件（子进程采集 + 文件机读），
零 LLM、不新增判定真源——判定归各闸，探针只采集与呈现。

十项（〔硬闸〕红 → 退出码 1；（信息）红只注记不判死）：
  1.〔硬闸〕出厂集：fixture_run --require-fixtures --json，逐套 PASS/PENDING/FAIL
  2.〔硬闸〕语义闸：schema_check 对「目标域 + 溯源 ontology 根」各跑一次（票 34
     扩根，目标即根时去重；任一红即红），L1/L2/L4 计数
  3.（信息）CORE 分布：八问逐条 semantic_service_core --json，status 分布+期望对照。
     八问常量表与 fixtures/semantic-service/assertions.json CORE-01–08 同步维护
     （断言 fixture 是真源，此处是探针内置副本）——改问/改期望两处一起改。
     问题集按渤海域冻结：换域跑探针时本项期望对照自然漂移（信息红，不判死）。
  4.（信息）边界闸豁免：.skill-deps-allow 逐条列出+人工复核栏（值留空，批收官填；
     复核结论由 --review 或缺省 docs/meta/exemption-reviews.json 并入留痕，票 29）
  5.（信息）归档豁免：.archive-allow 同上（文件缺席=0 条，不是错）
  6.〔硬闸〕安装位：install_skills --check --json，漂移/孤儿/注册表规模
  7.〔硬闸〕skill↔卡同步：specs/modules.md `## skill:` 卡名集合 vs skills/*/SKILL.md
     目录集合双向差集——有 skill 无卡=违规（红）；有卡无 skill=待建（占位卡不判违规）
  8.（信息）提案池：docs/proposals/PROP-*.md status 计数 + proposal_check 子进程
     （报其退出码；rc=1 有冲突/违规 → 信息红）
  9.（信息）图基线：graph_index <target> --query <ID> --json 的节点/边快照
     （对照漂移用；快照值随报告走，ID 缺 --graph-query 传）
 10.〔硬闸〕信号路由表（票 29）：policies/signal-routing.json 自检——合法 JSON、
     routes 恰三类（kind 覆盖 业务错/工程错/元模型错）、每类 instances ≥2 条且
     指针逐个核实（commit 在 git log、PROP 文件在 docs/proposals/）；任一不满足
     =硬闸红（路由表坏=体检红；约定不落闸等于没有）。

豁免复核并入（票 29）：--review <JSON 路径> 指向人工复核结论文件（格式：
[{"file":"<豁免路径模式>","verdict":"保留|可收敛|…","reason":"…"}]，或
{"reviewedBy":"L0","reviewedAt":"2026-09-19","entries":[…同上]}）；缺省自动读
docs/meta/exemption-reviews.json（随批更新的机读结论，协议第 9 条④）。有则并入
报告第 4/5 节复核栏（复核人/日期进留痕），无则留空栏；结论文件缺席/不可解析
只注记不判死（复核是人工义务，探针不代判）。

报告：MD（十节+结论行）+ 机读 JSON；--out <路径>.md 同时落同名 .json；
缺省只打 MD 到 stdout。留痕报告带生成时间戳（留痕不是 golden，确定性只要求
"同仓快照重跑结论一致"）。

退出码：0 无硬闸红（硬闸项 SKIPPED 时结论 DEGRADED，仍退出 0）；
1 任一硬闸红；2 用法错误（本体目录不存在等）。
子进程工具缺席（无法 spawn，内部约定 rc=127）或输出不可解析 → 该项 SKIPPED
降级，探针不因单个工具缺席而崩（票面 AC4）。
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path

# rc 约定（探针内部）：127=工具无法 spawn；124=子进程超时
RC_SPAWN_FAIL = 127
RC_TIMEOUT = 124

PROBE_TITLES = {
    "1": "出厂集", "2": "语义闸", "3": "CORE 分布", "4": "边界闸豁免",
    "5": "归档豁免", "6": "安装位", "7": "skill↔卡同步", "8": "提案池",
    "9": "图基线", "10": "信号路由表",
}
HARD_IDS = {"1", "2", "6", "7", "10"}
STATUS_MARK = {"green": "GREEN", "red": "RED", "skipped": "SKIPPED"}

# 信号路由表契约（票 29，真源=policies/signal-routing.json；本表只定探针怎么查）
ROUTING_TABLE_REL = Path("policies") / "signal-routing.json"
ROUTING_KINDS = ("业务错", "工程错", "元模型错")
ROUTING_MIN_INSTANCES = 2  # 设计裁决：三类各 ≥2 个真实实例指针
DEFAULT_REVIEW_REL = Path("docs") / "meta" / "exemption-reviews.json"

# 八问常量表（真源=fixtures/semantic-service/assertions.json CORE-01–08，
# 票 25 冻结期望；本表是探针内置副本，同步维护，别处不立第二份）。
CORE_QUESTIONS = [
    {"core": "CORE-01", "q": "Q1", "ask": "日产量口径是什么？",
     "expect": "answered"},
    {"core": "CORE-02", "q": "Q3", "ask": "@AGG-BOHAI-001 有哪些行为？",
     "expect": "answered"},
    {"core": "CORE-03", "q": "Q4", "ask": "桶油增产成本的口径是什么？",
     "expect": "refused_missing"},
    {"core": "CORE-04", "q": "Q5", "ask": "@SCR-BOHAI-01 的界面细节",
     "expect": "refused_out_of_surface"},
    {"core": "CORE-05", "q": "Q8", "ask": "老完成率还能用吗？",
     "expect": "refused_banned"},
    {"core": "CORE-06", "q": "Q7", "ask": "剔检产量是什么口径？",
     "expect": "answered"},
    {"core": "CORE-07", "q": "Q2", "ask": "月度结算的口径是什么？",
     "expect": "answered"},
    {"core": "CORE-08", "q": "Q6", "ask": "有效产量的口径是什么？",
     "expect": "answered"},
]
CORE_STATUSES = ("answered", "refused_missing", "refused_banned",
                 "refused_out_of_surface")

DEFAULT_GRAPH_QUERY = "AGG-BOHAI-001"  # 渤海域真实聚合对象（票 25 CORE-02 锚点）

Runner = Callable[[Sequence[str]], "tuple[int, str, str]"]


# ---------- 基座 ----------

def subprocess_runner(root: Path) -> Runner:
    """默认 runner：cwd=root 跑子进程，返回 (rc, stdout, stderr)。

    工具无法 spawn（FileNotFoundError 等）→ rc=127；超时 → rc=124。
    """
    def run(cmd: Sequence[str]) -> "tuple[int, str, str]":
        try:
            proc = subprocess.run(list(cmd), capture_output=True, text=True,
                                  timeout=600, cwd=str(root))
        except subprocess.TimeoutExpired:
            return RC_TIMEOUT, "", f"子进程超时: {' '.join(cmd)}"
        except (OSError, ValueError) as exc:
            return RC_SPAWN_FAIL, "", f"工具缺席/无法执行: {exc}"
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    return run


def _item(pid: str, kind: str, status: str, summary: str,
          data: dict | None = None, error: str | None = None) -> dict:
    # kind 以 HARD_IDS 为准（采集器传入值仅作文档性冗余，防两处漂移）
    return {"id": pid, "title": PROBE_TITLES[pid],
            "kind": "hard" if pid in HARD_IDS else "info",
            "status": status, "summary": summary, "data": data or {},
            "error": error}


def _hard_item(pid, status, summary, data=None, error=None):
    return _item(pid, "hard", status, summary, data, error)


def _info_item(pid, status, summary, data=None, error=None):
    return _item(pid, "info", status, summary, data, error)


def _load_tool_json(rc: int, out: str, err: str) -> "tuple[dict | None, str | None]":
    """工具 stdout → JSON。工具缺席/超时/输出不可解析 → (None, 原因)。"""
    if rc in (RC_SPAWN_FAIL, RC_TIMEOUT):
        return None, err.strip() or f"rc={rc}"
    try:
        return json.loads(out), None
    except json.JSONDecodeError as exc:
        return None, f"输出不是合法 JSON（rc={rc}）: {exc}"


def _parse_allow(path: Path) -> "tuple[list[dict], list[str]]":
    """豁免清单逐行解析（`模式  # 理由`，理由必填——同归档闸格式）。

    返回 (entries, bad_lines)；缺理由行进 bad_lines 不静默吞。
    """
    entries: list[dict] = []
    bad: list[str] = []
    if not path.is_file():
        return entries, bad
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        pattern, sep, reason = s.partition("#")
        if not sep or not reason.strip():
            bad.append(f"第{lineno}行缺理由: {s}")
            continue
        entries.append({"pattern": pattern.strip(), "reason": reason.strip()})
    return entries, bad


def _prop_status(path: Path) -> str | None:
    """PROP-*.md YAML 头的 status 字段（只在 frontmatter 块内找，不扫正文）。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    scope = m.group(1) if m else text
    m2 = re.search(r"^status:\s*(\S+)\s*$", scope, re.M)
    return m2.group(1) if m2 else None


def load_reviews(path: Path | None) -> "tuple[dict | None, str | None]":
    """豁免复核结论文件（票 29）→ (规范化 dict, 解析错误)。

    接受两种形态：list[entry]（纯条目数组）或 {"reviewedBy","reviewedAt",
    "entries":[entry]}（带署名对象）；entry = {"file":<豁免路径模式>,
    "verdict":<结论>,"reason":<一行理由>}。文件缺席 → (None, None)（留空栏，
    不是错）；不可解析/结构不符 → (None, 原因)（注记，不判死）。
    """
    if path is None or not path.is_file():
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, f"复核结论文件不可解析（忽略，留空栏）: {exc}"
    if isinstance(data, list):
        return {"entries": data}, None
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return data, None
    return None, "复核结论文件结构不符（需 list 或 {entries:[...]}）（忽略，留空栏）"


def attach_reviews(root: Path, items: list[dict],
                   review_path: Path | None) -> list[dict]:
    """把复核结论按路径模式并入第 4/5 项 data["reviews"]（票 29）。

    byPattern: 模式 → {verdict, reason, reviewedBy, reviewedAt}（entry 级署名
    优先，缺省回落顶层）；unmatched: 结论文件里有、豁免清单里没有的模式
    （注记，防结论文件与豁免清单漂移后静默失配）；unreviewed: 豁免清单里有、
    结论文件里没有的模式（票 54 反向检查，防新增豁免漏复核被绿灯掩盖——
    第八轮 P2-B）。第 4 项两向差集任一非空 → 信息红（红灯形态照该项现行
    信息项语义，不进硬闸结论；双向零差才绿）。复核文件缺席仍留空栏不算差。
    """
    data, err = load_reviews(review_path)
    for item in items:
        if item["id"] in ("4", "5"):
            item["data"]["reviews"] = {
                "source": (str(review_path.relative_to(root))
                           if review_path and review_path.is_relative_to(root)
                           else (str(review_path) if review_path else None)),
                "loaded": data is not None,
                "reviewedBy": (data or {}).get("reviewedBy"),
                "reviewedAt": (data or {}).get("reviewedAt"),
                "byPattern": {},
                "unmatched": [],
                "error": err,
            }
    if data is None:
        return items
    top_who = data.get("reviewedBy")
    top_date = data.get("reviewedAt")
    by_pattern: dict = {}
    for entry in data.get("entries", []):
        if not isinstance(entry, dict) or not entry.get("file"):
            continue
        by_pattern[entry["file"]] = {
            "verdict": entry.get("verdict", ""),
            "reason": entry.get("reason", ""),
            "reviewedBy": entry.get("reviewedBy", top_who),
            "reviewedAt": entry.get("reviewedAt", top_date),
        }
    for item in items:
        if item["id"] not in ("4", "5"):
            continue
        rv = item["data"]["reviews"]
        patterns = [e["pattern"] for e in item["data"].get("entries", [])]
        rv["byPattern"] = {p: c for p, c in by_pattern.items() if p in patterns}
        rv["unmatched"] = sorted(set(by_pattern) - set(patterns))
        # 票 54（第八轮 P2-B）反向检查：豁免有、复核无
        rv["unreviewed"] = sorted(set(patterns) - set(by_pattern))
        if rv["byPattern"]:
            # 摘要行同步改口，防"总表说留空、正文已填"的自相矛盾留痕
            who = rv.get("reviewedBy") or "—"
            when = rv.get("reviewedAt") or "—"
            n_entries = len(item["data"].get("entries", []))
            item["summary"] = (f"{n_entries} 条豁免（复核结论已并入 "
                               f"{len(rv['byPattern'])} 条，复核人 {who}，"
                               f"复核日期 {when}）")
        # 第 4 项双向差集任一非空 → 信息红（信息项语义，不进硬闸结论；
        # 第 5 项维持注记形态——复核结论按节归属，零条目节不背另一节噪音）
        if item["id"] == "4" and (rv["unmatched"] or rv["unreviewed"]):
            diffs = []
            if rv["unmatched"]:
                diffs.append(f"{len(rv['unmatched'])} 条结论模式未匹配豁免清单")
            if rv["unreviewed"]:
                diffs.append(f"{len(rv['unreviewed'])} 条豁免无复核结论")
            item["status"] = "red"
            item["summary"] += "；" + "、".join(diffs) + "（信息红）"
    return items


# ---------- 九项采集器（全部注入式：root/runner 由调用方给） ----------

def probe_fixtures(root: Path, runner: Runner) -> dict:
    """1. 出厂集：fixture_run --require-fixtures，逐套 PASS/PENDING/FAIL。"""
    rc, out, err = runner([sys.executable, "tools/fixture_run.py",
                           "--require-fixtures", "--json"])
    data, skip = _load_tool_json(rc, out, err)
    if data is None:
        return _hard_item("1", "skipped", f"出厂集 runner 不可用，降级 SKIPPED：{skip}",
                          error=err.strip() or skip)
    suites = [{"name": f.get("name", ""), "status": f.get("status", "")}
              for f in data.get("fixtures", [])]
    counts = dict(Counter(s["status"] for s in suites))
    n_fail = counts.get("fail", 0)
    ok = rc == 0 and data.get("status") == "pass" and n_fail == 0
    if ok:
        summary = (f"{counts.get('pass', 0)}/{len(suites)} 套全过"
                   f"（pending {counts.get('pending', 0)}，fail 0）")
    else:
        bad = "、".join(s["name"] for s in suites if s["status"] == "fail") or " runner 非零退出"
        summary = f"出厂集有红（fail {n_fail}）：{bad}"
    return _hard_item("1", "green" if ok else "red", summary,
                      {"suites": suites, "counts": counts,
                       "runnerExitCode": rc, "reportStatus": data.get("status")})


def find_ontology_root(target: Path) -> Path | None:
    """溯源 ontology 根（票 34 P2-A 扩根）：从目标目录起向上找含 `schema/`
    子目录的祖先（含目标自身，最多向上 3 级）。目标本身即根时返回自身
    （probe 侧去重只跑一次）；3 级内找不到返回 None（仅跑目标域）。"""
    cur = target
    for depth in range(4):  # 自身 + 向上 3 级
        if (cur / "schema").is_dir():
            return cur
        if depth == 3 or cur.parent == cur:
            break
        cur = cur.parent
    return None


def probe_schema(root: Path, target: Path, runner: Runner) -> dict:
    """2. 语义闸：schema_check 对「目标域 + 溯源 ontology 根」各跑一次（票 34
    扩根——根是任一域的超集，裸仓根绿挂硬闸：patterns 排除后域内绿不等于仓根
    绿，根下任一真域坏 YAML 根必红），L1/L2/L4 计数；目标即根时去重只跑一次。
    硬闸语义：任一红即红。"""
    checks = [target]
    ont_root = find_ontology_root(target)
    if ont_root is not None and ont_root != target:
        checks.append(ont_root)
    runs: list[dict] = []
    for tgt in checks:
        rc, out, err = runner([sys.executable, "tools/schema_check.py",
                               str(tgt), "--json"])
        data, skip = _load_tool_json(rc, out, err)
        if data is None:
            return _hard_item("2", "skipped", f"语义闸不可用，降级 SKIPPED：{skip}",
                              error=err.strip() or skip)
        levels = data.get("levels", {})
        files = data.get("files")
        runs.append({
            "target": str(tgt),
            "role": "目标域" if tgt == target else "仓根",
            "status": data.get("status"),
            "levels": {"L1": levels.get("L1", 0), "L2": levels.get("L2", 0),
                       "L4": levels.get("L4", 0)},
            "violationCount": len(data.get("violations", [])),
            "fileCount": files if isinstance(files, int) else None,
            "runnerExitCode": rc,
        })
    reds = [r for r in runs if r["status"] != "pass" or r["runnerExitCode"] != 0]
    deciding = reds[0] if reds else runs[0]
    ok = not reds
    levels = deciding["levels"]
    n_files = deciding["fileCount"]
    n_viol = sum(r["violationCount"] for r in runs)
    if ok:
        scope = "目标域" + ("+仓根" if len(runs) > 1 else "")
        summary = (f"L1/L2/L4 全 0（pass，{scope}）"
                   + (f"，检查文件 {n_files}" if n_files is not None else ""))
    else:
        summary = (f"语义闸有红（{'、'.join(r['role'] for r in reds)}）："
                   f"L1 {levels.get('L1', 0)} / L2 {levels.get('L2', 0)}"
                   f" / L4 {levels.get('L4', 0)}（violation {n_viol} 条，"
                   f"rc={deciding['runnerExitCode']}）")
    return _hard_item("2", "green" if ok else "red", summary,
                      {"status": deciding["status"], "levels": levels,
                       "violationCount": n_viol, "fileCount": n_files,
                       "runnerExitCode": deciding["runnerExitCode"],
                       "ontologyRoot": str(ont_root) if ont_root else None,
                       "rootChecked": len(runs) > 1,
                       "runs": runs})


def probe_core(root: Path, target: Path, runner: Runner) -> dict:
    """3. CORE 分布：八问逐条跑核心，status 分布 + 期望对照（信息项）。"""
    rows = []
    for q in CORE_QUESTIONS:
        rc, out, err = runner([sys.executable, "tools/semantic_service_core.py",
                               str(target), "--ask", q["ask"], "--json"])
        if rc in (RC_SPAWN_FAIL, RC_TIMEOUT):
            actual = "skipped"
        else:
            try:
                verdict = json.loads(out)
                actual = verdict.get("status") if isinstance(verdict, dict) else None
            except json.JSONDecodeError:
                actual = None
            if not actual:
                actual = "error"
        rows.append({"core": q["core"], "q": q["q"], "ask": q["ask"],
                     "expect": q["expect"], "actual": actual,
                     "match": actual == q["expect"]})
    dist = dict(Counter(r["actual"] for r in rows))
    if all(r["actual"] == "skipped" for r in rows):
        return _info_item("3", "skipped", "语义核心缺席，八问未采，降级 SKIPPED",
                          {"dist": dist, "questions": rows})
    refused = sum(dist.get(s, 0) for s in CORE_STATUSES if s != "answered")
    answered = dist.get("answered", 0)
    bad = [r for r in rows if not r["match"]]
    status = "green" if not bad else "red"
    summary = (f"answered {answered}/{len(rows)}，拒答 {refused}/{len(rows)}"
               f"（missing {dist.get('refused_missing', 0)} / banned "
               f"{dist.get('refused_banned', 0)} / out_of_surface "
               f"{dist.get('refused_out_of_surface', 0)}）")
    if bad:
        summary += f"；{len(bad)} 问与冻结期望不符（信息红）"
    return _info_item("3", status, summary,
                      {"dist": dist, "questions": rows, "answered": answered,
                       "refused": refused, "mismatched": [r["core"] for r in bad]})


def probe_boundary_allow(root: Path) -> dict:
    """4. 边界闸豁免：.skill-deps-allow 逐条+人工复核栏（信息项）。"""
    entries, bad = _parse_allow(root / ".skill-deps-allow")
    status = "red" if bad else "green"
    summary = f"{len(entries)} 条豁免（复核栏留空待批收官填）"
    if bad:
        summary += f"；{len(bad)} 行缺理由（信息红）"
    return _info_item("4", status, summary,
                      {"file": ".skill-deps-allow", "entries": entries,
                       "badLines": bad, "reviewSlots": len(entries)})


def probe_archive_allow(root: Path) -> dict:
    """5. 归档豁免：.archive-allow 逐条+人工复核栏（信息项；缺席=0 条）。"""
    allow = root / ".archive-allow"
    entries, bad = _parse_allow(allow)
    status = "red" if bad else "green"
    note = "" if allow.is_file() else "（豁免文件不存在，0 条——不是错）"
    summary = f"{len(entries)} 条豁免{note}"
    if bad:
        summary += f"；{len(bad)} 行缺理由（信息红）"
    return _info_item("5", status, summary,
                      {"file": ".archive-allow", "exists": allow.is_file(),
                       "entries": entries, "badLines": bad,
                       "reviewSlots": len(entries)})


def probe_install(root: Path, runner: Runner) -> dict:
    """6. 安装位：install_skills --check，漂移/孤儿/注册表规模。"""
    rc, out, err = runner([sys.executable, "tools/install_skills.py",
                           "--check", "--json"])
    data, skip = _load_tool_json(rc, out, err)
    if data is None:
        return _hard_item("6", "skipped", f"安装位核查不可用，降级 SKIPPED：{skip}",
                          error=err.strip() or skip)
    diffs = data.get("diffs", [])
    orphans = data.get("orphans", [])
    by_type = dict(Counter(d.get("type", "?") for d in diffs))
    ok = rc == 0 and not diffs and not orphans
    if ok:
        summary = (f"零漂移零孤儿，{len(data.get('consistent', []))} 个 skill "
                   f"双位置一致（注册表规模 {len(data.get('skills', []))}）")
    else:
        summary = (f"漂移 {len(diffs)}（{by_type}）+ 孤儿 {len(orphans)}"
                   f"（rc={rc}）")
    return _hard_item("6", "green" if ok else "red", summary,
                      {"registrySize": len(data.get("skills", [])),
                       "consistent": data.get("consistent", []),
                       "drift": diffs, "driftByType": by_type,
                       "driftCount": len(diffs),
                       "orphans": [o.get("skill", "?") for o in orphans],
                       "orphanCount": len(orphans), "runnerExitCode": rc})


def probe_card_sync(root: Path) -> dict:
    """7. skill↔卡同步：卡名集合 vs skills/*/SKILL.md 双向差集。

    有 skill 无卡=违规（硬红）；有卡无 skill=待建（占位卡不判违规）。
    """
    modules = root / "specs" / "modules.md"
    if not modules.is_file():
        return _hard_item("7", "skipped", "specs/modules.md 不存在，降级 SKIPPED",
                          error=f"{modules} 不存在")
    text = modules.read_text(encoding="utf-8")
    cards = re.findall(r"^## skill: (.+?)\s*$", text, re.M)
    skills_dir = root / "skills"
    skills = (sorted(p.name for p in skills_dir.iterdir()
                     if p.is_dir() and (p / "SKILL.md").is_file())
              if skills_dir.is_dir() else [])
    skill_no_card = sorted(set(skills) - set(cards))
    card_no_skill = sorted(set(cards) - set(skills))
    ok = not skill_no_card
    summary = (f"卡 {len(cards)} : skill {len(skills)}"
               f"；有 skill 无卡 {len(skill_no_card)}（违规向）"
               f"；有卡无 skill {len(card_no_skill)}（占位卡待建，不判违规）")
    return _hard_item("7", "green" if ok else "red", summary,
                      {"cards": cards, "skills": skills,
                       "skillNoCard": skill_no_card,
                       "cardNoSkill": card_no_skill})


def probe_proposals(root: Path, runner: Runner) -> dict:
    """8. 提案池：PROP-*.md status 计数 + proposal_check 退出码（信息项）。"""
    pdir = root / "docs" / "proposals"
    files = sorted(pdir.glob("PROP-*.md")) if pdir.is_dir() else []
    counts: Counter = Counter()
    unparsed = []
    for f in files:
        st = _prop_status(f)
        if st is None:
            unparsed.append(f.name)
        else:
            counts[st] += 1
    rc, out, err = runner([sys.executable, "tools/proposal_check.py",
                           str(pdir), "--json"])
    data, skip = _load_tool_json(rc, out, err)
    if data is None:
        return _info_item("8", "skipped",
                          f"proposal_check 不可用，冲突快查未跑：{skip}",
                          {"files": len(files), "statusCounts": dict(counts),
                           "unparsed": unparsed},
                          error=err.strip() or skip)
    ok = rc == 0 and not unparsed
    summary = (f"{len(files)} 份提案（status: "
               + " ".join(f"{k}×{v}" for k, v in sorted(counts.items()))
               + f"）；proposal_check rc={rc}（violations "
               f"{len(data.get('violations', []))}）")
    if unparsed:
        summary += f"；{len(unparsed)} 份缺 status 行（信息红）"
    return _info_item("8", "green" if ok else "red", summary,
                      {"files": len(files), "statusCounts": dict(counts),
                       "unparsed": unparsed,
                       "proposalCheck": {"exitCode": rc,
                                         "status": data.get("status"),
                                         "violations":
                                             len(data.get("violations", []))}})


def probe_graph(root: Path, target: Path, runner: Runner,
                query_id: str) -> dict:
    """9. 图基线：graph_index 节点/边快照（对照漂移用，信息项）。"""
    rc, out, err = runner([sys.executable, "tools/graph_index.py",
                           str(target), "--query", query_id, "--json"])
    data, skip = _load_tool_json(rc, out, err)
    if data is None:
        return _info_item("9", "skipped", f"图索引不可用，降级 SKIPPED：{skip}",
                          error=err.strip() or skip)
    stats = data.get("stats", {})
    found = bool(data.get("found"))
    summary = (f"查询 {query_id}（{'命中' if found else '未命中，仅取全图统计'}）"
               f"：节点 {stats.get('nodes', '?')} / 边 {stats.get('edges', '?')}")
    return _info_item("9", "green", summary,
                      {"query": query_id, "found": found,
                       "nodes": stats.get("nodes"), "edges": stats.get("edges"),
                       "runnerExitCode": rc})


def probe_signal_routing(root: Path, runner: Runner) -> dict:
    """10. 信号路由表自检（硬闸，票 29）：表在、合法 JSON、恰三类、实例指针逐个真实。

    (a) policies/signal-routing.json 存在且合法 JSON；(b) routes 恰三类（kind
    覆盖 业务错/工程错/元模型错，无缺无重无多）；(c) 每类 instances ≥2 条，每条
    指针核实——commit 走 git log 逐个验存、PROP 逐个查 docs/proposals/ 文件在池；
    (d) 任一不满足=硬闸红。git 本身缺席 → SKIPPED 降级（环境问题不是表的问题）。
    """
    table = root / ROUTING_TABLE_REL
    if not table.is_file():
        return _hard_item("10", "red",
                          f"路由表缺失：{ROUTING_TABLE_REL} 不存在（硬闸红）",
                          {"table": str(ROUTING_TABLE_REL), "exists": False,
                           "errors": ["路由表文件不存在"]})
    try:
        data = json.loads(table.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return _hard_item("10", "red",
                          f"路由表不是合法 JSON（硬闸红）: {exc}",
                          {"table": str(ROUTING_TABLE_REL), "exists": True,
                           "errors": [f"JSON 不可解析: {exc}"]})
    if not isinstance(data, dict) or not isinstance(data.get("routes"), list):
        return _hard_item("10", "red",
                          "路由表结构不符：缺 routes 数组（硬闸红）",
                          {"table": str(ROUTING_TABLE_REL), "exists": True,
                           "errors": ["routes 不是数组（或缺顶层 routes 键）"]})
    routes = data["routes"]
    kinds = [r.get("kind") for r in routes if isinstance(r, dict)]
    errors: list[str] = []
    for k in ROUTING_KINDS:
        if k not in kinds:
            errors.append(f"缺路由类「{k}」")
    for k, n in Counter(kinds).items():
        if n > 1:
            errors.append(f"路由类「{k}」重复 {n} 条（恰三类=不许重）")
    for k in kinds:
        if k not in ROUTING_KINDS:
            errors.append(f"未知路由类「{k}」（合法: {'/'.join(ROUTING_KINDS)}）")

    commit_checks: list[dict] = []
    prop_checks: list[dict] = []
    route_rows: list[dict] = []
    for r in routes:
        if not isinstance(r, dict):
            errors.append("routes 含非对象条目")
            continue
        kind = r.get("kind")
        dest, mech = r.get("destination"), r.get("mechanism")
        if not dest or not mech:
            errors.append(f"路由「{kind}」缺 destination/mechanism 字段")
        instances = r.get("instances")
        if not isinstance(instances, list) or len(instances) < ROUTING_MIN_INSTANCES:
            errors.append(f"路由「{kind}」实例指针不足 {ROUTING_MIN_INSTANCES} 条"
                          f"（实有 {len(instances) if isinstance(instances, list) else 0}）")
            route_rows.append({"kind": kind, "destination": dest,
                               "instanceCount": len(instances)
                               if isinstance(instances, list) else 0})
            continue
        route_rows.append({"kind": kind, "destination": dest,
                           "instanceCount": len(instances)})
        for n, inst in enumerate(instances, 1):
            if not isinstance(inst, dict) or not (inst.get("commit") or inst.get("props")):
                errors.append(f"路由「{kind}」第 {n} 条实例缺 commit/props 指针")
                continue
            commit = inst.get("commit")
            if commit:
                rc, _out, err = runner(["git", "-C", str(root), "log",
                                        "--format=%h", "--no-walk", "-1",
                                        str(commit)])
                if rc in (RC_SPAWN_FAIL, RC_TIMEOUT):
                    return _hard_item("10", "skipped",
                                      f"git 不可用，commit 核实降级 SKIPPED：{err.strip() or rc}",
                                      error=err.strip() or f"rc={rc}")
                ok = rc == 0
                commit_checks.append({"commit": commit, "ticket": inst.get("ticket"),
                                      "desc": inst.get("desc", ""), "exists": ok})
                if not ok:
                    errors.append(f"commit {commit}（{inst.get('desc', '')}）不在 git log")
            for prop in inst.get("props") or []:
                in_pool = (root / "docs" / "proposals" / f"{prop}.md").is_file()
                prop_checks.append({"prop": prop, "exists": in_pool})
                if not in_pool:
                    errors.append(f"提案 {prop} 不在 docs/proposals/（不在池）")
    ok = not errors
    if ok:
        summary = (f"三类路由齐（{'/'.join(ROUTING_KINDS)}），实例指针 "
                   f"{len(commit_checks)} commit 全在 log + {len(prop_checks)} PROP 全在池")
    else:
        head = "；".join(errors[:3])
        more = f"（等共 {len(errors)} 处）" if len(errors) > 3 else ""
        summary = f"路由表自检红 {len(errors)} 处：{head}{more}"
    return _hard_item("10", "green" if ok else "red", summary,
                      {"table": str(ROUTING_TABLE_REL), "exists": True,
                       "version": data.get("version"), "routes": route_rows,
                       "kindsFound": kinds, "commitChecks": commit_checks,
                       "propChecks": prop_checks, "errors": errors})


# ---------- 汇总 / 评估 / 渲染 ----------

def collect_all(root: Path, target: Path, runner: Runner,
                graph_query: str = DEFAULT_GRAPH_QUERY) -> list[dict]:
    """跑十项探针。单项采集异常 → 该项 SKIPPED 降级，不崩（票面 AC4）。"""
    specs = [
        ("1", lambda: probe_fixtures(root, runner)),
        ("2", lambda: probe_schema(root, target, runner)),
        ("3", lambda: probe_core(root, target, runner)),
        ("4", lambda: probe_boundary_allow(root)),
        ("5", lambda: probe_archive_allow(root)),
        ("6", lambda: probe_install(root, runner)),
        ("7", lambda: probe_card_sync(root)),
        ("8", lambda: probe_proposals(root, runner)),
        ("9", lambda: probe_graph(root, target, runner, graph_query)),
        ("10", lambda: probe_signal_routing(root, runner)),
    ]
    items = []
    for pid, fn in specs:
        try:
            items.append(fn())
        except Exception as exc:  # 探针不死：单工具故障只降级自己
            kind = "hard" if pid in HARD_IDS else "info"
            items.append(_item(pid, kind, "skipped",
                               "采集异常，降级 SKIPPED",
                               error=f"{type(exc).__name__}: {exc}"))
    return items


def evaluate(items: list[dict]) -> "tuple[str, int]":
    """结论与退出码：硬闸红 → (FAIL, 1)；硬闸全绿无缺 → (PASS, 0)；
    硬闸全绿但有硬闸项 SKIPPED → (DEGRADED, 0)。信息项不进结论。"""
    hard = [i for i in items if i["kind"] == "hard"]
    red = [i for i in hard if i["status"] == "red"]
    skipped = [i for i in hard if i["status"] == "skipped"]
    if red:
        return "FAIL", 1
    if skipped:
        return "DEGRADED", 0
    return "PASS", 0


def render_md(items: list[dict], conclusion: str, target: Path, root: Path,
              generated_at: str) -> str:
    lines: list[str] = []
    hard = [i for i in items if i["kind"] == "hard"]
    red = [i for i in hard if i["status"] == "red"]
    skipped = [i for i in hard if i["status"] == "skipped"]
    if conclusion == "PASS":
        tail = f"硬闸 {len(hard)}/{len(hard)} 全绿，信息项仅注记"
    elif conclusion == "FAIL":
        tail = "硬闸红灯：" + "、".join(f"#{i['id']} {i['title']}" for i in red)
    else:
        tail = "硬闸全绿但 " + "、".join(f"#{i['id']} {i['title']}"
                                      for i in skipped) + " 降级 SKIPPED"
    lines += [
        "# 元循环体检报告（meta_probe · 票 28/29）",
        "",
        f"- 生成时间: {generated_at}",
        f"- 本体目标: {target}",
        f"- 仓根: {root}",
        "- 探针: 十项（零 LLM，只读现有闸与文件；判定归各闸，本报告只采集与呈现）",
        "",
        f"**结论: {conclusion}** —— {tail}。退出码 "
        f"{'1' if conclusion == 'FAIL' else '0'}。",
        "",
        "| # | 探针 | 性质 | 状态 | 摘要 |",
        "|---|---|---|---|---|",
    ]
    for i in items:
        lines.append(f"| {i['id']} | {i['title']} | "
                     f"{'硬闸' if i['kind'] == 'hard' else '信息'} "
                     f"| {STATUS_MARK[i['status']]} | {i['summary']} |")
    lines.append("")

    for i in items:
        kind_label = "硬闸" if i["kind"] == "hard" else "信息"
        lines += ["", f"## {i['id']}. {i['title']}（{kind_label}）", "",
                  f"状态: **{STATUS_MARK[i['status']]}** — {i['summary']}", ""]
        if i["error"]:
            lines += [f"- 降级原因: {i['error']}", ""]
        d = i["data"]
        if i["id"] == "1" and d.get("suites"):
            lines += ["| 出厂集 | 判定 |", "|---|---|"]
            for s in d["suites"]:
                mark = {"pass": "PASS", "pending": "PENDING", "fail": "FAIL"}.get(
                    s["status"], s["status"].upper())
                lines.append(f"| {s['name']} | {mark} |")
        elif i["id"] == "2" and d.get("levels") is not None:
            lv = d["levels"]
            scope = ("目标域 + 仓根（" + d["ontologyRoot"] + "）"
                     if d.get("rootChecked") else "仅目标域")
            lines += [f"- 检查范围: {scope}",
                      f"- L1: {lv.get('L1', 0)}　L2: {lv.get('L2', 0)}　"
                      f"L4: {lv.get('L4', 0)}　violation: {d.get('violationCount', 0)}"]
            for r in d.get("runs", []):
                mark = "pass" if r["status"] == "pass" else f"红（{r['status']}）"
                lines.append(f"  - {r['role']} `{r['target']}`: {mark}"
                             f"（L1 {r['levels']['L1']} / L2 {r['levels']['L2']}"
                             f" / L4 {r['levels']['L4']}）")
        elif i["id"] == "3" and d.get("questions"):
            dist = d["dist"]
            lines.append("status 分布: " + "，".join(
                f"{s}×{dist.get(s, 0)}" for s in CORE_STATUSES)
                + f"（skipped×{dist.get('skipped', 0)}，error×{dist.get('error', 0)}）")
            lines += ["", "| CORE | 问 | 期望 | 实际 | 对照 |", "|---|---|---|---|---|"]
            for r in d["questions"]:
                ask = r["ask"] if len(r["ask"]) <= 24 else r["ask"][:23] + "…"
                lines.append(f"| {r['core']}（{r['q']}） | {ask} | {r['expect']} "
                             f"| {r['actual']} | {'一致' if r['match'] else '**漂移**'} |")
        elif i["id"] in ("4", "5") and d.get("entries") is not None:
            rv = d.get("reviews") or {}
            rmap = rv.get("byPattern") or {}
            if rv.get("loaded") and d["entries"]:
                # 复核注记只落在有条目的节（零条目节如"归档豁免"不背另一节的未匹配噪音）
                who = rv.get("reviewedBy") or "—"
                when = rv.get("reviewedAt") or "—"
                note = (f"豁免复核: 本次留痕并入 {len(rmap)} 条复核结论"
                        f"（复核人 {who}，复核日期 {when}；来源 {rv.get('source')}）")
                if rv.get("unmatched"):
                    note += (f"；{len(rv['unmatched'])} 条结论模式未匹配豁免清单"
                             f"（{'、'.join(rv['unmatched'])}）")
                if rv.get("unreviewed"):
                    note += (f"；{len(rv['unreviewed'])} 条豁免无复核结论"
                             f"（{'、'.join(rv['unreviewed'])}）")
                lines += [note, ""]
            if rv.get("error"):
                lines.append(f"复核结论文件注记: {rv['error']}")
                lines.append("")
            col = ("人工复核结论（复核人 / 日期）" if rmap
                   else "人工复核（值留空，批收官填）")
            if not d["entries"] and not d.get("badLines"):
                lines.append("（无豁免条目）")
            else:
                lines += ["| # | 路径模式 | 理由 | " + col + " |",
                          "|---|---|---|---|"]
                for n, e in enumerate(d["entries"], 1):
                    filled = "- [ ] 保留 / 可收敛: ____"
                    c = rmap.get(e["pattern"])
                    if c:
                        filled = (f"- [x] {c['verdict']}"
                                  f"（{c.get('reviewedBy') or '—'} "
                                  f"{c.get('reviewedAt') or '—'}）"
                                  f": {c.get('reason') or '—'}")
                    lines.append(f"| {n} | `{e['pattern']}` | {e['reason']} "
                                 f"| {filled} |")
                for n, b in enumerate(d.get("badLines", []), 1):
                    lines.append(f"| 坏{n} | — | {b} | - [ ] 修复缺理由行 |")
        elif i["id"] == "6" and d:
            lines += [f"- 注册表规模: {d.get('registrySize', 0)} 个 skill",
                      f"- 双位置一致: {', '.join(d.get('consistent', [])) or '—'}",
                      f"- 漂移: {d.get('driftCount', 0)}"
                      f"（{d.get('driftByType', {})}）"
                      + ("" if not d.get("drift") else
                         "；" + "；".join(f"`{x.get('skill')}/{x.get('path')}` "
                                         f"{x.get('type')}" for x in d["drift"])),
                      f"- 孤儿: {d.get('orphanCount', 0)}"
                      + ("" if not d.get("orphans") else
                         "；" + "、".join(d["orphans"]))]
        elif i["id"] == "7" and d:
            lines += [f"- 卡（modules.md `## skill:`）: {len(d.get('cards', []))} 张",
                      f"- skill（skills/*/SKILL.md）: {len(d.get('skills', []))} 个"]
            if d.get("cardNoSkill"):
                lines += ["- 有卡无 skill（占位卡待建，不判违规）: "
                          + "、".join(d["cardNoSkill"])]
            lines += ["- 有 skill 无卡（违规向）: "
                      + ("、".join(d["skillNoCard"]) if d.get("skillNoCard")
                         else "无")]
        elif i["id"] == "8" and d:
            lines.append("status 计数: " + (" ".join(
                f"{k}×{v}" for k, v in sorted(d.get("statusCounts", {}).items()))
                or "（无提案）"))
            pc = d.get("proposalCheck") or {}
            if pc:
                lines += [f"- proposal_check: rc={pc.get('exitCode')}，"
                          f"status={pc.get('status')}，"
                          f"violations {pc.get('violations', 0)} 条"]
        elif i["id"] == "9" and d:
            lines += [f"- 查询 ID: {d.get('query')}（"
                      f"{'命中' if d.get('found') else '未命中'}）",
                      f"- 图基线快照: 节点 {d.get('nodes')} / 边 {d.get('edges')}"
                      "（对照漂移用，随本报告走）"]
        elif i["id"] == "10" and d:
            for r in d.get("routes", []):
                lines.append(f"- {r.get('kind')} → {r.get('destination')}"
                             f"（实例 {r.get('instanceCount', 0)} 条）")
            lines += [f"- commit 核实: {sum(1 for c in d.get('commitChecks', [])
                      if c.get('exists'))}/{len(d.get('commitChecks', []))} 在 git log",
                      f"- PROP 在池: {sum(1 for p in d.get('propChecks', [])
                      if p.get('exists'))}/{len(d.get('propChecks', []))}"
                      "（docs/proposals/ 文件在场）"]
            if d.get("errors"):
                lines.append("- 红灯明细: " + "；".join(d["errors"]))
    lines.append("")
    return "\n".join(lines)


def render_json(items: list[dict], conclusion: str, exit_code: int,
                target: Path, root: Path, generated_at: str,
                graph_query: str) -> str:
    return json.dumps({
        "tool": "meta_probe",
        "ticket": "28/29",
        "generatedAt": generated_at,
        "root": str(root),
        "ontologyTarget": str(target),
        "graphQuery": graph_query,
        "conclusion": conclusion,
        "exitCode": exit_code,
        "hardProbeIds": sorted(HARD_IDS),
        "probes": items,
    }, ensure_ascii=False, indent=2)


def main(argv=None, runner: Runner | None = None) -> int:
    """runner 参数供单测注入假 runner（默认在仓根跑真子进程）。"""
    ap = argparse.ArgumentParser(
        description="元循环探针（票 28/29）：十项确定性体检，MD+JSON 报告；"
                    "退出码 0 硬闸全绿 / 1 硬闸红 / 2 用法错误")
    ap.add_argument("target", help="ontology 目录（如 ontology/bohai）")
    ap.add_argument("--out", default=None,
                    help="报告落盘路径（.md；同时落同名 .json；缺省只打 stdout）")
    ap.add_argument("--root", default=None,
                    help="仓根（默认取本脚本的上级目录）")
    ap.add_argument("--graph-query", default=DEFAULT_GRAPH_QUERY,
                    help="图基线探针查询 ID（缺省=渤海域真实聚合对象；"
                         "换域请传该域真实 ID）")
    ap.add_argument("--review", default=None,
                    help="豁免复核结论 JSON（票 29；缺省自动读仓根 "
                         + str(DEFAULT_REVIEW_REL) + "，文件缺席=留空栏）")
    args = ap.parse_args(argv)

    root = (Path(args.root).resolve() if args.root
            else Path(__file__).resolve().parent.parent)
    target = Path(args.target)
    if not target.is_dir():
        print(f"用法错误: 本体目录不存在: {args.target}", file=sys.stderr)
        return 2
    review_path = (Path(args.review) if args.review
                   else (root / DEFAULT_REVIEW_REL
                         if (root / DEFAULT_REVIEW_REL).is_file() else None))

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    items = collect_all(root, target, runner or subprocess_runner(root),
                        graph_query=args.graph_query)
    items = attach_reviews(root, items, review_path)
    conclusion, exit_code = evaluate(items)

    md = render_md(items, conclusion, target, root, generated_at)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        json_path = out_path.with_suffix(".json")
        json_path.write_text(
            render_json(items, conclusion, exit_code, target, root,
                        generated_at, args.graph_query), encoding="utf-8")
        print(f"已落盘: {out_path}")
        print(f"已落盘: {json_path}")
        print(f"结论: {conclusion}（退出码 {exit_code}）")
    else:
        sys.stdout.write(md)  # 与 --out 落盘字节一致（不因 print 追加空行）
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
