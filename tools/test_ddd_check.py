#!/usr/bin/env python3
"""ddd_check.py 的单测（stdlib unittest + PyYAML，TDD 先行，票 51）。

合成最小订单域（订单 AGG-ORDER-001 / 订单项 AGG-ORDER-002 / 支付 AGG-ORDER-003，
词条 GLS-ORDER-001..007）走端到端：五查各一组负变体（AC1a–e 对应 tickets/51 票面
AC 表）+ 绿灯样本（AC2）+ failFast 批量报文（AC3a）+ 人审清单软节（AC3b）+
退出码 0/1/2 契约（AC4）+ 与 schema_check 解析族口径对齐单测（票 38 同族：
ref 值不自证存在 / 未注册前缀不入词条集合 / DICT 入集）。
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ddd_check as dc


def quiet_main(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = dc.main(argv)
    return rc


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def human(report) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        dc.print_human(report)
    return buf.getvalue()


DEPS = {
    "version": "1",
    "description": "单测基座（票 51）：idPrefixes/refKeys 与 ontology/schema/model-deps.json 同形",
    "idPrefixes": {"AGG-": "M1", "DICT-": "M1", "GLS-": "GLS"},
    "refKeys": ["targetAggregate", "relatedObjectRefs"],
}

GLS_NAMES = {
    1: "订单编号", 2: "下单时间", 3: "行数量", 4: "行单价",
    5: "收货地址", 6: "支付金额", 7: "支付状态",
}


def gls_yaml() -> str:
    lines = ["model_type: GLOSSARY", 'version: "1.0.0"', "domain: order", "terms:"]
    for n, name in GLS_NAMES.items():
        lines += [
            f"  - id: GLS-ORDER-{n:03d}",
            f"    term: {name}",
            "    termType: 术语",
            f"    definition: 订单域词条 {name}（票 51 出厂集合成词条）。",
            "    status: 有效",
            "    source: 合成·票 51 出厂集",
        ]
    return "\n".join(lines) + "\n"


M1_YAML = """\
model_type: OBJECT
version: "1.0.0"
domain: order
aggregates:
  - id: AGG-ORDER-001
    name: 订单
    alias: Order
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: orderNo, label: 订单编号, type: String }
      - { name: createdAt, label: 下单时间, type: Date }
  - id: AGG-ORDER-002
    name: 订单项
    alias: OrderItem
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: quantity, label: 行数量, type: Decimal }
      - { name: unitPrice, label: 行单价, type: Decimal }
  - id: AGG-ORDER-003
    name: 支付
    alias: Payment
    aggregateType: AGGREGATE_ROOT
    attributes:
      - { name: amount, label: 支付金额, type: Decimal }
      - { name: status, label: 支付状态, type: Enum }
"""

ORDER_CARD = """\
# 头注释：设计件=草案，业务裁决待 Owner 确认
kind: aggregate-card
status: 草案
domain: order
aggregate: AGG-ORDER-001
aggregate_root: true
domain_vision: "订单与订单项必须同时成立、同时改，不出现中间态"
properties:
  - GLS-ORDER-001
  - GLS-ORDER-002
entities:
  - entity: AGG-ORDER-002
    properties:
      - GLS-ORDER-003
      - GLS-ORDER-004
value_objects:
  - value_object: GLS-ORDER-005
invariants:
  - trigger: "submit（提交订单）"
    expect_fail: "订单项为空则拒，DomainError: EMPTY_ORDER"
    method: "Order.submit()"
  - trigger: "changeQuantity（改行数量）"
    expect_fail: "数量非正数则拒，DomainError: BAD_QUANTITY"
    method: "Order.changeQuantity()"
corrective_policies:
  - on: "DomainError: PAYMENT_FAILED"
    action: "订单回退待支付态并发出 PAYMENT_FAILED 事件，不静默吞"
domain_events:
  - ORDER_SUBMITTED
ways_to_access:
  - repository: "OrderRepository"
  - factory: "Order.place()"
"""

PAYMENT_CARD = """\
# 头注释：设计件=草案，业务裁决待 Owner 确认
kind: aggregate-card
status: 草案
domain: order
aggregate: AGG-ORDER-003
aggregate_root: true
domain_vision: "支付金额与支付状态同时成立，支付一旦成功不可变"
properties:
  - GLS-ORDER-006
  - GLS-ORDER-007
