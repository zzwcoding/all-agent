#!/usr/bin/env python3
"""skill_deps_check.py —— skill 边界闸（设计案 §3.1，票 01）。

扫每个 skill 的正文（SKILL.md + references/*.md）中的文件引用路径，
对照 specs/modules.md 里该 skill 卡的依赖行（skill:/script:/data:）与
reads/writes 声明面，以及「边界规则」表的第一条铁律：
**任何 skill 不许读另一 skill 的非公开文件（references 私件），无例外。**

判定规则（对每个反引号包裹的路径形态 token）：
  1. URL / 含空白的命令行 / 含 <> 的占位符 / 无法定位的散文碎片 → 跳过。
  2. 指向另一 skill 目录（skills 兄弟目录名开头）→ 只允许指向其 SKILL.md
     且该 skill 已在卡上声明依赖；指向私件（references 等）一律违规。
     声明为「外部」的 skill：不扫它的内部文件，但本 skill 正文引用其私件仍违规。
  3. `tools/` 开头 → 必须命中卡上 `script:` 依赖行；命中卡声明面
     （reads/writes/data 模式，指被治理项目的 tools/）亦可；
     存在于本仓 tools/ 却未在卡上登记 = 违规（脚本私拉）。
  4. 命中卡声明面（reads/writes/data 任一路径模式）→ 放行。
  5. 落在本 skill 自己目录内且文件存在 → 放行；文件不存在 = 悬空引用违规。
  6. 其余落在已知区域（卡声明面/兄弟 skill/本仓顶层目录的首段）但未声明 → 违规。

反向检查：卡上声明的 script 依赖必须有对应文件；声明的非外部 skill 依赖
必须能在 skills 目录找到；卡间 skill 依赖不许成环（设计案 §3.2）。

豁免：仓根 `.skill-deps-allow`，每行 `<路径模式>  # 理由`（理由必填），
匹配引用 token 即豁免——例外必须显式带理由（SKILL.md 原则 7）。

退出码：0 无违规；1 有违规；2 用法错误。--json 输出机读报告。

本仓实例化差异（All-agent 票 03，源自 sdd-flow2 票 01 原版）：
  a. 无 skill（仓根无 SKILL.md 且无 skills/）不判死——本仓 skill 随票 05 起落盘，
     此时只做卡↔脚本依赖核对；报告带 note 说明。
  b. 卡上声明的脚本若已登记 modules.md「脚本清单」但尚未落盘 = planned-script
     警告（不红），脚本随票分批落盘；未登记的缺失脚本仍 = missing-script 违规。
"""

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

# 已知文件扩展名：无斜杠但带扩展名的 token 也算路径引用（如 CONTEXT.md）
KNOWN_EXTS = (".md", ".py", ".json", ".sh", ".yml", ".yaml", ".html",
              ".png", ".svg", ".toml", ".cfg", ".txt")
# token 里出现即视为非路径（命令行/说明文字）
NOT_PATH_CHARS = re.compile(r"[\s（）《》「」\"']")

# 已知区域首段：token 首段落在此集合但未声明/不存在 = 违规；
# 不在此集合 = 散文碎片，跳过（闸只判能判的）。
WELL_KNOWN_AREAS = {
    "docs", "specs", "tickets", "tools", "fixtures", "lessons", "references",
    "src", "tests", "scripts", "evals", "ontology", "policies", "diagrams",
    "skills", ".github", ".scratch", "CONTEXT.md", "AGENTS.md", "README.md",
}
# 无歧义的本 skill 私域：被治理项目顶层没有 references/，出现即指自己
OWN_PRIVATE_AREAS = {"references", "SKILL.md"}
GLOB_CHARS = re.compile(r"[*?\[]")

CARD_SECTION_RE = re.compile(r"^## skill: (.+?)\s*$", re.MULTILINE)
DEP_LINE_RE = re.compile(r"^\s*- (skill|script|data): (.*)$")
READS_WRITES_RE = re.compile(r"^- (reads|writes): (.*)$")
BACKTICK_RE = re.compile(r"`([^`]+)`")


class Card:
    """一张 skill 卡的机器可读面。"""

    def __init__(self, name):
        self.name = name
        self.skill_deps = {}      # 名 -> 是否外部
        self.script_deps = []     # tools/ 路径
        self.data_patterns = []   # data: 声明
        self.declared_patterns = []  # reads/writes/data 全部路径模式

    def covers(self, token: str) -> bool:
        return any(fnmatch.fnmatch(token, p) for p in self.declared_patterns)


