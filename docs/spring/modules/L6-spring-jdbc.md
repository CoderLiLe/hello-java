# spring-jdbc 模块功能文档

---

## 一、模块定位

spring-jdbc 是 Spring 的 **JDBC 数据访问模块**，253 个 Java 文件，负责：

- **JdbcTemplate**：JDBC 操作模板（Template Method + Callback 模式），封装 Connection 获取/释放、异常翻译
- **NamedParameterJdbcTemplate**：命名参数支持（`:param` → `?`）
- **JdbcClient**：流式 JDBC 门面（6.1+），统一位置参数和命名参数
- **RowMapper / ResultSetExtractor**：结果集映射回调接口
- **SQL 异常翻译**：SQLException → DataAccessException 链（SQLErrorCode → SQLState 责任链）
- **DataSource 层次**：DriverManagerDataSource、SingleConnectionDataSource、AbstractRoutingDataSource 等
- **DataSource 事务管理**：DataSourceTransactionManager (spring-tx 集成)
- **批量操作**：BatchPreparedStatementSetter + 子批次支持
- **存储过程调用**：CallableStatementCreator + SqlParameter 层次
- **嵌入式数据库**：EmbeddedDatabaseBuilder（H2 / HSQL / Derby）
- **数据库脚本执行**：ResourceDatabasePopulator（SQL 脚本初始化）
- **LOB 处理**：LobHandler / LobCreator（已废弃 6.2，JDBC 4.0 直接支持）
- **KeyHolder**：自增键/生成键持有
- **R2DBC 桥接**：JdbcTransactionManager（统一命令式/响应式事务管理器）

**依赖**：`spring-beans`、`spring-core`、`spring-tx`

---

## 二、模块全景图

