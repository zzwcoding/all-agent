# 施工日志 06 · skill db-reverse + 出厂集

日期: 2026-09-17
角色: L2 编码（自主档）
票: tickets/06-skill数据库逆向.md（spec: specs/db-reverse.md AC1–4；PRD F6）

## 做了什么

1. **出厂集先行（红→绿）**：先写 fixtures/db-reverse/ 固定输入（input/bohai-8tables.sql，渤海域 8 表 DDL 子集）+ input/source-map.md（逐表逐字段注源 `R5·设定书附录 A.x`）+ assertions.json（9 条断言承载 AC1–4+注源齐+草案头部声明）→ 实跑全红（8 条 NG：产物文件不存在）；再按工序手工产出参照产物 expected-output/（object-inventory.md 对象清单 + mapping-evidence.md 映射证据 + dirty-signs.md 疑点清单 + bohai/manifest.json + m1-object-model.yaml），断言转绿。expected-output 就是 skill 在该固定输入上的标准产出样本，SKILL.md 六步工序（解析→抽取→疑点→草案+证据→过闸→交 Owner）与其一一对应。
2. **素材真源与转写纪律**：主窗口核查确认——R5（teach-petro-agent 设定书）当前版 v3 附录 A 收编了 v2 的 8 表字段级数据字典，git 历史无 CREATE TABLE 语句；故 fixture 输入=字典的忠实转写：字典给了类型的照抄（VARCHAR(8)/CHAR(2)/DECIMAL(10,2)/DATE/CHAR(1)），未给类型的 33 处「类型补记」、只给键语义的 5 处「列名补记」，全部在 source-map.md 逐字段留痕；单位/脏特征（吨方混写、A/B 班重复行、T-3 补录、新旧编码并存、30% 缺失、跨月作业等）随列注释照抄，零发明。
3. **skill 本体**：仓内 skills/db-reverse/ 正本（SKILL.md 薄壳：frontmatter 触发面原文「把这个库/这份 DDL 逆向成本体」+ 输入输出契约 + 六步工序路由 + 行为约定 + 细则索引；细则下沉 references/reverse-guide.md 一件：采信范围与补记规则、类型映射表、命名规范化与 PK→id 映射约定、关系判定保守边界、11 类脏特征识别清单、D/C/I 证据等级标注——全文域无关，grep 渤海/bohai/油田/井/CEP 为空）。写完原样安装到 ~/.agents/skills/db-reverse/（ditto + diff -r 校验一致）。
4. **AC 断言落地方式**：AC1=file-contains 对象清单含 8 表名+8 对象 ID（16 needle 一次断言全覆盖）；AC2=file-contains 映射证据含 8 个关键映射+「类型映射」「主键」约定词；AC3=cmd-succeeds 跑 schema_check 报「语义闸: 全过」+ manifest profile=v9-core；AC4=file-contains 疑点清单 8 个脏特征关键词（吨方混写/重复行/新旧编码并存/补录/30% 缺失/跨月等）+ 草案 YAML 含疑点点名（不静默吞的草案面）；另加草案头部声明断言「证据非权威，待 Owner 确认」（spec 行为约定）与 source-map 注源齐断言（A.1–A.8）。
5. **草案的保守边界（本票最有分量的取舍）**：DDL 无外键声明 → 草案零 AggregateRootRef/零 ASSOC/零 DICT，8 聚合根 50 属性全靠 D/C 级证据；同名键列的关联只是 I 级推断，15 条疑点（D1–D15）进 dirty-signs.md 并逐条点名回写草案描述。profile 取 v9-core（DDL 证据仅支撑 M1，M2/M3/M5 留给业务正向建模）。
6. modules.md db-reverse 卡目录字段照票 05 措辞改双位置说明；.skill-deps-allow 增 `fixtures/db-reverse/**` 豁免一条（同票 05 格式带理由）。

## 取舍

