# -*- coding: utf-8 -*-
"""生成 TDD 微循环图 SVG：单条目 TDD（红-绿-重构）+ 异模型只读审查 + 三道质量关"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def container(x, y, w, h, label):
    box(x, y, w, h, fill='none', stroke='#9ca3af', sw=1.3, rx=8, dash='8,4')
    lw = sum(7 if ord(c) > 255 else 6 for c in label) + 16
    lines.append(f'  <rect x="{x + 6}" y="{y - 9}" width="{lw}" height="18" rx="4" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1"/>')
    text(x + 6 + lw / 2, y + 4, label, size=11, fill='#374151', anchor='middle', weight=600)

def arrow(path, color, marker, dash=None, sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#{marker})"/>')

def alabel(x, y, s, size=11, fill='#6b7280', anchor='start'):
    text(x, y, s, size=size, fill=fill, anchor=anchor)

# ============ 文档头 ============
W, H = 1240, 810
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('green', '#059669'), ('purple', '#7c3aed'), ('gray', '#6b7280'), ('red', '#dc2626')]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')

text(W/2, 32, 'TDD 实现 · task 微循环与三道质量关', size=19, fill='#111827', anchor='middle', weight=600)
text(W/2, 56, '不写测试不让过（strict 门禁）· 异模型只读防共谋 · 分级测试防不足与过度', size=12.5, fill='#6b7280', anchor='middle')

# ============ 左侧前置约束 ============
box(90, 104, 260, 128, fill='#fff7ed', stroke='#fdba74')
text(220, 128, '前置约束 · DDL 人工门先行', size=12.5, fill='#9a3412', anchor='middle', weight=600)
text(220, 150, 'stage < 2 被 block —— 表结构必须先存在', size=10.5, fill='#6b7280', anchor='middle')
text(220, 168, '测试依赖真实库表，TDD 才有可靠对象', size=10.5, fill='#6b7280', anchor='middle')
text(220, 186, '人工执行 ddl 后回执 → Mika 置', size=10.5, fill='#6b7280', anchor='middle')
text(220, 204, 'metadata ddl_done 解锁 stage 3', size=10.5, fill='#6b7280', anchor='middle')
arrow('M 350,168 L 396,168', '#ea580c', 'orange')
lines.append('  <rect x="349" y="147" width="88" height="15" fill="#ffffff" opacity="0.9"/>')
text(373, 158, '解锁点火', size=10, fill='#ea580c', anchor='middle')

# ============ loop 框 ============
container(360, 96, 700, 470, 'loop · task 微循环 ×N（stage 3 内）')

# Mika 点火
box(430, 116, 200, 50, fill='#dbeafe', stroke='#93c5fd')
text(530, 146, 'Mika 点火 task#N', size=13, fill='#111827', anchor='middle', weight=600)
arrow('M 530,166 L 530,204', '#ea580c', 'orange')

# Developer 大节点（内嵌 TDD 三步）
box(400, 208, 320, 186, fill='#f0fdf4', stroke='#86efac')
text(560, 234, 'Developer · 单条目 TDD', size=13, fill='#111827', anchor='middle', weight=600)
steps = [
    ('红 RED', '先写测试', '必须失败', '#fef2f2', '#fca5a5'),
    ('绿 GREEN', '最小实现', '恰好通过', '#f0fdf4', '#86efac'),
    ('重构', '改善结构', '不改行为', '#eff6ff', '#93c5fd'),
]
for i, (t1, t2, t3, f, s) in enumerate(steps):
    sx = 418 + i * 106
    box(sx, 250, 86, 64, fill=f, stroke=s)
    text(sx + 43, 270, t1, size=11.5, fill='#111827', anchor='middle', weight=600)
    text(sx + 43, 288, t2, size=10.5, fill='#6b7280', anchor='middle')
    text(sx + 43, 304, t3, size=10.5, fill='#6b7280', anchor='middle')
    if i < 2:
        lines.append(f'  <line x1="{sx + 88}" y1="282" x2="{sx + 99}" y2="282" stroke="#059669" stroke-width="1.6"/>')
        lines.append(f'  <polygon points="{sx + 99},276 {sx + 106},282 {sx + 99},288" fill="#059669"/>')
text(560, 340, '技能挂载：executing-plans ·', size=10.5, fill='#6b7280', anchor='middle')
text(560, 356, 'test-driven-development · systematic-debugging', size=10.5, fill='#6b7280', anchor='middle')
text(560, 378, 'plan.md 单条目推进 · 禁止跨条目', size=11, fill='#059669', anchor='middle', weight=600)

# 完成信号 -> Reviewer
arrow('M 720,290 L 794,290', '#7c3aed', 'purple', dash='6,3')
alabel(757, 280, '完成评论', size=10, fill='#7c3aed', anchor='middle')
alabel(757, 304, '【编排信号】', size=10, fill='#7c3aed', anchor='middle')

# Reviewer
box(800, 240, 300, 132, fill='#f8fafc', stroke='#cbd5e1')
text(950, 266, 'Reviewer · 只读审查（异模型）', size=13, fill='#111827', anchor='middle', weight=600)
text(950, 290, '无写权限 —— 想放水也没有通道', size=11, fill='#6b7280', anchor='middle')
text(950, 310, '与 Developer 异模型，防「AI 审 AI」共谋', size=11, fill='#6b7280', anchor='middle')
text(950, 330, 'quick 4 关 / full 10 关（REVIEW.md 清单）', size=11, fill='#6b7280', anchor='middle')
text(950, 350, '产 review-report-{task-N}.md', size=11, fill='#2563eb', anchor='middle')

# 判定菱形
arrow('M 950,372 L 950,420', '#ea580c', 'orange')
lines.append('  <polygon points="950,424 1030,462 950,500 870,462" fill="#fefce8" stroke="#eab308" stroke-width="1.5"/>')
text(950, 458, '审查判定', size=12, fill='#111827', anchor='middle', weight=600)
text(950, 476, '过 / 不过', size=10, fill='#6b7280', anchor='middle')

# 通过 → 下一 task
arrow('M 1030,462 L 1076,462', '#059669', 'green')
box(1080, 438, 130, 48, fill='#f0fdf4', stroke='#86efac')
text(1145, 458, '点火下一 task', size=12, fill='#059669', anchor='middle', weight=600)
text(1145, 476, '循环推进', size=10, fill='#6b7280', anchor='middle')

# 打回 → Developer
arrow('M 950,500 L 950,533 L 560,533 L 560,398', '#dc2626', 'red', dash='6,3')
alabel(755, 525, '红牌打回 · 逐条列问题项 · 计打回次数（连打回 ≥2 → Mika 提炼 lesson）', size=10.5, fill='#dc2626', anchor='middle')

# ============ 底部三道关 ============
gates = [
    ('① TDD 强制（strict）', ['测试从「可选项」变为「门禁」', '不写测试，编码无法通过', '红-绿-重构循环完整留痕'], '#fef2f2', '#fca5a5'),
    ('② 异模型 + 只读', ['审查者无写权限、异模型家族', '专为 AI 代码设计审查项：', 'LLM 信任边界 · AI 冗余物'], '#f8fafc', '#cbd5e1'),
    ('③ 分级测试', ['Quick / Standard / Exhaustive', '浏览器 QA 报告式（不改码）', '防覆盖不足，也防过度测试'], '#eff6ff', '#93c5fd'),
]
for i, (t, subs, f, s) in enumerate(gates):
    gx = 90 + i * 380
    box(gx, 610, 350, 116, fill=f, stroke=s)
    text(gx + 175, 636, t, size=13, fill='#111827', anchor='middle', weight=600)
    sy = 662
    for sub in subs:
        text(gx + 175, sy, sub, size=11, fill='#6b7280', anchor='middle')
        sy += 20

# ============ 图例 ============
lx = 150
for c, mk, d, t in [
    ('#ea580c', 'orange', None, '橙 · 点火/推进'),
    ('#7c3aed', 'purple', '6,3', '紫虚 · 编排信号'),
    ('#059669', 'green', None, '绿 · 通过/TDD 步进'),
    ('#dc2626', 'red', '6,3', '红虚 · 打回'),
]:
    dd = f' stroke-dasharray="{d}"' if d else ''
    lines.append(f'  <line x1="{lx}" y1="770" x2="{lx+28}" y2="770" stroke="{c}" stroke-width="1.8"{dd} marker-end="url(#arrow-{mk})"/>')
    text(lx + 36, 774, t, size=11, fill='#6b7280')
    lx += 36 + sum(11 if ord(ch) > 255 else 6 for ch in t) + 40

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/tdd-microloop.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
