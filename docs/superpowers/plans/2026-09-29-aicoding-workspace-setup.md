# aicoding-workspace-setup 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新建编排型安装主 skill `aicoding-workspace-setup`，一次会话串联 5 个 bootstrap skill 完成新工作区建设（人只在开头问答 + 一次网页操作窗口接入，结尾人审 MR）。

**Architecture:** 主 skill 是指挥棒不复制子流程——SKILL.md 定义 8 阶段时序/断点探测判据/失败分级，两个 references 附带文档解决鸡生蛋（精简拉取通道）与人工窗口（网页操作清单模板）。断点续传靠幂等探测，无状态文件。

**Tech Stack:** 纯 Markdown 说明书（Multica skill 格式：frontmatter + 正文），无代码。

**Spec:** `docs/superpowers/specs/2026-09-29-aicoding-workspace-setup-design.md`

## Global Constraints

- skill 名固定 `aicoding-workspace-setup`，目录 `bootstrap/aicoding-workspace-setup/`
- 所有 skill 名引用与现有目录名精确一致：`aicoding-skills-bootstrap` / `aicoding-agent-bootstrap` / `aicoding-project-init` / `aicoding-orchestration-bootstrap` / `aicoding-harness-bootstrap` / `aicoding-db-schema-export`
- 本仓库地址（拉取通道固定写入）：`https://github.com/wengjinlin/sunny-multica-skills`
- superpowers 系列来源：`https://github.com/obra/superpowers`（agent-bootstrap 第 0 步注释的硬依赖：Tech-Lead/Developer 的 plan/TDD 能力）
- 文档中任何 CLI 示例含中文参数值必须 `@文件` 形式（multica_call.py 通道），禁止命令行内联中文
- 密码/token/secret 永不写入任何产出文档；env 永不代写（人工通道）
- 铁律措辞沿用各子 skill 原文风格（「不中断批处理」「只报告不修代码」等）
- 说明书类产物无单元测试，每任务验证 = 静态走查（步骤中给出确切核对清单），commit 收尾

## Review Focus

说明书最可能咬人的五类失败（每项的走查测试在所属任务内）：

1. **鸡生蛋断裂**——第②步若依赖 skills-bootstrap 已挂载则首跑必死。测试（Task 1）：走查 pull-repo-skills.md 全流程只用 git/multica CLI + 自身文档，零处引用「调用 aicoding-skills-bootstrap skill」。
2. **人工停等遗漏**——某子 skill 的隐藏问询点（如 harness 的 MR 目标分支）跑到中段突然停等，破坏「④后全自动」。测试（Task 3）：grep 5 个子 skill 全文的「问用户/等待/确认/停下」字样，逐一映射到 ①④ 或显式声明不停等。
3. **断点判据不可探测**——判据表写了探测不出的东西。测试（Task 3）：每条判据必须标注探测命令；不可探测项（env）显式标注「不可探测，靠对话上下文」。
4. **中文乱码入库**——文档里给出含中文直传的 CLI 示例会被照抄出乱码。测试（Task 1/3）：全部 CLI 示例逐条检查，中文参数一律 `@文件`。
5. **superpowers 系列漏拉**——Tech-Lead/Developer 缺 plan/TDD 能力。测试（Task 1）：来源清单含 obra/superpowers 且枚举方式不依赖其目录结构预设。

---

### Task 1: 拉取通道附带文档 pull-repo-skills.md

**Files:**
- Create: `bootstrap/aicoding-workspace-setup/references/pull-repo-skills.md`
- Modify: `docs/superpowers/specs/2026-09-29-aicoding-workspace-setup-design.md`（§4② 补 superpowers 来源一句）

**Interfaces:**
- Consumes: `bootstrap/aicoding-skills-bootstrap/SKILL.md`（方法论权威源，提炼而非复制）
- Produces: 主 skill 第②步的执行依据文档；被 Task 3 的 SKILL.md 以 `references/pull-repo-skills.md` 引用

- [ ] **Step 1: 写 pull-repo-skills.md**

章节骨架与各节确切内容：

