# 施工日志 36 · Skill 发布器（F10 skill_pack_gen，第六批第二票）

日期: 2026-09-19
角色: L2 编码（自主档）
票: tickets/36-Skill发布器.md（AC 真源=票面 AC 表；设计裁决：发布语义内容骨架/切片声明 --models/口径一致性红线/防陈旧幂等登记，L0 定稿照办）
因由: 第六批第二票（PRD F10）；skill-publisher 占位卡以 L3 工具群落地（照票 35 app-generator 手法），人审闸的生成物侧落位（头部 status: 待Owner人审）。手法基准=票 35 app_pack_gen（--out/--check/幂等/人审头/声明模型集报错骨架全照抄换内容）。
交接包注记: 主窗口防踩坑 8 条逐条照办（手法基准/切片声明语法两条报因/三件套全机读装配/口径同源机核/负变体×2/TDD+全量绿灯/边界只动 Touches/完成自查+不 commit），下文留证。

## 做了什么

1. **生成器** `tools/skill_pack_gen.py`（stdlib+PyYAML，确定性装配零 LLM 零时间戳）：单域出包（域目录=含 manifest.json）；切片声明 `--models` 显式子集（必填，空声明 exit 2，重复去重保序），四层拒收按序=未知模型（不在 model-registry.json models）→ 非 business-core 阵营（如 MU camp=build-contract，报「声明含非 business-core 阵营模型……检索面纪律」，**camp 判定先于文件存在性核对——先阵营后存在性**，同 core 瀑布 §0/§5，故 bohai 声明 MU 报阵营而非缺文件）→ 域缺声明模型文件（报「缺声明模型 Mx」，边界规则 5 同款）→ model_type 与注册表不符；口径卡装配闸=M7 在切片而 M1/M2/M3 缺伴 → 报「口径问答卡装配缺声明模型」不产残卡，M7 未声明 → 出包但口径卡节如实注记（L0 示例切片 M1,M3,GLS 可出包）。camp/yamlFile/modelType 真源=model-registry.json、前缀面真源=model-deps.json idPrefixes——读 JSON 不 import core。
2. **三件套**（SKILL.md 单文件三节 + skillpack.json 机读镜像，双载体同票 35）：①frontmatter（name=<域>-semantic/description/domain/slice-models/citation-prefixes——idPrefixes 反查声明模型的 ID 前缀回答面/人审状态）+工序路由（问答四步静态化常量：显式锚定→名称解析→闭包装配→可拒答，注记运行时真源=语义服务）；②口径问答卡（M7 逐口径：问题样例/描述/查询出口/行为/承载对象/参数/**命中 ID 集**/口径要点=规则 expression/narrative 摘录带 via——装配来源同票 35 口径节三支并集）；③引用纪律与拒答边界（ID 引用格式常量+camp 面外=registry camp≠business-core 的模型前缀（bohai 实装 SCR-/MU build-contract）+切片外=business-core 未入切片前缀（bohai 实装 M5 ACTOR-/ROLE-/PERM-、M6 FLOW-）+禁用词=GLS status 含「禁用」（bohai 实装老完成率 GLS-BOHAI-001）+可拒答声明常量）。
3. **引用核对口径**：校验面=口径卡装配链（behaviorRef/objectRef/appliedRules/reusedBy/ownerEntity）+GLS relatedObjectRefs，且跨模型引用只对两端都在切片的核对（靶模型不在切片=未装载无从核对，该面由口径卡四模型齐备闸兜住）——对比 app_pack_gen 全域校验是有意收窄，元素 id 重复五集合全查不收窄。
4. **单测** `tools/test_skill_pack_gen.py` 35 例全绿（TDD 先行，合成 demo 域+仓内真注册表 --schema-dir 注入）：切片声明（camp 面外/未知模型/缺文件/model_type 换/缺 --models/空声明/重复去重/camp 判定先于文件核对八例）、口径卡闸（M7 缺伴 exit 2/L0 示例切片出包+注记）、确定性（双跑字节一致/零日期 token 零时间戳键）、内容契约（人审头/三节齐+frontmatter/citation-prefixes 精确序列/路由四步/口径卡 hitIds 精确序列+via/面外面外切片外/禁用词/GLS 悬空关联引用 exit 2）、CLI 三模式+缺 schema exit 2、真域回归（三节齐+人审头/CORE-01 冻结集 ⊆ QR-BOHAI-001 卡 hitIds/禁用词面/入库副本 --check/剃 m3 负变体/真域 MU 负变体）。
5. **出厂集** `fixtures/skill-pack-gen/`（照票 35 格局）：assertions.json 6 条（AC1 双探针=三节齐+frontmatter+人审头部、core 子进程「日产量口径是什么」命中 ⊆ skillpack.json 口径卡 hitIds；AC2=--check 再制一致+tempfile 双跑字节一致；AC3 双负变体=剃 m3 副本 exit 2 指认 M3、真域 --models M1,MU exit 2 报阵营）；negative-variants/bohai-no-m3（金包切片全量声明面副本=manifest+M1/M2/M7+GLS，剃 m3）+README 记副本范围与 --schema-dir 显式注入缘由；cases/skill-consumption-checklist.md 消费用例单四场景。
6. **入库副本** `exports/skillpkg/bohai/`：SKILL.md 107 行（frontmatter+三节）/skillpack.json（slice/calibers 4 卡/glossary 10 条+citationDiscipline），gen 后落盘禁手改。
7. **登记**：references/repo-layout.json exports 条目 patterns 增 skillpkg/*.md、skillpkg/*.json+purpose/producer/description 补注（实跑归档闸驱动，513 文件全过）；specs/modules.md 两处=skill-publisher 占位卡 dated 注记（照票 35 app-generator 手法）+脚本清单 skill_pack_gen.py 行。

## 取舍

- **金包切片取 M1,M2,M3,M7,GLS，非 AC 表给定的 M1,M3,GLS（唯一偏差，回报项）**：AC 表期望列（exit 0+三件套齐+抽问同源）机制性要求口径卡 hitIds 覆盖 CORE-01 命中（含 QR-BOHAI-001/BH-BOHAI-QueryWellDailyOutput），而 QR 在 M7、行为链在 M2——给定示例切片装不出齐的口径卡。取五模型切片恰=core 检索引用面 CITATION_MODEL_TYPES（OBJECT/BEHAVIOR/RULE/REPORT/GLOSSARY 五型），同源红线最稳；生成器仍支持无 M7 切片出包（如实注记），L0 的 `--models M1,M3,GLS` 保留为语法示例可用（单测钉死 exit 0）。偏差已写进 fixtures/skill-pack-gen/assertions.json description 供验收复核。
- **camp 判定先于文件存在性**：负变体 B（--models M1,MU）若先查文件会报「缺声明模型 MU」——报因错则检索面纪律没被说出来。照 core「先阵营后存在性」排序后，bohai 无 mu-ui-model.yaml 也照样报阵营，负变体不必造 MU 文件。
- **跨模型引用核对收窄到两端都在切片**：切片的意义就是子集——M2 不在切片时 M3 的 reusedBy 指向的元素未装载，核对是伪命题；硬核对会把 L0 示例切片误杀。口径卡的完整性由四模型齐备闸独立兜住，两闸分工不重叠。
- **生成器本体零子进程耦合，同源对账归出厂集**（承票 35 同款取舍）：口径卡按结构装配（⊇ core 命中面），AC1 探针跑 core 子进程对账；不把 core 解析结果烤进技能包，core 行为演进不倒逼技能包再生成。
- **GLS 消费面=术语全账+禁用词子集**：切片声明了就要消费——术语表（id/term/aliases/status/termType/definition/relatedObjectRefs）进 JSON 供名称解析词表，禁用词进 MD 第③节拒答边界；definition 含「2024 年废弃」等叙述照登（零时间戳红线禁的是生成器盖时间戳，非源文本数字，单测 DATE_RE 验证无日期形态 token）。

## 坑

1. **fixtures 副本下 schema 自动定位不可达**：schema 定位照 core 手法（`<域>/schema` 或 `<域>/../schema`），ontology/bohai 命中上级，fixtures/skill-pack-gen/negative-variants/bohai-no-m3 两头都不命中——负变体 cmd 显式 `--schema-dir ontology/schema`；README 记了缘由，README 缺这句后来人会把报因「schema 目录未找到」误判成负变体失效。
2. **M7 缺伴的报因顺序**：第一版引用核对先行，M7 在切片而 M2 缺时先报「引用失效: behaviorRef 不在已解析元素集」——红是红了但报因不对（真因是装配缺伴模型非引用指空）。修正=跨模型引用核对收窄到两端在切片，让缺伴走到专用报因「口径问答卡装配缺声明模型」。
3. **build_slice 版本号被覆盖**：metas 在 load_domain 后回填各模型 version，build_slice 初版又 `{**meta, "version": ""}` 盖回空——单测没断言 version 所以没红，自查读码时抓到；修正为 dict(meta) 直用。教训：回填型字段只在一处写。
4. **同 tmp 二次 make_domain 撞目录**：GLS 悬空引用用例在 setUp 已建域的 tmp 上再建一次，FileExistsError——改用独立子目录（tmp/"glsbad"）。
5. **JSON cmd 里的 python -c 换行**（承票 35 坑 2）：多行探针代码内层字符串一律单引号、换行用真实 \n、`'---\\n'` 这类转义在 JSON 串里要双反斜杠——照票 35 先例一次写对。

## 收尾

- AC1–4 逐条实证：AC1 正例 exit 0+三件套齐（探针缺节 []/frontmatter True/人审头部 True）+口径同源（core 命中 5 ID ⊆ skillpack.json QR-BOHAI-001 卡 hitIds，口径卡缺 []）；AC2 双跑字节一致+--check exit 0+篡改探针（单测 stale exit 1 载体）；AC3 双负变体 exit 2（剃 m3 报「缺声明模型 M3」；M1,MU 报「非 business-core 阵营 MU」）无残包；AC4 人审头部在场+布局登记（归档闸 513 文件全过）+exports patterns 增补。
- `bash tools/ci.sh` 四闸绿：446 单测 OK 含 skip 3（411→446，+35 全绿零倒）/ 出厂集 14/14（13→14，+6 断言）/ 边界闸无违规 / 归档闸全过；`python3 tools/skill_pack_gen.py ontology/bohai --models M1,M2,M3,M7,GLS --check exports/skillpkg/bohai/SKILL.md` exit 0。
- 回归底线：ontology/ 与 skills/ 正文零改动；app_pack_gen/core/graph_index 零改动（git status 复核，改动恰为 Touches 清单）；现有 411 单测与 13/13 出厂集零倒。
- 不 commit（按交接包，验收归主窗口）。
