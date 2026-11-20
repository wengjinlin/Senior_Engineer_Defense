## Context

商品码（`MDM_VIEW_BASIC_SPMD.C_SPM`）有三条写入路径，空格处理现状不一致：

| 路径 | 入口 | 现状 |
|------|------|------|
| 基本视图修改→商品码对应 | `mdmViewBasic_update`（Impl ~L955） | `trim()` 仅判空；唯一校验/变更检测/insert 用原始值 |
| 大视图修改→商品码对应 | `mdmViewAll_update`（Impl ~L2572） | 同上（与上一条代码几乎重复） |
| 大视图→商品码批量导入 | `mdmViewBasicSpmd_importExcel`（Impl ~L5726） | 已 `String.trim()`，但去不掉全角空格 U+3000 与不换行空格 U+00A0 |

实时校验 `mdmViewBasic_check_spmd`（Impl ~L5716）用原始值查询。唯一性 SQL `checkUniqueWithWlbm` 为精确等值匹配（`C_SPM = #{cSpm}`），空格变体击穿唯一性并误触发状态重置。

**约束**：
- 表结构参考 `docs/database/mdm_view_basic_spmd.sql`：`UK_SPMD_SPLX_SPM` 唯一索引 (C_SPLX, C_SPM)；表**无 dUpdateTime**，仅有 TS 时间戳——存量冲突记录无可靠的"新旧"判定依据
- 隐性约定（`docs/architecture/implicit-contracts.md`）：本变更不修改接口返回结构、状态字段语义、默认值语义；变更检测逻辑本身不动，仅其输入值被清洗，无兼容性破坏
- 本变更为旧代码修改（非 harness 新建模块），测试策略按"修改旧代码降级"路径：手工验证 + prepare-review 声明

## Goals / Non-Goals

**Goals:**
- 三条写入路径 + 实时校验统一清洗口径：首尾 ASCII 空白 + 全角空格（U+3000）+ 不换行空格（U+00A0）
- 清洗发生在校验之前，必填/列表内去重/全局唯一/变更检测/insert 全链路使用干净值
- 交付存量清洗 SQL（含核查语句），由人工执行、人工处理清洗后暴露的冲突

**Non-Goals:**
- 前端组件不改动（后端兜底，用户决策）
- 不做自动去重 / 自动清洗存量数据
- 不处理字段**中间**的空白字符（只动首尾）
- 不改动 Mapper SQL、表结构、接口出入参

## Decisions

### D1: strip 实现为 `MdmViewManagementServiceImpl` 私有方法

```java
private String strip(String s) {
    if (s == null) return null;
    return s.replaceAll("^[\\s\\u00A0\\u3000]+|[\\s\\u00A0\\u3000]+$", "");
}
```

- Java 8 的 `\s` 不含 U+00A0/U+3000，必须显式列出
- **备选否决**：`String.trim()`（ASCII only，正是本次要修的漏洞）；`Character.isWhitespace`（含 U+3000 但不含 U+00A0，语义绕）；引入 commons-lang（违反"平台包优先/禁止引入重叠依赖"项目规则）
- 不建公共工具类：当前仅此一个类使用，避免过早抽象

### D2: 清洗位置 = 校验循环开头回写实体

在 `mdmViewBasic_update`（~L960）与 `mdmViewAll_update`（~L2577）的判空校验 `for` 循环开头执行：

```java
spmd.setcSplx(strip(spmd.getcSplx()));
spmd.setcSpm(strip(spmd.getcSpm()));
spmd.setcBeizhu(strip(spmd.getcBeizhu()));
```

- 回写后，后续判空（`trim().isEmpty()` 判断自然覆盖清洗结果）、列表内去重、`checkUniqueWithWlbm`、newKeys/oldKeys 变更检测、`insertBatch` 全部自动使用干净值——**一处清洗，全链路一致**
- **备选否决**：在各校验点分别 strip（散落多处，易漏，且 insert 仍可能用原始值）；SQL 层 `TRIM()` 匹配（`TRIM(C_SPM) = #{cSpm}` 会使 UK_SPMD_SPLX_SPM 索引失效，且治标不治本）
- 两处 update 路径代码是既有重复结构，按项目现状各加三行，不合并重构

### D3: `mdmViewBasic_check_spmd` 入参同步清洗

查询前对 `cSplx`/`cSpm` 执行 strip，保证"实时校验说无冲突 → 保存时也无冲突"的口径一致。

### D4: 导入解析升级为 strip

`mdmViewBasicSpmd_importExcel` L5734-5736 的 `.toString().trim()` 替换为 strip 后的值，其余校验链不动。

### D5: 存量清洗 SQL 只交付、人工执行

**涉及表与操作**（参考 `docs/database/mdm_view_basic_spmd.sql`）：

| 语句 | 类型 | WHERE 范围 | 索引影响 |
|------|------|-----------|---------|
| 核查 SQL | SELECT（只读） | `C_SPLX`/`C_SPM`/`C_BEIZHU` 首尾含 ASCII 空白、CHR(12288) 全角空格、CHR(160) NBSP 的行 | 无 |
| 清洗 SQL | UPDATE（写 C_SPLX/C_SPM/C_BEIZHU） | 同上，且排除"清洗后变为空"的行 | UPDATE 维护 `UK_SPMD_SPLX_SPM` 唯一索引；若清洗后与已有组合重复 → **ORA-00001 直接报错** |

- Oracle `REGEXP_REPLACE(col, '^[ ... ]+|[ ... ]+$', '')` 实现首尾清洗，字符类含 `' '`、`CHR(9/10/13)`、`CHR(160)`、`CHR(12288)`
- **边界**：值为纯空白的行清洗后变 NULL，违反 `C_SPLX/C_SPM NOT NULL` 约束 → 清洗 SQL 的 WHERE 显式排除（`TRIM(...)` 非空条件），此类行由核查 SQL 单独暴露，人工删除
- **冲突处理（人工）**：执行中 ORA-00001 时，用核查 SQL 定位 trim 后重复的组合，人工决定保留哪条（表无 dUpdateTime，不能按时间自动判定），删除后重跑
- 交付物放 `docs/database/` 下的 SQL 说明文件，不进 `src/main/resources/db/`（受保护目录，且不由应用执行）

## Risks / Trade-offs

- [清洗后暴露存量重复，UPDATE 报 ORA-00001] → 预期行为；核查 SQL 提前发现，人工处理后重跑；交付文档写明操作步骤
- [纯空白值的脏行清洗后违反 NOT NULL] → WHERE 排除 + 核查 SQL 单独暴露，人工删除
- [前端不清洗，用户在界面上仍看到自己输入的空格] → 后端落库为干净值，重新打开即正常；用户已确认接受
- [正则每次编译的开销] → 行数为个位数级（商品码列表），可忽略；如需优化可预编译 Pattern，暂不做
- [check_spmd 与保存校验仍有极小时间窗] → 既有行为，不因本变更恶化

## Migration Plan

1. 后端发版（增量清洗生效）
2. 人工执行核查 SQL → 确认量级与冲突组合
3. 人工处理冲突（删除/修改重复行）
4. 人工执行清洗 SQL
5. 回滚：代码回退即可；清洗 SQL 为数据订正，回滚依赖执行前人工备份（文档中提示先 `CREATE TABLE ... AS SELECT` 备份）

## Open Questions

（无——strip 范围、前端不动、人工清洗三个决策均已确认）
