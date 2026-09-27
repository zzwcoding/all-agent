#!/usr/bin/env python3
"""review_gate.py —— 人审闸审记状态机（票 45；docs/design-human-review-gate.md
§2.3 审记旁档+哈希锚定 / §3.4 边界情形 / §8 Owner 七点裁决）。

生成物本体一字不动（design §5 不做 5：三生成物 status 行字面、归档闸既有契约、
--check 防陈旧全零改动）；人审结论落**审记旁档** JSON（默认 exports/reviews/
<目标去扩展>-review.json，--review-dir 可注入），逐版本**追加不覆盖**。每条审记
锚定「被审版本的内容哈希 + commit」——本体再生即哈希变，已审结论**自动失效回落
待人审**（零宽限，裁决点 5）；复用 --check 的逐字节比对哲学：--check 判
「入库=可再生」，哈希锚定判「已审=就是这一版」。

威胁模型（措辞收敛，票 48 P3）：本闸防遗忘/防错版本（design §3.4 自我限定），
非防恶意篡改——防伪面=哈希锚定提供篡改*检测*非*防御*（再生漂移可检出、已审
失效回落，但不抵抗蓄意改写审记重放；防伪造的边界=拒绝重建审记，见 §3.4 #2）。

四动作 CLI：
  init <target>    建审记旁档骨架 {"target","created","records":[]}；已存在则
                   提示不重建（追加不覆盖；骨架损坏时拒绝重建退出 1，design
                   §3.4 #2：审记可以缺，不可以编）。
  approve <target> [--checkpoints "…"] [--notes "…"]
                   追加一条 verdict=已审 审记：{target, reviewedCommit(git HEAD),
                   reviewedSha256(现算 SHA256), verdict, checkpoints[], notes,
                   reviewedBy, date}。reviewedBy/reviewedCommit 取 git 身份
                   （裁决点③随票定：git config user.name / rev-parse HEAD，
                   以目标所在目录向上找仓）；取不到写 "unknown" 并 stderr 提示
                   （git 缺席降级，sha256 锚定不受影响）。审记缺席时自动落头
                   （首条记录即历史起点，不伪造任何裁决）；既有审记损坏/非法
                   则拒绝追加（不重建防伪造历史）。
  reject <target> --routing "…" [--checkpoints] [--notes] [--review-dir]
                   追加 verdict=打回 审记，routing 强制（缺失/空白 = exit 2）——
                   打回必须当场开单：业务错道→提案池 / 工程错道→tickets/NN
                   （裁决点 6，不允许只记审记意见悬着）。
  verify <target> [--json]
                   现算目标 sha256 与最新裁决比对。判定树（AC 真源=票 45 AC 表）：
                     目标不存在                        → 2 配置错
                     审记文件不存在                    → 1 缺失=待人审（不重建）
                     审记不可解析/头部结构坏           → 1 损坏=待人审（不重建）
                     审记无任何记录                    → 1 待人审
                     记录缺必备字段/verdict 非法值     → 2 审记非法（配置错，
                                                         AC2a/AC2b；追加与核对
                                                         同此判，防脏记录混入）
                     最新裁决=打回                     → 1 未通过（附 routing）
                     已审且哈希一致                    → 0
                     已审但哈希不一致（再生过）        → 1 失效回落待人审
                   审记损坏分两档（specs/review_gate.md 退出码表）：不可解析=
                   待人审（exit 1，宁多审一次）；可解析但违约（缺字段/非法值）=
                   配置错（exit 2，fail loud）。verify 只读，任何红都不重建审记。

退出码：0 一致（已审且哈希匹配）；1 失效/缺失/损坏/打回态；2 配置错（目标不
存在、reject 缺 routing、审记记录缺字段或 verdict 非法值、用法错误）。
错误与降级提示走 stderr，结论走 stdout（--json 时 stdout 只有机读 JSON）。

依赖：Python3 stdlib（hashlib/subprocess……纯标准库零外部依赖）。
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

TICKET = "45"
REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEW_FILENAME_SUFFIX = "-review.json"
DEFAULT_REVIEW_DIR = REPO_ROOT / "exports" / "reviews"   # 裁决点 4 审记落点

VERDICT_APPROVED = "已审"
VERDICT_REJECTED = "打回"
LEGAL_VERDICTS = (VERDICT_APPROVED, VERDICT_REJECTED)

# 审记记录必备字段（specs/review_gate.md 字段表镜像；routing 按 verdict 条件必备）
RECORD_BASE_FIELDS = ("target", "reviewedCommit", "reviewedSha256", "verdict",
                      "checkpoints", "notes", "reviewedBy", "date")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

EXIT_OK, EXIT_RED, EXIT_CONFIG = 0, 1, 2


class ConfigError(Exception):
    """配置错（exit 2）：目标不存在 / reject 缺 routing / 审记记录违约。"""


# ---------- 基础件 ----------

def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(args: list, cwd: Path) -> "tuple[bool, str]":
    """跑一条只读 git 命令，返回 (成功, stdout 去尾空白)。git 缺席/非仓 = (False, "")。"""
    try:
        proc = subprocess.run(["git", "-C", str(cwd)] + args,
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return proc.returncode == 0, (proc.stdout or "").strip()


def git_anchor(target: Path) -> "tuple[str, str, list[str]]":
    """取 (reviewedCommit, reviewedBy, 降级提示)。以目标所在目录向上找仓。

    git 缺席/非仓/无身份 → "unknown" + stderr 提示（单测钉死降级路径）。
    """
    cwd = target.resolve().parent
    notices = []
    ok, commit = _git(["rev-parse", "HEAD"], cwd)
    if not ok:
        commit = "unknown"
        notices.append("提示: 取不到 git HEAD（git 缺席或目标不在仓内）"
                       " —— reviewedCommit=unknown（sha256 锚定不受影响）")
    ok, name = _git(["config", "user.name"], cwd)
    if not ok or not name:
        name = "unknown"
        notices.append("提示: 取不到 git user.name —— reviewedBy=unknown")
    return commit, name, notices


def review_path_for(target: Path, review_dir: "Path | None") -> Path:
    """审记旁档路径：<review-dir>/<目标去扩展>-review.json；缺省 exports/reviews/。"""
    rdir = review_dir if review_dir is not None else DEFAULT_REVIEW_DIR
    return rdir / (target.stem + REVIEW_FILENAME_SUFFIX)


def load_trail(path: Path) -> "tuple[dict | None, str | None]":
    """读审记旁档。返回 (trail dict, None) 或 (None, 损坏原因)。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        return None, f"不可解析: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        return None, "头部结构坏（顶层须为含 records 列表的对象）"
    return data, None