entities: []
value_objects: []
invariants:
  - trigger: "capture（支付扣款）"
    expect_fail: "已支付再扣则拒，DomainError: ALREADY_PAID"
    method: "Payment.capture()"
domain_events:
  - PAYMENT_SUCCEEDED
ways_to_access:
  - repository: "PaymentRepository"
  - factory: "Payment.create()"
"""

EVENTS = """\
kind: domain-events
status: 草案
domain: order
events:
  - event: ORDER_SUBMITTED
    producer: AGG-ORDER-001
    consumers:
      - AGG-ORDER-003
    payload:
      - GLS-ORDER-001
      - GLS-ORDER-002
    delivery: outbox
  - event: PAYMENT_SUCCEEDED
    producer: AGG-ORDER-003
    consumers:
      - AGG-ORDER-001
    payload:
      - GLS-ORDER-006
      - GLS-ORDER-007
    delivery: inprocess
"""

MAPPING = """\
kind: table-mapping
status: 草案
domain: order
mappings:
  - aggregate: AGG-ORDER-001
    tables:
      - table: t_order
        columns:
          - column: order_no
            term: GLS-ORDER-001
          - column: created_at
            term: GLS-ORDER-002
      - table: t_order_item
        columns:
          - column: quantity
            term: GLS-ORDER-003
          - column: unit_price
            term: GLS-ORDER-004
    write_side: "仅订单模块代码库写；跨聚合不 JOIN"
  - aggregate: AGG-ORDER-003
    tables:
      - table: t_payment
        columns:
          - column: amount
            term: GLS-ORDER-006
          - column: status
            term: GLS-ORDER-007
    write_side: "仅支付模块代码库写"
"""

REPOS = """\
kind: repository-boundaries
status: 草案
domain: order
repositories:
  - repository: OrderRepository
    aggregate: AGG-ORDER-001
    returns: "仅本聚合（订单+订单项+值对象整体），不返回他聚合对象"
    persistence: "整体存取：save/load 整个聚合，不暴露逐字段 UPDATE"
  - repository: PaymentRepository
    aggregate: AGG-ORDER-003
    returns: "仅本聚合（支付整体），不返回他聚合对象"
    persistence: "整体存取：save/load 整个聚合，不暴露逐字段 UPDATE"
"""

GREEN = {
    "aggregate-order.yaml": ORDER_CARD,
    "aggregate-payment.yaml": PAYMENT_CARD,
    "domain-events.yaml": EVENTS,
    "table-mapping.yaml": MAPPING,
    "repository-boundaries.yaml": REPOS,
}


class Base(unittest.TestCase):
    """每测试一个临时仓：本体（schema+order 域）+ 设计目录。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.onto = root / "onto"
        write(self.onto / "schema" / "model-deps.json", json.dumps(DEPS))
        write(self.onto / "order" / "manifest.json", json.dumps(
            {"domain": "order", "profile": "mini", "schemaVersion": "1.0.0"}))
        write(self.onto / "order" / "m1-object-model.yaml", M1_YAML)
        write(self.onto / "order" / "glossary-model.yaml", gls_yaml())
        self.design = root / "design"
        for name, text in GREEN.items():
            write(self.design / name, text)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name: str, text: str) -> None:
        write(self.design / name, text)

    def run_check(self):
        return dc.run(self.design, self.onto)

    def run_rc(self):
        return quiet_main(["--ontology", str(self.onto), str(self.design)])

    def kinds_of(self, report) -> list:
        return [v["kind"] for v in report["violations"]]


