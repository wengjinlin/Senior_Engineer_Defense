# 双轨审查指南（REVIEW.md）

本项目的代码审查采用**双轨制**：quick-review（快速）+ full-review（完整，基于 gstack）。

## 审查触发时机

| 时机 | 强制轨道 | 说明 |
|------|---------|------|
| **每个 task 完成** | quick-review | 单 task 自检，~2 分钟 |
| **合并前（Merge / PR）** | full-review | 多 task 协同变更，完整 9 关 |
| **发布前（Release）** | full-review | 影响线上的最后关卡 |
| **热修复（Hotfix）** | quick-review + 人工复核 | 抢时间，但必须事后补 full-review |

**判断口诀**：单 task 走 quick，多 task 走 full；合并/发布必 full。

## 双轨对比表

| 维度 | quick-review（快速） | full-review（完整，gstack） |
|------|---------------------|----------------------------|
| **耗时** | ~2 分钟 | ~15-30 分钟 |
| **关卡数** | 3 关 | 9 关 |
| **覆盖范围** | 语法 / 测试 / 安全 | 语法 / 测试 / 安全 / 性能 / 可维护性 / 可访问性 / 错误处理 / 依赖 / 文档 |
| **适用场景** | 单 task、小改动（<200 行）| 新功能、架构调整、多 task 协同 |
| **触发命令** | `/quick-review` | `/full-review`（gstack `/review`） |
| **路由规则** | task ≤ 3 自动走此轨道 | task > 3 强制走此轨道 |
| **是否阻塞提交** | 是（任一关失败即阻止） | 是（任一关失败即阻止） |
| **人工复核** | 不要求 | 合并/发布前要求 |
| **依赖工具** | Maven、JUnit | gstack、Maven、JUnit、slop-scan |

## 9 关完整清单（full-review）

> 参考 gstack `/review` 文档，结合本项目（Java / Maven / Spring）特点裁剪。

### 第 1 关：语法 / 编译（quick-review 也覆盖）

- [ ] `mvn compile -q` 通过
- [ ] 无未使用 import
- [ ] 命名规范：类 PascalCase、方法/变量 camelCase、常量 UPPER_SNAKE
- [ ] 无语法错误、括号/分号匹配

### 第 2 关：测试覆盖（quick-review 也覆盖）

- [ ] 新代码有对应单元测试
- [ ] `mvn test -q` 全部通过
- [ ] 覆盖核心分支（happy path + 异常分支 + 边界值）
- [ ] 测试有断言，无 `@Ignore`、无注释掉的测试
- [ ] 覆盖率不低于基线（新增代码行覆盖 ≥ 70%）

### 第 3 关：安全（quick-review 也覆盖）

- [ ] 无硬编码密码、密钥、token
- [ ] 无 SQL 字符串拼接（必须参数化 / MyBatis `#{}`）
- [ ] 权限校验完整：接口有鉴权注解或全局过滤器覆盖
- [ ] 日志不打印敏感字段（密码、身份证、手机号脱敏）
- [ ] 输入校验：防 XSS、防路径穿越、防反序列化漏洞

### 第 4 关：性能

- [ ] 无 N+1 查询（循环中调 DB）
- [ ] 索引使用合理，无全表扫描风险
- [ ] 大结果集分页（禁止一次性捞全表）
- [ ] 缓存策略合理（热点数据、TTL）
- [ ] 无明显内存泄漏（流未关闭、静态集合无限增长）

### 第 5 关：可维护性

- [ ] 单方法 ≤ 80 行，圈复杂度 ≤ 10
- [ ] 无重复代码（DRY，相似逻辑抽取）
- [ ] 命名可读，无 `temp`、`data`、`info` 等无意义命名
- [ ] 注释只解释 **WHY**，不解释 WHAT
- [ ] 单一职责：一个类/方法只做一件事

### 第 6 关：可访问性 / 国际化

- [ ] 用户文案走 i18n 资源文件，无硬编码中文/英文
- [ ] 错误提示对用户友好（不暴露堆栈、不暴露技术细节）
- [ ] REST API 返回结构符合统一 Response 包装
- [ ] 时间统一时区（UTC 存储、展示层转换）

### 第 7 关：错误处理

- [ ] 异常分级：业务异常 `BusinessException`、系统异常 `SystemException`
- [ ] 不吞异常（`catch {}` 必须有日志或重新抛出）
- [ ] 不 catch `Throwable` / `Exception`（除非在顶层兜底）
- [ ] 事务边界正确（`@Transactional` rollbackFor 配置）
- [ ] 外部调用（HTTP、RPC）有超时、重试、熔断

### 第 8 关：依赖管理

- [ ] 无新增未审核依赖（pom.xml 变更需要 review）
- [ ] 无已知高危漏洞版本（`mvn dependency-check`）
- [ ] 无重复依赖、无版本冲突
- [ ] scope 正确（`provided` / `test` 不打入生产包）

### 第 9 关：文档 / 日志

- [ ] 公共 API 有 Javadoc
- [ ] 关键业务流程有日志（入参、出参、耗时）
- [ ] 日志级别合理（DEBUG 开发、INFO 生产、ERROR 异常）
- [ ] CHANGELOG / README 同步更新（若影响用户）
- [ ] 数据库变更脚本（Flyway / Liquibase）已编写

## 执行流程（full-review）

1. 读取当前 `git diff origin/master...HEAD`
2. 按 9 关顺序逐项检查
3. 每关输出 ✅ / ❌ / ⚠️（警告）
4. 全部通过 → 输出"full-review 通过"
5. 任一关失败 → 输出问题清单，**阻止合并/发布**

## 相关命令

| 命令 | 作用 |
|------|------|
| `/quick-review` | 3 关快速审查 |
| `/full-review` | 9 关完整审查（待实现，gstack `/review` 别名） |
| `/security-review` | 单独的安全审查（Claude Code 内置） |
| `/review` | gstack 的 PR 审查 skill |

## 参考

- gstack `/review` 文档：`.claude/skills/gstack/review/`
- 项目根 CLAUDE.md（全局规则）
- OpenSpec 工作流（task 数判定来源）
