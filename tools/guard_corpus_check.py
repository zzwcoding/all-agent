#!/usr/bin/env python3
"""guard_corpus_check.py —— 守卫正则例集回归检具（票 20：守卫单源化）。

守卫正则的唯一真源是 <root>/regex.txt：一行「检出正则」（禁用话术等 BAD 形态的
交替式，非 tempered 包裹——tempered 语义由本工具的预期核对承载）。manifest.txt
逐行登记被检文件与预期，行格式：

    match<TAB><相对 root 路径>      正则必须命中（坏例：含被禁话术）
    nomatch<TAB><相对 root 路径>    正则必须不命中（好例：干净文本/处置得当的回答）

路径先 os.path.normpath 再基于 root 拼接，允许 ../ 出 root 引用仓内真实文件
（如 ../expected-answers/ac8-banned-term-disposal.md——真答案由此持续受守卫）。
空行与 # 注释行跳过。预期不符=违规行；文件缺失=违规行；manifest 无任何条目=
违规（空套件不许亮绿灯，沿 fixture_run 同款纪律）。

用法: python3 tools/guard_corpus_check.py <root>
退出码（对齐仓内约定）: 0 全过；1 有违规；2 用法错误（缺参/root 不存在/
regex.txt 或 manifest.txt 缺失/regex.txt 非一行/正则编译失败/manifest 行格式非法）。
"""

import os
import re
import sys
from pathlib import Path

USAGE = "用法: python3 tools/guard_corpus_check.py <root>"


def fail2(msg: str) -> int:
    print(f"错误: {msg}", file=sys.stderr)
    return 2


def load_pattern(root: Path):
    """读 regex.txt（一行检出正则），返回 (编译后 pattern, 错误串)。"""
    rx = root / "regex.txt"
    if not rx.is_file():
        return None, "regex.txt 不存在"
    lines = rx.read_text(encoding="utf-8").rstrip("\n").split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    if len(lines) != 1:
        return None, f"regex.txt 须为一行正则，实得 {len(lines)} 行"
    try:
        return re.compile(lines[0]), None
    except re.error as exc:
        return None, f"正则编译失败: {exc}"


def load_manifest(root: Path):
    """读 manifest.txt，返回 (条目列表[(expect, relpath)], 错误串)。"""
    mf = root / "manifest.txt"
    if not mf.is_file():
        return None, "manifest.txt 不存在"
    entries = []
    for lineno, raw in enumerate(mf.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 2 or parts[0] not in ("match", "nomatch"):
            return None, f"manifest.txt 第 {lineno} 行格式非法（须 match|nomatch<TAB>路径）: {raw!r}"
        entries.append((parts[0], parts[1].strip()))
    return entries, None


def check(root: Path) -> tuple[int, list[str]]:
    """对 root 施例集回归，返回 (退出码, 报告行)。"""
    pattern, err = load_pattern(root)
    if err:
        return fail2(err), []
    entries, err = load_manifest(root)
    if err:
        return fail2(err), []
    report = [f"守卫正则: /{pattern.pattern}/"]
    if not entries:
        report.append("违规: manifest 为空（空套件不许亮绿灯）")
        report.append("例集回归: 1 项违规")
        return 1, report
    violations = 0
    for expect, relpath in entries:
        target = Path(os.path.normpath(root / relpath))
        if not target.is_file():
            violations += 1
            report.append(f"违规: 文件缺失 {relpath}（预期 {expect}）")
            continue
        hit = pattern.search(target.read_text(encoding="utf-8")) is not None
        ok = hit == (expect == "match")
        if ok:
            report.append(f"ok  {relpath}（{expect}）")
        else:
            violations += 1
            actual = "命中" if hit else "未命中"
            report.append(f"违规: {relpath} 预期 {expect}，实际 {actual}")
    tail = "例集回归: 全过" if violations == 0 else f"例集回归: {violations} 项违规"
    report.append(tail)
    return (0 if violations == 0 else 1), report


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print(USAGE, file=sys.stderr)
        return 2
    root = Path(argv[0])
    if not root.is_dir():
        return fail2(f"root 不是目录: {root}")
    code, report = check(root)
    for line in report:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
