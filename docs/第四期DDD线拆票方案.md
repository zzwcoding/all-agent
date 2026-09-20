# 第四期 DDD 线拆票方案（ddd-modeler 三件套，2026-09-20）

> 用法：Owner 拍板后按此方案拆票施工。规划输入 = `docs/ddd-modeler-建造交接包.md`（已对齐共识勿重新论证）；外部依据 = `references/ddd-as-code-digest.md`（Context Mapper / Event Modeling / jMolecules / Codely Blueprint / TUM 论文）。
> 全局纪律：脚本轨 TDD / skill 轨出厂集先行；一票一提交；约定不落闸等于没有；批收官六条清单。

## 开放问题逐条结论（交接包 §7，待 Owner 拍板）

| # | 问题 | 本方案建议 | 依据 |
|---|---|---|---|
| 1 | 第一版闸什么 | **只闸设计卡 YAML 的图结构规则**（五查见票 51），代码级闸（跨聚合 JOIN/裸 UPDATE）后置到有真实被建项目；粒度/完备性不硬闸，输出"待人审清单" | 交接包建议 + 调研 §3（结构可机判、语义靠评审是业界实证的边界） |
| 2 | Saga/事件运行时 | **不入第一期**：只到聚合+事件表设计件；Outbox/MQ 由被建项目按需建，skill 不预建 | 交接包建议 |
| 3 | 词条 ID 机检格式 | **复用现有机制不新造**：`ontology/schema/model-deps.json` 的 idPrefixes + schema_check 的悬空引用解析族；ddd_check 借同一解析口径判"载荷→词条 ID"。check_citations 是答案文件专用，不直接复用 | 仓内实查（schema.md §2 + 票 38 同族机制） |
| 4 | 设计件落盘位置 | **新目录 `design/ddd/<域>/`**（设计件是被建域的产物，与 `ontology/<域>/` 平级；specs/ 是 skill 卡与功能 spec 的家，不混）；repo-layout.json 登记 + archive-registry 新产物类（status 草案/已审，进仓走 MR 人审，非派生物不走 --check） | 归档闸纪律：新目录必登记否则红 |
| 5 | 与 F9 的接口 | **第一期不改 F9**：聚合卡作为可选增强输入预留，F9 消费面不动 | 交接包建议 |
| 6 | 批次排序 | **DDD 线四票先跑**（纯工程自走）；A 线（26 提案/第二域）等业务节奏互不阻塞。挂账项：L5 首跑发现的 **Q8 参照答案内部矛盾** 待开票——建议并入本线票 53 或单独小票，随拍板定 | 交接包 §0 锚点 + lessons/48 |
| 7 | 票拆法 | 调整为 **50–53 四票**（见下；交接包原拆法的 ②闸 与 ③出厂集合并进一票——负变体就是闸的测试，同票才不违反"出厂集先行"） | sdd-flow2 阶段 5 双轨纪律 |

## PRD 同步（批准入账时第一笔提交含）

- 功能清单增 **F15 DDD 建模线（选配）**：做什么 = 本体模型+行为清单 → 聚合卡/事件表/映射/仓储边界设计件（YAML，机器可闸）；不做什么 = 不生成代码（F9/sdd-flow 的事）、不预建事件运行时、不硬闸粒度合理性。
- 选配判断表（交接包 §5）落 F15 条目内。
- PRD 状态行**不翻回逼问中**：本需求的 11 维逼问已由 Owner-AI 对齐对话完成（交接包 §2 共识即逼问产物），按变更路由精神以变更记录追加。

## 批次一（票 50–51：规范+闸）

### 票 50：DDD 设计件规范 + ddd-modeler 开卡（阶段 2/3 性质）

- 范围：
  1. **设计件格式真源**（新建 `design/ddd/README.md` 或 specs 侧格式文档）：四类 YAML——聚合卡（aggregate_root 标记 / 属性 `- 词条ID` 引用 / 实体值对象区分 / **不变量三元组：触发操作→期望失败→指向聚合方法** / Corrective Policies / Ways to access）、领域事件表（事件名 / 载荷=词条 ID 表 / 生产聚合→消费聚合）、聚合↔表映射、仓储边界声明。字段骨架抄 CML+Codely（digest §1/§4）。
  2. **modules.md 开卡**：`skill: ddd-modeler`（层 L1 工序；触发面=选配路由；reads ontology/<域>+schema；writes design/ddd/<域>/ 草案；依赖 schema_check/ddd_check；边界=只产草案走 MR、不做代码生成、无词条不建模）。
  3. **边界规则增条**：ddd-modeler 不读生成器 skill 私件；design/ddd/ 只由 ddd-modeler 工序写入（草案制）。
  4. **布局与归档登记**：repo-layout.json 增 `design/ddd/` 目录；archive-registry 增 design-card 产物类（status 合法值：草案/已审）。
  5. `specs/ddd-modeler.md` 功能规格（含出厂集断言表骨架，票 51/52 填充）。
  6. 架构图 all-agent.html 插入 ddd-modeler 一格（流水线：onto-modeler → ddd-modeler → F9），随票报 Owner 过目。
