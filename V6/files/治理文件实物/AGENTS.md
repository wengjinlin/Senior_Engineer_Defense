# sunny-qms-service AGENTS.md

## 项目定位

舜宇智能 QMS（Quality Management System，质量管理系统）服务层 — Spring
Boot 单体应用，覆盖检验、SPC、VDA 过程审核、ESD 防护、LIMS 实验室、
经验库、工序/物料/设备、缺陷闭环等 120+ 业务模块，对接 Oracle + Nacos
+ Redis 哨兵 + Kafka + S3 对象存储。

## 技术栈（强制版本，来自 pom.xml 与父 `com.sunny:base-platform:0.0.1`）

- 框架：Spring Boot **2.2.6.RELEASE**
- Spring Cloud：**Hoxton.SR10**
- 服务发现：spring-cloud-starter-alibaba-nacos-discovery
- RPC：spring-cloud-starter-openfeign + feign-okhttp
- ORM：**MyBatis（Spring Boot Starter，非 MyBatis-Plus，非 JPA）**
- SQL 映射：XML Mapper（279 个 `*Mapper.xml`，与 Mapper 接口同包同名）
- 连接池：Druid **1.1.17**（druid-spring-boot-starter）
- 数据库：**Oracle**（驱动 `com.oracle:ojdbc8`；dev 环境 `jdbc:oracle:thin:@172.26.58.135:1521/orcl`）
  - 注：pom 也声明了 mysql-connector-java 和 postgresql，但当前部署用 Oracle
- 缓存：Redis Sentinel（哨兵模式，spring-boot-starter-data-redis 经由 base-platform 传递）
- 消息：Kafka（开关式，`kafka-config.enable`）
- 对象存储：S3 兼容（vestack-tos / obs.sunnyoptical.cn）
- 认证：sunny-auth-client 0.0.21-SNAPSHOT + jjwt 0.9.1
- API 文档：Knife4j（knife4j-spring-boot-starter）+ Swagger v2 注解（`@Api` / `@ApiOperation`）
- 工具库：Lombok、fastjson、joda-time、Apache POI、commons-math3、commons-csv、
  commons-net（FTP）、httpmime、mvel2（公式）、jfreechart、exp4j
- JDK：**1.8**（class major version 52，父 pom 强制 Java 8 编译）
- 构建：Maven（项目无 `mvnw`，使用 IDEA 内置 Maven：
  `/c/Program Files/JetBrains/IntelliJ IDEA 2025.3/plugins/maven/lib/maven3/bin/mvn.cmd`
  + `JAVA_HOME=D:\jdk1.8.0_171`）

## 模块边界（红线）

### 禁止修改（动了全站受影响）

- `com.sunny.StartApplication` — 启动入口，含 `@SpringBootApplication` /
  `@EnableDiscoveryClient` / `@EnableFeignClients` / `@ComponentScan` 等核心开关
- `com.sunny.config.MybatisConfigDs` — 数据源 + `@MapperScan` + PageHelper 拦截器，
  动了影响所有 Mapper
- `com.sunny.config.DataSourceConfig` — Druid 数据源 bean 定义
- `com.sunny.config.SwaggerConfig` / `SwaggerProperties`
- `com.sunny.aop.ParamCheckAspect` — 全局参数校验切面
- `com.sunny.exception.GlobalDefaultExceptionHandler` — 全局 `@RestControllerAdvice`
- `com.sunny.feign.*` — 对外 Feign 客户端接口
- `pom.xml` — 版本由父 `com.sunny:base-platform:0.0.1` 统一管理，禁止在子 pom
  写死版本号
- `src/main/resources/application*.yml` — 含数据库/Redis/Nacos/S3 凭证，受
  `.claude/hooks/guard_write.py` 拦截
- `src/main/resources/db/migration/`、`src/main/resources/sql/`（若有）— 受
  guard_write.py 拦截

### 谨慎修改（涉及多个业务模块，需评审）

- `com.sunny.baseframe.*` — 基础框架适配
- `com.sunny.kafka.*` — Kafka 数据处理器（`InspectionTransKafkaDataExecuteHandler` 等）
- `com.sunny.modules.common.*` — 跨模块公共能力
- `com.sunny.modules.commondialog.*` / `commonselect.*` — 通用下拉/弹窗
- 任何 `*Mapper.xml`（XML 改一行影响对应业务全部查询）

### 自由修改（在明确 change 范围内）

- `com.sunny.modules.<某业务>.*`（除上述 common/commondialog/commonselect 外）
  典型：`qmsXxx` / `limsXxx` / `inspectionTask` / `procedureManage` 等
  每个模块标准 5 层：`controller` → `service` (+`service/impl`) → `dao` → `entity`/`dto`/`enums`

