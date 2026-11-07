## Context

非SAP视图（mdmViewNonsap）是 MDM 物料视图管理模块的一部分，存储非 SAP 物料的扩展信息。当前页面只有查询和修改功能，需要新增审核、批量修改模版下载、批量修改三个功能。

**现有架构**：
- 前端：Vue 2.7 + Vuex + Element UI，按钮通过数据库配置
- 后端：Spring Boot + MyBatis + Oracle，Controller-Service-Mapper 三层架构
- 复用机制：非SAP视图数据通过 `nZhuid`（主物料ID）和 `cGongchang`（工厂）与 ALL 视图关联

## Goals / Non-Goals

**Goals:**
- 新增审核按钮，复用 ALL 视图审核逻辑
- 新增批量修改模版下载功能，导出非 SAP 视图字段
- 新增批量导入修改功能，只更新非 SAP 视图数据
- 保持与现有代码风格一致

**Non-Goals:**
- 不修改 ALL 视图的现有功能
- 不新增数据库表
- 不涉及 SAP 接口调用（审核由 ALL 视图统一处理）

## Decisions

### 1. 审核功能实现

**决策**：Controller 采用与 `mdmViewAll_sh` 完全相同的编排模式，Service 仅负责 NonSAP→ALL 视图转换

**理由**：
- ALL 视图审核逻辑（`mdmViewAll_sh`）已包含完整的校验
- 审核+SAP PO发送+9999工厂逻辑已在 `mdmViewAll_sh` Controller 中验证，直接复用该模式
- Service 层只做数据转换（NonSAP ID → ALL 视图记录），职责清晰

**实现方式**：
```
Controller: mdmViewNonsap_sh（与 mdmViewAll_sh 相同编排模式）
  for each nonsapId in idList:
    1. 构造单元素 idList 的 DTO
    2. 调用 Service.mdmViewNonsap_sh(singleDTO) → 转换 + 审核并返回结果
    3. 审核成功后: post_sap → mdmViewAll_fspo（发PO）
    4. 发PO成功后: 9999工厂逻辑（mdmViewAll_fspo_937）

Service: mdmViewNonsap_sh（单ID转换+审核）
  nonsapId → MdmViewNonsap(nZhuid, cGongchang) → MdmViewAll → mdmViewAll_sh
  直接返回 mdmViewAll_sh 的结果（含 MdmViewAll 数据，供 Controller 进行 PO 发送）
```

### 1b. 修改保存时重置审核状态

**决策**：在 `mdmViewNonsap_update` 中新增 `reset_shzt_all` 调用，将对应 ALL 视图的审核字段重置为未审核（N_SHZT=0）

**理由**：
- 非 SAP 视图修改后，关联的 ALL 视图数据发生变化，审核状态应回归未审核
- 与现有 `po_zt_fail_all`（重置同步状态 N_SFTB=0）保持一致的模式

**实现方式**：
- 新增 `MdmViewAllMapper.reset_shzt_all` 方法：`UPDATE ${table} SET N_SHZT=0 WHERE n_zhuid=? AND c_gongchang=?`
- 在 `mdmViewNonsap_update` 中紧接 `po_zt_fail_all` 之后调用
- 同时在日志记录部分，通过 `getbywuliao` 查询对应 ALL 视图 ID，将操作日志也存到 ALL 视图（参照 `mdmViewAll_update` 的日志记录模式）

### 2. 模版导出实现

**决策**：在 `MdmViewAllExportHandler` 中新增非 SAP 视图导出逻辑

**备选方案**：
- A. 新建 `MdmViewNonsapExportHandler` - 独立但代码重复
- B. 在现有 Handler 中扩展 - 复用代码，推荐

**理由**：复用现有的表头配置和数据字典转换逻辑，减少代码重复

**实现方式**：
- 新增 `customTableHead_nonsap` 方法定义非 SAP 视图表头
- 新增 `exportNonsapTemplate` 方法导出模版
- Mapper 新增 `selectNonsapForExport` 查询

### 3. 批量导入实现

**决策**：新增 `mdmViewNonsap_importExcel` 方法，参照 `mdmViewAll_importExcel` 简化实现

**理由**：
- 非 SAP 视图字段较少，校验逻辑简单
- 复用 `insert_ll` 履历记录逻辑

**实现方式**：
```
importExcel(Dict dict, List<Map> dataMap, LogCommonDTO logCommonDTO)
  → 数据校验（工厂、必填字段、字典值）
  → 批量更新 MDM_VIEW_NONSAP 表
  → 调用 insert_ll 记录履历
  → saveOperatorLogSimple(logCommonDTO)
```

### 4. 前端组件设计

**决策**：参照 `mdmViewAllExport.vue` 创建 `mdmViewNonsapExport.vue`

**实现要点**：
- 复用工厂选择、模版类型选择 UI
- 调用非 SAP 视图专用 API
- 通过 Vuex `show` action 控制弹窗显示

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 审核时数据转换可能失败 | 增加关联数据存在性校验 |
| 导入数据量大时内存溢出 | 复用框架的分批处理机制 |
| 与 ALL 视图功能耦合 | 仅通过接口调用，不直接依赖内部实现 |

## Implementation Details

### 后端接口清单

| 接口 | URL | 说明 |
|------|-----|------|
| mdmViewNonsap_sh | POST /mdmViewNonsap/sh | 审核 |
| mdmViewNonsap_exportInit | POST /mdmViewNonsap/exportInit | 模版初始化 |
| mdmViewNonsap_template | POST /mdmViewNonsap/template | 模版导出 |
| mdmViewNonsap_importExcel | POST /mdmViewNonsap/importExcel | 批量导入 |

### 前端文件清单

| 文件 | 变更 |
|------|------|
| mdmViewNonsap.js (Store) | 新增 sh、show action |
| mdmViewNonsapApi.js | 新增 shById、exportOpenInit、exportExcel API |
| mdmViewNonsapExport.vue | 新建导出弹窗组件 |
| mdmViewNonsapQuery.vue | 引入导出组件 |

### 后端文件清单

| 文件 | 变更 |
|------|------|
| MdmViewManagementController.java | 新增 4 个接口，mdmViewNonsap_sh 采用完整编排模式 |
| IMdmViewManagementService.java | 新增 4 个方法声明 |
| MdmViewManagementServiceImpl.java | 新增 4 个方法实现，mdmViewNonsap_update 新增审核状态重置及ALL视图日志记录 |
| MdmViewAllMapper.java | 新增 reset_shzt_all 方法声明 |
| MdmViewAllMapper.xml | 新增 reset_shzt_all SQL |
| MdmViewManagementServiceImpl.java | 新增 4 个方法实现 |
| MdmViewAllExportHandler.java | 新增非 SAP 视图导出逻辑 |
| MdmViewNonsapMapper.xml | 新增导出查询 SQL |
