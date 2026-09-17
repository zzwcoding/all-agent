# 票 06：skill db-reverse

Status: todo
Belongs to: specs/db-reverse.md；PRD F6
Touches: ~/.agents/skills/db-reverse/、fixtures/db-reverse/

## What to build

- skill 本体（DDL→本体草案工序；references 含逆向指导书）
- fixtures/db-reverse/ 出厂集：渤海域 8 表 DDL 子集（取自 R5 设定书附录 A）+ AC1–4 断言

## 验收（注源）

- [ ] AC1–4 全过（源：specs/db-reverse.md）
- [ ] 草案头固定声明"证据非权威"（源：spec 行为约定）
- [ ] 素材逐条注源 R5（源：取材锁纪律）

Blocked by: 票 03

## 交接包（L2 自主档）

任务: 建 skill db-reverse + fixtures/db-reverse/ 出厂集（渤海域 8 表 DDL 子集）。
先读: specs/db-reverse.md（AC1–4）；specs/modules.md 卡；ontology/schema/schema.md；素材真源 /Users/divh/Downloads/teach-petro-agent/docs/business-setting.md（8 表 DDL 在其附录 A，即 v2 §2；若当前版无完整 DDL 则 `git -C /Users/divh/Downloads/teach-petro-agent log --oneline -- docs/business-setting.md` 找 v2 版本提取）。
框架红线: 出厂集先行；素材逐条注源 R5；草案头部固定声明"证据非权威，待 Owner 确认"；不发明 DDL 里不存在的业务语义。
边界红线: skill 正文域无关；渤海域内容只许进 fixtures 与 ontology/bohai/。
产出: ~/.agents/skills/db-reverse/（含 references/ 逆向指导书）+ fixtures/db-reverse/（8 表 DDL 子集 + assertions.json AC1–4）+ lessons/06-*.md。
验收: AC1–4 全绿；注源齐；ci.sh 四闸绿。
回报: 产物路径 + ci.sh 摘要 + 偏差。不 commit。