```markdown
# 第②步拉取通道：技能批量入库（精简固定版）

> 场景固定（新工作区首装），方法论提炼自 aicoding-skills-bootstrap skill；
> 本文档自带完整操作步骤，不依赖该 skill 已挂载（鸡生蛋：本步执行时库里只有本 skill）。

## 来源（固定两个）

| 来源 | 仓库 | 范围 |
|---|---|---|
| 主 | https://github.com/wengjinlin/sunny-multica-skills | skills/ 与 bootstrap/ 下全部含 SKILL.md 的目录 |
| 辅 | https://github.com/obra/superpowers | 仓库内全部含 SKILL.md 的目录（Tech-Lead/Developer 的 plan/TDD 能力依赖） |

## 步骤

1. 逐来源 `git clone --depth 1 <repo-url> <临时目录>`
2. 枚举：`glob **/SKILL.md`（不预设目录层级，结构无关），父目录即 skill 目录
3. 逐 skill 打 zip——zip 内**顶层就是 SKILL.md 与附带文件平铺**（不打顶层目录）；
   排除 `.git` / `__pycache__` / `node_modules` 与 `.pyc` / `.zip`：
   （内嵌 skills-bootstrap 同款 python zipfile 代码块，逐字复制其第 5 步脚本，
    src 参数说明改为「<clone临时目录>/<skill目录>」）
4. 前台串行导入，结果先落盘再解析：
   multica skill import --file "./skill-<name>.zip" --on-conflict overwrite --output json > "./import-<name>.json" 2>&1
   jq -r '.status // "PARSE_FAIL"' "./import-<name>.json"
   PARSE_FAIL 时 cat 原始输出诊断，可重试一次；单个失败不阻断其余
5. 附件校验补漏（强制，防附带文档丢失）：对每个导入成功项——
   枚举源目录文件清单去掉 SKILL.md 本体得「应有效」；
   `multica skill files list <skill-id> --output json` 得「实有集」；
   缺失逐个补传：multica skill files upsert <skill-id> --path "<zip内相对路径>" --content-file "<本地clone中该文件>"
   补传后 list 复核；仍不符（超限被拒等）如实进报告
6. 挂载（本 skill 执行者 Mika 自用）：
   `multica skill list --output json` 按 name 解析 id；
   `multica agent skills add <Mika-UUID> --skill-ids <aicoding-skills-bootstrap,aicoding-agent-bootstrap,aicoding-project-init,aicoding-orchestration-bootstrap,aicoding-harness-bootstrap,aicoding-db-schema-export 的id列表>`
   （add 是追加式；**禁止 set**，会清空已有绑定；Mika-UUID 从 multica agent list 取）
7. 汇总表：created / updated / failed + 原因 + 附件校验结果；删除临时 json/zip/clone 目录

## 陷阱（照搬 skills-bootstrap 实测陷阱表中适用项）

- --url 直导只入库 SKILL.md，附带文档全丢 → 一律本地 zip + 第 5 步校验补漏
- skill files list 只列附件不含 SKILL.md 本体 → 校验对照先去掉本体
- 批量循环 $(...) 内联管道 + jq 静默失败 → 结果一律先写文件再 jq
- 超限：单文件 1MiB / 每包 8MiB / 256 文件 / 上传 16MiB → 打包排除 node_modules 等；仍超限如实报告
- overwrite 遇「非技能创建者」返回 failed → 属预期保护：报告原因，新工作区首装不会遇到（库为空全走 created）
```

- [ ] **Step 2: 修 spec §4② 补 superpowers 来源**

在 spec §4② 第一条 bullet「照 references/pull-repo-skills.md 执行」后追加一行：
`- 来源含两个：本仓库全部技能 + superpowers 系列（GitHub 源 obra/superpowers，Tech-Lead/Developer 的 plan/TDD 能力依赖）`

- [ ] **Step 3: 走查核对（Review Focus 1/4/5）**

1. 零处出现「调用 aicoding-skills-bootstrap」字样（鸡生蛋）
2. 全部 CLI 示例无中文直传（含 import 的文件名参数均为 ASCII 模式）
3. 来源表含 obra/superpowers；枚举用 glob 不预设目录
4. zip 打包/校验补漏/陷阱表与 skills-bootstrap 原文逐条对照，无关键陷阱遗漏（对照文件：`bootstrap/aicoding-skills-bootstrap/SKILL.md` 全文）

- [ ] **Step 4: Commit**

```bash
git add bootstrap/aicoding-workspace-setup/references/pull-repo-skills.md docs/superpowers/specs/2026-09-29-aicoding-workspace-setup-design.md
git commit -m "feat: workspace-setup 第②步拉取通道附带文档"
```

### Task 2: 人工窗口清单模板 human-checklist.md

**Files:**
- Create: `bootstrap/aicoding-workspace-setup/references/human-checklist.md`

**Interfaces:**
- Consumes: `bootstrap/aicoding-project-init/SKILL.md` 第 1 步三事项原文（A/B 项照抄）；`bootstrap/aicoding-agent-bootstrap/agents/*.md` 的「## 自定义 env」节（固定快照）
- Produces: 主 skill 第④步输出给用户的清单模板；含占位符 `{{REPO_URL}}` `{{DB_PASSWORD_HINT}}`，Task 3 引用

- [ ] **Step 1: 写 human-checklist.md**

章节骨架与确切内容：

