# L5 评分报告（l5_score · 票 42）

- 输入指纹: fde8ef84f05d1991（rubric×3 文件 + 评分结果×9 文件内容 sha256 前 16 位；零时间戳零机器路径，同输入两次生成字节一致——留痕时间性由 --out 序号后缀承载，票 48）
- 形态: 确定性骨架（零模型调用）——LLM 评分由运行时子 agent 产出评分结果 JSON（协议: specs/l5_score.md），本脚本只校验、聚合、判定、留痕

**结论: PASS**（退出码 0）
- 条件① 单问总分 ≥3: PASS（最低 Q2 = 12）
- 条件② 全集中位 ≥4.0: PASS（全集中位 13 ≥ 4.0，问总分集 [22, 12, 13]）
- 条件③ 无 disqualifier: PASS（0 问触发）

## 逐问明细

### Q1
- rubric: q1-rubric.yaml
- 判定: PASS ｜ 总分: 22 ｜ 稳定

| 维度 | 权重 | 三采样 | 中位 | 分差 |
|---|---|---|---|---|
| semantic_fidelity | 2 | [5, 4, 5] | 5 | 1 |
| caliber_quality | 2 | [4, 5, 4] | 4 | 1 |
| organization | 1 | [4, 4, 5] | 4 | 1 |

### Q2
- rubric: q2-rubric.yaml
- 判定: PASS ｜ 总分: 12 ｜ 稳定

| 维度 | 权重 | 三采样 | 中位 | 分差 |
|---|---|---|---|---|
| coverage | 2 | [4, 4, 5] | 4 | 1 |
| citation_fit | 1 | [4, 4, 4] | 4 | 0 |

### Q3
- rubric: q3-rubric.yaml
- 判定: PASS ｜ 总分: 13 ｜ 稳定

| 维度 | 权重 | 三采样 | 中位 | 分差 |
|---|---|---|---|---|
| coverage | 1 | [5, 5, 4] | 5 | 1 |
| accuracy | 2 | [4, 4, 5] | 4 | 1 |

## 不稳定升级提示（design-l5-scoring.md §4.3）

（无）

## 红灯路由去向（只报告不修复；分道人工裁决，路由表: policies/signal-routing.json）

- 语义内容错（保真度/口径类红）→ 业务错道: 提案池起草（skills/proposal-pool），Owner 裁决走 MR
- 话术/工序错（拒答话术/组织类红，本体没错）→ 工程错道: tickets/ 开票修 skill 工序或参照答案
- rubric 本身写错（锚例与工序矛盾）→ 元模型错道: 改 rubric 走票（改出厂集 = 走票）
- 本次红灯问: 无
