#!/usr/bin/env python3
"""report_numbers —— 收官报告数字快照（票 77）。

收官报告/锚点里的可机取数字（测试数/域清单/生成物面/审记状态）统一现跑现取、
落盘留痕，替代手写手查——票 37/55/73 三次「数字过期」勘误同根。只读、确定性。

用法:
    python3 tools/report_numbers.py                      # md 打 stdout
    python3 tools/report_numbers.py --out docs/meta/指标快照-2026-09-27.md
退出码: 0 正常 / 2 配置错
"""

import argparse
import json
import subprocess
import sys
import unittest
from datetime import datetime
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

import onboard_check  # noqa: E402  域枚举同源
import review_gate    # noqa: E402  审记状态机唯一真源


def git_head(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return "未知"
    return proc.stdout.strip() if proc.returncode == 0 else "未知"


def unit_test_count(root: Path) -> int:
    """单测计数（只 discover 数用例，不执行；tools/ 缺席=0）。"""
    tdir = root / "tools"
    if not tdir.is_dir():
        return 0
    suite = unittest.TestLoader().discover(str(tdir), pattern="test_*.py")
    return suite.countTestCases()


def domain_rows(root: Path) -> "list[dict]":
    rows = []
    for d in onboard_check.list_domains(root):
        try:
            m = json.loads(
                (root / "ontology" / d / "manifest.json")
                .read_text(encoding="utf-8"))
        except (ValueError, OSError):
            m = {}
        dpath = root / "ontology" / d
        rows.append({
            "domain": d,
            "profile": m.get("profile", "?"),
            "modelFiles": len(list(dpath.glob("*.yaml")))
                          + len(list(dpath.glob("*.yml"))),
            "omitted": len(m.get("omittedModels") or []),
        })
    return rows


def export_rows(root: Path) -> "list[dict]":
    rdir = root / "exports" / "reviews"
    rows = []
    for pat in review_gate.VERIFY_ALL_GLOBS:
        for t in sorted(root.glob(pat)):
            _c, status, _r, _rec, _n = review_gate.verify_record(
                t, review_gate.review_path_for(t, rdir))
            rows.append({"target": str(t.relative_to(root)), "review": status})
    return rows


def collect(root: Path) -> dict:
    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gitHead": git_head(root),
        "unitTests": unit_test_count(root),
        "domains": domain_rows(root),
        "exports": export_rows(root),
        "checkupNotes": len(list((root / "docs" / "meta").glob("体检-*.md")))
                        if (root / "docs" / "meta").is_dir() else 0,
    }


def render_md(report: dict) -> str:
    lines = [
        "# 指标快照（票 77 · report_numbers 机取）",
        "",
        f"- 生成时点: {report['generatedAt']}  git HEAD: {report['gitHead']}",
        f"- 单测用例数: {report['unitTests']}（discover 计数，未执行）",
        f"- 体检留痕: docs/meta/体检-*.md 共 {report['checkupNotes']} 篇",
        "",
        "| 域 | profile | 模型文件 | 豁免数 |",
        "|---|---|---|---|",
    ]
    for r in report["domains"]:
        lines.append(f"| {r['domain']} | {r['profile']} | "
                     f"{r['modelFiles']} | {r['omitted']} |")
    lines += ["", "| 生成物 | 审记 |", "|---|---|"]
    for r in report["exports"]:
        lines.append(f"| {r['target']} | {r['review']} |")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="收官报告数字快照（票 77）：可机取数字现跑现取，勿手写手查")
    ap.add_argument("--out", default=None,
                    help="落盘路径（.md；同时落同名 .json；缺省只打 stdout）")
    ap.add_argument("--root", default=None, help="仓根（默认取本脚本的上级目录）")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve() if args.root else REPO_ROOT
    report = collect(root)
    md = render_md(report)
    if args.out:
        out_path = Path(args.out)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
            out_path.with_suffix(".json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except OSError as exc:
            print(f"配置错误: 落盘失败: {exc}", file=sys.stderr)
            return 2
        print(f"已落盘: {out_path}")
        print(f"已落盘: {out_path.with_suffix('.json')}")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
