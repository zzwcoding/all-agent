# Kafka Topic 设计文档

## 一、Topic 基础信息

| 参数 | 值 | 说明 |
|------|-----|------|
| Topic 名称 | `flume_kafka_topic` | 采集医院业务日志 |
| 分区数 | 3 | 三节点并行消费，提升吞吐 |
| 副本因子 | 2 | 单节点宕机不丢数据 |
| 最小同步副本 | `min.insync.replicas=1` | 实际测试调为1，生产环境建议2 |
| 清理策略 | delete | 默认策略，过期自动删除 |
| 消费组 | `flume-consumer-group` | Flume 专用，支持断点续传 |

## 二、设计说明

1. **分区数=3**：集群3个节点，每个Broker可承担1个Leader分区，实现并行读写
2. **副本因子=2**：Leader + 1个Follower，保证HA；若设为3会占满所有节点
3. **消费方案**：Flume 作为消费者，从 `earliest` 起始，重启后继续从 offset 消费
4. **数据流转**：

```
业务模拟日志 → Kafka Producer → Topic(flume_kafka_topic)
                                        │
                                  Flume Consumer
                                        │
                                        ▼
                              HDFS /flume/flume/kafka/YYYYMMDD/
```

## 三、创建命令

```bash
/opt/kafka/bin/kafka-topics.sh --create \
  --bootstrap-server 192.168.100.200:9092,192.168.100.201:9092,192.168.100.202:9092 \
  --topic flume_kafka_topic \
  --partitions 3 \
  --replication-factor 2
```

## 四、验证命令

```bash
# 查看 Topic 详情
/opt/kafka/bin/kafka-topics.sh --describe --topic flume_kafka_topic \
  --bootstrap-server 192.168.100.200:9092

# 命令行生产者（测试用）
echo "test-message-$(date +%H:%M:%S)" | \
  /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server 192.168.100.200:9092 \
  --topic flume_kafka_topic

# 命令行消费者（验证用）
/opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server 192.168.100.200:9092 \
  --topic flume_kafka_topic \
  --from-beginning --max-messages 5
```

## 五、Topic 分区详情

```
Topic: flume_kafka_topic   PartitionCount: 3   ReplicationFactor: 2
  Partition: 0   Leader: 1   Replicas: 1,0   Isr: 1,0
  Partition: 1   Leader: 0   Replicas: 0,2   Isr: 0,2
  Partition: 2   Leader: 2   Replicas: 2,1   Isr: 2,1
```

三个分区 Leader 均匀分布在三个节点上，负载均衡。

## 六、Flume 消费者配置（关联文件）

Flume 通过 `kafka-to-hdfs.conf`（`ReportCharts/configs/flume/kafka-to-hdfs.conf`）消费该 Topic：

```properties
a1.sources.kafkaSource.type = org.apache.flume.source.kafka.KafkaSource
a1.sources.kafkaSource.kafka.topics = flume_kafka_topic
a1.sources.kafkaSource.kafka.consumer.group.id = flume-consumer-group
a1.sources.kafkaSource.kafka.consumer.auto.offset.reset = earliest
```
