# 10 条血泪教训（Superpowers + gstack 集成坑点）

> 这是集成 Superpowers / gstack / HyperSpec 时的避坑指南。
> 每条都是真实项目踩过的坑，按"症状 → 原因 → 解决"组织。

---

## 1. 装完 Superpowers 就忘了改 config.yaml

**症状**：对话开始时 AI 不调用 `using-superpowers`；tasks 没有强制 2-5 分钟粒度。

**原因**：skills 默认是 on-demand 触发，没有强制"会话开始时自检"。

**解决**：

- 在 `CLAUDE.md` 加 "Superpowers 元技能自检" 段（**已做**）
- 在 `openspec/config.yaml` 的 `context` 加 2026-06 增量段（**已做**）
- 跑 `/superpowers:using-superpowers` 验证输出包含 always_active skills

## 2. gstack 子代理没有用户上下文

**症状**：`gstack /review` 给出"通用化"建议，与本项目 baseframe 平台包冲突（如建议引入 Redisson 替代 `sunny-base-lock`）。

**原因**：gstack 子代理不知道项目有 baseframe 自研包。

**解决**：

- 在 `.claude/skills/gstack/skills/*/SKILL.md` 中注入项目 context（人工编辑或 hook 注入）
- 或在 `gstack /review` 命令前先说一句："本项目使用 sunny-base-* 自研包，禁止引入重叠依赖"

## 3. TDD 与项目现状冲突

**症状**：强制 TDD 时发现 `src/test/` 目录不存在，写测试找不到父类 / 配置。

**原因**：`spring-boot-starter-test` 已在 pom.xml，但实际从未建过 `src/test/java/`。

**解决**：

- 第一次 TDD 任务时**先建立测试目录骨架**（标准 Maven layout）：
  ```
  src/test/java/
  src/test/resources/
  ```
- 写入 `application-test.yml`（用 H2 内存库或 Testcontainers 替代 Oracle）
- 后续任务按 TDD 推进

## 4. /opsx:verify 与 gstack /review 重复检查

**症状**：9 关审查中规范对齐和通用代码质量都跑一遍，发现大量重复警告。

**原因**：两者关注点有重叠（都在看代码）。

**解决**：

- 明确职责分工：
  - **`/opsx:verify`** 看"实现 vs OpenSpec 工件"（proposal 范围 / tasks 覆盖）
  - **`gstack /review`** 看"代码质量"（命名 / 重复 / 复杂度）
- 跑顺序：先 `/opsx:verify`（如失败，根本不进入 `gstack /review`）

## 5. 2-5 分钟粒度被一刀切

**症状**：所有 task 都被强制拆到 2-5 分钟，但有些任务（如"修改 yml 配置"）本身就是 1 分钟的事，强行拆细反而冗余。

**原因**：粒度规则过于死板。

**解决**：

- 2-5 分钟是**目标**而非硬规则
- 简单任务（配置 / 文档 / 注释）可以 < 2 分钟
- 复杂任务（Service 业务）必须 ≥ 2 分钟粒度
- writing-plans skill 会自动判断

## 6. 子代理并发跑导致 git 冲突

**症状**：多个子代理同时 commit，`git push` 时出现 rebase 冲突。

**原因**：子代理默认并行执行。

**解决**：

- 在 `subagent-driven-development` 中**强制串行**（`--serial` 标志）
- 或在 commit 前加 git lock 文件

## 7. gstack /qa 找不到测试数据库

**症状**：`gstack /qa` 报"无法连接 oracle 测试库"。

**原因**：本地没有 Oracle，CI 才有。

**解决**：

- 短期：跳过 `gstack /qa`，用 `/prepare-review` 手工验证
- 长期：CI 集成 Testcontainers（Oracle in Docker）

## 8. 9 关审查一次都过不了

**症状**：第一次跑 9 关，前 3 关都失败，循环多轮。

**原因**：tasks 粒度不够、OpenSpec proposal 边界不清。

**解决**：

- **第一版 proposal 通常只是草案**（Harness.md 实战经验第 1 条）
- 如果 proposal 拆错，**宁可废弃当前 change 重开**，不要硬补
- 9 关都通过再合入；任一失败阻塞

## 9. 升级后 OpenSpec 命令失灵

**症状**：升级后 `/opsx:propose` 报错或产物不全。

**原因**：`openspec/config.yaml` 中 `rules` 段语法错误（追加时破坏 YAML 结构）。

**解决**：

- 修改后跑 `openspec list` 验证（应正常列出）
- YAML 缩进用 2 空格，列表项 `-` 顶格
- 配置错误时 OpenSpec 会在加载时报错并指向具体行号

## 10. 用户问"为什么不直接写代码"

**症状**：用户嫌流程繁琐，跳过 OpenSpec 直接让 AI 改代码。

**原因**：9 关审查 + 12 步工作流对简单修改过重。

**解决**：