- 验收：卡格式合规（skill-module-format）+ 边界闸消费新规则 + 归档闸认新目录与产物类 + 四闸全绿。

### 票 51：tools/ddd_check.py + fixtures 第八套（脚本轨 TDD）

- 范围：五查（违规码 ddd-*）：
  1. `ddd-cross-agg-embed` 跨聚合引用必须是 ID，不得内嵌对方属性（防 JOIN 暗桩）；
  2. `ddd-term-ref` 聚合字段/事件载荷必须解析到本体词条 ID（复用 schema_check 解析族，悬空=红）；
  3. `ddd-invariant` 不变量清单非空且每条三元组齐备（触发操作/期望失败/指向方法——防贫血回潮）；
  4. `ddd-mapping` 聚合↔表映射的表/列在映射文件可解析（防映射腐烂）；
  5. `ddd-naming` 重名/ID 前缀合规（照 model-deps 同族口径）。
- 工程形态：**一次收集全部错误批量返回**（failFast=false，调研 §5 先例）；报告含"待人审清单"软节（粒度合理性提示，不影响退出码）；退出码 0/1/2 同族。
- fixtures 第八套 `fixtures/ddd-modeler/`：最小订单域绿灯样本（本体输入→期望聚合卡输出）+ 负变体 ×5（五查各一），断言表注源票面 AC。
- 验收：五查负变体各红、绿灯样本绿、批量报文断言、四闸全绿。

## 批次二（票 52–53：skill+走查）

### 票 52：ddd-modeler skill 正文（skill 轨出厂集先行）

- 范围：SKILL.md + references/ 私件。核心工序（调研 §2 切片法 + TUM 教训固化）：
  1. 术语锚定（无词条不建模——输入必须是本体模型产物，缺词条先回 onto-modeler/提案池）；
  2. 事件时间轴 → 命令 → 聚合候选：逐轮产结构化 YAML 中间件落盘，**每步新鲜上下文、只喂上一步定稿**；
  3. **"合并候选上下文"显式追问步**（对冲 LLM 切碎偏差）；
  4. 聚合卡/事件表/映射成稿 → ddd_check 自检 → 待人审清单 → 草案走 MR；
  5. 副产物：设计件→Mermaid 图（人审靠图）。
- 出厂集：固定本体输入 → 断言产出的聚合卡结构与工序中间件清单（断言类型照 fixture_run 四类）。
- 验收：出厂集先行红→绿 + 安装位双落零漂移 + 边界闸过 + 四闸全绿。

### 票 53：文档对齐 + 端到端走查 + 挂账清偿（小票）

- 范围：PRD F15 转正为已建 + CONTEXT.md 增「DDD/聚合卡」词条 + AGENTS.md 锚点 + **最小订单域端到端实弹**（本体草案→ddd-modeler 全工序→ddd_check 绿→人审清单产出，走查留痕 docs/walkthrough/）+ Q8 参照答案矛盾修复（若拍板并入本票）。
- 验收：走查留痕在场 + 文档对齐 + 四闸全绿。

## 四闸影响分析

| 闸 | 影响 |
|---|---|
| 脚本单测 | +ddd_check 测试组（票 51） |
| 出厂集回归 | 7 套 → 8 套（fixtures/ddd-modeler/） |
| skill 边界闸 | +ddd-modeler 卡与依赖行（票 50）；豁免清单预期零新增 |
| 归档闸 | +design/ddd/ 目录登记 + design-card 产物类（票 50） |

## 批收官清单适配

六条照跑（探针/锚点/审查落盘/豁免复核等）；新增候选：ddd_check 对仓内真实 design/ 目录的全量跑（有真实设计件后挂批收官软闸，票 53 定）。

## 明确不做（本方案外）

- 代码级闸（跨聚合 JOIN/裸 UPDATE 静态检查）——等真实被建项目
- Saga/Outbox/MQ 运行时件、F9 消费聚合卡、代码生成
- 粒度/完备性硬闸（永远是"人审清单"，不是闸）
- A 线（26 提案裁决/第二域）——等业务输入，与本线互不阻塞

## 批收官

四票跑完做总收官：meta_probe 留痕 + 豁免复核 + 锚点推进（第四期 DDD 线完）+ 收官记录追加二期收官报告。