def record_problems(rec: object, where: str) -> "list[str]":
    """单条审记记录的 schema 校验（verify/追加共用，AC2a/AC2b 的机判面）。"""
    problems = []
    if not isinstance(rec, dict):
        return [f"{where}记录不是对象"]
    for field in RECORD_BASE_FIELDS:
        if field not in rec:
            problems.append(f"{where}缺必备字段 `{field}`")
    for field in ("target", "reviewedCommit", "reviewedBy", "date", "notes"):
        if field in rec and not isinstance(rec[field], str):
            problems.append(f"{where}字段 `{field}` 须为字符串")
    if "reviewedBy" in rec and not rec["reviewedBy"]:
        problems.append(f"{where}字段 `reviewedBy` 为空")
    verdict = rec.get("verdict")
    if "verdict" in rec and verdict not in LEGAL_VERDICTS:
        problems.append(f"{where}verdict 非法值: {verdict!r}"
                        f"（合法: {'/'.join(LEGAL_VERDICTS)}）")
    sha = rec.get("reviewedSha256")
    if "reviewedSha256" in rec and not (isinstance(sha, str) and SHA256_RE.match(sha)):
        problems.append(f"{where}字段 `reviewedSha256` 须为 64 位十六进制")
    if "checkpoints" in rec and not (isinstance(rec["checkpoints"], list)
                                     and all(isinstance(c, str) for c in rec["checkpoints"])):
        problems.append(f"{where}字段 `checkpoints` 须为字符串列表")
    if verdict == VERDICT_REJECTED:
        routing = rec.get("routing")
        if not (isinstance(routing, str) and routing.strip()):
            problems.append(f"{where}verdict=打回 须带非空 `routing`（打回必须当场开单）")
    return problems


def trail_problems(trail: dict) -> "list[str]":
    """全量记录校验：任一脏记录都使审记整体不可信（fail loud，不跳过）。"""
    problems = []
    for i, rec in enumerate(trail["records"]):
        problems.extend(record_problems(rec, f"records[{i}] "))
    return problems


