# -*- coding: utf-8 -*-
"""生成目标仓库 harness 结构图"""

lines = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def text(x, y, s, size=12, fill='#111827', anchor='start', weight=400):
    lines.append(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')

def box(x, y, w, h, fill='#ffffff', stroke='#d1d5db', sw=1.5, rx=8):
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def node(x, y, w, h, fill, stroke, title, subs, tsize=13, tsz2=11):
    box(x, y, w, h, fill=fill, stroke=stroke)
    if not subs:
        text(x + w/2, y + h/2 + 4.5, title, size=tsize, fill='#111827', anchor='middle', weight=600)
        return
    text(x + w/2, y + 24, title, size=tsize, fill='#111827', anchor='middle', weight=600)
    sy = y + 43
    for s in subs:
        text(x + w/2, sy, s, size=tsz2, fill='#6b7280', anchor='middle')
        sy += 16

def sec(y, s):
    text(56, y, s, size=12, fill='#374151', weight=600)

lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1420 900" width="1420" height="900">')
lines.append('  <style>text { font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", "Microsoft JhengHei", sans-serif; }</style>')
lines.append('  <defs>')
lines.append('    <marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/></marker>')
lines.append('  </defs>')
lines.append('  <rect width="1420" height="900" fill="#ffffff"/>')

text(710, 34, '目标仓库 harness 结构图 —— agent 的制度与字典', size=20, fill='#111827', anchor='middle', weight=600)
text(710, 56, '三大治理文档（红线）+ docs/ 字典体系（唯一权威源）+ 机制硬约束 + 一次性建设 + 双重防漂移', size=13, fill='#6b7280', anchor='middle')

# ============ ① 治理文档 ============
sec(84, '① 治理文档（红线层）—— 所有 agent 开工必读，违反即打回')
node(56, 96, 344, 76, '#ffedd5', '#fdba74', 'CLAUDE.md · 项目宪法', ['15 节红线：定位/模块表/构建/TDD/分层', '命名/保护路径/响应格式/日志——覆盖全仓库'])
node(413, 96, 344, 76, '#ffedd5', '#fdba74', 'AGENTS.md · 协作总纲', ['角色速查 · Git 策略 · OpenSpec 工件结构', '变更联动矩阵 · lessons 读写矩阵'])
node(770, 96, 344, 76, '#ffedd5', '#fdba74', 'REVIEW.md · 审查关卡', ['quick 4 关：spec-align / risk / lesson / archive', 'full 10 关 · protected 路径加人工复核'])

# ============ ② docs/ 字典体系 ============
sec(196, '② docs/ 字典体系（唯一权威源）—— docs/index.md 是唯一入口')
box(56, 208, 1058, 44, fill='#dbeafe', stroke='#93c5fd')
text(585, 235, 'docs/index.md —— 目录导航 · 按角色必读顺序 · 维护规则 · 对账基线表（DocKeeper 维护）', size=12, fill='#1e40af', anchor='middle', weight=600)

docs9 = [
    (56, 262, 'architecture/index.md', ['模块定位字典：业务域↔模块↔表前缀', '高风险区 / ADR / 技术债 · 全角色']),
    (413, 262, 'architecture/implicit-contracts.md', ['隐性约定：口头约定 / 历史包袱', '代码看不出来的规则 · 全角色']),
    (770, 262, 'product/index.md', ['业务域划分 / 术语表 / 状态机', '业务校验铁律 · PM 为主']),
    (56, 352, 'database/（index + tables/）', ['全库表清单 + 每表字段详情', '唯一生成通道 aicoding-db-schema-export']),
    (413, 352, 'standards/（api · database · testing）', ['三篇详单 + 评审检查清单', '宪法红线与详单两向引用']),
    (770, 352, 'templates/design-review-template.md', ['前端设计人审模板', '逐字段选型 + 偏离声明 · PM/Reviewer']),
    (56, 442, 'help/（能力清单 + 7 篇能力文档）', ['平台能力使用指南（po/s3/kafka…）', '涉平台集成需求必读 · 全角色']),
    (413, 442, 'lessons/（index + {Role}.md）', ['错题本：日期+change-id+❌/✅ 对照', '开工必读视同本级约束']),
    (770, 442, 'human-test-reports/', ['人工测试报告（日期-分支名.md）', '人类维护 · agent 只读 · 复盘归档']),
]
for x, y, t, subs in docs9:
    node(x, y, 344, 80, '#f0fdf4', '#86efac', t, subs, tsize=12)

# ============ ③ 机制层 ============
sec(548, '③ 机制层（硬约束 —— 不靠自觉靠拦截）')
node(56, 560, 344, 88, '#ede9fe', '#c4b5fd', '.claude/hooks/guard_write.py', ['PreToolUse 钩子：保护路径写入直接 block', '默认 application*.yml / db / sql / pom', '变更须 design.md 声明 + Reviewer 过审'])
node(413, 560, 344, 88, '#ede9fe', '#c4b5fd', 'openspec/config.yaml', ['spec-driven 工件链强制顺序', 'tdd_enforcement / ordering: strict', 'model_routing_hints · protected_paths'])
node(770, 560, 344, 88, '#ede9fe', '#c4b5fd', 'Git 流（唯一写通道）', ['feature/{change-id} → MR → 人审合并', '禁直推保护分支', 'commit 后立即 push（跨 runtime 可见）'])

# ============ ④ 建设流程 ============
sec(672, '④ 建设流程（aicoding-harness-bootstrap · chat 内单会话执行 · 一次性）')
steps = [
    (56,  '① 前置', ['checkout · 建分支', '已有文档 → 对齐模式', '数据库预检（密码两路）']),
    (269, '② 铺 skeleton', ['20+ 文件原样拷入', '含模板与 {{占位符}}', '结构权威源']),
    (482, '③ 代码分析填充', ['逐条消灭 {{占位符}}', '每条须有代码证据', '库文档走专用 skill']),
    (695, '④ hook 自测', ['guard_write.py 落位', '写保护路径应被 block', '普通路径应放行']),
    (908, '⑤ 交付', ['feature/init-harness', '占位未清不得 commit', '人审 MR + 审宪法']),
]
for x, t, subs in steps:
    node(x, 684, 198, 100, '#ffffff', '#93c5fd', t, subs, tsize=12)
for x1 in (254, 467, 680, 893):
    lines.append(f'  <path d="M {x1},734 L {x1+10},734" fill="none" stroke="#2563eb" stroke-width="1.8" marker-end="url(#arrow-blue)"/>')

# ============ ⑤ 双重防守 ============
sec(808, '⑤ 文档漂移双重防守')
node(56, 820, 520, 64, '#fef2f2', '#fca5a5', '第一道 · 变更随行（主防线）', ['代码结构变更 → 同一 change 内更新文档', 'Tech-Lead 显式排 task · 禁止事后补文档'], tsize=12)
node(594, 820, 520, 64, '#fef2f2', '#fca5a5', '第二道 · 周级对账（兜底）', ['DocKeeper 周一 autopilot · diff 基线以来变更', 'doc-audit MR · 基线表随 MR 前移 · 无差异静默'], tsize=12)

# ============ 右侧栏：角色必读路由 ============
box(1160, 88, 250, 770, fill='#f9fafb', stroke='#e5e7eb', sw=1, rx=10)
text(1285, 112, '角色必读路由', size=13, fill='#374151', anchor='middle', weight=600)
routes = [
    ('PM', ['product → architecture', '→ database → implicit-contracts', '（+ help，涉及时）']),
    ('Tech-Lead', ['architecture/index', '→ lessons 全部']),
    ('Developer', ['architecture（代码落位）', '→ standards 对应篇', '→ lessons/Developer']),
    ('Tester', ['standards/testing', '→ lessons/Tester']),
    ('Reviewer', ['standards 全部', '→ lessons 全部']),
    ('DevOps', ['lessons 全部']),
]
ry = 126
for name, subs in routes:
    box(1172, ry, 226, 86, fill='#ffffff', stroke='#cbd5e1', sw=1.2)
    text(1285, ry + 20, name, size=12, fill='#111827', anchor='middle', weight=600)
    sy = ry + 38
    for s in subs:
        text(1285, sy, s, size=10.5, fill='#6b7280', anchor='middle')
        sy += 15
    ry += 98

box(1172, 714, 226, 66, fill='#ffffff', stroke='#cbd5e1', sw=1.2)
text(1285, 736, '对齐模式', size=12, fill='#111827', anchor='middle', weight=600)
text(1285, 752, '已有 CLAUDE.md 的仓库：', size=10.5, fill='#6b7280', anchor='middle')
text(1285, 766, '对照骨架补缺节，不覆盖定制', size=10.5, fill='#6b7280', anchor='middle')
box(1172, 788, 226, 56, fill='#ffffff', stroke='#cbd5e1', sw=1.2)
text(1285, 808, 'skeleton/ = 结构权威源', size=12, fill='#111827', anchor='middle', weight=600)
text(1285, 824, '章节变更回写；内容演进走 MR', size=10.5, fill='#6b7280', anchor='middle')
text(1285, 840, '（周级对账兜漂移）', size=10.5, fill='#6b7280', anchor='middle')

lines.append('</svg>')

import io
out = io.open('D:/project/sunny-multica-skills/docs/images/harness-repo-structure.svg', 'w', encoding='utf-8')
out.write('\n'.join(lines))
out.close()
print('SVG generated:', len(lines), 'lines')
