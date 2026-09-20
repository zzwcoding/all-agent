# 样例生成物（出厂集靶件 · 票 45）

status: 待Owner人审（生成物禁手改，可再生）

本文件是 fixtures/review-gate 出厂集的**审记靶件**：内容固定、逐字节稳定，
records*/ 下的预置审记以本文件的 SHA256 为锚。预置审记里的 reviewedCommit
= 348fa9cfcf1404144e771574b5742af30e16393c（本出厂集落盘时点所在 commit）。

靶件正文（稳定字节面，任何一方不得改动——改了 stale 变体之外的全套断言会翻红）：

- 数据字典：sample_entity(id, name)
- 口径卡：SAMPLE_QR「样例口径」→ sample_entity.name 计数
- 行为：SAMPLE_ACT.create（约束 name 非空）
