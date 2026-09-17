# sdd-flow2 设计案：skill = 深模块（待拍板）

状态: 提案（2026-09-17）。本文回答：如何把 sdd-flow 的深模块纪律施加到 skill+脚本系统上，以及 sdd-flow2 自身怎么改。拍板后动手改 sdd-flow2 正文。

## 0. 出发点

- All-agent 大框架走 skill+脚本路线（已拍板，不建代码系统）。
- skill 以后会变多 → 每个 skill+脚本视为一个**代码模块**，深模块/模块卡纪律全套施加：边界、依赖、输入输出、测试、归档，全部严格规定。
- sdd-flow2 是大框架的一环，且自身由 skill 组成 → **sdd-flow2 是本纪律的第一个被治理对象（dogfooding）**。
- 结构思想：大模块包含小模块、层层封装、**渐进披露**——每层入口只放"何时用+接口"，细节下沉。

## 1. 分层模型（四层半，依赖只许向下）

| 层 | 是什么 | 例子 | 渐进披露形态 |
|---|---|---|---|
| L0 编排层 | 路由器 skill：阶段路由+产物契约，**不干活** | sdd-flow2、未来 allagent 编排器 | SKILL.md 薄：何时用/路由表/产物清单 |
| L1 工序层 | 变换器 skill：一类输入→一类输出 | 需求探索/DB逆向/代码逆向/应用生成/变更影响分析（≈12 个封顶） | 正文放主干流程，格式细节下沉 references/ |
| L2 共享规约层 | 纯只读数据：格式模板、Schema 文档、公共指导段落 | references/*.md、ontology-schema/ | 无逻辑，被引用 |
| L3 确定性脚本层 | 可测试的闸与工具 | tools/schema_check.py、semci、出厂集 runner、skill 边界闸 | CLI 签名即接口 |
| L4 数据层 | 本体仓 YAML、fixtures、policies、lessons、ADR | ontology/**、fixtures/** | 被治理对象 |

规则：
- **依赖只许向下**：L0→L1→L2/L3→L4；同层调用必须显式声明并记理由；下层不许感知上层。
- **每层的"公开接口"**：L0/L1 = frontmatter description（机器路由接口）+ reads/writes 契约；L3 = CLI 签名；L2/L4 = 文件路径模式 + schema 版本。
- 深模块判定不变：接口（何时用/进什么/出什么）必须明显比实现简单；浅 skill（正文就是全部，接口含糊）= 设计错误，合并或下沉。

## 2. skill 卡（模块卡的 skill 变体）

每个 L0/L1 skill 一张卡，集中在仓的 `specs/modules.md`（与椒图同构）。字段：

```
## skill: <名>
- 职责: <一句话>
- 目录: skills/<名>/
- 触发面: <description 的触发条件——机器路由依据>
- reads: <输入契约：读哪些文件/YAML，路径模式 + schema 版本>
- writes: <输出契约：产出哪些文件，落盘路径>
- 依赖:
  - skill: <显式声明>
  - script: tools/<名>
  - data: ontology/**
- Seam 与出厂集: fixtures/<名>/ 路径；断言方式；stub 输入
- 边界: 不许读 <其他 skill 的私有 references>
```

对应关系（点题）：skill 卡 ≈ 本体 M2 行为模型——触发面 = triggerType，reads = 前置条件，writes = 后置条件；L0 编排的阶段路由 ≈ M6 流程模型；出厂集走查 ≈ M4 场景。**大框架用自己的词汇建造自己**。

## 3. 五件严格规定

### 3.1 边界（机器化）
- `tools/skill_deps_check.py`：扫每个 skill 正文/references 里的文件引用路径，对卡的依赖行与"边界"字段——引用未声明的路径 = CI 红。
- 前端 skill 禁直连后端 skill 私有文件这条大框架铁律，落成闸的一条规则。

### 3.2 依赖
- 卡上显式依赖行（skill/script/data 三类），无环自查沿依赖行走一遍。
- 新增依赖 = 改卡（回阶段 2），不许 skill 正文里私拉。

### 3.3 输入输出契约
- reads/writes 精确到路径模式 + schema 版本；产出**必须落盘**（产物即状态），不许只留在对话里。
- 契约变更 = 接口变更，走铁律：停下回报，回阶段 2 改卡。

### 3.4 测试（双轨）
- **脚本轨（L3）**：真单测，TDD 不变。
- **skill 轨（L0/L1）**：**出厂集 = skill 的测试**。`fixtures/<skill>/` 固定输入 + 断言集。断言必须**确定性可判**：结构断言（产出含哪些节）、ID/路径引用断言、schema 校验、diff 断言（脚本类）；AI 产出的质量判断留给人审——Coyle 原则的落地："断言在门口，人在账房"。
- **出厂集先行 = skill 界的 TDD**：先写 fixtures+断言，再写指导书正文。红→绿同样成立。
- 回归：`tools/fixture_run.py` 全量跑出厂集，CI 门槛 = 全过 + 负样本不误报（双门槛）。

### 3.5 归档记录
- skill 变更记 CHANGELOG（语义变更 = 版本号，元模型纪律）。
- lessons/ 施工日志（每票一篇：做了什么、坑、取舍）。
- 设计决策记 ADR。
- 卡随实现事实同步（出入回阶段 2，不许就地改）。

## 4. sdd-flow2 自身的改造点（相对 sdd-flow 的 diff）

1. 阶段 0：项目类型识别——skill+脚本项目 → 读本文件；CI = 脚本单测 + 出厂集回归 + skill 边界闸 + schema 校验（无构建链）。
2. 阶段 2：模块卡 → **skill 卡**（§2 格式）；深模块准则沿用，判定对象换成 skill。
3. 阶段 3：spec 的验收测试表 → **出厂集断言表**（每条断言确定性可判）。
4. 阶段 5 实现拍：脚本走 tdd；skill 走"出厂集先行"；互动/自主分档不变。
5. 阶段 6：CI 模板换成 skill+脚本版（无 lint/类型，有 fixture_run + skill_deps_check + schema_check）。
6. 阶段 7：体检新增 **skill 腐烂检测**——指导书与规范漂移、出厂集长期未跑、两 skill 段落雷同（→ 抽 L2 共享 reference）。
7. 窗口分层/交接包/失败处理/变更路由：**不变，全部继承**。

## 5. dogfooding：sdd-flow2 第一个被治理

- sdd-flow2 自己先写卡：它调用的底层 skill（tdd/grilling/codebase-design…）声明为**外部依赖**；它的 references/ 七件逐一登记 L2 层。
- sdd-flow2 的出厂集：用一个迷你项目（All-agent 自己的第一张票）走全流程，断言 = 各阶段产物齐备、状态流转正确。

## 6. 建造顺序（拆票预告）

- 票 00：骨架 + `references/skill-module-format.md`（卡格式真源）+ sdd-flow2 自卡落 specs/modules.md
- 票 01：`tools/skill_deps_check.py` 边界闸 + `tools/fixture_run.py` 出厂集 runner + **归档登记表 + `tools/archive_check.py` 归档闸**（验收主线 2）+ CI 骨架
- 票 02：sdd-flow2 正文改造（§4 的 7 处 diff）
- 票 03 起：用 sdd-flow2 造 All-agent 的第一个 skill（本体仓 schema + schema_check）

## 拍板点

1. 四层半切法与"依赖只许向下"
2. skill 卡字段（§2）
3. 出厂集先行纪律 + 断言确定性红线（§3.4）
4. 改造顺序（§6）

## 两条验收主线（2026-09-17 用户拍板时收敛）

建造 sdd-flow2 的成败按这两条验收，先于四个拍板点：

1. **结构一致**：造完的真实结构 = 本设计案的四层半。机器验证，不目测——卡与文件一一对应（无孤儿 skill、无卡外文件）、依赖只许向下（边界闸扫）、sdd-flow2 自卡齐全且第一个被治理。
2. **统一口径归档（强力约束）**：所有文档类产物一个口径归档。分两级，真源都收在 sdd-flow2（跨项目唯一）：
   - **跨项目骨架统一**（治"不同项目目录结构不一致"）：`repo-layout.md` 升级为**机读布局表**（目录 → 用途 → 允许的文件类型 → 产生者），sdd-flow2 references 内置一份，所有项目共用；阶段 0 从该表**生成**骨架（不是参考着建）；项目特有目录走白名单登记（声明+理由），未登记目录 = 闸红。
   - **项目内产物归档**：**归档登记表**先行——每类产物 → 唯一路径模式（引用布局表）+ 模板真源 + 状态字段 + 谁翻转（覆盖 skill 卡/出厂集/断言表/票/施工日志/ADR/CHANGELOG/本体 YAML）。
   - **`archive_check` 脚本进 CI**：仓内每个文件必须对得上布局表+登记表（命名/位置/必备字段/状态合法值），对不上 = 孤儿文件/非法目录，CI 红。
   - **每票收尾**：从"回写五件齐全"升级为"过归档闸才算完"——状态翻转以归档闸绿为前提。
