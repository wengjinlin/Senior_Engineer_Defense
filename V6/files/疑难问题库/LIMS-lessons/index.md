# lessons — 项目经验库（持续学习层，按角色分文件）

> 【归档注记 2026-11-07】原仓库实物本表缺 Prototyper 行（骨架复制时未同步；Prototyper.md 文件及其 7 条实录实际在案），归档副本评审时补登此行。

> **结构**：本目录 = 本索引 + 每角色一个 md 文件（条目只写角色文件，**不在本索引维护条目或计数**，防索引漂移）。
>
> **机制**：Reviewer 打回 / Tester 测试踩坑 / DevOps 发布踩坑时追加条目；DevOps 归档 change 时把散落在 review-report / test-report 的条目合并进对应角色文件；同类错误第 2 次出现由 Reviewer 标注「建议晋升宪法」，经人类确认后写入 CLAUDE.md / REVIEW.md 红线并删除原条目。
>
> **条目格式**（必须含日期、来源 change-id、❌/✅ 对照动作；拒绝空话式教训）：
>
> - [YYYY-MM-DD] [change-id] 一句话标题
>   ❌ 错误做法（具体到命令/代码形态）
>   ✅ 正确做法（具体可执行）

## 角色索引

| 角色 | 文件 | 说明 |
|---|---|---|
| Prototyper | [Prototyper.md](Prototyper.md) | 前端原型链踩坑（dev server/HMR/组件库插槽/端口分配） |
| PM | [PM.md](PM.md) | 需求澄清与工件（proposal/specs/design/api/ddl）产出踩坑 |
| Tech-Lead | [Tech-Lead.md](Tech-Lead.md) | 拆解 tasks / plan.md / 排他文件清单踩坑 |
| Developer | [Developer.md](Developer.md) | 编码与 TDD 循环踩坑 |
| Reviewer | [Reviewer.md](Reviewer.md) | 审查方法论教训（Reviewer 自身只读，条目由 DevOps 归档落盘） |
| Tester | [Tester.md](Tester.md) | 浏览器 QA 与测试报告踩坑 |
| DocKeeper | [DocKeeper.md](DocKeeper.md) | 文档对账与复盘踩坑 |
| DevOps | [DevOps.md](DevOps.md) | 归档 / tag / MR / 发布踩坑 |

<!-- 分析指引：角色文件与索引行按 Multica agent list 对齐（与 AGENTS.md §3 速查表同源）；每个角色文件从同目录 _template.md 复制生成。各角色读/写分区见 AGENTS.md §7 矩阵 -->
