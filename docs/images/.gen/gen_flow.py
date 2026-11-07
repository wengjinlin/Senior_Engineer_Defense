# -*- coding: utf-8 -*-
"""生成 harness 运转流程图 SVG（泳道式流程图，Style 1 Flat Icon）"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def node(x, y, w, h, fill, stroke, title, subs=(), tsize=13):
    box(x, y, w, h, fill=fill, stroke=stroke)
    if not subs:
        text(x + w/2, y + h/2 + 4.5, title, size=tsize, fill='#111827', anchor='middle', weight=600)
    else:
        text(x + w/2, y + 22, title, size=tsize, fill='#111827', anchor='middle', weight=600)
        sy = y + 38
        for s in subs:
            text(x + w/2, sy, s, size=11, fill='#6b7280', anchor='middle')
            sy += 15

def arrow(path, color, marker, dash=None, sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')

def line(path, color, dash=None, sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d}/>')

def alabel(x, y, s, anchor='middle'):
    text(x, y, s, size=11, fill='#6b7280', anchor=anchor)

BLUE, ORANGE, PURPLE, GRAY, RED = '#2563eb', '#ea580c', '#7c3aed', '#6b7280', '#dc2626'

# ============ 文档头 ============
lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 1270" width="1440" height="1270">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('green', '#059669'), ('purple', '#7c3aed'), ('gray', '#6b7280'), ('red', '#dc2626')]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append('  <rect width="1440" height="1270" fill="#ffffff"/>')

text(720, 34, 'harness 运转流程 —— 一个 change 的完整生命周期', size=20, fill='#111827', anchor='middle', weight=600)
text(720, 56, '五阶段链（蓝）· Mika 编排（橙点火 / 紫信号）· 人工门 ×2 · autopilot 旁路（灰虚）', size=13, fill='#6b7280', anchor='middle')

# ============ 泳道 ============
lanes = [
    (60, 220, '#fffbeb', '#fedxaa', '人工（发起人 / 审阅人）'),
]
# 手动逐个画（标题条 + 泳道体）
def lane(x, w, body_fill, head_fill, head_stroke, label):
    box(x, 104, w, 1096, fill=body_fill, stroke='#e5e7eb', sw=1, rx=0)
    box(x, 70, w, 34, fill=head_fill, stroke=head_stroke, sw=1.2, rx=6)
    text(x + w/2, 92, label, size=13, fill='#374151', anchor='middle', weight=600)

lane(60, 220, '#fffdf5', '#ffedd5', '#fdba74', '人工（发起人 / 审阅人）')
lane(300, 460, '#f7faff', '#dbeafe', '#93c5fd', '角色 agent（五阶段链）')
lane(780, 200, '#fdfaff', '#ede9fe', '#c4b5fd', 'Mika 编排')
lane(1010, 400, '#fafafa', '#f3f4f6', '#d1d5db', '常驻 autopilot（cron 旁路）')

# ============ A 泳道节点 ============
node(85, 130, 170, 42, '#ffedd5', '#fdba74', '发起人 · chat 澄清', tsize=12)
node(75, 310, 190, 64, '#fed7aa', '#f97316', '人工门 G1', ['人审四工件', '人工执行 DDL / 权限 SQL'], tsize=13)
node(75, 946, 190, 64, '#fed7aa', '#f97316', '人工门 G2', ['人审合并 MR', '（change / doc-audit / retro）'], tsize=13)

# ============ B 泳道节点 ============
node(330, 130, 400, 42, '#dbeafe', '#93c5fd', 'PM · chat 澄清（双向 explore）→ 建 change issue', tsize=12)
node(330, 240, 400, 56, '#dbeafe', '#93c5fd', 'stage 1 · PM：四工件 + 三件套',
     ['proposal→specs→design→api(+ddl) · auth-resource.sql'])
node(330, 460, 400, 46, '#dbeafe', '#93c5fd', 'stage 2 · Tech-Lead：tasks.md + DAG + plan.md', tsize=12)
node(330, 824, 400, 46, '#dbeafe', '#93c5fd', 'stage 4 · Tester：测试 + 浏览器 QA',
     ['browser-qa → test-report.md'])
node(330, 888, 400, 46, '#dbeafe', '#93c5fd', 'stage 5 · DevOps：归档 + tag + CHANGELOG',
     ['GitLab API 建 MR（Closes {issue}）'])
node(330, 1024, 400, 46, '#dcfce7', '#86efac', '合并 → Closes {issue} 自动关主 issue',
     ['lesson 沉淀 · 文档随行更新'])

# ============ stage 3 循环框 ============
box(316, 596, 428, 196, fill='#ffffff', stroke='#9ca3af', sw=1.2, rx=10, dash='6,4')
text(530, 612, 'task 微循环 ×N（stage 3 · Developer ⇄ Reviewer）', size=11, fill='#6b7280', anchor='middle', weight=600)
node(344, 624, 372, 50, '#dbeafe', '#93c5fd', 'Developer · TDD 编码',
     ['executing-plans · db-schema-export'])
node(344, 692, 372, 46, '#f3f4f6', '#cbd5e1', 'Reviewer · 只读审查 4/10 关',
     ['review-report-{task-N}'])
lines.append(f'  <polygon points="530,750 574,773 530,796 486,773" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>')
text(530, 777, '通过？', size=11, fill='#111827', anchor='middle')

# ============ C 泳道节点 ============
node(800, 172, 160, 56, '#ede9fe', '#c4b5fd', 'Mika · 守门校验', ['五要素 ✗退回 / ✓登记'], tsize=12)
node(800, 388, 160, 50, '#ede9fe', '#c4b5fd', 'Mika · 置 metadata', ['ddl_done · role_bind'], tsize=12)
node(800, 528, 160, 60, '#ede9fe', '#c4b5fd', 'Mika · 建 task 子 issue', ['逐 task 点火 Developer'], tsize=12)
node(800, 700, 160, 80, '#ede9fe', '#c4b5fd', 'Mika · 审查路由',
     ['接收完成信号', '点名 Reviewer', '点火 stage 4 / 5'], tsize=12)

# ============ D 泳道节点 ============
node(1030, 150, 360, 110, '#ffffff', '#cbd5e1', '兜底巡检 autopilot',
     ['assignee Mika · */30 min（cron）', '巡检全部 issue：挂起路由 · 卡点提醒', '失败断点重路由 · 连败≥2 停止@用户', '连打回≥2 → 提炼 lesson'], tsize=12)
node(1030, 300, 360, 96, '#ffffff', '#cbd5e1', '结构文档对账 autopilot',
     ['DocKeeper · 周一 08:17', '调 aicoding-harness-audit', '代码 diff → doc-audit MR · 无差异静默'], tsize=12)
node(1030, 430, 360, 110, '#ffffff', '#cbd5e1', '人工测试复盘 autopilot',
     ['DocKeeper · 周一 08:23', '调 aicoding-human-test-retro', '逐问题四源归因 → 期报 + lesson 草案', 'retro MR · 人审合并即决策'], tsize=12)

# ============ 主流程箭头 ============
# 1 A1 -> PM
arrow('M 255,151 L 326,151', BLUE, 'blue')
alabel(292, 143, '① 澄清')
# 2 PM -> C1 信号
arrow('M 530,172 L 530,200 L 796,200', PURPLE, 'purple', dash='5,3')
alabel(665, 193, '编排信号 @Mika')
# 3 C1 -> stage1 点火
arrow('M 880,228 L 880,268 L 734,268', ORANGE, 'orange')
alabel(807, 261, '点火 stage 1')
# 4 stage1 -> G1
arrow('M 400,296 L 400,342 L 269,342', BLUE, 'blue')
alabel(334, 334, '提交人审')
# 5 G1 -> C2 回执
arrow('M 170,374 L 170,413 L 796,413', PURPLE, 'purple', dash='5,3')
alabel(480, 406, '执行回执 @Mika（ddl_done 等）')
# 6 C2 -> stage2 点火
arrow('M 880,438 L 880,483 L 734,483', ORANGE, 'orange')
alabel(807, 476, '点火 stage 2')
# 7 stage2 -> C3 信号
arrow('M 530,506 L 530,558 L 796,558', PURPLE, 'purple', dash='5,3')
alabel(660, 550, '完成信号')
# 8 C3 -> 循环框 点火
arrow('M 880,588 L 880,650 L 748,650', ORANGE, 'orange')
alabel(814, 643, '点火 stage 3')
# 9 Developer -> Reviewer
arrow('M 530,674 L 530,690', BLUE, 'blue')
text(542, 686, '完成信号', size=11, fill='#6b7280')
# 10 Reviewer -> 菱形
arrow('M 530,738 L 530,748', BLUE, 'blue')
# 11 打回（红）
arrow('M 486,773 L 328,773 L 328,649 L 340,649', RED, 'red')
alabel(407, 788, '打回返工')
# 12 菱形 -> stage4（出口）
arrow('M 530,796 L 530,820', BLUE, 'blue')
text(542, 812, '全部 task 通过', size=11, fill='#6b7280')
# 13 C4 -> stage4 / stage5 点火（共竖线）
line('M 880,780 L 880,909', ORANGE)
arrow('M 880,845 L 736,845', ORANGE, 'orange')
alabel(808, 838, '点火 stage 4')
arrow('M 880,909 L 736,909', ORANGE, 'orange')
alabel(808, 902, '点火 stage 5')
# 14 stage4 -> stage5
arrow('M 530,870 L 530,886', BLUE, 'blue')
# 15 stage5 -> G2
arrow('M 330,911 L 300,911 L 300,978 L 269,978', BLUE, 'blue')
text(308, 950, 'MR 待审', size=11, fill='#6b7280')
# 16 G2 -> 终点
arrow('M 170,1010 L 170,1046 L 326,1046', BLUE, 'blue')
alabel(249, 1040, '合并')

# ============ D 区关联箭头 ============
arrow('M 960,200 L 1026,200', GRAY, 'gray', dash='5,3')
alabel(993, 192, '巡检兜底')
arrow('M 1210,540 L 1210,1090 L 172,1090 L 172,1014', GRAY, 'gray', dash='5,3')
alabel(920, 1082, 'doc-audit / retro MR → 人审合并')

# ============ 图例 ============
lx = 60
legend = [
    (BLUE, None, 'blue', '蓝 · 主流程 / 工件流'),
    (ORANGE, None, 'orange', '橙 · Mika 点火 / 路由'),
    (PURPLE, '5,3', 'purple', '紫虚线 · 编排信号 / 回执'),
    (RED, None, 'red', '红 · 审查打回'),
    (GRAY, '5,3', 'gray', '灰虚线 · autopilot 旁路'),
]
for c, d, mid, t in legend:
    dd = f' stroke-dasharray="{d}"' if d else ''
    lines.append(f'  <line x1="{lx}" y1="1232" x2="{lx+30}" y2="1232" stroke="{c}" stroke-width="1.8"{dd} marker-end="url(#arrow-{mid})"/>')
    text(lx + 38, 1236, t, size=11, fill='#6b7280')
    lx += 38 + sum(11 if ord(ch) > 127 else 6.5 for ch in t) + 40

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/harness-runtime-flow.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
