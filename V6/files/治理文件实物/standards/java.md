# Java 编码规范 (java.md)

> 基于代码实测：323 Entity / 279 Mapper / 182 Controller / 171 ServiceImpl。
> 不是阿里巴巴规范的复述，是项目**实际做法 + 边界红线**。

## 现状实测

| 维度 | 项目实际 | 数量 |
|------|---------|------|
| `@Slf4j` | 主流日志方式 | 182 文件 |
| `@Data` Lombok | Entity / DTO / VO 必备 | 323+ |
| `@RequiredArgsConstructor` | **0 处**（构造器注入几乎不用） | 0 |
| Stream API | 大量使用，业务转换/过滤主流 | 826 处 |
| `Optional` | 大量使用（多用于链式空判断） | 数百处 |
| 异常 | `RuntimeException` / `DatabaseException` 抛出，`GlobalDefaultExceptionHandler` 兜底 | 1 全局 |
| `new Date()` | Joda-Time 与 `System.currentTimeMillis()` 并存 | — |

## 🔴 必须遵守（红线）

1. **JDK 1.8**：禁用 `var`、record、switch 表达式（JDK 14+）
2. **包结构**：`com.sunny.modules.<业务域>.{controller,service,service/impl,dao,entity,dto,enums}`
3. **类名后缀**：`Controller` / `ServiceImpl` / `Mapper` / `Entity`（无后缀） / `DTO` / `VO`
4. **Service 接口**：`IXxxService` 前缀 I，实现 `XxxServiceImpl extends BaseServiceManager`
5. **方法命名**：业务命名优先，CRUD 用 `insert/update/delete/get/findXxx/selectForPage`（见 naming.md）
6. **异常**：业务层抛 `RuntimeException` 或 `DatabaseException`，**禁止 try-catch 吞异常**；Controller 不 try-catch
7. **日志**：`@Slf4j` + `log.error("xxx 失败 param={}", param, e)`（异常对象放最后，占位符 `{}` 不字符串拼接）

## 🟢 推荐做法

- DTO ↔ Entity 转换：简单用 `BeanUtils.copyProperties`，复杂手写 setter
- 集合判空：用项目工具 `ListCheckUtil.isNotEmpty(list)` 而非 `list != null && list.size() > 0`
- 时间：用 Joda-Time `DateTime.now(DateTimeZone.forID("Asia/Shanghai"))`，跨时区显式声明
- 字符串：`String.format` 或 `Message.format`，避免 `+` 拼接
- 集合返回空值：用 `Collections.emptyList()` 而非 `null`
- Stream：单表达式用 Stream，多步骤循环用 for（IDE 友好）

## ⚫ 禁止做法

| ❌ 禁止 | 原因 |
|--------|------|
| `@Controller + @ResponseBody` | 项目统一 `@RestController` |
| 业务模块 `@Autowired` 跨模块别 Service | 跨模块走 Feign，参考 modules.md 边界红线 |
| `try-catch` 后 `e.printStackTrace()` | 用 `log.error("msg", e)`；吞异常会被 GlobalDefaultExceptionHandler 漏掉 |
| `new FileInputStream` 不 close | 用 try-with-resources |
| 静态可变字段（`static Map` 写缓存） | 项目有 Redis Sentinel，用 `@Cacheable` 或 RedisTemplate |
| `SimpleDateFormat` 共享实例 | 线程不安全；用 `FastDateFormat` 或 Joda `DateTimeFormatter` |
| 业务代码 `Thread.sleep` | 用异步任务 / Kafka |
| 在 Controller 写业务逻辑 | 只做参数校验 + 调 Service + 包装 Result |

## 建议改进（现状标记）

| 现状 | 建议 | 阻力 |
|------|------|------|
| `@Autowired` 字段注入 999 处 | 新代码用构造器注入（循环依赖编译期暴露） | 父类 BaseServiceManager 强制字段注入 |
| `@ConfigurationProperties` 仅 2 处 | 配置类集中用 `@ConfigurationProperties` 而非散落 `@Value` | 历史代码迁移成本 |
| 测试覆盖近 0 | 新增 Service 必须带单测（见 testing.md） | 全量补单测不现实 |