```
spring-jdbc (253 files)
│
├── org.springframework.jdbc.core/                   # JDBC 核心 (44 files)
│   ├── JdbcTemplate                                  — ★ JDBC 操作模板 (1825 行)
│   ├── JdbcOperations                                — JDBC 操作接口 (所有 query/update 方法声明)
│   ├── RowMapper<T>                                  — 行映射器接口 (ResultSet → Object)
│   ├── ResultSetExtractor<T>                         — 结果集提取器接口 (整个 ResultSet → Object)
│   ├── RowCallbackHandler                            — 行回调处理器 (逐行处理)
│   ├── PreparedStatementCreator                      — PreparedStatement 创建回调
│   ├── PreparedStatementSetter                       — PreparedStatement 参数设置回调
│   ├── PreparedStatementCallback<T>                  — PreparedStatement 执行回调
│   ├── StatementCallback<T>                          — Statement 执行回调
│   ├── ConnectionCallback<T>                         — Connection 执行回调
│   ├── CallableStatementCallback<T>                  — 存储过程回调
│   ├── CallableStatementCreator                      — 存储过程创建回调
│   ├── BeanPropertyRowMapper<T>                      — Bean 属性行映射器
│   ├── DataClassRowMapper<T>                         — Record / Data Class 行映射器
│   ├── ColumnMapRowMapper                            — Map 行映射器 (列名 → 值)
│   ├── SingleColumnRowMapper<T>                      — 单列行映射器
│   ├── ParameterizedPreparedStatementSetter<T>       — 参数化批量设置器
│   ├── BatchPreparedStatementSetter                  — 批量 PreparedStatement 设置器
│   ├── SqlParameter / SqlParameterValue              — 存储过程参数
│   ├── SqlOutParameter / SqlInOutParameter           — OUT / INOUT 参数
│   ├── SqlReturnResultSet / SqlReturnUpdateCount     — 存储过程返回
│   ├── sqlProvider                                   — SQL 提供者接口
│   ├── StatementCreatorUtils                         — Statement 创建工具
│   └── RowMapperResultSetExtractor<T>                — RowMapper → ResultSetExtractor 适配
│
├── org.springframework.jdbc.core.namedparam/         # 命名参数 (14 files)
│   ├── NamedParameterJdbcTemplate                    — ★ 命名参数 JDBC 模板 (506 行)
│   ├── NamedParameterJdbcOperations                  — 命名参数操作接口
│   ├── NamedParameterUtils                          — 命名参数解析 (:name → ?)
│   ├── SqlParameterSource                            — SQL 参数源接口
│   ├── MapSqlParameterSource                         — Map 参数源
│   ├── BeanPropertySqlParameterSource                — Bean 属性参数源
│   ├── EmptySqlParameterSource                       — 空参数源
│   ├── AbstractSqlParameterSource                     — 参数源抽象基类
│   └── ParsedSql                                      — 已解析的 SQL (含参数名列表)
│
├── org.springframework.jdbc.core.simple/             # 流式 API (3 files)
│   ├── JdbcClient                                    — ★ 流式 JDBC 门面 (6.1+, 466 行)
│   ├── SimpleJdbcCall                                — 存储过程流式调用
│   └── SimpleJdbcInsert                              — 插入操作流式门面
│
├── org.springframework.jdbc.core.metadata/            # 数据库元数据 (13 files)
│   ├── TableMetaDataProvider                         — 表元数据提供者
│   ├── GenericTableMetaDataProvider                  — 通用表元数据
│   └── OracleTableMetaDataProvider / ...              — 各数据库特定实现
│
├── org.springframework.jdbc.core.support/             # 核心支持 (8 files)
│   ├── JdbcDaoSupport                                — JDBC DAO 支持基类
│   ├── SqlLobValue                                   — SQL LOB 值
│   └── SqlBinaryValue / SqlCharacterValue            — LOB 值封装
│
├── org.springframework.jdbc.datasource/               # DataSource 支持 (21 files)
│   ├── DataSourceTransactionManager                  — ★ 数据源事务管理器 (523 行)
│   ├── AbstractDataSource                            — DataSource 抽象基类
│   ├── AbstractDriverBasedDataSource                 — 基于驱动的 DataSource 抽象
│   ├── DriverManagerDataSource                       — 简单 DriverManager 封装
│   ├── SimpleDriverDataSource                        — JDBC 4.0 简单 DataSource
│   ├── SingleConnectionDataSource                    — 单连接 DataSource (测试用)
│   ├── TransactionAwareDataSourceProxy               — 事务感知 DataSource 代理
│   ├── LazyConnectionDataSourceProxy                 — 延迟获取连接的 DataSource 代理
│   ├── IsolationLevelDataSourceAdapter               — 隔离级别适配
│   ├── ShardingKeyDataSourceAdapter                  — 分片键适配
│   ├── DelegatingDataSource                           — 委托模式 DataSource
│   ├── SmartDataSource                                — 智能 DataSource 接口
│   ├── ConnectionHolder                               — Connection 资源持有者
│   ├── ConnectionHandle / ConnectionProxy            — Connection 代理
│   └── DataSourceUtils                                — DataSource 工具类 (getConnection / releaseConnection)
│
├── org.springframework.jdbc.datasource.embedded/      # 嵌入式数据库 (6 files)
│   ├── EmbeddedDatabaseBuilder                        — 嵌入式数据库构建器
│   ├── EmbeddedDatabaseFactory                        — 嵌入式数据库工厂
│   ├── EmbeddedDatabase                               — 嵌入式数据库接口
│   └── H2EmbeddedDatabaseConfigurer / ...              — 各厂商配置器
│
├── org.springframework.jdbc.datasource.init/          # 数据库初始化 (10 files)
│   ├── ResourceDatabasePopulator                      — 资源数据库填充器 (SQL 脚本执行)
│   ├── DataSourceInitializer                          — DataSource 初始化器
│   ├── DatabasePopulator                              — 数据库填充器接口
│   └── ScriptUtils                                     — 脚本工具 (分号分隔 SQL)
│
├── org.springframework.jdbc.datasource.lookup/        # DataSource 路由 (8 files)
│   ├── AbstractRoutingDataSource                      — ★ 抽象路由 DataSource (读写分离)
│   ├── MapDataSourceLookup                            — Map 查找
│   └── JndiDataSourceLookup                           — JNDI 查找
│
├── org.springframework.jdbc.support/                  # JDBC 支持 (22 files)
│   ├── SQLExceptionTranslator                        — ★ SQL 异常翻译接口
│   ├── AbstractFallbackSQLExceptionTranslator        — 回退异常翻译抽象
│   ├── SQLErrorCodeSQLExceptionTranslator            — ★ 基于错误码的翻译 (433 行)
│   ├── SQLStateSQLExceptionTranslator                 — 基于 SQLState 的翻译
│   ├── SQLExceptionSubclassTranslator                 — 基于子类的翻译 (JDBC 4.0+)
│   ├── SQLErrorCodes / SQLErrorCodesFactory          — SQL 错误码 (从 sql-error-codes.xml 加载)
│   ├── CustomSQLExceptionTranslatorRegistrar / Registry — 自定义翻译注册
│   ├── JdbcAccessor                                   — JDBC 访问器基类
│   ├── JdbcUtils                                     — JDBC 工具类
│   ├── KeyHolder / GeneratedKeyHolder                 — 自增键持有
│   ├── DatabaseMetaDataCallback                       — 数据库元数据回调
│   └── DatabaseStartupValidator                       — 数据库启动验证器
│
├── org.springframework.jdbc.support.rowset/            # SqlRowSet 支持 (5 files)
│   └── ResultSetWrappingSqlRowSet / CachedRowSetImpl
│
├── org.springframework.jdbc.support.incrementer/      # ID 自增器 (10 files)
│   └── DataFieldMaxValueIncrementer — MySQL / Oracle / PostgreSQL / HSQL / Derby
│
├── org.springframework.jdbc.support.lob/              # LOB 支持 (14 files)
│   ├── LobHandler / LobCreator                         — LOB 处理器接口 (已废弃 6.2)
│   └── DefaultLobHandler / TemporaryLobCreator
│
├── org.springframework.jdbc.support.xml/               # XML 支持 (5 files)
│   └── SqlXmlFeatureNotImplementedException
│
├── org.springframework.jdbc.config/                   # XML 配置 (4 files)
│   └── JdbcNamespaceHandler
│
└── org.springframework.jdbc.object/                   # RDBMS 对象建模 (12 files)
    ├── SqlQuery / SqlUpdate / SqlCall / SqlFunction    — 对象化 SQL 操作
    ├── MappingSqlQuery<T>                              — 泛型映射查询
    └── StoredProcedure                                — 存储过程对象
```

