# Step 7 · MCP 端到端实弹走查（票 24）

> 走查对象：`tools/semantic_mcp_server.py`（票 23 发布面，四工具）× 官方 mcp SDK 客户端实调（`tools/mcp_smoke_client.py`，本票新落）。
> 行为真源：`fixtures/mcp-publisher/cases/mcp-tool-contract-usecases.md`（U1–U8 对照单）= `fixtures/semantic-service/assertions.json` CORE-01/03/04/05（同源八问）。
> 纪律：本记录所有输出均为真实命令的真实输出（smoke client 逐调用打印，`--full` 全文留证；不表演）。
> 红线核对：`tools/semantic_mcp_server.py` **零改动**（实弹未暴露 server 胶水不符，探针+实调直接过）；ontology/、skills/、既有 tools/ 零改动。

## 一、环境（真实版本）

| 项 | 值 | 来源 |
|---|---|---|
| mcp SDK | **2.2.0**（`pip show mcp` 实录；与 tech-selection §3 预言版本一致） | `.venv-mcp/bin/pip show mcp` |
| venv Python | **3.11.15**（`.venv-mcp`，另装 PyYAML 6.0.3 供 server 子进程链用） | `.venv-mcp/bin/python --version` |
| 系统解释器（CI 面） | 3.14.7（homebrew，无 mcp——`import mcp` = ModuleNotFoundError） | `python3 --version` |
| MCP 协议版本 | 2025-11-25（`session.initialize()` 实回 `protocol_version`） | smoke client `[init]` 行 |
| server API 面 | `v2 mcp.server.MCPServer`（起服 stderr 自报；盲写面与 2.2.0 实际 API 完全吻合） | 起服 stderr |

**venv 解释器偏差（实弹环境事故，记档）**：`python3 -m venv .venv-mcp`（homebrew 3.14.7）在 ensurepip 步骤崩——该机 homebrew Python 的 `pyexpat` dlopen 断链（符号 `_XML_SetAllocTrackerActivationThreshold` 不在系统 `/usr/lib/libexpat.1.dylib`）→ `import plistlib` 失败 → `platform.mac_ver()` 返回空串 → pip 内置 truststore 模块级 `int('')` 崩溃。homebrew python@3.10 同病；`/usr/bin/python3`（3.9.6）低于 SDK 要求。处置：改用用户本地健康解释器 `/Users/divh/.local/bin/python3.11`（3.11.15，plistlib/mac_ver 实测正常）建同一个仓内 `.venv-mcp`——隔离不变，不触「装系统/换源/--user」三禁。系统 3.14 的 pyexpat 断链不影响 CI（四闸不用 plistlib/pyexpat，收工 ci.sh 全绿实证）。

## 二、起服方式（真实命令）

smoke client 以 SDK `StdioServerParameters` 把 server 当 stdio 子进程拉起（客户端与 server 均用 `.venv-mcp/bin/python`）：

```bash
.venv-mcp/bin/python tools/mcp_smoke_client.py --full        # 实调+全文留证，exit 0
# 等价起服形态（server 侧被拉起的是）：
#   .venv-mcp/bin/python tools/semantic_mcp_server.py ontology/bohai
```

起服 stderr 实录：`all-agent-semantic MCP 服务器就绪：ontology=ontology/bohai API=v2 mcp.server.MCPServer 工具=4（stdio；HTTP 形态见 docs/mcp-server.md）`。

CI 免疫红线复核（裸环境、系统 python3，无 mcp）：`python3 tools/semantic_mcp_server.py ontology/bohai` → stderr 打安装指引（`pip install mcp`…），**exit 2**。smoke client 同纪律：无 SDK 时 exit 2 指引建 venv（BootstrapTest 强制标志实测 + 裸环境 unittest 2 skip 实证）。

## 三、实弹调用记录（每调用一行；输出=`.venv-mcp/bin/python tools/mcp_smoke_client.py --full` 真实录）

前置两行（协议握手与工具清单，均 PASS）：`[init] server=all-agent-semantic protocol=2025-11-25`；`[tools] ['semantic_ask','semantic_closure','semantic_impact','semantic_query']`。

