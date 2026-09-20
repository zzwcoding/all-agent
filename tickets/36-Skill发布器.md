# 票 36：F10 Skill 发布器（skill_pack_gen）

Status: done
Belongs to: 第六批拆票方案（2026-09-20 用户批准）；PRD F10；specs/modules.md 边界规则 5
Touches: tools/skill_pack_gen.py、tools/test_skill_pack_gen.py、exports/skillpkg/、fixtures/skill-pack-gen/、references/repo-layout.json、specs/modules.md、lessons/36

## What to build

- `tools/skill_pack_gen.py`：本体切片 → 可对话技能包骨架 → `exports/skillpkg/<域>/`
- 出厂集：bohai 切片黄金包 + 缺声明模型负变体

## 设计裁决（L0 已定）

- **发布的是语义内容骨架**：切片（域+模型子集声明）→ 三件套——①SKILL.md 骨架（frontmatter 触发面/输入输出契约/工序路由：问答走语义服务纪律的静态化表述）；②口径问答卡（逐口径：问题样例/命中 ID 集/口径要点——经 core/图索引装配，与 CORE 八问同源）；③引用纪律（ID 引用格式+拒答边界声明）。内容全部源自本体确定性装配，**成稿润色归人审后的使用方**；头部人审状态纪律（同票 35）。
- **切片声明**：`--models M1,M3,GLS` 显式声明子集；域缺声明模型 → 报错退出不硬编（边界规则 5 同款）；声明模型必须 camp=business-core 或 GLS（build-contract 切片=报错——检索面纪律的生成器侧延伸）。
- **口径一致性红线**：问答卡的口径命中集必须与 `semantic_service_core.py` 对同域同问的行为同源（出厂集抽问机核，照票 35 AC1 手法）。
- **防陈旧/幂等/登记**：--check 模式、零时间戳、exports/skillpkg/ 布局增补、modules.md 脚本清单行+skill-publisher 占位卡 dated 注记（照票 35 手法）。

## 验收（注源）

- [x] AC1 正例：bohai 切片 exit 0，三件套齐，问答卡与 CORE 行为同源（源：本票 AC 表）
- [x] AC2 幂等+防陈旧+篡改探针（源：本票 AC 表）
- [x] AC3 负变体×2：缺声明模型报错；声明含 build-contract 模型报错（源：边界规则 5+检索面纪律）
- [x] AC4 人审头部+登记+四闸（源：PRD 决策 2 与 CI）

## 交接包（L2 自主档）

任务: 生成器+出厂集+入库副本+登记。
先读: tools/app_pack_gen.py（票 35 手法基准——先行票）；tools/semantic_service_core.py；fixtures/doc-extractor/（GLS/M3 内容形态参照）；specs/modules.md 边界规则。
框架红线: 同票 35（stdlib/确定性/TDD/全量绿灯）。
边界红线: 只动 Touches 清单；skills/ 正文与 ontology/ 零改动；core/graph_index 零改动。
产出: 生成器+单测+exports/skillpkg/bohai/ 入库副本+fixtures/skill-pack-gen/（正例/负变体×2/assertions）+布局+modules.md 两处+lessons/36。
验收: AC1–4 全过；`bash tools/ci.sh` 四闸绿。
回报: 产物路径+三件套摘要+AC 实证+ci.sh 摘要+偏差。不 commit。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | bohai 切片（M1,M3,GLS） | exit 0；三件套齐；抽问口径命中与 CORE 同源 |
| AC2 | 幂等与防陈旧 | 双跑字节一致；--check exit 0；篡改单测红 |
| AC3 | 负变体×2 | 缺声明模型/含 build-contract 声明 → 均报错退出 |
| AC4 | 人审头部+登记+CI | 头部在；归档闸绿；四闸全绿 |
