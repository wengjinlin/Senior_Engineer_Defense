# 测试规范 (testing.md)

> 现状：`src/test/java` **仅 2 个测试文件**（`ApplicationTest` / `MyTest`），代码被注释，覆盖率 ≈ 0%。
> 本文档定义**新增代码**的测试要求，不强制回溯补测。

## 现状实测

| 维度 | 项目实际 |
|------|---------|
| 测试文件 | 2 个（`ApplicationTest.java` / `MyTest.java`） |
| 覆盖率 | ≈ 0% |
| 测试框架 | JUnit 4（`@RunWith(SpringRunner.class)` + `org.junit.Test`） |
| 切片测试 | 无 `@DataJpaTest` / `@WebMvcTest`（无 JPA） |
| Mock | 无 Mockito 使用 |
| Jacoco | 未配置 |

## 测试目录结构

```
sunny-qms-service/src/test/java/com/sunny/
├── ApplicationTest.java                          # 已有
├── MyTest.java                                   # 已有
└── modules/<业务域>/
    ├── service/impl/XxxServiceImplTest.java      # 单测
    ├── controller/XxxControllerTest.java         # MockMvc
    └── it/XxxServiceIT.java                      # 集成测试（连 Oracle dev）
```

包结构与 `src/main/java/com/sunny/` 镜像。

## 🔴 命名规范（强制）

| 类型 | 命名 | 示例 |
|------|------|------|
| 单测类 | `<被测类>Test` | `QmsProbfbctrlAbnServiceImplTest` |
| 集成测试 | `<被测类>IT` | `QmsInspectionTaskServiceIT` |
| 测试方法 | `should_<期望> when_<前置>` | `should_returnOpenItems when_statusIsOpen` |

JUnit 4 沿用现有：`@Test` 来自 `org.junit.Test`。

## 🟢 AAA 结构

```java
@Test
public void should_createBkm_when_alarmUnprocessed() {
    // Arrange
    when(spcAlarmMapper.selectUnprocessed()).thenReturn(Arrays.asList(buildAlarm()));
    // Act
    int count = bkmService.scanAndCreateBkm();
    // Assert
    assertThat(count).isEqualTo(1);
    verify(bkmMapper).insert(argThat(b -> "OPEN".equals(b.getCState())));
}
```

## 覆盖目标（新增代码强制）

| 层 | 目标 | 优先级 |
|----|------|--------|
| 新增 Service 写操作 | ≥ 80%（含异常分支） | P0 |
| 新增 Controller | ≥ 60%（MockMvc + 参数校验） | P1 |
| Mapper 复杂 SQL | 集成测试覆盖（连 Oracle dev） | P1 |
| 工具类 / 静态方法 | 100% | P0 |
| 历史 Service | 不强制回溯 | — |

## 🟢 Mock 策略

**Mock**（Mockito）：`@FeignClient` 客户端 / `KafkaTemplate` / `RedisTemplate` / 外部 HTTP
**不要 Mock**：MyBatis Mapper（集成测试连 Oracle dev） / `SunnyPageInterceptor` / `BeanUtils`

```java
@RunWith(SpringRunner.class)
@SpringBootTest(classes = {QmsBkmServiceImpl.class})
public class QmsBkmServiceImplTest {
    @MockBean private QmsBkmMapper bkmMapper;
    @Autowired private QmsBkmServiceImpl bkmService;
}
```

## ⚫ 禁止

| ❌ 禁止 | 原因 |
|--------|------|
| `assertTrue(true)` 占位 | 无意义的"绿"测试 |
| try-catch 后 `assertNull` | 用 `@Test(expected = XxxException.class)` |
| 测试间共享状态（static 字段） | 测试必须独立 |
| Mock Mapper 跑"集成测试" | Mock 掉 SQL 错误，集成测试无意义 |
| 测试连接生产 Oracle | 用 dev 或 test profile |

## 待办

TODO: 需要人工补充
- 引入 Jacoco + CI 阻断（≥ 60% for new code）
- 集成测试 profile（连 Oracle dev）建立
