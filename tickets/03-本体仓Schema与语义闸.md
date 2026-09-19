# 票 03：本体仓 Schema + 语义闸 + 骨架

Status: done
Belongs to: specs/schema_check.md；PRD F1/F2
Touches: ontology/schema/、tools/、fixtures/schema_check/

## What to build

- `ontology/schema/`：七模型精简 YAML schema（M1/M2/M3/M5/M6/M7/MU，v9 蓝本+运行期字段预留）+ `model-registry.json`（camp/consumers/profiles/dependsOn）+ `model-deps.json`
- `tools/schema_check.py`（TDD，stdlib+PyYAML，实现 specs/schema_check.md AC1–7）
- 从 sdd-flow2 实例化三闸 + ci.sh 进本仓 tools/
- fixtures/schema_check/ 最小域出厂集
- 渤海域 manifest（profile=v9 七模型）

## 验收（注源）

- [x] AC1–7 全过（源：specs/schema_check.md）
- [x] 模型注册表含 camp/consumers/profiles/dependsOn 四字段（源：PRD F1）
- [x] ci.sh 四闸绿（源：设计案主线 2）
- [x] 归档闸过（本仓文件全合规）

Blocked by: 无
