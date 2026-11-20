# Spring Boot 规范 (spring.md)

> 基于 Spring Boot 2.2.6 + Spring Cloud Hoxton.SR10 + Nacos。

## 现状实测

| 维度 | 项目实际 | 数量 |
|------|---------|------|
| Controller 注解 | 统一 `@RestController`，无 `@Controller+@ResponseBody` | 182 |
| Service 接口 | `@Service` 标在 `XxxServiceImpl` 上，必带接口 `IXxxService` | 171 |
| DI 方式 | `@Autowired` 字段注入主流（`@RequiredArgsConstructor` 0 处） | 999 字段注入 |
| 事务 | `@Transactional(rollbackFor = Exception.class)` 写操作方法级 | 744 |
| 配置读取 | `@Value("${x}")` 散落（37 处），`@ConfigurationProperties` 仅 2 处 | — |
| 配置文件 | `application.yml` + 6 个 profile（dev/pro/prodev/proyn/test/mcppro/mcptest） | 7 |
| 异步 | `@Async` + `AsyncConfig` 线程池配置 | inspectionTask 异步采集 |
| 异常处理 | `@RestControllerAdvice` 统一兜底 | 1 |

## 🔴 强制

1. **Controller**：`@RestController + @RequestMapping("/<业务>") + @Api(tags="中文")`
2. **Controller 方法**：`@PostMapping` 主流（项目非严格 RESTful）；`@ApiOperation` 必填；返回 `Result<?>`
3. **Service 实现**：`@Service` + `extends BaseServiceManager`；接口命名 `IXxxService`
4. **事务**：写操作方法上加 `@Transactional(rollbackFor = Exception.class)`，**类级别不加**（查询也会启动事务，浪费）
5. **日志 Service**：`@Transactional(propagation = Propagation.REQUIRES_NEW)`（参考 `DirectConnectionLogServiceImpl`）
6. **配置 profile**：开发 `dev`、生产 `pro`、预发 `prodev`；启动参数 `--spring.profiles.active=dev`
7. **Bean 注入**：跨模块必须走 `@FeignClient`，禁止 `@Autowired` 别模块 Service（见 modules.md）

## 🟢 选择

| 场景 | 选 A | 选 B | 项目偏好 |
|------|------|------|---------|
| Controller URL | `@PostMapping("/insert")` | `@PutMapping`/`@PatchMapping` | **A**（项目主流 PostMapping） |
| DI | `@Autowired` 字段 | 构造器 + `@RequiredArgsConstructor` | **A**（历史），**新代码 B** |
| 事务范围 | 方法级 | 类级 | **方法级**（强制） |
| 配置注入 | `@Value` | `@ConfigurationProperties` | 历史代码 `@Value`，**新代码 `@ConfigurationProperties`** |
| 异步 | `@Async` | Kafka 解耦 | 简单异步 `@Async`，跨服务 Kafka |
| 异常 | `@RestControllerAdvice` | Controller 内 try-catch | **全局兜底**，Controller 不 try-catch |
| 拦截 | `@Authignore` | HandlerInterceptor | 标注接口用 `@Authignore` 免登 |

## 配置文件分层（实测）

```
application.yml          # 基础配置（端口/日志/Kafka 开关）
application-dev.yml      # 开发：内网 Oracle/Nacos/Redis 哨兵
application-pro.yml      # 生产：真实凭据（受保护）
application-prodev.yml   # 预发
application-proyn.yml    # YN 工厂专有配置
application-test.yml     # 测试
application-mcppro.yml   # MCp 生产
application-mcptest.yml  # MCp 测试
```

**禁止修改**：`application*.yml` 受 `.claude/hooks/guard_write.py` 拦截（见 openspec/config.yaml `protected_paths`）。

## 🟢 @Transactional 使用建议

| 场景 | 写法 |
|------|------|
| 写操作（insert/update/delete） | 方法上 `@Transactional(rollbackFor = Exception.class)` |
| 批量操作 | 方法上同上；Mapper 用 `insertBatch` 不循环单条 |
| 调用其他 Service 写方法 | 走自身代理（`self.xxx()`），避免 `this` 导致事务失效 |
| 跨 Service 调用链 | 链路上游加事务，下游用 `Propagation.REQUIRES_NEW` 仅在日志场景 |
| 长事务（>5s） | 拆分；或改 Kafka 异步 |

## ⚫ 禁止

| ❌ 禁止 | 原因 |
|--------|------|
| `@Transactional` 加在类上 | 查询也启事务，浪费连接 |
| `@Autowired` 构造器手动写 | 用 `@RequiredArgsConstructor`（项目虽未用，但新代码强制） |
| 跨模块 `@Autowired` 别模块 Service | 见 modules.md 边界红线 |
| 启动类加 `@ComponentScan("com.*")` | 项目用默认扫描 + `@MapperScan` |
| `application.yml` 硬编码密码 | 走 Nacos 配置中心 / 环境变量 |
