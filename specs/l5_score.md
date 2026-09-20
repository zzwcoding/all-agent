# spec · l5_score（L5 评分器确定性骨架）

触及: tools/l5_score.py、fixtures/l5-scoring/、fixtures/semantic-service/rubrics/（样例，票 43 填充）

> 断言真源：tickets/42-L5评分器骨架.md AC 表 + fixtures/l5-scoring/assertions.json（L5- 前缀）。
> 设计注源：docs/design-l5-scoring.md §3.3/§4/§5.3/§9（裁决①：评分器 = 运行时子 agent 注入，本脚本零模型调用）。

## 定位

L5（LLM 评分级）的确定性骨架：**LLM 打分、脚本判定**。评分由运行时子 agent 产出评分
结果 JSON 文件（票 44 接线派发；3 采样 = 3 次独立子 agent 派发），`l5_score.py` 只消费
文件——格式校验 → 中位聚合 → disqualifier 一票否决 → 通过线判定 → 报告落盘 → 退出码。
mock 注入 = 预置评分结果 JSON 文件（fixtures/l5-scoring/results-*）。零模型调用、零外部
服务，PyYAML 与 tools/ 现存闸脚本同水位。

## CLI 契约

```
python3 tools/l5_score.py --rubrics <目录> --results <目录或文件...> [--out <报告.md>] [--json]
```

- `--rubrics`：rubric 目录，逐份校验 `*.yaml`/`*.yml`（递归）。
- `--results`：评分结果 JSON，目录（递归取 `*.json`）或文件，可多个；同 `question_id`
  多份 = 多采样，**每问必须恰 3 份**（多/少/缺 = 配置错）。
- `--out`：报告落盘 `.md` + 同名 `.json` 机读伴生；同名已存在加 `-2`/`-3` 序号
  （md 与同名 json 都空闲才占用），**不覆盖旧留痕**（meta_probe 体检留痕同款惯例）。
  缺省只打 stdout（与落盘字节一致）；`--json` 时 stdout 只含机读 JSON。
- 退出码：`0` 通过线全绿 / `1` 红（低于通过线或触发 disqualifier）/ `2` 配置错
  （rubric 非法、评分文件无效、用法错误）。错误走 stderr，报告走 stdout。

## 评分请求/结果 JSON 协议（票 44 子 agent 派发契约以此为准，L0 定稿）

```json
// 评分请求（编排侧 → 评分子 agent；本脚本不消费请求侧）
{"question": "...", "reference_answer_path": "...", "candidate_answer_path": "...", "rubric_path": "..."}

// 评分结果（评分子 agent 落盘 → 本脚本消费）
{"question_id": "Q1",
 "dimensions": [{"id": "semantic_fidelity", "score": 4, "reason": "…非空一句"}],
 "disqualifier_triggered": false}
```

## rubric 格式（YAML；与 l5_score.py 校验互为镜像）

```yaml
question_id: Q1                                # 必填非空；目录内唯一
reference: ../expected-answers/ac1-xxx.md      # 必填；相对本 rubric 文件解析，须真实存在
scoring_prompt: |                              # 可选（校验忽略）——评分提示词载体随 rubric
  …                                            #   进 fixtures（design 开放问题④随票 42 定）；
                                               #   提示词改 = 改出厂集 = 走票
dimensions:                                    # 必填非空
  - id: semantic_fidelity                      # 必填非空；份内唯一
    weight: 2                                  # 必填正整数（不加权归一，见注意事项）
    anchors:                                   # 必填：5/3/1 三档非空字符串锚定例（键可写 "5"）
      5: "…"                                   #   锚 5 例引参照答案原文（内容质量归票 43）
      3: "…"
      1: "…"
disqualifiers: ["…"]                           # 可选；语义级一票否决项描述（非空字符串列表）
```

### rubric 校验三红（AC1，红 = exit 2「rubric 非法」附文件与脏点定位）

| # | 红因 | 判定 |
|---|---|---|
| 1 | 某维缺 anchors，或 anchors 缺 5/3/1 任一档，或锚定例为空串 | `维度 <id> 缺锚定例（…缺档: …）` |
| 2 | weight 非正整数（0/负数/浮点/字符串/布尔均红） | `维度 <id> weight 非法（须正整数）` |
| 3 | reference 解析后文件不存在 | `reference 不存在: <ref>（解析为 <绝对路径>）` |

附加结构红：YAML 不可解析 / 顶层非映射 / 缺 question_id 或 dimensions / 维度 id 份内重复
/ question_id 目录内重复 / disqualifiers 形态非法。

## 评分结果校验（AC2，违规 = exit 2「评分无效」附脏点定位，不进聚合）

| 红因 | 判定信息 |
|---|---|
| 文件不是合法 JSON / 顶层非对象 | `不是合法 JSON` |
| 维度 id 集与 rubric 不完全一致（漏维/多维/重复维） | `缺维度 <id>` / `多出维度 <id>` / `维度 id 重复` |
| score 非 0–5 整数（浮点/字符串/布尔均红） | `score 越界: <值>（合法 0–5 整数）` |
| reason 缺失或空白 | `reason 缺失或为空` |
| disqualifier_triggered 缺失或非布尔 | `disqualifier_triggered 缺失或非布尔` |
| question_id 无对应 rubric | `孤儿评分` |
| 每问采样 ≠ 3（0 份/2 份/4 份） | `缺评分采样` / `采样数不是 3` |