| # | 工具 | 入参 | 结果摘要（真实输出） | 断言 |
|---|---|---|---|---|
| U1 | semantic_ask | `{"question": "日产量口径是什么？"}` | 【裁决】answered（二级·ID/名称解析）；命中 5 候选（BH-BOHAI-QueryWellDailyOutput/QR-BOHAI-001/AGG-BOHAI-002/RULE-BOHAI-004/RULE-BOHAI-003）+「命中多个候选」注；引用清单 22 个 ID（含 AGG-BOHAI-002、RULE-BOHAI-002）；1285 字符 | PASS（7 检查全过） |
| U2 | semantic_ask | `{"question": "桶油增产成本的口径是什么？"}` | 【裁决】refused_missing（四级·可拒答）；缺件三层全「未建（仓内无承载，待 Owner 提案补建）」+提案流程指路；「近邻指路：无（无字面交集，不硬凑）」；引用清单节在场且如实注「无可引用元素」；493 字符 | PASS（6 检查全过；id_token 按缺件态设计不设） |
| U3 | semantic_ask | `{"question": "老完成率还能用吗？"}` | 【裁决】refused_banned；【禁用词】老完成率（GLS-BOHAI-001，禁用（替代：产量完成率））；替代口径真实 ID 指路 RULE-BOHAI-009 / BH-BOHAI-QueryBlockMonthlyCompletion / QR-BOHAI-002；引用清单 4 个 ID；501 字符 | PASS（8 检查全过） |
| U4 | semantic_ask | `{"question": "@SCR-BOHAI-01 的界面细节"}` | 【裁决】refused_out_of_surface（一级·显式锚定（检索面外））；【锚定】@SCR-BOHAI-01；camp=build-contract；「不返回该元素任何细节」；241 字符 | PASS（13 检查全过，含 7 个 MU 细节 token 全未泄：MENU-/gridDaily/screenType/GRID/日产量列表/单井日产量录入/产量管理） |
| U5 | semantic_query | `{"element_id": "AGG-BOHAI-001"}` | 【节点】AGG-BOHAI-001 (M1) 域=bohai 位置=m1-object-model.yaml:21；【属性】name=井；alias=Well；【图统计】节点=79 边=118 | PASS（6 检查全过） |
| U6 | semantic_query | `{"element_id": "AGG-BOHAI-999"}` | 【查询】AGG-BOHAI-999 未找到；【说明】未找到: AGG-BOHAI-999（图内共 79 节点；不做名称猜测） | PASS（4 检查全过） |
| U7 | semantic_closure | `{"element_id": "GLS-BOHAI-002", "hops": 1}` | 【闭包 --closure】2 个下游节点：AGG-BOHAI-001 hops=1 via=relatedObjectRefs、AGG-BOHAI-002 hops=1 via=relatedObjectRefs | PASS（7 检查全过） |
| U8 | semantic_impact | `{"element_id": "AGG-BOHAI-001"}` | 【影响 --impact】56 个受影响节点（依赖方）：hops=1 直挂（AGG-002…009/ASSOC×7/BH-BOHAI-QueryWellDailyOutput/FLOW/GLS/QR）至 hops=5（ACTOR），7 个 BH-BOHAI-* 全在集内 | PASS（5 检查全过） |
| U9 | semantic_closure | `{"element_id": "AGG-BOHAI-001", "hops": 2}` | 【节点】AGG-BOHAI-001 简报 + 【闭包 --closure】**0 个下游节点**（真实图形态：AGG-BOHAI-001 只被引用、无正向引用，见 §六-1）；118 字符 | PASS（4 检查全过，断言钉诚实空报告） |

**合计：9/9 用例过，exit 0**（`mcp 2.2.0 / Python 3.11.15`）。全文证据由 `--full` 输出承载（本次走查留证于施工窗口；任何人可按 §二命令复现逐字节同构的输出——server/client 均确定性，无时间戳无随机面）。

## 四、与出厂集行为对照表（AC2 核对）

