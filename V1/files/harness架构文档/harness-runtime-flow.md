# Harness 运转流程 —— 一个 change 的完整生命周期

> 建区完成后（见 [harness-architecture.md](./harness-architecture.md)），harness 的日常运转以 **change issue** 为主线，由 Mika 编排五阶段链，人类只握两个人工门。本文描述这条主线及常驻 autopilot 旁路。目标仓库内部的治理结构见 [harness-repo-structure.md](./harness-repo-structure.md)。

![harness 运转流程图](./images/harness-runtime-flow.svg)

## 主线：五阶段链

### 起步：需求澄清与建单

1. 发起人 chat @PM，双向 explore 澄清需求（PM 不写代码）
2. PM 建 change issue，发出**编排信号 @Mika**
3. Mika 守门校验 issue **五要素**：change-id / 五阶段链 / 人工门段 / 验收点 / 澄清结论 —— 不通过退回澄清，通过则登记并进入 stage 路由

### stage 1 · PM：四工件 + 三件套

- 产出 OpenSpec 四工件：`proposal → specs → design → api(+ddl)`（顺序铁律，先 WHAT 后 HOW）
- 同期生成三件套中的 `auth-resource.sql`（Vue2 走 config-auth-resource-v2，Vue3 走 v3，从 design.md 页面/按钮清单生成三表注册脚本）
- 提交人审，进入**人工门 G1**

### 人工门 G1（第一道人工关口）

- 人审四工件（proposal / specs / design / api）
- **人工执行** `ddl.sql` 与 `auth-resource.sql`（写库 SQL 永不由 agent 执行；DDL 执行前 stage ≥2 被 block——TDD 依赖表结构先存在）
- 权限就绪后回执 @Mika，Mika 置 metadata（ddl_done / role_bind）解锁下游

### stage 2 · Tech-Lead：拆解排期

- 读四工件拆 `tasks.md` + DAG + 排他文件清单，产 `plan.md`（superpowers:writing-plans）

### stage 3 · Developer ⇄ Reviewer：task 微循环 ×N

Mika 按 tasks 逐条建子 issue 点火 Developer，循环直到全部 task 通过：

1. **Developer** 按 plan.md 单条目 TDD 编码（executing-plans + test-driven-development + systematic-debugging；DDL 变更后收尾调 db-schema-export 重生成库文档）
2. 完成信号 @Mika → Mika **点名 Reviewer**
3. **Reviewer** 只读审查（REVIEW.md：quick 4 关 / full 10 关），产 `review-report-{task-N}.md`；与 Developer 异模型防共谋
4. 未通过 → **红色打回**，Developer 返工重走循环；通过 → 下一 task

### stage 4 · Tester：测试与浏览器 QA

- 集成 / 边界 / 性能测试 + 报告式浏览器 QA（aicoding-browser-qa，分级 Quick / Standard / Exhaustive）
- 产 `test-report.md`，不改生产代码

### stage 5 · DevOps：归档与 MR

- 归档 change（openspec-archive-change）+ tag + CHANGELOG
- 走 GitLab API 建 MR（JSON body 经 `@文件` 传参，description 含 **`Closes {issue}`**）

### 人工门 G2（终点）

人审合并 MR → GitLab 自动关闭主 issue → lesson 沉淀、文档随行更新，change 生命周期结束。

## 旁路：常驻 autopilot（与主线并行）

| autopilot | assignee / 频率 | 运转方式 |
|---|---|---|
| 兜底巡检 | Mika · `*/30 min` | 巡检全部 issue：路由挂起 issue、人工卡点提醒、失败 run 断点重路由、连续失败 ≥2 停止重试 @用户、连续打回 ≥2 提炼 lesson。主通道是编排信号秒级唤醒，cron 仅为兜底 |
| 结构文档对账 | DocKeeper · 周一 08:17 | run 内调 `aicoding-harness-audit`：从上次同步基线到 `origin/master` 的 diff 映射到结构文档更新项，走 `feature/doc-audit-{date}` MR，无差异静默 |
| 人工测试复盘 | DocKeeper · 周一 08:23 | run 内调 `aicoding-human-test-retro`：游标增量读 `docs/human-test-reports/` 未读报告，逐 ⚠️ 四源证据链归因（报告 × MR diff × OpenSpec 工件 × test-report），产期报 + lesson 草案走 `retro/{date}` MR，**人审合并即决策** |

doc-audit / retro MR 与 change MR 同走 G2 人工审合并通道。

## 学习闭环：每次踩坑都变成记忆（lesson 体系）

主线与旁路中反复出现的"lesson"，背后是一套贯穿运转的自我学习机制：

![AI 自我学习闭环](./images/lesson-loop.svg)

1. **采集**：REVIEW.md 关 3/9（lesson-check）要求审查时当场记录新教训；Mika 巡检对"连续打回 ≥2"自动提炼；DocKeeper 周级复盘对人工测试 ⚠️ 四源归因产 lesson 草案
2. **条目**：`[日期][change-id] 标题 + ❌ 错误做法 + ✅ 正确做法`，具体到命令/代码形态，拒绝空话
3. **入库**：按角色分文件写入 `docs/lessons/{Role}.md`（只追加不删除）；DevOps 归档时把 report 里散落条目合并落盘；retro 草案走 MR 人审合并
4. **消费**：各角色开工必读自己角色经验库，**历史教训视同本级约束执行**；Reviewer 审查时抽查是否读过
5. **晋升**：同类教训第 2 次出现（= 条目曝光不足）→ Reviewer 标注「建议晋升宪法」→ @Mika 转人类确认 → 写入 CLAUDE.md / REVIEW.md 全员红线，原条目删除

## 关键运转机制

- **编排信号**：角色 agent 完成评论发【编排信号】@Mika 秒级唤醒接力，Mika 无需轮询
- **断点续传**：失败 run 由兜底巡检自动重路由；建 MR 失败不回滚、降级人工
- **权限边界**：所有 agent 只 push `feature/{change-id}`，禁直推保护分支；hooks/guard_write.py 拦截保护路径写入（yml / db / sql / pom 等），变更须 design.md 声明 + Reviewer 过审
- **失败升级**：连续失败 ≥2 停止重试 @用户；连续打回 ≥2 自动提炼 lesson 沉淀到 `docs/lessons/`
- **环境信息**：env 是人工通道（网页注入），agent 只在自己进程内读；密码 / token 永不入文档与评论
