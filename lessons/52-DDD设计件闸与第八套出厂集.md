# 52 · 票 51：tools/ddd_check.py 五查 + fixtures 第八套（第四期 DDD 线批次一）

- 日期：2026-09-20
- 依据：tickets/51-ddd_check闸与第八套出厂集.md（AC 表 L0 定稿照办）+ design/ddd/README.md（票 50 格式真源，判定基准从它反推）+ tools/schema_check.py（报告结构/退出码/解析族口径）+ ontology/schema/model-deps.json（idPrefixes）+ docs/第四期DDD线拆票方案.md 批次一
- 触发：第四期 DDD 线批次一票 51 施工（L2 自主档串行一票）
- 卷号说明：票号 51 但施工日志顺延落 lessons/52（lessons/51 已被票 50 占用——延续票 48→lessons/49、票 49→lessons/50、票 50→lessons/51 同款顺延惯例；票面 Touches 写 lessons/51，已按主窗口交接包「lessons/52 顺延」执行）

## 做了什么

1. **五查闸（AC1/AC4）**：新建 `tools/ddd_check.py`，CLI `ddd_check.py <design目录> [--ontology <本体目录>] [--json]`，退出码 0/1/2 同族。五查违规码：ddd-cross-agg-embed（D1 点号路径内嵌）/ ddd-term-ref（D2 词条悬空与非词条形态）/ ddd-invariant（D3 清单缺失/空/三元组缺一）/ ddd-mapping（D4 映射聚合不在设计件集合+缺表名/列名/term 声明）/ ddd-naming（D5 四命名空间重名报双位置+ID-role 注册前缀+事件名大写下划线）。工程形态照票面：failFast=false 一次收集全部违规逐条输出（每条带文件+行定位，行号取 YAML start_mark）；「待人审清单」软节（单聚合零事件/单聚合实体数超 4/事件生产者·消费者·仓储聚合不在设计件聚合集合）只报告不进退出码。
2. **第八套出厂集（AC2/AC3）**：`fixtures/ddd-modeler/`——inputs/ontology/order（自造最小订单域词条输入：AGG-ORDER-001/002/003 + GLS-ORDER-001..007，schema 机读表经符号链接取仓内 ontology/schema 单一真源）+ expected/（绿灯样本四类设计件全齐，形照 README §1–§4 最小合法样例）+ negative-variants/ 七目录（五查负变体各一 + ac3a-multi-error 三类错误一次收齐 + ac3b-granularity 零事件软节 exit 0）+ assertions.json（DDD- 前缀 11 条断言，cmd-fails 各钉各违规码+关键 token）。出厂集 16→17 套全过。
3. **单测（AC4 双层实证）**：tools/test_ddd_check.py 43 测试全绿——五查各一组负变体 + 绿灯零违规 + failFast 批量报文 + 人审软节 + ExitCodes 类断言精确退出码整数（出厂集 cmd-fails 只能钉非零，2 路径以「配置错误」报文钉、整数由单测钉，双层合成 AC4 实证）+ ResolutionFamilyAlignment 类钉解析族口径对齐（ref 键值不自证存在/未注册前缀不入集/DICT 入集）。全仓单测 578→621。
4. **specs/ddd-modeler.md 断言表填充（AC5）**：AC1a–AC4c 与 fixtures/ddd-modeler/assertions.json 断言一一对应（同标签同真源），承接票面 AC 表 AC1a–AC6；AC7 行留票 52 占位。
5. **README 回写一行**：design/ddd/README.md §5 表后增「票 51 判定补注」——点号路径判定归 D1（他聚合卡主词条即红/自身引用合法/左段解析不到归 D2）、词条集合=collect_definitions 同族口径、生产者/消费者/仓储聚合完备性归人审软节（映射聚合例外硬闸）、文件不可判读报兜底码 ddd-file-kind。

## 取舍

