# spring-r2dbc 模块功能文档

---

## 一、模块定位

spring-r2dbc 是 Spring 的 **响应式关系型数据库访问模块**，53 个 Java 文件（~8300 行），负责：

- **DatabaseClient**：响应式数据库客户端，提供流式 SQL 操作
- **连接管理**：Spring 托管的 ConnectionFactory 包装体系
- **响应式事务**：R2dbcTransactionManager 与 ReactiveTransactionManager 集成
- **命名参数解析**：`:name` 风格命名参数 → 数据库方言占位符转换
- **行映射**：响应式 Row 到 Java 对象的映射
- **数据库初始化**：响应式连接工厂的脚本初始化支持

**依赖**：`spring-core`、`spring-tx`、`io.r2dbc:r2dbc-spi`

---

## 二、模块全景图

```
spring-r2dbc (53 files)
│
├── org.springframework.r2dbc/                         # 异常 (2 files)
│   ├── BadSqlGrammarException                          — SQL 语法错误异常
│   └── UncategorizedR2dbcException                     — 未分类 R2DBC 异常
│
├── org.springframework.r2dbc.connection/               # 连接核心 (5 files)
│   ├── ConnectionFactoryUtils                          — ★ 连接生命周期管理 + 异常转换
│   ├── ConnectionHolder                                — 事务资源持有者 (Savepoint 支持)
│   ├── DelegatingConnectionFactory                    — 委托连接工厂基类
│   ├── R2dbcTransactionManager                        — ★ 响应式事务管理器
│   ├── SingleConnectionFactory                        — 单连接工厂 (测试用)
│   └── TransactionAwareConnectionFactoryProxy         — 事务感知连接工厂代理
│
├── org.springframework.r2dbc.connection.init/          # 数据库初始化 (9 files)
│   ├── ConnectionFactoryInitializer                    — 连接工厂初始化器
│   ├── ResourceDatabasePopulator                       — 资源脚本数据库填充器
│   ├── ScriptUtils                                     — SQL 脚本解析工具
│   └── CompositeDatabasePopulator                      — 组合数据库填充器
│
├── org.springframework.r2dbc.connection.lookup/        # 连接工厂查找 (6 files)
│   ├── AbstractRoutingConnectionFactory               — 抽象路由连接工厂
│   ├── BeanFactoryConnectionFactoryLookup             — Spring BeanFactory 查找
│   └── MapConnectionFactoryLookup                     — Map 查找
│
├── org.springframework.r2dbc.core/                    # 核心操作 (21 files)
│   ├── DatabaseClient                                  — ★ 响应式数据库客户端接口
│   ├── DefaultDatabaseClient                           — ★ DatabaseClient 实现 (609 行)
│   ├── DefaultFetchSpec                                — Fetch 规范实现
│   ├── NamedParameterUtils                             — 命名参数工具 (610 行)
│   ├── NamedParameterExpander                          — 命名参数展开器
│   ├── BeanPropertyRowMapper                           — Bean 属性行映射器
│   ├── DataClassRowMapper                              — Data Class 行映射器
│   ├── ColumnMapRowMapper                              — Map 行映射器
│   ├── FetchSpec / RowsFetchSpec / UpdatedRowsFetchSpec — 查询结果规范接口
│   └── StatementFilterFunction                         — Statement 过滤器链
│
└── org.springframework.r2dbc.core.binding/            # 参数绑定 (10 files)
    ├── BindMarkersFactory                              — 绑定标记工厂
    ├── BindMarkersFactoryResolver                      — 绑定标记工厂解析器
    ├── BindMarkers / BindMarker                        — 绑定标记抽象
    ├── NamedBindMarkers / IndexedBindMarkers          — 命名/索引绑定标记
    └── Bindings / MutableBindings                      — 绑定数据容器
```

---

## 三、核心流程

### 3.1 DatabaseClient 查询流程

```
client.sql("SELECT * FROM foo WHERE id = :id")
      .bind("id", 42)
      .fetch()
      .all()
  │
  ├── ① sql("...") → 创建 DefaultGenericExecuteSpec (含 SQL Supplier + 空绑定 Map)
  │
  ├── ② bind("id", 42) → 创建新不可变 Spec (byName Map: {id → Parameters.in(42)})
  │
  ├── ③ fetch() → execute(sqlSupplier, result → result.map(ColumnMapRowMapper.INSTANCE))
  │        └── 创建 ResultFunction (持有 SQL Supplier + Statement 创建 lambda + filter 链 + ExecuteFunction)
  │
  ├── ④ all() → connectionAccessor.inConnectionMany(connectionFunction)
  │        │
  │        └── DefaultDatabaseClient.inConnectionMany():
  │              ├── ConnectionFactoryUtils.getConnection() 获取连接
  │              │     └── 检查 TransactionSynchronizationManager 事务上下文
  │              ├── CloseSuppressingInvocationHandler 代理 (禁止回调关闭连接)
  │              ├── Flux.usingWhen() 保证资源清理
  │              └── resultFunction.apply(connection) → flatMap(resultAdapter)
  │
  ├── ⑤ ResultFunction.apply(connection):
  │        ├── 解析 SQL (NamedParameterExpander 展开命名参数)
  │        │     └── NamedParameterUtils.parseSqlStatement() → ParsedSql
  │        │     └── substituteNamedParameters() → :name 替换为 $1 / ? / :p0
  │        ├── 创建 Statement → bindTo() 绑定参数
  │        ├── StatementFilterFunction 链处理
  │        └── executeFunction.execute(statement) → Flux<Result>
  │
  └── ⑥ rowMapper 将 Row → Java 对象，发射给订阅者
```

