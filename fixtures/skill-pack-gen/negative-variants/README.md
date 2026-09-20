# negative-variants（票 36 负变体）

## bohai-no-m3

bohai 副本剃掉 `m3-rule-model.yaml`，其余文件=金包切片（M1,M2,M3,M7,GLS）的
全量声明面副本：`manifest.json`、`m1-object-model.yaml`、`m2-behavior-model.yaml`、
`m7-report-model.yaml`、`glossary-model.yaml`。M5/M6 非切片声明面文件，不复制
（同票 35 app-pack-gen 负变体取舍：副本只带声明面，全量复制徒增同步面）。

断言（assertions.json AC3 第一条）：

```
python3 tools/skill_pack_gen.py {fixture_dir}/negative-variants/bohai-no-m3 \
  --models M1,M2,M3,M7,GLS --schema-dir ontology/schema
```

期望：exit 2，stderr 含「缺声明模型」并指认 M3，不产出残包
（specs/modules.md 边界规则 5 生成器侧，票 36 第二证）。

注：`--schema-dir ontology/schema` 为显式注入——fixtures/ 下无 schema 邻目录，
自动定位（`<域>/../schema`）不可达；schema 是仓级共享件，cmd 显式指认属正常
用法（cwd=仓根）。

## （负变体 B：build-contract 切片）

第二条负变体不需要域副本：对真域 `ontology/bohai` 声明 `--models M1,MU`
（MU camp=build-contract），camp 判定读 model-registry.json 且在文件存在性
核对之前（先阵营后存在性），exit 2 报「声明含非 business-core 阵营模型 MU」。
断言见 assertions.json AC3 第二条。
