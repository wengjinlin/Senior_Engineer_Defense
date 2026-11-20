## 1. Mapper层：新增分片查询

- [x] 1.1 `MdmViewAllMapper.java` 新增方法 `selectMaterialsFor4211ExtensionByShard(@Param("shardIndex") int shardIndex, @Param("shardTotal") int shardTotal)`
- [x] 1.2 `MdmViewAllMapper.xml` 新增对应SQL，在原 `selectMaterialsFor4211Extension` 查询基础上增加 `MOD(nZhuid, #{shardTotal}) = #{shardIndex}` 分片条件

## 2. Service层：实现单物料扩建方法

- [x] 2.1 `IMdmViewManagementService.java` 新增接口方法签名 `Result<?> factory4211ExtensionSingle(Mdm4211ExtensionMessage message)`
- [x] 2.2 `MdmViewManagementServiceImpl.java` 实现 `factory4211ExtensionSingle` 方法：从现有 `factory4211Extension(List<MdmViewAll>)` 批处理逻辑中提取单条处理，包含4211视图存在性校验（幂等）、创建4211工厂视图、复制非SAP字段、单条审核，标注 `@Transactional(rollbackFor = Exception.class)`

## 3. 定时任务重构：分片并行+线程池并发

- [x] 3.1 `MdmViewManagementAuto.java` 注入 `DiscoveryClient`、`PlatformTransactionManager`（用于构造 TransactionTemplate）、线程池大小配置 `@Value("${cusparam.4211.thread-pool-size:2}")`
- [x] 3.2 `MdmViewManagementAuto.java` 重构 `factory4211ExtensionAuto()` 方法：通过 DiscoveryClient 获取服务实例列表并排序计算 shardIndex/shardTotal，移除分布式锁逻辑，调用新的分片查询方法获取数据，使用 `Executors.newFixedThreadPool` + `CountDownLatch` 并发处理每条物料，每个任务通过 `TransactionTemplate` 执行独立事务调用 `factory4211ExtensionSingle`，记录成功/失败数量并输出汇总日志

## 4. 配置

- [x] 4.1 `application.yml` 新增配置项 `cusparam.4211.thread-pool-size: 2`

## 5. 清理Kafka方案代码

- [x] 5.1 检查并删除 `Mdm4211ExtensionProducer`、`Mdm4211ExtensionConsumer`、`KafkaTopicConfig` 等Kafka相关文件（如存在）
- [x] 5.2 检查 `Mdm4211ExtensionMessage` 是否仅被Kafka方案使用，若是则删除；若被 `factory4211ExtensionSingle` 复用则保留
- [x] 5.3 检查 `application.yml` 中4211扩建相关的Kafka配置项并移除（如存在），恢复Kafka配置为原值
