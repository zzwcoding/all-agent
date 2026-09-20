# 票 52：ddd-modeler skill 正文（skill 轨出厂集先行）

Status: todo

> 注（L0 拆票时点）：依赖票 50（卡与格式真源）、票 51（ddd_check——skill 的自检工具）。本票写 skill 正文，出厂集先行红→绿。
Belongs to: docs/第四期DDD线拆票方案.md 批次二；docs/ddd-modeler-建造交接包.md §3.1；references/ddd-as-code-digest.md §2/§5
Touches: skills/ddd-modeler/（正本）、~/.agents/skills/ddd-modeler/（安装位）、fixtures/ddd-modeler/（skill 轨断言扩充）、lessons/52

## What to build

`skills/ddd-modeler/`（SKILL.md + references/ 私件），核心工序五步（Event Modeling 切片法 + TUM 教训固化）：

1. **术语锚定**：输入必须是本体模型产物（无词条不建模）——缺词条回 onto-modeler 或提案池，不在本工序发明业务事实；
2. **事件时间轴 → 命令**：从行为清单推领域事件流与命令，产结构化 YAML 中间件落盘；
3. **聚合候选 + 合并追问**：列聚合候选后**必走一步"合并候选上下文"显式追问**（对冲 LLM 切碎偏差，digest §2）——"这几个候选是否必须同时成立/同时改？"；
4. **成稿**：聚合卡/事件表/映射/仓储边界 → `ddd_check` 自检 → 待人审清单 → 草案走 MR（不直改进仓本体/设计件）；
5. **副产物**：设计件 → Mermaid 图（人审靠图，digest §6 #6）。

工序纪律写进正文：**每步新鲜上下文、只喂上一步定稿 YAML 中间件，不做散文累积**（TUM 教训，digest §2）。

出厂集扩充 `fixtures/ddd-modeler/`：固定本体输入 → 断言产出的聚合卡结构（aggregateRoot/不变量三元组在场）与工序中间件清单（时间轴/命令/候选各落盘文件在场）。

## 设计裁决（L0 已定）

- 选配触发面：frontmatter description 写清"交易型/状态机型项目"路由条件（判据表引交接包 §5），不与 onto-modeler 触发面混淆。
- skill 只产草案；进仓走 MR 人审（design-card status 草案→已审）。
- 安装位双落：仓内正本 + ~/.agents/skills/ 安装位，内容一致（票 05/15 机制）。

## 验收（注源）

- [ ] AC1 出厂集先行红→绿留痕（lessons/52 记录）（源：本票 AC 表）
- [ ] AC2 五步工序正文在场，含"合并追问"显式步骤与"新鲜上下文只喂定稿"纪律（源：实读）
- [ ] AC3 出厂集断言：固定输入 → 聚合卡结构断言 + 中间件清单断言全过（源：CI）
- [ ] AC4 触发面选配路由明文 + 安装位双落零漂移（pre-commit install_skills --check 绿）（源：CI）
- [ ] AC5 `bash tools/ci.sh` 四闸绿（源：CI）

## 交接包（L2 自主档）

任务: ddd-modeler 正文+出厂集扩充+安装位。
先读: docs/ddd-modeler-建造交接包.md §2（共识：聚合/事件/Saga 判据）与 §3.1（开卡表）；references/ddd-as-code-digest.md（全件——工序设计的直接依据）；design/ddd/README.md（票 50 格式真源）；skills/onto-modeler/（既有工序型 skill 的组织先例）；fixtures/ddd-modeler/（票 51 绿灯样本）；AGENTS.md（安装位机制）。
框架红线: 无点名框架。
边界红线: 只动 Touches 清单；只产草案不写仓内已定稿本体；不读生成器 skill 私件（卡面边界）。
产出: skills/ddd-modeler/ 全套+安装位+fixtures 扩充+lessons/52（含红→绿留痕）。
验收: AC1–5 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径+五项 AC 实证+ci.sh 摘要+偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | lessons/52 | 出厂集先行红→绿记录在场 |
| AC2 | SKILL.md 正文 | 五步工序齐、合并追问步与新鲜上下文纪律明文 |
| AC3 | fixtures/ddd-modeler/ skill 轨断言 | 聚合卡结构+中间件清单断言全过 |
| AC4 | frontmatter + 安装位 | 选配路由明文、双落零漂移 |
| AC5 | CI | 四闸全绿 |
