# 四层规则下沉判定（onto-modeler 细则）

> 判定框架真源在 `ontology/schema/schema.md` §3（内置字段 → refRules → invariants → M3）；本文是工序视角的执行细则，不复制字段表。

## 判定（逐级下沉，不许上跳）

拿到一条约束，按顺序问：

1. **结构性约束？**（必填、唯一）→ 属性内置字段 required / unique。
2. **只依赖当前属性值？**（如「≥0」「非空格式」）→ 该属性的 refRules 局部执行点（带 violationMessage 与 enforcedAt）。
3. **只依赖同聚合内部？**（如「记录必须挂到本聚合的某对象上」）→ 聚合 invariants。
4. **跨对象/跨行为/被复用？**（行为引用的校验、多对象联动条件、多处共用的口径）→ M3 规则，行为用 appliedRules 显式引用 ID。

同一约束原则上单一落点；确需「局部执行点 + M3 复用登记」双层并存时，两处语义必须一致，并在草案标注待 Owner 确认（双层登记是维护负担，默认不加）。

## 硬约束（第 4 步修整自查用）

- **规则无副作用**：规则只答条件是否满足；改状态的是行为。两者不合并表达。
- M3 的 expression / narrative 双写法为运行期预留：一期至少给 expression；需要人读口径时补 narrative。
- **跨聚合联动**（syncTriggers）：下游行为必须作用于另一个独立聚合（禁止同聚合自我联动）；查询行为的 syncTriggers 必须为空；联动失败语义必须在 postconditions 或流程模型里写明，禁止隐含吞异常。
- **枚举互斥**：属性 type=Enum 用 enumValues，type=DictionaryRef 用 dictionaryRef，两者不得并存。
- **引用显式**：禁止只在 description 里写引用；引用字段值必须是带模型前缀的稳定 ID（「前缀即类型标签」，前缀与 ref 字段名真源在 `ontology/schema/model-deps.json`）。
- **换义锁定**：注册表 lockedFields 登记的字段名禁止复用——新义必须新增字段名。
- **字典治理**：字典项停用置 enabled: false 保留行，不删除；删除走影响分析。
