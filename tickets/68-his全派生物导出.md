# 票 68：his 全派生物导出（devkit+skillpkg+mcp manifest+审记 init）

Status: todo

> 反向验证：票 59 的豁免感知修复在本域**不应触发**（M1/M2/M3/M7/GLS 全齐，声明集天然满足）——全模型域出包路径首跑。
Belongs to: docs/第六批第三域拆票方案.md；前置=票 67 done
Touches: exports/devkit/his/、exports/skillpkg/his/、exports/mcp/capability-manifest.json、exports/reviews/devkit-review.json、exports/reviews/skillpkg-review.json（init）、fixtures/app-pack-gen|skill-pack-gen/assertions.json

## What to build

1. devkit 导出 exports/devkit/his/（四节齐：数据字典/口径节/行为+规则节/开放疑点）+ --check 再制一致。
2. skillpkg 导出 exports/skillpkg/his/（--models M1,M2,M3,M7,GLS）+ --check 再制一致——his 为 skillpkg 豁免裁决（5a44504）后首个出包域，反向验证豁免不影响全模型域。
3. mcp_manifest_gen 再制 capability-manifest.json（his 域块增量，bohai/pkb 零扰动）。
4. 审记 init：devkit/skillpkg 各 pending 待人审（approve 归 Owner 协议第 11 条）；bohai/pkb 件 verify 回归一致。
5. 出厂断言 +2（his devkit --check 防陈旧 + his skillpkg --check 防陈旧），AC 真源=本票 AC 表。

## 验收（注源）

- [ ] AC1 devkit 四节齐可指认（AGG-HIS-*/RULE-HIS-*/QR-HIS-*）；豁免修复零触发实证（生成器无豁免注记渲染，输出无「豁免未建」）
- [ ] AC2 skillpkg 出包+--check 一致；calibers 与 QR-HIS-* 对齐
- [ ] AC3 manifest --check 双跑一致（bohai/pkb 块字节零扰动实证）
- [ ] AC4 审记 verify=pending（bohai 已审/pkb pending 回归不变）
- [ ] AC5 出厂断言全过（含新增 2 条）+ `bash tools/ci.sh` 四闸全绿（最终树原样跑，协议⑩）

## 交接包（L0 自执行）

任务: 三件套导出+审记+断言。
产出: exports 下 his 全件+断言 2 条。
验收: AC1–5 全过后翻 done 一票一提交。
