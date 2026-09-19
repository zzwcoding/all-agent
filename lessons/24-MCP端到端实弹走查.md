# 施工日志 24 · MCP 端到端实弹走查

日期: 2026-09-19
角色: L2 编码（自主档）
票: tickets/24-MCP端到端实弹走查.md（AC 真源=票面 AC 表；venv 方案/smoke 客户端/行为一致性核对单/走查记录=设计裁决 L0，照办）
交接包注记: 主窗口防踩坑清单（venv 纪律/.gitignore/API 对齐/smoke 客户端/走查记录/单测面/红线/自查）逐条照办，其中两处真实世界偏差（venv 解释器、closure 期望形态）见下文，均已留证。

## 做了什么

1. **venv + SDK（防踩坑 1）**：`pip show mcp` 实录 **Version: 2.2.0**（与 R3·tech-selection §3 预言的 2026-09-07 版本号一致）；venv Python 3.11.15，另装 PyYAML 6.0.3（server 的 core/graph_index 子进程要用——venv 默认不继承 site-packages，防踩坑 4「统一 venv 最省事」的字面落地）。venv 建立事故与处置见「坑」1。
2. **.gitignore（防踩坑 2）**：读现有风格（注释头+逐条）后追加注释行+`.venv*/`；`git status` 实证不出现 .venv-mcp。
3. **API 探针（防踩坑 3）**：装完即探——`mcp.server` 成员含 `MCPServer`；`MCPServer.__init__` 首位 name、`tool(description=...)`、`run(transport='stdio' 缺省)` 与票 23 盲写的 v2 面**逐项吻合**；客户端面 `StdioServerParameters(command/args/env/cwd)`、`ClientSession.initialize/list_tools/call_tool` 齐。最小探针（起服+list_tools+实调 ask）一次过 → **server 零修改**（票 23 预留的 build_server 小修没用上，lessons/23 的选型账闭环）。
4. **直连基线先行**：写客户端前先把六问的 core/graph_index 直连输出跑一遍（U1 citations 22 项含 RULE-BOHAI-002、U2 缺件三层文本、U3 citations 4 项、U4 reason 全文、U6 未找到措辞、U7 闭包 2 节点、U8 影响集 56、U9 空闭包），期望值逐字抄自这些真实输出 + 出厂集 CORE 断言，不凭记忆写断言。
5. **smoke 客户端 `tools/mcp_smoke_client.py`**：用例表 U1–U9（U1–U8=fixtures/mcp-publisher/cases 对照单逐条 + U9=交接包指定 closure(AGG-BOHAI-001,hops=2)）；每用例内置 expect_contains/expect_not_contains/citation_header/id_token 断言 + is_error 检查；协议握手断言 server 名与工具清单；`--full` 打全文（走查留证）、`--list` 免 SDK；退出码 0/1/2（2=无 SDK 指引建 venv，与 server 同纪律）。ID token 正则 `\b[A-Z]{2,}[A-Z0-9]*-BOHAI-…` 可 grep 全部 bohai ID 形态。
6. **实弹 9/9 全过 exit 0**：协议版本 2025-11-25；四工具往返 is_error=False；拒答三分支（refused_missing/banned/out_of_surface）在协议文本内完整继承（含缺件三层、禁用词替代指路、MU 细节 7 token 全未泄）；AC3 面实证（ask 引用清单节全在场；各回答 BOHAI ID 计数 32/11/2/1/2/3/57/1）。
7. **单测 `tools/test_mcp_smoke_client.py` 20 测**：用例表结构 9 + 断言评估纯函数 6 + 免疫引导 3（强制 _HAS_MCP=False 实测 exit 2+指引）+ 协议面 2（skipUnless）。venv 实跑 20/20（协议面真起 server）；裸系统 python3 实跑 18 ran+2 skipped OK（`import mcp`=ModuleNotFoundError 实证 CI 无 SDK）。
8. **走查记录 `docs/walkthrough/step7-mcp-e2e.md`**：环境/起服式/每调用一行/出厂集对照表 8/8/问题清单四条/AC 实证——全部来自真实输出。
9. **边界**：改动面=.gitignore + tools/mcp_smoke_client.py（新）+ tools/test_mcp_smoke_client.py（新）+ docs/walkthrough/step7-mcp-e2e.md（新）+ lessons/24；ontology/、skills/、既有 tools/ 零改动（server 也在零改动之列）；venv 为执行面不入库；不 commit。

## 取舍（口径账）