---

## 三、核心接口层次

```
JdbcOperations                            — JDBC 操作接口
  └── JdbcTemplate                        — 核心实现 (1825 行)
        ├── execute(ConnectionCallback)   — 最低级 API, 直接操作 Connection
        ├── execute(StatementCallback)    — Statement 级回调
        ├── query(sql, RowMapper, args)   — 查询 (返回 List<T>)
        ├── queryForObject(sql, RowMapper, args) — 单对象查询
        ├── queryForList(sql, args)       — 查询 (返回 List<Map>)
        ├── queryForMap(sql, args)        — 单 Map 查询
        ├── queryForStream(sql, RowMapper, args) — 流式查询 (6.1+)
        ├── update(sql, args)             — 更新 (INSERT/UPDATE/DELETE)
        ├── batchUpdate(sql, BatchPreparedStatementSetter) — 批量更新
        └── call(CallableStatementCreator, params) — 存储过程

NamedParameterJdbcOperations              — 命名参数操作接口
  └── NamedParameterJdbcTemplate          — 命名参数实现 (506 行)
        └── 委托给 JdbcTemplate (内部将 :name 转为 ?)

JdbcClient (6.1+)                         — 流式门面 (466 行)
  ├── sql("SELECT * FROM users WHERE id = ?")
  ├── param(42)                           — 位置参数
  ├── param("name", "Jack")               — 命名参数
  ├── query(User.class)                   — 自动映射
  └── update() / query()
```

---

## 四、核心流程

### 4.1 JdbcTemplate 查询流程（Template Method + Callback）

