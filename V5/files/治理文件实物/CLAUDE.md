# sunny-qms-service CLAUDE.md

## 协作规则
- 始终用中文交流
- 计划执行结束时不需要执行 npm build 测试
- 不在文件里写无意义注释（只在 WHY 非显然时写）
- 项目规范见 `AGENTS.md`（技术栈 / 模块边界 / 编码规范 / 禁止事项）

## Maven 路径（本机实际）
```bash
MVN="/c/Program Files/JetBrains/IntelliJ IDEA 2025.3/plugins/maven/lib/maven3/bin/mvn.cmd"
export JAVA_HOME="/d/jdk1.8.0_171"
```
项目无 `mvnw`，统一用上面的 mvn.cmd。所有 `mvn` 命令默认带 `-f sunny-qms-service/pom.xml`。

## 项目命令（实测可用）
所有命令在仓库根目录执行。

| 用途 | 命令 |
|------|------|
| 编译 | `"$MVN" -q -DskipTests --batch-mode compile -f sunny-qms-service/pom.xml` |
| 启动 | `"$MVN" spring-boot:run -f sunny-qms-service/pom.xml` |
| 打包 | `"$MVN" -DskipTests clean package -f sunny-qms-service/pom.xml` |
| 跑测试 | `"$MVN" test -f sunny-qms-service/pom.xml`（⚠ 仅 2 个测试文件，覆盖近 0） |
| 依赖树 | `"$MVN" dependency:tree -f sunny-qms-service/pom.xml` |

启动后默认端口 `8084`，Knife4j 文档：`http://localhost:8084/doc.html`。
dev profile 用 Oracle + Nacos + Redis 哨兵，需内网访问。

## 目录约定
项目嵌套两层同名目录（**注意别进错**）：

- 仓库根：`E:\IdeaProjects\sunny-qms\sunny-qms-service\`
- Maven 模块根（pom.xml 在这里）：`sunny-qms-service/`
- Java 源码：`sunny-qms-service/src/main/java/com/sunny/`
- 测试源码：`sunny-qms-service/src/test/java/com/sunny/`
- 资源（application*.yml 等）：`sunny-qms-service/src/main/resources/`
- Mapper XML：`sunny-qms-service/src/main/java/com/sunny/modules/<业务>/dao/`（与接口同包）
- 业务模块：`sunny-qms-service/src/main/java/com/sunny/modules/<业务>/{controller,service,service/impl,dao,entity,dto,enums}/`

## OpenSpec 工作流规则

### spec-driven Schema 工件创建顺序（必须遵守）

无论项目是否配置了自定义 schema，使用 OpenSpec 时**必须按以下顺序创建 artifacts**：

```
proposal → specs → design → tasks
```

| 顺序 | Artifact | 作用 | 核心问题 |
|------|----------|------|----------|
| 1 | proposal | 定义变更动机 | WHY - 为什么做 |
| 2 | specs | 定义需求规格 | WHAT - 做什么 |
| 3 | design | 定义技术设计 | HOW - 怎么做 |
| 4 | tasks | 执行开发任务 | 执行 |

### 重要原则

1. **即使多个 artifacts 同时显示 "ready" 状态，也必须按顺序创建**
2. **specs 必须在 design 之前**，因为：
   - specs 定义需求（做什么）
   - design 依赖需求来设计技术方案（怎么做）
   - 先设计后需求会导致返工

### 常见错误警示

❌ **错误做法**：看到 design 和 specs 都是 ready，直接创建 design
✅ **正确做法**：即使 specs 也是 ready，也应该先创建 specs

### 判断口诀

> "先需求后设计，先 WHAT 后 HOW"

## 当前日期
Today's date is 2026-06-17