class DesignGreen(Base):
    def test_green_all_clear(self):
        r = self.run_check()
        self.assertEqual(r["status"], "pass")
        self.assertEqual(r["violations"], [])
        self.assertEqual(r["review"], [])
        self.assertEqual(r["termCount"], 10)  # AGG×3 + GLS×7
        self.assertEqual(r["kinds"], {"aggregate-card": 2, "domain-events": 1,
                                      "table-mapping": 1, "repository-boundaries": 1})
        self.assertEqual(self.run_rc(), 0)

    def test_green_json_report(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = dc.main(["--json", "--ontology", str(self.onto), str(self.design)])
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        for key in ("status", "target", "ontology", "termCount", "files",
                    "kinds", "checks", "violations", "review"):
            self.assertIn(key, data)
        self.assertEqual(data["checks"]["ddd-cross-agg-embed"], 0)
        self.assertEqual(data["checks"]["ddd-term-ref"], 0)


class CrossAggEmbed(Base):
    """D1 ddd-cross-agg-embed：跨聚合引用必须 ID，字段级内嵌（点号路径）=红。"""

    def test_embed_other_aggregate_property(self):
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            "properties:\n  - GLS-ORDER-001",
            "properties:\n  - AGG-ORDER-003.amount\n  - GLS-ORDER-001"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]],
                         ["ddd-cross-agg-embed"])
        v = r["violations"][0]
        self.assertIn("AGG-ORDER-003.amount", v["message"])
        self.assertGreater(v["line"], 0)

    def test_embed_in_payload(self):
        self.put("domain-events.yaml", EVENTS.replace(
            "    payload:\n      - GLS-ORDER-006",
            "    payload:\n      - AGG-ORDER-001.orderNo\n      - GLS-ORDER-006"))
        r = self.run_check()
        # 生产者=支付聚合，载荷点号路径左段=订单聚合（另一聚合卡）→ D1 红
        self.assertEqual([v["kind"] for v in r["violations"]],
                         ["ddd-cross-agg-embed"])

    def test_self_dot_path_allowed(self):
        # 左段=本卡聚合主词条（自身结构引用）不判内嵌
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            "properties:\n  - GLS-ORDER-001",
            "properties:\n  - AGG-ORDER-001.items\n  - GLS-ORDER-001"))
        r = self.run_check()
        self.assertEqual(r["violations"], [])

    def test_dot_path_unknown_left_is_term_ref(self):
        # 左段解析不到任何聚合卡聚合主词条 → 归 D2（红因不混）
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            "properties:\n  - GLS-ORDER-001",
            "properties:\n  - t_order.order_no\n  - GLS-ORDER-001"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-term-ref"])
        self.assertIn("t_order", r["violations"][0]["message"])


