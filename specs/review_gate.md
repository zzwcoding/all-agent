# spec · review_gate（人审闸审记状态机）

触及: tools/review_gate.py、tools/test_review_gate.py、fixtures/review-gate/、specs/archive-registry.json（review-record 类）

> 断言真源：tickets/45-人审闸审记状态机.md AC 表 + fixtures/review-gate/assertions.json（RG- 前缀探针）。
> 设计注源：docs/design-human-review-gate.md §2.3（审记旁档+哈希锚定）/§2.4（生命周期走查）/§3.4（边界情形）/§4（结论词汇与打回路由统一）/§5（明确不做）/§8（Owner 七点裁决，2026-09-20 全按推荐）。

## 定位

人审闸的承载机制（选型 A 吸收 C 的哈希锚定防伪面）：**生成物本体一字不动**（三生成物
status 行字面、归档闸既有契约、`--check` 防陈旧全零改动，design §5 不做 5），人审结论落
**审记旁档** JSON，每条审记锚定「被审版本的内容哈希 + commit」——本体再生即哈希变，
已审结论**自动失效回落待人审**（零宽限，裁决点 5）。与 `--check` 的哲学同构：`--check`
判「入库=可再生」，哈希锚定判「已审=就是这一版」，两处比对一套心智。威胁模型措辞
收敛（票 48 P3，与脚本头注同款）：本闸防遗忘/防错版本（design §3.4 自我限定），
非防恶意篡改——哈希锚定提供篡改*检测*非*防御*。本票（45）只做
审记格式与状态机脚本；**exports 接线在票 46**（必须等本格式冻结）。

## CLI 契约（照 --check 家族惯例）

```
python3 tools/review_gate.py init    <target> [--review-dir <目录>]
python3 tools/review_gate.py approve <target> [--checkpoints "…"] [--notes "…"] [--review-dir <目录>]
python3 tools/review_gate.py reject  <target> --routing "…" [--checkpoints "…"] [--notes "…"] [--review-dir <目录>]
python3 tools/review_gate.py verify  <target> [--review-dir <目录>] [--json]
```

- `<target>`：被审生成物路径（只读，任何动作不改其一个字节）。
- 审记旁档路径 = `<review-dir>/<target 去扩展>-review.json`；`--review-dir` 缺省
  `exports/reviews/`（裁决点 4 落点）。**必须可注入**：出厂集/单测在 exports 之外
  跑状态链全靠它。
- `init`：建审记旁档骨架（见下）。已存在 → 提示不重建（追加不覆盖）退出 0；
  已存在但不可解析（损坏）→ 拒绝重建退出 1（design §3.4 #2：审记可以缺，不可以编）。
- `approve`：追加一条 verdict=已审 审记。审记缺席时自动落头（首条记录即历史起点，
  不伪造任何裁决）；既有审记损坏 → 拒绝追加退出 1、既有审记记录违约 → 拒绝追加
  退出 2（追加不能"顺手修史"）。
- `reject`：追加 verdict=打回 审记。`--routing` 必带（缺失/空白 = exit 2，报错带
  「打回必须当场开单」分道指引）——裁决点 6：不允许只记审记意见悬着。打回即
  当场开单语义：业务错道→提案池起草 / 工程错道→tickets/NN（policies/signal-routing.json
  分道；人审闸因此是信号路由表的新信号源，design §4）。
- `verify`：现算目标 sha256 与最新裁决比对（判定树见下）。只读：任何红都不重建审记。
  `--json` 时 stdout 只含机读 JSON（含 status/exitCode/recordsCount/最新记录）。
- 错误与降级提示走 stderr，结论走 stdout。

## 审记旁档格式（与实现互为镜像）