## 业务术语（**5 项待业务侧确认 — 下方 TODO[业务术语] 请逐条校正**）

> 下列 5 个术语是按模块/接口名推测，未与领域专家核对。

- **BKM** — 推测 = "问题闭环管理"（基于 `@Api(tags = "问题闭环-公共功能-BKM台账")`）
- **VDA** — 推测 = VDA 6.3 过程审核标准（基于 `qmsVdaBasic` / `qmsVdaDetail` / `qmsVdaReport`）
- **GP12** — 推测 = GP12 早期生产抑制程序（基于 `qmsGp12Pzjk`，"Pzjk" 可能=品质监控）
- **ESD** — 推测 = 静电放电防护 ElectroStatic Discharge（基于 `qmsEsd*` 系列）
- **QDAS** — 推测 = 质量数据采集系统 Quality Data Acquisition System（基于 `qdas.ftp` 配置）

其他明确术语（无歧义）：
- **LIMS** — 实验室信息管理系统（Laboratory Information Management System）
- **SPC** — 统计过程控制（Statistical Process Control）
- **PAT** — 过程审核（Process Audit Test，基于 `qmsPatMain`）
- **PO** — 测试机调用接口（基于 `po.http.urlPrefix`，访问产线测试设备）
- **工序**（procedureManage）/ **物料**（wuliao）/ **工厂**（qmsFactory）

TODO[业务术语]：以上 5 项推测请逐条确认或更正，BKM / GP12 / Pzjk 等内部缩写尤其需要业务侧解释。

## 编码规范（按项目现状写，非理想规范）

### 命名

| 类型 | 规则 | 示例 |
|------|------|------|
| Controller | `<业务>Controller`，所有 Controller 必须用 `@RestController`（全站 170 个，0 个 `@Controller`） | `QmsBkmController` |
| Service 接口 | `I<业务>Service`（168 个，驼峰 + I 前缀） | `IQmsBkmService` |
| Service 实现 | `<业务>ServiceImpl`，放在 `service/impl/` 子包（171 个） | `QmsBkmServiceImpl` |
| Mapper 接口 | `<业务>Mapper`，放在 `dao/` 子包（无 `@Mapper` 注解，由 `MybatisConfigDs` 的 `@MapperScan(basePackages={"com.sunny.modules.*.dao", "com.sunny.auth.modules.*.dao", "com.sunny.core.modules.*.dao"})` 扫描） | `QmsBkmMapper` |
| Mapper XML | `<业务>Mapper.xml`，与接口同包（共 279 个） | `QmsBkmMapper.xml` |
| Entity | `<业务>` 或 `Qms<业务>`，放在 `entity/` 子包，使用 Lombok `@Data` + Swagger `@ApiModelProperty`，**无 JPA 注解** | `QmsBkm` |
| DTO | 放在 `dto/` 子包 | — |

### 分层依赖方向（强制）

```
Controller  ──依赖──▶  Service(接口)  ──依赖──▶  Mapper(接口) ──绑定──▶ *Mapper.xml
                              │
                              └─▶ ServiceImpl(实现, 在 service/impl/)
```

- Controller 只依赖 Service 接口，禁止直接 new Impl、禁止直接调 Mapper
- ServiceImpl 依赖 Mapper 接口（不依赖 XML；XML 由 MyBatis 绑定）
- Entity 在三层间流转；DTO 用于 Controller ↔ Service；禁止 Entity 直接当
  Controller 返回值（除非该模块已约定）

### 依赖注入（按项目现状）

> 项目主流是 **`@Autowired` 字段注入**（999 处）+ `@Resource`（353 处），
> 构造器注入仅 38 处。**新增代码沿用字段注入以保持一致性**，不要在老
> 代码里强改构造器注入（会引入大量噪声 diff）。

- 新建 Service/Controller：沿用 `@Autowired` 字段注入
- 同类型多 Bean 注入：用 `@Resource(name="...")` 或 `@Qualifier`
- 测试代码：允许 `@InjectMocks` 构造器注入

### 异常处理

- 全局拦截：`com.sunny.exception.GlobalDefaultExceptionHandler`（`@RestControllerAdvice`）
- 业务异常：抛 `RuntimeException` 或 `DatabaseException`（同包内定义）
- 返回结构：`com.sunny.util.Result`（`Result.error(code, msg)` / `Result.ok(data)`）
- 国际化：`com.sunny.auth.runner.I18n.errDB(path, msg)` 等方法

### 日志（强制规范）

- **用 `@Slf4j`（Lombok）** — 182 处在用；新代码默认此方式
- 或 `private static final Logger log = LoggerFactory.getLogger(Xxx.class);`
- **禁止 `System.out.println` / `ex.printStackTrace()`**（现状有 86 处违规，
  属历史债务；新代码必须避免，改动老代码遇到时可顺手清理）
