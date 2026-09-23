# 第九轮后·第二域（pkb）专项审查 + 文档对齐盘点

- 日期：2026-09-23
- 范围：ontology/pkb/ 五件（第二域定稿，票 58/59 后）、平台多域承载面（meta_probe/graph_index/MCP manifest/审记）、文档对齐（AGENTS.md/lessons/PRD）
- 基线：`bash tools/ci.sh` 四闸全绿（出厂集 17/17）；`schema_check` 全仓 bohai 7 + pkb 4 = 11 文件 L1–L4 零；`meta_probe ontology/pkb` 硬闸 5/5 绿（信息项失真见 P2-1）
- verdict：**无 P1；P2 ×2；P3 ×5；观察项 ×2** → 已拆整改票 63（本体残留）/ 64（探针多域）/ 65（文档对齐+lessons）

## 核查面与通过项

| 面 | 结果 |
|---|---|
| 拍板清单一致性（docs/requirements/pkb-拍板清单-Q2-Q10.md 九问 vs 本体落点） | 通过：Q2 单聚合+sourceType / Q3 六值 String 占位 / Q8 书摘优先全文可选 / Q10 双链（status Enum[暂存,入册]）均与 M1 一致；Q5/Q6/Q7 落 M2 五行为面一致；M3/M7 豁免理由与 manifest omittedModels 一致 |
| 语义闸/图索引跨域 | 通过：graph_index ontology/pkb 正常建图查询（19 节点/23 边）；capability-manifest 已含 pkb 域块（票 54e4e76 再制） |
| 审记纪律 | 通过：pkb devkit verify=pending 待人审（协议第 11 条不代行）；bohai 件回归一致 |
| 四闸 | 通过：ci.sh 全绿（最终树原样跑） |

## P2（实锤，拆票整改）

### P2-1 meta_probe 对第二域信息项失真（平台缝隙）

`python3 tools/meta_probe.py ontology/pkb` 硬闸 5/5 绿，但两项信息探针硬编码渤海域假设：

- 第 3 项 CORE 分布：golden 问答集为 bohai 冻结期望 → pkb 域跑 8/8 全拒答（missing 7 / out_of_surface 1）报信息红；
- 第 9 项图基线：锚查询硬编码 `AGG-BOHAI-001` → pkb 域「未命中，仅取全图统计」，基线与域错配。

后果：批收官协议第①条体检留痕对第二域失真（pkb 收官将留一份带假红的体检报告），多域接入后该失真随域数放大。修法（票 64 面）：探针按目标域选 golden 集/基线锚，域无基线时渲染「无基线=豁免」注记而非假红。

### P2-2 AGENTS.md 两处漂移（入口文档）

1. **状态锚点未推进**：锚点停在第九轮整改（票 57 = c2e472b），缺第五期全部六个提交记录——54e4e76（pkb 立项进仓+R10–R12）/ 7b6591b（拆票方案）/ d9b1894（拍板清单）/ 590b0e2（拆票落盘票 58–62）/ a7fa7bb（票 58 定稿）/ de7bb50（票 59 devkit+两缝隙修复）；
2. **目录地图 ontology/ 行只提渤海域**：「首个业务域渤海域已进仓（bohai/：6 模型+glossary+manifest）」未提第二域 pkb（现值：bohai 7 文件 + pkb 5 文件，M3/M7 豁免态）。

## P3（小件，并入整改票）

1. **GLS-PKB-003 definition 主文残留待裁语气**：definition 内「个人版主从关系待细稿 Q6 裁决」——Q6 已于 2026-09-22 裁（Wiki=本体下游派生页），同条 notes 已更新而主文（口径登记层正文）未同步，自相矛盾（ontology/pkb/glossary-model.yaml:36）。
2. **GLS-PKB-005 notes stale**：「个人版 Local/Global 分档取舍挂细稿 Q5」——Q5 已裁（通用清单起步+三接入点预留），「挂」字待裁语气过期（glossary-model.yaml:62）。
3. **GLS-PKB-004 notes 残留「（待 Owner 确认）」**：定稿文件（票 58 已 Owner 全签收）不应存待确认注记；该注记所指的 relatedObjectRefs 挂接语义应转正式注记或删除（glossary-model.yaml:52）。
4. **M5 header 引用错位**：「Q9 已裁单 Owner（『我的知识库』），无多角色/多主体」——细稿 Q9 = 工作业务资料隐私边界（已裁=本地处理档），与「单 Owner 无多主体建模」非同一问；单 Owner 建模裁决缺真实出处注源，应改挂真实素材（Owner 原话「我的知识库」=细稿 §一 Owner 关键词，或拍板清单相应行）（ontology/pkb/m5-actor-model.yaml:4）。
5. **lessons 缺票 58/59 两篇**：惯例每票一篇（03 起），pkb 域定稿与 devkit 导出两票无施工日志。

## 观察项（不拆票，待 Owner/挂账）

1. **exports/skillpkg 无 pkb**：第五期拆票方案票 59 范围只含 devkit；headless 域（M1/M2/M5/GLS）是否需要 skillpkg 产物未见豁免或挂账文书——待 Owner 裁决，挂 docs/proposals/residual-questions.md。
2. **PRD 无第二域登记行**：PRD 是功能需求层，域素材属 requirements 层（细稿+拍板清单已齐备），是否如 F15 入账同款补行随票 65 一并定夺，不单独拆票。

## 整改票映射

| 票 | 内容 | 覆盖 |
|---|---|---|
| 63 | pkb 本体定稿残留修复 | P3-1/2/3/4 |
| 64 | meta_probe 多域适配 | P2-1 |
| 65 | 文档对齐 + lessons 补篇 | P2-2、P3-5、观察项 2 定夺 |
