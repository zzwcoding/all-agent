# 施工日志 23 · MCP stdio 服务器与发布物

日期: 2026-09-19
角色: L2 编码（自主档）
票: tickets/23-MCP-stdio服务器与发布物.md（AC 真源=票面 AC 表；CI 免疫红线/四工具契约/确定性零时间戳/派生物纪律=设计裁决 L0，照办）
交接包注记: 主窗口防踩坑清单（无 mcp 免疫、生成器确定性核心、exports 登记、fixtures 推荐落法 --check、server 细节含 ID token、docs 结构、modules 两行、边界照票面）逐条照办，下文留证。

## 做了什么

1. **TDD 红先绿后**：`test_mcp_manifest_gen.py` 21 测先行（红相=模块缺失收集即红），实现生成器后绿；`test_semantic_mcp_server.py` 21 测先行（协议面 1 测 `skipUnless(_HAS_MCP)` 占位，CI 无 SDK 天然跳过），实现 server 后绿。全仓 `unittest discover` 296 = 既有 254 + 新 42，零倒。
2. **生成器 `tools/mcp_manifest_gen.py`**（stdlib 零第三方，只读 JSON 不碰 YAML）：域发现（扫 `*/manifest.json`，graph_index.discover_domains 同一手法的第三个读者）+ 每域 profile/camp 概览（读 model-registry.json，按域 profile 圈定模型面、omittedModels 剔除，逐模型 name/modelType/camp）+ 四工具契约模板 `TOOL_CONTRACTS`（name/description/inputSchema 简体中手写为常量=描述真源）。三模式：缺省 stdout / `--out` 写文件（stdout 安静）/ `--check` 与入库副本逐字节比对（0 一致 / 1 不一致或缺副本 / 2 配置错误）。**零时间戳**：无日期键无日期形态 token（单测正则断言）；确定性=注册表序+域名字典序+固定模板，同本体仓重生成字节一致。
3. **发布物入库**：`exports/mcp/capability-manifest.json` 生成落盘（bohai：profile=v9-full，模型面 7 个=全 business-core，MU 按 omittedModels 剔除且 reason 照登；四工具契约全文）。`--check` exit 0 实证。
4. **server `tools/semantic_mcp_server.py`**：CI 免疫红线落地——SDK import 双层 try/except 收敛为 `_HAS_MCP`/`_MCP_API`，缺 SDK 时**引导路径先于参数校验**（裸起也是同一出口）打安装指引（含 `pip install mcp`/venv/文档指路）exit 2。四工具：ask→票 22 core 子进程 `--json`（0/1 都解析成裁决文本，2=配置错误文本）；query/closure/impact→graph_index 子进程 `--json`（1 未找到=有效结论文本）。回答骨架必含「本回答引用的元素 ID」清单节——answered 态列 citations，拒答态列禁用词条目/替代口径/近邻真实 ID，面外态不泄细节仅锚定 ID 可 grep（纪律不破、票 24 grep 面不空）。描述真源链：TOOL_CONTRACTS import 同源 → 起服装载入库 manifest **逐项核对（name+description+inputSchema 三元组）** → 漂移/缺失回退模板并 stderr 报注。
5. **出厂集 `fixtures/mcp-publisher/`**：按交接包推荐落法，AC1+AC2 合并为一条 `--check` cmd-succeeds（再制一致）；AC3=生成到 stdout 的 outputContains 钉四工具 JSON 键值串+`"domain": "bohai"`+inputSchema；AC4=cmd-fails 起 server（钉 `pip install mcp`）；再补 docs 存在性=cmd-succeeds + `python3 -c` 探针。cases/ 落四工具行为一致性用例单 U1–U8（与 fixtures/semantic-service CORE 八问同源，票 24 smoke client 内置断言的对照真源）。
6. **两表一步到位登记**（照 adr README 事件教训）：repo-layout.json 增 exports/ 条目（patterns `["mcp/*.json","mcp/*.md"]`，purpose 写明派生物禁手改）；archive-registry.json 增 `mcp-manifest` 产物类（requiredFields 五键、status 契约 `已生成`）。归档闸实跑一次全绿（378 文件），零返工。
7. **消费文档 docs/mcp-server.md**：定位/前提（3.10+、pip install mcp、venv）/运行（stdio 说明+HTTP 改一行注记照 R3=tech-selection §3 `mcp.run(transport="http", …)`）/四工具契约表/与 semantic-service skill 关系（同判定核心两种成稿形态）。modules.md 脚本清单增两行（生成器+server，含免疫红线与 API 面注记）。
8. **边界**：只动 Touches 清单内文件；票 22 core 零改动（未发现 bug）；skills/、ontology/、schema/ 零改动；不 commit。

## 取舍（口径账）

