# 票 66：MCP smoke U8 量级快照断言陈旧修复（断契约形态不断快照数）

Status: done

> 来源：2026-09-24 全量 demo 实弹发现（Owner 在场）：`.venv-mcp/bin/python tools/mcp_smoke_client.py` 8/9——U8 断言钉票 24 时点快照「56 个受影响节点」，渤海域本体合法演进（第五期前各票增规则/行为）后实际 64，断言红非产品红（服务端与图索引行为均正常）。同源陈旧：fixtures/mcp-publisher/cases/mcp-tool-contract-usecases.md U8 行钉「（56 节点）」。可复跑：现跑 smoke 客户端 U8 必红（56≠64）。
Belongs to: 第五期批外整改（demo 信号即时清偿）
Touches: tools/mcp_smoke_client.py、tools/test_mcp_smoke_client.py、fixtures/mcp-publisher/cases/mcp-tool-contract-usecases.md

## What to build

1. U8 断言改形态契约：contains「【影响 --impact】」+「个受影响节点（依赖方）」+ BH-BOHAI-QueryWellDailyOutput + hops=1；not_contains「0 个受影响节点」（非空守卫）。不再钉任何数字量级——量级随本体演进是活数（56→64 实证），契约断形态不断快照。
2. fixtures 对照单 U8 行同步去数字（同款口径注记，注票 66）。
3. 单测加 U8 契约钉（test_u9 同款先例）：形态 token 与非空守卫必须在位、任何「<数字> 个受影响节点」量级快照 token 不得出现在 expect_contains——约定不落闸等于没有。
4. docs/walkthrough/step7-mcp-e2e.md 两处「56」=票 24 时点快照走查留痕，**不回改**（审计链保持原样）；本票票面与 commit message 留痕说明。

## 验收（注源）

- [x] AC1 `.venv-mcp/bin/python tools/mcp_smoke_client.py` 9/9 全过退出 0（修复后实跑，输出摘要留票面施记）
- [x] AC2 `python3 -m unittest tools/test_mcp_smoke_client.py` 全过（含新增 U8 契约钉；`.venv-mcp/bin/python -m unittest` 协议面全过）
- [x] AC3 `bash tools/ci.sh` 四闸全绿（最终树原样跑，协议⑩）
- [x] AC4 lessons/61 在场（对齐票 55 收敛体例：含「取舍/坑」必备节）

## 交接包（L0 自执行）

任务: U8 断言快照值改形态契约 + 对照单同步 + 契约钉单测。
产出: smoke 客户端 9/9 实跑留痕（票面施记）+ lessons/61。
验收: AC1–4 全过后翻 done 一票一提交。

## 施记（2026-09-24，L0 自执行）

1. 修三处：`tools/mcp_smoke_client.py` U8 用例（量级快照→形态契约+非空守卫）；`tools/test_mcp_smoke_client.py` 增 `test_u8_impact_asserts_shape_not_count` 契约钉；fixtures 对照单 U8 行去数字。
2. 验收实跑：系统侧单测 21 例 OK（协议面 2 例按设计 skip）；`.venv-mcp/bin/python tools/mcp_smoke_client.py` **9/9 退出 0**（U8 实点 64 节点以形态契约过）；`.venv-mcp/bin/python -m unittest` 21/21 OK（含真起服协议面）。
3. walkthrough step7-mcp-e2e.md 两处「56」未回改（票 24 时点快照留痕，审计链原样）。
4. lessons/61 落盘（「绿会过期」+「demo 是唯一抓到它的面」两坑入账）。
