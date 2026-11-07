## 1. 后端 - 审核功能

- [x] 1.1 在 IMdmViewManagementService.java 新增 mdmViewNonsap_sh 方法声明
- [x] 1.2 在 MdmViewManagementServiceImpl.java 实现 mdmViewNonsap_sh 方法（**已重构：处理单个NonSAP ID的转换+审核，直接返回mdmViewAll_sh结果供Controller进行PO发送**）
- [x] 1.3 在 MdmViewManagementController.java 新增 POST /mdmViewNonsap/sh 接口（**已重构：采用与mdmViewAll_sh相同的完整编排模式——遍历ID→转换+审核→发PO→9999工厂逻辑**）

## 1b. 后端 - 修改保存时重置审核状态

- [x] 1b.1 在 MdmViewAllMapper.java 新增 reset_shzt_all 方法声明
- [x] 1b.2 在 MdmViewAllMapper.xml 新增 reset_shzt_all SQL（将 ${table} 的 N_SHZT 设为 0）
- [x] 1b.3 在 MdmViewManagementServiceImpl.mdmViewNonsap_update 中调用 reset_shzt_all，将对应ALL视图的审核字段改为未审核
- [x] 1b.4 在 MdmViewManagementServiceImpl.mdmViewNonsap_update 中，通过 getbywuliao 查询对应ALL视图ID，将操作日志也存到ALL视图（saveOperatorLogAndHistory "MDM_VIEW_ALL-"+all_id）

## 2. 后端 - 模版导出功能

- [x] 2.1 在 MdmViewNonsapMapper.xml 新增 selectNonsapForExport 查询 SQL
- [x] 2.2 在 MdmViewNonsapMapper.java 新增 selectNonsapForExport 方法
- [x] 2.3 ~~在 MdmViewAllExportHandler.java 新增 customTableHead_nonsap 方法定义非SAP视图表头~~（已删除，改用动态获取）
- [x] 2.4 在 IMdmViewManagementService.java 新增 mdmViewNonsap_exportInit 和 mdmViewNonsap_template 方法声明
- [x] 2.5 在 MdmViewManagementServiceImpl.java 实现模版初始化和导出方法（**已重构：参照 mdmViewAll_exportInit 动态获取字段**）
- [x] 2.6 在 MdmViewManagementController.java 新增 POST /mdmViewNonsap/exportInit 和 /mdmViewNonsap/template 接口

## 3. 后端 - 批量导入功能

- [x] 3.1 在 IMdmViewManagementService.java 新增 mdmViewNonsap_importExcel 方法声明
- [x] 3.2 在 MdmViewManagementServiceImpl.java 实现 mdmViewNonsap_importExcel 方法（**已重构：底层调用 mdmViewManagementAutoService.mdmViewAll_importExcel，外层筛选只保留非SAP视图字段**）
- [x] 3.3 在 MdmViewManagementController.java 新增 POST /mdmViewNonsap/importExcel 接口（不需要，导入通过数据库配置回调实现）
- [x] 3.4 准备导入模版文件 resources/excelTemplate/MdmViewNonsapTemplate.xlsx（通过template接口动态生成，不需要静态文件）

## 4. 前端 - 审核功能

- [x] 4.1 在 mdmViewNonsapApi.js 新增 shById API 方法
- [x] 4.2 在 mdmViewNonsap.js (Store) 新增 sh action（参照 edit 方法）
- [x] 4.3 在 mdmViewNonsapQuery.vue 引用 sh action（按钮已在数据库配置）

## 5. 前端 - 模版导出功能

- [x] 5.1 在 mdmViewNonsapApi.js 新增 exportOpenInit 和 exportExcel API 方法
- [x] 5.2 在 mdmViewNonsap.js (Store) 新增 show action
- [x] 5.3 创建 mdmViewNonsapExport.vue 组件（参照 mdmViewAllExport.vue）
- [x] 5.4 在 mdmViewNonsapQuery.vue 引入并注册 mdmViewNonsapExport 组件

## 6. 前端 - 批量导入功能

- [x] 6.1 确认 mdmViewNonsapQuery.vue 已引入 importDialog 组件（公共组件自动调用）
- [x] 6.2 在数据库配置导入按钮的导入/导出配置字段：mdmViewNonsapTemplate@非SAP视图批量修改模版,MdmViewManagementServiceImpl,mdmViewNonsap_importExcel（需在系统管理界面配置）

## 7. 验证

- [ ] 7.1 验证审核功能：选中非SAP视图记录，点击审核按钮，确认审核状态更新（需手动验证）
- [ ] 7.2 验证模版下载：点击按钮弹出选择框，选择工厂和类型后下载模版（需手动验证）
- [ ] 7.3 验证批量导入：上传填写好的模版，确认数据更新正确，履历记录生成（需手动验证）
