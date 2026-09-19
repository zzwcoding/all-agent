# 施工日志 18 · proposal-pool skill 与提案检查工具

日期: 2026-09-19
角色: L2 编码（自主档）
票: tickets/18-proposal-pool-skill.md（AC 真源=票面 AC 表 AC1–6；触发面/提案规范/proposal_check 四类检查均为 L0 设计裁决定稿，照办）
交接包注记: 主窗口防踩坑清单（卡转正手法、边界闸反引号白名单、target 判定过真域+独立实现、出厂集格式、规范落两处、双落安装位、TDD 全绿、边界清单）均已照办，下文逐条留证。

## 做了什么

1. **出厂集先行（红→绿）**：`fixtures/proposal-pool/` 先落——正例 `cases/`（PROP-BOHAI-001 add RULE-BOHAI-020 新规则 + PROP-BOHAI-002 modify AGG-BOHAI-002 真实元素，各带证据附件与非提案 README）+ 负变体五类各一（missing-field / target-not-exist / target-already-exists / same-target-conflict / evidence-missing）另加 bad-enum（AC4 后半枚举面，AC 表明写「必备字段缺失/枚举值非法」两半，五类清单不含故补一）+ `assertions.json` 9 条断言（2 file-exists + 7 cmd-*，cmd-fails 的 outputContains 逐条钉死违规码与关键细节）。红相实测：恰好 7 条 cmd 全红且红因纯净（工具不存在的 FileNotFoundError，无一条误绿）；既有出厂集零扰动。
2. **TDD 工具**：`tools/test_proposal_check.py` 39 条单测（Schema 12 / Target 7 / Conflict 6 / Evidence 5 / Cli 9），tempfile 自建最小本体仓（model-deps.json + 一个域 yaml）+ `--root` 注入，**零真实仓接触**（红线）；真实仓端到端红绿由出厂集承载。红相：模块不存在 1 error → 实现后 39 OK。
3. **实现 `tools/proposal_check.py`**（确定性零 LLM，stdlib+PyYAML）：①proposal-schema（七必备字段+三组枚举+id 正则+同池 id 唯一+YAML 头形态；schema 红的文件不进后续检查防连环误报）②proposal-target（modify/deprecate 靶必须在域、add 必须不在域；元素集口径照票 04 图索引——定义键 id/*Id 非 ref 键+idPrefixes 已登记前缀，**独立实现不 import graph_index**）③proposal-conflict（同靶两个 open 提案 change 两两不同值即矛盾；同值/draft/已裁决不参战）④proposal-evidence（剥 #锚点后仓根相对→提案目录相对两试；绝对路径与只剩锚点=红）。退出码 0/1/2 对齐仓内约定，--json 机读。ontology YAML 不可解析=配置错误拒判（部分元素集=说谎的元素集，同图索引红线；这是与 graph_index「无域拒建」的有意差异——空本体对提案检查是合法状态，全过 add、红 modify 语义自洽）。
4. **skill 落盘**：`skills/proposal-pool/SKILL.md` 薄壳（触发面一字不差/输入输出契约/起草四步/行为约定/出厂集）+ `references/signal-normalization.md` 信号归一指南（五类受理标准表、A/B/C 证据等级、逐字段归一细则、冲突与状态流转处置；全文域无关，成色照 db-reverse 逆向指导书）。
5. **规范落两处**：仓根 `references/proposal-format.md`（机器可核字段定义，§0 镜像声明与工具头注一字不差对齐）+ `docs/proposals/README.md` 规范指引一页（池说明/状态机速查/起草与自检指路）；本票未落任何真提案（真提案是票 19 的事）。
6. **卡转正**：specs/modules.md 的 `## skill: proposal-pool` 占位卡就地扩成完整卡（职责/层/目录双位置/触发面/reads/writes/依赖/Seam 与出厂集/边界九字段），**卡名保持 proposal-pool 不加后缀**（边界闸按名精确匹配，票 05 教训）；脚本清单增 `tools/proposal_check.py` 行。
7. **边界**：`.skill-deps-allow` 增 `fixtures/proposal-pool/**` 豁免行（带理由，照票 05/06/07/08 手法）；边界闸实测五 skill 全扫无违规，归档闸 306 文件全合规。
8. **安装位**：`python3 tools/install_skills.py sync proposal-pool` → rewrite 2 文件、sync 后复检零漂移；`--check` 五 skill 全一致零漂移；**注册表由 sync 原子自动入表**（4→5 项，含 proposal-pool）——票 15 AC6 的自动维护路径实弹验证通过，无工具 bug。

## 取舍（口径账）

1. **元素存在性独立实现而非子进程调 graph_index**（防踩坑 3 预授权二选一）：工具保持 stdlib+PyYAML、单测全走 tempfile 注入 root，零耦合零子进程开销；代价是 ~30 行口径代码与图索引重复——口径漂移风险用「文档互指」（工具头注/卡/格式规范三处都写明「口径照票 04 图索引」）+ 出厂集打真域（AGG-BOHAI-001/002/999、RULE-BOHAI-020 的红绿即口径回归）双保险兜住。
2. **同名定义键取首个命中**（同图索引 def_id_of 先到语义）：一个映射出现两个定义键属 schema 问题归语义闸，本工具不重复判定。
3. **conflict 只判 change 两两不同值**：票面原文「change 类型矛盾」；同靶同值（两份 open 都要 modify 同一元素）是竞争提案但方向不矛盾，机械面判不了内容优劣——按「闸只报矛盾不判对错」的裁决纪律留给人，重复查重落在归一指南 §5 的工序纪律里。
4. **schema 红的文件短路后续三查**：脏数据的 target/evidence 会产生连环误报（如缺 ref 时 evidence 检查无从谈起），红因纯净优先——负变体断言因此敢钉死单一违规码。
5. **证据解析双基准（仓根相对优先、提案目录相对兜底）**：真提案的证据多在仓内他处（B 级走查记录等）走仓根相对，出厂集证据随池落盘走提案目录相对，一个规则通吃两类场景；绝对路径拒收防证据逃逸出仓。
6. **空本体不拒判**（与 graph_index「无任何域拒建」差异）：fresh 仓全过 add、红 modify 语义正确，拒判反而错杀；但 ontology YAML 不可解析仍拒判——假「不存在」比空「不存在」危险得多。
7. **仓根共享规约不入 skill 私件、正文平文指路**：`references/proposal-format.md` 在仓根 references/（票面指定），若在 SKILL.md 反引号会踩边界闸规则 4（references 首段被认作本 skill 私域，先于卡声明面判定而报悬空引用）——实测确认后改为正文平文提及，卡 reads 仍显式声明该共享件（诚实声明面，闸不扫描卡）。
8. **AC4 拆两半各给负变体**：missing-field 与 bad-enum 各一，断言分别钉「缺必备字段+status」与「published+非法」——AC 表原文就是「缺失/非法」两半，五类清单只列了前半，按「AC 表=真源」补齐。

## 坑

- **YAML 头里 `#` 起注释**：`ref: #只有锚点` 被解析成 ref: None，evidence 检查根本没跑到就死在 schema——anchor-only 负例必须写成引号包裹的 `"#只有锚点"` 才能真正进 evidence 分支。同理给提案模板的示例值要留意 `#`、`no`、`off` 等 YAML 陷阱。
- **测试工厂的字段拼装漏一行**：提案文件工厂里 id/title/status 定义了却忘了 append 进行列表，26 条单测齐刷刷报「缺必备字段」——红相 ≠ 实现红，先查测试脚手架本身。修一行后 39 条只余 2 条真问题。
- **配置错误优先于逐文件违规**：初版把元素集收集放在「有有效提案才执行」分支，「ontology YAML 不可解析」在池内提案本身也坏时被 schema 红盖住（rc 1 而非 2）——配置错误必须前置于一切文件处理，退出码语义才对齐「2=用法/配置」。
- **边界闸规则 4 先于卡声明面**：skill 正文反引号 `references/xxx` 一律先按「本 skill 私域悬空引用」判定，卡 reads 里声明了也救不回来（continue 短路）——仓级共享件的指路只能平文，这条坑已回写进取舍 7 供后续票参考。
- **fixture_run 的 outputContains 是子串匹配**：断言词要选违规消息里稳定出现的形态（如「不存在」而不是整句），且注意中文数字词（「2 个」）换内容就会漂——跳过计数断言用「跳过非提案 md 文件」前缀+「解析提案 2 份」双钉。

## 验收（对照票面 AC 表，逐条实证）

- [x] AC1：`python3 tools/proposal_check.py fixtures/proposal-pool/cases` → exit 0「结论: 全过」，解析提案 2 份、跳过非提案 md 文件 3 个（README+两证据附件，只解析 PROP-*.md 的契约行为同时被钉住）
- [x] AC2：`…negative-variants/target-not-exist` → exit 1 `[proposal-target] …: modify 的靶元素在 ontology/ 真域不存在: AGG-BOHAI-999`
- [x] AC3：`…negative-variants/target-already-exists` → exit 1 `[proposal-target] …: add 的靶元素在 ontology/ 真域已存在…: AGG-BOHAI-002`
- [x] AC4：`…missing-field` → exit 1 `[proposal-schema] 缺必备字段 \`status\``；`…bad-enum` → exit 1 `[proposal-schema] status 值「published」非法（合法值: draft/open/accepted/rejected）`
- [x] AC5：`…same-target-conflict` → exit 1 `[proposal-conflict] PROP-BOHAI-001.md × PROP-BOHAI-002.md: 同靶元素 AGG-BOHAI-001 的两个 open 提案 change 矛盾: modify…vs deprecate…裁决在人`
- [x] AC6：`…evidence-missing` → exit 1 `[proposal-evidence] 证据文件不存在: evidence/ghost-note.md（已试: 仓根相对、提案目录相对…）`
- [x] 出厂集断言面：fixtures/proposal-pool PASS（9/9 条，含 7 条 cmd 钉码）；单测 39 OK；`bash tools/ci.sh` 四闸绿
- [x] 触发面一字不差：「把这条信号起草成提案/过一遍提案池/查提案池状态」卡与 frontmatter 一致；边界闸无违规
- [x] 安装位双落零漂移（sync rewrite 2 文件+复检零漂移；`--check` 五 skill 全一致）且注册表含 proposal-pool（sync 自动入表，4→5 项）
- [x] `git config core.hooksPath` → `tools/hooks`（未动）

## 偏差与遗留

- 负变体在票面五类之外多补 bad-enum 一个目录（AC4 后半枚举面的出厂集实证需要），其余零偏差。
- references/proposal-format.md 在票面 Touches 清单未列但为交接包「产出」与防踩坑 5 明文指定，已落；卡 reads 为此显式声明该仓级共享件（闸不扫卡，声明属诚实记账非机器需要）。
- 本票不 commit；票面 Status 留 todo，待主窗口按协议验收（ci.sh 四闸+AC 逐条）后翻 done 并提交。
- 真提案落池（docs/proposals/PROP-*.md）是票 19 的事；本票只在出厂集 fixtures 里放样本提案，不污染真池。
