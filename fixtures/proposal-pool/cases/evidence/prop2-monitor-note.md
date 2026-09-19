# 监督巡检告警摘录 · planOutput 负值

- 告警编号: 告警-1（出厂集固定样本）
- 巡检项: 数值属性值域
- 现象: planOutput（配产量，吨）存在负值行，模型未声明值域约束，闸上无拦截。
- 对照: 同元素 waterCut 已有「含水率值域」refRules（value >= 0 and value <= 100），planOutput 属同类缺口。
- 建议: 值域下沉为 refRules（详见提案 PROP-BOHAI-002）。
