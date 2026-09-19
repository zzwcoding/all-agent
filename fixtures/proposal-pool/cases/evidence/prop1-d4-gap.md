# 对账缺口记录 · 配产双值行（D4）

- 登记时间: 2026-09（出厂集固定样本，内容取自渤海域走查遗留疑点）
- 缺口编号: D4（AGG-BOHAI-002 描述注记同源）
- 现象: oil_production_daily 同一 (wellId, prodDate) 存在两行均带非空 planOutput，与模型复合主键声明矛盾。
- 影响: 产量完成率（planOutput 作分母）在切换日取值不定，报表口径可被双值行漂移。
- 建议: 新增校验规则拦截双值行（详见提案 PROP-BOHAI-001）；取舍策略待 Owner 裁决。