- 小修改（typo / 注释 / 文档）走**快速通道**（见 `integration.md` §降级矩阵）
- 大修改（涉及 Service / Mapper / 跨服务）必须走完整流程
- 在 `AGENTS.md` 明确"硬约束：没有 OpenSpec change 不允许开始开发"

## 附录：自检清单

集成完成后逐项验证：

- [ ] `openspec list` 正常
- [ ] `/superpowers:using-superpowers` 列出 always_active skills
- [ ] `gstack --help` 列出所有子命令
- [ ] `.hyperspec-state.yaml` 12 个 checkpoint 都是 pending
- [ ] `CLAUDE.md` 包含 "Superpowers 元技能自检" 段
- [ ] `AGENTS.md` 包含 "AI 协作增强层" 段
- [ ] `REVIEW.md` 包含 "gstack /review 协作" 段
- [ ] `docs/standards/testing.md` 包含 "TDD 红绿重构" 段
- [ ] `openspec/config.yaml` 包含 2026-06 增量 context 和 rules
- [ ] `.claude/settings.local.json` 包含 4 个新 allowedTools

---

## 闭环台账（条目全生命周期追踪）

> 口径：闭环 = 已具备「原因分析 + 改善措施 + 改善结果 + 复验」四要素；复验方式含实战复跑、后续 change 验证、机制实物核对。整理于 2026-11（答辩归档时按本人工作记录回填，改善动作均发生于各条目发现后的实战周期内）。

| 条目 | 发现时间 | 原因分析 | 改善措施 | 改善结果 | 复验时间 | 闭环状态 |
|---|---|---|---|---|---|---|
| 1. 装完 Superpowers 忘改 config.yaml | 2026.05 | skills 默认 on-demand 触发，无会话自检强制 | CLAUDE.md 加元技能自检段 + config context 增量段 | 会话开始自检生效，元技能 always_active | 2026.05（/superpowers:using-superpowers 验证输出） | ✅ 已闭环 |
| 2. gstack 子代理无用户上下文 | 2026.05 | 子代理不知项目有 baseframe 自研包 | SKILL.md 注入项目 context / 提示词前置声明 | 审查建议不再与自研包冲突 | 2026.05-06 多轮实战审查 | ✅ 已闭环 |
| 3. TDD 与项目现状冲突（无 src/test） | 2026.05 | 项目从未建测试目录骨架 | 先建标准 Maven 测试骨架 + application-test.yml 再按 TDD 推进 | TDD 门禁可执行；后续测试 22→41 递增 | 2026.06 PLM 接口（Tests 22/0）→ 2026.11 复跑（41/0） | ✅ 已闭环 |
| 4. verify 与 review 重复检查 | 2026.05 | 两者关注点重叠 | 职责分工：verify 看工件对齐、review 看代码质量，先 verify 后 review | 重复警告消除，审查时长可控 | 2026.06 起历次实战审查 | ✅ 已闭环 |
| 5. 2-5 分钟粒度一刀切 | 2026.05 | 粒度规则过死 | 定为目标而非硬规则，writing-plans 自动判断 | 简单任务不再冗余拆分 | 2026.06 起拆解实战 | ✅ 已闭环 |
| 6. 子代理并发 git 冲突 | 2026.05 | 子代理默认并行 commit | 强制串行 / commit 前 git lock | push 冲突消失；机制后续演进为排他文件清单 + Developer 5 实例并行 | 2026.06-10 并行实战（V3 阶段 6 MR 零冲突合入） | ✅ 已闭环 |
| 7. gstack /qa 找不到测试库 | 2026.05 | 本地无 Oracle，CI 才有 | 短期 prepare-review 手工验证；长期 Testcontainers 规划 | 质量验证不因环境缺失中断（降级预案同源） | 2026.06 起降级路径执行 | ✅ 已闭环（长期项规划中） |
| 8. 9 关审查一次过不了 | 2026.06 | proposal 边界不清、tasks 粒度不够 | proposal 视为草案可废弃重开，不硬补 | 首轮通过率显著上升；审查关卡演进为现行 4+10 关 | 2026.06.23 PLM 实战（3 Critical 修复后通过） | ✅ 已闭环 |
| 9. 升级后 OpenSpec 命令失灵 | 2026.06 | config.yaml rules 段语法被追加破坏 | 修改后 openspec list 验证 + YAML 缩进规范 | 命令失灵不再复现 | 2026.06 起历次配置变更 | ✅ 已闭环 |
| 10. 用户问"为什么不直接写代码" | 2026.06 | 全流程对简单修改过重 | 降级矩阵快速通道 + AGENTS.md 硬约束（无 change 不开发） | 小修改走快速通道不被劝退，大修改不失控 | 2026.06 起实战（快速/全量审查自动路由） | ✅ 已闭环 |

**闭环率：10/10 = 100%**（口径：完整闭环条数/总条数；条目 7 长期项 Testcontainers 为增强方向，不影响短期措施闭环判定）。
