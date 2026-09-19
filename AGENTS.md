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
5. 当前状态锚点：一期九票全 done（9ca5db2）；二期第一批 done（10=0474bc8 / 11=a0359e0 / 12=634dcbd）；治理批 done（13=987525c / 14=c56ed08 / 15=3bc3b93）；第二批 done（16=bad916c / 17=29f890b / 18=fe36610 / 19=1086c2b）；整改票 20 done（审查尾款五件套，见 tickets/20）；第三批开工：票 21 文档对齐 → 票 22 语义服务核心提纯 → 票 23 MCP stdio 服务器+发布物 → 票 24 端到端实弹走查（venv 安装 mcp，用户已批）。第三批 done：21 文档对齐=af4a68b / 22 语义核心提纯=a98add1 / 23 MCP 服务器+manifest=7bfd781 / 24 端到端实弹=eecd17b（语义 MCP 服务可用，运行式见 docs/mcp-server.md）。第四批（方案 2026-09-19 用户批准）= 票 27 缺 id 盲区演进 / 28 元循环探针 meta_probe / 29 信号路由表+体检节奏。第四批收官：27=a4fb938 / 28=5c149c1 / 29 信号路由表+体检节奏=7a11d59（F14 元循环闭环）。第五批（定时任务用户预批准"拆票后按推荐方式开跑"）= 输入侧三适配器+模式件库：票 30 需求探索器 F5 / 31 代码逆向器 F7 / 32 文档萃取器 F8 / 33 模式件库，当前下一张 = 票 30。第六批候选 = 输出侧 F9/F10（方案留待用户批准）。动土前先跑收官报告 §2 两条回归底线命令。尾款票 25 done（d0be9c2，camp 裁剪 P1）/票 26 卫生清偿与流程补丁 done（ae53845）。
6. 批次纪律三件套：扩张/新批次须用户批准入账 + PRD 同步 + 批收官推锚点——推锚点/回写文档的字符串替换必须带断言验证（替换后 grep 复核预期内容在位），静默失配=事故（票 24 收官 replace 与收官报告 sed 两次同款实证，见 lessons/26）。
7. 审查报告必落盘 `docs/reviews/`，不以对话转述存活；整改票引用审查结论须引落盘路径。
8. 验收扫描面必须对得上 AC 声明面：AC 说"全仓"就查全仓含 `.py`；票面引用"本票 AC 表"必须真实存在（票 14/票 20 两次教训）。断言真源：出厂断言以票面 AC 表为正，specs/*.md 仅为一期基线+汇总指针。
9. 批收官清单（票 29 起）：① `python3 tools/meta_probe.py ontology/bohai --out docs/meta/体检-<日期>.md` 留痕（硬闸必须全绿，路由表自检在内；同名已存在则加序号后缀追加，不覆盖旧留痕）；② 锚点推进入账（带断言验证）；③ 本批审查报告落盘 docs/reviews/（如有审查）；④ 豁免复核结论更新 docs/meta/exemption-reviews.json。探针硬闸红灯=下批首票。

## 使用方式（建成后）

工作流各功能 = 用户级 skill（需求探索/本体建模/逆向/生成/治理），Kimi Code 按触发面自动路由；闸与工具在 `tools/`，CI 即四闸。
