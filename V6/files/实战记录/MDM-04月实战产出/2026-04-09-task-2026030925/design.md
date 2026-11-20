## Context

当前4211工厂扩建定时任务（`MdmViewManagementAuto.factory4211ExtensionAuto`）采用单实例分布式锁+全量查询+大事务模式。5个部署实例中仅1个获取锁执行任务，其余4个空闲。查询SQL一次性加载所有待扩建物料，整个批处理在单个 `@Transactional` 中运行。

**当前代码现状**：
- `factory4211Extension(List<MdmViewAll>)` — 已实现，大事务批处理（ServiceImpl:5524-5593）
- `factory4211ExtensionSingle(Mdm4211ExtensionMessage)` — **未实现**，需从批处理方法中提取
- `selectMaterialsFor4211Extension()` — 已实现，无分页无分片（Mapper.xml:640-665）
- `Mdm4211ExtensionMessage` 实体类 — 已存在
- Kafka相关文件（Producer、Consumer、TopicConfig）— **未实现**，无需清理

## Goals / Non-Goals

**Goals:**
- 5个实例并行处理各自分片数据，消除单实例瓶颈
- 每条物料独立事务，单条失败不影响其他
- 实例内线程池并发，提升单实例处理吞吐
- 改动量控制在~150行，不引入新依赖

**Non-Goals:**
- 不解决跨天数据丢失问题（SQL仍查当天数据，保持现有行为）
- 不实现分页查询（分片已将数据量缩小到原来的1/5）
- 不引入Kafka、数据库任务表等外部依赖
- 不改变任务执行频率（保持30分钟）

## Decisions

### Decision 1: 实例编号获取方式 — 通过 Nacos 实例列表自动分配

**选择**: 定时任务触发时，通过 `DiscoveryClient` 查询当前服务所有健康实例，按 IP:Port 排序后取当前实例的位置作为 `shardIndex`，实例总数即为 `shardTotal`。

```java
@Autowired
private DiscoveryClient discoveryClient;

// 获取当前实例的分片信息
List<ServiceInstance> instances = discoveryClient.getInstances("sunny-mdm");
instances.sort(Comparator.comparing(i -> i.getHost() + ":" + i.getPort()));  // 排序保证各实例结果一致
int shardTotal = instances.size();
int shardIndex = -1;
for (int i = 0; i < instances.size(); i++) {
    if (instances.get(i).getHost().equals(localHost) && instances.get(i).getPort() == localPort) {
        shardIndex = i;
        break;
    }
}
```

**备选方案**:
- IP+端口取模：K8S 环境中 pod IP 不稳定（重启即变），且 `InetAddress.getLocalHost()` 在容器中返回值不可控
- 配置文件指定 shardIndex：运维成本高，扩缩容需手动改配置
- StatefulSet 序号：需要改变部署方式

**理由**: 项目已集成 Nacos（`spring-cloud-starter-alibaba-nacos-discovery`），`DiscoveryClient` 是 Spring Cloud 标准接口，零额外依赖。各实例排序结果一致，自动感知扩缩容，无需运维介入。

### Decision 2: 分片字段选择 — 使用 nZhuid（物料主ID）

**选择**: `MOD(nZhuid, #{shardTotal}) = #{shardIndex}`

**理由**:
- nZhuid 是数值型字段，取模效率高
- nZhuid 在查询结果中天然存在，无需额外JOIN
- nZhuid 分布均匀（物料ID自增），各分片数据量接近

### Decision 3: 分片参数传入方式 — 新增带分片参数的Mapper方法

**选择**: 新增 `selectMaterialsFor4211ExtensionByShard(int shardIndex, int shardTotal)` 方法，不修改原方法签名。

**理由**: 保留原方法 `selectMaterialsFor4211Extension()` 不变，避免影响其他可能的调用方。新方法在原SQL基础上增加分片条件。

### Decision 4: 线程池配置 — 使用固定大小线程池

**选择**: `Executors.newFixedThreadPool(poolSize)`，poolSize通过 `@Value` 配置，默认值2。

**理由**: 固定大小线程池控制并发压力，避免无限制创建线程。poolSize=2 时单实例内存和数据库连接压力可控。每条物料提交为独立 `Runnable`，使用 `CountDownLatch` 等待所有任务完成。

### Decision 5: 事务管理 — 编程式事务

**选择**: 使用 `TransactionTemplate`（编程式事务），在每个线程的 `Runnable` 内部执行。

**理由**: Spring的 `@Transactional` 基于ThreadLocal，多线程场景下每个线程需要独立的事务。`TransactionTemplate` 由 `PlatformTransactionManager` 构造，注入到 `MdmViewManagementAuto` 中使用。

### Decision 6: 移除分布式锁

**选择**: 完全移除 `AssLockUtils.newSimpleLock("factory-4211-extension-lock", 300)`。

**理由**: 每个实例只处理自己的分片数据（`MOD(nZhuid, total) = index`），天然无冲突，不需要锁竞争。幂等校验（`factory4211ExtensionSingle` 中的双重检查）兜底防止极端情况下的重复处理。

### Decision 7: factory4211ExtensionSingle 实现 — 从批处理方法中提取

**选择**: 从现有 `factory4211Extension(List<MdmViewAll>)` 中提取单条处理逻辑，封装为 `factory4211ExtensionSingle(Mdm4211ExtensionMessage)`。

**实现要点**:
- 检查4211视图是否已存在（幂等）
- 调用 `createForAll_wuliao_othergc` 创建4211视图
- 调用 `copyNonsapSpecifiedFields` 复制非SAP字段
- 单条审核（调用 `mdmViewAllMapper.sh`）
- 整个方法标注 `@Transactional(rollbackFor = Exception.class)`

## Risks / Trade-offs

**[扩缩容分片规则变化]** → Nacos 实例列表实时反映当前在线实例，扩缩容时 shardTotal/shardIndex 自动调整。`factory4211ExtensionSingle` 的幂等校验（检查4211视图是否已存在）兜底处理过渡期的重复数据。

**[实例宕机导致分片数据未处理]** → 需等下次定时任务触发（最长30分钟）。对于非实时性要求的扩建场景可接受。若需更快恢复，可将cron频率提高到10分钟。

**[线程池内存压力]** → poolSize默认2，最多2个并发事务，Druid连接池（max-active=10）足够支撑。可通过配置调整。

**[SQL分片条件性能]** → `MOD(nZhuid, N)` 无法使用普通索引，但查询本身已有 `TRUNC(D_SHTIME) = TRUNC(SYSDATE)` 和 `N_SHZT = 1` 过滤，数据量已限制在当天审核通过的范围内，MOD过滤影响有限。

## 改动文件清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `MdmViewAllMapper.java` | 新增方法 | `selectMaterialsFor4211ExtensionByShard(shardIndex, shardTotal)` |
| `MdmViewAllMapper.xml` | 新增SQL | 在原SQL基础上增加 `MOD(nZhuid, #{shardTotal}) = #{shardIndex}` 条件 |
| `MdmViewManagementServiceImpl.java` | 新增方法 | `factory4211ExtensionSingle(Mdm4211ExtensionMessage)` — 从批处理提取 |
| `IMdmViewManagementService.java` | 新增方法签名 | `factory4211ExtensionSingle` 接口声明 |
| `MdmViewManagementAuto.java` | 重构 | 移除分布式锁，通过 Nacos DiscoveryClient 获取分片参数，使用线程池+独立事务 |
| `application.yml` | 新增配置项 | `cusparam.4211.thread-pool-size`（默认2） |
