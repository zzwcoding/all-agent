# spec · graph_index（图索引构建器）

触及: tools/graph_index.py（L3 脚本）；契约: CLI `graph_index <ontology目录> --query <id> [--closure N] [--impact] [--json]`

> 断言真源（2026-09-19 起）：tickets/04 票面 AC 表 + fixtures/graph_index/assertions.json；本表为一期原始基线。

## 出厂集断言表

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | fixtures 最小域 | 图构建成功，节点/边数非零 |
| AC2 | 查询存在的 ID | 返回该节点及属性 |
| AC3 | --closure 2 | 返回 2 跳引用闭包（含经 ref 连出的下游） |
| AC4 | --impact 改某对象 | 返回受影响节点集（沿依赖白名单反向走） |
| AC5 | 查询不存在的 ID | 明确报"未找到"，不猜 |
| AC6 | 仓内容变化后重建 | 重建结果反映新真源（无陈旧缓存） |

## 行为约定

- 纯 Python stdlib 内存图；每次启动从 YAML 全量重建（Git 是真源，图是派生物）；禁止持久化缓存成权威
