## Why

非SAP视图页面目前缺少审核、批量修改模版下载、批量修改三个核心功能，用户需要切换到ALL视图才能完成这些操作，影响工作效率。本次变更将这三个功能直接集成到非SAP视图页面，复用ALL视图的已有业务逻辑。

## What Changes

### 1. 审核按钮 (mdmViewNonsap/sh)
- **前端**：新增 `sh` action，参照现有 `edit` 方法模式，调用审核 API
- **后端**：Controller `mdmViewNonsap_sh` 采用与 `mdmViewAll_sh` 相同的完整编排模式（遍历ID→转换+审核→发PO→9999工厂逻辑）；Service `mdmViewNonsap_sh` 负责单个NonSAP ID到ALL视图的转换+审核

### 1b. 修改保存重置审核状态及日志记录 (mdmViewNonsap/update)
- **后端**：在 `mdmViewNonsap_update` 中新增 `reset_shzt_all` 调用，修改保存时将对应ALL视图的审核字段（N_SHZT）重置为0（未审核）；同时通过 `getbywuliao` 查询ALL视图ID，将操作日志也存到ALL视图（参照 `mdmViewAll_update` 模式）

### 2. 批量修改模版下载 (mdmViewNonsap/show)
- **前端**：新增 `mdmViewNonsapExport.vue` 组件，参照 `mdmViewAllExport.vue` 弹窗机制
- **后端**：新增 `mdmViewNonsap_exportInit` 和 `mdmViewNonsap_template` 接口，复用 `MdmViewAllExportHandler` 但只导出非SAP视图字段

### 3. 批量修改按钮 (daoru/show)
- **前端**：复用公共 `importDialog` 组件（已自动调用）
- **后端**：新增 `mdmViewNonsap_importExcel` 方法，参照 `mdmViewAll_importExcel`，只处理非SAP视图的批量更新

## Capabilities

### New Capabilities

无

### Modified Capabilities

- `mdmviewmanagement`: 扩展非SAP视图功能，新增审核、批量修改模版下载、批量导入修改三个功能

## Impact

### 前端影响
| 文件 | 变更 |
|------|------|
| `src/store/modules/mdmViewNonsap/mdmViewNonsap.js` | 新增 `sh`、`show` action |
| `src/api/mdmViewNonsap/mdmViewNonsapApi.js` | 新增 `shById`、`exportOpenInit`、`exportExcel` API |
| `src/views/mdmViewNonsap/mdmViewNonsapExport.vue` | 新建导出弹窗组件 |
| `src/views/mdmViewNonsap/mdmViewNonsapQuery.vue` | 引入导出组件 |

### 后端影响
| 文件 | 变更 |
|------|------|
| `MdmViewManagementController.java` | 新增 5 个接口，mdmViewNonsap_sh 采用完整编排模式 |
| `IMdmViewManagementService.java` | 新增 5 个方法声明 |
| `MdmViewManagementServiceImpl.java` | 新增 5 个方法实现，mdmViewNonsap_update 新增审核状态重置及ALL视图日志记录 |
| `MdmViewAllMapper.java` | 新增 reset_shzt_all 方法 |
| `MdmViewAllMapper.xml` | 新增 reset_shzt_all SQL |
| `MdmViewAllExportHandler.java` | 新增非SAP视图导出逻辑（或新建 Handler） |

### 依赖关系
- 审核功能复用 `mdmViewAll_sh` 核心逻辑，Controller 层包含完整编排（SAP PO发送、9999工厂逻辑）
- 修改保存时通过 `reset_shzt_all` 重置 ALL 视图审核状态，并将操作日志同时记录到 ALL 视图
- 导出功能复用 `MdmViewAllExportHandler` 的表头配置
- 导入功能复用 `insert_ll` 履历记录逻辑
