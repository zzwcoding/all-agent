# 票 59：pkb 域 devkit 导出 + 审记（含实弹暴露两处平台缝隙修复）

Status: done

> 实弹记录（2026-09-22）：本票 do 时发现两处平台缝隙，均按信号路由工程错道**并入本票修复**（两处都是本票交付物 devkit 导出+审记的直接阻塞，非顺手修）：① `app_pack_gen` 声明集写死 M1/M2/M3/M7，遇 manifest `omittedModels` 豁免域（pkb 豁免 M3/M7）拒产——而豁免是 schema 合法态（bohai MU 同款机制）；修法=声明集校验尊重 manifest（M2/M3/M7 带理由可豁免→对应节渲染「豁免未建」注记；M1 恒不可豁免；未豁免缺件照 exit 2，bohai-no-m3 负变体红保持）。② `review_gate verify` 取旁档 `records[-1]` 不过滤 target——devkit 旁档按 stem 共享（bohai/pkb 同落 devkit-review.json），pkb verify 错拿 bohai 锚误判「失效」；修法=按记录内 target 过滤（构件边界后缀匹配——approve 相对串/verify 绝对串判同件，review-gate 夹具 stale 负变体回归钉死），无本目标记录→pending「无本目标审记」。
Belongs to: docs/第五期端到端实弹拆票方案.md §4（前置：票 58 done）
Touches: exports/devkit/pkb/、exports/reviews/devkit-review.json（init 骨架）、tools/app_pack_gen.py、tools/test_app_pack_gen.py、tools/review_gate.py、tools/test_review_gate.py、fixtures/app-pack-gen/assertions.json

## What to build

1. 生成器 profile 感知（缝隙①修复）+ 单测 3 例（豁免出包注记/M1 不可豁免/文件在场豁免无效）。
2. verify 按 target 过滤（缝隙②修复）+ 单测 1 例（共享旁档跨件不误判）。
3. pkb devkit 导出 `exports/devkit/pkb/`（devkit.md+json，四节齐：①数据字典 AGG-PKB-001/②口径节豁免注记/③行为五件清单+规则节豁免注记/④开放疑点）。
4. 审记：verify 状态=**pending 无本目标审记（待人审）**——approve 是 Owner 人审动作（协议第11条不代行），Owner 过目后 `review_gate.py approve exports/devkit/pkb/devkit.md`；bohai 件 verify 回归仍已审一致（零扰动实证）；review-gate 出厂集 stale 负变体回归通过（绝对路径 verify 判「审记失效」）。
5. 出厂集 +2 断言（pkb 豁免域 --check 防陈旧 + 豁免注记机核），AC 真源=本票 AC 表。

## 验收（注源）

- [x] AC1 devkit 生成且四节齐可指认（AGG-PKB-001/BH-PKB-*，M3/M7 豁免注记符合 manifest）（源：本票 AC 表+出厂集断言②）
- [x] AC2 豁免域正例：pkb exit 0 出包+入库副本 --check 再制一致；未豁免缺件照拒（bohai-no-m3 出厂集红保持）（源：出厂集断言①+现有 AC3）
- [x] AC3 审记：verify=pending 待人审（旁档在场不代审）；bohai 件 verify 仍 exit 0 已审一致（源：design §3.4 #2+协议第11条）
- [x] AC4 单测：app_pack_gen 32 OK（+3 豁免例）、review_gate 38 OK（+2 跨件例/夹具回归例）（源：实跑）
- [x] AC5 归档闸认 exports/devkit/pkb/ 布局（沿既有 exports/devkit/&lt;域&gt; 模式）（源：归档闸）
- [x] AC6 `bash tools/ci.sh` 四闸全绿（源：CI/协议⑩）

## 交接包（L0 自执行）

任务: 两缝隙修复+devkit 导出+审记 init+出厂集扩容。
产出: 生成器/审记闸改+测试 4 例+exports/devkit/pkb/+断言 2 条。
验收: AC1–6 全过后翻 done 一票一提交。
