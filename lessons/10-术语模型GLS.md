# 施工日志 10 · 术语模型 GLS（元模型演进）+ 渤海域术语落仓

日期: 2026-09-19
角色: L2 编码（自主档）
票: tickets/10-术语模型GLS.md（AC 真源=票面 AC 表；PRD F1 配套；一期收官报告 §7 第一批 / §6 缺口 8）

## 做了什么

1. **GLS 进 schema（元模型演进）**：第 8 个模型类型 GLOSSARY——文件 `glossary-model.yaml`（照 `mu-ui-model.yaml` 非数字先例）、ID `GLS-{域}-{Seq}`、camp=business-core、consumers=[runtime, build]；profile 入 v9-full 与 headless、**不入 v9-core**（四模型最小核保持原样，"未启用"因此有可测负变体）。schema.md 增 §11（字段表：term/aliases/termType/definition/relatedObjectRefs/status/owner/source/notes；source 必填=术语必须可溯源），原 §11/§12 顺延为 §12/§13，两份机读表 description 里的 § 引用同步改。
2. **机读表演进**：model-registry.json 增 GLS 条目；model-deps.json 增 `GLS-→GLS` 前缀、`relatedObjectRefs` refKey、`GLS.relatedObjectRefs→[M1]` 边（与 registry dependsOn=["M1"] 过一致性核对）。两表顶层 version 整数 `1` → `"1.1.0"`；新建 `ontology/schema/CHANGELOG.md`（语义化日期+变更点+迁移注记"旧域零改动兼容"；布局表 ontology/** 已覆盖，无需登记）。
3. **schema_check 扩展**：新增 **L1 filename-mismatch**——模型文件名 ≠ 注册表该模型 `yamlFile` 即红。单测补 GlossaryModel 7 条（全库单测 104 条 OK）；出厂集增 4 目录（`gls-valid` 正变体 + `gls-ac2-core-profile`/`gls-ac3-dangling-ref`/`gls-ac4-filename-mismatch` 负变体）+ assertions 增 GLS-AC1–4，**先红后绿**：红相=GLS-AC1 退出码 1 / AC2-AC3 红因是 unknown-model-type（非目标违规）/ AC4 缺 filename-mismatch 断言needle，绿相后四条全按票面语义红绿就位（AC1 全过；AC2 `[L4][profile-disabled] 未启用模型 GLS`；AC3 `[L2][dangling-ref] AGG-GLSA-999`；AC4 `[L1][filename-mismatch] ×2`——model_type 写错与文件名错挂两个子变体都红）。
4. **渤海域术语落仓**：`ontology/bohai/glossary-model.yaml`，R5·§6 十条全量（GLS-BOHAI-001…010，每条注源 `R5·设定书 §6`，含 term/aliases/definition/relatedObjectRefs/status/owner/notes）。对账第三节缺口关闭：承载 7 条补术语本体位 + 未建 3 条（水淹层/配注合格率/三多四难）落位且 relatedObjectRefs 留空不硬挂。bohai 语义闸 7 文件全绿。

## 盘点结论：schema_check 的硬编码面（主窗口提示①的答案）

- **判定全走机读表，脚本零硬编码**：模型类型合法值=registry `modelType`、ID 前缀=deps `idPrefixes`、ref 扫描面=refKeys ∪ `*Ref/*Refs` 后缀 ∪ edges 登记字段（三源并集）、profile=各模型 `profiles` 并集。glossary 只需机读表加条目即生效——实证：graph_index 与 semantic-service 因 camp=business-core/前缀表数据驱动**自动纳管 GLS，两处零改动**（检索面划界只看 camp，semantic-service SKILL.md §检索面原文）。
- **唯一例外**：registry 的 `yamlFile` 字段此前**声明了但从不校验**。AC4"GLS 文件名错挂→L1 红"没有机检面就实现不了，故本票把它闸上（filename-mismatch）；对旧七模型是"一模型一 YAML、固定文件名"（schema.md §1）的强化，现网所有文件本就合规——红绿实证零扰动（单测 `test_existing_correct_filenames_still_pass` + valid-domain/六出厂集全绿）。

## 取舍

- **GLS→GLS（术语见术语）不设专用边**（最小够用）：当前十条无此需求。若将来出现指 GLS- 的 `xxxRef(s)` 字段，落"未登记 edges 字段按 dependsOn 兜底"路径（兜底集含自身，不白名单红；悬空检查仍生效）——即**事实上隐式允许且有存在性校验**，规模化再用时再显式登记边。
- **relatedObjectRefs 挂选从严**（可空留空不硬挂）：只挂与定义有直接数据承载关系的既有聚合根。剔检产量挂两对象（AGG-BOHAI-001+002：量在日产计量、剔检判据=井状态「检修」），递减增油挂 AGG-BOHAI-009（splitCoefficient 是其劈分承载，m1 描述原文背书）；水淹层/三多四难留空；配注合格率/存水率挂 AGG-BOHAI-003（分子/注入侧承载真实存在，未建的是另一侧——缺口如实写进 notes 而非清空引用）。承载落点 RULE/QR 等**不挂引用**（边只有 GLS→M1），以 notes 文字注记"对账落点 step5-fidelity §三"作人读追溯。
- **termType/status 沿真源原文不做枚举收敛**：R5 的类型列（禁用词/别名/一词两译/黑话/缩写/术语/治理热词）与状态列（禁用（替代：×）/有效（待联席裁决）…）逐字保真——GLS 的职责是术语的可溯源载体，不是分类学收敛。
- **版本号从整数 1 起**：票面写"1.0.0→1.1.0"，实际现状是票 03 落的整数 `1`；按主窗口提示"按现状惯例演进"改为 `1`→`"1.1.0"`（int→string 无消费者受影响，全库 grep 实证无人读该字段），CHANGELOG 记账并立约"本票起语义化三段、两表同步"。
- **assertions.json 的 GLS 套件标签用 `GLS-AC1…4`**：与基础套件 AC1–7 撞号会毁报告可读性；AC 编号语义不变（真源仍是票面 AC 表）。

## 坑

- **域 manifest 的 schemaVersion 与 schema 版本不联动**：现状闸不校验联动（bohai/fixture 均 "1.0.0"，机读表已 1.1.0）——这是事实而非缺陷，票 10 不强制联动，CHANGELOG 迁移注记已写明。将来若要联动需先立 spec 再加闸。
- **负变体在实现前也会红，但红因不对**：机读表未加 GLS 时 AC2/AC3 已经是红的（unknown-model-type）——"先红后绿"必须核红因是不是断言声明的那个 kind，否则负变体验收形同虚设（断言 outputContains 就是为钉死红因设计的）。
- **schema.md 章节号是活引用**：两份机读表 description 里写着 `schema.md §11/§12`，增章顺延后必须同步改引用，否则人读文档与机读表漂移。

## 验收（对照票面）

- [x] AC1–4 出厂集全绿（源：票面 AC 表——红绿转换证据见上"做了什么 3"）
- [x] 渤海域术语 10 条进仓且语义闸全绿（源：step5-fidelity §三；`python3 tools/schema_check.py ontology/bohai` → 7 文件全过）
- [x] schema.md/注册表/依赖表/CHANGELOG 四件一致，版本号已演进（源：信号路由表"元模型错"行；registry/deps version="1.1.0"，edges⊆dependsOn 过一致性核对）
- [x] 旧域零破坏：valid-domain 不加 GLS 仍全绿；六出厂集全 PASS；bohai 既有六文件零改动
- [x] `bash tools/ci.sh` 四闸全绿（摘要见回报）

## 遗留与移交

- semantic-service 检索面自动纳入 GLS（camp=business-core）：术语问答能力随之生效，但其 Golden Question 出厂集未加术语问句——按边界红线本票不动出厂集，术语问句压测留二批票。
- 禁用词（老完成率）的**校验侧强制拦截**仍未建（step5-fidelity 缺口原文）：GLS 只提供了载体，拦截面需 L3/L5 闸或生成器规则，待后续票。
- 本票不 commit，产物待主窗口验收后统一提交。
