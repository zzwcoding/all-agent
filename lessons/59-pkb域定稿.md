# 59 · pkb 域定稿（第二域建模：九问拍板 → 定稿翻版）

- 日期: 2026-09-22
- 角色: L2 编码（票 58 施工窗）
- 票: tickets/58-pkb域定稿.md
- 依据: docs/第五期端到端实弹拆票方案.md §4；docs/requirements/pkb-拍板清单-Q2-Q10.md（Owner 全签收）；docs/requirements/personal-weknora-细稿.md
- 性质: 第二域（首个非渤海域域）完整建模工序留痕

## 做了什么

1. **九问拍板 → 定稿翻版**：粗需求细稿（15 关键词三落点全覆盖/开放问题 Q1–Q10）→ Owner 对 Q2–Q10 逐条签收（Q1 此前已裁）→ ontology/pkb 从草案翻定稿——M1 知识条目定稿 1.0.0（status 转 Enum[暂存,入册] 承载 Q10 双链、contentRef 指针化 Q8 书摘优先、sourceType 六值起步保持 String 占位、lifecycle 两态）、新建 M2 五行为（CaptureItem/PromoteItem 双链 COMMAND + AskKnowledge/QueryGraph 消费 QUERY + RegenWiki 派生页）、新建 M5 单 Owner 三件套（ACTOR+ROLE+PERM×5 对准五行为）、GLS 六术语定稿翻版、manifest omittedModels 收敛 M3/M7 带理由。
2. **豁免走满理由**：M3（规则素材零输入，Q5 通用清单起步+三接入点预留）/M7（「以后可能会要」不算证据）均带理由豁免——沿用 bohai MU 同款机制，但理由是逐域素材判断，不复制 bohai 文本。

## 取舍

1. **String 占位 vs Enum 的边界**：sourceType 值集未闭（六值起步）保持 String、status 两值已闭转 Enum——「值集闭没闭」是类型判据，枚举冲动要压住（schema 不替业务提前封口，新增类型走提案池转 DICT）。
2. **headless profile 首跑**：pkb 是 headless（无 UI/报表/流程素材）首个真实域，M3/M7 豁免态首过语义闸——manifest omittedModels 机制在 bohai 是 MU 单件缺席，pkb 是两整模型豁免，理由文书化（谁的裁决+为什么）是豁免被信的关键。
3. **拍板清单独立落盘（d9b1894）是授权证据**：Owner 会话口头拍板 → 签收表独立文件 + 会话引用，与协议第 11 条（Owner 权柄代行使须独立落盘）同款思路——业务裁决的留痕标准与权柄代行使一致。

## 坑（如实记，两条）

1. **九问清单是最小裁决面，推荐档质量=定稿质量**：细稿阶段把 Owner 关键词全部转开放问题（不硬建模），拍板时 Owner 一句「都按你推荐的就行」九问全签收——推荐档逐条落点表（拆票方案 §2）是签收清单的骨架，省不掉；推荐档写含糊=定稿埋雷。
2. **引用要挂原话出处，别挂到不相干的问题编号上**（票 63 清偿）：M5 header 原写「Q9 已裁单 Owner」——细稿 Q9 实为工作业务隐私边界（已裁=本地处理档），与单 Owner 建模非同一问；定稿文件里的注源错位语义闸不查、审查才显形。Owner 原话「我的知识库」（细稿 §一）才是主体建模的直接素材，原话即证据，不需要额外裁决会议。
