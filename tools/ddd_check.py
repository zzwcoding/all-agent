#!/usr/bin/env python3
"""ddd_check.py —— DDD 设计件确定性闸（All-agent 票 51；spec: specs/ddd-modeler.md
AC1–6；格式真源 design/ddd/README.md 票 50）。

对给定设计目录（design/ddd/<域>/ 或其等价物，票 50 §0：与 ontology/<域>/ 平级同名）
做五查，违规码 ddd-* 前缀（真源=tickets/51-ddd_check闸与第八套出厂集.md AC 表）：

  ddd-file-kind         文件级不可判读兜底（五查之外的结构闸，lessons/52 记边界）：
                        YAML 语法错 / 顶层非映射 / kind 不在四类（README §0.6）——
                        无此码则坏文件静默逃逸全部五查，约定不落闸等于没有；
  ddd-cross-agg-embed   D1 跨聚合内嵌（防 JOIN 暗桩，README §0.5）：词条面条目带
                        字段路径点号（`AGG-X.field` 形态）且左段解析到另一聚合卡
                        声明的聚合主词条 → 红；左段=本条目所属聚合自身 → 合法
                        （自身结构引用）；左段解析不到任何聚合卡聚合主词条 →
                        归 ddd-term-ref（红因不混）；
  ddd-term-ref          D2 词条解析（README §0.4 引用即类型，悬空=红）：聚合卡
                        聚合主词条/实体/属性/实体属性/值对象 + 事件载荷 + 映射列
                        term 必须解析到本体词条集合；无注册前缀（裸列名/裸文本
                        指代）同红。词条集合复用 schema_check 悬空引用解析族
                        口径（collect_definitions 同族：id/*Id 定义键、非 ref 键、
                        值带 model-deps.json idPrefixes 注册前缀——ref 键值不进
                        集合，防自引用洗白），独立实现保持零耦合，口径由
                        test_ddd_check.ResolutionFamilyAlignment 单测钉死
                        （lessons/52 记取舍）；
  ddd-invariant         D3 不变量齐备（README §1，防空壳聚合/贫血回潮）：每聚合卡
                        invariants 在场且非空，每条三元组 trigger/expect_fail/
                        method 在场且非空。method 目标可达性（方法真在聚合内）
                        语义判断不机判——归人审清单软节边界（裁决点 1：粒度/
                        完备性永远是人审）；
  ddd-mapping           D4 映射不断链（README §3，防映射腐烂）：mappings 非空，
                        条目聚合在设计件聚合集合中存在，tables 每表有表名、每列
                        有列名与 term 声明；列 term 的悬空解析归 D2（红因不混）；
  ddd-naming            D5 命名合规（README §0.4/§1/§2 + model-deps 同族口径）：
                        ID-role 字段（聚合主词条/实体/事件生产者/消费者/映射聚合/
                        仓储聚合）必须带注册前缀（缺失/非字符串/带字段路径同红）；
                        事件名大写下划线（README §2）；聚合/实体/事件/仓储四命名
                        空间内重名=红（报双位置）。

工程形态（票 51）：一次收集全部错误批量返回（failFast=false，digest §6 #3）；
报告含「待人审清单」软节（粒度/完备性提示：单聚合零事件、实体数/聚合数比超阈、
生产者/消费者/仓储聚合不在设计件聚合集合——只报告不影响退出码）；退出码
0 绿 / 1 红 / 2 配置错（--check 家族同族；配置错=目标目录不存在/设计目录无
设计件/本体目录不可用/schema 机读表缺失/本体无域）。

status 字段（草案/已审）的机判面在归档闸（票 50 design-card 类），本闸不重复；
本体侧 YAML 语法错归 schema_check L1，本闸跳过该文件（其词条不收集，悬空由
D2 如实暴露，不静默放行设计件侧引用）。

只读不写；失败输出含文件+行级定位（行号取自 YAML node start_mark，与
schema_check 同族的独立实现）；--json 供 CI 消费。依赖：Python3 stdlib +
PyYAML（safe 装载，PRD 技术栈唯一第三方）。

CLI: python3 tools/ddd_check.py <design目录> [--ontology <本体目录>] [--json]
  <本体目录> 缺省猜测同仓 ontology/（本脚本上级目录的上级）；显式传域目录或
  本体仓根均可（schema 解析顺序：本目录 schema/ → 上级目录 schema/，同 schema_check）。

退出码：0 全过；1 有违规；2 配置/用法错误。
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

KINDS = ("aggregate-card", "domain-events", "table-mapping",
         "repository-boundaries")
CHECK_CODES = ("ddd-cross-agg-embed", "ddd-term-ref", "ddd-invariant",
               "ddd-mapping", "ddd-naming", "ddd-file-kind")
CHECK_LABELS = {"ddd-cross-agg-embed": "D1", "ddd-term-ref": "D2",
                "ddd-invariant": "D3", "ddd-mapping": "D4",
                "ddd-naming": "D5", "ddd-file-kind": "文件"}
# 素材目录排除（与 schema_check PATTERN_DIRS 同族口径）：patterns 是素材区不是域
SKIP_DIR_NAMES = ("schema", "patterns")
# 事件名形态（README §2：大写下划线）
EVENT_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
# 人审清单软节阈值：单聚合实体数超过此值 → 粒度过大嫌疑提示（只提示不闸，
# digest §3「结构可机判、语义靠评审」边界；票 51 报告软节）
GR_MAX_ENTITIES_PER_AGG = 4


class ConfigError(Exception):
    """配置/用法错误（退出码 2 的承载）。"""


# ---------- 带行号的 YAML 装载（与 schema_check 同族口径的独立实现，只读 safe） ----------

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


# ---------- 遍历与 ID 判定（schema_check 解析族同族口径） ----------

def iter_mappings(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from iter_mappings(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_mappings(item)


def key_line(mapping, key) -> int:
    if getattr(mapping, "key_lines", None):
        return mapping.key_lines.get(key, mapping.line)
    return getattr(mapping, "line", 0)


def id_model_of(value: str, prefix2model: dict) -> str | None:
    for prefix, model in prefix2model.items():
        if value.startswith(prefix):
            return model
    return None


def is_registered_id(value, prefix2model: dict) -> bool:
    return isinstance(value, str) and id_model_of(value, prefix2model) is not None


def collect_terms(domain: Path, prefix2model: dict) -> set:
    """本体域目录 → 词条 ID 集合（schema_check collect_definitions 同族口径）。

    定义键 = id / *Id（非 ref 键）上的字符串值且带注册前缀；ref 键值不进集合
    （防自引用洗白悬空检查，与 schema_check 同一裁决）。语法错的文件跳过——
    本体侧语法归 schema_check L1 管辖，该文件词条不收集、设计件侧引用由 D2
    如实报悬空。
    """
    terms: set = set()
    for path in sorted(p for p in domain.rglob("*")
                       if p.is_file() and p.suffix in (".yaml", ".yml")):
        try:
            data = load_yaml(path)
        except _YamlSyntaxError:
            continue
        if not isinstance(data, dict):
            continue
        for mapping in iter_mappings(data):
            for key, value in mapping.items():
                if not (isinstance(key, str)
                        and (key == "id" or key.endswith("Id"))):
                    continue
                if key == "targetAggregate" or key.endswith(("Ref", "Refs")):
                    continue  # ref 键值不自证存在
                if is_registered_id(value, prefix2model):
                    terms.add(value)
    return terms


def resolve_schema_dir(target: Path) -> Path | None:
    for cand in (target / "schema", target.parent / "schema"):
        if cand.is_dir():
            return cand
    return None


def load_deps(schema_dir: Path) -> tuple[dict, set]:
    try:
        deps = json.loads((schema_dir / "model-deps.json").read_text(
            encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"{schema_dir / 'model-deps.json'} 不存在"
                          f"（ID 前缀机读表必配，真源 ontology/schema/）") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ConfigError(f"{schema_dir / 'model-deps.json'} 不是合法 JSON: "
                          f"{exc}") from exc
    prefix2model = deps.get("idPrefixes")
    if not isinstance(prefix2model, dict) or not prefix2model:
        raise ConfigError(f"{schema_dir / 'model-deps.json'} 缺 idPrefixes"
                          f"（前缀即类型标签，词条解析口径真源）")
    return prefix2model, set(deps.get("refKeys", []))


# ---------- 五查 ----------

class Checker:
    """单次运行的收集器：violations 硬违规 + review 人审清单软节。"""

    def __init__(self, prefix2model: dict):
        self.prefix2model = prefix2model
        self.violations: list = []
        self.review: list = []
        self._seen = set()

    def add(self, kind: str, file: str, line: int, message: str) -> None:
        key = (kind, file, line, message)
        if key in self._seen:
            return
        self._seen.add(key)
        self.violations.append({"check": CHECK_LABELS[kind], "kind": kind,
                                "file": file, "line": line, "message": message})

    def soft(self, message: str) -> None:
        if message not in self.review:
            self.review.append(message)


def check_file_kind(checker: Checker, files: list) -> list:
    """文件级判读：返回 (rel, data, kind) 三元组列表；不可判读文件报 ddd-file-kind。"""
    parsed = []
    for path in files:
        rel = str(path)
        try:
            data = load_yaml(path)
        except _YamlSyntaxError as exc:
            checker.add("ddd-file-kind", rel, 0,
                        f"YAML 语法错误: {exc}——文件不可判读，五查全部让位"
                        f"（design/ddd/README.md §0.6 一文件一类别）")
            continue
        if not isinstance(data, dict):
            checker.add("ddd-file-kind", rel, 0,
                        "YAML 顶层必须是映射——文件不可判读，五查全部让位")
            continue
        kind = data.get("kind")
        if kind not in KINDS:
            checker.add("ddd-file-kind", rel,
                        getattr(data, "line", 0) or 0,
                        f"顶层 kind「{kind}」不在四类设计件"
                        f"（{ ' / '.join(KINDS) }，design/ddd/README.md §0.6/"
                        f"§1–§4）——文件不可判读，五查全部让位")
            continue
        parsed.append((rel, data, kind))
    return parsed


def check_naming(checker: Checker, parsed: list, aggs: dict) -> None:
    """D5 ddd-naming：ID-role 前缀形态 + 事件名形态 + 四命名空间重名。"""
    # ID-role 字段：必须带注册前缀（缺字段/非字符串/带字段路径同红——形态归本查，
    # 悬空解析归 D2/D4/人审软节，红因不混）
    id_roles = []  # (值, 文件, 行, 字段说明)
    for rel, data, kind in parsed:
        if kind == "aggregate-card":
            id_roles.append((data.get("aggregate"), rel, key_line(data, "aggregate")
                             if "aggregate" in data else getattr(data, "line", 0),
                             "聚合主词条 aggregate"))
            for ent in data.get("entities") or []:
                if isinstance(ent, dict) and "entity" in ent:
                    id_roles.append((ent.get("entity"), rel,
                                     key_line(ent, "entity"), "实体 entity"))
        elif kind == "domain-events":
            for ev in data.get("events") or []:
                if not isinstance(ev, dict):
                    continue
                for field, label in (("producer", "事件生产者 producer"),):
                    if field in ev:
                        id_roles.append((ev.get(field), rel,
                                         key_line(ev, field), label))
                for i, c in enumerate(ev.get("consumers") or []):
                    id_roles.append((c, rel, key_line(ev, "consumers"),
                                     f"事件消费者 consumers[{i}]"))
        elif kind == "table-mapping":
            for mp in data.get("mappings") or []:
                if isinstance(mp, dict) and "aggregate" in mp:
                    id_roles.append((mp.get("aggregate"), rel,
                                     key_line(mp, "aggregate"), "映射聚合 aggregate"))
        elif kind == "repository-boundaries":
            for rp in data.get("repositories") or []:
                if not isinstance(rp, dict):
                    continue
                if "repository" in rp:
                    id_roles.append((rp.get("repository"), rel,
                                     key_line(rp, "repository"), "仓储名 repository"))
                if "aggregate" in rp:
                    id_roles.append((rp.get("aggregate"), rel,
                                     key_line(rp, "aggregate"), "仓储聚合 aggregate"))
    for value, rel, line, label in id_roles:
        if not isinstance(value, str) or not value.strip():
            checker.add("ddd-naming", rel, line,
                        f"{label} 缺失或非字符串——ID-role 字段必须是有值词条 ID"
                        f"（design/ddd/README.md §0.4 引用即类型；票 51 D5）")
            continue
        if "." in value:
            checker.add("ddd-naming", rel, line,
                        f"{label}「{value}」带字段路径点号——ID-role 字段只收干净"
                        f"词条 ID，字段级路径出现在词条面归 D1 ddd-cross-agg-embed"
                        f"判定（票 51 D5）")
            continue
        if label != "仓储名 repository" and \
                not is_registered_id(value, checker.prefix2model):
            checker.add("ddd-naming", rel, line,
                        f"{label}「{value}」未带注册前缀（model-deps.json "
                        f"idPrefixes: {sorted(checker.prefix2model)}）——词条 ID "
                        f"前缀即类型标签（票 51 D5，model-deps 同族口径）")
    # 事件名形态（README §2：大写下划线）
    for rel, data, kind in parsed:
        if kind != "domain-events":
            continue
        for ev in data.get("events") or []:
            if not isinstance(ev, dict) or "event" not in ev:
                continue
            name = ev.get("event")
            if not isinstance(name, str) or not EVENT_NAME_RE.match(name):
                checker.add("ddd-naming", rel, key_line(ev, "event"),
                            f"事件名「{name}」不合大写下划线形态"
                            f"（design/ddd/README.md §2；票 51 D5）")
    # 四命名空间重名：聚合（跨卡）/实体/事件/仓储；撞名逐处报双位置（票 38 同族）
    namespaces: dict = {"聚合": [], "实体": [], "事件": [], "仓储": []}
    for rel, data, kind in parsed:
        if kind == "aggregate-card":
            agg = data.get("aggregate")
            if isinstance(agg, str) and agg:
                namespaces["聚合"].append(
                    (agg, rel, key_line(data, "aggregate")))
            for ent in data.get("entities") or []:
                if isinstance(ent, dict) and isinstance(ent.get("entity"), str):
                    namespaces["实体"].append(
                        (ent["entity"], rel, key_line(ent, "entity")))
        elif kind == "domain-events":
            for ev in data.get("events") or []:
                if isinstance(ev, dict) and isinstance(ev.get("event"), str):
                    namespaces["事件"].append(
                        (ev["event"], rel, key_line(ev, "event")))
        elif kind == "repository-boundaries":
            for rp in data.get("repositories") or []:
                if isinstance(rp, dict) and isinstance(rp.get("repository"), str):
                    namespaces["仓储"].append(
                        (rp["repository"], rel, key_line(rp, "repository")))
    for ns_name, occ in namespaces.items():
        seen: dict = {}
        for value, rel, line in occ:
            first = seen.get(value)
            if first is not None:
                checker.add("ddd-naming", rel, line,
                            f"{ns_name}命名空间重名「{value}」: 先出现 "
                            f"{first[0]}:{first[1]}，后出现 {rel}:{line}"
                            f"——设计件内 id 不得重复（票 51 D5）")
            else:
                seen[value] = (rel, line)


def check_terms_and_embed(checker: Checker, parsed: list, aggs: dict,
                          terms: set) -> None:
    """D1 ddd-cross-agg-embed + D2 ddd-term-ref：词条面逐条判定。

    词条面（引用即类型，README §0.4）：聚合卡聚合主词条/实体（ID-role 字段：形态
    归 D5 命名，悬空解析归本查——单一红因）+ properties/entities[].properties/
    value_objects[].value_object + 事件 payload + 映射列 term（纯词条面：无前缀
    即裸列名/裸文本指代红）。
    点号条目归 D1（左段=另一聚合卡聚合主词条→内嵌红；左段=本条目所属聚合自身
    →合法；左段解析不到→归 D2）；无点号条目归 D2（无注册前缀=裸列名/裸文本
    指代红；带前缀而悬空红）。
    """
    surfaces = []  # (值, 所属聚合或 None, 文件, 行, 面说明, 是否 ID-role 字段)
    for rel, data, kind in parsed:
        if kind == "aggregate-card":
            owner = data.get("aggregate") if isinstance(data.get("aggregate"), str) else None
            if "aggregate" in data:
                surfaces.append((data.get("aggregate"), owner, rel,
                                 key_line(data, "aggregate"),
                                 "聚合主词条 aggregate", True))
            for i, prop in enumerate(data.get("properties") or []):
                surfaces.append((prop, owner, rel, _item_line(data, "properties", i),
                                 "聚合属性 properties", False))
            for ent in data.get("entities") or []:
                if not isinstance(ent, dict):
                    continue
                if "entity" in ent:
                    surfaces.append((ent.get("entity"), owner, rel,
                                     key_line(ent, "entity"),
                                     f"实体 entity", True))
                for i, prop in enumerate(ent.get("properties") or []):
                    surfaces.append((prop, owner, rel,
                                     _item_line(ent, "properties", i),
                                     f"实体 {ent.get('entity', '?')} 属性 properties",
                                     False))
            for vo in data.get("value_objects") or []:
                if isinstance(vo, dict) and "value_object" in vo:
                    surfaces.append((vo.get("value_object"), owner, rel,
                                     key_line(vo, "value_object"),
                                     "值对象 value_object", False))
        elif kind == "domain-events":
            for ev in data.get("events") or []:
                if not isinstance(ev, dict):
                    continue
                producer = (ev.get("producer")
                            if isinstance(ev.get("producer"), str) else None)
                for i, item in enumerate(ev.get("payload") or []):
                    surfaces.append((item, producer, rel,
                                     _item_line(ev, "payload", i),
                                     f"事件 {ev.get('event', '?')} 载荷 payload",
                                     False))
        elif kind == "table-mapping":
            for mp in data.get("mappings") or []:
                if not isinstance(mp, dict):
                    continue
                mp_agg = (mp.get("aggregate")
                          if isinstance(mp.get("aggregate"), str) else None)
                for tb in mp.get("tables") or []:
                    if not isinstance(tb, dict):
                        continue
                    for col in tb.get("columns") or []:
                        if isinstance(col, dict) and "term" in col:
                            surfaces.append((col.get("term"), mp_agg, rel,
                                             key_line(col, "term"),
                                             f"表 {tb.get('table', '?')} 列 term",
                                             False))
    for value, owner, rel, line, label, id_role in surfaces:
        if not isinstance(value, str) or not value.strip():
            checker.add("ddd-term-ref", rel, line,
                        f"{label} 词条条目缺失或非字符串（引用即类型：一杠一词条 ID，"
                        f"design/ddd/README.md §0.4；票 51 D2）")
            continue
        if "." in value:
            left = value.split(".", 1)[0]
            if left in aggs:
                if owner is not None and left == owner:
                    continue  # 本聚合自身结构引用，合法
                checker.add("ddd-cross-agg-embed", rel, line,
                            f"{label}「{value}」字段级内嵌他聚合：左段「{left}」是"
                            f"另一聚合卡声明的聚合主词条——跨聚合只许 ID 引用，"
                            f"不得内嵌对方属性（防 JOIN 暗桩，design/ddd/README.md "
                            f"§0.5；票 51 D1）")
            else:
                checker.add("ddd-term-ref", rel, line,
                            f"{label}「{value}」字段路径左段「{left}」解析不到任何"
                            f"聚合卡聚合主词条——字段路径引用仅允许指向本聚合自身"
                            f"结构（票 51 D1/D2 边界：点号条目归 D1 判定，左段不在"
                            f"设计件聚合集合时按词条解析红）")
            continue
        if not is_registered_id(value, checker.prefix2model):
            if id_role:
                continue  # ID-role 字段的无前缀形态归 D5 naming，红因不混
            checker.add("ddd-term-ref", rel, line,
                        f"{label}「{value}」非词条 ID 形态（未带注册前缀）——裸列名/"
                        f"裸文本指代禁止（design/ddd/README.md §0.4；票 51 D2，"
                        f"model-deps.json idPrefixes 口径）")
            continue
        if value not in terms:
            checker.add("ddd-term-ref", rel, line,
                        f"{label}「{value}」悬空：在本体词条集合中不存在"
                        f"（票 51 D2，schema_check 悬空引用解析族同族口径）")


def _item_line(owner_map, key, index: int) -> int:
    """列表条目行号：条目带行号（MDict）用自身行，否则退列表行。"""
    items = owner_map.get(key) if isinstance(owner_map, dict) else None
    if isinstance(items, MList) and index < len(items):
        item = items[index]
        if hasattr(item, "line"):
            return item.line
    return getattr(items, "line", 0) if isinstance(items, MList) else 0


def check_invariants(checker: Checker, parsed: list) -> None:
    """D3 ddd-invariant：清单缺失/非清单/空/三元组缺一（防空壳聚合/贫血回潮）。"""
    for rel, data, kind in parsed:
        if kind != "aggregate-card":
            continue
        agg = data.get("aggregate", "?")
        if "invariants" not in data:
            checker.add("ddd-invariant", rel, getattr(data, "line", 0),
                        f"聚合卡 {agg} 缺 invariants 不变量清单（design/ddd/"
                        f"README.md §1 必填；票 51 D3，防空壳聚合/贫血回潮）")
            continue
        invariants = data.get("invariants")
        if not isinstance(invariants, list):
            checker.add("ddd-invariant", rel, key_line(data, "invariants"),
                        f"聚合卡 {agg} invariants 必须是清单（票 51 D3）")
            continue
        if not invariants:
            checker.add("ddd-invariant", rel, key_line(data, "invariants"),
                        f"聚合卡 {agg} 不变量清单为空——每聚合至少一条不变量三元组"
                        f"（design/ddd/README.md §1 不得为空；票 51 D3）")
            continue
        for i, inv in enumerate(invariants):
            if not isinstance(inv, dict):
                checker.add("ddd-invariant", rel, _item_line(data, "invariants", i),
                            f"聚合卡 {agg} 不变量条目 #{i + 1} 不是映射——三元组"
                            f"trigger/expect_fail/method 各一行（票 51 D3）")
                continue
            for field, cn in (("trigger", "触发操作"), ("expect_fail", "期望失败"),
                              ("method", "指向方法")):
                v = inv.get(field)
                if not (isinstance(v, str) and v.strip()):
                    checker.add("ddd-invariant", rel, key_line(inv, field),
                                f"聚合卡 {agg} 不变量三元组缺「{field}」（{cn}）"
                                f"——触发操作→期望失败→指向方法缺一不可"
                                f"（design/ddd/README.md §1；票 51 D3）")


def check_mappings(checker: Checker, parsed: list, aggs: dict) -> None:
    """D4 ddd-mapping：映射不断链（聚合在设计件集合中存在；表/列声明齐备）。"""
    for rel, data, kind in parsed:
        if kind != "table-mapping":
            continue
        mappings = data.get("mappings")
        if not isinstance(mappings, list) or not mappings:
            checker.add("ddd-mapping", rel, key_line(data, "mappings"),
                        "映射清单 mappings 缺失或为空（design/ddd/README.md §3；"
                        "票 51 D4）")
            continue
        for i, mp in enumerate(mappings):
            if not isinstance(mp, dict):
                checker.add("ddd-mapping", rel, _item_line(data, "mappings", i),
                            "映射条目不是映射（票 51 D4）")
                continue
            agg = mp.get("aggregate")
            if isinstance(agg, str) and is_registered_id(agg, checker.prefix2model) \
                    and "." not in agg and agg not in aggs:
                checker.add("ddd-mapping", rel, key_line(mp, "aggregate"),
                            f"映射声明的聚合「{agg}」在设计件聚合集合"
                            f"（{sorted(aggs)}）中不存在——映射不断链"
                            f"（票 51 D4）")
            tables = mp.get("tables")
            if not isinstance(tables, list) or not tables:
                checker.add("ddd-mapping", rel, key_line(mp, "tables"),
                            f"映射条目 {agg if isinstance(agg, str) else '?'} 缺 "
                            f"tables 表清单（design/ddd/README.md §3；票 51 D4）")
                continue
            for j, tb in enumerate(tables):
                if not isinstance(tb, dict):
                    checker.add("ddd-mapping", rel, _item_line(mp, "tables", j),
                                "表条目不是映射（票 51 D4）")
                    continue
                table = tb.get("table")
                if not (isinstance(table, str) and table.strip()):
                    checker.add("ddd-mapping", rel, key_line(tb, "table"),
                                f"映射条目 {agg if isinstance(agg, str) else '?'} "
                                f"表条目缺表名 table——表不可解析（票 51 D4）")
                columns = tb.get("columns")
                if not isinstance(columns, list) or not columns:
                    checker.add("ddd-mapping", rel, key_line(tb, "columns"),
                                f"表「{table if isinstance(table, str) else '?'}」"
                                f"缺 columns 列映射（票 51 D4）")
                    continue
                for col in columns:
                    if not isinstance(col, dict):
                        checker.add("ddd-mapping", rel,
                                    getattr(col, "line", 0) or key_line(tb, "columns"),
                                    "列条目不是映射（票 51 D4）")
                        continue
                    column = col.get("column")
                    if not (isinstance(column, str) and column.strip()):
                        checker.add("ddd-mapping", rel, key_line(col, "column"),
                                    f"表「{table if isinstance(table, str) else '?'}」"
                                    f"列条目缺列名 column——映射指向的列不可解析"
                                    f"（design/ddd/README.md §3 列与词条双向可解析；"
                                    f"票 51 D4）")
                    term = col.get("term")
                    if term is None or (isinstance(term, str) and not term.strip()):
                        checker.add("ddd-mapping", rel, key_line(col, "term"),
                                    f"表「{table if isinstance(table, str) else '?'}」"
                                    f"列「{column if isinstance(column, str) else '?'}」"
                                    f"缺 term 词条声明——列↔词条双向可解析断裂"
                                    f"（票 51 D4；term 在场而悬空归 D2，红因不混）")


def collect_review(parsed: list, aggs: dict) -> list:
    """人审清单软节（不进退出码）：粒度/完备性提示（README §5，digest §3 边界）。"""
    review = []
    producers = set()
    role_refs = []
    n_entities = 0
    ent_per_agg: dict = {}
    for rel, data, kind in parsed:
        if kind == "domain-events":
            for ev in data.get("events") or []:
                if isinstance(ev, dict) and isinstance(ev.get("producer"), str):
                    producers.add(ev["producer"])
                    for c in ev.get("consumers") or []:
                        if isinstance(c, str):
                            role_refs.append(("事件消费者", c, rel))
        elif kind == "repository-boundaries":
            for rp in data.get("repositories") or []:
                if isinstance(rp, dict) and isinstance(rp.get("aggregate"), str):
                    role_refs.append(("仓储聚合", rp["aggregate"], rel))
        elif kind == "aggregate-card":
            agg = data.get("aggregate")
            ents = [e for e in (data.get("entities") or [])
                    if isinstance(e, dict) and isinstance(e.get("entity"), str)]
            n_entities += len(ents)
            if isinstance(agg, str):
                ent_per_agg[agg] = ent_per_agg.get(agg, 0) + len(ents)
    for agg in aggs:
        if agg not in producers:
            review.append(f"聚合 {agg} 零事件（事件表无其生产条目）——跨聚合协作"
                          f"缺失嫌疑，粒度人审裁决（票 51 人审清单，digest §3）")
    for agg, n in ent_per_agg.items():
        if n > GR_MAX_ENTITIES_PER_AGG:
            review.append(f"聚合 {agg} 含 {n} 个实体（超过 {GR_MAX_ENTITIES_PER_AGG}"
                          f"）——聚合过大嫌疑，宁小勿大原则人审裁决（design/ddd/"
                          f"README.md §1；票 51 人审清单）")
    for label, value, rel in role_refs:
        # 前缀形态已由 D5 判定，此处只看设计件集合成员资格（软节）
        if value not in aggs:
            review.append(f"{label}「{value}」不在设计件聚合集合（{sorted(aggs)}）"
                          f"中——设计内角色引用悬空，完备性人审裁决（票 51 人审清单；"
                          f"映射聚合的此形态是硬闸 ddd-mapping，不在此重复）")
    return review


# ---------- 主流程 ----------

def run(target: Path, ontology: Path | None = None) -> dict:
    target = Path(target).resolve()
    if not target.is_dir():
        raise ConfigError(f"目标目录不存在: {target}")
    files = sorted(p for p in target.rglob("*")
                   if p.is_file() and p.suffix in (".yaml", ".yml"))
    if not files:
        raise ConfigError(f"{target} 内无 .yaml/.yml 设计件（DDD 闸不空跑——"
                          f"空设计目录无法断言任何约定）")

    onto = Path(ontology).resolve() if ontology else \
        Path(__file__).resolve().parent.parent / "ontology"
    if not onto.is_dir():
        raise ConfigError(f"本体目录不存在: {onto}（--ontology 显式传入或同仓 "
                          f"ontology/）")
    schema_dir = resolve_schema_dir(onto)
    if schema_dir is None:
        raise ConfigError(f"{onto} 及其上级都没有 schema/（缺 model-deps.json "
                          f"ID 前缀机读表）")
    prefix2model, _ref_keys = load_deps(schema_dir)
    if (onto / "manifest.json").is_file():
        domains = [onto]
    else:
        domains = sorted(d for d in onto.iterdir() if d.is_dir()
                         and d.name not in SKIP_DIR_NAMES
                         and (d / "manifest.json").is_file())
    if not domains:
        raise ConfigError(f"{onto} 中未发现任何域（含 manifest.json 的目录）——"
                          f"无词条不建模（design/ddd/README.md §0.1）")
    terms: set = set()
    for domain in domains:
        terms |= collect_terms(domain, prefix2model)

    checker = Checker(prefix2model)
    parsed = check_file_kind(checker, files)

    aggs: dict = {}  # 聚合主词条 → (文件, 行)（聚合卡声明面）
    for rel, data, kind in parsed:
        if kind == "aggregate-card" and isinstance(data.get("aggregate"), str) \
                and data["aggregate"]:
            aggs.setdefault(data["aggregate"], (rel, key_line(data, "aggregate")))

    check_naming(checker, parsed, aggs)
    check_terms_and_embed(checker, parsed, aggs, terms)
    check_invariants(checker, parsed)
    check_mappings(checker, parsed, aggs)
    checker.review.extend(collect_review(parsed, aggs))

    checks = {code: sum(1 for v in checker.violations if v["kind"] == code)
              for code in CHECK_CODES}
    kinds = {k: sum(1 for _rel, _d, kd in parsed if kd == k) for k in KINDS}
    return {
        "status": "fail" if checker.violations else "pass",
        "target": str(target),
        "ontology": str(onto),
        "termCount": len(terms),
        "files": len(files),
        "kinds": kinds,
        "checks": checks,
        "violations": checker.violations,
        "review": checker.review,
    }


def print_human(report: dict) -> None:
    kinds = report["kinds"]
    print(f"DDD 设计件闸 ddd_check — {report['target']}")
    print(f"本体: {report['ontology']}（词条 {report['termCount']} 条）；"
          f"设计件 {report['files']} 个（聚合卡 {kinds.get('aggregate-card', 0)} / "
          f"事件表 {kinds.get('domain-events', 0)} / 映射 "
          f"{kinds.get('table-mapping', 0)} / 仓储 "
          f"{kinds.get('repository-boundaries', 0)}）")
    for v in report["violations"]:
        loc = f"{v['file']}:{v['line']}" if v["line"] else v["file"]
        print(f"[{v['check']}][{v['kind']}] {loc} — {v['message']}")
    c = report["checks"]
    print(f"五查: cross-agg-embed {c['ddd-cross-agg-embed']} | "
          f"term-ref {c['ddd-term-ref']} | invariant {c['ddd-invariant']} | "
          f"mapping {c['ddd-mapping']} | naming {c['ddd-naming']} | "
          f"file-kind {c['ddd-file-kind']}")
    if report["review"]:
        print("待人审清单（软节，不进退出码）:")
        for item in report["review"]:
            print(f"  - {item}")
    if report["status"] == "pass":
        print("DDD 闸: 全过")
    else:
        print(f"DDD 闸: {len(report['violations'])} 处违规")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="DDD 设计件五查闸（specs/ddd-modeler.md；格式真源 "
                    "design/ddd/README.md；票 51）")
    ap.add_argument("target", help="设计目录（design/ddd/<域>/ 或等价物）")
    ap.add_argument("--ontology", default=None,
                    help="本体目录（域目录或本体仓根；缺省猜测同仓 ontology/）")
    ap.add_argument("--json", action="store_true", help="机读 JSON 输出（供 CI 消费）")
    args = ap.parse_args(argv)
    try:
        report = run(Path(args.target),
                     Path(args.ontology) if args.ontology else None)
    except ConfigError as exc:
        print(f"配置错误: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