```
JdbcTemplate.query("SELECT name, age FROM users WHERE id = ?", rowMapper, 42)
  │
  ├── ① 获取 Connection: DataSourceUtils.getConnection(dataSource)
  │     │
  │     ├── 检查 TransactionSynchronizationManager 是否有事务绑定的 Connection
  │     │     ├── YES (Spring 事务管理中) → 返回事务 Connection (同一事务复用)
  │     │     └── NO  → dataSource.getConnection() (从连接池获取新连接)
  │     │
  │     └── 如果 Spring 事务同步活跃 → bindConnectionToTransaction(holder)
  │           └── TransactionSynchronizationManager.bindResource(dataSource, holder)
  │
  ├── ② 创建 PreparedStatement: PreparedStatementCreator
  │     └── con.prepareStatement(sql) + 设置参数 (42 → ?)
  │
  ├── ③ 应用 Statement 设置:
  │     ├── queryTimeout → stmt.setQueryTimeout()
  │     ├── maxRows → stmt.setMaxRows()
  │     └── fetchSize → stmt.setFetchSize()
  │
  ├── ④ 执行查询: pstmt.executeQuery() → ResultSet
  │
  ├── ⑤ 提取结果:
  │     RowMapperResultSetExtractor.extractData(rs)
  │       │
  │       ├── 逐行遍历 ResultSet:
  │       │   while (rs.next()) {
  │       │     T row = rowMapper.mapRow(rs, rowNum++);
  │       │     results.add(row);
  │       │   }
  │       │
  │       ├── RowMapper 实现:
  │       │   ├── BeanPropertyRowMapper: 通过 Bean 内省 → setter 注入
  │       │   ├── DataClassRowMapper: 通过 Record Constructor 注入
  │       │   ├── ColumnMapRowMapper: 列名 → Map
  │       │   └── SingleColumnRowMapper: 第 1 列 → 标量值
  │       │
  │       └── 返回 List<T>
  │
  ├── ⑥ 异常处理:
  │     catch (SQLException ex) {
  │       JdbcUtils.translateException(task, sql, ex)
  │         └── SQLExceptionTranslator 责任链翻译 (见 §4.5)
  │     }
  │
  └── ⑦ 清理资源 (finally):
        ├── JdbcUtils.closeResultSet(rs)
        ├── JdbcUtils.closeStatement(stmt)
        └── DataSourceUtils.releaseConnection(con, dataSource)
              ├── 事务绑定连接 → 不关闭 (等待事务提交/回滚)
              └── 独立连接 → close() (归还连接池)
```

### 4.2 NamedParameterJdbcTemplate 参数解析

```
NamedParameterJdbcTemplate.query("SELECT * FROM users WHERE name = :name AND age > :age", params, rowMapper)
  │
  ├── ① 解析 SQL:
  │     NamedParameterUtils.parseSqlStatement(sql)
  │       │
  │       ├── 词法分析: 扫描 SQL 字符串
  │       ├── 识别命名参数: :name, :age
  │       ├── 替换为位置占位符: SELECT * FROM users WHERE name = ? AND age > ?
  │       └── 返回 ParsedSql(parsedSql="... ? ... ?", paramNames=["name", "age"])
  │       │
  │       └── ★ 缓存: ConcurrentHashMap<String, ParsedSql> (LRU 风格)
  │
  ├── ② 构建参数数组:
  │     └── 根据 paramNames 顺序从 SqlParameterSource 中取值
  │           ├── MapSqlParameterSource → map.get(name)
  │           └── BeanPropertySqlParameterSource → bean.getProperty(name)
  │
  └── ③ 委托 JdbcTemplate: jdbcTemplate.query(parsedSql, args, rowMapper)
```

### 4.3 DataSourceTransactionManager 事务流程

