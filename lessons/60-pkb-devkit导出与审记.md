# 60 · pkb devkit 导出与审记（生成器豁免感知 + 审记跨件错拿锚，两缝隙实弹修复）

- 日期: 2026-09-22
- 角色: L2 编码（票 59 施工窗）
- 票: tickets/59-devkit导出与审记.md
- 依据: docs/reviews/2026-09-23-phase9-review-pkb-domain.md（第九轮后 pkb 审查——meta_probe 多域失真 P2-1 与本案同源于「工具写死第一域假设」，票 64 另修）；design-human-review-gate §3（devkit=全审级）
- 性质: 第二域首个派生物导出 + 两处平台缝隙实弹发现与修复

## 做了什么

1. **pkb devkit 导出** exports/devkit/pkb/（四节齐：数据字典 AGG-PKB-001/口径节豁免注记/行为五件+规则节豁免注记/开放疑点）+ 入库副本 --check 再制一致。
2. **审记 init**：exports/reviews/devkit-review.json 记 pkb 件 pending 待人审（approve 归 Owner，协议第 11 条不代行）；bohai 件 verify 回归仍已审一致（零扰动实证）。
3. **缝隙①修复**：app_pack_gen 声明集写死 M1/M2/M3/M7，遇 manifest omittedModels 豁免域拒产——修法=声明集尊重 manifest（M2/M3/M7 带理由可豁免→渲染「豁免未建」注记；M1 恒不可豁免；未豁免缺件照 exit 2，bohai-no-m3 负变体红保持）+ 单测 3 例。
4. **缝隙②修复**：review_gate verify 取 records[-1] 不过滤 target——devkit 旁档按 stem 共享（bohai/pkb 同落 devkit-review.json），pkb verify 错拿 bohai 锚误判失效；修法=按记录内 target 过滤（构件边界后缀匹配）+ 单测 2 例。
5. 出厂集 +2 断言（豁免域 --check 防陈旧 + 豁免注记机核）。

## 取舍

1. **常量改按域查表，缺表项=显式豁免而非报错或错配**：app_pack_gen 声明集、review_gate 取 records[-1]、（票 64 修的）meta_probe golden 集与图基线锚——三处同款病根（第一域=唯一域时期写的常量），修法也同款：按 manifest/记录内字段/注册表查，查不到就渲染豁免注记。
2. **审记旁档消费契约=先过滤 target 再取最新**：旁档按 stem 共享后「最新一条」≠「本件一条」；错拿是静默错（误判失效/误判已审都可能），比拒产更危险——契约应随票 46 人审闸面传播到所有共享旁档消费方。
3. **skillpkg 无 pkb 产物挂账不默认**：headless 域是否需要 skillpkg 未裁，挂 docs/proposals/residual-questions.md 待 Owner（2026-09-23 已入账）——豁免与否要有文书，不留「没做就是不要」的默认。

## 坑（如实记，两条）

1. **豁免域出包是合法态不是异常，但工具把它当异常**：bohai MU 单件缺席时缝隙①没暴露（M3 在场凑齐了声明集），pkb 两整模型豁免才压出拒产——第一域的「恰好没缺」掩盖了写死常量，第二域一来显形；负变体（bohai-no-m3）红保持=「未豁免缺件照拒」边界没破，修复面只在豁免侧，别为修豁免把负变体修绿。
2. **verify 错拿他域锚是静默误判**：records[-1] 在单域时期语义正确，多域共享旁档后 pkb 拿 bohai 锚判「失效」——表面是审记问题，根因是取数无过滤；修完必须用共享旁档跨件回归例钉死（stale 负变体），否则下域接入再犯。
