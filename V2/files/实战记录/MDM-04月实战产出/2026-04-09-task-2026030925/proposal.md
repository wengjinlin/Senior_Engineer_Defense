## Why

4211工厂自动扩建定时任务存在严重的性能瓶颈：分布式锁导致仅1个实例执行（5实例中4个空闲）、万条物料一次性加载到内存、整个批处理在单个大事务中运行。之前已实施的Kafka方案（方案A）引入了较重的外部依赖，现在需要采用**方案B（线程池分片模式）**替代——不引入新依赖，通过SQL分片让5个实例并行处理各自负责的数据，每个实例内部使用线程池并发执行，每条物料独立事务。

## What Changes

- **SQL增加分片条件**：`MdmViewAllMapper.xml` 中的查询SQL增加 `MOD(nZhuid, #{shardTotal}) = #{shardIndex}` 条件，让每个实例只查自己负责的分片数据
- **Mapper接口新增分片参数**：`MdmViewAllMapper.java` 新增 `shardIndex`、`shardTotal` 参数
- **定时任务改造**：`MdmViewManagementAuto.java` 的 `factory4211ExtensionAuto()` 方法改造为：
  - 获取当前实例编号（通过IP+端口取模）
  - 移除分布式锁（各实例独立处理自己的分片，无需竞争）
  - 传入分片参数查询数据
  - 使用线程池并发处理每条物料，每条物料独立事务
- **复用已有单物料扩建方法**：`MdmViewManagementServiceImpl.factory4211ExtensionSingle()` 已实现，直接复用
- **移除Kafka方案相关代码**：删除 `Mdm4211ExtensionProducer`、`Mdm4211ExtensionConsumer`、`KafkaTopicConfig` 等Kafka相关文件，恢复 `application.yml` 中的Kafka配置

## Capabilities

### New Capabilities
- `mdmviewmanagement`: 基于SQL分片的多实例并行处理能力，通过实例编号取模分配数据分片，实现无锁并行执行
- `mdmviewmanagement`: 线程池并发扩建能力，在单个实例内使用固定大小线程池并发处理多个物料的扩建操作

### Modified Capabilities
- `mdmviewmanagement`: 4211扩建定时任务的执行方式从单实例全量处理改为分片并行处理

## Impact

- **代码影响**：
  - `MdmViewAllMapper.xml` — 查询SQL增加分片条件
  - `MdmViewAllMapper.java` — 接口方法签名变更（新增参数）
  - `MdmViewManagementAuto.java` — 定时任务逻辑重构
  - `MdmViewManagementServiceImpl.java` — 复用已有方法，可能需微调
  - 删除Kafka相关文件（Producer、Consumer、TopicConfig、Message）
- **配置影响**：`application.yml` 中Kafka相关配置需恢复原值
- **依赖影响**：无新依赖引入，移除对Kafka的运行时依赖
- **API影响**：无对外API变更
- **数据库影响**：无表结构变更
- **运维影响**：无需Kafka Topic，扩缩容时需注意分片规则变化（需幂等校验兜底）
