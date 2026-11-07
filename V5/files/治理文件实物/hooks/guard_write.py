#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L7 安全保护层 - guard_write.py
================================
触发: PreToolUse (Edit | Write)
作用: 拦截对敏感文件的写入,强制人工确认

拦截规则 (基于 sunny-qms-service 项目实际):
  a. application.yml / application*.properties
     - 配置文件,含数据库连接 / 密钥 / 第三方凭证
  b. src/main/resources/db/migration/
     - Flyway / Liquibase 数据库迁移,生产 DDL
  c. src/main/resources/sql/
     - 手工 SQL 脚本,通常用于数据修复 / 初始化
  d. 财务相关包路径 (com.*.finance 或目录 finance/)
     - 涉及金额计算 / 账务,风险最高

白名单: 环境变量 HARNESS_ALLOW_WRITE=1 时全部跳过
        (仅 HyperSpec 编排器在受控流程中使用)

输出: 拦截时 exit(1) + stderr 打印原因,工具调用被阻止
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


# 命中即拦截的路径模式 (正则,大小写不敏感,匹配 posix 路径)
# 这些模式针对 sunny-qms-service 实际结构
BLOCKED_PATTERNS = [
    # a. Spring Boot 配置文件 (根路径或任意子目录下)
    (re.compile(r"(^|/)application.*\.ya?ml$", re.IGNORECASE),
     "Spring Boot YAML 配置 (可能含数据库/密钥)"),
    (re.compile(r"(^|/)application.*\.properties$", re.IGNORECASE),
     "Spring Boot properties 配置 (可能含数据库/密钥)"),

    # b. 数据库迁移目录 (Flyway / Liquibase)
    (re.compile(r"/db/migration/", re.IGNORECASE),
     "Flyway/Liquibase 数据库迁移目录"),
    (re.compile(r"/db/changelog/", re.IGNORECASE),
     "Liquibase changelog 目录"),

    # c. 手工 SQL 脚本目录
    (re.compile(r"/resources/sql/", re.IGNORECASE),
     "手工 SQL 脚本目录"),

    # d. 财务相关包/目录 (com.xxx.finance 或目录 finance/)
    (re.compile(r"/com/\w+/finance/", re.IGNORECASE),
     "财务包路径 (金额/账务)"),
    (re.compile(r"(^|/)finance/.*\.(java|kt|py|ts|js)$", re.IGNORECASE),
     "finance/ 目录下的代码"),
]

# 显式允许的例外 (例如测试 fixtures / 模板)
ALLOWED_PATTERNS = [
    re.compile(r"/src/test/.*", re.IGNORECASE),           # 测试代码
    re.compile(r"/test/resources/.*", re.IGNORECASE),
    re.compile(r"/__tests__/.*", re.IGNORECASE),
    re.compile(r"\.test\.(java|kt)$", re.IGNORECASE),
    re.compile(r"/target/classes/.*", re.IGNORECASE),     # 编译产物,只读
    re.compile(r"/build/.*", re.IGNORECASE),
    re.compile(r"\.example$", re.IGNORECASE),             # 示例文件
]


def normalize(path: str) -> str:
    """转 posix + 规范化,便于跨平台匹配"""
    p = path.replace("\\", "/")
    # 去掉 ./ ../ 前缀
    p = re.sub(r"^\./+", "", p)
    return p


def is_blocked(path: str):
    """返回 (blocked, reason)"""
    n = normalize(path)

    # 先检查白名单
    for pat in ALLOWED_PATTERNS:
        if pat.search(n):
            return (False, None)

    # 再检查黑名单
    for pat, reason in BLOCKED_PATTERNS:
        if pat.search(n):
            return (True, reason)

    return (False, None)


def main():
    # 白名单逃生阀: 编排器专用
    if os.environ.get("HARNESS_ALLOW_WRITE", "") == "1":
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        # 解析失败,保守放行 (避免 hook 错误锁死工具)
        sys.stderr.write("[guard_write] stdin parse failed: %s\n" % e)
        sys.exit(0)

    tool = payload.get("tool_name", "")
    if tool not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        sys.exit(0)

    blocked, reason = is_blocked(file_path)
    if not blocked:
        sys.exit(0)

    # 拦截: exit 2 让 Claude Code 知道这是"阻止"决策,stderr 会回显给模型
    msg = (
        "\n"
        "========================================================\n"
        " [guard_write] 写入被拦截 - 需要人工确认\n"
        "========================================================\n"
        " 文件: %s\n"
        " 原因: %s\n"
        "--------------------------------------------------------\n"
        " 若确需修改:\n"
        "   1. 向用户说明修改必要性与影响范围\n"
        "   2. 获得用户明确同意\n"
        "   3. 受控流程下可设置 HARNESS_ALLOW_WRITE=1 临时绕过\n"
        "      (仅 HyperSpec 编排器使用,绕过即丧失保护)\n"
        "========================================================\n"
    ) % (file_path, reason)
    sys.stderr.write(msg)
    sys.exit(2)


if __name__ == "__main__":
    main()
