# 目标仓库 harness 结构 —— agent 的制度与字典

> 平台侧（Multica + Mika + 7 角色）见 [harness-architecture.md](./harness-architecture.md)，日常运转见 [harness-runtime-flow.md](./harness-runtime-flow.md)。本文专讲**被治理的那个目标仓库**：里面铺了什么、每个文件管什么、怎么建起来、怎么防漂移。

![目标仓库 harness 结构图](./images/harness-repo-structure.svg)

## 一图总览

目标仓库 harness = **三大治理文档（红线）+ docs/ 字典体系（唯一权威源）+ 机制硬约束 + 一次性建设 + 双重防漂移**。前两者管"agent 读什么"，机制层管"agent 想越界时被什么拦住"，建设与防漂移管"这套制度怎么落地、怎么不过期"。

## ① 治理文档（红线层）—— 开工必读，违反即打回

| 文档 | 定位 | 核心内容 |
|---|---|---|
| **CLAUDE.md** | 项目宪法 | 15 节红线：§0 适用范围 / §1 定位 / §2 模块表（业务域↔模块↔表前缀）/ §3 基础设施 / §4 构建命令 / §5 TDD 纪律 / §6 分层 / §7 命名 / … §10 保护路径。每个 agent 开工第一件事就是读它 |
| **AGENTS.md** | 协作总纲 | 角色速查表、Git 策略（`feature/{change-id}`、禁直推）、OpenSpec 工件结构、**变更联动矩阵**（改了 X 必须同步查 Y）、**§7 lessons 读写矩阵**（每角色读什么写什么） |
| **REVIEW.md** | 审查关卡 | quick 4 关：spec-align / risk-check / **lesson-check** / archive；full 10 关覆盖测试、分层、命名、安全；protected 路径变更另加人工复核 |

三份文档相互引用形成闭环：宪法立红线 → 总纲定协作 → 关卡验执行。

## ② docs/ 字典体系 —— 唯一权威源

**`docs/index.md` 是唯一入口**：目录导航 + 按角色必读顺序 + 维护规则 + DocKeeper 对账基线表。任何人（含 agent）查文档先从这里进。

| 子目录 | 内容 | 主要读者 | 生成方式 |
|---|---|---|---|
| `architecture/index.md` | 模块定位字典、高风险区、ADR、技术债 | 全角色 | 人工 + 周级对账 |
| `architecture/implicit-contracts.md` | 隐性约定：口头约定、历史包袱、代码看不出来的规则 | 全角色 | 人工积累 |
| `product/index.md` | 业务域划分、术语表、状态机、业务校验铁律 | PM 为主 | PM 维护 |
| `database/`（index + tables/） | 全库表清单 + 每表字段详情 | Developer / Reviewer | **唯一通道 `aicoding-db-schema-export`** |
| `standards/`（api · database · testing） | 三篇详单 + 评审检查清单，与宪法红线两向引用 | Developer / Reviewer | 人工 + 对账 |
| `templates/design-review-template.md` | 前端设计人审模板（逐字段选型 + 偏离声明） | PM / Reviewer | 静态模板 |
| `help/`（能力清单 + 7 篇能力文档） | 平台能力使用指南（po / s3 / kafka…），涉平台集成需求必读 | 全角色 | 人工 |
| `lessons/`（index + {Role}.md） | 错题本：`[日期][change-id] ❌/✅ 对照` 条目，开工必读视同本级约束 | 各角色 | 人审 MR 入库 |
| `human-test-reports/` | 人工测试报告（`日期-分支名.md`），**人类维护、agent 只读**，复盘归档 | DocKeeper 读 | 人类写 |

## ③ 机制层 —— 不靠自觉靠拦截

文档说了不算数的地方，由三道机制硬约束兜底：

1. **`.claude/hooks/guard_write.py`**：挂在 agent 工具调用前的 PreToolUse 钩子。对保护路径（`application*.yml` / `db/` / `sql/` / `settings.xml` / `pom.xml`）的写入**直接 block**——要改必须先在 design.md 声明且 Reviewer 过审。agent 想绕过？钩子根本不给执行机会。
2. **`openspec/config.yaml`**：spec-driven 工件流引擎。`tdd_enforcement: strict`（没有测试不让过）、`ordering: strict`（proposal → specs → design → tasks 顺序不能乱）、`model_routing_hints`（explore 小模型 / design·review 大模型 / apply 中档，按工序省钱）、`protected_paths`。
3. **Git 流（唯一写通道）**：所有提交只能走 `feature/{change-id}` 分支 → MR → 人工合并，直推保护分支被平台侧拒绝；commit 后立即 push（跨 runtime 可见）。

## ④ 建设流程（aicoding-harness-bootstrap · 一次性）

对 Mika 说「铺设仓库 harness」，chat 内单会话五步完成（幂等，中断说"继续"即可续传）：

| 步骤 | 动作 | 关键点 |
|---|---|---|
| ① 前置 | checkout · 建分支 · 数据库预检 | 已有治理文档的仓库 → 切**对齐模式**（补缺节不覆盖定制）；密码两路校验 |
| ② 铺 skeleton | 20+ 文件原样拷入 | 含模板与 `{{占位符}}`；skeleton/ 是结构权威源 |
| ③ 代码分析填充 | 逐条消灭 `{{占位符}}` | **每条须有代码证据**，禁止编造；库文档走 `aicoding-db-schema-export` 专用 skill |
| ④ hook 自测 | guard_write.py 落位 | 写保护路径应被 block、普通路径应放行，自测通过才算装好 |
| ⑤ 交付 | `feature/init-harness` → MR | **占位符未清零不得 commit**；人审 MR + 审宪法首版 |

## ⑤ 文档漂移双重防守

| 防线 | 机制 | 内容 |
|---|---|---|
| 第一道 · 变更随行（主防线） | 流程内嵌 | 代码结构变更 → **同一 change 内**更新对应文档；Tech-Lead 拆解时显式排 task，禁止事后补文档 |
| 第二道 · 周级对账（兜底） | DocKeeper autopilot（周一 08:17） | 调 `aicoding-harness-audit`：从上次基线到 `origin/master` 的 diff 映射为文档更新项，走 `feature/doc-audit-{date}` MR；基线表随 MR 前移；无差异静默不打扰 |

## 角色必读路由（AGENTS.md §7 的落地）

| 角色 | 必读顺序 |
|---|---|
| PM | product → architecture → database → implicit-contracts（+ help，涉及时） |
| Tech-Lead | architecture/index → lessons 全部 |
| Developer | architecture（代码落位）→ standards 对应篇 → lessons/Developer |
| Tester | standards/testing → lessons/Tester |
| Reviewer | standards 全部 → lessons 全部 |
| DevOps | lessons 全部 |

## 对齐模式与维护约定

- **对齐模式**：仓库已有 CLAUDE.md 等治理文档时，bootstrap 对照 skeleton 骨架**补缺节、不覆盖定制**——尊重既有制度，只补缺口。
- **结构权威源**：skeleton/ 决定章节结构；章节变更须回写 skeleton，内容演进走 MR；周级对账兜底防漂移。
- **database/ 例外**：库表文档永远只能由 `aicoding-db-schema-export` 从活库生成，人工不得手改——手改必与库漂移。

## 铁律回响

平台侧六条铁律（见 [架构文档](./harness-architecture.md#架构级铁律)）在仓库侧的具体投射：写库 SQL 永不执行 → guard_write.py 拦 sql 目录；文档唯一权威源 → database/ 单通道生成 + 双重防守；其余红线 → CLAUDE.md 十五节逐一落地。
