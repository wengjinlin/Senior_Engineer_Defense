# -*- coding: utf-8 -*-
"""生成 AI 自我学习闭环图（lesson 经验库 + 宪法晋升）"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def node(x, y, w, h, fill, stroke, title, subs, tsize=13):
    box(x, y, w, h, fill=fill, stroke=stroke)
    text(x + w/2, y + 24, title, size=tsize, fill='#111827', anchor='middle', weight=600)
    sy = y + 43
    for s in subs:
        text(x + w/2, sy, s, size=11, fill='#6b7280', anchor='middle')
        sy += 16

def arrow(path, color, dash=None, sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#arrow-{color})"/>')

BLUE, ORANGE, GRAY = 'blue', 'orange', 'gray'

lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1360 580" width="1360" height="580">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('gray', '#6b7280')]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append('  <rect width="1360" height="580" fill="#ffffff"/>')

text(680, 30, 'AI 自我学习闭环 —— 从踩坑到宪法', size=20, fill='#111827', anchor='middle', weight=600)

# ============ 主循环（上排 5 盒） ============
node(60, 100, 220, 100, '#dbeafe', '#93c5fd', '① 干活踩坑', ['Reviewer 打回', 'Tester 测试踩坑', '发布翻车 / 人工测试警告'])
node(304, 100, 220, 100, '#ede9fe', '#c4b5fd', '② 归因提炼', ['Mika 巡检：连打回≥2', '周级复盘：四源证据归因', 'REVIEW 关 3：新教训即记'])
node(548, 100, 220, 100, '#dcfce7', '#86efac', '③ lesson 条目', ['[日期][change-id] 标题', '❌ 错误做法（具体到命令）', '✅ 正确做法（具体可执行）'])
node(792, 100, 220, 100, '#ffedd5', '#fdba74', '④ 人审入库', ['retro MR 人审合并', 'DevOps 归档时落盘', 'docs/lessons/{Role}.md'])
node(1036, 100, 220, 100, '#dbeafe', '#93c5fd', '⑤ 开工必读', ['先读自己角色经验库', '历史教训', '视同本级约束执行'])

for x1 in (282, 526, 770, 1014):
    arrow(f'M {x1},150 L {x1+20},150', BLUE)

# 回环大弧：⑤ → ①
arrow('M 1146,94 C 950,44 390,44 178,94', BLUE)
text(662, 48, '开工即带上全部历史记忆 —— AI 越干越聪明', size=12, fill='#2563eb', anchor='middle', weight=600)

# ============ 晋升通道（下排） ============
arrow('M 902,200 L 902,336', BLUE)
lines.append('  <polygon points="902,340 1052,380 902,420 752,380" fill="#fef9c3" stroke="#ca8a04" stroke-width="1.5"/>')
text(902, 376, '同类教训', size=11, fill='#111827', anchor='middle')
text(902, 392, '第 2 次出现？', size=11, fill='#111827', anchor='middle')

# 是 → 晋升
text(1058, 368, '是', size=11, fill='#ea580c')
arrow('M 1054,380 L 1066,380', ORANGE)
node(1070, 345, 264, 70, '#ffedd5', '#fdba74', 'Reviewer 标注「建议晋升」', ['@Mika 转人类确认'], tsize=12)
arrow('M 1202,415 L 1202,441', ORANGE)
node(1070, 445, 264, 80, '#ffffff', '#dc2626', '晋升宪法（制度红线）',
     ['写入 CLAUDE.md / REVIEW.md', '原 lesson 条目删除'], tsize=12)

# 否 → 回经验库
text(742, 370, '否', size=11, fill='#6b7280')
arrow('M 752,380 L 658,380 L 658,204', GRAY, dash='5,3')
text(705, 398, '继续作为经验生效', size=11, fill='#6b7280', anchor='middle')

text(680, 556, '两级进化：角色经验库 docs/lessons/{Role}.md（越攒越厚）→ 全员制度红线 CLAUDE.md / REVIEW.md（越用越硬）· 每次晋升必经人类确认',
     size=12, fill='#6b7280', anchor='middle')

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/lesson-loop.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
