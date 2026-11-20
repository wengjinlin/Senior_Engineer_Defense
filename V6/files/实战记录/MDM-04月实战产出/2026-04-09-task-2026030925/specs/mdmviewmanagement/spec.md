## ADDED Requirements

### Requirement: SQL分片多实例并行处理
系统 SHALL 支持基于SQL分片条件的多实例并行处理。每个实例根据自身实例编号取模 `shardTotal` 得到 `shardIndex`，查询SQL MUST 包含 `MOD(nZhuid, #{shardTotal}) = #{shardIndex}` 条件，确保每个实例仅处理属于自己的分片数据，各实例间无数据交叉。

实例编号获取 MUST 通过IP+端口取模方式计算：`Math.abs((IP + ":" + port).hashCode() % shardTotal)`。

`shardTotal` MUST 支持通过配置项设置，默认值为5，以适配不同部署环境的实例数量。

#### Scenario: 正常分片查询
- **WHEN** 5个实例同时执行扩建任务，shardTotal=5
- **THEN** 每个实例仅查询到 MOD(nZhuid, 5) 等于自身 shardIndex 的数据，所有分片数据合起来为全量待处理数据，无交叉无遗漏

#### Scenario: 实例数变化
- **WHEN** 实例数从5个扩容到7个，shardTotal配置更新为7
- **THEN** 所有数据按 MOD(nZhuid, 7) 重新分配到7个分片，每个实例处理新的分片数据，已成功处理的数据因幂等校验不会重复处理

#### Scenario: 单实例部署
- **WHEN** 开发环境仅部署1个实例，shardTotal=1
- **THEN** 该实例的 shardIndex=0，查询 MOD(nZhuid, 1)=0 即全量数据，等同于不分片

---

### Requirement: 线程池并发扩建处理
系统 SHALL 在单个实例内使用固定大小的线程池并发处理扩建操作。线程池大小 MUST 通过配置项设置，默认值为2，以控制单实例并发压力。

每条物料的扩建 MUST 在独立事务中执行（`@Transactional`），单条失败 MUST NOT 影响其他物料的处理。

扩建处理 MUST 调用已有的 `factory4211ExtensionSingle` 方法，该方法包含：双重校验（是否已存在4211视图）、创建4211工厂视图、复制非SAP视图字段、执行审核。

系统 MUST 记录每条物料的处理结果（成功/失败），任务结束后输出汇总日志。

#### Scenario: 正常并发处理
- **WHEN** 实例分片查询到100条待扩建物料，线程池大小为2
- **THEN** 2个线程并发处理，每条物料独立事务，成功处理的物料记录到成功列表，失败的记录到失败列表

#### Scenario: 单条扩建失败不影响其他
- **WHEN** 某条物料在扩建过程中抛出异常
- **THEN** 仅该条物料的事务回滚，线程池继续处理剩余物料，失败信息记录到日志

#### Scenario: 幂等校验防止重复扩建
- **WHEN** 同一条物料因分片规则变化被重复处理
- **THEN** factory4211ExtensionSingle 的双重校验检测到4211工厂视图已存在，返回成功并跳过，不产生重复数据

## MODIFIED Requirements

### Requirement: 4211扩建定时任务执行方式
4211工厂扩建定时任务 `factory4211ExtensionAuto` 的执行方式 SHALL 从"单实例分布式锁+全量处理"改为"多实例分片并行+线程池并发"。

系统 MUST 移除原有的分布式锁逻辑（`factory-4211-extension-lock`），因为每个实例独立处理自己的分片数据，无需竞争。

系统 MUST 移除Kafka方案相关代码，包括：`Mdm4211ExtensionProducer`、`Mdm4211ExtensionConsumer`、`KafkaTopicConfig`、`Mdm4211ExtensionMessage`（如果仅被Kafka方案使用）。

系统 MUST 恢复 `application.yml` 中的Kafka配置为原值（移除4211扩建相关的Kafka配置项）。

任务执行频率 SHALL 保持每30分钟（`0 0/30 * * * ?`）。

#### Scenario: 定时任务正常触发
- **WHEN** 定时任务触发，5个实例同时执行
- **THEN** 5个实例各自查询自己的分片数据，使用线程池并发处理，无需获取分布式锁，无竞争等待

#### Scenario: 清理Kafka方案代码
- **WHEN** 实施分片方案
- **THEN** Kafka相关文件（Producer、Consumer、TopicConfig）被删除，application.yml中4211相关的Kafka配置被移除，Mdm4211ExtensionMessage实体类若仍被复用则保留
