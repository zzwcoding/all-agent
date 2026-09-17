# All-agent 技术选型调研 · tech-selection.md

> 调研日期：2026-09-17。约束：All-agent 是"skill+脚本"形态（无构建链、不建代码系统），核心资产是本体仓（Git+YAML）。
> 选型总纪律：**能用 Python3 标准库就不用第三方；引入第三方必须给足理由**。
> 信源均为一手来源：官方文档 / PyPI / GitHub（链接附各节末尾）。

---

## 1. YAML 解析

### 背景判断

Python 标准库**没有** YAML 解析器（stdlib 只有 `json` 和 Python 3.11+ 的只读 `tomllib`）。而本体仓承载对象/行为/规则/事件等十类模型，节点多、嵌套深、引用密，且**本体文件由人手编**——承载格式必须对人友好（注释、多行文本、列表）。

一个关键的设计前提先立住：**脚本是本体的只读消费者**。按 CONTEXT.md 的约定，前端只产 YAML 草案（人/AI 写），进仓过 MR；后端/脚本只读仓。**只要工具链不回写 YAML，注释天然就保住了**——注释活在 Git 里，解析器根本不需要保注释能力。这直接改变选型权重。

### 候选对比

| 候选 | 依赖代价 | 保注释/保顺序 | 安全 | 维护状态 | 结论 |
|---|---|---|---|---|---|
| **PyYAML** | 一个第三方包，**零传递依赖**，纯 Python 可用（libyaml C 加速可选，装不上也能跑） | ❌ 不保注释（`safe_load` 出来就是 dict/list，注释丢弃）；✅ 保插入顺序（dict 天然有序） | ✅ `yaml.safe_load()` 安全；教训：历史上 `yaml.load()` 误用致 RCE（CVE-2020-14343），5.4+ 起强制显式 Loader | ✅ 事实标准，最新 6.0.3（2025-09 发布），6.x 线维护正常 | **推荐** |
| **ruamel.yaml** | 一个第三方包 + 可选 C 扩展；0.19 系构建链变动多（setuptools-zig），安装面比 PyYAML 粗糙 | ✅✅ round-trip 模式（`YAML(typ='rt')`）保注释、保顺序、保格式，是唯一能"读-改-写不伤注释"的方案 | ✅ 默认 YAML 实例即安全加载 | ⚠️ 单人维护（Anthon van der Neut），作者公开声明 PyPI 命名不符合 PEP 625、未来上传可能受阻；发布节奏靠个人 | 备选（仅当需要程序回写 YAML） |
| 自写受限子集解析器 | 零依赖 | 理论可控 | 自己负责 | —— | **否决**。YAML 的"简单"是错觉：锚点/别名、多行块标量（`\|`/`>`）、引号转义、多文档、merge key，每个都是坑。为了省一个零传递依赖的包去自担解析器的正确性与安全责任，违背本项目的"脚本薄"纪律 |
| 改用 TOML（stdlib `tomllib`） | 零依赖 ✅ | ✅ 支持 `#` 注释；⚠️ `tomllib` **只读**（stdlib 无 TOML 写出器） | ✅ | ✅ stdlib | 否决但值得说明：本体模型是深嵌套 + 大量列表引用（节点下挂 N 条规则/行为），TOML 的 `[tables]` 语法在这种结构下极啰嗦、重复表头多，人手编体验明显差于 YAML |
| 改用 JSON（stdlib `json`） | 零依赖 ✅ | ❌ **不支持注释**——本体是人手编的，直接出局 | ✅ | ✅ stdlib | 否决 |

### 推荐

**引入 PyYAML（6.0.3+），全链路只用 `yaml.safe_load()`，工具链只读不写 YAML。**

### 理由

1. **第三方是被迫引入的**：stdlib 无 YAML 解析器，这是唯一的依赖缺口；PyYAML 是把缺口补上的最小代价（零传递依赖、纯 Python 回退、约 200KB 量级）。
2. **注释不靠解析器保，靠"只读"保**：本体注释由 Git + MR 流程天然保存。程序若从不回写 YAML，PyYAML"丢注释"的短板就不成立。若未来出现必须程序改写 YAML 的场景（如批量 codemod 迁移），再局部引入 ruamel.yaml round-trip 模式——预留为备选而非默认。
3. **安全纪律随选型一并定死**：仓库级约定只允许 `yaml.safe_load`，禁止裸 `yaml.load`（前者永不执行任意标签，后者是 CVE-2020-14343 一类 RCE 的根源）。
4. **相对 TOML/JSON 的取舍落在"人手编体验"**：本体深层嵌套 + 引用列表，YAML 的可读性优势是实质性的；这值得一个零传递依赖的包。

### 信源

- PyYAML（PyPI，6.0.3，2025-09-25）：https://pypi.org/project/PyYAML/
- PyYAML 官方仓与 safe_load 文档：https://github.com/yaml/pyyaml
- ruamel.yaml（PyPI，0.19.1，2026-01 发布；PEP 625 命名风险自述见页面顶部）：https://pypi.org/project/ruamel.yaml/
- ruamel.yaml 文档（round-trip 模式）：https://yaml.dev/doc/ruamel.yaml
- tomllib（stdlib，3.11+，只读）：https://docs.python.org/3/library/tomllib.html
- PyYAML 不安全加载的历史教训（CVE-2020-14343 被下游复发的案例）：https://www.wiz.io/vulnerability-database/cve/cve-2026-24009