| 对照单 | 出厂集断言（真源） | MCP 实调结果 | 一致 |
|---|---|---|---|
| U1 日产量 | CORE-01：answered + AGG-BOHAI-002 + RULE-BOHAI-002（ambiguous 列候选合法） | answered；AGG-BOHAI-002 ∈ hits；RULE-BOHAI-002 ∈ 引用清单（22 ID）；「命中多个候选」注在场 | ✓ |
| U2 桶油成本 | CORE-03：refused_missing + 未建 + 待 Owner；cases：提案流程指路、不硬凑近邻 | refused_missing；三层未建+待 Owner 提案补建；提案流程；「无（无字面交集，不硬凑）」 | ✓ |
| U3 老完成率 | CORE-05：refused_banned + GLS-BOHAI-001 + RULE-BOHAI-009 + QR-BOHAI-002 | 四者全在场 + 替代口径「产量完成率」 | ✓ |
| U4 @SCR-BOHAI-01 | CORE-04：refused_out_of_surface + camp=build-contract；fixture AC4：不泄 MU 细节 | refused_out_of_surface + camp=build-contract；7 个 MU token 全未出现 | ✓ |
| U5 query 命中 | cases U5：ID/model=M1/域=bohai/文件位置 | 节点简报四要素齐 | ✓ |
| U6 query 未找到 | cases U6 + 出厂集「未找到不猜」机读佐证 | 未找到 + 不做名称猜测 | ✓ |
| U7 closure GLS-002 hops1 | cases U7 + 票 17 机读佐证：relatedObjectRefs → AGG-001/002 | 2 节点 via=relatedObjectRefs | ✓ |
| U8 impact AGG-001 | cases U8：56 节点、含 BH-BOHAI-* | 【影响 --impact】56 个受影响节点；7 个 BH 全在 | ✓ |
| 直连基线（同日实测） | core CLI U1–U4 退出码 0/1/1/1（拒答=有效裁决） | 经 MCP 全部 is_error=False（协议层无错，裁决在文本内）——两层语义各归其位 | ✓ |

## 五、单测与 CI 面（AC4 核对）

- `tools/test_mcp_smoke_client.py`（新）：20 测=用例表结构 9 + 断言评估纯函数 6 + 免疫引导 3 + 协议面 2（skipUnless）。
- venv 实跑（`.venv-mcp/bin/python -m unittest tools.test_mcp_smoke_client`）：**20/20 OK**（协议面 2 测真起 server 实调）。
- 裸环境实跑（`python3 -m unittest tools.test_mcp_smoke_client`）：**18 ran + 2 skipped，OK**；`import mcp` = ModuleNotFoundError 实证 CI 无 SDK。
- 收工回归：`bash tools/ci.sh` 四闸全绿（系统 python3，未装 mcp——CI 免疫红线守住，见 lessons/24 验收节）。

## 六、发现的问题清单（含处置）

1. **交接包 closure 期望与真实图形态不符（防踩坑笔误，非工具 bug）**：防踩坑 4 预期「closure(AGG-BOHAI-001, hops=2) 返回含命中 ID」，实际该节点无任何正向 ref（只被 56 个节点反向依赖）→ 闭包恒空。处置：U9 断言钉「【闭包 --closure】0 个下游节点」的诚实报告（拒答/空集不硬凑与服务纪律同源）；闭包内容断言落在对照单 U7（GLS-BOHAI-002 hops=1）。**server/core 零改动**。
2. **venv 解释器事故（§一详述）**：homebrew Python 3.14/3.10 的 pyexpat dlopen 断链导致 ensurepip 不可用。处置：换用户本地健康 python3.11 建同一 `.venv-mcp`；偏差已回报主窗口并记 lessons/24。对 CI 零影响（ci.sh 全绿实证）。
3. **客户端 API 首写笔误（smoke client 自身，非 server）**：`InitializeResult` 字段实为 snake_case（`server_info`/`protocol_version`，实测 2.2.0），首写 camelCase（`serverInfo`）取空 → init 探针误 FAIL。处置：修客户端一处取值后过；顺手修合计行在「未进入用例」时的误导输出。**server 零修改**（票 23 预留的「build_server 小修」最终没用上）。
4. **无其他问题**：四工具契约、拒答三分支、ID 引用清单、未找到不猜、只读边界全部与出厂集行为一致；manifest 描述真源链（起服装载入库 manifest）无漂移报注。

## 七、AC 实证（真源=tickets/24 AC 表）

- [x] **AC1**：smoke client 全量实调，四工具各≥1 次成功（ask×4/query×2/closure×2/impact×1），退出 0（§三 合计行）
- [x] **AC2**：ask 三形态+禁用词例 status/ID 与出厂集一致（§四 对照表 8/8 ✓）
- [x] **AC3**：全部回答带 ID 引用——ask 必带「本回答引用的元素 ID」清单节（U1–U4 实录在场）；其余态 BOHAI ID token 可 grep（U1=32/U3=11/U4=2/U5=1/U6=2/U7=3/U8=57/U9=1 个；客户端内置断言非人眼）
- [x] **AC4**：`bash tools/ci.sh` 四闸绿（系统 python3，无 mcp）；`git status` 无 .venv（.gitignore 增 `.venv*/` 挡住）；裸环境单测协议面 2 skip、18 过