- **独立实现 vs import schema_check 解析族**：防踩坑建议「独立实现保持零耦合，口径对齐写单测」采纳——带行号 YAML 装载（LineLoader/MDict/MList）、iter_mappings、id_model_of、collect_terms（=collect_definitions 同族：id/*Id 定义键、非 ref 键、值带 idPrefixes 注册前缀）为独立副本，两闸互不 import；口径漂移风险由 ResolutionFamilyAlignment 单测钉死（ref 键值不自证存在等三条同款裁决逐条有测试）。代价是约 60 行样板复制，换来 schema_check 零改动（本票红线）与两闸可独立演进。
- **fixture 自管词条、不借真域 bohai**：输入本体用自造 order 域词条（防踩坑点 5 明示）——bohai 词条演进（改 id/加禁用词）不会波及本套；符号链接只引 schema 机读表（idPrefixes/refKeys 真源单一），不引域文件。前缀仍用注册前缀 AGG-/GLS-（自造的是「域段+序号」不是前缀——前缀必须注册否则 D5/D2 全红，这与真仓口径一致）。
- **expected/ 即正例对象，不设生成物目录**：ddd_check 是闸不是生成器，设计件本身就是 ddd-modeler 工序的产物——交接包「绿灯样本跑通的产物形态」落地为 expected/（四类设计件全齐），inputs/ 只放本体词条输入，避免同一组设计件存两份漂移。断言 cmd 直接跑 expected/。
- **兜底码 ddd-file-kind（票面五查之外第六码）**：语法错/顶层非映射/kind 不在四类的文件若无承载码将静默逃逸全部五查（kind 判别失败=无查可施），违反「约定不落闸等于没有」；故增文件级兜底码并在 README 补注一行。票面 AC 面不变——负变体不涉此码，五查码与票面一一对应。
- **红因纯净 vs 跨文件级联**：卡文件不可判读（file-kind）或聚合主词条变异时，其余文件对该聚合的映射引用连锁报 ddd-mapping——沿 schema_check 先例（语法错文件的定义不收集→他文件悬空照报，ac2-bad-yaml 同形态），级联是真后果照报不吞；单测对级联场景断言「目标码在场」而非「红因唯一」，出厂集负变体全部单点变异保证真唯一（d3 例外：清单空+三元组缺项两实例同码，正对 AC1c「为空/缺项」双形态）。
- **D1 范围统一到全部词条面**：任务判定口径举「聚合卡属性列表」为例，落地为聚合卡属性/实体属性/值对象/事件载荷/映射列 term 五个词条面统一判定（同一 JOIN 暗桩在任何面同罪）；载荷面 owner=生产聚合、映射面 owner=映射聚合，左段=自身聚合的点号路径合法。
- **ID-role 字段红因分工**：聚合主词条/实体/生产者/消费者/映射聚合/仓储聚合的**形态**（无前缀/带点号/非字符串）归 D5 naming，**悬空解析**归 D2（聚合主词条+实体）/D4（映射聚合）/人审软节（生产者/消费者/仓储聚合——跨域消费者是合法设计形态，硬闸会误伤）；单一红因不混，同 schema_check「悬空归 dangling-ref、本组只补语义闭合向」同款分工。
- **status 字段本闸不查**：草案/已审的机判面在归档闸（票 50 design-card 类），两闸不重复追责；本闸只查 README §0.6 kind 与四类设计件 schema 结构面。
- **lessons 卷号顺延**：票面 Touches 写 lessons/51，实际顺延 lessons/52（lessons/51 被票 50 占用，日志只增不改），照票 48/49/50 三次先例执行并在卷号说明留痕。

## 坑

- **dict.setdefault 收集重名=静默吞重**：重名检测若用 `namespace.setdefault(value, loc)` 收集（键唯一化），后续逐 key 查重永远查不到第二处——必须收集为出现位列表再逐处比对首现。首版实现即踩此坑（test_duplicate_event_name 报 []），票 38 duplicate-id 是「同域索引+先出现/后出现」列表形态，照抄才对。
- **负变体构造删整行会破坏 YAML 列表结构**：删「`- trigger: …`」这类列表首行会让余下键行并入上一容器（映射变标量/清单变映射），触发的是结构性红因而非目标红因——负变体一律用**整块替换**（把完整条目块替换为缺目标字段的完整条目块），单测 test_invariant_missing_trigger 首版即踩。
- **fixture_run cmd-fails 只能断言非零退出码**：钉不了 1 还是 2——本票手法：2 路径用「配置错误」报文钉（该报文仅在 exit 2 分支输出，报文在场即码为 2），1 路径用违规码钉，精确整数由单测 `main()` 返回值断言。后票要精确码断言可循此双层。
- **f-string 拼词条 ID 忘零填充**：`f"AGG-ORDER-{n}"` 生成 AGG-ORDER-4，与词卡里的 AGG-ORDER-004 形同实异→悬空四连红；ID 拼接一律 `{:03d}`（本仓 ID 形态=前缀-域-三位序号）。
- **管道里 `$?` 是 grep 的退出码不是被测工具的**：批量冒烟验证退出码必须单跑（`cmd > /dev/null; echo $?`），带管道的循环里 echo 到的永远是最后一个管道段的码。
