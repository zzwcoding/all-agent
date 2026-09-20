#!/usr/bin/env python3
"""app_pack_gen.py —— F9 应用生成器（票 35，PRD 决策 2 生成物侧）。

本体域 → 导出开发包（交接给编码 agent 的轻形态）→ exports/devkit/<域>/，
MD+JSON 双载体。生成=确定性装配非创作：输入=域目录 + 技术架构约束/开发指导书
（fixtures/app-pack-gen/inputs 固定输入，合成中性文本）+ 可选开放提案开关；
装配逻辑零 LLM（YAML 机读 + docs/proposals frontmatter 扫描），零时间戳——
输出不含任何日期/时间形态 token，同域任意机器重生成字节一致。

开发包四节（票 35 设计裁决，每域）：
  ①数据字典——解析域内 M1 YAML：逐聚合根属性/类型/约束（unique/targetAggregate/
    enumValues/dictionaryRef/refRules）/不变量，附聚合关联清单；
  ②口径四件套——从域 M7 query_reports 逐口径出发，每口径一卡（CORE 八问常量表
    同款思路）：问题样例=QR name、命中 ID 集=QR+behaviorRef+objectRefs+关联 M3
    规则（behavior.appliedRules ∪ reusedBy ∪ 承载对象关联规则=ownerEntity 落在
    承载对象上的行为的 appliedRules）、口径要点=规则 expression/narrative 摘录。
    与 CORE 八问的同源（core 命中 ⊆ 对应卡片 hitIds）由 fixtures/app-pack-gen
    AC1 探针机核（跑 semantic_service_core 子进程对账）——生成器本体零子进程
    耦合：core/graph_index 是同源裁决参照面，不进装配数据流，避免 core 解析
    行为演进倒逼开发包再生成；
  ③行为与规则清单——M2/M3 全量（id/name/类型/注源列；注源=模型文件全行注释里
    的 [R<n>·…] 源标签，逐元素挂靠其 id 行，照 bohai 注源纪律机读化）；
  ④开放疑点——扫 docs/proposals/PROP-*.md frontmatter，status=open 且
    target.element 含本域前缀（域名大写形态作 ID 词元）的逐条列，无则
    "无开放提案"；--no-proposals 可关（可选开关）。

声明模型集：M1/M2/M3/M7——域缺任一声明模型文件 → stderr 报「缺声明模型 Mx」
退出 2，不产出残包（specs/modules.md 边界规则 5 的生成器侧首证）。模型文件
model_type 不符 / 引用失效（behaviorRef/objectRef/appliedRules/reusedBy/
targetAggregate 指空）同样拒绝——不硬编不产残包。

头部人审状态纪律（PRD 决策 2 生成物侧落位）：status: 待Owner人审（生成物禁手
改，可再生）。入库副本 exports/devkit/bohai/ 是派生物禁手改，防陈旧断言 =
--check 模式（现场重生成与入库逐字节比对，照 mcp_manifest_gen 手法）。

CLI: python3 tools/app_pack_gen.py <域目录> [--out <目录>] [--check <路径>]
     [--no-proposals] [--inputs-dir <目录>] [--proposals-dir <目录>]
  缺省        MD 打到 stdout（人读面预览）
  --out <目录> 写 devkit.md + devkit.json 双文件（UTF-8；stdout 保持安静）
  --check <路径> 现场重生成并与给定入库副本（devkit.md 文件或其目录）逐字节
               比对 MD+JSON：一致退出 0；不一致/副本缺失退出 1（防陈旧载体）
退出码：0 成功/一致；1 --check 不一致或副本缺失；2 配置错误（域目录不存在/
缺 manifest/缺声明模型/model_type 不符/引用失效/固定输入或提案池缺失/解析失败
——拒收残包）。

依赖：Python3 stdlib + PyYAML（safe 装载）。
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

STATUS_REVIEW = "待Owner人审（生成物禁手改，可再生）"
GENERATOR = "tools/app_pack_gen.py"

# 声明模型集（票 35 设计裁决：缺了报错不硬编——边界规则 5 生成器侧首证）
DECLARED_MODELS = (
    ("M1", "m1-object-model.yaml", "OBJECT", "对象模型"),
    ("M2", "m2-behavior-model.yaml", "BEHAVIOR", "行为模型"),
    ("M3", "m3-rule-model.yaml", "RULE", "规则模型"),
    ("M7", "m7-report-model.yaml", "REPORT", "查询统计与报表模型"),
)

# 固定输入（出厂集固定输入（合成）；文件头自带同款声明行）
FIXED_INPUT_FILES = (("techConstraints", "tech-constraints.md", "技术架构约束"),
                     ("devGuide", "dev-guide.md", "开发指导书"))
DEFAULT_INPUTS_DIR = REPO_ROOT / "fixtures" / "app-pack-gen" / "inputs"
DEFAULT_PROPOSALS_DIR = REPO_ROOT / "docs" / "proposals"

MD_NAME = "devkit.md"
JSON_NAME = "devkit.json"

SECTION_HEADS = ("## 一、数据字典", "## 二、口径四件套", "## 三、行为与规则清单",
                 "## 四、开放疑点")

# 注源抽取：全行注释里的 [R<n>·…] 源标签 → 挂靠其后第一个 id 行元素。
# 同行尾注（属性行 # [R5·…]）不收——挂靠粒度是元素 id 行。
SOURCE_TAG_RE = re.compile(r"\[(R\d[^[\]]*)\]")
ID_LINE_RE = re.compile(r"^\s*-\s+id:\s*([A-Za-z][A-Za-z0-9-]*)\s*(?:#.*)?$")
MODEL_TYPE_LINE_RE = re.compile(r"^model_type:\s*\S+")
DOMAIN_PREFIX_RE = None  # 按域动态编译：(^|-)<域名大写>(-|$)


class ConfigError(ValueError):
    """域/固定输入/提案池配置不可用（退出码 2，拒收残包）。"""


# ---------- 读取 ----------


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"{path} 不存在") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ConfigError(f"{path} 不是合法 JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path} 顶层必须是映射")
    return data


def load_yaml_doc(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} YAML 解析失败: {exc}") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(f"{path} 无法读取: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path} 顶层必须是映射（模型文件约定）")
    return data


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"{path} 不存在") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(f"{path} 无法读取: {exc}") from exc


def extract_source_notes(text: str) -> dict:
    """全行注释 [R<n>·…] 源标签 → 元素 id 挂靠表（model_type 行起扫，同 id 取先）。

    bohai 注源纪律的机读化：块注释 `# [R5·A.1 井档案…]` 紧邻 `- id: AGG-…`
    之前 → 记为该元素注源；无标签的注释行（如文件尾说明）不入账。
    """
    notes: dict[str, str] = {}
    pending: list[str] = []
    started = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if not started:
            if MODEL_TYPE_LINE_RE.match(stripped):
                started = True
            continue
        if stripped.startswith("#"):
            pending.extend(m.group(1).strip()
                           for m in SOURCE_TAG_RE.finditer(stripped))
            continue
        m = ID_LINE_RE.match(raw.rstrip())
        if m and pending:
            eid = m.group(1)
            if eid not in notes:  # 同 ID 取先出现（同 graph_index 手法）
                notes[eid] = "；".join(dict.fromkeys(pending))
            pending = []
    return notes


def source_label(path: Path) -> str:
    """generatedFrom.source：仓内取仓根相对 posix 路径，仓外取绝对路径。"""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _req_list(doc: dict, key: str, model: str, path: Path) -> list:
    value = doc.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError(f"{path} 的 {key}（{model}）必须是列表")
    return [v for v in value if isinstance(v, dict)]


# ---------- 域装载与引用核对（缺声明模型/引用失效 → 拒收残包） ----------


def load_domain(target: Path) -> dict:
    target = target.resolve()
    if not target.is_dir():
        raise ConfigError(f"域目录不存在: {target}")
    manifest_path = target / "manifest.json"
    if not manifest_path.is_file():
        raise ConfigError(f"{target} 不是域目录（缺 manifest.json）——"
                          f"本生成器按单域出包，请传域目录")
    manifest = load_json(manifest_path)
    domain = manifest.get("domain") or target.name
    models, declared = {}, []
    for model_id, filename, model_type, cname in DECLARED_MODELS:
        path = target / filename
        if not path.is_file():
            raise ConfigError(
                f"缺声明模型 {model_id}: {path} 不存在"
                f"（生成器声明集 {'/'.join(m for m, _f, _t, _c in DECLARED_MODELS)}"
                f"；边界规则 5：缺了报错不硬编，拒绝产出残包）")
        doc = load_yaml_doc(path)
        if doc.get("model_type") != model_type:
            raise ConfigError(
                f"{path} model_type={doc.get('model_type')!r}，"
                f"声明模型 {model_id} 须为 {model_type}")
        models[model_id] = doc
        declared.append({"model": model_id, "file": filename,
                         "modelType": model_type, "name": cname,
                         "version": doc.get("version", "")})
    m1, m2, m3, m7 = (models["M1"], models["M2"], models["M3"], models["M7"])
    domain_data = {
        "name": domain,
        "label": manifest.get("label", ""),
        "profile": manifest.get("profile", ""),
        "sourcePath": source_label(target),
        "m1": m1, "m2": m2, "m3": m3, "m7": m7,
        "aggregates": _req_list(m1, "aggregates", "M1", target / DECLARED_MODELS[0][1]),
        "associations": _req_list(m1, "aggregate_associations", "M1",
                                  target / DECLARED_MODELS[0][1]),
        "behaviors": _req_list(m2, "behaviors", "M2", target / DECLARED_MODELS[1][1]),
        "rules": _req_list(m3, "rules", "M3", target / DECLARED_MODELS[2][1]),
        "queryReports": _req_list(m7, "query_reports", "M7", target / DECLARED_MODELS[3][1]),
        "notes": {mid: extract_source_notes((target / f).read_text(encoding="utf-8"))
                  for mid, f, _t, _c in DECLARED_MODELS},
        "declared": declared,
    }
    _validate_references(domain_data)
    return domain_data


def _validate_references(dd: dict) -> None:
    """引用一致性核对（对照本域已解析元素集；指空即拒——不硬编不产残包）。"""
    agg_ids = [a.get("id") for a in dd["aggregates"] if a.get("id")]
    beh_ids = [b.get("id") for b in dd["behaviors"] if b.get("id")]
    rule_ids = [r.get("id") for r in dd["rules"] if r.get("id")]
    for label, ids in (("M1 aggregates", agg_ids), ("M2 behaviors", beh_ids),
                       ("M3 rules", rule_ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ConfigError(f"{label} 元素 id 重复: {dupes}")
    agg_set, beh_set, rule_set = set(agg_ids), set(beh_ids), set(rule_ids)

    def check(cond_id: str, pool: set, where: str, kind: str) -> None:
        if cond_id not in pool:
            raise ConfigError(f"引用失效: {where} 的 {kind} {cond_id!r} "
                              f"不在本域已解析元素集（不硬编，拒绝出包）")

    for a in dd["aggregates"]:
        for attr in a.get("attributes") or []:
            if isinstance(attr, dict) and attr.get("targetAggregate"):
                check(attr["targetAggregate"], agg_set,
                      a.get("id", "?"), "attributes.targetAggregate")
    for b in dd["behaviors"]:
        if b.get("ownerEntity"):
            check(b["ownerEntity"], agg_set, b.get("id", "?"), "ownerEntity")
        for rid in b.get("appliedRules") or []:
            check(rid, rule_set, b.get("id", "?"), "appliedRules")
    for r in dd["rules"]:
        for bid in r.get("reusedBy") or []:
            check(bid, beh_set, r.get("id", "?"), "reusedBy")
    for qr in dd["queryReports"]:
        if qr.get("behaviorRef"):
            check(qr["behaviorRef"], beh_set, qr.get("id", "?"), "behaviorRef")
        for src in qr.get("sourceObjects") or []:
            if isinstance(src, dict) and src.get("objectRef"):
                check(src["objectRef"], agg_set, qr.get("id", "?"),
                      "sourceObjects.objectRef")


# ---------- 四节装配（确定性：YAML 序 + id 序，零时间戳） ----------


def _rule_point(rule: dict) -> dict:
    if rule.get("expression"):
        return {"expression": rule["expression"]}
    if rule.get("narrative"):
        return {"narrative": rule["narrative"]}
    return {}


def build_data_dictionary(dd: dict) -> dict:
    """①数据字典：逐聚合根属性/类型/约束/字典引用 + 不变量 + 聚合关联。"""
    notes = dd["notes"]["M1"]
    aggregates = []
    for a in dd["aggregates"]:
        attrs = []
        for attr in a.get("attributes") or []:
            if not isinstance(attr, dict):
                continue
            row = {"name": attr.get("name"), "label": attr.get("label"),
                   "type": attr.get("type")}
            cons = {}
            if attr.get("unique"):
                cons["unique"] = True
            if attr.get("targetAggregate"):
                cons["targetAggregate"] = attr["targetAggregate"]
            if attr.get("enumValues"):
                cons["enumValues"] = attr["enumValues"]
            if attr.get("dictionaryRef"):
                cons["dictionaryRef"] = attr["dictionaryRef"]
            if attr.get("refRules"):
                cons["refRules"] = [
                    {"name": rr.get("name"), "expression": rr.get("expression"),
                     "enforcedAt": rr.get("enforcedAt")}
                    for rr in attr["refRules"] if isinstance(rr, dict)]
            if cons:
                row["constraints"] = cons
            attrs.append(row)
        agg = {"id": a.get("id"), "name": a.get("name"), "alias": a.get("alias"),
               "aggregateType": a.get("aggregateType"),
               "description": a.get("description", ""),
               "sourceNote": notes.get(a.get("id"), ""),
               "attributes": attrs}
        if a.get("lifecycle"):
            agg["lifecycle"] = a["lifecycle"]
        if a.get("invariants"):
            agg["invariants"] = [
                {"name": iv.get("name"), "expression": iv.get("expression"),
                 "enforcedAt": iv.get("enforcedAt")}
                for iv in a["invariants"] if isinstance(iv, dict)]
        aggregates.append(agg)
    associations = [
        {"id": x.get("id"), "sourceAggregate": x.get("sourceAggregate"),
         "targetAggregate": x.get("targetAggregate"),
         "associationType": x.get("associationType"),
         "sourceRole": x.get("sourceRole"), "targetRole": x.get("targetRole"),
         "cardinality": x.get("cardinality"),
         "referenceField": x.get("referenceField")}
        for x in dd["associations"]]
    return {"aggregates": aggregates, "associations": associations}


def build_calibers(dd: dict) -> list:
    """②口径四件套：M7 逐口径一卡（问题样例/行为/承载/关联规则/命中 ID 集）。"""
    notes_m7 = dd["notes"]["M7"]
    notes_m2 = dd["notes"]["M2"]
    notes_m3 = dd["notes"]["M3"]
    beh_by_id = {b.get("id"): b for b in dd["behaviors"]}
    rule_by_id = {r.get("id"): r for r in dd["rules"]}
    agg_by_id = {a.get("id"): a for a in dd["aggregates"]}
    # 承载对象关联规则：ownerEntity 落在该对象上的行为 → 其 appliedRules
    owner_rules: dict[str, list[str]] = {}
    for b in dd["behaviors"]:
        for rid in b.get("appliedRules") or []:
            owner_rules.setdefault(b.get("ownerEntity"), []).append(rid)

    cards = []
    for qr in dd["queryReports"]:
        behavior = beh_by_id[qr["behaviorRef"]]
        object_ids = [s.get("objectRef") for s in qr.get("sourceObjects") or []
                      if isinstance(s, dict) and s.get("objectRef")]
        rules, seen = [], set()

        def add_rule(rid: str, via: str) -> None:
            if rid in seen:
                return
            seen.add(rid)
            rule = rule_by_id.get(rid, {})
            rules.append({"id": rid, "name": rule.get("name", rid),
                          "type": rule.get("ruleType", ""),
                          "point": _rule_point(rule), "via": via})

        for rid in behavior.get("appliedRules") or []:
            add_rule(rid, f"behavior.appliedRules({behavior.get('id')})")
        for r in dd["rules"]:
            if behavior.get("id") in (r.get("reusedBy") or []):
                add_rule(r.get("id"), f"reusedBy({behavior.get('id')})")
        for oid in object_ids:
            for rid in owner_rules.get(oid, []):
                add_rule(rid, f"ownerObjectBehaviors({oid})")

        sources = []
        for s in qr.get("sourceObjects") or []:
            if not (isinstance(s, dict) and s.get("objectRef")):
                continue
            row = {"objectRef": s["objectRef"], "alias": s.get("alias", ""),
                   "primary": bool(s.get("primary")),
                   "name": agg_by_id.get(s["objectRef"], {}).get("name",
                                                                 s["objectRef"])}
            sources.append(row)
        hit_ids = [qr.get("id"), qr.get("behaviorRef"), *object_ids]
        hit_ids += [r["id"] for r in rules]
        cards.append({
            "id": qr.get("id"),
            "name": qr.get("name"),
            "alias": qr.get("alias", ""),
            "objectType": qr.get("objectType", ""),
            "questionSample": qr.get("name", ""),
            "sourceNote": notes_m7.get(qr.get("id"), ""),
            "description": qr.get("description", ""),
            "behavior": {"id": behavior.get("id"),
                         "name": behavior.get("name", ""),
                         "type": behavior.get("behaviorType", ""),
                         "triggerType": behavior.get("triggerType", ""),
                         "ownerEntity": behavior.get("ownerEntity", ""),
                         "sourceNote": notes_m2.get(behavior.get("id"), "")},
            "sourceObjects": sources,
            "parameters": [
                {"name": p.get("name"), "label": p.get("label"),
                 "dataType": p.get("dataType"), "required": bool(p.get("required")),
                 "allowedOperators": p.get("allowedOperators", [])}
                for p in qr.get("parameters") or [] if isinstance(p, dict)],
            "conditions": [
                {k: c.get(k) for k in
                 ("conditionId", "leftExpression", "operator", "parameterRef")}
                for c in qr.get("conditions") or [] if isinstance(c, dict)],
            "resultColumns": [
                {k: col.get(k) for k in
                 ("name", "label", "dataType", "sourceExpression",
                  "aggregateFunction") if col.get(k) is not None}
                for col in qr.get("resultColumns") or [] if isinstance(col, dict)],
            "rules": rules,
            "hitIds": hit_ids,
        })
    return cards


def build_behavior_rule_inventory(dd: dict) -> dict:
    """③行为与规则清单：M2/M3 全量（id/name/类型/注源列）。"""
    notes_m2 = dd["notes"]["M2"]
    notes_m3 = dd["notes"]["M3"]
    behaviors = [
        {"id": b.get("id"), "name": b.get("name"),
         "behaviorType": b.get("behaviorType", ""),
         "triggerType": b.get("triggerType", ""),
         "ownerEntity": b.get("ownerEntity", ""),
         "preconditions": [str(p) for p in b.get("preconditions") or []],
         "postconditions": [p for p in b.get("postconditions") or []
                            if isinstance(p, dict)],
         "appliedRules": list(b.get("appliedRules") or []),
         "requiredPermissions": list(b.get("requiredPermissions") or []),
         "sourceNote": notes_m2.get(b.get("id"), "")}
        for b in dd["behaviors"]]
    rules = [
        {"id": r.get("id"), "name": r.get("name"),
         "ruleType": r.get("ruleType", ""),
         "description": r.get("description", ""),
         "expression": r.get("expression", ""),
         "narrative": r.get("narrative", ""),
         "reusedBy": list(r.get("reusedBy") or []),
         "sourceNote": notes_m3.get(r.get("id"), "")}
        for r in dd["rules"]]
    return {"behaviors": behaviors, "rules": rules}


def build_open_proposals(proposals_dir: Path, domain: str) -> dict:
    """④开放疑点：docs/proposals PROP-*.md frontmatter → 指向本域的 open 提案。

    判定=status=open 且 target.element 含本域前缀（域名大写形态作 ID 词元，
    如域 bohai ↔ RULE-BOHAI-020）；frontmatter 不可解析=配置错误（不静默吞）。
    """
    prefix_re = re.compile(rf"(?i)(^|-){re.escape(domain.upper())}(-|$)")
    items = []
    for path in sorted(proposals_dir.glob("PROP-*.md")):
        text = read_text_file(path)
        if not text.startswith("---"):
            raise ConfigError(f"{path} 缺 frontmatter（提案文件约定）")
        block, sep, _rest = text[3:].partition("---")
        if not sep:
            raise ConfigError(f"{path} frontmatter 未闭合")
        try:
            meta = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            raise ConfigError(f"{path} frontmatter YAML 解析失败: {exc}") from exc
        if not isinstance(meta, dict):
            raise ConfigError(f"{path} frontmatter 顶层必须是映射")
        status = meta.get("status")
        target = meta.get("target") if isinstance(meta.get("target"), dict) else {}
        element = target.get("element")
        if status != "open" or not element:
            continue  # status 非 open / 无 target.element → 不归属任何域
        if not prefix_re.search(str(element)):
            continue  # 非本域
        signal = meta.get("source-signal") \
            if isinstance(meta.get("source-signal"), dict) else {}
        items.append({"id": meta.get("id", path.stem), "title": meta.get("title", ""),
                      "change": meta.get("change", ""),
                      "targetModel": target.get("model", ""),
                      "targetElement": element,
                      "signalKind": signal.get("kind", ""),
                      "signalRef": signal.get("ref", ""),
                      "path": source_label(path)})
    return {"enabled": True, "scannedDir": source_label(proposals_dir),
            "items": items}


# ---------- 固定输入 ----------


def load_fixed_inputs(inputs_dir: Path) -> dict:
    inputs = {}
    for key, filename, cname in FIXED_INPUT_FILES:
        path = inputs_dir / filename
        try:
            inputs[key] = {"file": filename, "name": cname,
                           "path": source_label(path),
                           "text": read_text_file(path)}
        except ConfigError as exc:
            raise ConfigError(f"固定输入缺失（{cname}）: {exc}") from exc
    return inputs


# ---------- 包组装与渲染 ----------


def build_package(domain_dir: Path, *, inputs_dir: Path = None,
                  proposals_dir: Path = None,
                  include_proposals: bool = True) -> dict:
    """纯函数式组装：同输入同输出，零副作用（幂等/防陈旧的根基）。"""
    dd = load_domain(domain_dir)
    inputs = load_fixed_inputs(inputs_dir or DEFAULT_INPUTS_DIR)
    if include_proposals:
        pdir = proposals_dir or DEFAULT_PROPOSALS_DIR
        if not pdir.is_dir():
            raise ConfigError(f"提案池目录不存在: {pdir}")
        open_proposals = build_open_proposals(pdir, dd["name"])
    else:
        open_proposals = {"enabled": False, "scannedDir": "", "items": [],
                          "note": "未启用开放提案扫描（--no-proposals）"}
    return {
        "status": STATUS_REVIEW,
        "domain": {k: dd[k] for k in ("name", "label", "profile", "sourcePath")},
        "declaredModels": dd["declared"],
        "fixedInputs": inputs,
        "dataDictionary": build_data_dictionary(dd),
        "calibers": build_calibers(dd),
        "behaviorRuleInventory": build_behavior_rule_inventory(dd),
        "openProposals": open_proposals,
        "generatedFrom": {
            "generator": GENERATOR,
            "source": dd["sourcePath"],
            "note": "确定性派生物：确定性装配零 LLM 零时间戳，同域重生成字节一致；"
                    "生成物禁手改，防陈旧断言=--check 再制一致（票 35）",
        },
    }


def _md_cell(text) -> str:
    """表格单元格转义：竖线与换行拍平（确定性渲染）。"""
    return str(text if text is not None else "").replace("|", "\\|") \
        .replace("\n", " ").strip()


def render_md(pkg: dict) -> str:
    """开发包 → 人读 MD（四节 + 头部 + 固定输入节，确定性）。"""
    dom = pkg["domain"]
    lines = []
    ap = lines.append

    ap(f"# {dom['label'] or dom['name']} 开发包（devkit · {dom['name']}）")
    ap("")
    ap(f"status: {STATUS_REVIEW}")
    ap("")
    ap(f"- 生成器: {GENERATOR}（确定性装配：YAML 机读 + 提案 frontmatter 扫描，"
       f"零 LLM 零时间戳）")
    ap(f"- 本体来源: {dom['sourcePath']}（profile={dom['profile']}）")
    ap("- 声明模型: " + " / ".join(
        f"{m['model']} {m['name']}" for m in pkg["declaredModels"]))
    ap("- 固定输入: " + "、".join(
        f"{i['path']}（出厂集固定输入（合成））"
        for i in pkg["fixedInputs"].values()))
    if pkg["openProposals"]["enabled"]:
        ap(f"- 开放提案开关: 启用（{pkg['openProposals']['scannedDir']}）")
    else:
        ap("- 开放提案开关: 未启用（--no-proposals）")
    ap(f"- 防陈旧: python3 {GENERATOR} {dom['sourcePath']} "
       f"--check exports/devkit/{dom['name']}/{MD_NAME}")
    ap("")
    for key, cname in (("techConstraints", "技术架构约束"),
                       ("devGuide", "开发指导书")):
        ap(f"## {cname}（固定输入，原样装配）")
        ap("")
        ap(pkg["fixedInputs"][key]["text"].rstrip())
        ap("")
    ap("---")
    ap("")

    # ①数据字典
    ap(SECTION_HEADS[0] + "（M1 对象模型）")
    ap("")
    dd = pkg["dataDictionary"]
    if not dd["aggregates"]:
        ap("（本域 M1 无聚合根）")
        ap("")
    for a in dd["aggregates"]:
        title = f"### {a['id']} {a['name']}"
        if a.get("alias"):
            title += f"（{a['alias']}）"
        ap(title)
        ap("")
        if a.get("sourceNote"):
            ap(f"- 注源: {a['sourceNote']}")
        ap(f"- {a.get('aggregateType', '')}；描述: {_md_cell(a.get('description'))}")
        if a.get("lifecycle"):
            ap("- lifecycle: " + "/".join(a["lifecycle"]))
        ap("")
        ap("| 属性 | 标签 | 类型 | 约束与字典 |")
        ap("|---|---|---|---|")
        for attr in a["attributes"]:
            cons = attr.get("constraints") or {}
            cells = []
            if cons.get("unique"):
                cells.append("unique")
            if cons.get("targetAggregate"):
                cells.append(f"引用→{cons['targetAggregate']}")
            if cons.get("enumValues"):
                cells.append("字典值集: " + "/".join(cons["enumValues"]))
            if cons.get("dictionaryRef"):
                cells.append(f"字典: {cons['dictionaryRef']}")
            for rr in cons.get("refRules") or []:
                cells.append(f"值域[{rr.get('name')}]: {rr.get('expression')}")
            ap(f"| {_md_cell(attr.get('name'))} | {_md_cell(attr.get('label'))} "
               f"| {_md_cell(attr.get('type'))} | {_md_cell('；'.join(cells))} |")
        ap("")
        for iv in a.get("invariants") or []:
            ap(f"- 不变量 {iv.get('name')}: {_md_cell(iv.get('expression'))}"
               f"（enforcedAt={iv.get('enforcedAt')}）")
        if a.get("invariants"):
            ap("")
    if dd["associations"]:
        ap("聚合关联（aggregate_associations）:")
        ap("")
        ap("| 关联 | 源 → 靶 | 类型 | 基数 | 引用字段 | 角色 |")
        ap("|---|---|---|---|---|---|")
        for x in dd["associations"]:
            ap(f"| {x['id']} | {x['sourceAggregate']} → {x['targetAggregate']} "
               f"| {x['associationType']} | {x['cardinality']} "
               f"| {_md_cell(x['referenceField'])} "
               f"| {_md_cell(x['sourceRole'])}→{_md_cell(x['targetRole'])} |")
        ap("")

    # ②口径四件套
    ap(SECTION_HEADS[1] + "（M7 查询出口 × M2 行为 × M3 规则 × M1 承载）")
    ap("")
    if not pkg["calibers"]:
        ap("（本域 M7 无查询出口）")
        ap("")
    for c in pkg["calibers"]:
        ap(f"### 口径 {c['id']} · {c['name']}")
        ap("")
        if c.get("sourceNote"):
            ap(f"- 注源: {c['sourceNote']}")
        ap(f"- 问题样例: {c['questionSample']}")
        ap(f"- 查询出口: {c['id']}（{c['objectType']}）")
        b = c["behavior"]
        ap(f"- 行为: {b['id']} {b['name']}（{b['type']}/{b['triggerType']}，"
           f"ownerEntity={b['ownerEntity']}）")
        owners = "、".join(
            f"{s['objectRef']} {s['name']}" + ("（主）" if s["primary"] else "")
            for s in c["sourceObjects"])
        ap(f"- 承载对象: {owners or '—'}")
        if c["parameters"]:
            ap("- 参数: " + "；".join(
                f"{p['name']}（{_md_cell(p.get('label'))}，{p.get('dataType')}"
                f"{'，必填' if p.get('required') else ''}"
                f"{'，运算符 ' + '/'.join(p.get('allowedOperators') or []) if p.get('allowedOperators') else ''}）"
                for p in c["parameters"]))
        if c["resultColumns"]:
            ap("- 结果列: " + "；".join(
                f"{col['name']}={_md_cell(col.get('label'))}"
                f"（{_md_cell(col.get('sourceExpression'))}"
                f"{'，' + col['aggregateFunction'] if col.get('aggregateFunction') and col['aggregateFunction'] != 'NONE' else ''}）"
                for col in c["resultColumns"]))
        ap("- 命中 ID 集: " + " ".join(c["hitIds"]))
        ap("- 口径要点（关联规则 expression/narrative 摘录）:")
        if not c["rules"]:
            ap("  - （无关联 M3 规则）")
        for r in c["rules"]:
            point = r["point"]
            detail = point.get("expression") or point.get("narrative") or "（无表达式/叙述）"
            ap(f"  - {r['id']} {r['name']}（{r['type']}；via={r['via']}）: "
               f"{_md_cell(detail)}")
        ap("")

    # ③行为与规则清单
    ap(SECTION_HEADS[2] + "（M2/M3 全量，注源=模型文件 [R<n>·…] 注释标签）")
    ap("")
    inv = pkg["behaviorRuleInventory"]
    ap(f"### 行为（M2 · {len(inv['behaviors'])} 条）")
    ap("")
    for b in inv["behaviors"]:
        rules_ref = ",".join(b["appliedRules"]) or "—"
        note = f"— 注源: {b['sourceNote']}" if b["sourceNote"] else ""
        ap(f"- {b['id']} {b['name']} [{b['behaviorType']}/{b['triggerType']}] "
           f"ownerEntity={b['ownerEntity']} appliedRules={rules_ref} {note}".rstrip())
    ap("")
    ap(f"### 规则（M3 · {len(inv['rules'])} 条）")
    ap("")
    for r in inv["rules"]:
        note = f"— 注源: {r['sourceNote']}" if r["sourceNote"] else ""
        point = r.get("expression") or r.get("narrative")
        tail = f"— {_md_cell(point)}" if point else ""
        ap(f"- {r['id']} {r['name']} [{r['ruleType']}] {note} {tail}".rstrip())
    ap("")

    # ④开放疑点
    ap(SECTION_HEADS[1].replace("二、口径四件套", "四、开放疑点")
       + "（docs/proposals 扫描）")
    ap("")
    op = pkg["openProposals"]
    if not op["enabled"]:
        ap("未启用开放提案扫描（--no-proposals）。")
        ap("")
    elif not op["items"]:
        ap("无开放提案。")
        ap("")
    else:
        ap(f"指向本域的 open 提案 {len(op['items'])} 条（裁决与详情看提案原文）:")
        ap("")
        for i in op["items"]:
            ap(f"- {i['id']} {i['title']}［{i['change']} → "
               f"{i['targetModel']}/{i['targetElement']}］（{i['path']}）")
        ap("")
    return "\n".join(lines).rstrip() + "\n"


def render_json(pkg: dict) -> str:
    """开发包 → 机读 JSON（ensure_ascii=False + indent=2 + 尾换行）。"""
    return json.dumps(pkg, ensure_ascii=False, indent=2) + "\n"


# ---------- CLI ----------


def _resolve_check_dir(check_path: Path) -> Path:
    """--check 入参：devkit.md 文件 → 其目录；目录 → 原样。"""
    if check_path.is_file():
        return check_path.parent
    return check_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="F9 应用生成器（票 35；开发包=确定性装配，零 LLM 零时间戳）")
    ap.add_argument("target", help="本体域目录（含 manifest.json，单域出包）")
    ap.add_argument("--out", default=None, metavar="目录",
                    help="写出 devkit.md + devkit.json 双文件（缺省 MD 打 stdout）")
    ap.add_argument("--check", default=None, metavar="入库路径",
                    help="重生成并与入库副本（devkit.md 或其目录）逐字节比对"
                         "（一致 0 / 不一致 1）")
    ap.add_argument("--no-proposals", action="store_true",
                    help="关闭第④节开放提案扫描（可选开关）")
    ap.add_argument("--inputs-dir", default=None, metavar="目录",
                    help="固定输入目录（缺省 fixtures/app-pack-gen/inputs）")
    ap.add_argument("--proposals-dir", default=None, metavar="目录",
                    help="提案池目录（缺省 docs/proposals）")
    args = ap.parse_args(argv)

    try:
        pkg = build_package(
            Path(args.target),
            inputs_dir=Path(args.inputs_dir) if args.inputs_dir else None,
            proposals_dir=(Path(args.proposals_dir)
                           if args.proposals_dir else None),
            include_proposals=not args.no_proposals)
    except ConfigError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2

    if args.check:
        check_dir = _resolve_check_dir(Path(args.check))
        results = []
        for name, fresh in ((MD_NAME, render_md(pkg)),
                            (JSON_NAME, render_json(pkg))):
            stored = check_dir / name
            if not stored.is_file():
                results.append((name, False,
                                f"入库副本不存在: {stored}（生成：--out {check_dir}）"))
                continue
            same = stored.read_text(encoding="utf-8") == fresh
            results.append((name, same, "再制一致" if same else
                            f"与现场重生成有差异（入库副本陈旧或被手改；再制："
                            f"python3 {GENERATOR} {args.target} --out {check_dir}）"))
        if all(same for _n, same, _m in results):
            print(f"再制一致：{check_dir} 的 {MD_NAME}+{JSON_NAME} "
                  f"与现场重生成逐字节一致")
            return 0
        for name, _same, msg in results:
            if "再制一致" not in msg:
                print(f"再制不一致：{name} — {msg}")
        return 1

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / MD_NAME).write_text(render_md(pkg), encoding="utf-8")
        (out_dir / JSON_NAME).write_text(render_json(pkg), encoding="utf-8")
        return 0

    sys.stdout.write(render_md(pkg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
