# AGENTS.md · All-agent 仓库协作说明

> 任何 agent/新窗口进入本仓，先读本文件，再按"新窗口入口"恢复上下文。

## 这个仓库是什么

**All-agent = 企业语义中台 + 建造/运行一体化平台**：本体仓（Git+YAML）为唯一真源，多输入（需求/数据库/源代码/文档）多输出（应用包/Skill/MCP/分析报告/运行时语义服务），三循环自迭代。形态：**skill+脚本，不建代码系统**。

- 建造方法：`sdd-flow2`（~/.agents/skills/sdd-flow2，从 sdd-flow 分叉，专攻 skill+脚本形态）
- 核心纪律：skill=深模块（卡/边界/依赖/输入输出契约/出厂集/归档）；约定不落闸等于没有

## 新窗口入口协议

1. 读本文件 → `docs/prd.md`（顶部状态行判断阶段）
2. `CONTEXT.md`（术语表）、`RESOURCES.md`（R 编号信源清单）
3. `specs/`（卡与登记表）、`tickets/`（进度）
4. 报告"当前在阶段 X、产物 Y 已有/缺失"，给出下一步，**停下等拍板**

## 目录地图

| 路径 | 是什么 |
|---|---|
| `docs/prd.md` | PRD（状态驱动：粗稿→逼问中→已定稿） |
| `docs/design-sdd-flow2.md` | sdd-flow2 设计案（两条验收主线） |
| `docs/`（子目录） | reviews/（外部审查）/ walkthrough/（端到端走查）/ proposals/（提案池 PROP）/ impact/（影响分析）/ adr/（决策记录） |
| `references/` | 调研落盘：omf-spec-digest（OMF 规范精读）/ existing-research-inventory（既有调研盘点）/ tech-selection（选型） |
| `diagrams/` | 三张图：all-agent（大总架构）/ skill-structure（skill 组织）/ sdd-flow2（建造流内部） |
| `specs/` `tickets/` `policies/` | 骨架已立，随阶段推进填充 |
| `ontology/` | 本体仓：schema/（八模型 schema+模型注册表+依赖白名单，票 03 立七模型、票 10 增 GLS）；首个业务域渤海域已进仓（bohai/：6 模型+glossary+manifest，语义闸全绿） |
| `tools/` | schema_check（L1/L2/L4+必填/一致性对/禁用词）+ graph_index + install_skills（+hooks/ pre-commit 安装位闸）+ proposal_check + check_citations + guard_corpus_check + 三闸（skill_deps/fixture_run/archive_check）+ ci.sh |
| `fixtures/` | 出厂集七套全建 7/7：schema_check / graph_index / onto-modeler / db-reverse / semantic-service（含 guard-corpus 守卫例集）/ impact-analyzer / proposal-pool |
| `lessons/` | 施工日志：每票一篇（03 起） |

## 流水线续跑协议（一期票 04–09 已收官；二期票同协议）

新窗口接续流水线时：

