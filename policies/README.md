# policies/ · 策略数据说明（人读一页）

> 本目录 = L4 策略数据（门禁规则、机读策略；归档布局表 `references/repo-layout.json` policies 条目登记）。
> **机读真源是 JSON，本页只做人读说明；两处不一致以 JSON 为准并修本页。**

## signal-routing.json · 信号路由表（票 29）

**用途**：元循环的核心纪律（CONTEXT.md「信号路由表」词条）——探针/审查/交互发现的问题信号，按出错层次分三类走各自的修复道；本表是三类路由的唯一机读登记处，`tools/meta_probe.py` 第 10 项（硬闸）逐项自检它。

**三类定义**：

| kind | 修什么 | 去处（destination） | 机制（mechanism） |
|---|---|---|---|
| 业务错 | 业务口径/事实错（如数值口径、术语缺失） | 本体 MR（人审） | 提案池 `docs/proposals/PROP-*.md` → Owner 裁决 → 人 merge（过语义 CI） |
| 工程错 | 平台脚本/闸的实现错（不涉本体语义） | `tickets/` 票 | `tickets/NN-*.md` 一票一提交（续跑协议串行，四闸绿收官） |
| 元模型错 | schema/框架层错（七模型、闸的判定面本身） | schema 演进票 | CHANGELOG+版本号+迁移注记，模型注册表/依赖白名单同步 |

**实例指针**：每条实例 = `{desc, ticket, commit, props?}`，commit 是修复落地票的短哈希、props 是该道修复涉及/产出的提案 ID。**每类路由 instances ≥2 条真实指针**；写入前逐个核实（commit 在 `git log`、PROP 文件在 `docs/proposals/`），probe 第 10 项每次体检都会逐个复核，坏指针=体检红。

**维护纪律（改路由三件套）**：改路由 = ①改本 JSON + ②补/改实例指针（先核实再写入）+ ③跑 `python3 tools/meta_probe.py ontology/<域>` 逐域（实跑域 ontology/bohai、ontology/his 必跑；豁免注记域 ontology/pkb 照跑留痕——第 10 项硬闸必须全绿）。只改 README 不改 JSON = 没改。
