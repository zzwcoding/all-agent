# spec · schema_check（语义 CI L1–L4）

触及: tools/schema_check.py（L3 脚本）；契约: CLI `schema_check <ontology目录> [--json]`

## 出厂集断言表

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | 合法本体（fixtures 最小域） | exit 0，报"全过" |
| AC2 | YAML 语法错误文件 | 报 L1 失败+文件名，非零退出 |
| AC3 | 缺 model_type/version/domain 公共字段 | 报 L1 失败并指名字段 |
| AC4 | ref 指向不存在的 ID | 报 L2 失败+悬空引用位置 |
| AC5 | ref 类型越白名单（M2 引 M7） | 报 L2 失败+违反的依赖规则 |
| AC6 | profile 未启用的模型文件出现 | 报 L4 失败 |
| AC7 | 字段换义式变更（同名不同义） | 报 L4 兼容性失败 |

## 行为约定

- 只读不写 YAML；失败输出含文件+行级定位；--json 供 CI 消费
- 依赖白名单与模型注册表来自 `ontology/schema/model-registry.json` + `model-deps.json`，不硬编码