0. 新 clone 一次性 setup：`git config core.hooksPath tools/hooks`——启用 pre-commit 安装位漂移拦截（票 15；钩子只跑 `install_skills --check`，漂移/孤儿即拒提交；不配置本项则钩子静默不生效，对其他 clone 无副作用）。
1. 读 `tickets/NN-*.md` 找 Status: todo 的最小票号——交接包在票面内（自包含，不依赖旧窗口记忆）。
2. 严格串行：一派一验一提交。派发用票面交接包原文；验收 = L0 自己跑 `bash tools/ci.sh`（必须四闸全绿）+ 逐条核票面验收；过了翻 `Status: done` 再 `git commit`（一票一提交）；不过打回（附红灯输出）。
3. 同一任务连续两次不合格 → 主窗口接管自写并记原因。
4. 一期已收官：票 09 完成端到端走查与收官报告（commit 9ca5db2，报告 `docs/一期收官报告.md`，含缺口清单与二期四批建议）。
5. 当前状态锚点：一期九票全 done（9ca5db2）；二期第一批 done（10=0474bc8 / 11=a0359e0 / 12=634dcbd）；治理批 done（13=987525c / 14=c56ed08 / 15=3bc3b93）；第二批 done（16=bad916c / 17=29f890b / 18=fe36610 / 19=1086c2b）；整改票 20 done（审查尾款五件套，见 tickets/20）；第三批开工：票 21 文档对齐 → 票 22 语义服务核心提纯 → 票 23 MCP stdio 服务器+发布物 → 票 24 端到端实弹走查（venv 安装 mcp，用户已批）。第三批 done：21 文档对齐=af4a68b / 22 语义核心提纯=a98add1 / 23 MCP 服务器+manifest=7bfd781 / 24 端到端实弹=eecd17b（语义 MCP 服务可用，运行式见 docs/mcp-server.md）。第四批（方案 2026-09-19 用户批准）= 票 27 缺 id 盲区演进 / 28 元循环探针 meta_probe / 29 信号路由表+体检节奏。第四批收官：27=a4fb938 / 28=5c149c1 / 29 信号路由表+体检节奏=7a11d59（F14 元循环闭环）。第五批收官（定时任务用户预批准）：30 需求探索器=42bb42c / 31 代码逆向器=0943cc6 / 32 文档萃取器=fb4f474 / 33 模式件库=7c99306（含批收官探针留痕 docs/meta/体检-2026-09-20 与豁免复核 9 条更新）。第五轮审查（票 25–33）两 P2 实锤（patterns 裸仓根红灯+废弃/禁用缝隙），整改票 34 done（patterns 排除+仓根挂探针硬闸/废弃禁用换算/latent 收敛/悬账入账）；第六批收官：35 F9 应用生成器（本票前序提交）/ 36 F10 Skill 发布器（本票提交）——二期功能面（F1–F14+模式件库）全落地。二期收官对账已落盘：docs/二期收官报告.md（六批 27 票总览/六条回归底线/缺口清单现行/第三期建议）。第六轮审查（二期外部审查：票 34-36+收官报告）三票全过无 P1/P2、收官报告 4 处数字勘误，整改票 37 done（收官报告 4 数字现跑现取勘误/回归底线第七条 manifest --check/登记 devkit+skillpack 两类/观察项三条入账）。第三期 B 线方案已落盘（docs/第三期B线拆票方案.md，2ec5bcb）并拆票：38 重复id检测 / 39 工具卫生两件 / 40 SDK版本钉可执行化 / 41 L3确定性闸（子集清单已 L0 裁决入票面），当前下一张 = 票 38。批次三两设计案已落盘待 Owner 过目（docs/design-l5-scoring.md：L5 离线批评分器推荐+评分器模型选型待拍板；docs/design-human-review-gate.md：审记旁档状态机+哈希锚定推荐+三生成物初始档位待拍板）。第三期 B 线收官：38=4b81b98 / 39=c98d9ac / 40=571d44d / 41=0104735（探针留痕 体检-2026-09-20-3 PASS；收官记录=二期收官报告 §10）。两设计案已裁决（2026-09-20，裁决记录落 design-l5-scoring.md §9 / design-human-review-gate.md §8：L5=运行时子agent注入、人审闸=§6七点全按推荐），C 线拆票方案落盘（docs/第三期C线拆票方案.md）并已拆票落盘 42–47（42 L5评分器骨架 / 43 Golden扩编+rubric / 44 L5节奏接线 / 45 人审闸状态机 / 46 三生成物接线 / 47 文档对齐+ADR0003）。C 线收官：42=db4beec / 43=0cb5efc / 44=348fa9c / 45=2c7e565 / 46=6f85807 / 47=8a79895（L5 评分面+人审闸承载全落地；探针留痕 体检-2026-09-20-4 PASS；收官记录=二期收官报告 §11）。L5 首次全量实战完成（docs/meta/l5-评分-2026-09-20 PASS，单代理内独立评分降级形态如实留痕 lessons/48；Q8 参照答案内部矛盾实弹发现待开票）。第七轮审查（B线+C线+L5首跑，票 37-47）发现 P1 一项（8a4a632 带红入仓：收官追加文件未复跑四闸，lessons/48 缺三节）——L0 已紧急清偿翻绿（7dd3bf2，报告落盘 docs/reviews/2026-09-20-phase6-*）；P2-A L5 门槛量纲失配与 P2-B out/ 漂移待整改票。第七轮整改已拆票：48（协议第⑩条「最终树四闸」+out/确定性化+P3 五小件含 ac8 修复）/ 49（L5 门槛归一化——Owner 已批归一方案+CIT×6+反注入+disqualifiers 一致性项），当前下一张 = 票 48。动土前先跑收官报告 §2 两条回归底线命令。尾款票 25 done（d0be9c2，camp 裁剪 P1）/票 26 卫生清偿与流程补丁 done（ae53845）。
6. 批次纪律三件套：扩张/新批次须用户批准入账 + PRD 同步 + 批收官推锚点——推锚点/回写文档的字符串替换必须带断言验证（替换后 grep 复核预期内容在位），静默失配=事故（票 24 收官 replace 与收官报告 sed 两次同款实证，见 lessons/26）。
7. 审查报告必落盘 `docs/reviews/`，不以对话转述存活；整改票引用审查结论须引落盘路径。
8. 验收扫描面必须对得上 AC 声明面：AC 说"全仓"就查全仓含 `.py`；票面引用"本票 AC 表"必须真实存在（票 14/票 20 两次教训）。断言真源：出厂断言以票面 AC 表为正，specs/*.md 仅为一期基线+汇总指针。
9. 批收官清单（票 29 起）：① `python3 tools/meta_probe.py ontology/bohai --out docs/meta/体检-<日期>.md` 留痕（硬闸必须全绿，路由表自检在内；同名已存在则加序号后缀追加，不覆盖旧留痕）；② 锚点推进入账（带断言验证）；③ 本批审查报告落盘 docs/reviews/（如有审查）；④ 豁免复核结论更新 docs/meta/exemption-reviews.json；⑤ L5 全量跑（12 问 × 3 子 agent 派发）留痕落 docs/meta/l5-评分-<日期>.md/.json——软闸：红灯开单走信号路由分道，不阻塞收官留痕与锚点推进（派发契约见 semantic-service skill references/l5-dispatch.md，票 44）。Owner 抽检校准（随票 44 定）：L5 绿的批次 Owner 按比例抽检评分结论，抽检被人工复核证伪即推翻该问结论、按元模型错道开票修 rubric/评分提示词（ADR 0002「复核证伪则推翻」同款句式）；⑥ 审记 verify（devkit/skillpkg，票 46 起）：`python3 tools/review_gate.py verify exports/devkit/bohai/devkit.md`、`python3 tools/review_gate.py verify exports/skillpkg/bohai/SKILL.md`——审记缺失或失效=收官挂账项，不阻塞四闸（manifest 免审级不要求审记）。探针硬闸红灯=下批首票。
10. 翻 done 与批收官提交前，必须对「将提交的最终树」复跑 `bash tools/ci.sh`——CI 结论只对跑它那一刻的树负责（8a4a632 带红入仓事故：验收时点绿 ≠ 最终树绿，第七轮 P1）。

## 使用方式（建成后）

工作流各功能 = 用户级 skill（需求探索/本体建模/逆向/生成/治理），Kimi Code 按触发面自动路由；闸与工具在 `tools/`，CI 即四闸。