def _normalize_pattern(pat: str) -> str:
    pat = pat.strip().rstrip("。")
    if pat.endswith("/"):
        pat += "**"
    return pat


def parse_cards(modules_md: str) -> dict[str, Card]:
    """解析 specs/modules.md 的全部 skill 卡。"""
    cards = {}
    matches = list(CARD_SECTION_RE.finditer(modules_md))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(modules_md)
        body = modules_md[m.start():end]
        # 卡节在遇到下一个同级或更高级标题时结束（边界规则/规约清单等节不属卡）
        cut = re.search(r"^## (?!skill:)", body[len(m.group(0)):], re.MULTILINE)
        if cut:
            body = body[:len(m.group(0)) + cut.start()]
        card = Card(m.group(1))
        for line in body.splitlines():
            dm = DEP_LINE_RE.match(line)
            if dm:
                kind, rest = dm.groups()
                if kind == "skill":
                    name_m = re.search(r"`([^`]+)`", rest)
                    if name_m:
                        card.skill_deps[name_m.group(1)] = ("外部" in rest)
                elif kind == "script":
                    name_m = re.search(r"`([^`]+)`", rest)
                    if name_m:
                        card.script_deps.append(name_m.group(1))
                else:  # data
                    pats = BACKTICK_RE.findall(rest) or re.split(r"[、，,\s]+", rest)
                    card.data_patterns.extend(
                        _normalize_pattern(p) for p in pats if p.strip())
                continue
            rm = READS_WRITES_RE.match(line)
            if rm:
                card.declared_patterns.extend(
                    _normalize_pattern(p) for p in BACKTICK_RE.findall(rm.group(2)))
        card.declared_patterns.extend(card.data_patterns)
        cards[card.name] = card
    return cards


def looks_like_path(token: str) -> bool:
    if "<" in token or ">" in token:
        return False  # 占位符
    if token.startswith(("http://", "https://", "ftp://")):
        return False
    if NOT_PATH_CHARS.search(token):
        return False
    return "/" in token or token.endswith(KNOWN_EXTS)


def extract_path_tokens(text: str) -> list[str]:
    # 先去掉围栏代码块：里面是模板/示例（如交接包模板），不是本 skill 的引用面
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    tokens = []
    for raw in BACKTICK_RE.findall(text):
        token = raw.strip()
        if token.startswith("./"):
            token = token[2:]
        if token and looks_like_path(token):
            tokens.append(token)
    return tokens


def load_allowlist(path: Path) -> list[tuple[str, str]]:
    """读 .skill-deps-allow：每行 `模式  # 理由`，理由必填。"""
    entries = []
    if not path.is_file():
        return entries
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pattern, sep, reason = line.partition("#")
        if not sep or not reason.strip():
            raise ValueError(f"{path}:{lineno} 豁免条目缺理由（格式: 模式  # 理由）")
        entries.append((pattern.strip(), reason.strip()))
    return entries


def discover_skills(root: Path) -> dict[str, Path]:
    """单 skill 仓（仓根有 SKILL.md）或 skills/ 目录模式。"""
    if (root / "SKILL.md").is_file():
        return {root.name: root}
    skills_dir = root / "skills"
    if skills_dir.is_dir():
        return {d.name: d for d in sorted(skills_dir.iterdir())
                if d.is_dir() and (d / "SKILL.md").is_file()}
    return {}


