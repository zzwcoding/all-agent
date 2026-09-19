#!/usr/bin/env python3
"""schema_check.py —— 语义 CI L1–L4 闸（All-agent 票 03；spec: specs/schema_check.md AC1–7；
票 10 增 GLS 术语模型套件 GLS-AC1–4；票 11 增 L2 一致性对检查组 consistency-*，真源=
tickets/11-一致性对核验.md AC 表 + ontology/schema/schema.md §14；票 13 增 L1 元素级
结构性必填闸 required-field（真源=model-registry.json 每模型 requiredElementFields）与
L4 AC6 反向闸 missing-model-file（profile 启用却缺文件，经 manifest omittedModels
带理由豁免）；票 16 增 L4 禁用词拦截面 banned-term（真源=域内 GLS 术语 status 含
「禁用」条目的 term+aliases，匹配面=递归收集键恰为 name/alias 的字符串值子串命中，
description/notes 不扫=文档自由）。

对给定 ontology 目录做确定性校验：
  L1 schema 合法——YAML 可解析（AC2）、公共字段 model_type/version/domain 在场（AC3）、
     域 manifest.json 在场且 profile 已登记、模型类型已知、文件名与注册表该模型
     yamlFile 一致（票 10 AC4：GLS 文件名错挂/model_type 写错；真源=model-registry.json
     yamlFile，即"一模型一 YAML、固定文件名"约定的闸上强化）、schema 两份机读表互相一致、
     逐元素结构性必填字段在场（票 13 required-field：身份/类型判别/检查锚点/载荷容器四类，
     口径与逐模型推导表见 lessons/13；空壳文件——不含任何本模型元素——同报 required-field）；
  L2 引用与依赖——ref 指向的 ID 全仓有定义（AC4 悬空引用）、ref 目标模型不越
     类型层依赖白名单（AC5，真源 ontology/schema/model-deps.json + model-registry.json）；
     一致性对（票 11，digest §12.2 本仓可行子集）：
       consistency-redirection    M7.behaviorRef 未指向 behaviorType=QUERY 的 M2 行为
       consistency-not-one-to-one 同一 M2 查询行为被两个 M7 对象绑定（严格一对一）
       consistency-permission     M2.requiredPermissions 指到的 PERM.targetRef 未回指该行为
       consistency-flow-role      M6 活动 roleRef 不在流程 roleRefs 集合内；
     涉事元素存在性仍由 dangling-ref 承载（ref 扫描面=refKeys ∪ *Ref/Refs ∪ edges），
     本组只补"语义闭合向"，违规 kind 一律 consistency- 前缀（schema.md §14）。
  L4 profile 合规与兼容——profile 未启用的模型文件不得出现（AC6；票 10 GLS-AC2 同款）、
     profile 启用的模型缺文件且 manifest omittedModels 无带理由豁免条目必须红
     （票 13 AC6 反向 missing-model-file）、换义锁定字段（lockedFields）不得复用
     （AC7 字段换义式变更）。

模型类型/文件名/前缀/依赖/必填判定全部走两份机读表（model-registry.json +
model-deps.json），本脚本不硬编码任何模型清单——新增模型=机读表加条目。

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


def collect_elements(data, mkey: str, prefix2model: dict, ref_keys: set):
    """收集本文件中主 ID 前缀→mkey 的元素：[(元素ID, 映射)]（票 11 一致性对用）。

    元素主 ID = `id` / `*Id` 键（非 ref 键）上的字符串值——与 collect_definitions
    同一定义面，且前缀判回本模型；嵌套结构里的非注册前缀 ID（如 M6 活动 activityId、
    M7 条件 conditionId 不在 idPrefixes）天然不入选。
    """
    out = []
    for mapping in iter_mappings(data):
        for key, value in mapping.items():
            if not (isinstance(key, str) and (key == "id" or key.endswith("Id"))):
                continue
            if is_ref_key(key, ref_keys) or not isinstance(value, str):
                continue
            if id_model_of(value, prefix2model) == mkey:
                out.append((value, mapping))
    return out


# ---------- 禁用词拦截面（票 16：GLS×schema_check 联动闸） ----------

NAME_ALIAS_KEYS = ("name", "alias")


def load_yaml_from_text(text: str):
    """文本直载（单测构造带行号数据用，与 load_yaml 同一 LineLoader）。"""
    import io
    return yaml.load(io.StringIO(text), Loader=LineLoader)


def iter_name_alias_values(data):
    """递归收集键恰为 name/alias 的字符串值：[(值, 所在映射, 键名)]。

    匹配面口径（票 16 L0 定稿）：所有字典中键**恰为** `name`/`alias` 的字符串值，
    通用口径递归全仓（不逐模型硬列挂点）。不入面的：label/definition/notes 等
    其他键（文档提及合法）、复数 `aliases` 键（那是 GLS 禁用词表的**来源**字段，
    不是匹配面）、非字符串值。GLS 条目以 `term` 键承载词面——天然不在匹配面
    （禁用词表不会自匹配，专测钉死）。
    """
    for mapping in iter_mappings(data):
        for key in NAME_ALIAS_KEYS:
            value = mapping.get(key) if isinstance(mapping, dict) else None
            if isinstance(value, str):
                yield value, mapping, key


def collect_banned_terms(data) -> list[tuple[str, str, str]]:
    """从 GLS 术语数据收集禁用词表：[(词, 条目ID, status 原文)]。

    判定（票 16 设计裁决，宽进严出）：条目 `status` 字段值**包含**「禁用」子串
    即入表（不枚举状态值——「禁用（替代：×）」「已禁用待复核」同拦）；
    禁用词成员 = term 字段值 + aliases 列表成员。
    """
    out: list[tuple[str, str, str]] = []
    terms = data.get("terms")
    if not isinstance(terms, list):
        return out
    for entry in terms:
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        if not (isinstance(status, str) and "禁用" in status):
            continue
        gls_id = entry.get("id", "?")
        term = entry.get("term")
        if isinstance(term, str) and term:
            out.append((term, gls_id, status))
        for alias in iter_ref_strings(entry.get("aliases") or []):
            if isinstance(alias, str) and alias:
                out.append((alias, gls_id, status))
    return out


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

        # AC6 反向（票 13）：manifest omittedModels 显式豁免清单——profile 启用的
        # 模型无文件时，必须有带理由的豁免条目，否则 L4 missing-model-file 红。
        # 豁免条目 = {model: 注册表模型键, reason: 非空字符串}；reason 缺失/空串
        # 视为无效豁免（=无豁免），引用未注册模型单独 L1 红。
        omitted: dict[str, str] = {}
        for entry in manifest.get("omittedModels") or []:
            if not isinstance(entry, dict) or "model" not in entry:
                add("L1", "bad-omitted-model", str(domain / "manifest.json"), 0,
                    f"omittedModels 条目必须是含 model/reason 的对象: {entry!r}")
                continue
            om = entry.get("model")
            if om not in models:
                add("L1", "unknown-omitted-model", str(domain / "manifest.json"),
                    0, f"omittedModels 引用未注册模型「{om}」（注册表: {sorted(models)}）")
                continue
            reason = entry.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                continue  # 无理由 = 无效豁免，缺文件时照报 missing-model-file
            omitted[om] = reason.strip()
        # 在场判定按注册文件名（稳健于内容解析失败：文件建了=在场，schema 错误
        # 是 L1 的管辖面，不在此重复追责）
        file_names = {p.name for p in files}
        present_models = {key for key, m in models.items()
                          if m.get("yamlFile") in file_names}

        domain_summaries.append({"domain": dname, "profile": profile,
                                 "files": len(files), "enabled": sorted(enabled),
                                 "omittedModels": sorted(omitted)})

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
            yaml_file = models[mkey].get("yamlFile")
            name_mismatch = bool(yaml_file) and path.name != yaml_file
            if name_mismatch:  # 票 10 AC4：文件名与 model_type 错挂
                add("L1", "filename-mismatch", rel, data.line,
                    f"文件名「{path.name}」与 model_type「{mtype}」的注册文件名"
                    f"「{yaml_file}」不符（一模型一 YAML、固定文件名，"
                    f"真源 model-registry.json yamlFile）")

            # 元素级结构性必填闸（票 13，真源=model-registry.json
            # requiredElementFields）。文件名错挂时内容与模型的锚已断，闸让位给
            # filename-mismatch，不叠加空壳红因（负变体红因纯净，lessons/13）。
            req_map = models[mkey].get("requiredElementFields") or {}
            if req_map and not name_mismatch:
                elements = collect_elements(data, mkey, prefix2model, ref_keys)
                if not elements:
                    add("L1", "required-field", rel, data.line,
                        f"模型 {mkey} 文件不含任何本模型元素（空壳文件：主集合为空"
                        f"或缺失）——结构性必填闸（票 13），真源 model-registry.json "
                        f"{mkey}.requiredElementFields")
                for eid, mapping in elements:
                    for prefix, fields in req_map.items():
                        if not eid.startswith(prefix):
                            continue
                        for fieldname in fields:
                            if fieldname not in mapping:
                                add("L1", "required-field", rel,
                                    key_line(mapping, fieldname),
                                    f"元素 {eid} 缺必填字段「{fieldname}」"
                                    f"（结构性必填：身份/类型判别/检查锚点/载荷容器，"
                                    f"缺失会使一致性对与引用扫描静默跳过；真源 "
                                    f"model-registry.json {mkey}.requiredElementFields）")

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

        # 禁用词拦截面（票 16）：域内 GLS 术语 status 含「禁用」条目的 term+aliases
        # = 机读禁用词表（闸位在 schema_check L4，真源唯一=GLS；运行时拒答是消费侧，
        # 票 17）。对全域文件 name/alias 做子串匹配，命中 = L4 banned-term。
        # GLS 无文件（未建模/旧域）时表为空、闸静默——禁用词拦截随术语表在场而启用。
        glossary_key = model_by_type.get("GLOSSARY")
        if glossary_key:
            banned: list[tuple[str, str, str]] = []
            for path in files:
                try:
                    data_b = load_yaml(path)
                except _YamlSyntaxError:
                    continue  # 语法错误由 L1 yaml-syntax 管辖
                if not isinstance(data_b, dict):
                    continue
                mtype_b = data_b.get("model_type")
                if isinstance(mtype_b, str) and \
                        model_by_type.get(mtype_b) == glossary_key:
                    banned.extend(collect_banned_terms(data_b))
            if banned:
                for path in files:
                    rel_b = str(path)
                    try:
                        data_m = load_yaml(path)
                    except _YamlSyntaxError:
                        continue
                    if not isinstance(data_m, dict):
                        continue
                    mtype_m = data_m.get("model_type")
                    mkey_m = (model_by_type.get(mtype_m)
                              if isinstance(mtype_m, str) else None)
                    if mkey_m is None:
                        continue
                    yaml_file_m = models[mkey_m].get("yamlFile")
                    if yaml_file_m and path.name != yaml_file_m:
                        continue  # filename-mismatch 管辖面，不叠禁用词红因（沿票 13 先例）
                    for value, mapping, key in iter_name_alias_values(data_m):
                        for word, gls_id, status in banned:
                            if word in value:
                                add("L4", "banned-term", rel_b,
                                    key_line(mapping, key),
                                    f"{key}「{value}」命中禁用词「{word}」"
                                    f"（{gls_id}，status={status}）——禁用术语不得"
                                    f"进元素 name/alias（description/notes 提及合法"
                                    f"=文档自由）；真源=域内 GLS 术语表 status 含"
                                    f"「禁用」条目（票 16）")

        # AC6 反向（票 13）：profile 启用的模型缺文件且无带理由豁免 = L4 红。
        # profile 未知时 enabled 为空、不触发（unknown-profile 已单独红）。
        if profile is not None:
            for mkey in sorted(enabled):
                if mkey in present_models or mkey in omitted:
                    continue
                add("L4", "missing-model-file", str(domain / "manifest.json"), 0,
                    f"profile「{profile}」启用模型 {mkey}，但域内无 "
                    f"{models[mkey].get('yamlFile')} 文件且 omittedModels 无带理由"
                    f"豁免条目（AC6 反向，票 13；确属有意裁剪须在 manifest 登记 "
                    f"omittedModels: [{{\"model\": \"{mkey}\", \"reason\": \"…\"}}]）")

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

    # ---------- 一致性对核验（票 11；digest §12.2 本仓可行子集，schema.md §14） ----------
    # 元素收集：锚定各模型的结构性承载字段（behaviorType/targetRef/behaviorRef/
    # activities），模型定位走注册表 modelType（脚本不硬编码模型键名）。涉事 ID 的
    # 存在性由上方 dangling-ref 承载，此处只判语义闭合向。
    m2_key = model_by_type.get("BEHAVIOR")
    m5_key = model_by_type.get("ACTOR")
    m6_key = model_by_type.get("FLOW")
    m7_key = model_by_type.get("REPORT")
    behaviors: dict[str, tuple[dict, str]] = {}
    permissions: dict[str, tuple[dict, str]] = {}
    query_reports: list[tuple[str, dict, str]] = []
    flows: list[tuple[str, dict, str]] = []
    if m2_key or m5_key or m6_key or m7_key:
        for domain in domains:
            for path in model_files(domain):
                rel_c = str(path)
                try:
                    data_c = load_yaml(path)
                except _YamlSyntaxError:
                    continue
                if not isinstance(data_c, dict):
                    continue
                mtype_c = data_c.get("model_type")
                mkey_c = model_by_type.get(mtype_c) if isinstance(mtype_c, str) else None
                if m2_key and mkey_c == m2_key:
                    for eid, mapping in collect_elements(
                            data_c, m2_key, prefix2model, ref_keys):
                        if "behaviorType" in mapping:
                            behaviors.setdefault(eid, (mapping, rel_c))
                elif m5_key and mkey_c == m5_key:
                    for eid, mapping in collect_elements(
                            data_c, m5_key, prefix2model, ref_keys):
                        if "targetRef" in mapping:
                            permissions.setdefault(eid, (mapping, rel_c))
                elif m7_key and mkey_c == m7_key:
                    for eid, mapping in collect_elements(
                            data_c, m7_key, prefix2model, ref_keys):
                        if "behaviorRef" in mapping:
                            query_reports.append((eid, mapping, rel_c))
                elif m6_key and mkey_c == m6_key:
                    for eid, mapping in collect_elements(
                            data_c, m6_key, prefix2model, ref_keys):
                        if "activities" in mapping:
                            flows.append((eid, mapping, rel_c))

    # P1 M7↔M2 严格一对一：M7.behaviorRef 必指向 behaviorType=QUERY 的行为，
    # 且同一查询行为不得被第二个 M7 绑定（依赖边单向 M7→M2，反向经 ref 反查，
    # schema.md §2/§9；本仓 M2 不写 queryReportRef）
    if m2_key and m7_key:
        first_bound: dict[str, str] = {}
        for qr_id, qr, rel_c in query_reports:
            bref = qr.get("behaviorRef")
            if not isinstance(bref, str):
                continue
            beh = behaviors.get(bref)
            if beh is None:
                continue  # 指向不存在行为 = dangling-ref 已报
            if beh[0].get("behaviorType") != "QUERY":
                add("L2", "consistency-redirection", rel_c, key_line(qr, "behaviorRef"),
                    f"一致性对 P1（M7↔M2 严格一对一）: 报表 {qr_id} 的 behaviorRef"
                    f"「{bref}」指向 behaviorType={beh[0].get('behaviorType')} 的行为，"
                    f"必须指向 behaviorType=QUERY 的 M2 行为"
                    f"（依据 M7.behaviorRef ↔ M2.behaviorType，schema.md §14）")
                continue
            if bref in first_bound:
                add("L2", "consistency-not-one-to-one", rel_c, key_line(qr, "behaviorRef"),
                    f"一致性对 P1（M7↔M2 严格一对一）: M2 查询行为「{bref}」已被报表 "
                    f"{first_bound[bref]} 绑定，报表 {qr_id} 再次绑定——同一行为不得被"
                    f"两个 M7 对象共享（依据 M7.behaviorRef 反查去重，schema.md §14）")
            else:
                first_bound[bref] = qr_id

    # P2 M2.requiredPermissions ↔ M5 双向闭合：requiredPermissions 指到的每个
    # PERM 的 targetRef 必回指该行为（存在性=dangling-ref：requiredPermissions 在
    # refKeys 且有 M2→M5 边）。锚定 M2.requiredPermissions 面——M5 侧单面登记权限
    # 承载岗位职责（行为 requiredPermissions 留空）不判红（schema.md §7/§14）
    if m2_key and m5_key:
        for bh_id, (bh, rel_c) in behaviors.items():
            req = bh.get("requiredPermissions")
            if not req:
                continue
            for pref in iter_ref_strings(req):
                if not isinstance(pref, str):
                    continue
                perm = permissions.get(pref)
                if perm is None:
                    continue  # 指向不存在权限 = dangling-ref 已报
                perm_target = perm[0].get("targetRef")
                if perm_target != bh_id:
                    add("L2", "consistency-permission", rel_c,
                        key_line(bh, "requiredPermissions"),
                        f"一致性对 P2（M2.requiredPermissions↔M5）: 行为 {bh_id} 的 "
                        f"requiredPermissions「{pref}」存在，但其 targetRef="
                        f"{perm_target} 未回指本行为——权限须双向闭合"
                        f"（依据 M2.requiredPermissions ↔ M5.targetRef，schema.md §14）")

    # P3 M6 活动 roleRef ∈ 流程 roleRefs（活动级角色必须是流程角色集的子集，
    # digest §12.2 P3 / v9 §6.5；ROLE 本身的存在性由 dangling-ref 承载）
    if m6_key:
        for flow_id, flow, rel_c in flows:
            role_refs = {r for r in iter_ref_strings(flow.get("roleRefs") or [])
                         if isinstance(r, str)}
            activities = flow.get("activities")
            if not isinstance(activities, list):
                continue
            for act in activities:
                if not isinstance(act, dict):
                    continue
                for rref in iter_ref_strings(act.get("roleRef") or []):
                    if not isinstance(rref, str) or rref in role_refs:
                        continue
                    add("L2", "consistency-flow-role", rel_c, key_line(act, "roleRef"),
                        f"一致性对 P3（M6 活动 roleRef∈流程 roleRefs）: 流程 {flow_id} "
                        f"活动 {act.get('activityId', '?')} 的 roleRef「{rref}」不在"
                        f"流程 roleRefs {sorted(role_refs)} 内"
                        f"（依据 M6.roleRef ⊆ M6.roleRefs，schema.md §14）")

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
