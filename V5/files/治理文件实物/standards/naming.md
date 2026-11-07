# 命名规范 (naming.md)

> 基于代码实测的项目命名约定，非 Java 通用规范复述。

## 包名

```
com.sunny
├── StartApplication                  # 启动类（根级，无包）
├── aop / config / exception / constant / utils   # 框架级
├── feign / kafka / schedule          # 外部对接
└── modules.<业务域>                   # 120+ 业务模块
    ├── controller / service / service/impl / dao
    ├── entity / dto / vo / enums / util
    └── handler / config / event      # 部分模块有
```

**规则**：
- 业务域全小写驼峰：`inspectionTask` / `qmsVdaBasic` / `qmsProbfbctrlAbn`
- 模块名首字母大写的（`QmsProbfbZczljzyf` / `QmsProbfbZcycZl`）是历史命名，**新模块不要这样**

## 类名后缀（强制）

| 后缀 | 含义 | 包路径 | 示例 |
|------|------|--------|------|
| `Controller` | HTTP 入口 | `controller/` | `QmsBkmController` |
| `Service`（接口前缀 I） | Service 接口 | `service/` | `IQmsBkmService` |
| `ServiceImpl` | Service 实现 | `service/impl/` | `QmsBkmServiceImpl extends BaseServiceManager` |
| `Mapper` | MyBatis 接口 | `dao/` | `QmsBkmMapper` |
| `DTO` | Controller ↔ Service 入参 | `dto/` | `QmsBkmDTO` |
| `Request` / `Response` | 具体动作入参/出参 | `dto/` | `QmsLabEntrustOrderInsertRequest` |
| `VO` | 复杂查询返回 | `vo/`（少数） | `BaseVo` |
| Entity | 与表一对一，**无后缀** | `entity/` | `QmsBkm` |
| `Handler` | 弹窗/选择器处理器 | `handler/` | `DepartmentDialogHandler` |

### 后缀禁忌

| ❌ 禁止 | 正确 |
|--------|------|
| `QmsBkmService`（无 I 前缀） | 接口 `IQmsBkmService`，实现 `QmsBkmServiceImpl` |
| `QmsBkmEntity` | `QmsBkm`（无后缀） |
| `QmsBkmDTO2` / `QmsBkmDTOCopy` | 用动作后缀：`QmsBkmInsertRequest` |

## 方法命名

### 业务方法（Service）

| 动词 | 用法 |
|------|------|
| `get` | 按 id 单查 |
| `find*` | 列表查询 |
| `getBy*` | 按唯一键查（非 id） |
| `selectForPage` | 分页查询 |
| `count*` / `exists*` | 统计 / 存在性 |
| `insert` / `insertBatch` | 新增 / 批量新增 |
| `update` / `updateStatus` | 更新 / 状态机更新 |
| `delete` | 软删除 |
| `export` / `generate*` / `async*` | 导出 / 生成 / 异步 |

### Controller 方法

项目非 RESTful，主流 `/insert` / `/update` / `/delete` / `/get`：
```java
@PostMapping("/insert")
public Result<Long> insert(@RequestBody QmsBkmDTO dto) { ... }
```

## 数据库字段命名

见 [docs/database/conventions.md](../database/conventions.md)：匈牙利前缀 `N_` / `C_` / `D_` / `FK_`。

## 常量命名

| 类型 | 风格 | 示例 |
|------|------|------|
| 静态 final 常量 | UPPER_SNAKE | `public static final String STATUS_OPEN = "OPEN";` |
| 枚举值 | UPPER_SNAKE | `CalibrationStatusEnum.AGREE` |
| 状态码（业务） | 数字字符串存 DB | `cState = "1"` |

## 业务术语 → 代码命名映射（实测）

| 业务术语 | 代码命名 | 含义 |
|---------|---------|------|
| 检验单号 | `cJydh` / `C_JYDH` | Jianyan Dan Hao |
| 物料编码 | `cWlbm` / `C_WLBM` | Wuliao Bianma |
| 供应商编码 | `cGysbm` / `C_GYSBM` | Gongyingshang Bianma |
| 批次号 | `cPch` / `C_PCH` | Pi Ci Hao |
| 工厂 | `cFactory` / `C_FACTORY` | 工厂隔离字段（多租户） |
| 状态 | `cZt` / `cState` | Zhuangtai |
| BKM | `qmsProbfbctrlAbn` | 不合格品闭环（代码用 Probfb 不用 Bkm） |
| VDA 6.3 | `qmsVdaBasic` | 过程审核 |

> 业务命名用**拼音首字母缩写**（`cWlbm` = 物料编码），新模块若英文化会破坏一致性，沿用既有缩写。
