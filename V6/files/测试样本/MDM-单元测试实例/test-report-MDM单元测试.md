# MDM 单元测试报告实例（test-report）

> 来源：`http://192.168.45.236/MDM/sunny-mdm.git` master 分支 `sunny-mdm-service` 模块。
> 执行命令：`mvn test -Dtest=...`（Maven + JDK 1.8），surefire 输出原文见同目录 `*.txt`。
> 用途：4.3 综合测试举证 §3.6 测试样本实例——AI 编码流水线交付的单元测试真实运行记录。

## 一、测试范围与结果总览

| 测试类 | 对应 change（openspec 工件） | 阶段 | Tests run | Failures | Errors | Skipped |
|---|---|---|---|---|---|---|
| PlmViewVariantServiceImplTest | 2026-06-24-plm-variant-view-iface（PLM 继承接口） | Harness V2 | **18** | 0 | 0 | 0 |
| PlmViewVariantControllerTest | 同上 | Harness V2 | **6** | 0 | 0 | 0 |
| MdmViewManagementAutoServiceImplTrimTest | 2026-07-17-mdm-view-import-trim（视图导入数据清洗） | Harness V2 | **5** | 0 | 0 | 0 |
| MdmViewManagementServiceImplPriceMaskTest | 2026-09-24-add-sensitive-field-mask-role（敏感字段价格脱敏） | Multica | **5** | 0 | 0 | 0 |
| MdmWlglControllerPlmWuliaoInsertTest | 物流管理 PLM 物料插入 | Harness V2 | **7** | 0 | 0 | 0 |
| **合计** | | | **41** | **0** | **0** | **0** |

**构建结果：BUILD SUCCESS**（Maven surefire，Time elapsed 合计约 2.5 s）。

## 二、与实战记录的口径对照

- 2026.06 MDM「PLM 继承接口」实战交付当期记录为 **Tests run: 22, Failures: 0, BUILD SUCCESS**（`files/实战记录/MDM-PLM继承接口/6.md`）；当前 master 上 PLM 相关测试为 24 项（Service 18 + Controller 6）——增量来自后续 change `2026-06-25-plm-variant-view-audit-fix`（cBtvalue 纯空格校验）与 `2026-06-29-plm-variant-view-exception-handling`（Controller 兜底 try-catch）按 TDD 口径补充，只增不减，增量测试与既有测试共存且全部通过。
- 后续新增测试类（Trim 5 项 / PriceMask 5 项）同样全绿——TrimTest 属 Harness V2 阶段 change `2026-07-17-mdm-view-import-trim`、PriceMaskTest 属 Multica 阶段 change `2026-09-24-add-sensitive-field-mask-role`（归属经 git 历史核实，见《测试分析报告》§3.6 归属说明），两代阶段共享同一套测试规范（standards/testing.md：新代码 TDD 不降级、旧代码修改降级条件、被测对象禁止 mock 自己证明自己）。

## 三、测试设计要点（对应 standards/testing.md 条款）

- **被测对象不 mock 自己**：PlmViewVariantServiceImplTest 以真实 Service 逻辑为被测对象，mock 仅用于 Mapper 边界；
- **私有工具方法反射直测**：TrimTest 通过反射调用 `trimDataMap` 私有方法，断言含全角空格（U+3000）/ 不换行空格（U+00A0）清洗、非字符串值保持原引用、空串与纯空白归一；
- **边界与异常路径**：ControllerTest 覆盖 PLM 接口异常与"新增成功后回滚"路径（日志可见 ERROR 分支被测试触达，属预期异常场景验证，非测试失败）；
- **切片测试降级有据**：@WebMvcTest 被 Redis 依赖链阻塞时降级纯 Mockito 切片测试，该决策作为教训记录于实战记录 6.md。

## 四、证据文件清单

- `com.sunny.modules.mdmviewmanagement.PlmViewVariantServiceImplTest.txt`（18/0）
- `com.sunny.modules.mdmviewmanagement.PlmViewVariantControllerTest.txt`（6/0）
- `com.sunny.modules.mdmviewmanagement.service.impl.MdmViewManagementAutoServiceImplTrimTest.txt`（5/0）
- `com.sunny.modules.mdmviewmanagement.service.impl.MdmViewManagementServiceImplPriceMaskTest.txt`（5/0）
- `com.sunny.modules.mdmwlgl.MdmWlglControllerPlmWuliaoInsertTest.txt`（7/0）
- 测试源码副本：`MdmViewManagementAutoServiceImplTrimTest.java`、`MdmViewManagementServiceImplPriceMaskTest.java`
