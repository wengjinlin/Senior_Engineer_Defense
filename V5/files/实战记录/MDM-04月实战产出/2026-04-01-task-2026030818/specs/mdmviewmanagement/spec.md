## ADDED Requirements

### Requirement: 非SAP视图审核按钮
系统 SHALL 在非SAP视图页面提供审核按钮，允许用户对单条非SAP物料记录进行审核操作。

#### Scenario: 成功审核非SAP视图记录
- **WHEN** 用户选中一条非SAP视图记录并点击审核按钮
- **THEN** 系统调用ALL视图审核逻辑，更新审核状态为已审核

#### Scenario: 审核前校验失败
- **WHEN** 用户选中的记录不满足审核条件（如同步中、必填字段缺失）
- **THEN** 系统返回错误提示，不执行审核

#### Scenario: 未选择记录
- **WHEN** 用户未选择任何记录点击审核按钮
- **THEN** 系统提示"请选择一条记录"

#### Scenario: 选择多条记录
- **WHEN** 用户选择多条记录点击审核按钮
- **THEN** 系统提示"只能选择一条记录"

### Requirement: 审核数据转换
系统 SHALL 将非SAP视图数据转换为ALL视图格式后调用审核逻辑。

#### Scenario: 数据转换后审核
- **WHEN** 非SAP视图记录需要审核
- **THEN** 系统根据 nZhuid 和 cGongchang 查询对应的 ALL 视图记录并执行审核

### Requirement: 审核完整编排
系统 SHALL 在非SAP视图审核成功后执行与ALL视图审核相同的后续流程（SAP PO发送、9999工厂逻辑）。

#### Scenario: 审核成功后发送PO
- **WHEN** 非SAP视图记录审核成功
- **THEN** 系统调用 post_sap 获取 PO JSON，再调用 mdmViewAll_fspo 发送 PO

#### Scenario: 审核成功后9999工厂自动分发
- **WHEN** 审核发送 PO 成功，且工厂不为 9999
- **THEN** 系统检查 9999 工厂是否存在且未导入，若未导入则自动发送 937 接口

### Requirement: 审核状态同步
系统 SHALL 在审核成功后同步更新非SAP视图的审核状态字段。

#### Scenario: 审核状态更新
- **WHEN** 审核操作成功完成
- **THEN** 非SAP视图记录的 N_SHZT 字段更新为 1

### Requirement: 修改保存时重置ALL视图审核状态
系统 SHALL 在非SAP视图修改保存时，将对应ALL视图的审核状态重置为未审核（N_SHZT=0），并将操作日志同时记录到ALL视图。

#### Scenario: 修改保存重置审核状态
- **WHEN** 用户修改并保存非SAP视图记录
- **THEN** 系统将对应 ALL 视图记录的 N_SHZT 字段重置为 0（未审核）

#### Scenario: 修改保存日志记录到ALL视图
- **WHEN** 非SAP视图修改保存成功
- **THEN** 系统将操作日志（变更前后数据对比）同时存到 NonSAP 视图（"MDM_VIEW_NONSAP-"+id）和 ALL 视图（"MDM_VIEW_ALL-"+all_id）

### Requirement: 非SAP视图批量修改模版下载弹窗
系统 SHALL 在非SAP视图页面提供模版下载弹窗，参照ALL视图的导出弹窗机制。

#### Scenario: 打开模版下载弹窗
- **WHEN** 用户点击批量修改模版下载按钮 (mdmViewNonsap/show)
- **THEN** 系统弹出模版下载对话框

#### Scenario: 选择工厂和模版类型
- **WHEN** 用户在弹窗中选择工厂和模版类型（新增/修改）
- **THEN** 系统根据选择加载对应的模版字段

### Requirement: 非SAP视图模版导出字段
系统 SHALL 只导出非SAP视图相关的字段，不包含其他视图字段。

#### Scenario: 导出非SAP视图模版
- **WHEN** 用户点击导出按钮
- **THEN** 系统生成仅包含非SAP视图字段的Excel模版

#### Scenario: 按工厂过滤
- **WHEN** 用户选择特定工厂
- **THEN** 导出的模版仅包含该工厂的非SAP视图字段配置

### Requirement: 模版字段配置
系统 SHALL 复用ALL视图的表头配置逻辑，但只取非SAP视图字段。

#### Scenario: 字段表头配置
- **WHEN** 系统生成模版
- **THEN** 表头字段与 MdmViewNonsap 实体字段对应，包含数据字典和下拉选项

### Requirement: 前端导出组件实现
前端 SHALL 创建 mdmViewNonsapExport.vue 组件，复用 mdmViewAllExport.vue 的弹窗机制。

#### Scenario: 组件引入
- **WHEN** mdmViewNonsapQuery.vue 页面加载
- **THEN** 自动引入并注册 mdmViewNonsapExport 组件

### Requirement: 非SAP视图批量导入入口
系统 SHALL 在非SAP视图页面支持批量导入功能，通过 daoru/show 按钮触发。

#### Scenario: 打开导入对话框
- **WHEN** 用户点击批量修改按钮 (daoru/show)
- **THEN** 系统弹出文件上传对话框

#### Scenario: 上传Excel文件
- **WHEN** 用户选择Excel文件并上传
- **THEN** 系统解析文件并调用后端导入方法

### Requirement: 非SAP视图批量更新逻辑
系统 SHALL 只对非SAP视图进行批量更新，不影响其他视图数据。

#### Scenario: 批量更新执行
- **WHEN** 后端接收到导入数据
- **THEN** 系统只更新 MDM_VIEW_NONSAP 表中的记录

#### Scenario: 数据校验
- **WHEN** 导入数据包含校验错误（如必填字段缺失、字典值不合规）
- **THEN** 系统返回错误明细，不执行更新

### Requirement: 履历记录
系统 SHALL 在批量更新完成后记录操作履历，参照 ALL 视图的 insert_ll 方法。

#### Scenario: 记录操作履历
- **WHEN** 批量更新成功
- **THEN** 系统插入履历记录到 mdm_view_dr 表，包含变更前后数据

### Requirement: 导入配置
系统 SHALL 配置导入回调方法，指定服务实例和方法名。

#### Scenario: 导入回调配置
- **WHEN** 资源管理中配置导入按钮
- **THEN** vuex方法为 daoru/show，导入配置格式为：模板标识@文件名,MdmViewManagementServiceImpl,mdmViewNonsap_importExcel