def check_skill(skill_name: str, skill_root: Path, card: Card | None,
                sibling_skills: set[str], known_areas: set[str],
                allowlist: list[tuple[str, str]]) -> list[dict]:
    """扫一个 skill 的正文引用，返回违规列表。"""
    violations = []
    scan_files = []
    if (skill_root / "SKILL.md").is_file():
        scan_files.append(skill_root / "SKILL.md")
    refs = skill_root / "references"
    if refs.is_dir():
        scan_files.extend(sorted(refs.rglob("*.md")))

    if card is None:
        violations.append({
            "skill": skill_name, "file": "specs/modules.md", "token": skill_name,
            "kind": "no-card",
            "message": f"skill {skill_name} 在 specs/modules.md 没有卡（孤儿 skill）",
        })
        card = Card(skill_name)

    def exempt(token: str) -> bool:
        return any(fnmatch.fnmatch(token, pat) for pat, _ in allowlist)

    def add(f, token, kind, message):
        if not exempt(token):
            violations.append({"skill": skill_name, "file": str(f),
                               "token": token, "kind": kind, "message": message})

    for f in scan_files:
        for token in extract_path_tokens(f.read_text(encoding="utf-8")):
            first_seg = token.split("/", 1)[0]
            # 2. 跨 skill 引用
            if first_seg in sibling_skills and first_seg != skill_name:
                rest = token[len(first_seg):].lstrip("/")
                if rest == "SKILL.md" and first_seg in card.skill_deps:
                    continue  # 已声明 skill 的公开名片
                add(f, token, "cross-skill-private",
                    f"引用另一 skill「{first_seg}」的私件（边界规则：无例外；"
                    f"公开面只有 SKILL.md 且须在卡上声明依赖）")
                continue
            # 3. tools/ 引用
            if first_seg == "tools":
                if any(fnmatch.fnmatch(token, dep) for dep in card.script_deps):
                    continue  # 已声明的脚本依赖
                if (skill_root / token).exists():
                    add(f, token, "undeclared-script",
                        "本仓 tools/ 下的脚本未在卡的 script: 依赖行登记")
                    continue
                if card.covers(token):
                    continue  # 被治理项目的 tools/（卡声明面覆盖）
                add(f, token, "undeclared",
                    "tools/ 引用既非卡上 script 依赖，也不被 reads/writes/data 声明面覆盖")
                continue
            # 4. 本 skill 私域（references/、SKILL.md）：非 glob 且文件不存在 = 悬空引用
            if first_seg in OWN_PRIVATE_AREAS and not GLOB_CHARS.search(token):
                if (skill_root / token).exists():
                    continue
                add(f, token, "dangling", "本 skill 内的悬空引用（文件不存在）")
                continue
            # 5. 卡声明面覆盖（含 glob token：模式引用只做声明面核对）
            if card.covers(token):
                continue
            # 6. 本仓内确实存在的引用（自治理产物等）
            if (skill_root / token).exists():
                continue
            # 7. 已知区域内的未声明引用
            if first_seg in known_areas:
                add(f, token, "undeclared", "引用落在已知区域但未在卡上声明")
            # 首段不在已知区域 → 散文碎片，跳过
    return violations


def parse_planned_scripts(modules_md: str) -> set[str]:
    """解析 modules.md 的「脚本清单」节：登记过但尚未落盘的脚本 = 已规划（警告不红）。

    反引号包裹与表格裸写的 tools/*.py 都认（本仓脚本清单表格现状为裸写）。
    """
    m = re.search(r"^## 脚本清单.*$", modules_md, re.MULTILINE)
    if not m:
        return set()
    rest = modules_md[m.end():]
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    if nxt:
        rest = rest[:nxt.start()]
    tokens = set(BACKTICK_RE.findall(rest))
    tokens |= set(re.findall(r"\btools/[\w./-]+", rest))
    return {t for t in tokens if t.startswith("tools/")}


def check_declared_deps(cards: dict[str, Card], skills: dict[str, Path],
                        root: Path, planned: set[str]) -> tuple[list[dict], list[dict]]:
    """反向检查：声明的依赖必须真实存在；卡间依赖无环。

    返回 (violations, warnings)。脚本已登记「脚本清单」但未落盘 = 已规划（warning，
    本仓脚本随票分批落盘，如 graph_index.py 属票 04）；未登记 = missing-script 违规。
    """
    violations, warnings = [], []
    for card in cards.values():
        for script in card.script_deps:
            if not (root / script).is_file():
                if script in planned:
                    warnings.append({
                        "skill": card.name, "file": "specs/modules.md", "token": script,
                        "kind": "planned-script",
                        "message": f"卡上声明的 script 依赖 {script} 尚未落盘"
                                   f"（已登记脚本清单，属后续票）",
                    })
                else:
                    violations.append({
                        "skill": card.name, "file": "specs/modules.md", "token": script,
                        "kind": "missing-script",
                        "message": f"卡上声明的 script 依赖 {script} 在仓内不存在",
                    })
        for dep, is_external in card.skill_deps.items():
            if not is_external and dep not in skills and dep not in cards:
                violations.append({
                    "skill": card.name, "file": "specs/modules.md", "token": dep,
                    "kind": "missing-skill",
                    "message": f"卡上声明的非外部 skill 依赖 {dep} 找不到",
                })
    # 无环自查（仅卡间，沿 skill 依赖边 DFS）
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {name: WHITE for name in cards}

    def visit(name, stack):
        color[name] = GRAY
        for dep in cards[name].skill_deps:
            if dep not in cards:
                continue
            if color[dep] == GRAY:
                violations.append({
                    "skill": name, "file": "specs/modules.md",
                    "token": " -> ".join(stack + [dep]),
                    "kind": "dependency-cycle",
                    "message": f"skill 依赖成环: {' -> '.join(stack + [dep])}",
                })
            elif color[dep] == WHITE:
                visit(dep, stack + [dep])
        color[name] = BLACK

    for name in cards:
        if color[name] == WHITE:
            visit(name, [name])
    return violations, warnings


