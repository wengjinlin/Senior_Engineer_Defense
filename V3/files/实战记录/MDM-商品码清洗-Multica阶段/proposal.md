## Why

商品码（C_SPM）在三条写入路径中均可能带首尾空格落库，破坏业务规则：

1. **大视图修改→商品码对应**（`mdmViewAll_update`）与 **基本视图修改→商品码对应**（`mdmViewBasic_update`）：`trim()` 仅用于判空校验，唯一性校验（`C_SPM = #{cSpm}` 精确匹配）、变更检测（newKeys/oldKeys 拼接比较）、insert 均使用原始值。`" ABC "` 与 `"ABC"` 被视为不同值，导致同一商品码可绑定多个物料（UK 索引也拦不住），并可能误判变更、触发多余的先删后插与同步/审核状态重置。
2. **大视图→商品码批量导入**（`mdmViewBasicSpmd_importExcel`）：已对三列做 `String.trim()`，但 Java `trim()` 只去除 ASCII 空白（≤ U+0020），**去不掉全角空格（U+3000）与不换行空格（U+00A0）**——这两个恰是 Excel 复制粘贴与中文输入法的高频产物。

实时校验接口 `mdmViewBasic_check_spmd` 同样使用原始值查询，与保存校验行为需保持一致。

## What Changes

- `MdmViewManagementServiceImpl` 新增私有 strip 方法：去除首尾 ASCII 空白 + 全角空格（U+3000）+ 不换行空格（U+00A0）
- `mdmViewBasic_update`（~L955）：进入校验循环前将 `cSplx` / `cSpm` / `cBeizhu` 清洗后回写实体，此后判空、列表内去重、全局唯一校验、变更检测、insert 全链路使用干净值
- `mdmViewAll_update`（~L2572）：同上
- `mdmViewBasic_check_spmd`（~L5716）：查询前对入参 strip，与保存校验口径一致
- `mdmViewBasicSpmd_importExcel`（~L5734-5736）：`trim()` 升级为同一 strip 逻辑，堵住全角空格漏洞
- **交付一次性存量清洗 SQL（仅交付，不自动执行）**：定位 C_SPLX / C_SPM 首尾含空白（含全角/不换行空格）的存量记录并清洗
- 前端不改（商品码对应组件维持现状，由后端统一兜底）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `product-code-mapping`: 商品码对应字段在所有保存路径与实时校验中强制清洗首尾空白（含全角空格、不换行空格）；补充存量数据清洗交付物
- `spmd-batch-import`: 导入解析的 trim 升级为含全角/不换行空白的清洗

## Impact

- 后端：`MdmViewManagementServiceImpl`（mdmViewBasic_update、mdmViewAll_update、mdmViewBasic_check_spmd、mdmViewBasicSpmd_importExcel）
- 无 Mapper / 表结构变更
- **存量清洗由人工执行**：清洗 SQL 随变更交付（含执行前的只读核查语句）；清洗后若暴露"类型+商品码"trim 后重复的记录，**保留/删除策略由人工决定与处理**，本变更不含自动去重逻辑
- 风险：清洗 SQL 执行后可能暴露重复数据（UK 语义冲突），需人工核查后处理
