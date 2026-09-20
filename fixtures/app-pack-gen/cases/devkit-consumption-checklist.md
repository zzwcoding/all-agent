# 开发包消费用例单（fixtures/app-pack-gen/cases，票 35）

> 出厂集用例面：编码 agent 拿到 exports/devkit/<域>/ 后的确定性消费契约。
> 断言真源=本出厂集 assertions.json（AC 表=tickets/35-应用生成器.md）。

## C1 · 四节齐读（AC1/AC4 载体）

给定 devkit.md（人读面）与 devkit.json（机读面）：

- 头部 `status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）` 在场——生成物禁手改，缺件回生成器再生；人审结论在审记旁档 exports/reviews/（票 46），本件被审过与否由 `python3 tools/review_gate.py verify <devkit.md>` 机判；
- 四节齐：一、数据字典（M1）；二、口径四件套（M7×M2×M3×M1）；三、行为与规则清单（M2/M3 全量）；四、开放疑点（docs/proposals 扫描）；
- 头部约束节=技术架构约束/开发指导书（出厂集固定输入（合成）），按原样装配。

## C2 · 口径同源机核（AC1 载体，抽 1 问）

跑语义服务核心对 bohai 问「日产量口径是什么？」，其命中 ID 集（CORE-01 冻结
期望=AGG-BOHAI-002 / BH-BOHAI-QueryWellDailyOutput / QR-BOHAI-001 /
RULE-BOHAI-003 / RULE-BOHAI-004）必须逐个落在开发包 JSON 口径节对应卡片
（QR-BOHAI-001 单井日产量明细查询）的 `hitIds` 里——口径四件套与 CORE 八问
同源（装配面：behaviorRef + sourceObjects.objectRef + 关联 M3 规则）。

## C3 · 防陈旧（AC2 载体）

- 幂等：同域连跑两次，devkit.md/devkit.json 字节一致；
- `--check`：现场重生成与入库副本逐字节比对，一致 exit 0；入库副本禁手改，
  篡改/陈旧即红（单测篡改探针钉死）。

## C4 · 缺声明模型拒收（AC3 载体）

负变体 negative-variants/bohai-no-m3（bohai 副本剃掉 m3）→ exit 2 + stderr
指认「缺声明模型 M3」，不产出残包（边界规则 5 生成器侧首证）。