---

## 2. 图索引形态

### 背景判断

本体 YAML 要构建成图谱索引供 Agent 检索（多跳遍历、按 ID 解析引用闭包）。规模：**单域数百到数千节点**——这个数字先看清：数千节点的邻接表在内存里是几 MB 量级，BFS 遍历是毫秒级。**这个规模远够不着任何"图数据库"的立项门槛。**

### 候选对比

| 候选 | 零依赖程度 | 查询能力 | 持久化与重建成本 | 与"Git 是真源/图是派生物"的契合 | 结论 |
|---|---|---|---|---|---|
| **纯 Python 内存图**（dict 邻接表 + id→节点索引，启动时从 YAML 重建） | ✅✅ 零依赖（纯 stdlib） | 自写 BFS/DFS/闭包——多跳遍历与引用闭包恰恰是最简单的图算法，数十行 | 无持久化：启动重建，秒级以内；**无索引状态可漂移** | ✅✅ 图是每次启动从真源重新推导的纯派生物，最彻底 | **推荐** |
| **SQLite 邻接表**（stdlib `sqlite3`） | ✅✅ 零依赖 | 递归 CTE（`WITH RECURSIVE`）可做闭包/多跳；按 ID 查询有索引 | 文件级持久化；重建 = 删文件重灌 | ✅ 但引入一份持久化派生物，需要缓存失效纪律（本体仓 commit 后要重灌） | 推荐（可选件，见下） |
| **networkx**（3.6.1，2025-12 发布） | ❌ 第三方；核心纯 Python，但默认 extras 拉 numpy/scipy/pandas/matplotlib | 最强（内置最短路、社区发现等成套算法） | 无持久化，同样内存重建 | ✅ | 否决：为"多跳遍历 + 闭包"引入成套图算法库是高射炮打蚊子；本项目的检索需求用不到其算法面 |
| **Kuzu**（嵌入式图库，最后版本 0.11.3） | ❌ 第三方，C++ 原生二进制，引入构建链/平台 wheel 依赖 | openCypher，很强 | 嵌入式文件库 | ✅ 形态上契合 | **否决（一票否决级）**：Kùzu Inc. 已于 2025-10-10 **归档仓库、停止维护**（团队被 Apple 收编），官网下线，只剩社区 fork（LadybugDB/Bighorn）接盘。给 All-agent 选一个死上游的图库，直接违背"无构建链"约束 |
| **Neo4j** | ❌❌ 需独立服务进程 + JVM，最重 | Cypher，最强 | 服务端持久化 | ❌ 派生物变成"必须养的服务" | 否决 |

### 推荐

**主推：纯 Python 内存图（stdlib）——启动时从 YAML 重建 `id → node` 索引 + `id → set(邻接 id)` 邻接表，多跳与闭包自写 BFS。**
**可选件：当出现"跨脚本多次加载、重建耗时可感"的实证需要时，加一层 stdlib `sqlite3` 邻接表缓存（递归 CTE 做闭包），缓存文件登记为可重建派生物、禁手改。**

### 理由

1. **规模判决**：数千节点用内存图是毫秒级，任何持久化图库在此规模下只贡献复杂度不贡献性能。
2. **契合派生物纪律**：CONTEXT.md 已定义图谱索引为派生物、可从本体仓重建、禁手改。内存图把这条纪律执行到极致——**没有索引状态，就没有索引漂移**；SQLite 缓存是次优解（多一份需要失效管理的派生物），只在重建成本被实测证明可感时才引入。
3. **零依赖目标达成**：主推方案不含任何第三方，与第 1 节仅有的 PyYAML 并存后，整个运行时依赖面 = PyYAML 一个。
4. **排除项的证据链**：Kuzu 上游已死（归档实锤），Neo4j 违背 skill+脚本形态，networkx 的算法面用不上——三者都有明确否决理由，不是拍脑袋。

### 信源

- sqlite3（stdlib）与 `WITH RECURSIVE`：https://docs.python.org/3/library/sqlite3.html 、https://www.sqlite.org/lang_with.html
- Kuzu 归档事件（The Register 报道，2025-10-14）：https://www.theregister.com/software/2025/10/14/kuzudb-graph-database-abandoned-community-mulls-options/1142229
- Kuzu 归档公告佐证（ArcadeDB 对比文，"Status: archived, v0.11.3 October 2025"）：https://arcadedb.com/blog/open-source-knowledge-graph-graphrag-databases-compared/
- Kuzu 生态后续（社区 fork LadybugDB）：https://gdb-engines.com/db/ladybugdb/
- networkx（PyPI，3.6.1）：https://pypi.org/project/networkx/
- Neo4j 部署形态（需服务端）：https://neo4j.com/docs/operations-manual/current/

---

## 3. MCP 发布形态

