# Event Modeling 切片法操作细则（ddd-modeler 工序步 2–5 细则；全文域无关）

> 依据：本仓调研落盘《ddd-as-code 方法论》§2/§6（事件建模四积木 + TUM 2026 教训）。
> 对冲两个已知偏差：①五步 LLM 框架里聚合设计/技术映射两步**误差累积后不可用，修复比重来更贵**；
> ②LLM 切聚合倾向**偏碎**。对策两件：每轮新鲜上下文只喂上轮定稿（§3）+ 合并候选显式追问（§4 轮 4）。

## 1. 轮次总表

| 轮 | 中间件文件（`tmp/ddd/<域>/`） | 产物 | 合格判据 |
|---|---|---|---|
| 1 | round-1-event-timeline.yaml | 事件时间轴 | 每事件动宾过去式+词条锚+来源线索 origin |
| 2 | round-2-commands.yaml | 命令清单 | 每命令挂触发事件+发起方（或如实记系统/外部） |
| 3 | round-3-aggregate-candidates.yaml | 聚合候选 | 每候选=词条根+成员词条+一句一致性锚 |
| 4 | round-4-merge-review.yaml | 合并追问记录 | 逐组追问+裁决（merge/keep-apart/pending）+定稿候选 |

## 2. 各轮操作

- **轮 1 事件时间轴**：把行为/规则清单素材按业务时间铺成事件流。全部事件先铺（含疑似单聚合内部流转），成稿时再按格式真源 §2 筛（跨聚合事件才进事件表）。每事件记：时间轴位置（自然语言锚）、涉及词条、来源线索。
- **轮 2 命令**：只读轮 1 定稿，为每个事件找触发命令与发起方；找不到命令的事件（定时任务/外部系统）`origin` 如实记，不硬造 actor。
- **轮 3 聚合候选**：只读轮 2 定稿。名词词条为候选根；成员词条按"哪个命令改它"归组；每候选写一句**一致性锚**——什么数据必须同时成立/同时改/不出现中间态。这一步**只列候选不合并**，切碎了没关系，轮 4 收口。
- **轮 4 合并追问（必走步）**：只读轮 3 定稿。逐组提问：**"这几个候选是否必须同时成立/同时改？"** 判据满足→`verdict: merge`（记 `merged_into`）；不满足→`verdict: keep-apart`；有疑义→`verdict: pending`，问题原样进《待人审清单》，**成稿挂起等 Owner 裁决，不擅自合并也不机械拆分凑数**。`resolved_candidates` 是成稿的唯一输入。

## 3. 新鲜上下文轮换纪律（硬规则，TUM 教训的落地）

1. **一轮一会话**：每轮定稿落盘后本轮结束；下一轮**新开上下文**，只喂上一轮定稿中间件文件——禁止把前几轮的对话、草稿、解释散文一起带过去（散文累积=误差温床）。
2. **喂定稿不喂过程**：下一轮输入=上一轮定稿文件本体；上一轮的 open_questions 未决条目不流入下一轮主体清单，只能原地挂起或转《待人审清单》。
3. **留痕**：每份中间件 `input_of_round` 字段写明本轮消费的定稿文件（轮 1 写本体域目录）——链条本身可机核（出厂集断言钉轮 2→1、轮 3→2、轮 4→3）。
4. **中间件是工作件不是设计件**：无 status 字段、不写 design/ddd/、不进 MR；运行时落 `tmp/ddd/<域>/`（tmp/ 不入仓，归档闸与五查闸都不见它），成稿后由运行方自行清理。过程档案若 Owner 要留，走 MR 另议，不随设计件进仓。

## 4. 中间件 YAML 文件格式

公共头（四轮一致）：

```yaml
# 工序中间件·轮 N/4：<artifact 名>（ddd-modeler 工序；工作件不入仓）
round: <N>
artifact: <event-timeline | commands | aggregate-candidates | merge-review>
domain: <域>                                    # 与 ontology/<域>/ 同名
input_of_round: <上轮定稿路径；轮 1 填本体域目录>
<主体清单>                                       # 各轮字段见下
open_questions: []                               # 或逐条列出（轮 4 为 pending_questions）
```

各轮主体清单字段：

```yaml
# 轮 1：events[]
  - event: <动宾过去式大写下划线>
    position: <时间轴位置，自然语言>
    terms: [<词条 ID>...]                        # 事件涉及词条（引用即类型）
    origin: <来源线索：行为/规则清单出处>

# 轮 2：commands[]
  - command: <动宾>
    actor: <发起方>
    triggers_event: <轮 1 事件名>
    terms: [<词条 ID>...]

# 轮 3：candidates[]
  - candidate: <聚合根词条 ID>
    member_terms: [<成员词条 ID>...]
    consistency_anchor: <一句：什么必须同时成立/同时改>

# 轮 4：merge_questions[] + resolved_candidates[] + pending_questions[]
  - question: <候选 A 与 B 是否必须同时成立/同时改？>
    candidates: [<候选词条 ID>...]
    answer: <判据事实>
    verdict: <merge | keep-apart | pending>
    merged_into: <verdict=merge 时必填：并入哪个候选>
    decided_by: <Owner | 待 Owner>
  - aggregate: <定稿聚合根词条 ID>
    absorbed: [被并入的候选词条 ID...]
```

本文件不复制设计件字段 schema——成稿格式唯一真源是 `design/ddd/README.md`，中间件格式真源是本节（出厂集样例与之互为镜像）。

## 5. 成稿映射（中间件 → 四类设计件）

| 设计件 | 来源 | 要点 |
|---|---|---|
| 聚合卡 aggregate-card | 轮 4 定稿候选 + 轮 1/2 | 不变量三元组从事件/命令反推：命令触发=trigger、拒答条件=expect_fail、聚合方法=method |
| 领域事件表 domain-events | 轮 1 只收跨聚合事件 | 单聚合内部流转不进表；载荷=词条 ID 表禁裸列名 |
| 聚合↔表映射 table-mapping | 聚合卡属性 | 表列↔词条双向可解析；谁的表谁写 |
| 仓储边界 repository-boundaries | 每聚合恰一仓储 | 只返回本聚合整体，不暴露逐字段更新 |

字段 schema 一字照格式真源；草案头固定注释「设计件=草案，业务裁决待 Owner 确认」+ `status: 草案`；成稿即跑五查自检（工序步 4）。

## 6. Mermaid 图导出（副产物，人审靠图）

- 聚合卡 → `classDiagram`：聚合/实体/值对象为类，不变量方法入类，跨聚合引用不画线（只画事件流）；
- 事件表 → `flowchart LR`：生产聚合→事件→消费聚合，逐事件一链；
- 映射 → `erDiagram`：聚合↔表投影关系。

三图合成 `design/ddd/<域>/diagrams.md`，与《待人审清单》一起交 Owner——设计评审靠图，不靠逐行读 YAML。