class TermRef(Base):
    """D2 ddd-term-ref：词条 ID 悬空/非词条形态=红（复用 schema_check 解析族口径）。"""

    def test_payload_dangling_term(self):
        self.put("domain-events.yaml", EVENTS.replace(
            "      - GLS-ORDER-002\n    delivery: outbox",
            "      - GLS-ORDER-999\n    delivery: outbox"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-term-ref"])
        self.assertIn("GLS-ORDER-999", r["violations"][0]["message"])

    def test_bare_column_name_in_properties(self):
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            "  - GLS-ORDER-002", "  - order_no"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-term-ref"])
        self.assertIn("order_no", r["violations"][0]["message"])

    def test_mapping_term_dangling(self):
        self.put("table-mapping.yaml", MAPPING.replace(
            "term: GLS-ORDER-004", "term: GLS-ORDER-999"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-term-ref"])

    def test_aggregate_root_dangling(self):
        self.put("aggregate-order.yaml",
                 ORDER_CARD.replace("aggregate: AGG-ORDER-001",
                                    "aggregate: AGG-ORDER-999"))
        r = self.run_check()
        self.assertIn("ddd-term-ref", self.kinds_of(r))
        self.assertIn("AGG-ORDER-999",
                      next(v["message"] for v in r["violations"]
                           if v["kind"] == "ddd-term-ref"))

    def test_value_object_dangling(self):
        self.put("aggregate-order.yaml",
                 ORDER_CARD.replace("value_object: GLS-ORDER-005",
                                    "value_object: GLS-ORDER-999"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-term-ref"])


class Invariant(Base):
    """D3 ddd-invariant：清单缺失/空/三元组缺一=红（防贫血回潮）。"""

    def test_invariants_key_missing(self):
        text = "\n".join(l for l in ORDER_CARD.splitlines()
                         if not l.startswith("invariants:"))
        self.put("aggregate-order.yaml", text + "\n")
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-invariant"])
        self.assertIn("缺 invariants", r["violations"][0]["message"])

    def test_invariants_empty_list(self):
        self.put("aggregate-order.yaml",
                 ORDER_CARD.replace("    method: \"Order.changeQuantity()\"\n",
                                    "    method: \"Order.changeQuantity()\"\n")
                 .replace("""invariants:
  - trigger: "submit（提交订单）"
    expect_fail: "订单项为空则拒，DomainError: EMPTY_ORDER"
    method: "Order.submit()"
  - trigger: "changeQuantity（改行数量）"
    expect_fail: "数量非正数则拒，DomainError: BAD_QUANTITY"
    method: "Order.changeQuantity()"
""", "invariants: []\n"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-invariant"])
        self.assertIn("空", r["violations"][0]["message"])

    def test_invariant_missing_expect_fail(self):
        self.put("aggregate-payment.yaml", PAYMENT_CARD.replace(
            "    expect_fail: \"已支付再扣则拒，DomainError: ALREADY_PAID\"\n", ""))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-invariant"])
        self.assertIn("expect_fail", r["violations"][0]["message"])

    def test_invariant_missing_method(self):
        self.put("aggregate-payment.yaml", PAYMENT_CARD.replace(
            "    method: \"Payment.capture()\"\n", ""))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-invariant"])
        self.assertIn("method", r["violations"][0]["message"])

    def test_invariant_missing_trigger(self):
        self.put("aggregate-payment.yaml", PAYMENT_CARD.replace(
            '''invariants:
  - trigger: "capture（支付扣款）"
    expect_fail: "已支付再扣则拒，DomainError: ALREADY_PAID"
    method: "Payment.capture()"
''', '''invariants:
  - expect_fail: "已支付再扣则拒，DomainError: ALREADY_PAID"
    method: "Payment.capture()"
'''))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-invariant"])
        self.assertIn("trigger", r["violations"][0]["message"])

    def test_invariant_non_dict_entry(self):
        self.put("aggregate-payment.yaml", PAYMENT_CARD.replace(
            """invariants:
  - trigger: "capture（支付扣款）"
    expect_fail: "已支付再扣则拒，DomainError: ALREADY_PAID"
    method: "Payment.capture()"
""", "invariants:\n  - 支付一旦成功不可变\n"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-invariant"])


class Mapping(Base):
    """D4 ddd-mapping：聚合↔表映射不断链（防映射腐烂）。"""

    def test_mapping_aggregate_not_in_design(self):
        self.put("table-mapping.yaml", MAPPING.replace(
            "  - aggregate: AGG-ORDER-003", "  - aggregate: AGG-ORDER-099"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-mapping"])
        self.assertIn("AGG-ORDER-099", r["violations"][0]["message"])

    def test_missing_table_name(self):
        self.put("table-mapping.yaml", MAPPING.replace(
            "      - table: t_payment\n", "      - label: t_payment\n"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-mapping"])
        self.assertIn("表名", r["violations"][0]["message"])

    def test_missing_column_name(self):
        self.put("table-mapping.yaml", MAPPING.replace(
            "          - column: quantity\n", "          - remark: quantity\n"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-mapping"])
        self.assertIn("列名", r["violations"][0]["message"])

    def test_missing_term(self):
        self.put("table-mapping.yaml", MAPPING.replace(
            "            term: GLS-ORDER-003\n", ""))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-mapping"])
        self.assertIn("term", r["violations"][0]["message"])

    def test_empty_mappings(self):
        self.put("table-mapping.yaml", MAPPING.split("mappings:")[0]
                 + "mappings: []\n")
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-mapping"])


class Naming(Base):
    """D5 ddd-naming：重名/前缀合规/事件名形态（照 model-deps 同族口径）。"""

    def test_duplicate_event_name(self):
        self.put("domain-events.yaml", EVENTS.replace(
            "  - event: PAYMENT_SUCCEEDED", "  - event: ORDER_SUBMITTED"))
        r = self.run_check()
        self.assertEqual(set(self.kinds_of(r)), {"ddd-naming"})
        first = r["violations"][0]
        self.assertIn("重复", first["message"])
        self.assertIn("ORDER_SUBMITTED", first["message"])

    def test_duplicate_aggregate_across_cards(self):
        # 副卡改挂他卡聚合：D5 重名 + 映射引用 AGG-ORDER-003 断链级联（真后果，照报）
        self.put("aggregate-payment.yaml",
                 PAYMENT_CARD.replace("aggregate: AGG-ORDER-003",
                                      "aggregate: AGG-ORDER-001"))
        r = self.run_check()
        self.assertIn("ddd-naming", self.kinds_of(r))
        naming = next(v for v in r["violations"] if v["kind"] == "ddd-naming")
        self.assertIn("重复", naming["message"])

    def test_duplicate_repository_name(self):
        self.put("repository-boundaries.yaml", REPOS.replace(
            "  - repository: PaymentRepository", "  - repository: OrderRepository"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-naming"])

    def test_producer_unregistered_prefix(self):
        self.put("domain-events.yaml", EVENTS.replace(
            "    producer: AGG-ORDER-003", "    producer: PAY-001"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-naming"])
        self.assertIn("前缀", r["violations"][0]["message"])

    def test_event_name_not_upper_snake(self):
        self.put("domain-events.yaml", EVENTS.replace(
            "  - event: PAYMENT_SUCCEEDED", "  - event: paymentSucceeded"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-naming"])
        self.assertIn("paymentSucceeded", r["violations"][0]["message"])

    def test_entity_unregistered_prefix(self):
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            "  - entity: AGG-ORDER-002", "  - entity: ORDER-ITEM-1"))
        r = self.run_check()
        self.assertEqual([v["kind"] for v in r["violations"]], ["ddd-naming"])


class FileKind(Base):
    """ddd-file-kind：文件级不可判读（语法错/非映射/kind 未知）——五查之外的结构兜底。

    卡文件不可判读时其聚合声明缺席，其余文件对该聚合的映射引用会连锁报
    ddd-mapping（同 schema_check「语法错文件的定义不收集→他文件悬空照报」的
    跨文件级联先例），故此处只断言 file-kind 在场，不断言红因唯一。
    """

    def _assert_kind_red(self):
        r = self.run_check()
        self.assertIn("ddd-file-kind", self.kinds_of(r))
        self.assertEqual(r["status"], "fail")
        return r

    def test_bad_yaml(self):
        self.put("aggregate-order.yaml",
                 ORDER_CARD.replace("kind: aggregate-card", "kind: [aggregate-card"))
        self._assert_kind_red()

    def test_unknown_kind(self):
        self.put("aggregate-order.yaml",
                 ORDER_CARD.replace("kind: aggregate-card", "kind: aggregateCard"))
        r = self._assert_kind_red()
        self.assertIn("aggregateCard", r["violations"][0]["message"])

    def test_top_level_not_mapping(self):
        self.put("aggregate-order.yaml", "- a\n- b\n")
        self._assert_kind_red()


class BatchAndReview(Base):
    """AC3a failFast 批量报文 + AC3b 人审清单软节。"""

    def test_multi_error_collected_in_one_report(self):
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            "properties:\n  - GLS-ORDER-001",
            "properties:\n  - AGG-ORDER-003.amount\n  - GLS-ORDER-001")
            .replace("""invariants:
  - trigger: "submit（提交订单）"
    expect_fail: "订单项为空则拒，DomainError: EMPTY_ORDER"
    method: "Order.submit()"
  - trigger: "changeQuantity（改行数量）"
    expect_fail: "数量非正数则拒，DomainError: BAD_QUANTITY"
    method: "Order.changeQuantity()"
""", "invariants: []\n"))
        self.put("domain-events.yaml", EVENTS.replace(
            "      - GLS-ORDER-002\n    delivery: outbox",
            "      - GLS-ORDER-999\n    delivery: outbox"))
        r = self.run_check()
        kinds = set(self.kinds_of(r))
        self.assertEqual(kinds, {"ddd-cross-agg-embed", "ddd-term-ref",
                                 "ddd-invariant"})
        self.assertGreaterEqual(len(r["violations"]), 3)
        self.assertEqual(r["status"], "fail")
        self.assertEqual(self.run_rc(), 1)

    def test_zero_event_aggregate_soft_review_exit_0(self):
        self.put("domain-events.yaml", EVENTS.split("  - event: PAYMENT_SUCCEEDED")[0])
        r = self.run_check()
        self.assertEqual(r["violations"], [])
        self.assertEqual(r["status"], "pass")
        self.assertEqual(len(r["review"]), 1)
        self.assertIn("AGG-ORDER-003", r["review"][0])
        self.assertIn("待人审清单", human(r))
        self.assertEqual(self.run_rc(), 0)

    def test_entity_ratio_hint(self):
        # 订单卡 5 实体（>4）→ 粒度软提示；实体 id 唯一不触 D5，词条在 M1 补齐
        extra = "".join(
            f"  - id: AGG-ORDER-{n:03d}\n    name: 附属实体{n}\n    alias: Sub{n}\n"
            f"    aggregateType: AGGREGATE_ROOT\n    attributes: []\n"
            for n in (4, 5, 6, 7))
        write(self.onto / "order" / "m1-object-model.yaml",
              M1_YAML.replace("  - id: AGG-ORDER-003", extra + "  - id: AGG-ORDER-003"))
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            """entities:
  - entity: AGG-ORDER-002
    properties:
      - GLS-ORDER-003
      - GLS-ORDER-004
value_objects:""",
            """entities:
  - entity: AGG-ORDER-002
    properties:
      - GLS-ORDER-003
      - GLS-ORDER-004
  - entity: AGG-ORDER-004
    properties:
      - GLS-ORDER-003
  - entity: AGG-ORDER-005
    properties:
      - GLS-ORDER-003
  - entity: AGG-ORDER-006
    properties:
      - GLS-ORDER-003
  - entity: AGG-ORDER-007
    properties:
      - GLS-ORDER-003
value_objects:"""))
        r = self.run_check()
        self.assertEqual(r["violations"], [])
        self.assertEqual(len(r["review"]), 1)
        self.assertIn("实体", r["review"][0])
        self.assertEqual(self.run_rc(), 0)


class ExitCodes(Base):
    """AC4 退出码 0/1/2 契约。"""

    def test_exit_0_green(self):
        self.assertEqual(self.run_rc(), 0)

    def test_exit_1_violation(self):
        self.put("domain-events.yaml", EVENTS.replace(
            "      - GLS-ORDER-002\n    delivery: outbox",
            "      - GLS-ORDER-999\n    delivery: outbox"))
        self.assertEqual(self.run_rc(), 1)

    def test_exit_2_target_missing(self):
        rc = quiet_main(["--ontology", str(self.onto),
                         str(Path(self.tmp.name) / "nope")])
        self.assertEqual(rc, 2)

    def test_exit_2_design_dir_empty(self):
        (self.design / "README.md").write_text("只有文档没有设计件", encoding="utf-8")
        for name in list(GREEN):
            (self.design / name).unlink()
        self.assertEqual(self.run_rc(), 2)

    def test_exit_2_ontology_without_schema(self):
        bare = Path(self.tmp.name) / "bare-onto"
        bare.mkdir()
        rc = quiet_main(["--ontology", str(bare), str(self.design)])
        self.assertEqual(rc, 2)

    def test_exit_2_ontology_without_domain(self):
        (self.onto / "order" / "manifest.json").unlink()
        rc = self.run_rc()
        self.assertEqual(rc, 2)


class ResolutionFamilyAlignment(Base):
    """与 schema_check 解析族口径对齐（票 51 设计裁决：独立实现、口径单测钉死）。"""

    def test_ref_value_not_self_certifying(self):
        # 本体里 ref 键值（targetAggregate）不进词条集合——悬空照报（防自引用洗白）
        self.put("aggregate-order.yaml",
                 ORDER_CARD.replace("aggregate: AGG-ORDER-001",
                                    "aggregate: AGG-GHOST-001"))
        r = self.run_check()
        self.assertIn("ddd-term-ref", self.kinds_of(r))

    def test_unregistered_prefix_not_collected(self):
        # 聚合主词条无注册前缀：ID-role 形态归 D5 naming（D2 红因不混）；副卡聚合
        # 缺席使映射引用连锁断链（真后果，级联照报，见 FileKind 类注释）
        self.put("aggregate-order.yaml",
                 ORDER_CARD.replace("aggregate: AGG-ORDER-001",
                                    "aggregate: XX-ORDER-1"))
        r = self.run_check()
        self.assertEqual(self.kinds_of(r)[0], "ddd-naming")
        self.assertIn("XX-ORDER-1",
                      next(v["message"] for v in r["violations"]
                           if v["kind"] == "ddd-naming"))

    def test_dict_ids_collected(self):
        write(self.onto / "order" / "m1-object-model.yaml",
              M1_YAML + "data_dictionaries:\n  - id: DICT-ORDER-001\n"
                        "    name: 订单状态字典\n")
        self.put("aggregate-order.yaml", ORDER_CARD.replace(
            "  - GLS-ORDER-002\nentities:", "  - DICT-ORDER-001\nentities:"))
        r = self.run_check()
        self.assertEqual(r["violations"], [])


if __name__ == "__main__":
    unittest.main()
