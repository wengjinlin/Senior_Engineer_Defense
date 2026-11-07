# -*- coding: utf-8 -*-
"""生成 SDD 工件链图 SVG：OpenSpec proposal→specs→design→api + 双 strict + 人工门 + 规格回写闭环"""

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

def alabel(x, y, s, size=11, fill='#6b7280', anchor='start', weight=400):
    text(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight)

# ============ 文档头 ============
W, H = 1240, 790
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
for cid, c in [('blue', '#2563eb'), ('orange', '#ea580c'), ('green', '#059669'), ('purple', '#7c3aed'), ('gray', '#6b7280'), ('red', '#dc2626')]:
    lines.append(f'    <marker id="arrow-{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="{c}"/></marker>')
lines.append('  </defs>')
lines.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')

text(W/2, 32, 'SDD 实现 · OpenSpec 工件链与强制机制', size=19, fill='#111827', anchor='middle', weight=600)
text(W/2, 56, '先 WHAT 后 HOW（顺序铁律）· 双 strict 强制 · 三件套人工执行 · 规格与实现单态同步', size=12.5, fill='#6b7280', anchor='middle')

# ============ 行1：四工件主链 ============
alabel(90, 96, '工件属性 →', size=11, fill='#9ca3af')
node(90, 104, 130, 66, '#fef3c7', '#fcd34d', 'PM 澄清', ['chat 双向 explore', '不写代码'], tsize=12)
text(339, 96, 'WHY', size=11, fill='#b45309', anchor='middle', weight=600)
node(267, 104, 145, 66, '#dbeafe', '#93c5fd', '① proposal', ['变更动机 · 为什么做'])
text(521, 96, 'WHAT', size=11, fill='#b45309', anchor='middle', weight=600)
node(449, 104, 145, 66, '#dbeafe', '#93c5fd', '② specs', ['需求规格 · 做什么'])
text(703, 96, 'HOW', size=11, fill='#b45309', anchor='middle', weight=600)
node(631, 104, 145, 66, '#dbeafe', '#93c5fd', '③ design', ['技术设计 · 怎么做'])
text(893, 96, '契约', size=11, fill='#b45309', anchor='middle', weight=600)
node(813, 104, 160, 66, '#dbeafe', '#93c5fd', '④ api (+ ddl)', ['接口 / 表结构变更'])
node(1010, 104, 170, 66, '#ffedd5', '#fdba74', 'auth-resource.sql', ['菜单 / 按钮权限三表', '从 design 清单生成'], tsize=12)

for x1, x2 in [(224, 264), (398, 445), (598, 627), (780, 809)]:
    arrow(f'M {x1},137 L {x2},137', '#ea580c', 'orange')
alabel(244, 127, 'ordering', size=8, fill='#dc2626', anchor='middle', weight=600)
alabel(420, 127, 'strict', size=9, fill='#dc2626', anchor='middle', weight=600)
alabel(613, 127, '跳序即', size=9, fill='#dc2626', anchor='middle', weight=600)
alabel(795, 127, 'block', size=9, fill='#dc2626', anchor='middle', weight=600)
arrow('M 977,137 L 1006,137', '#ea580c', 'orange')

# ============ G1 人工门 ============
arrow('M 620,170 L 620,208', '#7c3aed', 'purple', dash='5,3')
alabel(632, 196, '提交人审')
box(90, 212, 1090, 92, fill='#fff7ed', stroke='#fdba74')
text(635, 236, '人工门 G1 —— 第一道人工关口（写库 SQL 永不由 agent 执行）', size=13.5, fill='#9a3412', anchor='middle', weight=600)
text(635, 258, '人审四工件（proposal / specs / design / api） · 人工执行 ddl.sql + auth-resource.sql（三件套 = design + ddl + auth）', size=11.5, fill='#6b7280', anchor='middle')
text(635, 278, '回执 @Mika → 置 metadata（ddl_done / role_bind）→ 解锁 stage ≥2（表结构先存在，TDD 才有可依赖的测试对象）', size=11.5, fill='#6b7280', anchor='middle')

