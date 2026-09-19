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
| `references/` | 调研落盘：omf-spec-digest（OMF 规范精读）/ existing-research-inventory（既有调研盘点）/ tech-selection（选型） |
| `diagrams/` | 三张图：all-agent（大总架构）/ skill-structure（skill 组织）/ sdd-flow2（建造流内部） |
| `specs/` `tickets/` `policies/` | 骨架已立，随阶段推进填充 |
| `ontology/` | 本体仓：schema/（七模型 schema+模型注册表+依赖白名单，票 03）；首个业务域=渤海油田产量域（bohai/manifest.json 已声明 profile，模型 YAML 票 05 起） |
| `tools/` | 已落：schema_check（语义 CI L1–L4）+ 三闸（skill_deps/fixture_run/archive_check）+ ci.sh；graph_index 票 04 |
| `fixtures/` | 出厂集：schema_check/（AC1–7 最小域+非法变体）；其余随票补 |
| `lessons/` | 施工日志：每票一篇（03 起） |

## 流水线续跑协议（一期票 04–09 已收官；二期票同协议）

新窗口接续流水线时：

1. 读 `tickets/NN-*.md` 找 Status: todo 的最小票号——交接包在票面内（自包含，不依赖旧窗口记忆）。
2. 严格串行：一派一验一提交。派发用票面交接包原文；验收 = L0 自己跑 `bash tools/ci.sh`（必须四闸全绿）+ 逐条核票面验收；过了翻 `Status: done` 再 `git commit`（一票一提交）；不过打回（附红灯输出）。
3. 同一任务连续两次不合格 → 主窗口接管自写并记原因。
4. 一期已收官：票 09 完成端到端走查与收官报告（commit 9ca5db2，报告 `docs/一期收官报告.md`，含缺口清单与二期四批建议）。
5. 当前状态锚点：一期九票全 done（9ca5db2）；二期第一批已收官（票 10 术语 GLS=0474bc8 / 票 11 一致性对=a0359e0 / 票 12 安装位同步=634dcbd），下一批 = 第二批 F13 提案池（收官报告 §7 建议二：三源信号归一+冲突检测+MR 草稿，配套渤海域 Owner 裁决队列 §6 业务面 9–13 条）；动土前先跑收官报告 §2 两条回归底线命令。

## 使用方式（建成后）

工作流各功能 = 用户级 skill（需求探索/本体建模/逆向/生成/治理），Kimi Code 按触发面自动路由；闸与工具在 `tools/`，CI 即四闸。
