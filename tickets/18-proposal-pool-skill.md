# 票 18：proposal-pool skill（业务语义循环自动化核心票）

Status: done
Belongs to: 第二批拆票方案（2026-09-19 用户批准）；PRD F13；CONTEXT.md 业务语义循环；收官报告 §7 建议二
Touches: skills/proposal-pool/、tools/proposal_check.py、fixtures/proposal-pool/、specs/modules.md、.skill-deps-allow、docs/proposals/、lessons/18

## What to build

- 二期占位卡转正：skill proposal-pool（薄壳 + references）+ 双落安装位
- 提案文件规范 + L3 工具 proposal_check（确定性冲突检测）+ 出厂集

## 设计裁决（L0 已定）

- **触发面**（卡与 frontmatter 一字不差）：「把这条信号起草成提案/过一遍提案池/查提案池状态」。卡转正=把 modules.md 占位卡扩成完整卡（职责/层 L1 工序/目录双位置/reads/writes/依赖/Seam/边界全填）。
- **提案文件规范**：`docs/proposals/PROP-<域>-<NNN>.md`；必备字段（YAML 头）：`id / title / status(draft|open|accepted|rejected) / source-signal(kind: 拒答|疑点|对账缺口|监督|交互; ref: 证据路径[#锚点]) / target(model, element) / change(add|modify|deprecate) / rationale`；正文=草案内容与证据展开。**自动化止于提案**：不起 git 分支、不直改 ontology/**。
- **proposal_check.py 职责**（确定性）：①必备字段与枚举值自检（`proposal-schema`）；②target 存在性：modify/deprecate 时元素必须已在仓、add 时必须不存在（`proposal-target`，防重复建）；③池内冲突：同 target 元素的两个 open 提案 change 类型矛盾 → `proposal-conflict`；④source-signal.ref 证据文件必须存在（`proposal-evidence`，#锚点容许）。只解析 `PROP-*.md`，目录内其他文件（如对账 README）跳过。退出码 0/1/2 对齐仓内约定，--json 机读。
- **边界闸**：卡声明 script=`tools/proposal_check.py`、data=`ontology/**`、reads=`docs/proposals/**`；Seam=fixtures/proposal-pool/（.skill-deps-allow 加一行豁免带理由，照票 05 手法）。
- 双落安装位 + sync——新 skill 入 install-registry 注册表（票 15 AC6 的实弹路径）。

## 验收（注源）

- [x] AC1–6 全过（源：本票 AC 表）
- [x] 卡触发面与 frontmatter 一致、边界闸无违规（源：字段纪律 1、边界铁律 4）
- [x] 安装位双落零漂移且注册表含 proposal-pool（源：票 15）

## 交接包（L2 自主档）

任务: proposal-pool skill + proposal_check 工具 + 出厂集 + 卡转正。
先读: specs/modules.md（占位卡现状与四张一期卡的成色基准）；skills/db-reverse/SKILL.md（薄壳范本）；tools/schema_check.py 与 check_citations.py 的 CLI/单测风格；tools/fixture_run.py 断言类型；tools/install_skills.py（sync 入注册表路径）；docs/reviews/ 两报告（三源信号提法）；CONTEXT.md 业务语义循环定义；lessons/15（注册表机制）。
框架红线: 出厂集先行红→绿；proposal_check 确定性零 LLM、TDD；卡依赖纪律（正文反引号只许已声明面：`tools/proposal_check.py`/`ontology/**`/`docs/proposals/**`/自身文件/Seam）；全量绿灯红线（现有四闸零破坏）。
边界红线: 只动票面 Touches 清单；不动 ontology/ 真域本体文件；docs/proposals/ 本票只落规范说明（README 或样例若出厂集需要——真提案是票 19 的事）。
产出: 卡转正 + skills/proposal-pool/{SKILL.md, references/}（起草工序：信号受理→归一格式→冲突预检→提案落盘→状态流转纪律；细则下沉 references）+ tools/proposal_check.py + 单测 + fixtures/proposal-pool/（正例提案 2 份 + 负变体：字段缺失/modify 不存在元素/add 已存在元素/同靶冲突/证据路径不存在）+ modules.md 卡与脚本清单 + .skill-deps-allow 行 + lessons/18 + 安装位 sync 与 --check 证明（注册表含新 skill）。
验收: AC1–6 全过；`bash tools/ci.sh` 四闸绿；`python3 tools/install_skills.py --check` 零漂移。
回报: 产物路径 + AC 实证 + ci.sh 摘要 + 偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | 两份正例提案（add + modify 真实元素） | proposal_check exit 0 |
| AC2 | modify/deprecate 指向不存在元素 | proposal-target 红 |
| AC3 | add 指向已存在元素 | proposal-target 红 |
| AC4 | 必备字段缺失/枚举值非法 | proposal-schema 红 |
| AC5 | 同靶元素两个 open 提案 change 矛盾 | proposal-conflict 红 |
| AC6 | source-signal.ref 指向不存在文件 | proposal-evidence 红 |
