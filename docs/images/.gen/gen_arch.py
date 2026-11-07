# -*- coding: utf-8 -*-
"""生成 harness 架构图 SVG（标准分层：顶层用户端 → 底层平台基座；Multica 平台拆解融入各层）"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def container(x, y, w, h, label, fill='#f9fafb'):
    box(x, y, w, h, fill=fill, stroke='#9ca3af', sw=1.2, rx=10, dash='6,4')
    text(x + 16, y + 20, label, size=12, fill='#374151', weight=600)

def node(x, y, w, h, fill, stroke, title, subs, tsize=13, ssize=11):
    box(x, y, w, h, fill=fill, stroke=stroke)
    n = len(subs)
    if n == 0:
        text(x + w/2, y + h/2 + 4.5, title, size=tsize, fill='#111827', anchor='middle', weight=600)
        return
    ty = y + (26 if n >= 3 else 24)
    text(x + w/2, ty, title, size=tsize, fill='#111827', anchor='middle', weight=600)
    sy = ty + 17
    for s in subs:
        text(x + w/2, sy, s, size=ssize, fill='#6b7280', anchor='middle')
        sy += 15

def arrow(path, color, marker, dash=None, sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')

def alabel(x, y, s, size=11, fill='#6b7280', anchor='start'):
    text(x, y, s, size=size, fill=fill, anchor=anchor)

# ============ 文档头 ============
lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1460 1340" width="1460" height="1340">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('green', '#059669'), ('purple', '#7c3aed'), ('gray', '#6b7280')]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append('  <rect width="1460" height="1340" fill="#ffffff"/>')

# ============ 标题 ============
text(730, 34, 'sunny-multica 多 Agent 编码 Harness 架构', size=20, fill='#111827', anchor='middle', weight=600)
text(730, 58, '标准分层：顶层用户端 → 底层平台基座 · Multica 平台能力（蓝系标识）已拆解融入 UI / 编排 / 基座各层', size=13, fill='#6b7280', anchor='middle')

# ============ 左侧层级轴 ============
lines.append('  <line x1="36" y1="82" x2="36" y2="1250" stroke="#9ca3af" stroke-width="1.2" stroke-dasharray="4,4" marker-end="url(#arrow-gray)"/>')
text(36, 72, '用户端', size=11, fill='#6b7280', anchor='middle')
text(36, 1272, '平台基座', size=11, fill='#6b7280', anchor='middle')

# ============ L-顶 人工层 ============
box(220, 76, 680, 60, fill='#fff7ed', stroke='#fdba74')
text(560, 101, '人类 · 发起人 / 审阅人（握住全部决策权）', size=14, fill='#9a3412', anchor='middle', weight=600)
text(560, 122, '澄清问答 · 人审四工件 · 人工执行 DDL / 权限 SQL · 合并 MR · env 注入（网页操作，agent 永不代写）', size=11, fill='#6b7280', anchor='middle')

# 人工 <-> UI
arrow('M 500,136 L 500,158', '#ea580c', 'orange')
alabel(488, 150, '派活 · 澄清问答', anchor='end')
arrow('M 640,162 L 640,138', '#7c3aed', 'purple', dash='5,3')
alabel(652, 150, '汇报 · 待拍板')

# ============ L6 交互层 UI 端（Multica 拆解 ①）============
container(80, 162, 960, 118, '交互层 · UI 端 — Multica 客户端（Web / 桌面 / 移动同一工作区）')
node(96, 196, 222, 66, '#eff6ff', '#93c5fd', '看板 · Issue', ['任务派发 · stage 链权威展示', '边做边评论'])
node(330, 196, 222, 66, '#eff6ff', '#93c5fd', 'Chat', ['评论接力 · 人可随时插话', 'agent 在此被触发'])
node(564, 196, 222, 66, '#eff6ff', '#93c5fd', '收件箱 · 提醒', ['人工卡点召唤', '待办聚合'])
node(798, 196, 222, 66, '#eff6ff', '#93c5fd', '用量审计', ['模型用量观测', 'run 记录'])

# UI -> 编排
arrow('M 500,280 L 500,302', '#ea580c', 'orange')
alabel(512, 296, 'issue / chat 触发 agent')

# ============ L5 编排层（Multica 拆解 ②）============
container(80, 306, 960, 148, '编排层 — Mika 编排接力 + 兜底巡检（事件驱动 · 编排信号秒级唤醒）')
node(96, 342, 420, 92, '#dbeafe', '#93c5fd', 'Mika · 编排 agent（Multica 内置）', ['建单守门：issue 五要素校验', 'stage 路由 · 审查点火 · 人工门 metadata', '失败清扫 · lesson 提炼'])
node(528, 342, 240, 92, '#ffffff', '#c4b5fd', '兜底巡检 autopilot', ['assignee Mika · */30 min', '挂起路由 · 失败断点重试', '连败 ≥2 停止 @用户'])
node(780, 342, 240, 92, '#ffffff', '#c4b5fd', '五阶段链 · 权威源', ['stage 1→5 写入 issue 描述', '仓库只认编号 · 不维护链序'])

# 编排 <-> 角色
arrow('M 500,454 L 500,476', '#ea580c', 'orange')
alabel(512, 470, 'stage 点火 · 点名审查')
arrow('M 660,480 L 660,456', '#7c3aed', 'purple', dash='5,3')
alabel(672, 470, '编排信号 @Mika')

# ============ L4 角色执行层 ============
container(80, 480, 960, 138, '角色执行层 — 7 角色 agent（aicoding-agent-bootstrap 批量创建 · model 跟随 runtime）')
roles = [
    ('PM', ['需求澄清', '三件套发起'], '#dbeafe', '#93c5fd'),
    ('Tech-Lead', ['拆解排期', 'tasks / plan'], '#dbeafe', '#93c5fd'),
    ('Developer×N', ['TDD 编码', '可并行 5 实例'], '#dcfce7', '#86efac'),
    ('Reviewer', ['只读审查', '4 关 / 10 关'], '#f3f4f6', '#cbd5e1'),
    ('Tester', ['测试 + QA', '浏览器报告式'], '#dbeafe', '#93c5fd'),
    ('DevOps', ['归档 · tag', 'GitLab 建 MR'], '#dbeafe', '#93c5fd'),
    ('DocKeeper', ['文档对账', '周级 autopilot'], '#ede9fe', '#c4b5fd'),
]
for i, (t, subs, f, s) in enumerate(roles):
    node(100 + i * 134, 516, 126, 76, f, s, t, subs, tsize=12, ssize=10)

# 角色 -> 技能
arrow('M 500,618 L 500,640', '#059669', 'green')
alabel(512, 634, '挂载 · 按需调用')

# ============ L3 技能供给层 ============
container(80, 644, 960, 148, '技能供给层 — multica skill import · zip 通道全量入库')
node(100, 680, 296, 92, '#dbeafe', '#93c5fd', 'openspec 工件系', ['explore / new / continue / apply', 'verify / archive / sync-specs', '使用者：全角色（工件链驱动）'])
node(410, 680, 296, 92, '#dcfce7', '#86efac', 'superpowers 工程系', ['writing-plans（Tech-Lead）', 'executing-plans · TDD · debugging', 'verification（Developer）'])
node(720, 680, 296, 92, '#ffedd5', '#fdba74', 'aicoding 业务系（本仓库 ×8）', ['lookup-ui · config-auth v2/v3', 'db-schema-export · browser-qa', 'harness-audit · human-test-retro'])

# 技能/角色 -> 仓库
arrow('M 500,792 L 500,814', '#2563eb', 'blue')
alabel(512, 808, '读宪法 / 工件 · 写代码与文档')

# ============ L2 项目资产层（目标仓库 harness）============
container(80, 818, 960, 190, '项目资产层 — 目标仓库 harness（aicoding-harness-bootstrap 铺设 · 人审 init MR 合入）')
node(96, 854, 222, 58, '#ffffff', '#fdba74', 'CLAUDE.md · 项目宪法', ['定位 / 模块表 / 保护路径'])
node(330, 854, 222, 58, '#ffffff', '#fdba74', 'AGENTS.md · 协作总纲', ['角色速查 · Git 策略 · 联动矩阵'])
node(564, 854, 222, 58, '#ffffff', '#fdba74', 'REVIEW.md · 审查关卡', ['quick 4 关 / full 10 关'])
node(798, 854, 222, 58, '#ffffff', '#fdba74', 'hooks / guard_write.py', ['block 保护路径写入'])
node(96, 926, 300, 64, '#ffffff', '#fdba74', 'docs/ · 唯一权威源', ['architecture · product · database', 'standards · lessons · 测试报告'])
node(408, 926, 300, 64, '#ffffff', '#fdba74', 'openspec/ · 工件流', ['proposal → specs → design → tasks', 'tdd / ordering strict'])
node(720, 926, 300, 64, '#ffffff', '#fdba74', 'Git 流 · 唯一写通道', ['feature/{change-id} → MR', '禁直推 · commit 即 push'])

# 仓库 -> 基座 GitLab
arrow('M 800,1008 L 800,1030', '#2563eb', 'blue')
alabel(812, 1024, 'feature → MR · 人审合并 · Closes {issue}')

# ============ L1 平台基座（Multica 拆解 ③ + 外部支撑）============
container(80, 1034, 960, 228, '平台基座 — Multica 运行底座（自托管）+ 外部支撑系统')
container(96, 1068, 548, 180, 'Multica 运行底座', fill='#f0f6ff')
node(112, 1102, 164, 130, '#eff6ff', '#93c5fd', 'Go 后端 + PostgreSQL', ['工作区状态 · 权限', 'WebSocket 实时通道', 'issue / run 持久化'], ssize=10)
node(288, 1102, 164, 130, '#eff6ff', '#93c5fd', 'Runtime 守护进程（本机）', ['拉起 agent CLI', 'Claude Code 等 26 种', '进程级隔离'], tsize=11, ssize=10)
node(464, 1102, 164, 130, '#eff6ff', '#93c5fd', 'Autopilot 调度器（cron）', ['定时触发 autopilot run', '兜底巡检 / 文档对账', '人工测试复盘 · run_only'], tsize=11, ssize=10)
container(664, 1068, 360, 180, '外部支撑系统', fill='#f9fafb')
node(676, 1102, 336, 44, '#ffffff', '#d1d5db', 'GitLab（自托管）', ['仓库 · webhook · MR 审查 · 合并自动关单'], tsize=12, ssize=10)
node(676, 1152, 336, 44, '#ffffff', '#d1d5db', '数据库（活库）', ['schema 导出源 · DDL/权限 SQL 人工执行'], tsize=12, ssize=10)
node(676, 1202, 336, 44, '#ffffff', '#d1d5db', 'GitHub 技能源', ['obra/superpowers + 本仓库 · zip 通道导入'], tsize=12, ssize=10)

# 基座向上供给：Runtime/Autopilot -> 角色层（沿左外侧走线，避免穿节点）
arrow('M 370,1234 L 370,1254 L 62,1254 L 62,554 L 74,554', '#ea580c', 'orange', dash='6,4', sw=1.5)
text(50, 850, '基', size=10, fill='#ea580c', anchor='middle')
text(50, 864, '座', size=10, fill='#ea580c', anchor='middle')
text(50, 878, '供', size=10, fill='#ea580c', anchor='middle')
text(50, 892, '给', size=10, fill='#ea580c', anchor='middle')

# 技能 -> 基座数据库（右侧走廊；语义见 DB 节点「schema 导出源」）
arrow('M 1040,730 L 1054,730 L 1054,1171 L 1016,1171', '#2563eb', 'blue', sw=1.5)

# ============ 右侧：建区脚手架（一次性）============
container(1100, 162, 330, 646, '建区脚手架（bootstrap ×6 · 一次性）')
boots = [
    ('① workspace-setup', ['一键主入口 · chat 内执行', '幂等 · 断点续传']),
    ('② skills-bootstrap', ['zip 通道拉技能', '本仓库 + obra/superpowers']),
    ('③ agent-bootstrap', ['按 agents/*.md', '批量建 7 角色']),
    ('④ project-init', ['建项目 · 绑仓库', 'checkout 验证']),
    ('⑤ orchestration', ['铺 Mika 接力', '+ 兜底巡检 autopilot']),
    ('⑥ harness-bootstrap', ['铺仓库骨架', 'feature/init → MR']),
]
for i, (t, subs) in enumerate(boots):
    f, s = ('#ffedd5', '#fdba74') if i == 0 else ('#ffffff', '#d1d5db')
    node(1116, 202 + i * 92, 298, 78, f, s, t, subs, tsize=12)
text(1116, 762, '⏸ 人工窗口 A：GitLab 连接 · webhook · env 注入', size=10, fill='#9a3412')
text(1116, 780, '⏸ 人工窗口 B：人审 init MR + 宪法首版', size=10, fill='#9a3412')

# 脚手架 -> 主列（一次性铺设）
arrow('M 1100,490 L 1042,490', '#6b7280', 'gray', dash='5,3', sw=1.5)

# ============ 右下：持续学习闭环（贯穿日常运转）============
container(1100, 840, 330, 422, '持续学习闭环（贯穿日常运转）')
loops = [
    ('① 采集 · 四源', ['Reviewer / Tester / DevOps', '当场追加 · Mika 连打 ≥2 提炼']),
    ('② 入库 · 只追加', ['docs/lessons/{Role}.md', '散落条目归档时合并落盘']),
    ('③ 消费 · 视同约束', ['开工先读 index → 角色文件', 'Reviewer 抽查已读引用']),
    ('④ 晋升 · 知识进化', ['同类第 2 次 → 人类确认', '写入宪法红线 · 删原条目']),
]
for i, (t, subs) in enumerate(loops):
    node(1116, 876 + i * 94, 298, 74, '#fefce8', '#fde68a', t, subs, tsize=12, ssize=10)
for i in range(3):
    arrow('M 1265,' + str(876 + 74 + i * 94 + 3) + ' L 1265,' + str(876 + 94 + i * 94 - 4), '#d97706', 'orange', sw=1.4)

# ============ 图例 ============
lx = 96
def legend_item(color, dash, label, marker_color, swatch=None):
    global lx
    d = f' stroke-dasharray="{dash}"' if dash else ''
    if swatch:
        lines.append(f'  <rect x="{lx}" y="1300" width="22" height="13" rx="3" fill="{swatch}" stroke="#93c5fd"/>')
    else:
        lines.append(f'  <line x1="{lx}" y1="1306" x2="{lx+26}" y2="1306" stroke="{color}" stroke-width="1.8"{d} marker-end="url(#arrow-{marker_color})"/>')
    text(lx + 32, 1310, label, size=11, fill='#6b7280')
    lx += 32 + sum(11 if ord(ch) > 255 else 6 for ch in label) + 26

legend_item('#ea580c', None, '橙 · 控制 / 点火', 'orange')
legend_item('#2563eb', None, '蓝 · 数据 / 工件流', 'blue')
legend_item('#059669', None, '绿 · 技能挂载', 'green')
legend_item('#7c3aed', '5,3', '紫虚 · 信号 / 人工审批', 'purple')
legend_item('#ea580c', '6,4', '橙虚 · 基座供给（拉起 CLI · cron）', 'orange')
legend_item('#6b7280', '5,3', '灰虚 · 一次性建区', 'gray')
legend_item(None, None, '蓝底 · Multica 平台组件', None, swatch='#eff6ff')

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/harness-architecture.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
