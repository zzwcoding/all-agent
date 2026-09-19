#!/usr/bin/env python3
"""install_skills.py —— 安装位同步脚本（All-agent 票 12；AC 真源=tickets/12 AC 表）。

仓内 skills/ 正本 → ~/.agents/skills/ 安装位的同步与核查。双位置定例（lessons/05）：
仓内正本受四闸治理，安装位供 Kimi Code 路由，两份必须一致；「改正本后需重装」的
手工纪律由本脚本机械化——sync 负责装，--check 负责验。

CLI:
  python3 tools/install_skills.py sync [skill名...]      同步（缺省全量；先清后拷）
  python3 tools/install_skills.py --check [skill名...]   核查（逐文件 diff，漂移即非零退出）
  skill 名可多选；--json 机读输出（供未来 pre-commit 钩子/CI 消费）。

路径解析（可注入）:
  正本根   = 环境变量 ALL_AGENT_SKILLS_SRC，缺省 <仓根>/skills/
  安装位根 = 环境变量 ALL_AGENT_SKILLS_HOME，缺省 $HOME/.agents/skills/
  单测用 tempfile + 环境变量注入，绝不读写真实 HOME（票面红线）。

语义:
  漂移三型 = missing（正本有安装位无）/ modified（两边都有内容不同）/ extra（安装位多余）。
  sync 只重写有漂移的 skill（整目录先清后拷）；已一致的 skill 原样跳过——
  连跑两次第二次全跳过（幂等，文件 mtime 不变）。删除面只到 <安装位>/<skill名>/
  目录本身，绝不触碰安装位内兄弟 skill（用户另有数十个非本仓 skill）；skill 名
  含路径分隔符判用法错误，安装位根=正本根时拒跑（防先清后拷自删正本）。
  不进 ci.sh 四闸：安装位是仓外环境状态，CI 保持确定性（本仓 git 内容）。

退出码：0 一致/同步成功；1 有漂移（--check）/ sync 后复检仍漂移；2 用法/配置错误。
依赖：Python3 stdlib。
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


class UsageError(ValueError):
    """用法/配置错误（退出码 2）。"""


# ---------- 路径解析（环境变量可注入；单测强制走注入路径） ----------


def repo_skills_root() -> Path:
    """正本根：ALL_AGENT_SKILLS_SRC 优先，缺省 <仓根>/skills/（本脚本上级的上级）。"""
    injected = os.environ.get("ALL_AGENT_SKILLS_SRC", "").strip()
    if injected:
        return Path(injected).resolve()
    return (Path(__file__).resolve().parent.parent / "skills").resolve()


def install_skills_root() -> Path:
    """安装位根：ALL_AGENT_SKILLS_HOME 优先，缺省 $HOME/.agents/skills/。"""
    injected = os.environ.get("ALL_AGENT_SKILLS_HOME", "").strip()
    if injected:
        return Path(injected).resolve()
    home = os.environ.get("HOME", "").strip()
    if not home:
        raise UsageError("无法解析安装位根：HOME 未设置且未注入 ALL_AGENT_SKILLS_HOME")
    return (Path(home) / ".agents" / "skills").resolve()


# ---------- skill 名与清单 ----------


def validate_skill_name(name: str) -> str:
    """skill 名不得含路径分隔符（防先清后拷的删除面逃逸出安装位）。"""
    separators = {os.sep, "/", "\\", *([os.altsep] if os.altsep else [])}
    if not name or name in (".", "..") or any(sep in name for sep in separators):
        raise UsageError(f"非法 skill 名: {name!r}（不得为空、.、.. 或含路径分隔符）")
    return name


def discover_skills(src_root: Path) -> list[str]:
    """正本根下全部 skill 名（子目录名，排序定序）；根缺失/为空=配置错误。"""
    if not src_root.is_dir():
        raise UsageError(f"正本根不存在: {src_root}")
    names = sorted(p.name for p in src_root.iterdir() if p.is_dir())
    if not names:
        raise UsageError(f"正本根下没有任何 skill 目录: {src_root}")
    return names


def select_skills(requested: list[str], available: list[str]) -> list[str]:
    """argv 选中的 skill 名（缺省全量）；未知名明确报错并列可用清单，不猜。"""
    if not requested:
        return list(available)
    out = []
    for name in requested:
        validate_skill_name(name)
        if name not in available:
            raise UsageError(
                f"未知 skill: {name}（正本根下可用: {' '.join(available)}）")
        out.append(name)
    return out


# ---------- 逐文件 diff（漂移三型） ----------


def list_files(root: Path) -> dict[str, Path]:
    """目录内全部文件的 {相对路径(posix): 绝对路径}；根不存在=空集（全 missing）。"""
    if not root.is_dir():
        return {}
    return {p.relative_to(root).as_posix(): p
            for p in sorted(root.rglob("*")) if p.is_file()}


def same_file(a: Path, b: Path) -> bool:
    """字节级内容对照（不引 filecmp 缓存，保证确定性）。"""
    if a.stat().st_size != b.stat().st_size:
        return False
    return a.read_bytes() == b.read_bytes()


def diff_skill(src: Path, dst: Path) -> list[dict]:
    """单 skill 逐文件 diff：[{path, type}]，type ∈ missing/modified/extra。

    missing=正本有安装位无；modified=两边都有内容不同；extra=安装位多余。
    """
    src_files = list_files(src)
    dst_files = list_files(dst)
    diffs = []
    for rel in sorted(set(src_files) | set(dst_files)):
        if rel not in dst_files:
            diffs.append({"path": rel, "type": "missing"})
        elif rel not in src_files:
            diffs.append({"path": rel, "type": "extra"})
        elif not same_file(src_files[rel], dst_files[rel]):
            diffs.append({"path": rel, "type": "modified"})
    return diffs


# ---------- sync（先清后拷，删除面只到本 skill 目录） ----------


def sync_one(src: Path, dst: Path) -> None:
    """整目录先清后拷。前置：validate_skill_name 已过，dst.parent==安装位根。"""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def run_sync(src_root: Path, dst_root: Path, names: list[str],
             json_out: bool) -> int:
    if dst_root.resolve() == src_root.resolve():
        raise UsageError(f"安装位根与正本根相同（{src_root}），拒绝 sync——"
                         f"先清后拷会自删正本")
    report = {"mode": "sync", "src": str(src_root), "dst": str(dst_root),
              "skills": names, "actions": [], "post_diffs": []}
    for name in names:
        src, dst = src_root / name, dst_root / name
        diffs = diff_skill(src, dst)
        if not diffs:
            total = len(list_files(src))
            report["actions"].append({"skill": name, "action": "skip",
                                      "files": total})
            continue
        sync_one(src, dst)
        remaining = diff_skill(src, dst)
        report["actions"].append({
            "skill": name, "action": "rewrite",
            "cleared": {t: sum(1 for d in diffs if d["type"] == t)
                        for t in ("missing", "modified", "extra")},
            "files": len(list_files(src))})
        for d in remaining:
            report["post_diffs"].append({"skill": name, "path": d["path"],
                                         "type": d["type"]})
    if json_out:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"安装位同步 install_skills sync — 正本 {src_root} → 安装位 {dst_root}")
        for act in report["actions"]:
            if act["action"] == "skip":
                print(f"skip\t{act['skill']}（已一致，{act['files']} 个文件未动）")
            else:
                c = act["cleared"]
                print(f"rewrite\t{act['skill']}（先清后拷 {act['files']} 个文件；"
                      f"清账 missing {c['missing']} / modified {c['modified']}"
                      f" / extra {c['extra']}）")
        rewritten = sum(1 for a in report["actions"] if a["action"] == "rewrite")
        skipped = len(report["actions"]) - rewritten
        if report["post_diffs"]:
            for d in report["post_diffs"]:
                print(f"{d['type']}\t{d['skill']}/{d['path']}")
            print(f"sync 后复检仍有 {len(report['post_diffs'])} 处漂移"
                  f"（不应发生，属脚本 bug，请回报）", file=sys.stderr)
            return 1
        print(f"sync 完成: {len(names)} 个 skill（重写 {rewritten} / 跳过 {skipped}），"
              f"sync 后复检零漂移")
    return 0


# ---------- --check（漂移即非零退出并列差异清单） ----------


def run_check(src_root: Path, dst_root: Path, names: list[str],
              json_out: bool) -> int:
    report = {"mode": "check", "src": str(src_root), "dst": str(dst_root),
              "skills": names, "diffs": [], "consistent": []}
    for name in names:
        diffs = diff_skill(src_root / name, dst_root / name)
        if diffs:
            for d in diffs:
                report["diffs"].append({"skill": name, "path": d["path"],
                                        "type": d["type"]})
        else:
            report["consistent"].append(name)
    if json_out:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"安装位检查 install_skills --check — 正本 {src_root} ↔ 安装位 {dst_root}")
        for d in report["diffs"]:
            print(f"{d['type']}\t{d['skill']}/{d['path']}")
        if report["diffs"]:
            counts = {t: sum(1 for d in report["diffs"] if d["type"] == t)
                      for t in ("missing", "modified", "extra")}
            print(f"漂移 {len(report['diffs'])} 处"
                  f"（missing {counts['missing']} / modified {counts['modified']}"
                  f" / extra {counts['extra']}），退出码 1")
        else:
            print("零漂移。一致清单:")
            for name in report["consistent"]:
                total = len(list_files(src_root / name))
                print(f"  {name}: {total} 个文件一致")
    return 1 if report["diffs"] else 0


# ---------- CLI ----------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="install_skills",
        description="安装位同步脚本（票 12）：仓内 skills/ 正本 ↔ ~/.agents/skills/ "
                    "安装位的同步与核查（sync 装、--check 验；漂移三型 "
                    "missing/modified/extra）")
    # 单位置参数手工分词：argparse 的「可选位置+choices」会把 --check 后的 skill 名
    # 错喂给命令槽触发 SystemExit，故 sync/skill 名统一收进 words 再解释。
    ap.add_argument("words", nargs="*", metavar="sync | skill名...",
                    help="子命令 sync（其后可跟 skill 名，缺省全量）；"
                         "--check 模式下位置参数全部按 skill 名解释")
    ap.add_argument("--check", action="store_true",
                    help="核查模式：逐文件 diff，漂移即退出码 1 并列差异清单")
    ap.add_argument("--json", dest="json_out", action="store_true",
                    help="机读 JSON 输出（供 CI/pre-commit 钩子消费）")
    args = ap.parse_args(argv)

    words = list(args.words)
    if args.check:
        if words and words[0] == "sync":
            print("用法错误: sync 与 --check 互斥，一次只用一个", file=sys.stderr)
            return 2
        mode, names = "check", words
    else:
        if not words:
            print("用法错误: 需要子命令 sync 或 --check（--help 看用法）",
                  file=sys.stderr)
            return 2
        if words[0] != "sync":
            print(f"用法错误: 未知子命令: {words[0]}（应为 sync，"
                  f"或用 --check 核查）", file=sys.stderr)
            return 2
        mode, names = "sync", words[1:]

    try:
        src_root = repo_skills_root()
        dst_root = install_skills_root()
        names = select_skills(names, discover_skills(src_root))
        if mode == "check":
            return run_check(src_root, dst_root, names, args.json_out)
        return run_sync(src_root, dst_root, names, args.json_out)
    except UsageError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
