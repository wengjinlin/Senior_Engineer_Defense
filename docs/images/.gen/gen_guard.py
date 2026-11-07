# -*- coding: utf-8 -*-
"""生成硬约束体系图 SVG：guard_write.py 拦截链 + 合法变更通道 + 四道锁 + 密钥/自测"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

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
W, H = 1240, 800
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('green', '#059669'), ('purple', '#7c3aed'), ('gray', '#6b7280'), ('red', '#dc2626')]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')

text(W/2, 32, '硬约束体系 · 写入拦截与四道锁', size=19, fill='#111827', anchor='middle', weight=600)
text(W/2, 56, '规范不靠自觉靠拦截 —— 保护路径写入物理不可达 · 密钥永不落盘 · 变更有唯一合法通道', size=12.5, fill='#6b7280', anchor='middle')

# ============ 拦截主链 ============
node(90, 104, 200, 76, '#dbeafe', '#93c5fd', 'agent 写入动作', ['Write / Edit / Bash', '（任何角色 · 每一次）'])
arrow('M 290,142 L 326,142', '#2563eb', 'blue')
node(330, 104, 190, 76, '#dbeafe', '#93c5fd', 'PreToolUse hook', ['工具调用前触发', '（Claude Code 钩子）'])
arrow('M 520,142 L 556,142', '#2563eb', 'blue')
lines.append('  <polygon points="640,98 724,142 640,186 556,142" fill="#fefce8" stroke="#eab308" stroke-width="1.5"/>')
text(640, 138, '命中保护', size=11.5, fill='#111827', anchor='middle', weight=600)
text(640, 154, '路径清单？', size=11.5, fill='#111827', anchor='middle', weight=600)

# 分叉
lines.append('  <line x1="724" y1="142" x2="756" y2="142" stroke="#6b7280" stroke-width="1.6"/>')
arrow('M 756,142 L 756,116 L 786,116', '#dc2626', 'red')
alabel(764, 106, '是', size=11, fill='#dc2626', anchor='middle')
node(790, 84, 400, 64, '#fef2f2', '#fca5a5', 'block · 拒绝执行（零违反）', ['写入根本发生不了 —— 物理不可绕过'], tsize=12.5)
arrow('M 756,142 L 756,176 L 786,176', '#059669', 'green')
alabel(764, 196, '否', size=11, fill='#059669', anchor='middle')
node(790, 160, 400, 52, '#f0fdf4', '#86efac', '放行 · 正常落盘', [], tsize=12.5)

# 保护清单
lines.append('  <path d="M 640,186 L 640,232 L 786,232" fill="none" stroke="#6b7280" stroke-width="1.4" stroke-dasharray="5,3"/>')
alabel(713, 226, '判定依据', size=10, fill='#6b7280', anchor='middle')
node(790, 232, 400, 64, '#ffffff', '#d1d5db', '保护路径清单（示例）', ['application*.yml · db/ · sql/', 'settings.xml · pom.xml'], tsize=12.5)

# ============ 合法变更通道 ============
box(90, 336, 1100, 70, fill='#fff7ed', stroke='#fdba74')
text(640, 360, '变更保护路径的唯一合法通道（声明制，不是禁止制）', size=13, fill='#9a3412', anchor='middle', weight=600)
text(640, 384, 'design.md 显式声明变更 → Reviewer 审查通过 → protected 路径另加人工复核 → 解锁变更', size=11.5, fill='#6b7280', anchor='middle')

# ============ 四道锁 ============
locks = [
    ('① 开工必读', ['干活前强制读', 'CLAUDE.md + AGENTS.md', '规范从「参考」变「前提」'], '#dbeafe', '#93c5fd'),
    ('② 程序拦截', ['guard_write.py', 'PreToolUse 直接 block', '零违反 · 不可绕过'], '#fef2f2', '#fca5a5'),
    ('③ 只读审查', ['Reviewer 无写权限', 'quick 4 / full 10 关', '想放水没有通道'], '#f8fafc', '#cbd5e1'),
    ('④ Git 铁律', ['只 push feature/{change-id}', '禁直推保护分支', '上主线唯一路：MR 人审'], '#f0fdf4', '#86efac'),
]
for i, (t, subs, f, s) in enumerate(locks):
    node(90 + i * 286, 436, 262, 118, f, s, t, subs, tsize=13, ssize=10.5)

# ============ 密钥 + 自测 ============
box(90, 588, 535, 96, fill='#faf5ff', stroke='#c4b5fd')
text(357, 612, '密钥管理 · env 人工通道', size=12.5, fill='#6d28d9', anchor='middle', weight=600)
text(357, 634, '密码 / token 人工网页注入 · agent 仅进程内可读', size=11, fill='#6b7280', anchor='middle')
text(357, 654, '永不落盘：不入脚本参数 · 不入 issue 评论 · 不入文档', size=11, fill='#6b7280', anchor='middle')

box(655, 588, 535, 96, fill='#f0f6ff', stroke='#93c5fd')
text(922, 612, '安装自测门（hook 自测）', size=12.5, fill='#1e40af', anchor='middle', weight=600)
text(922, 634, '保护路径写入 → 应被拦截；普通路径写入 → 应放行', size=11, fill='#6b7280', anchor='middle')
text(922, 654, '两例全过才算装好 —— 建区完成的前置校验', size=11, fill='#6b7280', anchor='middle')

# ============ 图例 ============
lx = 150
for c, mk, d, t in [
    ('#2563eb', 'blue', None, '蓝 · 调用链'),
    ('#dc2626', 'red', None, '红 · 拦截'),
    ('#059669', 'green', None, '绿 · 放行'),
    ('#6b7280', 'gray', '5,3', '灰虚 · 判定依据'),
]:
    dd = f' stroke-dasharray="{d}"' if d else ''
    mk_attr = f' marker-end="url(#arrow-{mk})"' if c != '#6b7280' else ''
    lines.append(f'  <line x1="{lx}" y1="730" x2="{lx+28}" y2="730" stroke="{c}" stroke-width="1.8"{dd}{mk_attr}/>')
    text(lx + 36, 734, t, size=11, fill='#6b7280')
    lx += 36 + sum(11 if ord(ch) > 255 else 6 for ch in t) + 40

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/hard-guard.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
