# proposal-format · 提案文件格式规范（机器可核字段定义）

> **镜像声明**：本文与 `tools/proposal_check.py` 头注一字不差对齐（字段/枚举/四类
> 检查/退出码），改一处必改另一处，不许漂移。AC 真源=tickets/18 AC 表；提案池目录
> 的人读一页见 docs/proposals/README.md。本文是仓级共享规约（L2），消费方：起草
> 工序（proposal-pool skill）、检查工具、走 MR 的人。

## §1 文件与命名

- 提案文件落 `docs/proposals/PROP-<域>-<NNN>.md`；`<域>` 为字母数字（域目录名），
  `<NNN>` 恰三位数字，同池 id 不得重复。
- 检查工具只解析 `PROP-*.md`；目录内其他 md（对账 README、证据附件）跳过不解析。

## §2 YAML 头必备字段

提案文件以 YAML 头开始（首行 `---` 起、至下一个 `---` 行止），正文为草案内容与
证据展开。七字段全必备：

| 字段 | 类型 | 约束 |
|---|---|---|
| `id` | str | 格式 `PROP-<域>-<NNN>`（正则 `^PROP-[A-Za-z0-9]+-[0-9]{3}$`）；同池不得重复 |
| `title` | str | 非空；一句话动宾结构，带靶 ID |
| `status` | str | 枚举 `draft / open / accepted / rejected`（状态机见 §4） |
| `source-signal` | map | 两键：`kind`（枚举 `拒答 / 疑点 / 对账缺口 / 监督 / 交互`）、`ref`（非空 str，证据路径`[#锚点]`，解析规则见 §5） |
| `target` | map | 两键：`model`（非空 str，靶元素前缀在 idPrefixes 登记的模型标识）、`element`（非空 str，元素 ID） |
| `change` | str | 枚举 `add / modify / deprecate` |
| `rationale` | str | 非空；一段话说清「什么信号→什么缺口→建议什么动作→待谁裁决什么」 |

YAML 头缺失/未闭合/不可解析/非映射，同归 schema 违规。

## §3 四类机读检查（确定性、零 LLM）

| 码 | 查什么 | 判定 |
|---|---|---|
| `proposal-schema` | 必备字段与枚举值自检 | 七字段全备 + 三组枚举合法 + id 格式与同池唯一 + 非空字符串约束（见 §2） |
| `proposal-target` | target 存在性 | `modify`/`deprecate` → `target.element` 必须已在 ontology/ 真域；`add` → 必须不存在（防重复建）。元素判定口径照票 04 图索引：定义键 `id`/`*Id`（ref 键除外）且值为字符串、且带 model-deps.json idPrefixes 已登记前缀；未登记前缀判「不存在」，前缀登记属 schema 演进面 |
| `proposal-conflict` | 池内冲突 | 同 `target.element` 的两个 `status: open` 提案 change 类型矛盾（两个不同枚举值即矛盾）。同值重复提案不判（人裁决面）；draft 与已裁决提案不参战 |
| `proposal-evidence` | 证据在档 | `source-signal.ref` 剥 `#锚点` 后（锚点容许、不校验内容）依次按 仓根相对 → 提案目录相对 解析，两处皆无 = 红；绝对路径与只剩锚点的空路径 = 红 |

- schema 红的文件不再进 target/conflict/evidence 检查（红因纯净，脏数据不进池内
  比对）。
- 退出码：0 全过；1 有违规；2 用法/配置错误（缺参、提案目录不存在、--root 下无
  ontology/ 或缺 model-deps.json、ontology YAML 不可解析——部分元素集=说谎的
  元素集，拒绝判定）。
- 机械面只报矛盾不判对错：提案该不该提、冲突双方谁对，裁决权在人（自动化止于
  提案）。

## §4 状态机

```
draft ──起草人（自检全过且无未解冲突）──> open ──Owner 裁决──> accepted
  │                                        └──Owner 裁决──> rejected
  └─ 证据只有 C 级 / 有未解冲突时停留
```

- `draft`：起草中/证据不足/有未解冲突；不算待决。
- `open`：自检全过，等待 Owner 裁决。
- `accepted`/`rejected`：只由 Owner 裁决产生；代执行只许改 status 一处 + 正文留
  裁决注记（日期、裁决出处），不删档。
- `rejected` 提案是资产：同信号再现先查池；翻案走新提案并引用旧号。

## §5 证据路径解析规则

1. 先剥 `#锚点` 后缀（锚点容许，不校验内容）；
2. 依次尝试：仓根相对 → 提案目录相对，任一命中即在档；
3. 绝对路径、只剩锚点的空路径一律红——证据必须随仓/随池可追溯；
4. 仓外材料（C 级证据）先全文转录落盘成仓内文件，再以仓内路径引用。

## §6 正文结构

两节起步：**草案内容**（拟新增/拟修改的元素 YAML 或要点，标注「进仓走 MR，非已
定稿本体」）与**证据展开**（逐条列证据与信号原文摘录）。正文不受机读检查，但受
起草工序纪律约束（见 proposal-pool skill 的 references/signal-normalization.md）。
