# 使用方消费用例单（skill-pack-gen · 票 36）

技能包（exports/skillpkg/<域>/ 的 SKILL.md+skillpack.json）交给人审后的使用方
（对话技能装配方）。成稿润色归使用方；本包只供确定性骨架。四个消费场景与
出厂集断言一一对应：

## 场景 1 · 三件套齐读（AC1 断言①）

读 SKILL.md：frontmatter（name/domain/slice-models/citation-prefixes/人审
状态）→ 一、工序路由（问答四步·静态化）→ 二、口径问答卡 → 三、引用纪律与
拒答边界。机读面读 skillpack.json（slice/calibers/glossary/citationDiscipline
镜像）。任何一节缺失 = 拒收。

## 场景 2 · 口径问答同源（AC1 断言②）

口径问答卡问题样例/命中 ID 集/口径要点与语义服务 CORE 行为同源：抽问
「日产量口径是什么？」，core 命中 ID（CORE-01 冻结=AGG-BOHAI-002 /
BH-BOHAI-QueryWellDailyOutput / QR-BOHAI-001 / RULE-BOHAI-003 /
RULE-BOHAI-004）逐个 ∈ skillpack.json 口径卡 QR-BOHAI-001 的 hitIds。
使用方成稿时对命中 ID 逐条挂引用，不得引入 hitIds 之外的口径元素。

## 场景 3 · 防陈旧再制（AC2 断言①②）

入库副本禁手改。本体域演进后再制：

```
python3 tools/skill_pack_gen.py ontology/bohai --models M1,M2,M3,M7,GLS \
  --check exports/skillpkg/bohai/SKILL.md
```

一致 exit 0；不一致 exit 1（副本陈旧或被手改）——用 --out 重新生成落盘。
双跑字节一致、零时间戳由生成器单测背书。

## 场景 4 · 负变体拒收（AC3 断言①②）

- 域缺声明模型文件（剃 m3 副本）→ exit 2「缺声明模型 M3」，不产残包；
- 声明含 build-contract 模型（--models M1,MU）→ exit 2「声明含非
  business-core 阵营模型 MU」（检索面纪律的生成器侧延伸，camp 判定在先）。

两类报错都是配置错误拒绝服务，不是可跳过的警告——技能包切片宁缺毋残。
