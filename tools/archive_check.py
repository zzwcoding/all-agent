#!/usr/bin/env python3
"""archive_check.py —— 归档闸（设计案「两条验收主线」主线 2，票 01）。

仓内每个受管文件必须对得上两份登记表：
  1. references/repo-layout.json（机读布局表）：落在已登记目录 + 命名/类型符合允许模式；
  2. specs/archive-registry.json（归档登记表）：命中产物类的文件过必备字段与状态合法值检查。

对不上 = 孤儿文件 / 非法目录 / 必备字段缺失 / 状态值非法 → CI 红。

受管文件集合：git 仓内 = `git ls-files --cached --others --exclude-standard`
（即"会被提交的全集"，gitignore 排除的不查）；非 git 仓 = 全量走目录
（排除 .git、__pycache__、.DS_Store）。

白名单：仓根 `.archive-allow`，每行 `<路径模式>  # 理由`（fnmatch glob，
理由必填）——项目特有产物登记例外，每轮体检复核可收回性。

profile：布局表按仓型分档（skill-repo / governed-project），默认自动判定
（仓根有 SKILL.md = skill-repo）。--json 输出机读报告。
退出码：0 全合规；1 有违规；2 配置/用法错误。
"""

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__"}
EXCLUDE_FILES = {".DS_Store"}
STATUS_LINE = "{field}:\\s*(\\S+)"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"{path} 不是合法 JSON: {exc}")


def collect_files(root: Path) -> list[str]:
    """受管文件全集（仓根相对 posix 路径）。"""
    if (root / ".git").exists():
        try:
            out = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z",
                 "--cached", "--others", "--exclude-standard"],
                check=True, capture_output=True).stdout
            return sorted(p for p in out.decode("utf-8").split("\0") if p)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # 回退到目录走查
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if p.name in EXCLUDE_FILES:
            continue
        files.append(rel.as_posix())
    return files


def load_allowlist(path: Path) -> list[tuple[str, str]]:
    """读 .archive-allow：每行 `模式  # 理由`，理由必填。"""
    entries = []
    if not path.is_file():
        return entries
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pattern, sep, reason = line.partition("#")
        if not sep or not reason.strip():
            raise ValueError(f"{path}:{lineno} 白名单条目缺理由（格式: 模式  # 理由）")
        entries.append((pattern.strip(), reason.strip()))
    return entries


def check_layout(files: list[str], dirs: list[dict],
                 allowlist: list[tuple[str, str]]) -> tuple[list[dict], list[str]]:
    """布局表核对：未登记目录 / 不符允许模式 / 命名违规。返回 (违规, 豁免文件)。"""
    violations, exempted = [], []
    by_path = {d["path"]: d for d in dirs}

    def is_exempt(rel: str) -> bool:
        return any(fnmatch.fnmatch(rel, pat) for pat, _ in allowlist)

    for rel in files:
        if is_exempt(rel):
            exempted.append(rel)
            continue
        top, _, rest = rel.partition("/")
        entry = by_path.get(top if rest else "")
        if entry is None:
            violations.append({
                "file": rel, "artifact": None, "kind": "unregistered-dir",
                "message": f"落在未登记目录「{top if rest else '(仓根)'}」（布局表无此条目）",
            })
            continue
        target = rest or top  # 目录内相对路径；仓根文件即 basename
        if not any(fnmatch.fnmatch(target, pat) for pat in entry.get("patterns", [])):
            violations.append({
                "file": rel, "artifact": None, "kind": "pattern-mismatch",
                "message": f"不符目录「{entry['path'] or '(仓根)'}」允许的文件模式 {entry.get('patterns')}",
            })
            continue
        name_re = entry.get("nameRegex")
        if name_re and not re.match(name_re, target):
            violations.append({
                "file": rel, "artifact": None, "kind": "name-mismatch",
                "message": f"命名不符目录「{entry['path']}」的命名纪律 /{name_re}/",
            })
    return violations, exempted


def check_skill_card(path: Path, artifact: dict) -> list[dict]:
    """specs/modules.md 里每个 `## skill:` 卡节必须含全部必备字段行。"""
    text = path.read_text(encoding="utf-8")
    sections = list(re.finditer(r"^## skill: (.+?)\s*$", text, re.MULTILINE))
    violations = []
    if not sections:
        return [{"file": str(path), "artifact": "skill-card", "kind": "missing-field",
                 "message": "modules.md 内没有任何 `## skill:` 卡节"}]
    for i, m in enumerate(sections):
        end = sections[i + 1].start() if i + 1 < len(sections) else len(text)
        body = text[m.start():end]
        for field in artifact.get("requiredFields", []):
            if not re.search(rf"^- {re.escape(field)}:", body, re.MULTILINE):
                violations.append({
                    "file": str(path), "artifact": "skill-card",
                    "kind": "missing-field",
                    "message": f"卡「{m.group(1)}」缺必备字段行 `- {field}:`",
                })
    return violations


def check_json_artifact(path: Path, artifact: dict) -> list[dict]:
    try:
        data = load_json(path)
    except ValueError as exc:
        return [{"file": str(path), "artifact": artifact["type"],
                 "kind": "missing-field", "message": str(exc)}]
    violations = []
    for field in artifact.get("requiredFields", []):
        if field not in data:
            violations.append({
                "file": str(path), "artifact": artifact["type"],
                "kind": "missing-field", "message": f"缺必备字段 `{field}`",
            })
    if artifact["type"] == "fixture":
        assertions = data.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            violations.append({
                "file": str(path), "artifact": "fixture", "kind": "missing-field",
                "message": "assertions 为空（空断言集不许登记，与 fixture_run 双门槛一致）",
            })
    return violations


