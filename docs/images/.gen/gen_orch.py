# -*- coding: utf-8 -*-
"""生成编排信号时序图 SVG：事件驱动接力 + cron 兜底 + 失败分级"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def frame(x, y, w, h, label, stroke='#9ca3af', fill='none'):
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.3" stroke-dasharray="8,4"/>')
    lw = sum(7 if ord(c) > 255 else 6 for c in label) + 16
    lines.append(f'  <rect x="{x + 6}" y="{y - 9}" width="{lw}" height="18" rx="4" fill="#f3f4f6" stroke="{stroke}" stroke-width="1"/>')
    text(x + 6 + lw / 2, y + 4, label, size=11, fill='#374151', anchor='middle', weight=600)

def arrow(x1, y, x2, color, marker, dash=None, sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#arrow-{marker})"/>')

def mlabel(x, y, s, fill='#374151'):
    w = sum(11.5 if ord(c) > 127 else 6.3 for c in s)
    lines.append(f'  <rect x="{x - w/2 - 4}" y="{y - 11}" width="{w + 8}" height="15" fill="#ffffff" opacity="0.85"/>')
    text(x, y, s, size=11.5, fill=fill, anchor='middle')

# ============ 文档头 ============
W, H = 1240, 880
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('green', '#059669'), ('purple', '#7c3aed'), ('gray', '#6b7280'), ('red', '#dc2626')]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')

text(W/2, 26, '编排实现 · 事件驱动接力机制（task 微循环时序）', size=18, fill='#111827', anchor='middle', weight=600)
text(W/2, 44, '编排信号 = 特定格式完成评论，@Mika 秒级唤醒 —— 主通道事件驱动，cron 仅兜底', size=12, fill='#6b7280', anchor='middle')

# ============ 生命线 ============
lanes = [
    ('Developer\n(执行 agent)', 210, '#dcfce7', '#86efac'),
    ('Mika · 编排 agent', 560, '#dbeafe', '#93c5fd'),
    ('Reviewer\n(只读 · 异模型)', 900, '#f3f4f6', '#cbd5e1'),
    ('兜底巡检\ncron */30min', 1130, '#fff7ed', '#fdba74'),
]
TOP, BOT = 104, 800
for name, x, f, s in lanes:
    parts = name.split('\n')
    box(x - 85, 52, 170, 52, fill=f, stroke=s)
    if len(parts) == 2:
        text(x, 72, parts[0], size=12.5, fill='#111827', anchor='middle', weight=600)
        text(x, 90, parts[1], size=10.5, fill='#6b7280', anchor='middle')
    else:
        text(x, 82, name, size=12.5, fill='#111827', anchor='middle', weight=600)
    lines.append(f'  <line x1="{x}" y1="104" x2="{x}" y2="{BOT}" stroke="#d1d5db" stroke-width="1.2" stroke-dasharray="5,4"/>')

DX, MX, RX, CX = 210, 560, 900, 1130

# ============ loop 框：task 微循环 ============
frame(120, 108, 900, 500, 'loop · task 微循环 ×N（stage 3 内）')

# 激活条
def act(x, y1, y2, color='#93c5fd'):
    lines.append(f'  <rect x="{x-5}" y="{y1}" width="10" height="{y2-y1}" fill="#e5e7eb" stroke="{color}" stroke-width="1"/>')

# m1
act(DX, 128, 172); act(MX, 128, 300)
arrow(MX - 8, 140, DX + 12, '#ea580c', 'orange')
mlabel((MX + DX) / 2, 133, '① 点火 task#N（tasks.md 单条目 · stage 路由）')

# m2
arrow(DX - 8, 196, MX + 12, '#7c3aed', 'purple', dash='6,3')
mlabel((MX + DX) / 2, 189, '② 完成评论【编排信号】@Mika')

# m3 唤醒标注（自消息）
box(MX + 14, 214, 320, 46, fill='#eff6ff', stroke='#93c5fd', rx=6)
text(MX + 174, 233, '③ 秒级唤醒 · 事件驱动（免轮询）', size=11.5, fill='#1e40af', anchor='middle', weight=600)
text(MX + 174, 250, '建单守门 / stage 路由 / 点名审查 决策', size=10.5, fill='#6b7280', anchor='middle')

# m4
act(MX, 268, 330); act(RX, 288, 470)
arrow(MX + 8, 292, RX - 12, '#ea580c', 'orange')
mlabel((MX + RX) / 2, 285, '④ 点名 Reviewer（quick 4 关 / full 10 关）')

# ============ alt 框：审查结果 ============
frame(300, 316, 660, 268, 'alt · 审查结果')

arrow(RX - 8, 352, MX + 12, '#059669', 'green', dash='6,3')
mlabel((MX + RX) / 2, 345, '⑤a review-report-{task-N}.md · 通过信号', '#059669')
arrow(MX - 8, 388, DX + 12, '#ea580c', 'orange')
mlabel((MX + DX) / 2, 381, '⑥a 点火下一 task（循环推进）')

lines.append('  <line x1="300" y1="408" x2="960" y2="408" stroke="#d1d5db" stroke-width="1.2" stroke-dasharray="6,4"/>')
text(948, 403, '[打回]', size=10.5, fill='#dc2626', anchor='end')

arrow(RX - 8, 440, DX + 12, '#dc2626', 'red', dash='6,3')
mlabel((DX + RX) / 2, 433, '⑤b 红牌打回 · 逐条列问题项', '#dc2626')
arrow(DX + 20, 470, DX + 78, '#dc2626', 'red', dash='6,3')
text(DX + 88, 474, '⑥b 返工 → 重发编排信号（计打回次数）', size=11.5, fill='#dc2626')

# ============ 保障机制标注（loop 下方）============
act(CX, 640, 780, '#fdba74')
arrow(CX - 8, 660, MX + 12, '#6b7280', 'gray', dash='5,3')
text((MX + CX) / 2 + 20, 650, '⑦ 巡检全部 issue（挂起路由 · 断点重路由）', size=11.5, fill='#6b7280', anchor='middle')

box(300, 700, 700, 84, fill='#fff7ed', stroke='#fdba74', rx=8)
text(650, 724, '失败分级升级（编排的第三重保障）', size=12.5, fill='#9a3412', anchor='middle', weight=600)
text(650, 744, 'run 失败 → 断点重路由续跑 ｜ 连续失败 ≥2 → 停止重试 @人类', size=11, fill='#6b7280', anchor='middle')
text(650, 762, '连续打回 ≥2 → 自动提炼 lesson 入错题本（同类坑提前规避）', size=11, fill='#6b7280', anchor='middle')
lines.append('  <path d="M 560,780 L 560,700" fill="none" stroke="#ea580c" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrow-orange)"/>')

# ============ 图例 ============
lx = 150
for c, mk, d, t in [
    ('#ea580c', 'orange', None, '橙 · 点火/控制'),
    ('#7c3aed', 'purple', '6,3', '紫虚 · 编排信号'),
    ('#059669', 'green', '6,3', '绿虚 · 通过'),
    ('#dc2626', 'red', '6,3', '红虚 · 打回'),
    ('#6b7280', 'gray', '5,3', '灰虚 · cron 兜底'),
]:
    dd = f' stroke-dasharray="{d}"' if d else ''
    lines.append(f'  <line x1="{lx}" y1="846" x2="{lx+28}" y2="846" stroke="{c}" stroke-width="1.8"{dd} marker-end="url(#arrow-{mk})"/>')
    text(lx + 36, 850, t, size=11, fill='#6b7280')
    lx += 36 + sum(11 if ord(ch) > 255 else 6 for ch in t) + 34

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/orchestration-signal.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