```json
{
  "target": "exports/devkit/bohai/devkit.md",     // 建档时的目标自述（记录被审对象）
  "created": "2026-09-20",                        // 骨架落盘日（ISO 日期）
  "records": [                                    // 按时间追加，最新一条=有效态
    {
      "target": "exports/devkit/bohai/devkit.md", // 必备，字符串：被审目标
      "reviewedCommit": "348fa9cf…",              // 必备，字符串：git rev-parse HEAD
      "reviewedSha256": "6a0732…",                // 必备，64 位十六进制：被审版本现算 SHA256
      "verdict": "已审",                          // 必备，二元词汇：已审 | 打回（design §4 不自造第三套词）
      "checkpoints": ["装配完整性", "提案内容落位"],  // 必备，字符串列表（可空）
      "notes": "首审",                            // 必备，字符串（可空）
      "reviewedBy": "divh",                       // 必备，非空字符串：裁决人
      "date": "2026-09-20",                       // 必备，ISO 日期：裁决日
      "routing": "业务错:提案池…；工程错:tickets/NN…"  // verdict=打回 时必备非空
    }
  ]
}
```

字段表（记录级必备 = `target` / `reviewedCommit` / `reviewedSha256` / `verdict` /
`checkpoints` / `notes` / `reviewedBy` / `date`；`routing` 按 verdict 条件必备）：

| 字段 | 类型 | 必备 | 说明 |
|---|---|---|---|
| target | 非空 str | 是 | 被审目标（建档/approve 时原样落笔） |
| reviewedCommit | str | 是 | `git rev-parse HEAD`（以目标所在目录向上找仓）；git 缺席降级 `"unknown"` + stderr 提示 |
| reviewedSha256 | 64 位 hex | 是 | 审定时目标现算 SHA256（`hashlib.sha256`，字节级锚定） |
| verdict | `已审`/`打回` | 是 | 二元词汇（design §4 统一结论词汇） |
| checkpoints | str 列表 | 是 | 审点清单（`--checkpoints` 逗号/顿号/分号分隔） |
| notes | str | 是 | 备注（缺省空串） |
| reviewedBy | 非空 str | 是 | 裁决人 = `git config user.name`（**随票裁决：git 身份**，design 开放问题③）；取不到写 `"unknown"` + stderr 提示 |
| date | ISO 日期 | 是 | 裁决日（当日） |
| routing | 非空 str | verdict=打回 时 | 打回路由（当场开单指针） |

归档闸登记（specs/archive-registry.json review-record 类，照票 37 先例）：闸只查顶层
必备键 `target`/`created`/`records` 在场（json 类 check_json_artifact 前置登记同款）；
记录级 schema 与哈希失效机判由本脚本承载，闸不重复判定。

## 状态机与 verify 判定树

```
verify <target>：
  目标不存在                         → exit 2 配置错
  审记文件不存在                     → exit 1 无审记=待人审（不重建）
  审记不可解析 / 头部结构坏          → exit 1 审记损坏=待人审（不重建）
  records 为空                       → exit 1 待人审
  任一记录缺必备字段 / verdict 非法值
  / 打回缺 routing / sha256 非 hex   → exit 2 审记非法（配置错，附逐条脏点定位）
  最新记录 verdict=打回              → exit 1 未通过（附 routing，整改后再审）
  最新记录 verdict=已审：
    现算 sha256 == 锚定 reviewedSha256 → exit 0 已审且哈希一致
    现算 sha256 != 锚定               → exit 1 审记失效（再生过）→ 回落待人审
                                        （零宽限，裁决点 5；旧审记保留可查）
```

生命周期（design §2.4 走查对应）：待审（无审记/失效/打回）→ `approve` 落已审锚定 →
真源变更再生（字节变，`--check` 仍绿——防陈旧闸不受人审影响，这正是旁档设计的意义）
→ `verify` 自动失效回落待人审 → 对照 diff 再审 → `approve` 追加新记录（旧记录保留，
历史可查）。

### 退出码表

| 码 | 含义 |
|---|---|
| 0 | 已审且哈希一致 |
| 1 | 失效（生成物再生/被改）/ 审记缺失 / 审记损坏（不可解析）/ 无记录 / 最新裁决为打回 |
| 2 | 配置错：目标不存在 / reject 缺 routing / 审记记录违约（缺必备字段、verdict 非法值、打回缺 routing、sha256 非 hex）/ 用法错误 |