def check_md_artifact(path: Path, artifact: dict) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # 非 UTF-8 文本（图表交付物 png 等）：无字段/状态要求的产物类直接放行；
        # 有要求的（本该是 md/json）报缺字段——二进制满足不了文本字段契约。
        if artifact.get("requiredFields") or artifact.get("status"):
            return [{"file": str(path), "artifact": artifact["type"],
                     "kind": "missing-field",
                     "message": "非 UTF-8 文本文件，无法满足该产物类的字段/状态检查"}]
        return []
    violations = []
    for field in artifact.get("requiredFields", []):
        if field not in text:
            violations.append({
                "file": str(path), "artifact": artifact["type"],
                "kind": "missing-field", "message": f"缺必备字段/节「{field}」",
            })
    status = artifact.get("status")
    if status:
        m = re.search(STATUS_LINE.format(field=re.escape(status["field"])),
                      text, re.MULTILINE)
        if not m:
            violations.append({
                "file": str(path), "artifact": artifact["type"],
                "kind": "missing-field",
                "message": f"缺状态行 `{status['field']}: <值>`",
            })
        elif m.group(1) not in status["values"]:
            violations.append({
                "file": str(path), "artifact": artifact["type"],
                "kind": "bad-status",
                "message": f"状态值「{m.group(1)}」非法（合法: {'/'.join(status['values'])}）",
            })
    return violations


def check_registry(files: list[str], root: Path, artifacts: list[dict]) -> list[dict]:
    violations = []
    for rel in files:
        for artifact in artifacts:
            if not any(fnmatch.fnmatch(rel, pat)
                       for pat in artifact.get("pathPatterns", [])):
                continue
            path = root / rel
            atype = artifact["type"]
            if atype == "skill-card":
                violations.extend(check_skill_card(path, artifact))
            elif rel.endswith(".json"):
                violations.extend(check_json_artifact(path, artifact))
            else:
                violations.extend(check_md_artifact(path, artifact))
    return violations


def warn_untracked(root: Path) -> "list[str]":
    """未跟踪文件清单（票 77，只警不拦）：git status --porcelain 的 ?? 项。
    git 缺席/非 git 仓/超时一律静默返回空表——警告不得反过来卡 CI。"""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false",
             "status", "--porcelain"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0:
        return []
    return [line[3:] for line in proc.stdout.splitlines()
            if line.startswith("?? ")]


def run(root: Path, profile: str | None = None,
        layout_path: Path | None = None, registry_path: Path | None = None,
        allow_path: Path | None = None) -> dict:
    root = root.resolve()
    layout_path = layout_path or root / "references" / "repo-layout.json"
    registry_path = registry_path or root / "specs" / "archive-registry.json"
    allow_path = allow_path or root / ".archive-allow"
    layout = load_json(layout_path)
    registry = load_json(registry_path)
    if profile is None:
        profile = "skill-repo" if (root / "SKILL.md").is_file() else "governed-project"
    if profile not in layout["profiles"]:
        raise ValueError(f"布局表无 profile「{profile}」（可选: {list(layout['profiles'])}）")
    dirs = layout["profiles"][profile]["dirs"]
    allowlist = load_allowlist(allow_path)

    files = collect_files(root)
    violations, exempted = check_layout(files, dirs, allowlist)
    violations.extend(
        check_registry([f for f in files if f not in exempted], root,
                       registry.get("artifacts", [])))
    return {
        "status": "fail" if violations else "pass",
        "profile": profile,
        "filesChecked": len(files),
        "untracked": warn_untracked(root),
        "exempted": [{"path": f,
                      "reason": next((r for p, r in allowlist
                                      if fnmatch.fnmatch(f, p)), "")}
                     for f in exempted],
        "violations": violations,
    }


def print_human(report: dict) -> None:
    print(f"profile={report['profile']} 受管文件 {report['filesChecked']} 个")
    for e in report["exempted"]:
        print(f"[豁免] {e['path']} — {e['reason']}")
    for f in report.get("untracked", []):
        print(f"[⚠ 未跟踪] {f} —— 提交前 git add（防文件只落盘不入账，"
              f"lessons/0019 误删实证，票 77；不影响本闸退出码）")
    if not report["violations"]:
        print("归档闸: 全部文件对得上布局表+登记表")
        return
    for v in report["violations"]:
        print(f"[{v['kind']}] {v['file']} — {v['message']}")
    print(f"归档闸: {len(report['violations'])} 处违规")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="归档闸（布局表+登记表核对）")
    ap.add_argument("--root", default=None, help="仓根（默认取本脚本的上级目录）")
    ap.add_argument("--profile", default=None,
                    choices=["skill-repo", "governed-project"],
                    help="布局表档位（默认按仓根有无 SKILL.md 自动判定）")
    ap.add_argument("--layout", default=None, help="布局表路径（默认 references/repo-layout.json）")
    ap.add_argument("--registry", default=None, help="登记表路径（默认 specs/archive-registry.json）")
    ap.add_argument("--allow", default=None, help="白名单路径（默认 <仓根>/.archive-allow）")
    ap.add_argument("--json", action="store_true", help="机读 JSON 输出（供 CI 消费）")
    args = ap.parse_args(argv)
    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    try:
        report = run(root, profile=args.profile,
                     layout_path=Path(args.layout) if args.layout else None,
                     registry_path=Path(args.registry) if args.registry else None,
                     allow_path=Path(args.allow) if args.allow else None)
    except ValueError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
