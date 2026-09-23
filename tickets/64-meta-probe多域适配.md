# 票 64：meta_probe 多域适配（信息项按域选基线，域无基线=豁免注记）

Status: done

> 来源：第九轮后第二域专项审查 P2-1（docs/reviews/2026-09-23-phase9-review-pkb-domain.md）。实弹：`meta_probe ontology/pkb` 硬闸 5/5 绿但第 3 项 CORE 分布 golden 集硬编码 bohai（pkb 跑 8/8 拒答信息红）、第 9 项图基线硬编码查 AGG-BOHAI-001（基线与域错配）——批收官协议第①条体检留痕对第二域失真，随域数放大。
Belongs to: 第九轮后 pkb 域审查整改（票 63–65）
Touches: tools/meta_probe.py、（如结构需要）fixtures/ 或 docs/meta/ 基线约定、tools/test_*.py

## What to build

1. 第 3 项 CORE 分布探针按目标域选择 golden 期望集：bohai 沿用现有冻结期望；pkb（及未来无 golden 集域）渲染「域无 CORE 基线=豁免」注记判 GREEN，不得假红。
2. 第 9 项图基线锚查询按目标域取值：bohai 仍查 AGG-BOHAI-001；pkb 查本域真实锚（如 AGG-PKB-001，存在性先核）或同豁免注记。
3. 单测/出厂断言：pkb 域跑探针信息项无 RED（豁免注记在位）；bohai 域两探针结果与现状逐字一致（回归零扰动，现值留痕可对照 /tmp 或重跑 bohai 基线）。
4. 硬闸五项对 bohai/pkb 两域均绿不变；探针报告模板两域同版式。

## 验收（注源）

- [x] AC1 `python3 tools/meta_probe.py ontology/pkb --out docs/meta/体检-<日期>-pkb.md` 结论 PASS 且信息项无 RED（CORE 分布/图基线均 GREEN 或豁免注记）
- [x] AC2 `python3 tools/meta_probe.py ontology/bohai --out <对照件>` 与整改前 bohai 结果逐项一致（第 3/9 项摘要零差）
- [x] AC3 单测/出厂断言在位并全过（新增豁免例数实跑记录）
- [x] AC4 `bash tools/ci.sh` 四闸全绿（最终树原样跑，协议⑩）

## 交接包（L0 自执行）

任务: 探针两信息项域感知化，硬闸不动。
产出: meta_probe.py 修订+测试+两域各一份体检留痕（pkb 为修复后首次无失真留痕）。
验收: AC1–4 全过后翻 done 一票一提交；commit message 引审查报告路径。
