# 票 69：his 全平台实弹走查（图索引/语义服务/Golden 冻结/影响分析）

Status: done

> 压测批的压测核心：让运行时消费面（图索引/语义核心/生成器/--check/审记闸）全部对新域实弹一轮，Golden 8 问冻结进 fixtures（meta_probe 第 3 项 his 条目随本票登记，票 64 机制复用）。
Belongs to: docs/第六批第三域拆票方案.md；前置=票 68 done
Touches: fixtures/semantic-service/assertions.json（+8 问）、tools/meta_probe.py（CORE_QUESTION_SETS 增 his）、docs/walkthrough/his-*、docs/impact/

## What to build

1. **图索引实弹**：graph_index ontology/his 建图统计留痕；closure/impact 各 2 例（如 QR-HIS 报表→ADS 对象下游、RULE-HIS 告警→Dashboard 影响面），走查留痕 docs/walkthrough/his-step-graph.md。
2. **语义核心实弹**：semantic_service_core 对 his 域 8 问（锚定/闭包/拒答三态各覆盖：命中对象问/口径问/越面问），逐问留痕状态与命中 ID。
3. **Golden 冻结**：8 问期望状态冻结进 fixtures/semantic-service/assertions.json（新域节，不碰 bohai CORE-01–08）；meta_probe CORE_QUESTION_SETS 增 his 条目+GRAPH_BASELINE_ANCHORS 增 his 锚——pkb 豁免注记与 his 实跑两态并存实证；meta_probe ontology/his 跑一遍信息项无失真。
4. **影响分析实弹**：impact-analyzer 对 1 个变更样本（如「退号率口径改阈值」）走 ref 反向取证，报告落 docs/impact/。
5. 全派生物 --check 再生一致复核（devkit/skillpkg/manifest）。

## 验收（注源）

- [x] AC1 建图统计+2 例 closure/impact 命令输出留痕，命中 ID 可指认
- [x] AC2 8 问实弹全绿（锚定问 answered/越面问 refused_*），语义核心不编造（拒答或带引用，零幻觉 ID）
- [x] AC3 fixtures 断言 his 节 8 条在池且 fixture_run 绿；meta_probe ontology/his 第 3/9 项实跑非豁免（his 有冻结集）
- [x] AC4 影响分析报告落 docs/impact/，每条影响项带传播依据
- [x] AC5 `bash tools/ci.sh` 四闸全绿（最终树原样跑，协议⑩）

## 交接包（L0 自执行）

任务: 运行时消费面全实弹+Golden 冻结。
产出: walkthrough/impact 留痕+fixtures his 节+探针 his 登记。
验收: AC1–5 全过后翻 done 一票一提交。
