## 1. 后端 strip 基础

- [x] 1.1 在 `MdmViewManagementServiceImpl` 添加私有方法 `strip(String)`：null 安全，正则去除首尾 ASCII 空白（`\s`）+ 不换行空格（`\u00A0`）+ 全角空格（`\u3000`）

## 2. 写入路径接入清洗

- [x] 2.1 `mdmViewBasic_update`（~L960 判空校验 for 循环开头）：对每行 `spmd` 回写 `setcSplx/setcSpm/setcBeizhu(strip(...))`，使判空、列表内去重、`checkUniqueWithWlbm`、newKeys/oldKeys 变更检测、`insertBatch` 全部使用清洗后值
- [x] 2.2 `mdmViewAll_update`（~L2577 判空校验 for 循环开头）：同 2.1
- [x] 2.3 `mdmViewBasic_check_spmd`（~L5716）：调用 `checkUniqueWithWlbm` 前对入参 `cSplx`/`cSpm` 执行 strip
- [x] 2.4 `mdmViewBasicSpmd_importExcel`（~L5734-5736）：三列的 `.toString().trim()` 替换为 strip 后的值
- [x] 2.5 编译验证：`mvn compile` 通过（JAVA_HOME=/d/jdk1.8.0_171）

## 3. 存量清洗 SQL 交付（仅交付，人工执行）

- [x] 3.1 编写核查 SQL（只读）：识别 `C_SPLX`/`C_SPM`/`C_BEIZHU` 首尾含 ASCII 空白 / CHR(12288) 全角空格 / CHR(160) NBSP 的行、纯空白脏行（清洗后将为空）、清洗后 (C_SPLX, C_SPM) 重复的组合
- [x] 3.2 编写清洗 UPDATE SQL：`REGEXP_REPLACE` 去首尾空白，WHERE 限定核查条件并排除清洗后为空的行
- [x] 3.3 编写操作说明文档（含先备份 `CREATE TABLE ... AS SELECT`、ORA-00001 冲突的人工处理步骤、回滚方式），与 SQL 一并放 `docs/database/`

## 4. 验证（旧代码修改：手工验证 + prepare-review 声明）

- [ ] 4.1 手工验证：基本视图修改→商品码对应，输入 ` ABC `（含全角/半角首尾空格）保存 → 落库为 `ABC`；再次录入同值被唯一校验拦截
- [ ] 4.2 手工验证：大视图修改同样场景，行为与 4.1 一致
- [ ] 4.3 手工验证：导入含全角空格与 NBSP 的商品码 Excel → 落库干净值，文件内去重按清洗值判定
- [ ] 4.4 手工验证：check_spmd 输入 ` ABC ` 命中已有 `ABC` 的冲突并返回物料编码
- [ ] 4.5 prepare-review 摘要声明测试缺口：本变更为旧代码修改，无自动化测试，列明上述手工验证步骤与结果
