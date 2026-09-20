# 票 51：tools/ddd_check.py + fixtures 第八套（脚本轨 TDD）

Status: todo

> 注（L0 拆票时点）：依赖票 50（设计件格式真源与样例以其为准）。闸与出厂集同票（负变体即闸的测试）。
Belongs to: docs/第四期DDD线拆票方案.md 批次一；references/ddd-as-code-digest.md §3/§6；PRD F15
Touches: tools/ddd_check.py、tools/test_ddd_check.py、fixtures/ddd-modeler/、specs/ddd-modeler.md（断言表填充）、lessons/51

## What to build

`tools/ddd_check.py`——DDD 设计件闸（schema_check 同款风格），五查：

| # | 检查 | 判定 | 违规码 |
|---|---|---|---|
| D1 | 跨聚合内嵌 | 跨聚合引用必须是 ID，不得内嵌对方属性（防 JOIN 暗桩） | `ddd-cross-agg-embed` |
| D2 | 词条解析 | 聚合字段/事件载荷必须解析到本体词条 ID（复用 schema_check 悬空引用解析族与 model-deps.json idPrefixes 口径） | `ddd-term-ref` |
| D3 | 不变量齐备 | 每聚合不变量清单非空，每条三元组齐（触发操作/期望失败/指向方法，方法须在该聚合卡内可指） | `ddd-invariant` |
| D4 | 映射不断链 | 聚合↔表映射中的表/列在映射文件内可解析 | `ddd-mapping` |
| D5 | 命名合规 | 设计件内重名/ID 前缀合规（照 model-deps 同族口径） | `ddd-naming` |

工程形态：

- **一次收集全部错误批量返回**（failFast=false，digest §6 #3），不逐条打回；
- 报告含**"待人审清单"软节**（聚合粒度合理性提示：如聚合数/实体数比异常、单聚合零事件——只报告不影响退出码，digest §3 边界）；
- 退出码契约 0 绿 / 1 红 / 2 配置错（--check 家族同族）。

fixtures 第八套 `fixtures/ddd-modeler/`：最小订单域绿灯样本（本体输入→期望聚合卡/事件表/映射输出）+ 负变体 ×5（D1–D5 各一），断言表落 fixture_run 四类断言，注源本票 AC 表。

## 设计裁决（L0 已定）

- 词条解析复用 schema_check 解析族（裁决点 3），不新造 ID 解析器；ddd_check 与 schema_check 的关系 = 同族分工（schema_check 闸 ontology/，ddd_check 闸 design/ddd/）。
- 第一版只闸设计卡 YAML；代码级闸（跨聚合 JOIN/裸 UPDATE）明示不做（裁决点 1）。
- 人审清单软节不进退出码——粒度/完备性永远是人审（裁决点 1 后半）。

## 验收（注源）

- [ ] AC1 D1–D5 负变体各红、红因可指认（源：本票 AC 表）
- [ ] AC2 绿灯样本（最小订单域）绿（源：本票 AC 表）
- [ ] AC3 批量报文断言：多错误一次收齐（failFast=false）+ 人审清单软节在场不影响退出码（源：本票 AC 表）
- [ ] AC4 退出码 0/1/2 契约断言（源：本票 AC 表）
- [ ] AC5 specs/ddd-modeler.md 断言表填充注源本票（源：实读）
- [ ] AC6 `bash tools/ci.sh` 四闸绿（源：CI）

## 交接包（L2 自主档）

任务: ddd_check 五查+第八套出厂集。
先读: design/ddd/README.md（票 50 格式真源——判定基准必须从它反推）；tools/schema_check.py（报告结构/退出码/悬空引用解析族——D2 复用点）；ontology/schema/model-deps.json（idPrefixes）；fixtures/schema_check/（出厂集正负变体组织先例）；docs/第四期DDD线拆票方案.md 批次一。
框架红线: 无点名框架；纯 Python 标准库 + PyYAML（技术栈表既定）。
边界红线: 只动 Touches 清单；不闸 ontology/（schema_check 的地盘）；人审清单不进门禁。
产出: ddd_check.py+单测+fixtures/ddd-modeler/（绿灯+负变体×5）+specs/ddd-modeler.md 断言表+lessons/51。
验收: AC1–6 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径+六项 AC 实证+ci.sh 摘要+偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1a | 聚合卡内嵌他聚合属性（负变体） | ddd-cross-agg-embed 红 |
| AC1b | 事件载荷词条 ID 悬空（负变体） | ddd-term-ref 红 |
| AC1c | 聚合不变量清单为空/三元组缺项（负变体） | ddd-invariant 红 |
| AC1d | 映射表指向不存在列（负变体） | ddd-mapping 红 |
| AC1e | 设计件内重名（负变体） | ddd-naming 红 |
| AC2 | 最小订单域全套设计件 | 绿 |
| AC3a | 含 ≥3 类错误的样本 | 一次报文收齐全部错误 |
| AC3b | 粒度异常样本（如单聚合零事件） | 人审清单软节在场、exit 仍 0 |
| AC4 | 正常/违规/配置错三路径 | exit 0/1/2 |
| AC5 | specs/ddd-modeler.md | 断言表与出厂集一一对应 |
| AC6 | CI | 四闸全绿 |
