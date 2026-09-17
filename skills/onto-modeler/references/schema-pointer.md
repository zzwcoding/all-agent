# schema 真源索引（onto-modeler 细则）

> 本文只指路，不复制内容——复制即造双真源。建模中要查什么，进下列真源：

| 要查什么 | 真源 |
|---|---|
| 人读总纲：公共字段与文件命名、ID 前缀与 ref 命名约定、四层下沉判定、七模型逐模型字段表、换义锁定字段表 | `ontology/schema/schema.md` |
| 机读：每模型 camp / consumers / profiles / dependsOn / modelType / lockedFields（profile 推荐与合规判定消费） | `ontology/schema/model-registry.json` |
| 机读：ID 前缀表、ref 字段名全集、类型层依赖白名单边（引用纪律与修整步自查消费） | `ontology/schema/model-deps.json` |

## 使用约定

- 「这个字段怎么写」以 schema.md 为准；schema.md 与本 skill 正文/细则冲突时 schema.md 赢，并回改本 skill（卡与正文是消费方，schema 是真源）。
- 两份机读表是语义闸（`tools/schema_check.py`）的判定真源；「草案修整到过闸」即「与机读表对齐」，不要绕过闸自行解释。
- schema 本身的演进（加模型、改组合、改白名单）不走本 skill——那是元模型错路由的 schema 演进票，本 skill 只按现行 schema 建模。
