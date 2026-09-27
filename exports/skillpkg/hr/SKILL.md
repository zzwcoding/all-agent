---
name: hr-semantic
description: "hr 人力资本域（MySQL employees 示例库）（hr）可对话技能包骨架——口径问答/对象问答/术语问答；tools/skill_pack_gen.py 自本体切片确定性装配（零 LLM 零时间戳）"
domain: hr
slice-models: ["M1", "M3", "GLS"]
citation-prefixes: ["AGG-", "ASSOC-", "DICT-", "RULE-", "GLS-"]
status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）
---

# hr 人力资本域（MySQL employees 示例库） 可对话技能包（skillpkg · hr）

status: 待Owner人审（生成物禁手改，可再生；审记旁档exports/reviews/，review_gate.py-verify判失效）

- 生成器: tools/skill_pack_gen.py（确定性装配：本体切片 + schema 注册表 camp 面，零 LLM 零时间戳）
- 本体来源: ontology/hr（profile=v9-full）
- 切片声明: --models M1,M3,GLS（3 模型，全部 camp=business-core）
- 防陈旧: python3 tools/skill_pack_gen.py ontology/hr --models M1,M3,GLS --check exports/skillpkg/hr/SKILL.md

## 一、工序路由（问答四步·静态化）

> 问答纪律的静态化表述：检索瀑布运行时真源见语义服务（skills/semantic-service）；成稿润色归人审后的使用方，本包只供确定性骨架。

- ① 显式锚定: 问句带 @ID 时按前缀定模型定阵营（先阵营后存在性）：面内确认存在并反向收名下行为；面外拒答，不返回该元素任何细节。
- ② 名称解析: 无锚定/锚定失败降级：候选词对 name/alias/属性标签/术语确定性分层匹配，不猜不模糊；多义列候选请锚定修饰词，不擅自合并。
- ③ 闭包装配: 命中元素沿引用/影响两向装配证据集（承载/行为/规则/查询出口/术语），只引用装配集内 ID，装配指令可复现。
- ④ 可拒答: 面外/仓内没有/禁用词三分支如实拒答：缺件分层说明+近邻指路；禁用词给替代口径真实 ID；写意图走提案流程。

## 二、口径问答卡（M7 逐口径·与语义服务 CORE 同源）

未声明 M7——无口径问答卡（口径卡命中集须与语义服务 CORE 同源，装配须 M1/M2/M3/M7 齐备）。

## 三、引用纪律与拒答边界

- ID 引用格式: 回答必带元素 ID 引用（前缀形态真实 ID，如 AGG-BOHAI-002），逐条可经 `python3 tools/graph_index.py <域> --query <ID> --json` 复核；成稿须含「本回答引用的元素 ID」清单节，与正文 ID token 双向一致（tools/check_citations.py 检具）。
- camp 面外: SCR-（MU UI 模型，camp=build-contract） → 面外拒答，不返回该面任何细节（建造契约由 build 侧消费方在建造链路消费）
- 切片外: BH-（M2 行为模型，camp=business-core）；ACTOR-/ROLE-/PERM-（M5 主体模型，camp=business-core）；FLOW-（M6 流程模型，camp=business-core）；QR-/RPT-（M7 查询统计与报表模型，camp=business-core） → business-core 但未入本包切片，按缺件如实说明不硬凑
- 禁用词: 无禁用术语（GLS status 全非禁用）
- 可拒答声明：仓内没有就说明缺什么，绝不编造；写意图一律回「走提案流程」（进仓走 MR + 语义 CI）；本包只读——运行面语义消费，不做本体写入。
