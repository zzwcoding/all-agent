---
name: proposal-pool
description: 提案池处理——把这条信号起草成提案/过一遍提案池/查提案池状态。把业务语义循环里的三源信号（监督/自检/交互）归一为标准提案文件，跑确定性冲突预检后落盘提案池，等 Owner 裁决；自动化止于提案——不起 git 分支、不直改 ontology，真提案进仓走 MR 由人完成。
---

# proposal-pool · 提案池（L1 工序，业务语义循环）

把信号变成结构完备、可裁决、可追溯的**提案文件**：机械管字段/靶/冲突/证据四类确定性检查，人管提案该不该提与矛盾裁决。本 skill 机器通用：正文不含任何具体业务域知识，域语义只存在于信号素材与本体仓里。

## 触发面 / 何时用

- 用户要「把这条信号起草成提案」「过一遍提案池」「查提案池状态」时使用。
- 不适用：直接修改已定稿本体（写入必经 MR——本 skill 的产出止于提案）；运行期查询口径（那是运行时服务的事，查不到、查不对的东西才回流成信号进本池）。

## 输入输出契约

- reads：用户提交的信号素材（拒答记录/疑点登记/对账缺口/监督告警/交互原文）；`docs/proposals/**`（提案池现状与池内冲突面）；`ontology/**`（真域——判定 add 是否重复建、modify/deprecate 靶是否存在）；仓根共享规约 references/proposal-format.md（提案文件格式规范，与检查工具的字段定义一字不差对齐；仓级共享件不入本 skill 私件目录，故以文内平文指路）。
- writes：`docs/proposals/PROP-<域>-<NNN>.md` 提案文件，及既有提案的裁决落痕（只动 status 与正文裁决注记；不直改 ontology/**、不起 git 分支）。
- 依赖脚本：`tools/proposal_check.py`（确定性冲突预检，起草第 3 步的判定器）。

## 工序（起草四步，按序执行）

1. **信号受理**：按 references/signal-normalization.md 的五类受理标准判断信号可受理（可定位/可证伪/可裁决），缺证据先补证据、仓外材料先转录落盘；不受理的逐条给原因，不静默吞掉。
2. **归一格式**：按 references/proposal-format.md（仓根共享规约，见上方 reads）把信号转成标准提案头（id/title/status/source-signal/target/change/rationale）+ 正文（草案内容与证据展开）；change 类型按真域核对——靶已存在是 modify/deprecate，不存在才是 add，不得凭印象选。
3. **冲突预检**：跑 `python3 tools/proposal_check.py <提案目录>`（整池时传提案池目录），四类检查全过才算起草完成；报 proposal-conflict 不改旧提案——新提案标 draft 并在正文登记与谁冲突，等 Owner 分泾渭。
4. **提案落盘+状态纪律**：新提案先 status=draft，自检全过且无未解冲突后翻 open；accepted/rejected 只由 Owner 裁决产生，skill 只代执行裁决结果（翻 status + 正文留裁决痕，不删档）。

## 行为约定

- **自动化止于提案**：不起 git 分支、不直改 ontology/** 已定稿本体；提案进仓由人走 MR + 语义 CI。
- **不静默吞信号**：不受理的信号逐条给原因；证据不足标 draft 不标 open。
- **冲突上报不自行取舍**：同靶矛盾是 Owner 的裁决点，skill 只报矛盾不判对错。
- 状态流转纪律见仓根共享规约 references/proposal-format.md §4：draft→open 由起草人，open→accepted/rejected 只由 Owner。

## 细则索引（进入对应步骤时读）

- references/signal-normalization.md——信号归一指南（五类信号的受理标准、证据等级与标注、逐字段归一操作细则、冲突处置；全文域无关）

## 出厂集（Seam）

`fixtures/proposal-pool/`——正例提案两份（add 渤海新规则 + modify 真实元素）+ 负变体 → 断言 proposal_check 四类检查（AC1–6，真源=票 18 AC 表）。改本 skill 工序描述前，先确认出厂集仍绿。
