# ontology/schema CHANGELOG

schema 三件（`schema.md` 人读 + `model-registry.json` / `model-deps.json` 机读）的版本演进账。
版本号记在两份机读表顶层 `version`（语义化三段，两表必须同步）；本文件记**为什么变、迁移注意什么**。
演进路由：元模型错 → 框架版本演进（CHANGELOG + 版本号 + 迁移票伴随实现票，CONTEXT.md 信号路由表）。

## 1.1.0 · 2026-09-19 · 票 10：术语模型 GLS（元模型演进）

**变更点**

- 新增第 8 个模型类型 **GLOSSARY（GLS）**：文件 `glossary-model.yaml`（照 `mu-ui-model.yaml` 非数字先例）、ID 前缀 `GLS-`（`GLS-{域}-{Seq}`）、camp=business-core、consumers=[runtime, build]。OMF v6/v9 均无此模型，属本仓自定义扩展——术语（概念定义/别名/解释）与 M1 DICT（值域字典）不是一回事。
- **profile 组合**：GLS 入 v9-full 与 headless，**不入 v9-core**（四模型最小核保持原样，术语属增强件；"未启用"因此有可测负变体 GLS-AC2）。
- `model-deps.json`：idPrefixes 增 `GLS-→GLS`；refKeys 增 `relatedObjectRefs`；edges 增 `GLS.relatedObjectRefs→[M1]`（GLS 依赖白名单只此一条，单向；GLS→GLS 不设边，见 schema.md §11）。
- `tools/schema_check.py` 新增 **L1 filename-mismatch** 检查：模型文件名必须等于注册表该模型 `yamlFile`（真源=机读表，非脚本硬编码）。对既有七模型是"一模型一 YAML、固定文件名"约定（schema.md §1）的闸上强化；对 GLS 承载票 10 AC4（model_type 写错如 OBJECT / GLS 文件名错挂 → 红）。
- 出厂集 `fixtures/schema_check/` 增 GLS 套件：`gls-valid` 正变体 + `gls-ac2-core-profile` / `gls-ac3-dangling-ref` / `gls-ac4-filename-mismatch` 三负变体，断言 GLS-AC1–4。

**版本演进说明**

- 两份机读表顶层 `version` 由整数 `1`（票 03 初版未落语义化号）演进为 **`"1.1.0"`**，本票起立约：版本号语义化三段、两表同步、每次演进必配本文件条目。

**迁移注记：旧域零改动兼容**

- 无 `glossary-model.yaml` 的域**不校验 GLS**（缺在场不校验是既定行为，AC6 同款语义）——现有域（`ontology/bohai/`、fixture `valid-domain` 等）零改动仍全绿。
- v9-core 域出现 GLS 文件 = L4 红（GLS-AC2）；GLS 文件 model_type 写错或文件名错挂 = L1 红（GLS-AC4）；术语 relatedObjectRefs 悬空 = L2 红（GLS-AC3）。
- 域 manifest 的 `schemaVersion` 不强制联动本版本号（现状闸不校验联动），各域按需自行演进。
