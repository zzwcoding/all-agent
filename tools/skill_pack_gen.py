#!/usr/bin/env python3
"""skill_pack_gen.py —— F10 Skill 发布器（票 36，PRD F10 生成物侧）。

本体域切片 → 可对话技能包骨架 → exports/skillpkg/<域>/，SKILL.md+skillpack.json
双载体（MD+JSON 双出口，同票 35 手法）。生成=确定性装配非创作：输入=域目录 +
--models 切片声明（显式子集，如 --models M1,M2,M3,M7,GLS）+ ontology/schema
注册表（camp/模型面真源——读 model-registry.json 的 camp 字段与 model-deps.json
的 idPrefixes 前缀表，不 import core）；装配逻辑零 LLM（YAML/JSON 机读），
零时间戳——输出不含任何日期/时间形态 token，同域同声明任意机器重生成字节一致。

技能包三件套（票 36 设计裁决，SKILL.md 单文件三节 + JSON 机读镜像）：
  ①frontmatter+工序路由——frontmatter：name/domain/slice-models/
    citation-prefixes（ID 前缀回答面=model-deps.json idPrefixes 反查声明模型）+
    人审状态；工序路由=问答四步的静态化表述（显式锚定→名称解析→闭包装配→
    可拒答），运行时真源=语义服务检索瀑布，发布物内只是静态化纪律卡；
  ②口径问答卡——M7 query_reports 逐口径一卡（问题样例/命中 ID 集/口径要点），
    装配来源同票 35 口径节（QR+behaviorRef+objectRefs+关联 M3 规则：
    behavior.appliedRules ∪ reusedBy ∪ 承载对象关联规则=ownerEntity 落在承载
    对象上的行为的 appliedRules）；与 CORE 八问的同源（core 命中 ⊆ 卡 hitIds）
    由 fixtures/skill-pack-gen AC1 探针机核（跑 semantic_service_core 子进程
    对账）——生成器本体零子进程耦合；口径卡装配须 M1/M2/M3/M7 齐备（M7 在
    切片而伴模型缺 → 报错不产残卡），M7 未声明 → 如实注记无口径卡（L0 示例
    切片 M1,M3,GLS 仍可出包）；
  ③引用纪律与拒答边界——ID 引用格式（真实 ID+「本回答引用的元素 ID」清单节
    双向一致）+camp 面外声明（registry camp≠business-core 的模型前缀，如
    SCR-/MU build-contract——先阵营后存在性）+切片外 business-core 前缀声明
    +禁用词（GLS status 含「禁用」的 term）+可拒答声明。

切片声明纪律（--models，检索面纪律的生成器侧延伸）：
  - 每个声明模型必须在 model-registry.json models 内（未知 → 报错）；
  - camp 必须=business-core（GLS 亦属 business-core）：声明 build-contract/
    integration 模型（如 MU）→ 报「声明含非 business-core 阵营模型」——建造
    契约面不进对话切片；camp 判定在文件存在性核对之前（先阵营后存在性，
    同 core 瀑布 §0/§5）；
  - 域缺声明模型文件 → 报「缺声明模型 Mx」退出 2（边界规则 5 同款，不硬编
    不产残包）；model_type 与注册表不符/口径卡装配链引用失效（behaviorRef/
    objectRef/appliedRules/reusedBy/ownerEntity/GLS relatedObjectRefs 指空）
    同拒。校验面=口径卡装配链与术语关联，不及其余（对比 app_pack_gen 全域
    校验：本生成器只消费装配链触到的引用）。

头部人审状态纪律（同票 35，PRD 决策 2 生成物侧落位）：
status: 待Owner人审（生成物禁手改，可再生）。入库副本 exports/skillpkg/bohai/
是派生物禁手改，防陈旧断言=--check 模式（现场重生成与入库逐字节比对）。

CLI: python3 tools/skill_pack_gen.py <域目录> --models M1,M2,M3,M7,GLS
     [--out <目录>] [--check <入库SKILL.md>] [--schema-dir <目录>]
  缺省        MD 打到 stdout（人读面预览）
  --out <目录> 写 SKILL.md + skillpack.json 双文件（UTF-8；stdout 保持安静）
  --check <路径> 现场重生成并与给定入库副本（SKILL.md 文件或其目录）逐字节
               比对 MD+JSON：一致退出 0；不一致/副本缺失退出 1（防陈旧载体）
  --schema-dir <目录> schema 目录（缺省按域目录自动定位 <域>/schema 或
               <域>/../schema；tempfile 合成域用本参显式注入）
退出码：0 成功/一致；1 --check 不一致或副本缺失；2 配置错误（域目录不存在/
缺 manifest/缺 schema/切片声明缺失或空/未知声明模型/非 business-core 阵营/
缺声明模型/model_type 不符/口径装配缺伴模型/引用失效——拒收残包）。

依赖：Python3 stdlib + PyYAML（safe 装载）。零 LLM，全路径确定性。
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

STATUS_REVIEW = "待Owner人审（生成物禁手改，可再生）"
GENERATOR = "tools/skill_pack_gen.py"

MD_NAME = "SKILL.md"
JSON_NAME = "skillpack.json"

SECTION_HEADS = ("## 一、工序路由（问答四步·静态化）",
                 "## 二、口径问答卡（M7 逐口径·与语义服务 CORE 同源）",
                 "## 三、引用纪律与拒答边界")

# 口径卡装配四模型（同票 35 口径节装配来源：M7 出口 × M2 行为 × M3 规则 × M1 承载）
CALIBER_QUARTET = ("M1", "M2", "M3", "M7")
GLOSSARY_MODEL = "GLS"

# 工序路由四步（静态化表述常量；运行时真源=语义服务检索瀑布）
ROUTING_NOTE = ("问答纪律的静态化表述：检索瀑布运行时真源见语义服务"
                "（skills/semantic-service）；成稿润色归人审后的使用方，"
                "本包只供确定性骨架。")
ROUTING_STEPS = (
    ("①", "显式锚定",
     "问句带 @ID 时按前缀定模型定阵营（先阵营后存在性）：business-core 面内 →"
     " 存在性确认并 --impact 反向收名下行为（ownerEntity 直挂与经子对象挂靠两类）；"
     "camp≠business-core → 面外拒答，不返回该元素任何细节。"),
    ("②", "名称解析",
     "无锚定/锚定失败降级：候选词对 name/alias/属性标签/术语 term+alias 确定性"
     "分层匹配（全等→字段⊆候选词→候选词⊆字段→头部同前缀），不猜不模糊；"
     "多义列候选请锚定修饰词，不擅自合并。"),
    ("③", "闭包装配",
     "命中元素沿 relatedObjectRefs/impact 反向装配证据集（承载/行为/规则/查询"
     "出口/术语），装配指令可复现；术语命中沿关联对象再收承载规则。"),
    ("④", "可拒答",
     "面外/仓内没有/禁用词三分支：缺件分层说明（查询层/对象字段层/行为规则层）"
     "+近邻指路；禁用词给替代口径真实 ID；业务口径缺口走提案流程（进仓走 MR +"
     " 语义 CI），本技能只读，不代填口径。"),
)

ID_CITATION_FORMAT = (
    "回答必带元素 ID 引用（前缀形态真实 ID，如 AGG-BOHAI-002），逐条可经"
    " `python3 tools/graph_index.py <域> --query <ID> --json` 复核；成稿须含"
    "「本回答引用的元素 ID」清单节，与正文 ID token 双向一致"
    "（tools/check_citations.py 检具）。")
REFUSAL_DECLARATION = (
    "可拒答声明：仓内没有就说明缺什么，绝不编造；写意图一律回「走提案流程」"
    "（进仓走 MR + 语义 CI）；本包只读——运行面语义消费，不做本体写入。")
CALIBER_NOTE_EMPTY = ("未声明 M7——无口径问答卡（口径卡命中集须与语义服务 CORE "
                      "同源，装配须 M1/M2/M3/M7 齐备）。")


class ConfigError(ValueError):
    """域/schema/切片声明配置不可用（退出码 2，拒收残包）。"""


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


def source_label(path: Path) -> str:
    """generatedFrom.source：仓内取仓根相对 posix 路径，仓外取绝对路径。"""
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def resolve_schema_dir(target: Path) -> Path | None:
    """schema 目录定位（同 semantic_service_core 手法：<域>/schema 或上级/schema）。"""
    for cand in (target / "schema", target.parent / "schema"):
        if cand.is_dir():
            return cand
    return None


def _req_list(doc: dict, key: str, model: str, path: Path) -> list:
    value = doc.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError(f"{path} 的 {key}（{model}）必须是列表")
    return [v for v in value if isinstance(v, dict)]


# ---------- schema 注册表（camp/模型面真源）与切片声明 ----------


def load_schema(schema_dir: Path) -> tuple[dict, dict]:
    """读 model-registry.json（models：camp/modelType/yamlFile/name）与
    model-deps.json（idPrefixes：前缀→模型）。配置不可用抛 ConfigError。"""
    registry = load_json(schema_dir / "model-registry.json")
    models = registry.get("models")
    if not isinstance(models, dict) or not models:
        raise ConfigError(f"{schema_dir / 'model-registry.json'} 缺 models")
    deps = load_json(schema_dir / "model-deps.json")
    prefixes = deps.get("idPrefixes")
    if not isinstance(prefixes, dict) or not prefixes:
        raise ConfigError(f"{schema_dir / 'model-deps.json'} 缺 idPrefixes")
    return models, prefixes


def parse_model_list(models_arg: str) -> list[str]:
    """--models 逗号分隔 → 去空白去重保序；空声明 = 配置错误（不猜默认集）。"""
    declared = [t.strip() for t in models_arg.split(",") if t.strip()]
    if not declared:
        raise ConfigError("--models 切片声明为空——须显式声明子集"
                          "（如 --models M1,M2,M3,M7,GLS）")
    return list(dict.fromkeys(declared))


def validate_slice(declared: list[str], registry: dict) -> list[dict]:
    """切片声明核对：未知模型/非 business-core 阵营 → 报错（检索面纪律的
    生成器侧延伸）。camp 判定在域文件核对之前（先阵营后存在性）。"""
    metas = []
    for model_id in declared:
        info = registry.get(model_id)
        if not isinstance(info, dict):
            raise ConfigError(
                f"未知声明模型 {model_id}（不在 model-registry.json models；"
                f"声明面=注册表 models 键集 {list(registry)}）")
        camp = info.get("camp")
        if camp != "business-core":
            raise ConfigError(
                f"声明含非 business-core 阵营模型 {model_id}"
                f"（camp={camp}）——检索面纪律：技能包切片只收 business-core"
                f"（GLS 亦属 business-core）；build-contract/integration 由"
                f"建造链路消费方在建造链路消费，不进对话切片")
        metas.append({"model": model_id, "name": info.get("name", model_id),
                      "camp": camp, "modelType": info.get("modelType", ""),
                      "yamlFile": info.get("yamlFile", "")})
    return metas


# ---------- 域装载与引用核对（缺声明模型/引用失效 → 拒收残包） ----------


def load_domain(target: Path, declared: list[str], metas: list[dict]) -> dict:
    target = target.resolve()
    if not target.is_dir():
        raise ConfigError(f"域目录不存在: {target}")
    manifest_path = target / "manifest.json"
    if not manifest_path.is_file():
        raise ConfigError(f"{target} 不是域目录（缺 manifest.json）——"
                          f"本生成器按单域出包，请传域目录")
    manifest = load_json(manifest_path)
    docs: dict[str, dict] = {}
    for model_id, meta in zip(declared, metas):
        path = target / meta["yamlFile"]
        if not path.is_file():
            raise ConfigError(
                f"缺声明模型 {model_id}: {path} 不存在"
                f"（切片声明 {'/'.join(declared)}；边界规则 5：缺了报错"
                f"不硬编，拒绝产出残包）")
        doc = load_yaml_doc(path)
        if doc.get("model_type") != meta["modelType"]:
            raise ConfigError(
                f"{path} model_type={doc.get('model_type')!r}，"
                f"声明模型 {model_id} 须为 {meta['modelType']}"
                f"（model-registry.json）")
        docs[model_id] = doc
    domain_data = {
        "name": manifest.get("domain") or target.name,
        "label": manifest.get("label", ""),
        "profile": manifest.get("profile", ""),
        "sourcePath": source_label(target),
        "docs": docs,
        "aggregates": _req_list(docs.get("M1", {}), "aggregates", "M1",
                                target / "m1-object-model.yaml")
        if "M1" in docs else [],
        "associations": _req_list(docs.get("M1", {}), "aggregate_associations",
                                  "M1", target / "m1-object-model.yaml")
        if "M1" in docs else [],
        "behaviors": _req_list(docs.get("M2", {}), "behaviors", "M2",
                               target / "m2-behavior-model.yaml")
        if "M2" in docs else [],
        "rules": _req_list(docs.get("M3", {}), "rules", "M3",
                           target / "m3-rule-model.yaml")
        if "M3" in docs else [],
        "queryReports": _req_list(docs.get("M7", {}), "query_reports", "M7",
                                  target / "m7-report-model.yaml")
        if "M7" in docs else [],
        "terms": _req_list(docs.get("GLS", {}), "terms", "GLS",
                           target / "glossary-model.yaml")
        if "GLS" in docs else [],
    }
    _validate_references(domain_data,
                         {m for m in ("M1", "M2", "M3", "GLS") if m in docs})
    return domain_data


def _dup_check(ids: list, label: str) -> None:
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ConfigError(f"{label} 元素 id 重复: {dupes}")


def _validate_references(dd: dict, loaded: set) -> None:
    """引用一致性核对（对照本域已解析元素集；指空即拒——不硬编不产残包）。
    校验面=口径卡装配链（behaviorRef/objectRef/appliedRules/reusedBy/
    ownerEntity）+ GLS relatedObjectRefs；跨模型引用只对两端都在切片的核对
   （靶模型不在切片=未装载，无从核对——该面由口径卡四模型齐备闸兜住）。"""
    agg_ids = [a.get("id") for a in dd["aggregates"] if a.get("id")]
    beh_ids = [b.get("id") for b in dd["behaviors"] if b.get("id")]
    rule_ids = [r.get("id") for r in dd["rules"] if r.get("id")]
    qr_ids = [q.get("id") for q in dd["queryReports"] if q.get("id")]
    term_ids = [t.get("id") for t in dd["terms"] if t.get("id")]
    _dup_check(agg_ids, "M1 aggregates")
    _dup_check(beh_ids, "M2 behaviors")
    _dup_check(rule_ids, "M3 rules")
    _dup_check(qr_ids, "M7 query_reports")
    _dup_check(term_ids, "GLS terms")
    agg_set, beh_set, rule_set = set(agg_ids), set(beh_ids), set(rule_ids)
    has_m1, has_m2, has_m3, has_gls = (
        m in loaded for m in ("M1", "M2", "M3", "GLS"))

    def check(cond_id: str, pool: set, where: str, kind: str) -> None:
        if cond_id not in pool:
            raise ConfigError(f"引用失效: {where} 的 {kind} {cond_id!r} "
                              f"不在本域已解析元素集（不硬编，拒绝出包）")

    for b in dd["behaviors"]:
        if b.get("ownerEntity") and has_m1:
            check(b["ownerEntity"], agg_set, b.get("id", "?"), "ownerEntity")
        if has_m3:
            for rid in b.get("appliedRules") or []:
                check(rid, rule_set, b.get("id", "?"), "appliedRules")
    if has_m2:
        for r in dd["rules"]:
            for bid in r.get("reusedBy") or []:
                check(bid, beh_set, r.get("id", "?"), "reusedBy")
    for qr in dd["queryReports"]:
        if qr.get("behaviorRef") and has_m2:
            check(qr["behaviorRef"], beh_set, qr.get("id", "?"),
                  "behaviorRef")
        if has_m1:
            for src in qr.get("sourceObjects") or []:
                if isinstance(src, dict) and src.get("objectRef"):
                    check(src["objectRef"], agg_set, qr.get("id", "?"),
                          "sourceObjects.objectRef")
    if has_m1 and has_gls:
        for t in dd["terms"]:
            for oid in t.get("relatedObjectRefs") or []:
                check(oid, agg_set, t.get("id", "?"), "relatedObjectRefs")


# ---------- 三件套装配（确定性：YAML 序 + id 序，零时间戳） ----------


def _rule_point(rule: dict) -> dict:
    if rule.get("expression"):
        return {"expression": rule["expression"]}
    if rule.get("narrative"):
        return {"narrative": rule["narrative"]}
    return {}


def build_calibers(dd: dict) -> list:
    """②口径问答卡：M7 逐口径一卡（问题样例/命中 ID 集/口径要点）——
    装配来源同票 35 口径节：hitIds=QR+behaviorRef+objectRefs+关联 M3 规则
    （behavior.appliedRules ∪ reusedBy ∪ 承载对象关联规则），每条规则带
    via 传播依据。"""
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

        hit_ids = [qr.get("id"), qr.get("behaviorRef"), *object_ids]
        hit_ids += [r["id"] for r in rules]
        cards.append({
            "id": qr.get("id"),
            "name": qr.get("name"),
            "alias": qr.get("alias", ""),
            "objectType": qr.get("objectType", ""),
            "questionSample": qr.get("name", ""),
            "description": qr.get("description", ""),
            "behavior": {"id": behavior.get("id"),
                         "name": behavior.get("name", ""),
                         "type": behavior.get("behaviorType", ""),
                         "ownerEntity": behavior.get("ownerEntity", "")},
            "sourceObjects": [
                {"objectRef": s["objectRef"], "alias": s.get("alias", ""),
                 "primary": bool(s.get("primary")),
                 "name": agg_by_id.get(s["objectRef"], {}).get(
                     "name", s["objectRef"])}
                for s in qr.get("sourceObjects") or []
                if isinstance(s, dict) and s.get("objectRef")],
            "parameters": [
                {"name": p.get("name"), "label": p.get("label"),
                 "dataType": p.get("dataType"), "required": bool(p.get("required"))}
                for p in qr.get("parameters") or [] if isinstance(p, dict)],
            "rules": rules,
            "hitIds": hit_ids,
        })
    return cards


def build_glossary(dd: dict) -> dict:
    """GLS 术语面：term 全账（id/term/aliases/status/termType/definition/
    relatedObjectRefs）+ 禁用词子集（status 含「禁用」，同 core 禁用词表口径
    ——GLS 文件是唯一真源，本生成器与 core 是两个读者）。"""
    terms = [
        {"id": t.get("id"), "term": t.get("term"),
         "aliases": t.get("aliases") if isinstance(t.get("aliases"), list)
         else [],
         "status": t.get("status") or "", "termType": t.get("termType") or "",
         "definition": t.get("definition") or "",
         "relatedObjectRefs": t.get("relatedObjectRefs")
         if isinstance(t.get("relatedObjectRefs"), list) else []}
        for t in dd["terms"]]
    banned = [{"id": t["id"], "term": t["term"], "aliases": t["aliases"],
               "status": t["status"]}
              for t in terms if "禁用" in t["status"]]
    return {"declared": GLOSSARY_MODEL in dd["docs"], "terms": terms,
            "bannedTerms": banned}


def build_slice(declared: list[str], metas: list[dict],
                prefix2model: dict) -> dict:
    """切片元数据 + citation-prefixes（ID 前缀回答面=idPrefixes 反查声明模型，
    前缀表序=声明面序，确定性）。"""
    citation_prefixes = [p for p, m in prefix2model.items() if m in declared]
    return {"declared": list(declared),
            "models": [dict(meta) for meta in metas],
            "citationPrefixes": citation_prefixes}


def _prefixes_of(model: str, prefix2model: dict) -> list[str]:
    return [p for p, m in prefix2model.items() if m == model]


def build_citation_discipline(registry: dict, prefix2model: dict,
                              declared: list[str]) -> dict:
    """③引用纪律与拒答边界：camp 面外（registry camp≠business-core，如
    SCR-/MU build-contract）+ 切片外（business-core 未入切片）+ 引用格式与
    可拒答声明（静态常量）。"""
    out_of_surface, outside_slice = [], []
    for model_id, info in registry.items():
        if not isinstance(info, dict) or model_id in declared:
            continue
        row = {"prefixes": _prefixes_of(model_id, prefix2model),
               "model": model_id, "name": info.get("name", model_id),
               "camp": info.get("camp", "")}
        if info.get("camp") != "business-core":
            out_of_surface.append(row)
        else:
            outside_slice.append(row)
    return {"idCitationFormat": ID_CITATION_FORMAT,
            "outOfSurface": out_of_surface, "outsideSlice": outside_slice,
            "refusal": REFUSAL_DECLARATION}


def build_package(domain_dir: Path, models: list[str],
                  schema_dir: Path = None) -> dict:
    """纯函数式组装：同输入同输出，零副作用（幂等/防陈旧的根基）。"""
    target = domain_dir.resolve()
    sdir = Path(schema_dir).resolve() if schema_dir else resolve_schema_dir(target)
    if sdir is None or not sdir.is_dir():
        raise ConfigError(
            f"schema 目录未找到（{target} 及其上级都没有 schema/）——"
            f"camp/模型面真源不可用，可用 --schema-dir 显式指定")
    registry, prefix2model = load_schema(sdir)
    if isinstance(models, str):  # 容错：直接传逗号串也可（CLI 走 list 已解析）
        models = parse_model_list(models)
    declared = list(dict.fromkeys(models))
    metas = validate_slice(declared, registry)
    dd = load_domain(target, declared, metas)
    for meta in metas:
        meta["version"] = dd["docs"][meta["model"]].get("version", "")
    has_m7 = "M7" in declared
    if has_m7:
        missing = [m for m in CALIBER_QUARTET if m not in declared]
        if missing:
            raise ConfigError(
                f"口径问答卡装配缺声明模型 {'/'.join(missing)}"
                f"（口径卡命中集须与语义服务 CORE 同源，M1/M2/M3/M7 需齐备；"
                f"边界规则 5 同款：缺了报错不硬编，不产残卡）")
    return {
        "status": STATUS_REVIEW,
        "domain": {k: dd[k] for k in ("name", "label", "profile", "sourcePath")},
        "slice": build_slice(declared, metas, prefix2model),
        "routing": {"note": ROUTING_NOTE,
                    "steps": [{"step": step, "name": name, "discipline": text}
                              for step, name, text in ROUTING_STEPS]},
        "calibers": build_calibers(dd) if has_m7 else [],
        "caliberNote": "" if has_m7 else CALIBER_NOTE_EMPTY,
        "glossary": build_glossary(dd),
        "citationDiscipline": build_citation_discipline(
            registry, prefix2model, declared),
        "generatedFrom": {
            "generator": GENERATOR,
            "source": dd["sourcePath"],
            "note": "确定性派生物：本体切片装配零 LLM 零时间戳，同域同声明"
                    "重生成字节一致；生成物禁手改，防陈旧断言=--check 再制"
                    "一致（票 36）",
        },
    }


# ---------- 包渲染 ----------


def _md_cell(text) -> str:
    """表格/行内单元格转义：竖线与换行拍平（确定性渲染）。"""
    return str(text if text is not None else "").replace("|", "\\|") \
        .replace("\n", " ").strip()


def render_frontmatter(pkg: dict) -> str:
    """①frontmatter：name/domain/slice-models/citation-prefixes + 人审状态。"""
    dom, sl = pkg["domain"], pkg["slice"]
    desc = (f"{dom['label'] or dom['name']}（{dom['name']}）可对话技能包骨架——"
            f"口径问答/对象问答/术语问答；{GENERATOR} 自本体切片确定性装配"
            f"（零 LLM 零时间戳）")
    lines = [
        "---",
        f"name: {dom['name']}-semantic",
        f"description: {json.dumps(desc, ensure_ascii=False)}",
        f"domain: {dom['name']}",
        f"slice-models: {json.dumps(sl['declared'])}",
        f"citation-prefixes: {json.dumps(sl['citationPrefixes'])}",
        f"status: {STATUS_REVIEW}",
        "---",
    ]
    return "\n".join(lines)


def _models_flag(pkg: dict) -> str:
    return ",".join(pkg["slice"]["declared"])


def render_md(pkg: dict) -> str:
    """技能包 → 人读 SKILL.md（frontmatter + 三节，确定性）。"""
    dom = pkg["domain"]
    lines = []
    ap = lines.append
    ap(render_frontmatter(pkg))
    ap("")
    ap(f"# {dom['label'] or dom['name']} 可对话技能包（skillpkg · {dom['name']}）")
    ap("")
    ap(f"status: {STATUS_REVIEW}")
    ap("")
    ap(f"- 生成器: {GENERATOR}（确定性装配：本体切片 + schema 注册表 camp 面，"
       f"零 LLM 零时间戳）")
    ap(f"- 本体来源: {dom['sourcePath']}（profile={dom['profile']}）")
    ap(f"- 切片声明: --models {_models_flag(pkg)}"
       f"（{len(pkg['slice']['declared'])} 模型，全部 camp=business-core）")
    if pkg["calibers"]:
        ap("- 口径同源: 口径问答卡命中集与语义服务 CORE 行为同源"
           "（出厂集 fixtures/skill-pack-gen AC1 探针机核）")
    ap(f"- 防陈旧: python3 {GENERATOR} {dom['sourcePath']} "
       f"--models {_models_flag(pkg)} "
       f"--check exports/skillpkg/{dom['name']}/{MD_NAME}")
    ap("")

    # ①工序路由
    ap(SECTION_HEADS[0])
    ap("")
    ap(f"> {pkg['routing']['note']}")
    ap("")
    for step in pkg["routing"]["steps"]:
        ap(f"- {step['step']} {step['name']}: {_md_cell(step['discipline'])}")
    ap("")

    # ②口径问答卡
    ap(SECTION_HEADS[1])
    ap("")
    if pkg["caliberNote"]:
        ap(pkg["caliberNote"])
        ap("")
    for c in pkg["calibers"]:
        ap(f"### 口径 {c['id']} · {c['name']}")
        ap("")
        ap(f"- 问题样例: {c['questionSample']}")
        if c.get("description"):
            ap(f"- 描述: {_md_cell(c['description'])}")
        ap(f"- 查询出口: {c['id']}（{c['objectType']}）")
        b = c["behavior"]
        ap(f"- 行为: {b['id']} {b['name']}"
           f"（{b['type']}，ownerEntity={b['ownerEntity']}）")
        owners = "、".join(
            f"{s['objectRef']} {s['name']}" + ("（主）" if s["primary"] else "")
            for s in c["sourceObjects"])
        ap(f"- 承载对象: {owners or '—'}")
        if c["parameters"]:
            ap("- 参数: " + "；".join(
                f"{p['name']}（{_md_cell(p.get('label'))}，{p.get('dataType')}"
                f"{'，必填' if p.get('required') else ''}）"
                for p in c["parameters"]))
        ap("- 命中 ID 集: " + " ".join(c["hitIds"]))
        ap("- 口径要点（关联规则 expression/narrative 摘录）:")
        if not c["rules"]:
            ap("  - （无关联 M3 规则）")
        for r in c["rules"]:
            point = r["point"]
            detail = point.get("expression") or point.get("narrative") \
                or "（无表达式/叙述）"
            ap(f"  - {r['id']} {r['name']}（{r['type']}；via={r['via']}）: "
               f"{_md_cell(detail)}")
        ap("")

    # ③引用纪律与拒答边界
    ap(SECTION_HEADS[2])
    ap("")
    cd = pkg["citationDiscipline"]
    ap(f"- ID 引用格式: {_md_cell(cd['idCitationFormat'])}")
    if cd["outOfSurface"]:
        faces = "；".join(
            f"{'/'.join(x['prefixes'])}（{x['model']} {x['name']}，"
            f"camp={x['camp']}）" for x in cd["outOfSurface"])
        ap(f"- camp 面外: {faces} → 面外拒答，不返回该面任何细节"
           f"（建造契约由 build 侧消费方在建造链路消费）")
    else:
        ap("- camp 面外: （registry 无非 business-core 模型）")
    if cd["outsideSlice"]:
        faces = "；".join(
            f"{'/'.join(x['prefixes'])}（{x['model']} {x['name']}，"
            f"camp={x['camp']}）" for x in cd["outsideSlice"])
        ap(f"- 切片外: {faces} → business-core 但未入本包切片，"
           f"按缺件如实说明不硬凑")
    gls = pkg["glossary"]
    if not gls["declared"]:
        ap("- 禁用词: 未声明 GLS——无术语面/禁用词表")
    elif gls["bannedTerms"]:
        ap("- 禁用词: " + "；".join(
            f"{t['term']}（{t['id']}，status={t['status']}）"
            for t in gls["bannedTerms"])
           + " → 问面命中即拦，指替代口径真实 ID，不得作为可用口径作答")
    else:
        ap("- 禁用词: 无禁用术语（GLS status 全非禁用）")
    ap(f"- {_md_cell(cd['refusal'])}")
    ap("")
    return "\n".join(lines).rstrip() + "\n"


def render_json(pkg: dict) -> str:
    """技能包 → 机读 JSON（ensure_ascii=False + indent=2 + 尾换行）。"""
    return json.dumps(pkg, ensure_ascii=False, indent=2) + "\n"


# ---------- CLI ----------


def _resolve_check_dir(check_path: Path) -> Path:
    """--check 入参：SKILL.md 文件 → 其目录；目录 → 原样。"""
    if check_path.is_file():
        return check_path.parent
    return check_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="F10 Skill 发布器（票 36；技能包=确定性装配，零 LLM 零时间戳）")
    ap.add_argument("target", help="本体域目录（含 manifest.json，单域出包）")
    ap.add_argument("--models", required=True, metavar="M1,M3,GLS",
                    help="切片声明（显式子集，逗号分隔；须全 business-core）")
    ap.add_argument("--out", default=None, metavar="目录",
                    help="写出 SKILL.md + skillpack.json 双文件（缺省 MD 打 stdout）")
    ap.add_argument("--check", default=None, metavar="入库路径",
                    help="重生成并与入库副本（SKILL.md 或其目录）逐字节比对"
                         "（一致 0 / 不一致 1）")
    ap.add_argument("--schema-dir", default=None, metavar="目录",
                    help="schema 目录（缺省按域目录自动定位 <域>/schema 或"
                         " <域>/../schema）")
    args = ap.parse_args(argv)

    try:
        models = parse_model_list(args.models)
        pkg = build_package(Path(args.target), models,
                            schema_dir=Path(args.schema_dir)
                            if args.schema_dir else None)
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
                            f"python3 {GENERATOR} {args.target} --models "
                            f"{args.models} --out {check_dir}）"))
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