- 异常日志：`log.error("context", ex)`（带异常栈，不要只打 `getMessage()`）
- 访问日志：由 `log-config.access-log-config` 通过 AOP 切面自动记录
  `com.sunny.modules.*.controller..*` 的所有调用，业务代码不需要手写

### API 文档（Swagger / Knife4j）

- Controller 类：必须 `@Api(tags = "中文业务名-子模块")`
- Controller 方法：必须 `@ApiOperation("接口中文描述")`
- 可选：`@ApiOperationSupport(author = "名字")`（Knife4j 扩展）
- Entity 字段：`@ApiModelProperty(value = "中文说明")`
- 访问地址：`http://<host>:8084/doc.html`（Knife4j）

### MyBatis 约定

- Mapper 接口方法命名：`get` / `insert` / `update` / `delete` / `findXxx` / `selectForPage` / `exportCustom`
- 分页：使用 `com.sunny.pagehelper.Page` + `SunnyPageInterceptor`（**不是** PageHelper 默认实现，
  也**不是** MyBatis-Plus 分页）
- MyBatis 二级缓存关闭（`LocalCacheScope.STATEMENT`，见 MybatisConfigDs）
- XML 中 `resultType` / `parameterType` 使用全限定类名
- Map 查询返回时 key 自动转大写（`MapKeyUpperWrapper`，见 `config.mybatis`）

## 验证命令（改完业务代码必跑）

> 项目无 Maven Wrapper，无 checkstyle / spotbugs / pmd 插件。统一用 IDEA 自带 Maven。
> 命令前缀（bash 下）：

```bash
MVN="/c/Program Files/JetBrains/IntelliJ IDEA 2025.3/plugins/maven/lib/maven3/bin/mvn.cmd"
export JAVA_HOME="D:/jdk1.8.0_171"
```

1. **编译检查**（改任何 .java 后必跑）：

   ```bash
   "$MVN" -q -DskipTests --batch-mode compile -f sunny-qms-service/pom.xml
   ```

   > `.claude/hooks/run_checks.sh` 会在每次 Edit/Write .java 后自动跑这个命令

2. **打包**（验证整体打包无误）：

   ```bash
   "$MVN" -DskipTests clean package -f sunny-qms-service/pom.xml
   ```

3. **测试**（**注意：项目测试覆盖几乎为 0，仅 2 个文件 — `ApplicationTest.java`、`MyTest.java`**）：

   ```bash
   "$MVN" test -f sunny-qms-service/pom.xml
   ```

   > 若新增业务代码，请同步在 `sunny-qms-service/src/test/java/com/sunny/modules/<业务>/`
   > 下补齐 `*ServiceTest` / `*ControllerTest`（用 `spring-boot-starter-test` 提供的
   > JUnit 4 + Mockito + Spring Test）

4. **依赖树**（排查冲突时用）：

   ```bash
   "$MVN" dependency:tree -f sunny-qms-service/pom.xml
   ```

## 禁止事项

- ❌ 不允许硬编码密码 / 密钥 / Token（凭证必须在 `application*.yml` 或环境变量中）
- ❌ 不允许在 Controller 里直接写 SQL（必须经 Mapper 接口 + XML）
- ❌ 不允许 `System.out.println` / `ex.printStackTrace()`（用 `@Slf4j`）
- ❌ 不允许在子 `pom.xml` 写死依赖版本（版本由父 `base-platform` 统一管理）
- ❌ 不允许业务代码直接依赖 `com.sunny.auth.*` 内部类（只能用 `sunny-auth-client`
  暴露的注解，如 `@Authignore`）
- ❌ 不允许新增 `@Controller`（统一用 `@RestController`）
- ❌ 不允许新增 JPA 注解（`@Entity` / `@Table` / `@Column`）— 项目用 MyBatis
- ❌ 不允许新增 MyBatis-Plus 注解（`@TableName` / `@TableId`）— 项目不是 MP
- ❌ 不允许在 `com.sunny.modules.*` 之外的业务包创建新模块（新业务必须在 `modules/` 下）

## TODO（探测不到，待人工补充）

- [ ] **业务术语 5 项**（见上文 TODO[业务术语]）
- [ ] 项目对外暴露的 Feign 接口清单（`com.sunny.feign.*` 内的具体客户端）
- [ ] 数据库 schema / DDL 位置（dev profile 仅给出连接，未见 Flyway / Liquibase 迁移目录）
- [ ] 代码生成器配置（pom 引入了 `sunny-base-code`，但具体生成模板未探测）
- [ ] CI / CD 构建脚本（未见 Jenkinsfile / GitHub Actions）