- **AC1/AC2 载体=生成器内建 `--check`（对防踩坑 4 字面的偏差，记偏差账）**：fixture cmd 断言无 shell 算子（fixture_run 用 shlex.split，`&&` 不解析）、不落 /tmp，file-equals-golden 的 golden 又限定在出厂集目录内——三条路都堵时，交接包推荐的 `--check` 模式是最干净载体：入库副本 vs 现场重生成逐字节比对=跨运行字节一致的门口实证（幂等）；连跑两次字节一致另由生成器单测 DeterminismTest 承载。AC1+AC2 在 assertions.json 里标注为一条断言的两组来源，AC 映射全文写进 description。
- **API 面选型（票 24 允许小修的预留）**：不查网，以仓内一手调研 R3·tech-selection §3 为准——官方 SDK v2 `from mcp.server import MCPServer`（2.x 起 FastMCP 更名）；同时留 v1 `mcp.server.fastmcp.FastMCP` 兼容回退（两线共用 `@server.tool(description=...)` 与 `.run()` 缺省 stdio，回退零额外分支）。**未实弹验证**：`description=` kwarg 若实际版本不符，票 24 小修 build_server 即可，出厂集不受影响（CI 不跑协议面）。
- **manifest 增 `status: "已生成"` 键（L0 四键之外的显式偏差）**：交接包点 3 建议登记产物类给状态合法值——照办进模板；且查明 `check_json_artifact` 当前只查必备顶层键不查状态值，status 契约属前置登记（闸后续增强时零返工），statusNote 里写明。此键确定性非时间戳，不破幂等。
- **描述真源的双重实现**：票面说「工具 description 从 capability manifest 取」，防踩坑 5 说「从生成器 import 模板常量」——落地为一条链：模板常量（真源）→ 生成 manifest → server 装载入库 manifest 并**三元组逐项核对** → 通过则用 manifest 的描述（字面满足票面），失败回退模板常量（字面满足防踩坑 5）并 stderr 报注。核对本身是防陈旧哨兵：入库 manifest 陈旧时起服即报。
- **server 单测面超出 L0 两面清单一点（记偏差账）**：除引导路径+manifest 装载外，加测了回答骨架组装纯函数与真域子进程链路（ask answered/refused、query 未找到、impact、hops 用法错误）。理由：协议面才是 L0 意义上的「留票 24 实弹」——SDK 拉起与协议对话；文本组装与子进程包装是无 SDK 的确定性面，不测则票 24 AC3（ID token 可 grep）裸奔。全绿红线要求下这是最小充分集。
- **docs 存在性断言不越界**：file-* 断言路径约定相对出厂集目录，`../../docs/...` 机械上可行但越权；改用 cmd-succeeds + `python3 -c` 探针（cwd=仓根是 cmd-* 的既定契约），语义等价且不破沙箱。
- **INSTALL_HINT 先于 argparse**：无 SDK 时裸起 server（无参数）也走同一免疫出口（argparse 用法错误会让「未装 SDK」信号被「缺参数」掩盖）；引导路径因此与参数形态无关，AC4 断言稳定。

## 坑

- **`check_json_artifact` 不查状态值**：archive_check 对 json 类只查 requiredFields（status 检查在 check_md_artifact 里）——给 mcp-manifest 类配 status 契约时别指望闸真的拦「已废弃」之类的值；要改状态语义得先增强闸。
- **fixture cmd 不是 shell**：多命令编排（gen 两连发+cmp）写不进一条 cmd-succeeds（shlex.split 把 `&&` 当普通 token，子进程直接找不到命令）；凡是「比 A 与 B」类断言要么生成器内建（--check），要么单测承载。
- **自己的测试帮手踩了自己**：CliModesTest.setUp 已建过合成根，坏 profile 用例再调 make_root 同一路径 → FileExistsError；合成根构造器加层级（`tmp/"second"`）绕开，与语义闸合成域的「schema 探测半径」教训同族——合成夹具先想清谁建过什么。
- **真环境免疫测试有噪声**：`test_real_environment_bootstrap` 直跑 main 会把安装指引打进测试 stderr（CI -v 输出可见）——断言照旧有效，属可接受噪声；若嫌吵可在测试内 redirect。

## 验收（对照票面 AC 表，逐条实证）

- [x] AC1（幂等）：单测 DeterminismTest 两轮实跑字节一致（stdout 与 --out 双路）+ 零时间戳正则断言；AC1+AC2 断言（--check）ok（源：AC 表 AC1）
- [x] AC2（防陈旧）：`python3 tools/mcp_manifest_gen.py ontology --check exports/mcp/capability-manifest.json` exit 0「再制一致」；篡改探针单测（改 server.name）exit 1（源：AC 表 AC2）
- [x] AC3（内容）：fixture 断言钉四工具名+`"domain": "bohai"`+inputSchema 全 ok；json.loads/inputSchema 结构面由 ContentContractTest 承载（21/21 绿）（源：AC 表 AC3）
- [x] AC4（无 mcp 引导）：fixture cmd-fails 起 server exit 2 + outputContains `pip install mcp` ok；单测 BootstrapTest 强制 `_HAS_MCP=False` 三态（带参/裸起/真环境）全绿（源：AC 表 AC4）
- [x] AC5（CI 免疫实证）：本机无 mcp（`import mcp` = ModuleNotFoundError），`bash tools/ci.sh` 四闸全绿——单测 296（1 skip=协议面占位）、出厂集 8/8、边界闸、归档闸零红（源：AC 表 AC5 + 票面验收三条）
- [x] 布局表/登记表登记完整、归档闸绿：exports/ 两表一步到位，`python3 tools/archive_check.py` 378 文件零违规（源：主线 2）

## 交接给票 24 的接口备忘

- server 路径 `tools/semantic_mcp_server.py`，启动式 `python3 tools/semantic_mcp_server.py ontology/bohai`（显式传，无默认）；smoke client 用 `.venv-mcp/bin/python` 拉起。
- 四工具名与入参：`semantic_ask(question)` / `semantic_query(element_id)` / `semantic_closure(element_id, hops=3)` / `semantic_impact(element_id)`——inputSchema 与 cases/ U1–U8 一致。
- ID token grep 面：「本回答引用的元素 ID」清单节（ask）/命中与影响行内 ID（query/closure/impact）。
- 若 SDK 实际 API 与 v2 `MCPServer`/`description=` kwarg 不符：小修 `build_server()` 一处即可，描述真源链与四工具包装不动；出厂集与 CI 不受影响。