### 当前状态（一手调研）

- 官方 SDK = **modelcontextprotocol/python-sdk**，PyPI 包名 `mcp`。当前稳定线是 **v2**（支持 2026-07-28 版 MCP 规范及全部更早版本）；**v2 已把 `FastMCP` 更名为 `MCPServer`**，`pip install mcp` 装到的就是 2.x（当前 2.2.0，2026-09-07 发布）。v1.x 在 `v1.x` 分支继续收关键修复，文档另址。
- 要求 Python 3.10+。最小 server 约 15 行：`MCPServer("名")` + `@mcp.tool()` 装饰普通类型注解函数，函数签名自动变 JSON Schema，无手写协议代码。
- 传输：**stdio**（`mcp.run()` 默认，本地子进程形态）与 **Streamable HTTP**（`mcp.run(transport="http", ...)`，网络部署形态，v2 中 transport 参数从构造函数移到 `run()`）都支持。
- 依赖体积：**不算轻**。2.2.0 的依赖含 pydantic>=2.12、anyio、httpx2、jsonschema、starlette、sse-starlette、opentelemetry-api、pyjwt[crypto]、python-multipart、mcp-types——但全部是 pip 可装的纯轮子（pydantic-core 有预编译 wheel），**不需要构建链**，装一次即用。

### 最小骨架（stdio，v2 语法）

```python
# server.py —— 本体仓 tools/mcp_server.py 的骨架
from mcp.server import MCPServer

mcp = MCPServer("all-agent-ontology")

@mcp.tool()
def resolve_closure(node_id: str, hops: int = 3) -> dict:
    """按 ID 解析引用闭包（读内存图，见第 2 节）。"""
    return graph_closure(node_id, hops)   # 调自写 stdlib 图索引

@mcp.tool()
def find_nodes(kind: str, query: str) -> list[dict]:
    """按模型类型（对象/行为/规则/...）检索节点。"""
    return graph_query(kind, query)

@mcp.resource("ontology://{node_id}")
def node(node_id: str) -> str:
    """读单个本体节点的 YAML 渲染文本。"""
    return render_node(node_id)

if __name__ == "__main__":
    mcp.run()  # 默认 stdio；Agent 平台以子进程拉起
```

发布 HTTP 形态时只改最后一行：`mcp.run(transport="http", port=8000, path="/mcp")`。开发调试用官方 Inspector：`mcp dev server.py`（需装 `mcp[cli]` extra，运行时可不必装）。

### 结论：**轻量可行**（stdio 档），HTTP 档次之，无需暂缓

| 档位 | 判断 | 依据 |
|---|---|---|
| stdio（本地子进程） | **轻量可行** | 代码 15 行级；Agent 平台把 server 当子进程拉起，零端口、零鉴权、零部署面；与"脚本形态"完全同构 |
| Streamable HTTP（平台远程消费） | 可行、代价中等 | 同一份 server 代码换个 `run()` 参数；代价是 HTTP 档要考虑鉴权与部署面（v2 有 OAuth/授权文档），依赖树不变 |
| 自研 MCP 协议（不用 SDK） | 否决 | 协议有规范版本演进（2026-07-28 大改直接引发了 SDK 2.0 重写），自研 = 永久追赶成本 |

**给足的第三方理由**：`mcp` 包是官方 SDK（MCP 协议的参考实现之一），协议演进风险由上游承担；其依赖树虽大但全部 pip 轮子、无构建链要求，且**只在发布给 Agent 平台消费时才需要安装**——本体仓的构建/CI 链路可以完全不碰它。

### 信源

- 官方 GitHub 仓（v2 说明、15 行示例、传输支持）：https://github.com/modelcontextprotocol/python-sdk
- 官方文档站（Get started / Servers / 迁移指南）：https://py.sdk.modelcontextprotocol.io/
- v1→v2 迁移指南（FastMCP→MCPServer、transport 移到 run()）：https://py.sdk.modelcontextprotocol.io/tr/migration/
- mcp 2.2.0（PyPI，2026-09-07，依赖清单见 requires_dist）：https://pypi.org/project/mcp/
- Streamable HTTP 与 stdio 取舍（部署形态对比，第三方佐证）：https://www.truefoundry.com/blog/mcp-stdio-vs-streamable-http-enterprise

---

## 总结论（三行）

1. **YAML**：引入 PyYAML 6.0.3+（唯一被迫的解析层依赖，零传递依赖），全链路 `safe_load`、脚本只读不写 YAML，注释靠 Git/MR 保；ruamel.yaml 留作"程序需回写 YAML"时的备选。
2. **图索引**：纯 Python stdlib 内存图（dict 邻接表 + 启动重建），多跳/闭包自写 BFS；`sqlite3` 邻接表缓存留作实测需要的可选派生物。Kuzu（上游已归档）、Neo4j（需服务）、networkx（算法冗余）均否决。
3. **MCP**：官方 `mcp` SDK v2（`MCPServer`），**轻量可行**——stdio 为默认发布形态（15 行骨架），HTTP 档仅换 `run()` 参数；依赖树偏重但无构建链要求，且只装在发布侧。