# ============ 行3：拆解与实现 ============
arrow('M 620,304 L 620,342', '#ea580c', 'orange')
alabel(632, 330, 'metadata 解锁 · 点火')
node(90, 346, 320, 72, '#dbeafe', '#93c5fd', 'Tech-Lead · 拆解排期', ['读四工件 → tasks.md + DAG + 排他文件清单', '产 plan.md（writing-plans）'], tsize=12.5)
node(450, 346, 300, 72, '#dcfce7', '#86efac', 'Developer · 单条目 TDD 编码', ['按 plan.md 逐条推进（红-绿-重构）', 'DDL 变更后 db-schema-export 重生成库文档'], tsize=12.5)
node(790, 346, 200, 72, '#dbeafe', '#93c5fd', 'Tester · 分级测试', ['Quick / Standard /', 'Exhaustive 三档'], tsize=12.5)
node(1020, 346, 160, 72, '#dbeafe', '#93c5fd', 'DevOps · 归档', ['archive-change', '+ tag + MR'], tsize=12.5)
for x1, x2 in [(414, 444), (754, 784), (994, 1014)]:
    arrow(f'M {x1},382 L {x2},382', '#ea580c', 'orange')

# ============ 行4：三大机制 ============
mech_y = 470
container(90, mech_y, 336, 146, '双 strict 强制（openspec 配置）')
node(106, mech_y + 34, 304, 94, '#fef2f2', '#fca5a5', 'ordering · strict', ['工件跳序 / 先码后文 → 直接 block', '', 'tdd_enforcement · strict', '不写测试不让过（门禁化）'], tsize=12, ssize=10.5)

container(466, mech_y, 336, 146, '模型分级路由（model_routing_hints）')
node(482, mech_y + 34, 304, 94, '#eff6ff', '#93c5fd', '按工序路由模型', ['explore 澄清 → 小模型（省）', 'design / review → 大模型（准）', 'apply 编码 → 中档（均衡）'], tsize=12, ssize=10.5)

container(842, mech_y, 336, 146, '文档漂移双重防守')
node(858, mech_y + 34, 304, 94, '#f0fdf4', '#86efac', 'docs/ 唯一权威源', ['第一道：变更随行（DDL 后重生成）', '第二道：周一 harness-audit 对账', 'diff→文档增量 MR · 无差异静默'], tsize=12, ssize=10.5)

# ============ 行5：规格回写闭环 ============
box(90, 640, 1090, 52, fill='#faf5ff', stroke='#c4b5fd')
text(635, 662, '闭环：归档时 sync-specs 将实现反哺回 specs —— 规格与实现永远单态，杜绝"文档是文档、代码是代码"', size=12, fill='#6d28d9', anchor='middle', weight=600)
text(635, 682, '消费端：全角色开工必读四工件（工件链驱动），CLAUDE.md / AGENTS.md 为项目事实唯一权威源', size=11, fill='#6b7280', anchor='middle')
arrow('M 1100,418 L 1100,442 L 1010,442 L 1010,466', '#7c3aed', 'purple', dash='5,3')
alabel(1112, 436, '归档触发', size=10.5, fill='#7c3aed')

# ============ 图例 ============
lx = 150
for c, mk, d, t in [
    ('#ea580c', 'orange', None, '橙 · 点火/推进'),
    ('#7c3aed', 'purple', '5,3', '紫虚 · 人工/回写'),
    ('#dc2626', 'red', None, '红字 · strict 拦截点'),
]:
    dd = f' stroke-dasharray="{d}"' if d else ''
    if mk:
        lines.append(f'  <line x1="{lx}" y1="740" x2="{lx+28}" y2="740" stroke="{c}" stroke-width="1.8"{dd} marker-end="url(#arrow-{mk})"/>')
    text(lx + 36, 744, t, size=11, fill='#6b7280')
    lx += 36 + sum(11 if ord(ch) > 255 else 6 for ch in t) + 40

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/sdd-pipeline.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