```
DataSourceTransactionManager (extends AbstractPlatformTransactionManager)
  │
  ├── doGetTransaction():
  │     └── 从 TransactionSynchronizationManager 获取 ConnectionHolder
  │           ├── 存在 → 事务 Connection
  │           └── 不存在 → 新建 ConnectionHolder
  │
  ├── isExistingTransaction(transaction):
  │     └── transaction.hasConnectionHolder() && holder.isTransactionActive()
  │
  ├── doBegin(transaction, definition):
  │     ├── 获取 Connection: DataSourceUtils.getConnection(dataSource)
  │     ├── 设置 autoCommit = false
  │     ├── 设置隔离级别: con.setTransactionIsolation(isolationLevel)
  │     ├── 设置只读: con.setReadOnly(readOnly)
  │     ├── 绑定到同步: TransactionSynchronizationManager.bindResource(dataSource, holder)
  │     └── 设置事务活跃: holder.setTransactionActive(true)
  │
  ├── doCommit(status):
  │     └── connection.commit()
  │
  ├── doRollback(status):
  │     └── connection.rollback()
  │
  ├── doSuspend(transaction):
  │     └── TransactionSynchronizationManager.unbindResource(dataSource)
  │         └── 保存并移除 ConnectionHolder
  │
  ├── doResume(transaction, suspendedResources):
  │     └── TransactionSynchronizationManager.bindResource(dataSource, suspendedResources)
  │
  └── doCleanupAfterCompletion(transaction):
        ├── TransactionSynchronizationManager.unbindResource(dataSource)
        ├── connection.setAutoCommit(true)
        └── DataSourceUtils.releaseConnection(connection, dataSource)
```

### 4.4 批量操作流程

```
JdbcTemplate.batchUpdate("INSERT INTO users (name, age) VALUES (?, ?)", batchSetter)
  │
  ├── ① 获取 Connection (同上)
  ├── ② 创建 PreparedStatement: con.prepareStatement(sql)
  │
  ├── ③ 循环批次:
  │     for (int i = 0; i < batchSize; i++) {
  │       batchSetter.setValues(pstmt, i);  ← 设置第 i 批参数
  │       pstmt.addBatch();
  │     }
  │
  ├── ④ 执行:
  │     pstmt.executeBatch() → int[] (每行影响行数)
  │
  ├── ⑤ 批量异常处理:
  │     BatchUpdateException ex → AggregatedBatchUpdateException (含失败索引)
  │       └── 子批次回退: 找到失败批次位置，执行同批次内逐个重试
  │
  └── ⑥ 清理资源 (同上)
```

### 4.5 SQL 异常翻译责任链

```
SQLExceptionTranslator 翻译链 (AbstractFallbackSQLExceptionTranslator):
  │
  ├── ① SQLExceptionSubclassTranslator (第一优先级):
  │     └── 检查异常是否为 JDBC 4.0+ 标准子类
  │           ├── SQLTransientException → TransientDataAccessException
  │           ├── SQLNonTransientException → NonTransientDataAccessException
  │           ├── SQLIntegrityConstraintViolationException → DataIntegrityViolationException
  │           └── ...
  │
  ├── ② SQLErrorCodeSQLExceptionTranslator (第二优先级):
  │     │
  │     ├── 获取 SQLErrorCodes: SQLErrorCodesFactory.resolve(dataSource)
  │     │     └── 从 sql-error-codes.xml 加载 (根据 DatabaseMetaData.getDatabaseProductName())
  │     │
  │     ├── 查找 errorCode 匹配:
  │     │   ├── badSqlGrammarCodes → BadSqlGrammarException
  │     │   ├── dataIntegrityViolationCodes → DataIntegrityViolationException
  │     │   ├── cannotAcquireLockCodes → CannotAcquireLockException
  │     │   ├── deadlockLoserCodes → DeadlockLoserDataAccessException
  │     │   └── ...
  │     │
  │     └── 自定义翻译: CustomSQLExceptionTranslatorRegistry (用户注册)
  │
  └── ③ SQLStateSQLExceptionTranslator (第三优先级, 兜底):
        └── 根据 SQLException.getSQLState() 分类:
              ├── 23xxx → DataIntegrityViolationException
              ├── 40xxx → TransientDataAccessException
              └── 42xxx → BadSqlGrammarException
```

---

## 五、JdbcClient 流式 API（6.1+）

```
JdbcClient client = JdbcClient.create(dataSource);

// 查询
List<User> users = client.sql("SELECT * FROM users WHERE age > ?")
    .param(18)
    .query(User.class)
    .list();

Optional<User> user = client.sql("SELECT * FROM users WHERE id = :id")
    .param("id", 42)
    .query(User.class)
    .optional();

// 更新
int rows = client.sql("UPDATE users SET name = :name WHERE id = :id")
    .param("name", "Jack")
    .param("id", 42)
    .update();

// 流式查询
Stream<User> stream = client.sql("SELECT * FROM users")
    .query(User.class)
    .stream();

JdbcClient 内部本质上是 JdbcTemplate + NamedParameterJdbcTemplate 的流式门面，
提供统一的 param() / query() / update() API，支持位置参数和命名参数混用。
```

