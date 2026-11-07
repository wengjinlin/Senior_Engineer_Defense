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