校验先于聚合：任一脏点 = 全体不进聚合（先红后算，不部分聚合）。

## 聚合与判定（先算术，后结论）

1. 逐问逐维 3 采样取**中位**；
2. 分差 max−min ≥2 → 该问标**「不稳定」**（只标记不判死；按 design §4.3 升级第二模型
   仲裁，票 44 接线）；
3. 任一采样 `disqualifier_triggered=true` → 该问**按 0 分计且一票否决**；
4. **总分 = 该问各维 score×weight 加权和**（weight 不常态化，L0 定稿照办）；
5. 通过线三条件**同时满足**才 exit 0：
   - 条件① 每问总分 ≥3；
   - 条件② 问总分集的中位 ≥4.0；
   - 条件③ 无 disqualifier 触发问。

### 退出码表

| 码 | 含义 |
|---|---|
| 0 | 三条件全绿（不稳定标记不影响退出码） |
| 1 | 红：任一条件不满足（含 disqualifier 一票否决） |
| 2 | 配置错：rubric 非法 / 评分文件无效 / 用法错误（rubrics 目录不存在、采样数≠3 等） |

## 报告与留痕

- `--out <路径>.md` → MD + 同名 `.json` 双落盘；同名加 `-2`/`-3` 序号不覆盖；正式留痕落
  `docs/meta/l5-评分-<日期>.md`（布局表 docs 条目 `meta/*.md`/`meta/*.json` 已收，票 42
  实跑归档闸确认）。留痕带生成时间戳（留痕不是 golden）。
- MD 内容：结论行 + 三条件逐条 PASS/FAIL（FAIL 附具体问与数值）+ 逐问明细（逐维
  权重/三采样/中位/分差表 + 判定行：稳定/不稳定/一票否决）+ 不稳定升级提示 + 红灯路由
  去向（只报告不修复，分道人工裁决）。
- 红灯三分道（design §4.4，静态指引 + 路由表指针）：语义内容错 → 业务错道（提案池）；
  话术/工序错 → 工程错道（tickets/）；rubric 写错 → 元模型错道（改 rubric 走票）。
- L5 留痕独立于 meta_probe 体检（design §6.4：体检是纯机判硬闸，不被软闸污染）。

## 注意事项（L0 定稿的边界语义）

1. **加和不常态化**：总分与中位都作用在 score×weight 加权和量纲上，门槛数值（≥3、
   ≥4.0）的松紧随 rubric 权重集取值变化——权重集是 rubric 内容 Owner 的定稿责任
   （票 43 定 12 问 rubric 时须知）；不做的归一化如后续需要，走票改本表+实现。
2. **维度 0 分是合法形态**（无 disqualifier 标记时）：「无 0 分」条件指问级
   disqualifier（按 0 分计），维度 0 分由条件①/②的加和自然兜底。
3. **不稳定不判死**：分差 ≥2 只标记并提示仲裁升级；仲裁派发归票 44。
4. **本脚本零模型调用**：消费的评分结果文件由票 44 的子 agent 派发协议产出；
   在那之前只有出厂集 mock 注入一种合法来源。
5. `fixtures/semantic-service/rubrics/` 样例（Q1）是票 43 的格式样板（真参照答案相对
   引用形态），票 43 填充 12 份真 rubric 时以此为准并接入出厂集断言；本票不改
   semantic-service 既有 questions/expected-answers/assertions。

## 出厂集断言表（真源 = tickets/42 AC 表；断言面 = fixtures/l5-scoring/assertions.json）

| 断言 | 给定 | 期望 |
|---|---|---|
| AC1a | rubric 整缺某维 anchors（negative-rubrics/missing-anchors） | 红（rubric 非法，缺锚定例） |
| AC1b | rubric 权重为 0（negative-rubrics/bad-weight） | 红（rubric 非法，weight） |
| AC1c | rubric reference 指向不存在文件（negative-rubrics/ghost-reference） | 红（rubric 非法，reference 不存在） |
| AC2 | 评分 JSON 漏维 / score=6 越界 / 混入非 JSON 文本（results-dirty-* 三形态） | exit 2 评分无效 |
| AC3a | mock 三采样 [5,3,4]（results-unstable Q1 semantic_fidelity） | 中位 4 |
| AC3b | mock 三采样分差 ≥2（同上） | 报告标「不稳定」，结论仍 PASS（不判死） |
| AC3c | mock 含 disqualifier_triggered=true（results-disq Q1 第 2 采样） | 该问 0 分、一票否决、整体红 |
| AC4a | 单问总分 <3（results-lowtotal Q3 总分 1；中位 12≥4.0、无 disq） | exit 1（条件①单点红） |
| AC4b | 全集中位 <4.0（results-lowmedian 总分集 [3,3,13]；单问均 ≥3、无 disq） | exit 1（条件②单点红） |
| AC4c | 全绿样本（results-green：总分 [22,12,13]、中位 13） | exit 0 + md/json 报告双落盘 |
| AC5 | CI | 四闸全绿 |