---

## 六、DataSource 层次速查

| 类 | 说明 |
|----|------|
| `DriverManagerDataSource` | 简单 DataSource（每次获取新连接，无连接池） |
| `SimpleDriverDataSource` | JDBC 4.0+ 简单实现 |
| `SingleConnectionDataSource` | 单连接 DataSource（测试用，每次返回同一连接） |
| `HikariDataSource` | HikariCP 连接池（外部） |
| `TransactionAwareDataSourceProxy` | 事务感知代理（复用事务 Connection） |
| `LazyConnectionDataSourceProxy` | 延迟获取 Connection（避免非事务操作持有连接） |
| `AbstractRoutingDataSource` | 抽象路由（读写分离：根据 lookupKey 路由到不同 DataSource） |
| `IsolationLevelDataSourceAdapter` | 隔离级别适配（强制设置默认隔离级别） |
| `ShardingKeyDataSourceAdapter` | 分片键适配 |
| `DelegatingDataSource` | 委托模式基类 |

---

## 七、关键类速查

| 类/接口 | 包 | 说明 |
|---------|-----|------|
| `JdbcTemplate` | `core` | JDBC 操作模板 (1825 行) |
| `NamedParameterJdbcTemplate` | `core.namedparam` | 命名参数模板 (506 行) |
| `JdbcClient` | `core.simple` | 流式 JDBC 门面 (6.1+, 466 行) |
| `RowMapper<T>` | `core` | 行映射器接口 |
| `ResultSetExtractor<T>` | `core` | 结果集提取器接口 |
| `PreparedStatementCreator` | `core` | PreparedStatement 创建回调 |
| `BeanPropertyRowMapper<T>` | `core` | Bean 属性行映射器 |
| `DataSourceTransactionManager` | `datasource` | 数据源事务管理器 (523 行) |
| `AbstractRoutingDataSource` | `datasource.lookup` | 抽象路由 DataSource |
| `SQLErrorCodeSQLExceptionTranslator` | `support` | SQL 错误码翻译 (433 行) |
| `SQLExceptionTranslator` | `support` | SQL 异常翻译接口 |
| `KeyHolder` | `support` | 自增键持有者 |
| `JdbcUtils` | `support` | JDBC 工具类 |
| `EmbeddedDatabaseBuilder` | `datasource.embedded` | 嵌入式数据库构建器 |
| `ResourceDatabasePopulator` | `datasource.init` | SQL 脚本执行器 |
| `SimpleJdbcInsert` | `core.simple` | 流式插入操作 |
| `SimpleJdbcCall` | `core.simple` | 流式存储过程调用 |

---

## 八、RowMapper vs ResultSetExtractor vs RowCallbackHandler

| 接口 | 职责 | 返回 | 使用场景 |
|------|------|------|---------|
| `RowMapper<T>` | 映射单行 → 对象 | 由 JdbcTemplate 收集为 List | 行级映射，自动遍历 |
| `ResultSetExtractor<T>` | 处理整个 ResultSet | 直接返回 | 需要自定义迭代逻辑 |
| `RowCallbackHandler` | 逐行处理（副作用） | void | 写入文件、流式输出 |

---

## 九、依赖关系

```
spring-jdbc
  ├── api: spring-beans
  ├── api: spring-core
  ├── api: spring-tx
  ├── optional: com.h2database:h2              (嵌入式数据库)
  ├── optional: org.apache.derby:derby         (嵌入式数据库)
  ├── optional: org.hsqldb:hsqldb              (嵌入式数据库)
  ├── optional: org.jetbrains.kotlin:kotlin-stdlib
  └── optional: org.jetbrains.kotlin:kotlin-reflect

---

## 十、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-tx](L5-spring-tx.md) | L5 事务 | DataSourceTransactionManager |
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | BeanFactory |
| 下游 | [spring-orm](L6-spring-orm.md) | L6 数据 | JPA/Hibernate 集成 |
```