def write_trail(path: Path, trail: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trail, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def append_record(target: Path, rpath: Path, record: dict) -> "tuple[bool, str]":
    """向审记旁档追加一条记录（追加不覆盖）。返回 (成功, 拒绝原因)。

    审记缺席 → 自动落头（首条记录即历史起点）；损坏/非法 → 拒绝追加（不重建，
    design §3.4 #2：审记可以缺，不可以编——追加不能"顺手修史"）。
    """
    if rpath.exists():
        trail, corrupt = load_trail(rpath)
        if trail is None:
            return False, f"审记损坏（{corrupt}）—— 拒绝追加（不重建审记，防伪造历史），" \
                          f"请先人工处置: {rpath}"
        problems = trail_problems(trail)
        if problems:
            return False, "审记非法（既有记录违约）—— 拒绝追加，请先人工处置:\n  " \
                          + "\n  ".join(problems)
        trail["records"].append(record)
    else:
        trail = {"target": str(target), "created": date.today().isoformat(),
                 "records": [record]}
    write_trail(rpath, trail)
    return True, ""


def parse_checkpoints(raw: "str | None") -> list:
    """--checkpoints "a, b、c" → ["a", "b", "c"]（逗号/顿号/分号分隔，空段丢弃）。"""
    if not raw:
        return []
    return [seg.strip() for seg in re.split(r"[,，、;；]", raw) if seg.strip()]


def build_record(target: Path, verdict: str, checkpoints: list, notes: str,
                 routing: "str | None") -> dict:
    commit, by, notices = git_anchor(target)
    for n in notices:
        print(n, file=sys.stderr)
    record = {
        "target": str(target),
        "reviewedCommit": commit,
        "reviewedSha256": sha256_of(target),
        "verdict": verdict,
        "checkpoints": checkpoints,
        "notes": notes,
        "reviewedBy": by,
        "date": date.today().isoformat(),
    }
    if verdict == VERDICT_REJECTED:
        record["routing"] = routing
    return record


def short(value: str) -> str:
    return value if len(value) <= 12 else value[:12] + "…"


# ---------- 四动作 ----------

def cmd_init(target: Path, rpath: Path) -> int:
    if not target.is_file():
        print(f"配置错误: 目标不存在: {target}", file=sys.stderr)
        return EXIT_CONFIG
    if rpath.exists():
        trail, corrupt = load_trail(rpath)
        if trail is None:
            print(f"审记已存在但不可解析（损坏）—— 不重建（design §3.4 #2："
                  f"审记可以缺，不可以编），请人工处置: {rpath}", file=sys.stderr)
            return EXIT_RED
        print(f"审记已存在，不重建（追加不覆盖）: {rpath}"
              f"（现有 {len(trail['records'])} 条记录）")
        return EXIT_OK
    write_trail(rpath, {"target": str(target),
                        "created": date.today().isoformat(), "records": []})
    print(f"已建审记旁档骨架: {rpath}")
    return EXIT_OK


def cmd_approve(target: Path, rpath: Path, checkpoints: list, notes: str) -> int:
    if not target.is_file():
        print(f"配置错误: 目标不存在: {target}", file=sys.stderr)
        return EXIT_CONFIG
    record = build_record(target, VERDICT_APPROVED, checkpoints, notes, None)
    ok, refuse = append_record(target, rpath, record)
    if not ok:
        print(refuse, file=sys.stderr)
        return EXIT_CONFIG if "审记非法" in refuse else EXIT_RED
    print(f"已记审记: {rpath}")
    print(f"  verdict=已审  sha256={short(record['reviewedSha256'])}"
          f"  commit={short(record['reviewedCommit'])}  by={record['reviewedBy']}"
          f"  date={record['date']}")
    return EXIT_OK


def cmd_reject(target: Path, rpath: Path, routing: "str | None",
               checkpoints: list, notes: str) -> int:
    if not routing or not routing.strip():
        print("配置错误: reject 须带 --routing（打回必须当场开单: "
              "业务错道→提案池 / 工程错道→tickets/NN）", file=sys.stderr)
        return EXIT_CONFIG
    if not target.is_file():
        print(f"配置错误: 目标不存在: {target}", file=sys.stderr)
        return EXIT_CONFIG
    record = build_record(target, VERDICT_REJECTED, checkpoints, notes,
                          routing.strip())
    ok, refuse = append_record(target, rpath, record)
    if not ok:
        print(refuse, file=sys.stderr)
        return EXIT_CONFIG if "审记非法" in refuse else EXIT_RED
    print(f"已记审记: {rpath}")
    print(f"  verdict=打回  routing: {record['routing']}")
    print(f"  sha256={short(record['reviewedSha256'])}"
          f"  commit={short(record['reviewedCommit'])}  by={record['reviewedBy']}"
          f"  date={record['date']}")
    return EXIT_OK


def verify_record(target: Path, rpath: Path) -> "tuple[int, str, str, dict | None, int]":
    """核审记核心（票 77 提炼）：verify --all / onboard_check / report_numbers
    共用同一状态机，不再各复制一份。返回 (exit_code, status, reason, record,
    records_count)，不打印。"""
    if not target.is_file():
        return EXIT_CONFIG, "invalid", f"配置错误: 目标不存在: {target}", None, 0

    trail = None
    if not rpath.exists():
        return EXIT_RED, "pending", (
            f"无审记（缺失=无效）: {rpath} —— 按待人审处理，"
            f"不重建审记（宁多审一次，design §3.4 #2）"), None, 0
    trail, corrupt = load_trail(rpath)
    if trail is None:
        return EXIT_RED, "pending", (
            f"审记损坏（{corrupt}）: {rpath} —— 按待人审处理，"
            f"不重建审记"), None, 0
    if not trail["records"]:
        return EXIT_RED, "pending", (
            f"审记无任何裁决记录: {rpath} —— 按待人审处理"), None, 0
    problems = trail_problems(trail)
    if problems:
        return EXIT_CONFIG, "invalid", (
            "审记非法（记录缺必备字段或 verdict 非法值）—— 配置错，脏点: "
            + "; ".join(problems) + "；不重建审记"), None, len(trail["records"])

    # 本目标的最新裁决（票 59）：审记旁档按 target.stem 命名（bohai 与 pkb 的
    # devkit 同落 devkit-review.json），记录内 target 字段是唯一甄别键——
    # 不过滤会错拿别的生成物最新锚来比对，跨件误判「失效」。
    # 同件判定（票 59 夹具回归）：approve 时写相对串（如夹具 'targets/x.md'）、
    # verify 传绝对串是同一件——构件边界后缀匹配（任一方完整后缀于另一方）。
    def _same_target(rec_target: str, tgt: str) -> bool:
        return rec_target == tgt or tgt.endswith("/" + rec_target) \
            or rec_target.endswith("/" + tgt)

    mine = [r for r in trail["records"]
            if isinstance(r.get("target"), str)
            and _same_target(r["target"], str(target))]
    if not mine:
        return EXIT_RED, "pending", (
            f"无本目标审记（旁档 {rpath} 现有其他生成物记录 "
            f"{len(trail['records'])} 条，无 {target} 的记录）"
            f"—— 按待人审处理（宁多审一次，design §3.4 #2）"), None, len(trail["records"])
    record = mine[-1]
    if record["verdict"] == VERDICT_REJECTED:
        return EXIT_RED, "rejected", (
            f"最新裁决为打回（routing: {record.get('routing', '')}）"
            f"—— 按未通过处理，整改后再审"), record, len(trail["records"])
    current = sha256_of(target)
    if current == record["reviewedSha256"]:
        return EXIT_OK, "pass", (
            f"已审且哈希一致: {target}\n  审记: {rpath}"
            f"\n  锚定 commit={short(record['reviewedCommit'])}"
            f" by={record['reviewedBy']} date={record['date']}"), record, len(trail["records"])
    return EXIT_RED, "stale", (
        f"审记失效: 生成物已再生/被改（现算 {short(current)} ≠ 锚定 "
        f"{short(record['reviewedSha256'])}）→ 已审结论自动失效，"
        f"回落待人审（零宽限；旧审记保留可查）"), record, len(trail["records"])


def cmd_verify(target: Path, rpath: Path, as_json: bool = False) -> int:
    code, status, reason, record, n_records = verify_record(target, rpath)
    if as_json:
        print(json.dumps({
            "tool": "review_gate", "ticket": TICKET,
            "target": str(target), "reviewFile": str(rpath),
            "status": status, "exitCode": code, "reason": reason,
            "recordsCount": n_records,
            "record": record,
        }, ensure_ascii=False, indent=2))
    elif code == EXIT_CONFIG:
        print(reason, file=sys.stderr)  # 配置错走 stderr（票 45 契约保持）
    else:
        print(reason)
    return code


# verify --all 的枚举面（票 77）：devkit 与 skillpkg 两类生成物；manifest 免审级不在面内。
VERIFY_ALL_GLOBS = ("exports/devkit/*/devkit.md", "exports/skillpkg/*/SKILL.md")


def cmd_verify_all(root: Path, as_json: bool = False,
                   review_dir: "Path | None" = None) -> int:
    """枚举 exports 面逐件核审记（票 77，AGENTS 协议⑥枚举化承载）。
    逐行报状态；任一非 pass exit 1，任一配置错 exit 2。缺失/失效照旧=
    收官挂账项，不阻塞四闸（本命令不进 ci.sh）。"""
    targets = sorted(t for pat in VERIFY_ALL_GLOBS for t in root.glob(pat))
    if not targets:
        print(f"配置错误: {root}/exports 下无 devkit/skillpkg 生成物可核",
              file=sys.stderr)
        return EXIT_CONFIG
    rdir = review_dir if review_dir is not None else root / "exports" / "reviews"
    if not as_json:
        print(f"verify --all：{len(targets)} 件（{' + '.join(VERIFY_ALL_GLOBS)}）")
    worst = EXIT_OK
    for t in targets:
        code, status, reason, record, n_records = verify_record(
            t, review_path_for(t, rdir))
        if as_json:
            print(json.dumps({
                "tool": "review_gate", "ticket": TICKET, "mode": "all",
                "target": str(t), "status": status, "exitCode": code,
                "reason": reason, "recordsCount": n_records, "record": record,
            }, ensure_ascii=False))
        else:
            stream = sys.stderr if code == EXIT_CONFIG else sys.stdout
            print(f"[{status}] {reason}", file=stream)
        worst = max(worst, code)
    if not as_json:
        print(f"verify --all 小结: {len(targets)} 件，最差退出码 {worst}"
              f"（非 0 = 存在待人审/失效/打回件，按收官挂账口径处理）")
    return worst


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="人审闸审记状态机（票 45）：init/approve/reject/verify + "
                    "哈希锚定。退出码 0 一致 / 1 失效或缺失 / 2 配置错")
    sub = ap.add_subparsers(dest="action", required=True)

    def add_target(p):
        p.add_argument("target", help="被审生成物路径")
        # --routing 不交给 argparse required：缺 routing 的报错须带「打回必须
        # 当场开单」语义（cmd_reject 内强制，exit 2），argparse 的裸缺参提示无此语义。
        p.add_argument("--routing", default=None,
                       help="打回路由（reject 必带: 业务错道→提案池 / "
                            "工程错道→tickets/NN）")
        p.add_argument("--checkpoints", default=None,
                       help="审点清单（逗号/顿号分隔）")
        p.add_argument("--notes", default="", help="审记备注")
        p.add_argument("--review-dir", default=None,
                       help=f"审记旁档目录（缺省 {DEFAULT_REVIEW_DIR}）")

    add_target(sub.add_parser("init", help="建审记旁档骨架（已存在不重建）"))
    add_target(sub.add_parser("approve", help="追加 verdict=已审 审记"))
    add_target(sub.add_parser("reject", help="追加 verdict=打回 审记"
                                          "（--routing 必带）"))
    p_verify = sub.add_parser("verify", help="现算 sha256 与最新审记比对"
                                              "（单件传 target；枚举面传 --all）")
    p_verify.add_argument("target", nargs="?", default=None,
                          help="被审生成物路径（--all 时可省）")
    p_verify.add_argument("--all", action="store_true",
                          help="枚举 exports/devkit/*/devkit.md + "
                               "exports/skillpkg/*/SKILL.md 逐件核（票 77）")
    p_verify.add_argument("--root", default=None,
                          help="--all 的枚举根（缺省=本脚本上级目录；单件模式不适用）")
    p_verify.add_argument("--review-dir", default=None,
                          help=f"审记旁档目录（缺省 {DEFAULT_REVIEW_DIR}；"
                               f"--all 缺省 <root>/exports/reviews）")
    p_verify.add_argument("--json", action="store_true",
                          help="机读输出（单件=单一 JSON；--all=逐件 JSON Lines）")
    args = ap.parse_args(argv)

    if args.action == "verify" and getattr(args, "all", False):
        root = Path(args.root) if args.root \
            else Path(__file__).resolve().parent.parent
        review_dir = Path(args.review_dir) if args.review_dir else None
        return cmd_verify_all(root, as_json=args.json, review_dir=review_dir)
    if args.action == "verify" and not args.target:
        ap.error("verify 需要单件 target 或 --all 枚举面")

    target = Path(args.target)
    rpath = review_path_for(target, Path(args.review_dir) if args.review_dir
                            else None)
    if args.action == "init":
        return cmd_init(target, rpath)
    if args.action == "approve":
        return cmd_approve(target, rpath, parse_checkpoints(args.checkpoints),
                           args.notes)
    if args.action == "reject":
        return cmd_reject(target, rpath, args.routing,
                          parse_checkpoints(args.checkpoints), args.notes)
    return cmd_verify(target, rpath, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
