# 票 56：proposal_check 裁决后盲区修复（A 线首份实弹发现的工程错）

Status: done

> 注（L0 紧急清偿，2026-09-21）：A 线 PROP-BOHAI-006 采纳进仓后 proposal_check 报「add 的靶元素已存在」——accepted add 提案的靶在场是**实施完成的预期态**，检查②对全状态提案一刀切属判定面越界。信号路由：工程错道 → 本票。另如实记：50da7f3 带红入仓（L0 闸链用管道致退出码被 tail 吞掉，违反协议第⑩条精神），教训落 lessons/57。
Belongs to: docs/proposals/PROP-BOHAI-006.md 采纳流程实弹发现；policies/signal-routing.json 工程错道
Touches: tools/proposal_check.py、tools/test_proposal_check.py、lessons/57-票56-proposal_check盲区修复.md

## What to build

检查②（proposal-target 存在性）判定面从"全部有效提案"收敛为**仅 draft/open**——与检查③（池内冲突只 open 参战）同一哲学：已裁决（accepted/rejected）提案的靶元素在场与否不再是待裁事实。accepted add → 靶在场=预期；accepted modify/deprecate → 靶在场=前提；rejected → 靶在不在都合法。④ evidence 检查维持全状态（证据链终身有效）。

## 验收（注源）

- [x] AC1 accepted add + 靶已存在 → 绿（回归钉死盲区）（源：本票 AC 表）
- [x] AC2 open add + 靶已存在 → 仍红（原判据不松）（源：本票 AC 表）
- [x] AC3 仓内真池全过（31 份：accepted 8 份含 4 份 add/modify 混合）（源：实跑）
- [x] AC4 `bash tools/ci.sh` 四闸绿（源：CI）

## 交接包（L0 自执行）

任务: ②判定面收敛+回归测试×2+头注口径更新+lessons 检讨。
产出: proposal_check.py（②加 draft/open 门）+test×2+lessons/57。
验收: AC1–4 全过。

### AC 表（出厂集断言，真源=本表）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 | accepted + add + 靶存在 | exit 0 无 proposal-target |
| AC2 | open + add + 靶存在 | exit 1 proposal-target 红 |
| AC3 | docs/proposals 真池 | 全过 |
| AC4 | CI | 四闸全绿 |
