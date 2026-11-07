#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L7 安全保护层 - ensure_change_context.py
=========================================
触发: PreToolUse (Bash)
作用: 无 active OpenSpec change 时,阻止危险 shell 命令

设计理念:
  在 spec-driven 流程下, 任何破坏性动作 (push/amend/reset/deploy/migrate)
  都应当发生在一个明确的 change context 中 (openspec/changes/<id>/ 存在).
  若 changes/ 目录为空, 说明当前不在任何受控变更中,
  此时的破坏性命令极有可能是"顺手做" -> 风险极高.

拦截的危险命令模式:
  - git push             (代码已出仓)
  - git commit --amend   (改写历史)
  - git reset --hard     (丢弃工作区)
  - git push --force     (覆盖远端)
  - mvn deploy           (产物推到制品库)
  - docker push          (镜像出仓)
  - flyway migrate / liquibase update  (生产数据库 DDL/DML)
  - psql/mysql 执行 .sql 文件
  - DROP / TRUNCATE / ALTER TABLE

放行条件 (任一满足):
  1. openspec/changes/ 下存在至少一个非 README/archive 子目录或 .md 文件
  2. 环境变量 HARNESS_ALLOW_DANGER=1 (编排器逃生阀)
  3. 命令本身不在危险列表中
"""

import json
import os
import re
import sys

# 强制 UTF-8 输出 (Windows 默认 GBK 会破坏中文,且 Claude Code 按 UTF-8 解析 stderr)
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


# 危险命令模式 (正则,大小写不敏感,搜索 command 字符串任意位置)
DANGEROUS_PATTERNS = [
    (re.compile(r"\bgit\s+push\b", re.IGNORECASE),
     "git push (代码出仓)"),
    (re.compile(r"\bgit\s+commit\s+--amend\b", re.IGNORECASE),
     "git commit --amend (改写历史)"),
    (re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
     "git reset --hard (丢弃工作区)"),
    (re.compile(r"\bgit\s+.*--force(-push)?\b", re.IGNORECASE),
     "git --force (覆盖远端)"),
    (re.compile(r"\bgit\s+branch\s+-D\b", re.IGNORECASE),
     "git branch -D (删除分支)"),

    (re.compile(r"\bmvn\s+deploy\b", re.IGNORECASE),
     "mvn deploy (推到制品库)"),
    (re.compile(r"\bmvn\s+release\b", re.IGNORECASE),
     "mvn release (发布)"),

    (re.compile(r"\bdocker\s+push\b", re.IGNORECASE),
     "docker push (镜像出仓)"),

    # 数据库迁移工具
    (re.compile(r"\bflyway\b.*\bmigrate\b", re.IGNORECASE),
     "flyway migrate (数据库迁移)"),
    (re.compile(r"\bliquibase\b.*\bupdate\b", re.IGNORECASE),
     "liquibase update (数据库迁移)"),

    # 直连数据库执行 SQL 文件
    (re.compile(r"\b(psql|mysql|mariadb)\s+.*-f\b", re.IGNORECASE),
     "直连数据库执行 SQL 文件"),
    (re.compile(r"\b(psql|mysql|mariadb)\s+.*<\s*\S+\.sql", re.IGNORECASE),
     "通过重定向灌入 SQL 文件"),

    # 危险 SQL 关键字 (针对 mvn 的 sql:execute 或类似)
    (re.compile(r"\b(DROP\s+(DATABASE|TABLE|SCHEMA))\b", re.IGNORECASE),
     "DROP DATABASE/TABLE/SCHEMA"),
    (re.compile(r"\bTRUNCATE\s+TABLE\b", re.IGNORECASE),
     "TRUNCATE TABLE"),
]


def has_active_change() -> bool:
    """检查 openspec/changes/ 是否有 active change"""
    # 从 hook 脚本位置回推项目根
    # .claude/hooks/ensure_change_context.py -> 项目根是 .claude/..
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    changes_dir = os.path.join(project_root, "openspec", "changes")

    if not os.path.isdir(changes_dir):
        return False

    for entry in os.listdir(changes_dir):
        full = os.path.join(changes_dir, entry)
        # 忽略 README / 隐藏文件 / archive 目录 (archive 是已归档历史)
        if entry.upper().startswith("README"):
            continue
        if entry.startswith("."):
            continue
        if entry.lower() == "archive":
            continue
        # 子目录 = 一个 active change
        if os.path.isdir(full):
            return True
        # .md 文件 (非 README) = 一个 active change
        if entry.lower().endswith(".md"):
            return True

    return False


def is_dangerous(command: str):
    """返回 (dangerous, reason)"""
    for pat, reason in DANGEROUS_PATTERNS:
        if pat.search(command):
            return (True, reason)
    return (False, None)


def main():
    if os.environ.get("HARNESS_ALLOW_DANGER", "") == "1":
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        sys.stderr.write("[ensure_change_context] stdin parse failed: %s\n" % e)
        sys.exit(0)

    if payload.get("tool_name", "") != "Bash":
        sys.exit(0)

    command = (payload.get("tool_input", {}) or {}).get("command", "") or ""
    if not command:
        sys.exit(0)

    dangerous, reason = is_dangerous(command)
    if not dangerous:
        sys.exit(0)

    if has_active_change():
        sys.exit(0)

    # 无 active change + 危险命令 = 阻止
    msg = (
        "\n"
        "========================================================\n"
        " [ensure_change_context] 危险命令被拦截\n"
        "========================================================\n"
        " 命令: %s\n"
        " 原因: %s\n"
        "--------------------------------------------------------\n"
        " 当前 openspec/changes/ 为空, 不存在 active change.\n"
        " spec-driven 流程下, 破坏性动作必须发生在 change context 中.\n"
        "--------------------------------------------------------\n"
        " 若确需执行:\n"
        "   1. 先创建 change: /opsx:new 或 /opsx:propose\n"
        "   2. 或获得用户明确同意后设置 HARNESS_ALLOW_DANGER=1\n"
        "      (绕过保护, 风险自负)\n"
        "========================================================\n"
    ) % (command, reason)
    sys.stderr.write(msg)
    sys.exit(2)


if __name__ == "__main__":
    main()
