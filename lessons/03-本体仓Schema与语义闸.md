# 施工日志 03 · 本体仓 Schema + 语义闸 schema_check + 三闸实例化 + CI 骨架

日期: 2026-09-17
角色: L2 编码（自主档）
票: tickets/03-本体仓Schema与语义闸.md（spec: specs/schema_check.md AC1–7；PRD F1/F2）

## 做了什么

1. **ontology/schema/**（七模型精简 schema，v9 蓝本）：
   - `schema.md`：公共字段与文件约定、ID 前缀与 ref 命名约定、四层规则下沉判定、字典治理（停用不删除）、运行期预留字段（M2 contract/riskLevel/idempotent、M3 narrative|expression 双写法、全模型元素级 version/validFrom）、七模型逐模型字段表、换义锁定字段表。
   - `model-registry.json`：每模型 camp/consumers/profiles/dependsOn 四字段（PRD F1）+ modelType + lockedFields；profile 组合由各模型 profiles 取并集反推（单一真源）。
   - `model-deps.json`：idPrefixes（ID 前缀→模型）+ refKeys（ref 字段名全集）+ edges（from 模型 × ref 字段 → 允许目标模型集），AC4/AC5 判定真源。
   - `ontology/bohai/manifest.json`：渤海域 profile 声明（v9-full），模型文件随票 05 起落盘。
2. **tools/schema_check.py**（TDD，先写 test_schema_check.py 13 条后实现）：实现 AC1–7——L1（YAML 语法/公共字段/manifest/profile 已登记/两份机读表一致性）、L2（悬空引用+依赖白名单）、L4（profile 未启用+换义锁定字段）。带行号 YAML 装载（SafeLoader 子类标注 node start_mark），失败输出文件+行级定位；只读不写；`--json` 供 CI。CLI 支持 ontology 仓根或单域目录（schema 解析：本目录 schema/ → 上级 schema/）。
3. **三闸实例化**（从 sdd-flow2 拷贝进 tools/，含单测）：skill_deps_check / fixture_run / archive_check + 各自 test_*.py + ci.sh（四闸：脚本单测+出厂集回归+边界闸+归档闸）。
4. **出厂集 fixtures/schema_check/**：最小域（两对象：井 AGG-BOHAI-001 + 单井日产量记录 AGG-BOHAI-002）七模型合法本体 + 6 个非法变体（ac2–ac7 一变体一 AC）；`ontology/schema` 是指向仓内 ontology/schema 的符号链接（机读表单一真源，不复制）；assertions.json 以 7 条 cmd-* 断言逐条对 AC1–7。
5. **归档两表**：references/repo-layout.json（governed-project profile，按本仓补 RESOURCES.md 根条目、docs/impact、ontology 细则）；specs/archive-registry.json（ticket 状态 todo/doing/done；新增 ontology 产物类 4 种）。
6. modules.md 规约清单/脚本清单状态翻「已建（票 03）」；AGENTS.md ontology 行刷新。

## 取舍

- **M2 不设 queryReportRef 依赖边**（对 OMF v9 的显式裁剪）：AC5 把「M2 引 M7」定为白名单违规，故 M7↔M2 严格一对一的依赖边只登记 M7→M2 单向，M2 侧该字段不使用；双向一致性核验留给 L2 一致性对清单（票 04 图索引后）。schema.md §2 已注明。
- **ID 全前缀化**：OMF 的 M2 行为 `{EntityAlias}_{ActionName}`、MU 屏幕 `frmXxx` 无前缀，无法机械校验指向；本仓改 `BH-{域}-{动宾}` / `SCR-`，schema.md §2 登记为两处显式偏差（digest §16.2「前缀即类型标签」依据）。
- **fixture_run 新增 cmd-succeeds/cmd-fails 断言类型**：AC1–7 是"闸对固定输入的行为"，文件类断言表达不了；命令 cwd=仓根、`{fixture_dir}` 占位替换。这是对 sdd-flow2 原版的加法（原 4 类断言不变），单测补 9 条。
- **空出厂集目录 = pending 不红**：db-reverse 等四目录是后续票占位；放了输入没写断言仍红（空套件不亮绿灯的镜像约束）。
- **skill_deps_check 两处实例化差异**：①本仓无 skill（票 05 起）不再判死，带 note 只核对卡↔脚本依赖；②卡上声明的脚本若已登记脚本清单但未落盘 = planned-script 警告（graph_index.py 属票 04），未登记的缺失脚本仍红。
- **archive-registry 的 skill-card requiredFields 收敛为 ["职责"]**：8 张二期占位卡按 ADR 0001 备注在二期立项卡审时才补全 9 字段，归档闸不提前判死。
- **锁文件/换义真源放 model-registry.json 的 lockedFields**：换义判定（AC7）需要机读，schema.md §11 是人读对照表，registry 是机器真源。

## 坑

- **pip 在 macOS 26 上崩**（vendored truststore 解析 macOS 版本串崩，`ValueError: invalid literal for int()`），且 PEP 668 拦 --user。绕法：从 PyPI 直接 curl cp314 arm64 wheel 解包进 `~/Library/Python/3.14/lib/python/site-packages`（用户级，未动 Homebrew site-packages）。
- **git ls-files 含已提交的 .DS_Store**：--exclude-standard 只排未跟踪文件；本仓早期提交把根 .DS_Store 收进了库。已 `git rm --cached .DS_Store`（盘上保留、.gitignore 防复发），主窗口提交时一并落"取消跟踪"。
- **modules.md 脚本清单的脚本名是表格裸写非反引号**：parse_planned_scripts 同时认裸写 token（正则兜底），否则 planned-script 判定失灵。
- **悬空引用不能边扫边判**：定义收集必须先于悬空判定全量完成（m2 在 m1 前解析时会把合法引用误判悬空），schema_check 用两遍扫（第一遍 L1/L4+依赖白名单+定义收集，第二遍悬空判定）。
- **ref 值不得自证存在**：定义收集跳过 ref 键本身，否则悬空 ID 会被自己的引用"定义"洗白。

## 验收（对照票面）

- [x] AC1–7 全过：单测 13 条 + 出厂集 7 条 cmd 断言（源：specs/schema_check.md）
- [x] 模型注册表含 camp/consumers/profiles/dependsOn 四字段（源：PRD F1）
- [x] ci.sh 四闸绿：`bash tools/ci.sh` → 单测 86 条 OK、出厂集 1/5 过（4 占位 pending）、边界闸无违规、归档闸全合规
- [x] 归档闸过：受管 86 文件全对上布局表+登记表

## 遗留与移交

- 票 04（graph_index.py）落盘后，边界闸的 planned-script 警告自动消失。
- 票 05 起建 skills/ 后，skill_deps_check 的正文扫描规则（判定规则 2–5）自动生效。
- 渤海域模型 YAML 进仓后，MR 流程对 `ontology/` 全量跑 schema_check（ci.sh 注释已注明）。
- 本票不 commit，产物待主窗口验收后统一提交。