```markdown
# 第④步人工窗口清单（一次做完，回复「完成」继续）

> 执行到本步 = 技能已入库、角色 agent 已建好，以下网页操作均可进行。
> 全部完成后回复「完成」；卡住哪条就说明哪条，Mika 给排查指引后重验。
> 值（token/密码/secret）走安全渠道，永不贴进对话、issue 或评论。

## A. GitLab 自托管连接（workspace 级，每工作区一次）
（照抄 project-init 第 1 步 A 项三小条原文：新建连接 / 记 webhook URL 与 secret / repo add 不注册 webhook）

## B. GitLab webhook（仓库级，仓库 {{REPO_URL}} 每仓库一次）
（照抄 project-init 第 1 步 B 项三小条原文：粘贴 A 所得勾 push+MR events / Test Hook 得 HTTP 200（401=secret 填错）/ 老 GitLab 11.x 不可跳过）

## C. 环境变量注入（agent 级；入口：Multica 网页 → 该 agent 详情 → 环境变量）

### 必配（不配则对应环节降级或失败）

| agent | 变量 | 用途 |
|---|---|---|
| Mika | GITLAB_TOKEN | GitLab project access token，第⑦步自动建 harness MR 用 |
| DevOps | GITLAB_TOKEN | 建 MR 用 |
| DocKeeper | GITLAB_TOKEN | 文档对账 MR 用 |
| Tester | TEST_ACCOUNT | 浏览器 QA 登录账号 |
| Tester | TEST_PASSWORD | 浏览器 QA 登录密码 |
| Tester | TEST_ROLE | 测试账号角色名（权限绑定提示用） |
{{DB_PASSWORD_HINT}}

### 选配（PATH 可用时可不填；构建/测试命令解析用）

| agent | 变量 | 用途 |
|---|---|---|
| Developer | MVN_BIN / JAVA_HOME / NODE_BIN | 本机构建工具绝对路径（Windows 形如 /c/.../mvn.cmd） |
| Tester | MVN_BIN / JAVA_HOME / NODE_BIN | 同上（测试命令用） |

> 权威源：agents/*.md 各文件「## 自定义 env」节——本表是快照，配置文件更新后以文件为准，改配置须同步改本表。
```

其中 `{{DB_PASSWORD_HINT}}` 由 SKILL.md 第①步判定后替换：密码在配置文件 → 整行删除（替换为空）；密码不在配置 → 替换为 `| Developer | DB_PASSWORD | 数据库密码（{{DB_PASSWORD_HINT 指明：连库导表结构文档用}}） |` 并归必配表。

- [ ] **Step 2: 走查核对**

