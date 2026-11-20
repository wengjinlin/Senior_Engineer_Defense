# sunny-multica 多 Agent 编码 Harness 架构

> 本文档描述基于 [Multica](https://github.com/multica-ai/multica) 搭建的多 agent 编码 harness 的整体架构。
> 运转流程见配套文档 [harness-runtime-flow.md](./harness-runtime-flow.md)。

![harness 架构图](./images/harness-architecture.svg)

## 一图总览

harness = **Multica 平台（工作区底座）+ Mika 编排 agent + 7 角色 agent + 3 系技能库 + 目标仓库治理层**，外围由 6 个 bootstrap 脚手架一次性建区，人类只握住三个人工关口（澄清问答、DDL 执行、MR 合并）。

## 分层说明（自上而下）

> 架构图按标准分层排版：**顶层最接近用户端，底层是平台基座**（见左侧行政轴）。Multica 平台能力不再单列一层，而是拆解融入三处并以蓝系统一标识：**UI 交互层**（看板 / Issue / Chat）、**编排层**（Mika）、**平台基座**（Go 后端 + Runtime + Autopilot 调度器）。建区脚手架位于右侧一次性建设栏，持续学习闭环位于右下角。

### 1. 人工层（人类 · 发起人 / 审阅人）

不写代码，但握住所有决策权：

- 开头一轮问答：项目名 / 仓库 URL / MR 目标分支 / 数据库信息 / 密码来源
- 中段一次网页操作窗口：GitLab 连接 + webhook + 各 agent 环境变量注入（env 是人工通道，agent 永不代写）
- 结尾人审：harness MR 合并、宪法首版审核、每期 change 的四工件审核、DDL / 权限 SQL 人工执行、最终 MR 合并

### 2. Multica 平台层（团队工作区 · 自托管 · 图中拆解融入三处）

来自 [multica-ai/multica](https://github.com/multica-ai/multica)：Web / 桌面 / 移动端同一工作区，Go 后端 + PostgreSQL，本机 Runtime 守护进程拉起 agent CLI（Claude Code 等 26 种），Autopilot 调度器按 cron 触发自动化 run。agent 在 issue / chat 中被触发，边做边评论，人可随时插话。

图中该层已拆解为：**看板 / Issue / Chat / 收件箱 → 交互层 UI 端**（顶层）、**Mika → 编排层**、**Go 后端 + PostgreSQL / Runtime / Autopilot 调度器 → 平台基座**（最底层）。

### 3. 编排层（aicoding-orchestration-bootstrap 复现）

| 组件 | assignee | 频率 | 职责 |
|---|---|---|---|
| **Mika · 编排 agent**（平台内置） | — | 事件驱动（编排信号秒级唤醒） | 建单守门（issue 五要素）、stage 路由、task 级审查点火、人工门 metadata（spec_review / ddl / role_bind）、失败清扫、lesson 提炼 |
| 兜底巡检 autopilot | Mika | `*/30 * * * *` | 挂起 issue 路由、人工卡点提醒、失败 run 断点重路由、连续失败 ≥2 停止重试 @用户、连续打回 ≥2 提炼 lesson |
| 结构文档对账 autopilot | DocKeeper | 周一 08:17 | run 内调 `aicoding-harness-audit`：代码 diff → 结构文档增量 MR，无差异静默 |
| 人工测试复盘 autopilot | DocKeeper | 周一 08:23 | run 内调 `aicoding-human-test-retro`：未读测试报告逐 ⚠️ 四源归因 → retro 分支 MR |

五阶段链的权威源在 Mika 编排层（写入 issue 描述），仓库侧只认 stage 编号不维护链序。

### 4. 角色 agent 层（aicoding-agent-bootstrap 批量创建 · 7 角色）

| 角色 | 职责 | 出场时机 | 并发 |
|---|---|---|---|
| **PM** | chat 双向澄清需求，产出 OpenSpec 四工件 proposal→specs→design→api(+ddl) 与 `auth-resource.sql`，不写代码 | stage 1 | 3 |
| **Tech-Lead** | 读工件拆 `tasks.md` + DAG + 排他文件清单，产 `plan.md` | stage 2（人审通过后 Mika 点火） | 1 |
| **Developer ×N** | 按 plan.md 单条目 TDD 编码，可多实例并行（dev-squad） | stage 3（task 子 issue 微循环） | 5 |
| **Reviewer** | 只读审查（quick 4 关 / full 10 关），产 `review-report-{task-N}.md`，与 Developer 异模型防共谋 | stage 3 内横向关卡 | 3 |
| **Tester** | 集成 / 边界 / 性能测试 + 报告式浏览器 QA，产 `test-report.md`，不改生产代码 | stage 4 | 2 |
| **DevOps** | 归档 change + tag + CHANGELOG + 走 GitLab API 建 MR（description 含 `Closes {issue}`） | stage 5 | 1 |
| **DocKeeper** | 结构文档对账 + 人工测试复盘，只改 `docs/`，走 doc-audit / retro 分支 MR | 周级 autopilot | 1 |

通用铁律：开工先读 CLAUDE.md + AGENTS.md（项目事实唯一权威源）；只 push `feature/{change-id}`，禁直推保护分支；commit 后立即 push（跨 runtime 协作）。

### 5. 技能层（multica skill import · zip 通道全量入库）

| 技能组 | 内容 | 主要使用者 |
|---|---|---|
| **openspec 工件系** | explore / new-change / continue-change / apply-change / verify-change / archive-change / sync-specs | 全角色（工件链驱动） |
| **superpowers 工程系**（源：obra/superpowers） | writing-plans（Tech-Lead）；executing-plans · TDD · systematic-debugging · verification（Developer） | Tech-Lead / Developer |
| **aicoding 业务系**（本仓库 `skills/` ×8） | lookup-ui-reference v2/v3 · config-auth-resource v2/v3 · db-schema-export · browser-qa · harness-audit · human-test-retro | PM / Developer / Tester / DocKeeper |

### 6. 目标仓库 harness 层（aicoding-harness-bootstrap 铺设 · 详见专篇 [harness-repo-structure.md](./harness-repo-structure.md)）

| 工件 | 作用 |
|---|---|
| `CLAUDE.md` | 项目宪法：§0 适用范围 / §1 定位 / §2 模块表 / §3 基础设施 … §10 保护路径 |
| `AGENTS.md` | 协作总纲：角色速查表、Git 策略（feature/{change-id}、禁直推）、OpenSpec 工件结构、变更联动矩阵、lessons 读写矩阵 |
| `REVIEW.md` | 审查关卡：quick 4 关（spec-align / risk-check / lesson-check / archive）+ full 10 关；protected 路径另加人工复核 |
| `hooks/guard_write.py` | Claude Code PreToolUse hook，block 保护路径写入（application*.yml / db/ / sql/ / settings.xml / pom.xml），变更须 design.md 声明 + Reviewer 过审 |
| `docs/` 文档体系 | **唯一权威源**：architecture（模块字典 + 隐性约定）/ product / database（只能经 aicoding-db-schema-export 生成）/ standards / lessons / help / human-test-reports |
| `openspec/` | spec-driven 工件流：proposal → specs → design → tasks；tdd_enforcement strict、ordering strict、model_routing_hints |
| Git 流 | 唯一写通道：`feature/{change-id}` → MR → 人审合并 → `Closes {issue}` 自动关 issue |

### 7. 建区脚手架层（bootstrap/ ×6 · 一次性 · 图中位于右侧建设栏）

对 Mika 说「**安装工作区**」，`aicoding-workspace-setup` 一键串联全链（幂等探测断点续传，中断后说「继续安装」即可）：

```
① aicoding-workspace-setup（主入口，chat 内单会话执行）
② aicoding-skills-bootstrap     zip 通道拉技能（本仓库 + GitHub obra/superpowers）
③ aicoding-agent-bootstrap      按 agents/*.md 批量建 7 角色
   → 人工窗口：GitLab 连接 + webhook + env 注入（网页操作）
④ aicoding-project-init         建项目 · 绑仓库 · checkout 验证
⑤ aicoding-orchestration-bootstrap  铺 Mika 接力 + 3 autopilot
⑥ aicoding-harness-bootstrap    铺仓库骨架 → feature/init-harness → MR
   → 人工收尾：人审合并 harness MR + 审宪法
```

### 8. 外部系统（图中沉入最底层平台基座 · 外部支撑系统子区）

- **GitLab（自托管）**：仓库托管、webhook、MR 审查流；MR description 含 `Closes {issue}`，合并后自动关 issue
- **数据库（活库）**：`aicoding-db-schema-export` 的唯一数据源；DDL / 权限 SQL 由发起人**人工执行**（agent 只生成与判读）
- **GitHub 技能源**：obra/superpowers 与本仓库，经 zip 通道导入 Multica 技能库

## 自我学习闭环（持续学习层 `docs/lessons/`）

harness 不是一个静态系统：它把每次踩坑变成可复用的记忆，让角色 agent **越干越准**。这是设计中的"AI 自我学习"部分，贯穿日常运转而非独立模块（架构图右下角为其采集→入库→消费→晋升四步概览）：

![AI 自我学习闭环](./images/lesson-loop.svg)

**采集（四源）**：

- Reviewer 打回 / Tester 测试踩坑 / DevOps 发布踩坑——REVIEW.md 关 3 / 关 9（lesson-check）要求"本次是否产生新教训？是则当场追加条目"
- Mika 兜底巡检：连续打回 ≥2 自动提炼 lesson
- DocKeeper 周级复盘 autopilot：人工测试报告逐 ⚠️ 四源归因（报告 × MR diff × OpenSpec 工件 × test-report），产 lesson 草案走 retro MR

**条目格式**（拒绝空话式教训，必须可执行）：

```
- [YYYY-MM-DD] [change-id] 一句话标题
  ❌ 错误做法（具体到命令/代码形态）
  ✅ 正确做法（具体可执行）
```

**入库**：按角色分文件 `docs/lessons/{Role}.md`（只追加不删除，索引不维护条目防漂移）；散落在 review-report / test-report 的条目由 DevOps 归档 change 时合并落盘；retro 草案经人审合并 MR 入库。

**消费**：AGENTS.md §7 读写矩阵——各角色开工先读 `docs/lessons/index.md` 再读自己角色文件，**历史教训视同本级约束执行**；Reviewer 还会在审查时抽查 Developer 是否读过（review-report 中引用条目编号）。

**晋升（知识进化）**：lesson-check 发现问题命中已有条目 = 曝光不足 → Reviewer 标注「建议晋升宪法」（同类第 2 次出现）→ @Mika 转人类确认 → 写入 CLAUDE.md / REVIEW.md 成为全员红线 → 原条目删除。经验库（越攒越厚）与制度红线（越用越硬）两级进化，每次晋升必经人类确认。

## 架构级铁律

1. **写库 SQL 永不执行**：`ddl.sql` 与 `auth-resource.sql` 同等待遇，三件套（design.md + ddl + auth-resource）由发起人人工执行，agent 只生成与判读
2. **文档是唯一权威源**：`docs/database/` 只能经 `aicoding-db-schema-export` 生成；结构文档双重防守 = 变更随行（第一道）+ harness-audit 周级对账（第二道）
3. **env 永不代写**：环境变量是人工通道，agent 只在自己进程内读
4. **中文传参铁律**：含中文的 CLI 参数值一律经临时文件 `@文件` 传参（GBK 代码页乱码事故）
5. **密码 / token** 只走环境变量或位置指针，永不写入脚本参数、issue 评论或任何文档
6. **不中断批处理**：autopilot run 内不逐条停下等确认
