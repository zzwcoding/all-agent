#!/usr/bin/env python3
"""install_skills.py —— 安装位同步脚本（All-agent 票 12；票 15 增强钩子三件套）。

仓内 skills/ 正本 → ~/.agents/skills/ 安装位的同步与核查。双位置定例（lessons/05）：
仓内正本受四闸治理，安装位供 Kimi Code 路由，两份必须一致；「改正本后需重装」的
手工纪律由本脚本机械化——sync 负责装，--check 负责验；pre-commit 钩子
（tools/hooks/pre-commit，core.hooksPath 启用）每次提交前跑 --check 落闸（票 15）。

CLI:
  python3 tools/install_skills.py sync [skill名...]      同步（缺省全量；先清后拷）
  python3 tools/install_skills.py --check [skill名...]   核查（逐文件 diff + 孤儿扫描）
  python3 tools/install_skills.py --prune [--yes]        孤儿清理（默认 dry-run 列清单）
  skill 名可多选；--json 机读输出（pre-commit 钩子/CI 消费）。

路径解析（可注入）:
  正本根   = 环境变量 ALL_AGENT_SKILLS_SRC，缺省 <仓根>/skills/
  安装位根 = 环境变量 ALL_AGENT_SKILLS_HOME，缺省 $HOME/.agents/skills/
  注册表   = 环境变量 ALL_AGENT_INSTALL_REGISTRY，缺省 <仓根>/tools/install-registry.json
  单测用 tempfile + 环境变量注入，绝不读写真实 HOME 与真实 git config（票面红线）。

语义:
  漂移三型 = missing（正本有安装位无）/ modified（两边都有内容不同）/ extra（安装位多余）。
  sync 只重写有漂移的 skill（整目录先清后拷）；已一致的 skill 原样跳过——
  连跑两次第二次全跳过（幂等，文件 mtime 不变）。删除面只到 <安装位>/<skill名>/
  目录本身，绝不触碰安装位内兄弟 skill（用户另有数十个非本仓 skill）；skill 名
  含路径分隔符判用法错误，安装位根=正本根时拒跑（防先清后拷自删正本）。
  不进 ci.sh 四闸：安装位是仓外环境状态，CI 保持确定性（本仓 git 内容）。

注册表与孤儿（票 15）:
  注册表 tools/install-registry.json 记「本仓管理的 skill 名清单」，是 sync 的
  原子副产物（临时文件 + os.replace，拷贝全部完成后才写，半途失败不留脏表；
  内容不变不重写）。孤儿三要素 = 注册表登记过 + 安装位还在 + 仓内正本已删——
  安装位里没登记过的目录是用户自装的别人的 skill，绝不当孤儿（--check 不报、
  --prune 不删）。孤儿除名只有两条路：--prune --yes 删净残留；或安装位目录已
  自然消失（自然退役）。sync 不遗忘未清场孤儿——注册表收敛规则 =
  现清单 ∪ {登记过、正本已删、安装位仍存的退役候选}，防止「删正本+sync」把
  孤儿洗白。--prune 默认 dry-run 只列将删清单，--yes 才真删并同步注册表
  （破坏性操作加确认闸，与仓内「删除需理由」文化一致）。

symlink 设防（票 15）:
  正本或安装位任一侧的 skill 目录若为符号链接，sync/--check/--prune 一律报
  config-error（退出码 2）拒处理并列出路径——不做递归解析，防路径逃逸。

退出码：0 一致/同步成功/无孤儿；1 有漂移或孤儿（--check）；2 用法/配置错误
（含 symlink 命中、注册表损坏、--prune 误用、sync 半途失败）。
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


def registry_path() -> Path:
    """安装注册表：ALL_AGENT_INSTALL_REGISTRY 优先，缺省 <仓根>/tools/install-registry.json
    （与被治理脚本同域，票 15 裁决：扩布局表 tools patterns 收编 *.json）。"""
    injected = os.environ.get("ALL_AGENT_INSTALL_REGISTRY", "").strip()
    if injected:
        return Path(injected).resolve()
    return Path(__file__).resolve().parent / "install-registry.json"


# ---------- 注册表（sync 的原子副产物；孤儿检测依据，票 15） ----------


def load_registry(path: Path) -> list[str]:
    """读注册表 skill 名清单（排序定序）；文件不存在=空册（从未 sync 过），损坏=config-error。"""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise UsageError(f"安装注册表不是合法 JSON: {path}: {exc}")
    if (not isinstance(data, dict)
            or not isinstance(data.get("skills"), list)
            or not all(isinstance(n, str) for n in data["skills"])):
        raise UsageError(f"安装注册表结构非法（需顶层 skills 字符串数组）: {path}")
    return sorted(data["skills"])


def write_registry(path: Path, names: list[str]) -> bool:
    """原子写注册表（同目录临时文件 + os.replace）；内容不变则跳过。返回是否落盘。"""
    payload = {
        "version": 1,
        "description": "本仓管理的安装位 skill 名清单（tools/install_skills.py sync "
                       "原子维护；孤儿三要素=登记过+安装位在+正本已删，票 15）",
        "skills": sorted(names),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path.is_file():
        try:
            if path.read_text(encoding="utf-8") == text:
                return False
        except OSError:
            pass
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return True


def reconcile_registry(current: list[str], registered: list[str],
                       dst_root: Path) -> tuple[list[str], list[str]]:
    """sync 后注册表收敛规则：现清单 ∪ {登记过、正本已删、安装位仍存的退役候选}。

    除名只有两条路：--prune --yes 删净残留；或安装位目录已自然消失（自然退役）。
    返回 (新名单, 自然退役名单)。"""
    kept, retired = list(current), []
    for name in registered:
        if name in current:
            continue
        if (dst_root / name).is_dir():
            kept.append(name)
        else:
            retired.append(name)
    return sorted(set(kept)), sorted(retired)


def find_orphans(registered: list[str], current: list[str],
                 dst_root: Path) -> list[str]:
    """孤儿三要素：注册表登记过 + 安装位还在 + 仓内正本已删。

    安装位里没登记过的目录是用户自装的别人的 skill，绝不算孤儿。"""
    return sorted(name for name in registered
                  if name not in current and (dst_root / name).is_dir())


# ---------- symlink 设防（防路径逃逸，票 15） ----------


def assert_no_symlink_dirs(roots: list[Path], names: list[str]) -> None:
    """任一候选 skill 目录为符号链接即 config-error（不做递归解析，防路径逃逸）。"""
    hits = sorted(str(root / name) for root in roots for name in names
                  if (root / name).is_symlink())
    if hits:
        raise UsageError("skill 目录为符号链接，拒处理（防路径逃逸）: "
                         + " ".join(hits))


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
             json_out: bool, current: list[str], registered: list[str],
             reg_path: Path) -> int:
    if dst_root.resolve() == src_root.resolve():
        raise UsageError(f"安装位根与正本根相同（{src_root}），拒绝 sync——"
                         f"先清后拷会自删正本")
    # 注册表先算收敛名单（现清单 ∪ 未清场退役候选），等拷贝全部完成后才落盘——
    # 半途失败直接抛异常，注册表一字不动（原子副产物，票 15）。
    new_registry, retired = reconcile_registry(current, registered, dst_root)
    retained = sorted(set(new_registry) - set(current))
    report = {"mode": "sync", "src": str(src_root), "dst": str(dst_root),
              "skills": names, "actions": [], "post_diffs": [],
              "registry": {"skills": new_registry, "retained": retained,
                           "retired": retired, "changed": None}}
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
    if report["post_diffs"]:
        # 复检有漂移=脚本 bug，注册表也不写（保持「失败不留新状态」）
        if json_out:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            for d in report["post_diffs"]:
                print(f"{d['type']}\t{d['skill']}/{d['path']}")
            print(f"sync 后复检仍有 {len(report['post_diffs'])} 处漂移"
                  f"（不应发生，属脚本 bug，请回报）", file=sys.stderr)
        return 1
    report["registry"]["changed"] = write_registry(reg_path, new_registry)
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
        print(f"sync 完成: {len(names)} 个 skill（重写 {rewritten} / 跳过 {skipped}），"
              f"sync 后复检零漂移；注册表{'已更新' if report['registry']['changed'] else '未变'}"
              f"（{len(new_registry)} 项）")
        if retired:
            print(f"注册表自然除名 {len(retired)} 个（安装位已无残留）: "
                  f"{' '.join(retired)}")
        if retained:
            print(f"注册表保留退役候选 {len(retained)} 个"
                  f"（正本已删、安装位仍存）: {' '.join(retained)}\n"
                  f"  处置: python3 tools/install_skills.py --prune --yes"
                  f"（先 --prune 看清单）", file=sys.stderr)
    return 0


# ---------- --check（漂移即非零退出并列差异清单；孤儿同报，票 15） ----------


def run_check(src_root: Path, dst_root: Path, names: list[str],
              json_out: bool, current: list[str],
              registered: list[str]) -> int:
    orphans = find_orphans(registered, current, dst_root)
    report = {"mode": "check", "src": str(src_root), "dst": str(dst_root),
              "skills": names, "diffs": [], "consistent": [],
              "orphans": [{"skill": n, "path": str(dst_root / n)}
                          for n in orphans]}
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
        for o in report["orphans"]:
            print(f"orphan\t{o['skill']}\t{o['path']}")
        if report["diffs"]:
            counts = {t: sum(1 for d in report["diffs"] if d["type"] == t)
                      for t in ("missing", "modified", "extra")}
            print(f"漂移 {len(report['diffs'])} 处"
                  f"（missing {counts['missing']} / modified {counts['modified']}"
                  f" / extra {counts['extra']}），退出码 1")
        elif not report["orphans"]:
            print("零漂移。一致清单:")
            for name in report["consistent"]:
                total = len(list_files(src_root / name))
                print(f"  {name}: {total} 个文件一致")
        if report["orphans"]:
            print(f"孤儿 {len(report['orphans'])} 个（注册表登记过、仓内正本已删、"
                  f"安装位残留）——清理: python3 tools/install_skills.py --prune --yes"
                  f"（先 --prune 看清单）")
    return 1 if (report["diffs"] or report["orphans"]) else 0


# ---------- --prune（孤儿清除：默认 dry-run，--yes 才删，票 15） ----------


def run_prune(src_root: Path, dst_root: Path, json_out: bool, assume_yes: bool,
              current: list[str], registered: list[str],
              reg_path: Path) -> int:
    if dst_root.resolve() == src_root.resolve():
        raise UsageError(f"安装位根与正本根相同（{src_root}），拒绝 prune——"
                         f"删除面会落到正本")
    orphans = find_orphans(registered, current, dst_root)
    report = {"mode": "prune", "dst": str(dst_root),
              "orphans": [{"skill": n, "path": str(dst_root / n)}
                          for n in orphans],
              "dryRun": not assume_yes, "pruned": [], "registry": None}
    if not orphans:
        if json_out:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"孤儿清理 install_skills --prune — 安装位 {dst_root}")
            print("无孤儿（注册表登记过的 skill 都有正本或已清场）")
        return 0
    if not assume_yes:
        if json_out:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"孤儿清理 install_skills --prune（dry-run，未动任何文件）— "
                  f"安装位 {dst_root}")
            for o in report["orphans"]:
                print(f"将删\t{o['skill']}\t{o['path']}")
            print(f"共 {len(orphans)} 个孤儿目录。确认删除请加 --yes: "
                  f"python3 tools/install_skills.py --prune --yes")
        return 0
    for name in orphans:
        target = dst_root / name
        # symlink 闸已在入口拦过；此处防御性再查，删除面绝不碰软链
        if target.is_symlink() or not target.is_dir():
            raise UsageError(f"孤儿目录形态异常，拒删: {target}")
    for name in orphans:
        shutil.rmtree(dst_root / name)
        report["pruned"].append(name)
    # 删净后重算收敛：被 prune 的名字安装位已无目录 → 自然退役除名
    new_registry, retired = reconcile_registry(current, registered, dst_root)
    write_registry(reg_path, new_registry)
    report["registry"] = {"skills": new_registry, "removed": sorted(orphans),
                          "retired": retired}
    if json_out:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"孤儿清理 install_skills --prune --yes — 安装位 {dst_root}")
        for name in orphans:
            print(f"已删\t{name}\t{dst_root / name}")
        print(f"清除 {len(orphans)} 个孤儿目录；注册表已同步"
              f"（余 {len(report['registry']['skills'])} 项）")
    return 0


# ---------- CLI ----------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="install_skills",
        description="安装位同步脚本（票 12/15）：仓内 skills/ 正本 ↔ ~/.agents/skills/ "
                    "安装位的同步与核查（sync 装、--check 验、--prune 清孤儿；漂移三型 "
                    "missing/modified/extra + 孤儿检测 + symlink 设防）")
    # 单位置参数手工分词：argparse 的「可选位置+choices」会把 --check 后的 skill 名
    # 错喂给命令槽触发 SystemExit，故 sync/skill 名统一收进 words 再解释。
    ap.add_argument("words", nargs="*", metavar="sync | skill名...",
                    help="子命令 sync（其后可跟 skill 名，缺省全量）；"
                         "--check 模式下位置参数全部按 skill 名解释；"
                         "--prune 不接 skill 名（孤儿按注册表全量认定）")
    ap.add_argument("--check", action="store_true",
                    help="核查模式：逐文件 diff + 孤儿扫描，漂移/孤儿即退出码 1")
    ap.add_argument("--prune", action="store_true",
                    help="孤儿清理：删「登记过+安装位在+正本已删」的目录；"
                         "默认 dry-run 只列清单，与 --yes 连用才真删")
    ap.add_argument("--yes", dest="assume_yes", action="store_true",
                    help="与 --prune 连用：确认执行删除（破坏性操作确认闸）")
    ap.add_argument("--json", dest="json_out", action="store_true",
                    help="机读 JSON 输出（供 CI/pre-commit 钩子消费）")
    args = ap.parse_args(argv)

    words = list(args.words)
    if args.prune:
        if args.check or (words and words[0] == "sync"):
            print("用法错误: --prune 与 sync/--check 互斥，一次只用一个",
                  file=sys.stderr)
            return 2
        if words:
            print("用法错误: --prune 不接 skill 名清单（孤儿按注册表全量认定）",
                  file=sys.stderr)
            return 2
        mode = "prune"
    else:
        if args.assume_yes:
            print("用法错误: --yes 只与 --prune 连用", file=sys.stderr)
            return 2
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
        reg_path = registry_path()
        current = discover_skills(src_root)
        registered = load_registry(reg_path)
        # symlink 闸：正本/安装位两侧、现清单 ∪ 注册表在册名，任一命中即拒处理
        assert_no_symlink_dirs([src_root, dst_root],
                               sorted(set(current) | set(registered)))
        if mode == "check":
            names = select_skills(names, current)
            return run_check(src_root, dst_root, names, args.json_out,
                             current, registered)
        if mode == "prune":
            return run_prune(src_root, dst_root, args.json_out,
                             args.assume_yes, current, registered, reg_path)
        names = select_skills(names, current)
        return run_sync(src_root, dst_root, names, args.json_out,
                        current, registered, reg_path)
    except UsageError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        # 拷贝/写表半途失败（磁盘、权限等）：注册表未写，不留脏表（票 15）
        print(f"配置错误: 安装位操作失败（未落任何新状态）: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
