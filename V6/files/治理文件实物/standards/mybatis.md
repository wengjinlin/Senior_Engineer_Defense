# MyBatis 规范 (mybatis.md)

> 项目用 **MyBatis 2.1.4（原生）+ XML Mapper**，**非 MyBatis-Plus，非 JPA**。

## 现状实测

| 维度 | 项目实际 | 数量 |
|------|---------|------|
| Mapper 接口 | 无 `@Mapper`，由 `MybatisConfigDs.@MapperScan` 统一扫描 | 279 |
| Mapper.xml | 与接口同包同名（`dao/XxxMapper.xml`） | 279 |
| SQL 方言 | Oracle（`ROWNUM` / `NVL` / `SEQ_*NEXTVAL` / `DUAL` / `TO_DATE`） | — |
| 参数占位符 | `#{param}` 主流；`${param}` 仅用于 sortField 白名单后 | — |
| 分页 | `com.sunny.pagehelper.Page` + `SunnyPageInterceptor`（非 PageHelper 默认） | — |
| Map 返回 | `MapKeyUpperWrapper` 强制 key 大写 | — |
| 批量 | `insertBatch` / `updateBatch`，Oracle 用 `begin...end;` 包装 | — |

## 🔴 强制

1. **Mapper 接口命名**：`XxxMapper`（不带 `I` 前缀），放 `dao/` 包
2. **XML 与接口同包**：`com.sunny.modules.<业务>.dao.XxxMapper.{java,xml}`
3. **参数**：单参数 `#{param}`；多参数必加 `@Param("name")`
4. **INSERT 主键回填**：用 `<selectKey keyColumn="id" resultType="java.math.BigDecimal" keyProperty="id" order="AFTER">SELECT SEQ_QMS_<TABLE>_ID.CURRVAL FROM DUAL</selectKey>`
5. **时间处理**：Oracle DATE 字段写入 `to_date(#{...},'yyyy-mm-dd hh24:mi:ss')`，读取 `to_char(d_createtime,'yyyy-mm-dd hh24:mi:ss')`
6. **批量**：禁止业务层循环单条 insert；用 `insertBatch` + `<foreach open="begin" close=";end;">`
7. **列字段抽取**：复用 `<sql id="result_column">` 不写 `SELECT *`

## 🟢 方法命名约定

| 前缀 | 含义 | 返回 |
|------|------|------|
| `get` | 按 id 单查 | `Entity` |
| `findByIds` | 批量按 id | `List<Entity>` |
| `findXxx` | 按条件查 | `List<Entity>` |
| `selectForPage` | 分页查 | `Page<Entity>` |
| `getByXxx` | 按唯一键查 | `Entity` |
| `getByCount` | 统计 | `int` / `Long` |
| `insertBatch` / `updateBatch` | 批量写 | `int` |
| `delete` | 软删（UPDATE c_sign） | `int` |
| `exportCustom` | 导出查询 | `List<Map>` |

## ⚫ 禁止

| ❌ 禁止 | 原因 |
|--------|------|
| `@Mapper` 注解 | 项目用 `@MapperScan` 统一扫描 |
| `SELECT *` | 必须显式列字段，用 `<sql id="result_column">` 抽取 |
| `${param}` 字符串拼接 | SQL 注入；仅 sortField 白名单后可用 |
| 跨模块 import 别模块 Mapper | Mapper 只服务本模块；跨模块走对方 Service |
| Mapper 返回 `Map<String,Object>` 混用 | key 大写易踩；用 `<resultMap>` |
| 业务层循环 `for { mapper.insert(x) }` | 必须用 `insertBatch` |
| 引入 MyBatis-Plus 依赖 | 父 POM 锁死原生 MyBatis 2.1.4 |
| 动态拼 ORDER BY `${sortField}` | 必须走白名单映射 |

## 排序字段白名单（强制）

用户可控 sortField 必须走 `<choose>` 映射，**禁止直接 `${sortField}`**，参考 `QmsInspectionTaskMapper.xml` 的 `<sql id="sortFieldMapping">`。

## 分页

```java
// 项目封装，不要用 com.github.pagehelper.PageHelper.startPage()
Page<T> page = new Page<>(pageNum, pageSize);
List<T> list = mapper.selectForPage(query);
page.setList(list);
```

由 `SunnyPageInterceptor` 拦截自动加 `ROWNUM`。
