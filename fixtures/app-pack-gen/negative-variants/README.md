# 负变体：bohai-no-m3（票 35 AC3）

bohai 副本剃掉 m3（fixtures 自管副本，防陈旧断言=CI 出厂集 AC3）。范围=生成器
声明面消费的文件：manifest.json + M1/M2/M7——生成器声明模型集为 M1/M2/M3/M7
（票 35 设计裁决），M3 缺席即触发「缺声明模型 M3」退出 2 不产残包
（specs/modules.md 边界规则 5 生成器侧首证）。

M5/M6/GLS 不是生成器输入，不入副本；真域文件演进时本副本随 bohai 对应文件
同步复制（固定输入，不自动跟踪）。副本内容与真域逐字节一致（复制时点），仅
缺席 m3——AC3 只判退出码与「缺声明模型」指认，不判副本内容新鲜度。

# 负变体：bohai-no-behaviorref（票 39 件一 AC1）

bohai 副本剃掉 M7 口径 QR-BOHAI-001 的 behaviorRef 行（fixtures 自管副本，防
陈旧断言=CI 出厂集票 39 AC1 探针）。范围=生成器声明面消费的文件：manifest.json
+ M1/M2/M3/M7 全量在场，仅 m7 的 QR-BOHAI-001 缺 behaviorRef 键——schema_check
对此副本会报 required-field（M7.behaviorRef 必填，schema.md §14），而生成器不
依赖闸先行：口径卡装配需要该键，缺键须由生成器自己干净拒绝（exit 2，stderr 定
位元素 id + behaviorRef 字样，无 traceback，不产残包文件）——字段完备的第一道
语义闸是 schema_check，但「遇残缺输入不裸崩」是生成器自己的纪律（票 39 设计裁
决 L0）。

副本内容与真域逐字节一致（复制时点），仅缺该行——AC1 只判退出码/stderr 定位/
无残包/无 traceback，不判副本内容新鲜度；真域文件演进时随 bohai 对应文件同步
复制（固定输入，不自动跟踪）。