审记损坏分两档（票 45 AC 表与 design §3.4 的合成裁决，勿混）：
- **不可解析**（非 JSON / 头部结构坏）= 丢失级损坏 → 按「待人审」处理 exit 1，宁多审
  一次，不重建（design §3.4 #2）；
- **可解析但违约**（记录缺必备字段 / verdict 非法值等）= 配置错 → exit 2 fail loud
  （票面 AC2a/AC2b 钉 exit 2；审记整体不可信，不跳过脏记录取旧值）。
两档共同点：verify 只读、不重建审记；approve/reject 遇损坏/违约拒绝追加（防伪造历史）。

## 边界语义（随票定与裁决点汇总）

1. **reviewedBy = git 身份**（design 开放问题③随票定）：`git config user.name`，取不到
   写 `"unknown"` 并 stderr 提示；reviewedCommit 同理（非仓/git 缺席 → `"unknown"`，
   sha256 锚定不受影响）。单人仓 git 身份足够（PRD 决策 1）。
2. **审记追加不覆盖**：状态演进只靠追加新记录，旧记录永不改写；init 幂等不重建；
   损坏审记任何动作都不重建（可以缺，不可以编）。
3. **目标绑定 = 旁档文件名 + 哈希锚定**：审记不做 target 字段与实参的路径机判（同内容
   哈希必同字节，跨目标错绑由哈希兜底必红）；旁档文件名 `<目标去扩展>-review.json`
   即绑定面。
4. **打回必须当场开单**（裁决点 6）：routing 强制非空；建议带分道前缀
   （业务错:…/工程错:…），分道前缀不做机判（路由表分道裁决归人，脚本只拦"没去向"）。
5. **published 态只预留不实现**（design 开放问题②裁决）：本票无发布态字段；未来出现
   真发布动作走票增字段。
6. **不进 ci.sh 硬闸**（design §5 不做 4）：人审是节奏性动作；接线（三生成物审记指针、
   档位登记、收官清单 verify 命令）在票 46。

## 出厂集断言表（真源 = tickets/45 AC 表；断言面 = fixtures/review-gate/assertions.json）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1 读面 | 预置失效审记（records-stale/，锚定哈希≠靶件现算哈希） | verify exit 1 报失效回落待人审 |
| AC1 写面 | RG-AC3 探针：approve 后手改目标字节（再生负变体） | verify exit 1 报失效 |
| AC2a | 预置缺必备字段审记（records-missing-field/ 缺 reviewedSha256） | exit 2 审记非法 |
| AC2b | 预置 verdict=「已合入」（records-badverdict/） | exit 2 审记非法 |
| AC2c | reject 缺 --routing | exit 2（报错带开单指引） |
| AC3a 读面 | 合法已审预置审记（records/，锚定=靶件真实 SHA256） | verify exit 0 |
| AC3a 写面 | RG-AC3 探针：tempfile 临时 git 仓 init→approve→verify | exit 0，锚定真 HEAD+真 sha256 |
| AC3b | RG-AC3 探针：失效后重新 approve→verify | 恢复 exit 0，旧审记保留可查（2 条记录） |
| AC4 | RG-AC4 探针 + CI 第 4 闸 | review-record 类在档（exports/reviews/*.json，必备键 target/created/records）、归档闸绿 |
| AC5 | `bash tools/ci.sh` | 四闸全绿 |
| reject 正链 | RG-REJECT 探针：reject 带 routing→verify→重审 approve | 打回落记录→verify 红未通过态→重审恢复绿 |
| 损坏读面 | records-corrupt/（不可解析） | verify exit 1 按待人审、不重建 |

单测层（tools/test_review_gate.py，36 例，tempfile 全覆盖）：四动作全链、记录字段真值、
git 缺席降级双路（非仓目标 / `_git` 注入失败 / 仅缺 user.name）、损坏审记拒绝重建与
拒绝追加、schema 违约逐字段 exit 2、`--json` 机读面、审记路径解析。
