# -*- coding: utf-8 -*-
"""生成 harness 概念科普图 SVG（一页看懂版）"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def node(x, y, w, h, fill, stroke, title, subs, tsize=13, tdy=26):
    box(x, y, w, h, fill=fill, stroke=stroke)
    text(x + w/2, y + tdy, title, size=tsize, fill='#111827', anchor='middle', weight=600)
    sy = y + tdy + 19
    for s in subs:
        text(x + w/2, sy, s, size=11, fill='#6b7280', anchor='middle')
        sy += 16

def arrow(path, color, marker, dash=None, sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#arrow-{marker})"/>')

BLUE, ORANGE, GRAY, RED = '#2563eb', '#ea580c', '#6b7280', '#dc2626'

lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1360 720" width="1360" height="720">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', BLUE), ('orange', ORANGE), ('gray', GRAY), ('red', RED)]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append('  <rect width="1360" height="720" fill="#ffffff"/>')

text(680, 34, '一张图看懂 sunny-multica harness', size=20, fill='#111827', anchor='middle', weight=600)
text(680, 56, '一条需求流水线（上） + 三个幕后支撑（中） + 三条铁律（下）· 人只在橙色两站出现', size=13, fill='#6b7280', anchor='middle')

# ============ 流水线带 ============
box(40, 100, 1280, 162, fill='#f9fafb', stroke='#e5e7eb', sw=1, rx=12)

stations = [
    (62,   '#dbeafe', '#93c5fd', 'PM · 产品', ['chat 澄清需求', '写设计四件套', '+ 权限 SQL 草案'], 26),
    (218,  '#fed7aa', '#f97316', '人工门 ①', ['人审设计四件套', '亲手执行', '数据库脚本'], 26),
    (374,  '#dbeafe', '#93c5fd', 'Tech-Lead', ['拆任务 · 排依赖', '产出 plan.md', '（写作计划 SOP）'], 26),
    (530,  '#dbeafe', '#93c5fd', 'Dev ⇄ Rev', ['程序员 TDD 写码', '审查员只读把关', '不过 → 打回返工'], 26),
    (686,  '#dbeafe', '#93c5fd', 'Tester', ['跑集成/边界测试', '浏览器页面 QA', '出测试报告'], 26),
    (842,  '#dbeafe', '#93c5fd', 'DevOps', ['归档 · 打 tag', '调 GitLab API', '建 MR 待审'], 26),
    (998,  '#fed7aa', '#f97316', '人工门 ②', ['人审 MR', '点合并', '（上线拍板）'], 26),
    (1154, '#dcfce7', '#86efac', '完成', ['MR 合并后', 'issue 自动关闭', '经验沉淀归档'], 26),
]
for x, f, s, t, subs, tdy in stations:
    node(x, 124, 132, 104, f, s, t, subs, tsize=13, tdy=tdy)

for i in range(7):
    x1 = 62 + i * 156 + 134
    arrow(f'M {x1},176 L {x1+20},176', BLUE, 'blue')

# Dev ⇄ Rev 打回小回环（红虚）
arrow('M 594,228 C 562,254 530,254 508,230', RED, 'red', dash='4,3', sw=2)
text(550, 258, '打回返工', size=10, fill='#dc2626', anchor='middle')

# ============ 三个支撑块 ============
for cx in (255, 695, 1135):
    arrow(f'M {cx},316 L {cx},268', GRAY, 'gray', dash='4,3')

box(60, 316, 390, 230, fill='#faf5ff', stroke='#c4b5fd', rx=10)
text(255, 344, 'Mika · 调度台（编排 agent）', size=14, fill='#6d28d9', anchor='middle', weight=600)
mika_rows = [
    '流水线的「交警」：谁完成了、下一棒给谁，它说了算',
    '角色完成时的评论 = 编排信号，秒级唤醒接力',
    '（cron 每 30 分钟巡逻一遍兜底，不怕漏单）',
    '建单守门：change-id / 阶段链 / 人工门 / 验收点',
    '失败自动重路由；连败 ≥2 停手喊人',
    '连打回 ≥2 自动提炼教训（lesson）入库',
]
sy = 370
for r in mika_rows:
    text(80, sy, '· ' + r, size=12, fill='#374151')
    sy += 26

box(500, 316, 390, 230, fill='#f0fdf4', stroke='#86efac', rx=10)
text(695, 344, '技能 · 工具箱（挂在角色身上）', size=14, fill='#047857', anchor='middle', weight=600)
skill_rows = [
    'agent 的「操作手册」，角色干活时按需翻阅',
    'openspec 系：proposal→specs→design→tasks',
    '（需求怎么一步步变成可执行任务）',
    'superpowers 系：写计划 / TDD / 调试 / 验收 SOP',
    'aicoding 系 ×8：UI 选型 · 权限 SQL · 库表文档',
    '· 浏览器 QA · 文档对账 · 测试复盘',
    'zip 整包导入技能库（附带文档不丢失）',
]
sy = 370
for r in skill_rows:
    text(520, sy, '· ' + r, size=12, fill='#374151')
    sy += 26

box(940, 316, 390, 230, fill='#fff7ed', stroke='#fdba74', rx=10)
text(1135, 344, '仓库 harness · 制度手册（开工必读）', size=14, fill='#9a3412', anchor='middle', weight=600)
harness_rows = [
    'CLAUDE.md 宪法：项目定位 / 模块表 / 保护路径',
    'AGENTS.md 协作：角色速查 · Git 策略 · 联动矩阵',
    'REVIEW.md 审查关卡：quick 4 关 / full 10 关',
    'docs/ 唯一事实源：库表文档只能由工具生成',
    'hooks/guard_write.py：保护路径写入直接拦截',
    '（配置/SQL/pom 等，变更须设计声明+审查）',
]
sy = 370
for r in harness_rows:
    text(960, sy, '· ' + r, size=12, fill='#374151')
    sy += 26

# ============ 三条铁律 ============
rules = [
    (60,  '铁律 ①  写库 SQL 永不执行', 'ddl / 权限脚本只由人执行，agent 只生成与判读'),
    (500, '铁律 ②  文档是唯一权威源', 'docs/ 与代码对不上？周级对账 autopilot 自动纠偏'),
    (940, '铁律 ③  密钥永不落盘', '密码 / token 只走环境变量：人注入，agent 进程内读'),
]
for x, t, sub in rules:
    box(x, 578, 390, 54, fill='#ffffff', stroke='#dc2626', rx=27, sw=1.5)
    text(x + 195, 600, t, size=13, fill='#dc2626', anchor='middle', weight=600)
    text(x + 195, 620, sub, size=11, fill='#6b7280', anchor='middle')

text(680, 672, '技术栈速览：Multica = Go 后端 + PostgreSQL + 本机 Runtime 守护进程（拉起 Claude Code 等 agent CLI）· MR 走 GitLab API（Closes {issue} 自动关单）· autopilot 由 cron 定时触发',
     size=12, fill='#9ca3af', anchor='middle')

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/harness-concept.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
