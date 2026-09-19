# 提案池（docs/proposals/）· 规范指引

这里是**业务语义循环的闸口**：监督/自检/交互三源信号归一成标准提案，等 Owner
裁决；自动化止于提案——不起 git 分支、不直改 ontology/**，真提案进仓走 MR +
语义 CI 由人完成。

## 这个目录里放什么

- `PROP-<域>-<NNN>.md`：提案文件（格式真源与机读字段定义见仓根
  references/proposal-format.md，与检查工具 tools/proposal_check.py 的头注一字
  不差对齐）。
- 其他 md（对账说明等）可以共存——检查工具只解析 `PROP-*.md`，其余跳过。

## 提案状态机（速查）

```
draft（起草中/证据不足/有未解冲突）
  → open（自检全过，等 Owner 裁决）
      → accepted / rejected（只由 Owner 裁决产生；落痕=改 status+正文注记，不删档）
```

- 起草人可翻：draft → open（条件：工具四类检查全过）。
- 只有 Owner 可翻：open → accepted / rejected。
- rejected 是资产：同信号再现先查池，不重复起草；翻案走新提案并引用旧号。

## 起草与自检

1. 起草按 proposal-pool skill 工序四步（信号受理 → 归一格式 → 冲突预检 → 落盘
   +状态纪律）；五类信号的受理标准与证据等级细则见该 skill 的
   references/signal-normalization.md。
2. 落盘前后自检：`python3 tools/proposal_check.py docs/proposals` ——四类检查
   （proposal-schema / proposal-target / proposal-conflict / proposal-evidence）
   全过（退出码 0）才算有效在池提案；新提案起草中允许暂为 draft，翻 open 前
   必须全过。
3. 冲突处置：同靶两 open 提案 change 矛盾由工具报出（proposal-conflict），谁对
   由 Owner 裁决；在裁决前任何一方不得擅自撤改对方提案。