### 3.2 命名参数展开流程

```
SELECT * FROM foo WHERE name = :name AND id IN (:ids)
  │
  ├── NamedParameterUtils.parseSqlStatement(sql):
  │     ├── 词法分析，跳过注释 (--, /* */)、引号字符串、双引号、Postgres :: 类型转换
  │     └── 返回 ParsedSql (参数位置列表)
  │
  ├── NamedParameterUtils.substituteNamedParameters(parsedSql, bindMarkersFactory, paramSource):
  │     ├── 每个 :name → 对应 BindMarker (如 $1, ?, :p0_name)
  │     ├── 同一参数名引用相同 BindMarker
  │     └── Collection 值展开: ids=[1,2,3] → WHERE id IN ($1, $2, $3)
  │
  └── 返回 PreparedOperation<String>: SQL + bindTo(BindTarget)
```

### 3.3 响应式事务流程

```
transactionalOperator.execute(status ->
    client.sql("INSERT INTO foo VALUES(:id)").bind("id", 1).fetch().rowsUpdated()
)
  │
  ├── R2dbcTransactionManager.doBegin():
  │     ├── ConnectionFactory.create() 获取新连接
  │     ├── connection.beginTransaction(transactionDefinition)
  │     ├── 如 enforceReadOnly 且只读 → SET TRANSACTION READ ONLY
  │     ├── 创建 ConnectionHolder → 绑定到 TransactionSynchronizationManager
  │     └── TransactionSynchronizationManager.forCurrentTransaction() 建立响应式上下文
  │
  ├── DefaultDatabaseClient.inConnection():
  │     └── ConnectionFactoryUtils.getConnection()
  │           └── 发现已绑定事务连接 → 复用同一连接
  │
  ├── R2dbcTransactionManager.doCommit() / doRollback():
  │     ├── connection.commitTransaction() / connection.rollbackTransaction()
  │     └── 嵌套事务: 使用 Savepoint (SAVEPOINT_1, SAVEPOINT_2...)
  │
  └── R2dbcTransactionManager.doCleanupAfterCompletion():
        ├── 解绑 ConnectionHolder
        ├── 恢复 auto-commit
        └── 释放连接到连接池
```

### 3.4 异常转换

```
ConnectionFactoryUtils.convertR2dbcException(task, sql, r2dbcEx):
  │
  ├── R2dbcTransientResourceException  → TransientDataAccessResourceException
  ├── R2dbcRollbackException (40001)   → CannotAcquireLockException
  ├── R2dbcRollbackException (其他)     → PessimisticLockingFailureException
  ├── R2dbcTimeoutException            → QueryTimeoutException
  ├── R2dbcNonTransientResourceException → DataAccessResourceFailureException
  ├── R2dbcDataIntegrityViolationException (23505 或重复键) → DuplicateKeyException
  ├── R2dbcDataIntegrityViolationException (其他) → DataIntegrityViolationException
  ├── R2dbcPermissionDeniedException   → PermissionDeniedDataAccessException
  ├── R2dbcBadGrammarException         → BadSqlGrammarException
  └── 其他 R2dbcException              → UncategorizedR2dbcException
```

重复键检测：SQL state `23505` 标准重复键，或 state `23000` + 已知厂商错误码（Oracle:1, SAP:301, MySQL:1062, MSSQL:2601/2627, Informix:-239/-268）

---

## 四、关键设计模式

| 模式 | 应用 |
|------|------|
| **不可变 Spec 模式** | DefaultGenericExecuteSpec 每次 bind/filter 返回新实例 |
| **延迟解析** | SQL Supplier 在订阅时才解析 |
| **三层连接管理** | raw ConnectionFactory.create() → 事务绑定 → usingWhen 资源清理 |
| **绑定标记抽象** | BindMarkersFactory 方言适配 ($1/?/:p0) 通过 SpringFactoriesLoader 自动检测 |
| **动态代理** | CloseSuppressingInvocationHandler 禁止手动关闭连接 |

---

## 五、依赖关系

```
spring-r2dbc
  ├── api: spring-core
  ├── api: spring-tx
  ├── api: io.r2dbc:r2dbc-spi
  ├── optional: io.micrometer:micrometer-observation  (观测)
  ├── optional: org.jetbrains.kotlin:kotlin-stdlib
  └── optional: org.jetbrains.kotlinx:kotlinx-coroutines-reactor

---

## 六、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-tx](L5-spring-tx.md) | L5 事务 | ReactiveTransactionManager |
| 上游 | [spring-core](L1-spring-core.md) | L1 核心 | 反射、ReactiveAdapterRegistry |
| 下游 | 响应式应用 | — | 非阻塞数据访问消费者 |
```