def run(root: Path, allow_path: Path | None = None) -> dict:
    root = root.resolve()
    report = {"status": "pass", "root": str(root), "skills": [],
              "violations": [], "warnings": []}
    modules_md = root / "specs" / "modules.md"
    if not modules_md.is_file():
        report["status"] = "fail"
        report["violations"].append({
            "skill": "-", "file": "specs/modules.md", "token": "-",
            "kind": "no-modules-md", "message": "缺 specs/modules.md（卡集合不存在）",
        })
        return report
    cards = parse_cards(modules_md.read_text(encoding="utf-8"))
    skills = discover_skills(root)
    if not skills:
        # 本仓实例化（All-agent）：skill 随票 05 起落盘，无 skill 不再判死，
        # 只做卡↔脚本依赖核对（docstring 判定规则 2–5 在 skills/ 出现后自动生效）。
        report["note"] = ("本仓尚无 skill（仓根无 SKILL.md 且无 skills/ 目录；"
                          "All-agent 票 05 起建）——本轮只核对卡↔脚本依赖一致性")
    if allow_path is None:
        allow_path = root / ".skill-deps-allow"
    allowlist = load_allowlist(allow_path)
    report["allowlist"] = [{"pattern": p, "reason": r} for p, r in allowlist]

    # 已知区域 = 内置区域表 ∪ 卡声明面首段 ∪ 兄弟 skill 名 ∪ 各 skill 仓顶层目录名
    sibling_names = set(skills)
    if len(skills) == 1 and next(iter(skills.values())) == root:
        # 单 skill 仓：兄弟 = 仓的父目录下其他 skill 目录
        parent = root.parent
        sibling_names |= {d.name for d in parent.iterdir()
                          if d.is_dir() and (d / "SKILL.md").is_file()}
    known_areas = set(WELL_KNOWN_AREAS) | set(sibling_names)
    for card in cards.values():
        known_areas.update(p.split("/", 1)[0] for p in card.declared_patterns)
    for skill_root in skills.values():
        if skill_root.is_dir():
            known_areas.update(p.name for p in skill_root.iterdir() if p.name != ".git")

    for name, skill_root in sorted(skills.items()):
        card = cards.get(name)
        report["skills"].append(name)
        report["violations"].extend(
            check_skill(name, skill_root, card, sibling_names, known_areas, allowlist))
    planned = parse_planned_scripts(modules_md.read_text(encoding="utf-8"))
    violations, warnings = check_declared_deps(cards, skills, root, planned)
    report["violations"].extend(violations)
    report["warnings"].extend(warnings)
    if report["violations"]:
        report["status"] = "fail"
    return report


def print_human(report: dict) -> None:
    if report.get("note"):
        print(f"注: {report['note']}")
    print(f"扫描 skill: {', '.join(report['skills']) or '（无）'}")
    if report.get("allowlist"):
        print(f"豁免清单 {len(report['allowlist'])} 条（.skill-deps-allow）")
    for w in report.get("warnings", []):
        print(f"[警告][{w['kind']}] {w['file']}: `{w['token']}` — {w['message']}")
    if not report["violations"]:
        print("边界闸: 无违规")
        return
    for v in report["violations"]:
        print(f"[{v['kind']}] {v['file']}: `{v['token']}` — {v['message']}")
    print(f"边界闸: {len(report['violations'])} 处违规")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="skill 边界闸（设计案 §3.1）")
    ap.add_argument("--root", default=None,
                    help="仓根（默认取本脚本的上级目录）")
    ap.add_argument("--allow", default=None,
                    help="豁免清单路径（默认 <仓根>/.skill-deps-allow）")
    ap.add_argument("--json", action="store_true", help="机读 JSON 输出（供 CI 消费）")
    args = ap.parse_args(argv)
    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    try:
        report = run(root, Path(args.allow) if args.allow else None)
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
