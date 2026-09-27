# hr 域端到端走查（第四域 · db-reverse 实战批 · 票 80）

> 日期：2026-09-28（施工窗自主完成，Owner 授权记录
> docs/meta/owner-delegation-2026-09-28.md）。走查面=his 票 69 同构
> （devkit/图索引/语义服务问答/smoke 文案/体检），golden 冻结与 L5 评分
> 面按授权拍板挂观察项（与 his 同待遇，见 §四）。

## 一、导出面

- devkit：`app_pack_gen.py ontology/hr --out exports/devkit/hr/` 产
  devkit.md+devkit.json；`--check` 再制逐字节一致；声明模型 M1/M2/M3/M7
  （app-pack 契约面，bohai 同构）。审记 pending 待 Owner 人审（授权边界：
  不代审，by= 字段会留「Owner 已审」假痕）。
- skillpkg：`skill_pack_gen.py ontology/hr --models M1,M3,GLS --out
  exports/skillpkg/hr/` 产 SKILL.md+skillpack.json。审记 pending 同上。
- capability-manifest：票 79 已再制加 hr（四域），`--check` 逐字节一致。

## 二、图索引面

全仓 `graph_index.py ontology`：**248 节点 / 400 边**（hr 入仓后）。
hr 域元素抽核（命中即结构四类可达）：

| 查询 ID | 模型 | 命中 |
|---|---|---|
| AGG-HR-001 员工 | M1 | ✔ hr/m1-object-model.yaml:19 |
| AGG-HR-006 薪酬记录 | M1 | ✔ |
| RULE-HR-003 现行任职判定 | M3 | ✔ |
| FLOW-HR-001 时态生命周期 | M6 | ✔ |
| QR-HR-002 部门在职人数查询 | M7 | ✔ |
| GLS-HR-006 现行任职 | GLS | ✔ |

## 三、语义服务实弹（两问，引用零悬空）

| 问句 | 裁决 | 命中链 | 引用数 |
|---|---|---|---|
| 人司年限口径是什么？ | answered（GLS 名称解析） | GLS-HR-008 → RULE-HR-008 → BH-HR-QueryTenure → QR-HR-005 | 14 |
| 部门在职人数怎么算？ | answered（ID/名称解析） | AGG-HR-002/GLS-HR-002 → BH-HR-QueryHeadcount → QR-HR-002 → RULE-HR-007 | 18 |

悬空核验：两问引用 ID 全集对 ontology/hr 定义集机扫——**悬空引用零**
（db-reverse 证据链反查可全数回溯到 DDL 行注）。

## 四、挂账面（如实）

- 审记 pending ×4：his devkit/skillpkg + hr devkit/skillpkg（verify --all
  现跑小结：7 件，最差退出码 1——按协议⑥挂账口径，不阻塞四闸）。
- L5 评分面/golden 冻结：hr 未建（词面检查如实报缺）——按授权拍板与 his
  同待遇挂观察项；后续若 Owner 要建，golden 候选面=细稿 Q1–Q8 派生四问
  （薪酬口径/在职人数/现行判定/人司年限）。
- smoke 断言面：ID_TOKEN_RE 仍为 bohai 词面（hr 语义服务面可问答、smoke
  用例未建），文案已如实标注（票 80）。

## 五、批次收官核对（协议⑨，2026-09-28）

1. ① 体检逐域留痕：docs/meta/体检-2026-09-28-{bohai,pkb,his,hr}.md 四件全 PASS（hr 带 --graph-query AGG-HR-001）；
2. ② 锚点推进：AGENTS.md §5 锚点段（本票提交，grep 断言在位）；
3. ③ 审查报告：docs/reviews/2026-09-28-phase14-review-ticket77.md（票 77）已入仓；本批审查见 docs/reviews/2026-09-28-phase14-review-hr-batch.md（收官后补）；
4. ④ 豁免复核：无新增豁免（hr 仅 MU omittedModels 登记，bohai 先例式，非审记豁免）；
5. ⑤ L5 全量：本批未建 hr 评分面（观察项挂账，见 §四）；既有 bohai 面未受影响；
6. ⑥ 审记 verify --all：7 件（见 §四）；
7. ⑦ ddd_check：design/ddd 无 hr 设计件（DDD 线未路由 hr——只读报表域，路由纪律同 his 判定先例）；
8. ⑧ 指标快照：docs/meta/指标快照-2026-09-28.md（+json）落盘，本批数字（模型文件 26/域 4/生成物 7/审记态）引自快照。
