#!/usr/bin/env python3
"""schema_check.py —— 语义 CI L1–L4 闸（All-agent 票 03；spec: specs/schema_check.md AC1–7）。

对给定 ontology 目录做确定性校验：
  L1 schema 合法——YAML 可解析（AC2）、公共字段 model_type/version/domain 在场（AC3）、
     域 manifest.json 在场且 profile 已登记、模型类型已知、schema 两份机读表互相一致；
  L2 引用与依赖——ref 指向的 ID 全仓有定义（AC4 悬空引用）、ref 目标模型不越
     类型层依赖白名单（AC5，真源 ontology/schema/model-deps.json + model-registry.json）；
  L4 profile 合规与兼容——profile 未启用的模型文件不得出现（AC6）、
     换义锁定字段（model-registry.json lockedFields）不得复用（AC7 字段换义式变更）。

只读不写 YAML；失败输出含文件+行级定位（行号取自 YAML node start_mark）；
--json 供 CI 消费。依赖：Python3 stdlib + PyYAML（safe 装载，PRD 技术栈唯一第三方）。

CLI: python3 tools/schema_check.py <ontology目录> [--json]
  <ontology目录> 可以是本体仓根（下含 schema/ 与若干域目录）或单个域目录
  （schema 解析顺序：本目录 schema/ → 上级目录 schema/）。

退出码：0 全过；1 有违规；2 配置/用法错误。
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

COMMON_FIELDS = ("model_type", "version", "domain")
MANIFEST_REQUIRED = ("domain", "profile")


# ---------- 带行号的 YAML 装载（只读；safe） ----------

class MDict(dict):
    """带行号与键行号的映射（行号=首键行；key_lines=各键自身行）。"""

    line = 0
    key_lines = None


class MList(list):
    """带行号的序列。"""

    line = 0


class LineLoader(yaml.SafeLoader):
    """SafeLoader + 行号标注：映射/序列容器记录 start_mark 行号。"""


def _construct_map(loader, node, deep=False):
    loader.flatten_mapping(node)
    mapping = MDict()
    yield mapping
    key_lines = {}
    for k_node, v_node in node.value:
        key = loader.construct_object(k_node, deep=deep)
        value = loader.construct_object(v_node, deep=deep)
        mapping[key] = value
        key_lines[key] = k_node.start_mark.line + 1
    mapping.line = node.start_mark.line + 1
    mapping.key_lines = key_lines


def _construct_seq(loader, node, deep=False):
    seq = MList()
    yield seq
    seq.extend(loader.construct_sequence(node, deep=deep))
    seq.line = node.start_mark.line + 1


LineLoader.add_constructor("tag:yaml.org,2002:map", _construct_map)
LineLoader.add_constructor("tag:yaml.org,2002:seq", _construct_seq)


def load_yaml(path: Path):
    """解析 YAML；语法错误抛 _YamlSyntaxError（带文件与行号）。"""
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.load(fh, Loader=LineLoader)
    except yaml.MarkedYAMLError as exc:
        mark = exc.problem_mark or exc.context_mark
        line = mark.line + 1 if mark else 0
        problem = exc.problem or str(exc)
        raise _YamlSyntaxError(f"{path.name}:{line} {problem}") from exc
    except yaml.YAMLError as exc:
        raise _YamlSyntaxError(f"{path.name} {exc}") from exc


class _YamlSyntaxError(Exception):
    pass


# ---------- 目录/配置解析 ----------

def resolve_schema_dir(target: Path) -> Path | None:
    for cand in (target / "schema", target.parent / "schema"):
        if cand.is_dir():
            return cand
    return None


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{path} 不存在（schema 机读表必配）") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"{path} 不是合法 JSON: {exc}") from exc


def discover_domains(target: Path) -> tuple[list[Path], list[Path]]:
    """返回 (域目录列表, 有模型文件但缺 manifest 的目录列表)。"""
    if (target / "manifest.json").is_file():
        return [target], []
    domains, missing = [], []
    for sub in sorted(target.iterdir()):
        if not sub.is_dir() or sub.name == "schema":
            continue
        if (sub / "manifest.json").is_file():
            domains.append(sub)
        elif any(sub.glob("*.yaml")) or any(sub.glob("*.yml")):
            missing.append(sub)
    return domains, missing


def model_files(domain: Path) -> list[Path]:
    return sorted(p for p in domain.rglob("*")
                  if p.is_file() and p.suffix in (".yaml", ".yml"))


# ---------- 遍历与 ID/ref 判定 ----------

def iter_mappings(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from iter_mappings(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_mappings(item)


def is_ref_key(key: str, ref_keys: set) -> bool:
    return key in ref_keys or key.endswith("Ref") or key.endswith("Refs")


def id_model_of(value: str, prefix2model: dict) -> str | None:
    for prefix, model in prefix2model.items():
        if value.startswith(prefix):
            return model
    return None


def key_line(mapping, key) -> int:
    if getattr(mapping, "key_lines", None):
        return mapping.key_lines.get(key, mapping.line)
    return getattr(mapping, "line", 0)


def collect_definitions(data, ref_keys: set, prefix2model: dict):
    """收集本文件定义的 ID：定义键（id / *Id，且非 ref 键）上带已知前缀的标量。"""
    found = {}
    for mapping in iter_mappings(data):
        for key, value in mapping.items():
            if is_ref_key(key, ref_keys):
                continue  # ref 值不得自证存在（防自引用洗白悬空检查）
            if key != "id" and not (isinstance(key, str) and key.endswith("Id")):
                continue
            if isinstance(value, str):
                model = id_model_of(value, prefix2model)
                if model:
                    found.setdefault(value, key_line(mapping, key))
    return found


def iter_ref_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_ref_strings(item)


# ---------- 主校验 ----------

def run(target: Path) -> dict:
    target = target.resolve()
    if not target.is_dir():
        raise ValueError(f"目标目录不存在: {target}")
    schema_dir = resolve_schema_dir(target)
    if schema_dir is None:
        raise ValueError(f"{target} 及其上级都没有 schema/ 目录（缺模型注册表）")
    registry = load_json(schema_dir / "model-registry.json")
    deps = load_json(schema_dir / "model-deps.json")
    models = registry.get("models")
    prefix2model = deps.get("idPrefixes")
    ref_keys = set(deps.get("refKeys", []))
    if not isinstance(models, dict) or not isinstance(prefix2model, dict):
        raise ValueError(f"{schema_dir} 的注册表/依赖表缺 models/idPrefixes")

    # 一致性核对：model-deps.json 的 edges 不得超出 model-registry.json 的 dependsOn（自依赖除外）
    edges = {}
    for edge in deps.get("edges", []):
        edges[(edge["from"], edge["field"])] = set(edge["to"])
    violations = []  # {level, kind, file, line, message}
    seen = set()

    def add(level, kind, file, line, message):
        key = (kind, file, line, message)
        if key not in seen:
            seen.add(key)
            violations.append(
                {"level": level, "kind": kind, "file": file,
                 "line": line, "message": message})

    for (frm, _field), to in edges.items():
        if frm not in models:
            add("L1", "deps-registry-conflict", str(schema_dir / "model-deps.json"), 0,
                f"edges 引用未注册模型 {frm}")
            continue
        extra = to - set(models[frm].get("dependsOn", [])) - {frm}
        if extra:
            add("L1", "deps-registry-conflict",
                str(schema_dir / "model-deps.json"), 0,
                f"{frm} 的依赖边 {sorted(to)} 超出 dependsOn "
                f"{sorted(models[frm].get('dependsOn', []))}（两份机读表冲突）")

    model_by_type = {m["modelType"]: key for key, m in models.items()}
    known_profiles = {p for m in models.values() for p in m.get("profiles", [])}
    domains, manifest_missing = discover_domains(target)
    for sub in manifest_missing:
        add("L1", "missing-manifest", str(sub / "manifest.json"), 0,
            f"目录「{sub.name}」含模型 YAML 但缺 manifest.json（域声明必配）")

    definitions: dict[str, tuple[str, int]] = {}
    domain_summaries = []
    n_files = 0

    for domain in domains:
        manifest = load_json(domain / "manifest.json")
        dname = manifest.get("domain", domain.name)
        profile = manifest.get("profile")
        for field in MANIFEST_REQUIRED:
            if field not in manifest:
                add("L1", "missing-manifest-field", str(domain / "manifest.json"), 0,
                    f"manifest 缺必备字段 `{field}`")
        if profile not in known_profiles:
            add("L1", "unknown-profile", str(domain / "manifest.json"), 0,
                f"未知 profile「{profile}」（注册表可用: {sorted(known_profiles)}）")
            profile = None
        enabled = {key for key, m in models.items()
                   if profile and profile in m.get("profiles", [])}
        files = model_files(domain)
        n_files += len(files)
        domain_summaries.append({"domain": dname, "profile": profile,
                                 "files": len(files), "enabled": sorted(enabled)})

        for path in files:
            rel = str(path)
            try:
                data = load_yaml(path)
            except _YamlSyntaxError as exc:  # AC2
                add("L1", "yaml-syntax", rel, 0, f"YAML 语法错误: {exc}")
                continue
            if data is None or not isinstance(data, dict):
                add("L1", "yaml-syntax", rel, 0, "YAML 顶层必须是映射")
                continue
            for field in COMMON_FIELDS:  # AC3
                if field not in data:
                    add("L1", "missing-common-field", rel,
                        key_line(data, field) or data.line,
                        f"缺少公共字段 `{field}`（公共字段: model_type/version/domain）")
            mtype = data.get("model_type")
            mkey = model_by_type.get(mtype) if isinstance(mtype, str) else None
            if mtype is not None and mkey is None:  # AC3 延伸：类型必须已注册
                add("L1", "unknown-model-type", rel, data.line,
                    f"未知 model_type「{mtype}」（注册表: {sorted(model_by_type)}）")
                continue
            if mkey is None:
                continue
            if mkey not in enabled:  # AC6
                add("L4", "profile-disabled", rel, data.line,
                    f"profile「{profile}」未启用模型 {mkey}，但出现其文件"
                    f"（注册表 profiles: {models[mkey].get('profiles')}）")
            locked = models[mkey].get("lockedFields", {})
            for mapping in iter_mappings(data):  # AC7
                for key in mapping:
                    if isinstance(key, str) and key in locked:
                        add("L4", "field-redefinition", rel, key_line(mapping, key),
                            f"字段「{key}」为换义锁定字段（旧义: {locked[key]}）——"
                            f"禁止复用换义，如需新义请新增字段名")
            depends_on = set(models[mkey].get("dependsOn", [])) | {mkey}
            for mapping in iter_mappings(data):
                for key, value in mapping.items():
                    if not (isinstance(key, str) and is_ref_key(key, ref_keys)):
                        continue
                    for ref in iter_ref_strings(value):
                        if not isinstance(ref, str):
                            continue
                        target_model = id_model_of(ref, prefix2model)
                        if target_model is None:
                            continue
                        allowed = edges.get((mkey, key), depends_on)
                        if target_model not in allowed:  # AC5
                            add("L2", "dep-whitelist", rel, key_line(mapping, key),
                                f"ref 类型越白名单: {mkey}.{key} → {target_model}"
                                f" 不在允许 {sorted(allowed)}（model-deps.json/"
                                f"model-registry.json dependsOn）")
            for ref_id, loc in collect_definitions(
                    data, ref_keys, prefix2model).items():
                definitions.setdefault(ref_id, (rel, loc))

    # 悬空引用统一判定（定义收集完后）
    for domain in domains:
        for path in model_files(domain):
            rel = str(path)
            try:
                data = load_yaml(path)
            except _YamlSyntaxError:
                continue
            if not isinstance(data, dict):
                continue
            mtype = data.get("model_type")
            if not isinstance(mtype, str) or mtype not in model_by_type:
                continue
            for mapping in iter_mappings(data):
                for key, value in mapping.items():
                    if not (isinstance(key, str) and is_ref_key(key, ref_keys)):
                        continue
                    for ref in iter_ref_strings(value):
                        if isinstance(ref, str) and \
                                id_model_of(ref, prefix2model) and \
                                ref not in definitions:
                            add("L2", "dangling-ref", rel, key_line(mapping, key),
                                f"悬空引用: ref 字段「{key}」指向的 {ref} "
                                f"在本体仓内无 ID 定义")

    by_level = {lv: sum(1 for v in violations if v["level"] == lv)
                for lv in ("L1", "L2", "L4")}
    return {
        "status": "fail" if violations else "pass",
        "target": str(target),
        "schemaDir": str(schema_dir),
        "domains": domain_summaries,
        "files": n_files,
        "levels": by_level,
        "violations": violations,
    }


def print_human(report: dict) -> None:
    domains = "、".join(
        f"{d['domain']}(profile={d['profile']},{d['files']}文件)"
        for d in report["domains"]) or "无域"
    print(f"语义闸 schema_check — {report['target']}")
    print(f"域: {domains}；模型文件 {report['files']} 个")
    for v in report["violations"]:
        loc = f"{v['file']}:{v['line']}" if v["line"] else v["file"]
        print(f"[{v['level']}][{v['kind']}] {loc} — {v['message']}")
    lv = report["levels"]
    if report["status"] == "pass":
        print("L1: 0 | L2: 0 | L4: 0")
        print("语义闸: 全过")
    else:
        print(f"L1: {lv['L1']} | L2: {lv['L2']} | L4: {lv['L4']}")
        print(f"语义闸: {sum(lv.values())} 处违规")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="语义 CI L1–L4 闸（specs/schema_check.md）")
    ap.add_argument("target", help="ontology 目录（仓根或单域目录）")
    ap.add_argument("--json", action="store_true", help="机读 JSON 输出（供 CI 消费）")
    args = ap.parse_args(argv)
    try:
        report = run(Path(args.target))
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