1. A/B 节与 project-init 第 1 步原文逐条一致（对照 `bootstrap/aicoding-project-init/SKILL.md:49-66`）
2. env 表与 agents/*.md 实际「## 自定义 env」节逐 agent 对照（当前 7 文件：PM/Reviewer/Tech-Lead 为「（无）」不列；DevOps/DocKeeper GITLAB_TOKEN；Developer/Tester 构建工具类；Tester 另有 TEST_* 三项）
3. 「值不入对话/评论」警示在文档头与 C 节各出现一次
4. 占位符仅 `{{REPO_URL}}` `{{DB_PASSWORD_HINT}}` 两个，与 Task 3 SKILL.md 用法一致

- [ ] **Step 3: Commit**

```bash
git add bootstrap/aicoding-workspace-setup/references/human-checklist.md
git commit -m "feat: workspace-setup 人工窗口清单模板"
```

### Task 3: 主文件 SKILL.md

**Files:**
- Create: `bootstrap/aicoding-workspace-setup/SKILL.md`

**Interfaces:**
- Consumes: spec §4（时序）§5（判据表）§6（失败分级）§7（大纲）；Task 1/2 两个 references 文件
- Produces: 完整可导入的 skill；被 Task 4 的 README 登记

- [ ] **Step 1: 写 SKILL.md**

frontmatter 与正文骨架（正文各节确切内容来源标注）：

```markdown
---
name: aicoding-workspace-setup
description: 新 Multica 工作区一键安装：一次会话串联技能入库→角色 agent 创建→项目绑定仓库→编排层→仓库 harness 全链，人工仅开头一轮问答+一次网页操作窗口，结尾人审 harness MR，中间全自动；断点续传（重跑跳过已完成阶段）。TRIGGER：「安装工作区」「一键安装」「初始化新工作区」「搭建新工作区」「workspace setup」。
---

# aicoding-workspace-setup：一键安装工作区

（定位段：编排型主 skill——只管时序/探测/人工窗口/终局报告，各环节做法归对应子 skill；
执行者 Mika；全程 chat 内直执行，不开 issue 不派子任务——issue 断链说明照抄 project-init 措辞）

## 输入
$ARGUMENTS 可选 =「项目名 仓库URL」；未给全则第①步问答补齐。

## 执行时序（8 阶段）
（spec §4 时序图原样内嵌，随后每阶段一小节，每节固定四要素：
做什么 / 调用哪个子 skill / 断点探测判据 / 产物。关键内容逐字取自 spec：
① 问答四类信息表（项目名+仓库URL / MR目标分支 / 数据库探测与连接信息 / 密码来源三选一）+ 预告网页操作
② 照 references/pull-repo-skills.md 执行；拉完给 Mika 补挂 6 个 skill
③ Skill 调用 aicoding-agent-bootstrap；收集其 env 待办与缺失登记供④⑤
④ 渲染 references/human-checklist.md（替换两占位符）等「完成」；
   repo add + checkout 间接验证 A/B（幂等重验）；env 不可探测沿用原链设计
⑤ Skill 调用 aicoding-project-init（项目名/URL 用①值不再问；三事项已在④完成）
⑥ Skill 调用 aicoding-orchestration-bootstrap（无人工点）
⑦ Skill 调用 aicoding-harness-bootstrap（数据库信息/分支/密码来源已齐不停等；
   用户当场供密码→单次命令 env 传入用完即弃）；
   MR 自动建：Mika 用自身 GITLAB_TOKEN 走 GitLab API（JSON body 文件防中文 500，
   PRIVATE-TOKEN: $GITLAB_TOKEN，API base 与 project-id 从项目上下文取——
   同 aicoding-harness-audit 既有做法）；失败降级人工待办给分支名与指引，不回滚
⑧ 人审合并 harness MR + 审宪法）

## 断点续传
（spec §5 判据表六行原样内嵌；附注：新会话续跑时④完成度以探测间接判断，
需要时重发清单确认——宁可重问不瞎猜）

## 失败处置分级
（spec §6 三级表 + 继承铁律四条原文）

## 终局报告
表：8 阶段 × 产物（UUID/链接/跳过原因）；缺失登记汇总；
唯一剩余人工待办 = 审 MR 合并（附 MR 链接或降级指引）；后续微调路径一句。

## 铁律
（继承清单：中文 @文件 传参 / 密码永不入库入评论 / 写库 SQL 永不执行 /
env 永不代写 / 不中断批处理 / 每阶段 chat 简短进度只在人工点停等）

## 维护约定
时序/判据/清单模板改动改本 skill；单环节做法改动改对应子 skill；
子 skill 保持独立可分步手动运行。
```

- [ ] **Step 2: 走查核对（Review Focus 2/3/4）**

对 5 个子 skill 全文 grep 停等语义（`bootstrap/*/SKILL.md` 搜「问用户|等待|确认|停下|向用户|问一次|二选一」），逐条映射：
- skills-bootstrap：输入 repo/only → 本场景固定（不问）
- agent-bootstrap：env 待办 → ④C；缺失登记 → 终局报告
- project-init：三事项 → ④A/B/C；项目名/URL 确认 → ①；验证失败停等 → ④重验
- orchestration-bootstrap：无停等 → 确认无漏
- harness-bootstrap：DB 预检收集/密码确认 → ①；MR 目标分支问用户 → ①；连接不就绪二选一 → ①密码来源三选一覆盖；hook 落位无人工 → 确认
判据表六行均有探测命令，env 类标注「不可探测，靠对话」；CLI 示例无中文直传。

- [ ] **Step 3: Commit**

```bash
git add bootstrap/aicoding-workspace-setup/SKILL.md
git commit -m "feat: workspace-setup 主 skill 编排流程"
```

### Task 4: README 登记与收尾一致性

**Files:**
- Modify: `README.md`（bootstrap 表 + 安装链节）

**Interfaces:**
- Consumes: Task 3 产物名与定位
- Produces: 仓库 README 与新 skill 一致

- [ ] **Step 1: 更新 README**

bootstrap 表首行前插入：

```markdown
| `aicoding-workspace-setup` | **一键安装主入口**：一次会话串联下列全部脚手架（技能入库→agent→项目→编排→harness），人工仅开头一轮问答+一次网页操作窗口，结尾人审 MR；断点续传 |
```

「新工作区安装链顺序」节改写为两段式：

```markdown
### 新工作区安装（推荐：一键）

手动导入本仓库 zip 挂给 Mika（`multica skill import --file <zip>` + `multica agent skills add <Mika> --skill-ids <id>`），
对 Mika 说「安装工作区」即走 `aicoding-workspace-setup` 全自动串联。

### 分步手动（备选）

（保留原 6 行安装链代码块原样）
```

- [ ] **Step 2: 走查核对**

README 表行数 = 6 个 bootstrap；一键入口命令与 SKILL.md/初始入口描述一致；原分步链保留未删。

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README 登记一键安装入口"
```