- **「不发明」与「可转写」的界线落在补记规则**：字典缺类型/列名时，逆向没法不补；补记本身不是发明业务语义，但必须（a）逐条留痕可审计，（b）等级降为 I（推断）标待 Owner 确认。这条写进了 reverse-guide §1.4，fixture 的 38 处补记就是它的示范。
- **AC4 的「不静默吞」拆成两层机械断言**：只断言疑点清单文件存在，清单可能是"写了但草案不体现"；故再加一条草案 YAML 含「吨方混写」「新旧编码并存」「待 Owner 确认」的 file-contains，把「疑点回写草案」也钉进 CI。纯文本断言仍不能证明语义完整，语义面由工序纪律（宁可多报不可漏报）兜底——同票 05 的「机械面+纪律面」双层思路。
- **草案零引用是特性不是偷工**：onto-modeler 参照产物有完整 ref 链（正向素材给了关系），db-reverse 参照产物 ref 为空——「无外键→零关系」正是「不发明 DDL 里不存在的业务语义」的机械面，出厂集 description 写明，防后续票把空 ref 误当缺陷补齐。
- **fixture SQL 方言保持中性**：标准 SQL + `--` 行注释，不用 MySQL COMMENT（方言私货会混入"约束感"）；主键声明照字典键语义写 PRIMARY KEY，A/B 重复行与主键声明冲突这类字典内矛盾照原样保留并注释——疑点是逆向的输入，不该在 fixture 里被"修好"。

## 坑

- **schema 符号链接的相对层数**：expected-output/schema 是上三级（expected-output→db-reverse→fixtures→仓根 ontology/schema）；同票 05 教训，动手前先按「链接所在目录」数了一遍并用注册表首行验证链接可达。
- **fixture_run 对占位目录的判定**：input/ 与 assertions.json 先落、expected-output 未建时，db-reverse 不再是 pending（有文件+有断言=实跑红）——正是红→绿想要的形态；若先建空目录会误判 pending，注意落盘顺序。
- **域词红线的隐蔽误伤**：正文里「口径」「字典」这类通用词安全，但单字「井」极易藏在词组里；写完对 SKILL.md + references 全文 grep 渤海/bohai/油田/井/CEP/渤南/渤中/渤西/注水/措施/检修/化验 十一词，本次零命中。
- **卡 reads 行的散文路径**：db-reverse 卡 reads 行「DDL 文件或库连接描述」无反引号路径，闸不扫散文——SKILL.md 输入输出契约同款写法保持一致，不引入新反引号 token。

## 验收（对照票面）

- [x] AC1–4 全过：fixture_run 对 fixtures/db-reverse/ 9 条断言 PASS（AC1 清单 8 表 8 对象 / AC2 映射证据 50 列全覆盖 / AC3 schema_check 全过+v9-core / AC4 疑点 8 关键词+草案点名）+ 草案头部声明 + 注源齐（A.1–A.8）（源：specs/db-reverse.md AC1–4）
- [x] 草案头固定声明"证据非权威，待 Owner 确认"：m1-object-model.yaml 头部注释逐字含声明，断言承载（源：spec 行为约定）
- [x] 素材逐条注源 R5：source-map.md 逐表逐字段 `R5·设定书附录 A.x`（8 表 50 列+全局注记），断言承载（源：取材锁纪律）
- [x] 边界红线：skill 正文域词 grep 为空；渤海域内容只在 fixtures/ 与草案 bohai/（expected-output 内）；正文反引号 token 仅卡声明面（ontology/schema/**、ontology/**）+ 依赖脚本 + 自目录文件 + Seam（豁免清单 1 条新行）（源：票面边界红线）
- [x] ci.sh 四闸绿：`bash tools/ci.sh` 退出码 0（见下回报摘要）

## 遗留与移交

- 票 07 semantic-service / 票 08 impact-analyzer 落 skill 时照本票+票 05 定例：正本双落、Seam 豁免行、AC 断言机械面+纪律面双层。
- 渤海域 8 表目前只有 M1 草案（expected-output 内）；真域 ontology/bohai/ 模型文件与端到端走查属票 09，届时可把 dirty-signs.md 的 D1–D15 当 Owner 裁决议程的输入。
- 补记规则（reverse-guide §1.4）首次实战，38 处补记的审计粒度是否合适，留体检议。
- 本票不 commit，产物待主窗口验收后统一提交。