- **venv 解释器换健康者（对防踩坑 1 字面的偏差，已按「立即回报」精神处置）**：见「坑」1。判定要点：防踩坑禁的是「装系统/换源/pip --user」三种污染面，不是「解释器从哪来」；换 `/Users/divh/.local/bin/python3.11` 建同一个仓内 `.venv-mcp`，隔离性质不变。若当时停手等裁决也可以，但根因清晰、处置在授权面内，选择继续并双通道记录（走查记录 §一 + 本篇）。
- **U9 期望钉「空闭包」而非「含命中 ID」（对交接包字面的偏差）**：AGG-BOHAI-001 无正向 ref 是图的真形态（直连 `--closure 2` 实证 0 节点）；按交接包字面写「含命中 ID」断言必红，按「实弹=以真实输出为准」纪律改为钉诚实空报告。这与服务自身纪律同构：可拒答/可为空、不硬凑。闭包内容断言由 U7（GLS-BOHAI-002 hops=1）承载，交接包「四工具各≥1 次成功」照样满足（closure 调了两次且都成功）。
- **ask 兼答四问而非三问**：票面核对单列「ask 三形态+禁用词例」，防踩坑 4 列 ask×3；对照单 U1–U8 含 U4（面外拒答）。U4 是拒答三分支唯一在 CORE 断言里钉了 camp 细节的一问，实弹漏它则「面外不泄」只有纸面证据——多调一发全过，成本≈0，证据面更完整。
- **AC3 的 U2 特例显式建卡**：refused_missing 且无近邻时，core 纪律是不硬凑 ID → 该回答全文无 BOHAI ID。AC3 写的是「引用清单/ID token」二选一——引用清单节在场且如实注「无可引用元素」即满足；客户端用例卡里 expect_id_token=False + 单测钉死该特例（防后人当 bug 修）。
- **协议面单测真跑而非占位**：票 23 留的 skipUnless 占位在其自身测试文件里不动（红线），本票测试文件的协议面 2 测在 venv 下真起 server 全流程实调（AC1 的单测面镜像）；CI 裸环境天然 skip，双世界各得其所。

## 坑

- **homebrew Python 的 pyexpat 系统级断链（本票最大坑）**：这台 mac 上 homebrew 3.14.7/3.10.20 的 `pyexpat*.so` dlopen 失败（符号 `_XML_SetAllocTrackerActivationThreshold` 不在系统 `/usr/lib/libexpat.1.dylib`）→ `import plistlib` ImportError → `platform.mac_ver()` 静默返空串（`_mac_ver_xml` 把 ImportError 吞成 None）→ **pip 内置 truststore 在 import 时 `int('')` 崩溃 → ensurepip 无法在任何 homebrew 解释器的 venv 里引导 pip**。诊断路径：venv 建失败 → 直接跑 inner ensurepip 看 traceback → 逐层试 `sw_vers`（好）/`platform.mac_ver()`（空）/`plistlib`（炸）→ 定位 pyexpat。教训：**「pip 失败」先分清网络/沙箱/解释器三种病因**，truststore 崩的锅常在 platform 链，不在 pip 本身。
- **pydantic v2 字段是 snake_case，协议对象取值别按 camelCase 猜**：`InitializeResult.server_info.name`/`protocol_version`——首写 `serverInfo` 取到 None，init 探针误 FAIL。取不确定的协议字段先 `model_dump()` 看一眼再写代码。
- **「空闭包」是合法回答**：impact 与 closure 方向相反（lessons/22 已记 appliedRules 之坑，本票是它的镜像——AGG-BOHAI-001 只进不出）。给上级交接包写期望值时，「某 ID 的 closure」先直连跑一下确认非空，否则断言与图形态打架。
- **早期失败的合计行会误导**：init/工具清单 FAIL 提前返回时，`0/0 用例过` 读起来像全过——补了「未进入用例实调」分支。凡是「N/M 过」式汇总，M=0 必须是另一种话术。
- **venv 里装 SDK 别忘了 PyYAML**：venv 不继承系统 site-packages，server 的子进程链（core/graph_index）import yaml 会炸在运行时而非装包时——装的时候一并 `pip install mcp pyyaml` 一次到位。

## 验收（对照票面 AC 表，逐条实证）

- [x] AC1：`.venv-mcp/bin/python tools/mcp_smoke_client.py --full` exit 0，四工具各≥1 次成功（ask×4/query×2/closure×2/impact×1），合计 9/9 用例过（源：AC 表 AC1）
- [x] AC2：客户端内置断言全过——U1=answered+AGG-BOHAI-002+RULE-BOHAI-002；U2=refused_missing+未建+待 Owner+提案流程；U3=refused_banned+GLS-BOHAI-001+RULE-BOHAI-009+QR-BOHAI-002；U4=refused_out_of_surface+camp=build-contract+MU 七 token 未泄；与出厂集 CORE 断言逐条对照 8/8 一致（源：AC 表 AC2 + 走查记录 §四）
- [x] AC3：全部回答带 ID 引用——ask 四答「本回答引用的元素 ID」清单节全在场；其余回答 BOHAI ID token 计数实证（U2 缺件态按 core 纪律不硬凑 ID、引用清单节在场，特例已建卡）（源：AC 表 AC3）
- [x] AC4：`bash tools/ci.sh` 四闸全绿（系统 python3 未装 mcp，单测协议面 2 skip）；`git status` 无 .venv；裸环境起服 exit 2+安装指引实证（源：AC 表 AC4 + 票面验收三条）
- [x] venv 不入库：.gitignore 增 `.venv*/`，git status 干净（源：票面验收「venv 不入库」）

## 交接备忘（给后续票/窗口）

- 实弹复现命令：`.venv-mcp/bin/python tools/mcp_smoke_client.py --full`（exit 0=全过）；单测双跑：venv 20/20、裸环境 18+2skip。
- venv 若要在别的 clone 重建：`/Users/divh/.local/bin/python3.11 -m venv .venv-mcp && .venv-mcp/bin/pip install mcp pyyaml`（本机 homebrew python 因 pyexpat 断链暂不可用；homebrew 修好后可换回 `python3`）。
- server 的 HTTP 形态（R3）：`mcp.run(transport="http", port=8000, path="/mcp")`——v2 2.2.0 的 run 签名实测支持 transport kwarg，本票未实弹 HTTP 档（票面只要求 stdio）。
