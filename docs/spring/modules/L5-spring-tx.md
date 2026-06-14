# spring-tx 模块功能文档

---

## 一、模块定位

spring-tx 是 Spring 的**事务管理核心模块**，173 个 Java 文件，负责：

- **事务抽象**：PlatformTransactionManager 统一编程式/声明式事务 API
- **声明式事务**：`@Transactional` 注解 + AOP 拦截器（TransactionInterceptor）
- **编程式事务**：TransactionTemplate（回调模板）、TransactionalOperator（响应式）
- **事务传播行为**：7 种传播级别（REQUIRED / REQUIRES_NEW / NESTED / SUPPORTS / NOT_SUPPORTED / MANDATORY / NEVER）
- **隔离级别**：4 种 JDBC 隔离级别 + DEFAULT
- **响应式事务**：ReactiveTransactionManager + TransactionalOperator（Reactor Context 传播）
- **事务同步**：TransactionSynchronization（命令式用 ThreadLocal，响应式用 Reactor Context）
- **JTA 集成**：JtaTransactionManager
- **DAO 异常体系**：DataAccessException 层次（与具体技术无关的异常翻译）
- **事务事件**：`@TransactionalEventListener`（事务提交后异步处理）

**依赖**：`spring-beans`、`spring-core`

---

## 二、模块全景图

```
spring-tx (173 files)
│
├── org.springframework.transaction/                  # 核心接口 (17 files)
│   ├── TransactionManager                            — 事务管理器标记接口
│   ├── PlatformTransactionManager                    — ★ 命令式事务管理器接口
│   ├── ReactiveTransactionManager                    — ★ 响应式事务管理器接口
│   ├── TransactionDefinition                         — 事务定义 (传播/隔离/超时/只读)
│   ├── TransactionStatus                             — 事务状态 (extends SavepointManager)
│   ├── TransactionExecution                          — 事务执行状态基接口
│   ├── SavepointManager                              — 保存点管理接口
│   ├── TransactionExecutionListener                  — 事务执行监听器
│   ├── TransactionException                          — 事务异常基类
│   ├── UnexpectedRollbackException                   — 意外回滚异常
│   ├── IllegalTransactionStateException              — 非法事务状态异常
│   ├── NestedTransactionNotSupportedException        — 嵌套事务不支持异常
│   └── ConfigurableTransactionManager                — 可配置事务管理器
│
├── org.springframework.transaction.support/          # 核心实现 (29 files)
│   ├── AbstractPlatformTransactionManager            — ★ 命令式事务管理器抽象基类 (1363 行)
│   ├── DefaultTransactionDefinition                  — 默认事务定义实现
│   ├── DefaultTransactionStatus                      — 默认事务状态实现
│   ├── TransactionTemplate                           — ★ 编程式事务模板 (185 行)
│   ├── TransactionCallback                          — 事务回调接口
│   ├── TransactionSynchronizationManager             — ★ 事务同步管理器 (ThreadLocal)
│   ├── TransactionSynchronization                    — 事务同步回调接口 (beforeCommit/afterCommit 等)
│   ├── TransactionSynchronizationUtils               — 同步工具类
│   ├── ResourceHolderSupport                         — 资源持有者基类
│   ├── ResourceHolderSynchronization                 — 资源同步适配
│   ├── SimpleTransactionStatus                       — 简单事务状态
│   └── CallbackPreferringPlatformTransactionManager  — 回调优先的事务管理器
│
├── org.springframework.transaction/interceptor/       # 声明式事务拦截 (19 files)
│   ├── TransactionInterceptor                        — ★ @Transactional AOP 拦截器 (182 行)
│   ├── TransactionAspectSupport                      — ★ 事务切面支持基类 (1139 行)
│   ├── TransactionAttribute                          — 事务属性接口 (扩展 TransactionDefinition)
│   ├── TransactionAttributeSource                    — 事务属性源接口
│   ├── AnnotationTransactionAttributeSource          — 注解事务属性源 (解析 @Transactional)
│   ├── DefaultTransactionAttribute                   — 默认事务属性
│   ├── RuleBasedTransactionAttribute                 — 基于规则的事务属性 (回滚规则)
│   ├── RollbackRuleAttribute                         — 回滚规则 (异常类型匹配)
│   ├── NoRollbackRuleAttribute                       — 不回滚规则
│   ├── TransactionAttributeSourceAdvisor             — 事务 Advisor (Pointcut 匹配)
│   ├── MatchAlwaysTransactionAttributeSource         — 始终匹配的事务属性源
│   └── BeanFactoryTransactionAttributeSourceAdvisor  — BeanFactory 感知 Advisor
│
├── org.springframework.transaction/annotation/        # 事务注解 (6 files)
│   ├── Transactional                                 — @Transactional 注解
│   ├── EnableTransactionManagement                   — @EnableTransactionManagement
│   ├── TransactionManagementConfigurationSelector    — 配置导入选择器
│   ├── ProxyTransactionManagementConfiguration       — 代理模式配置
│   ├── JtaTransactionManagementConfiguration         — JTA 代理配置
│   └── Isolation / Propagation                        — 枚举定义
│
├── org.springframework.transaction/reactive/          # 响应式事务 (14 files)
│   ├── ReactiveTransactionManager                    — 响应式事务管理器接口
│   ├── AbstractReactiveTransactionManager            — ★ 响应式事务管理器抽象基类
│   ├── TransactionalOperator                         — ★ 响应式事务操作符 (编程式)
│   ├── TransactionalOperatorImpl                     — 操作符实现
│   ├── GenericReactiveTransaction                    — 通用响应式事务状态
│   ├── TransactionContext                            — 事务上下文
│   ├── TransactionContextManager                     — 事务上下文管理器 (Reactor Context)
│   ├── TransactionContextHolder                      — 事务上下文持有者
│   ├── TransactionSynchronization                    — 响应式事务同步
│   ├── TransactionSynchronizationManager             — 响应式同步管理器
│   ├── ReactiveResourceSynchronization               — 响应式资源同步
│   └── TransactionalEventPublisher                   — 事务事件发布器
│
├── org.springframework.transaction/event/             # 事务事件 (8 files)
│   ├── TransactionalEventListener                    — @TransactionalEventListener
│   ├── TransactionalApplicationListener              — 事务感知监听器
│   ├── TransactionalApplicationListenerAdapter       — 监听器适配器
│   ├── ApplicationTransactionEventPublisher           — 事务事件发布
│   └── TransactionPhase                              — 事务阶段 (BEFORE_COMMIT / AFTER_COMMIT / AFTER_ROLLBACK / AFTER_COMPLETION)
│
├── org.springframework.transaction/jta/               # JTA 集成 (5 files)
│   ├── JtaTransactionManager                         — JTA 事务管理器
│   └── JtaTransactionObject                          — JTA 事务对象
│
├── org.springframework.transaction/config/            # XML 配置 (5 files)
│   └── TxNamespaceHandler / TxAdviceBeanDefinitionParser
│
├── org.springframework.dao/                           # DAO 异常体系 (6 files)
│   ├── DataAccessException                           — DAO 异常基类
│   ├── NonTransientDataAccessException               — 非瞬时异常
│   ├── TransientDataAccessException                  — 瞬时异常 (可重试)
│   ├── RecoverableDataAccessException                — 可恢复异常
│   ├── DataIntegrityViolationException               — 数据完整性异常
│   └── DataAccessResourceFailureException            — 资源访问异常
│
├── org.springframework.dao/annotation/                # DAO 注解 (2 files)
│   └── PersistenceExceptionTranslationAdvisor        — 持久化异常翻译 Advisor
│
├── org.springframework.dao/support/                   # DAO 支持 (5 files)
│   ├── PersistenceExceptionTranslator                — 持久化异常翻译接口
│   ├── DataAccessUtils                              — DAO 工具类
│   └── DaoSupport                                    — DAO 支持基类
│
└── org.springframework.jca/                           # JCA 资源适配 (8 files)
    └── endpoint/ support/                             — JCA 端点管理
```

---

## 三、核心类关系

```
TransactionManager (标记接口)
  ├── PlatformTransactionManager          — 命令式事务
  │     └── AbstractPlatformTransactionManager  — ★ 抽象基类 (Template Method)
  │           ├── DataSourceTransactionManager     (spring-jdbc 中)
  │           ├── JpaTransactionManager            (spring-orm 中)
  │           ├── HibernateTransactionManager      (spring-orm 中)
  │           ├── JtaTransactionManager
  │           └── JmsTransactionManager            (spring-jms 中)
  │
  └── ReactiveTransactionManager          — 响应式事务
        └── AbstractReactiveTransactionManager
              ├── R2dbcTransactionManager          (spring-r2dbc 中)
              └── ...

TransactionDefinition                    — 事务属性定义
  ├── DefaultTransactionDefinition       — 默认实现
  └── TransactionAttribute               — 扩展接口 (含回滚规则)
        └── DefaultTransactionAttribute
              └── RuleBasedTransactionAttribute

TransactionStatus (extends TransactionExecution, SavepointManager)
  └── DefaultTransactionStatus
        └── SimpleTransactionStatus
```

---

## 四、核心流程

### 4.1 事务传播行为完整流程

```
AbstractPlatformTransactionManager.getTransaction(definition)
  │
  ├── doGetTransaction()  ← 子类实现: 获取当前事务对象
  │     └── DataSourceTransactionManager: 从 DataSource 获取 Connection → ConnectionHolder
  │
  ├── isExistingTransaction(transaction)?
  │     ├── NO (无现存事务):
  │     │   │
  │     │   ├── PROPAGATION_MANDATORY → 抛异常 (必须有事务)
  │     │   │
  │     │   ├── PROPAGATION_REQUIRED / REQUIRES_NEW / NESTED:
  │     │   │   ├── suspend(null)  → 挂起空事务 (清理 ThreadLocal)
  │     │   │   └── startTransaction(def, transaction, ...):
  │     │   │         ├── doBegin(transaction, definition)  ← 子类: 开启 JDBC Connection / JPA EntityManager
  │     │   │         └── prepareSynchronization()  → 注册 TransactionSynchronization
  │     │   │
  │     │   └── PROPAGATION_SUPPORTS / NOT_SUPPORTED / NEVER:
  │     │         └── prepareTransactionStatus(def, null, ...)  → "空" 事务 (无实际资源事务)
  │     │
  │     └── YES (有现存事务):
  │           │
  │           ├── PROPAGATION_NEVER → 抛异常 (不能有事务)
  │           │
  │           ├── PROPAGATION_NOT_SUPPORTED:
  │           │   ├── suspend(transaction)  → 挂起当前事务
  │           │   └── 返回空事务状态
  │           │
  │           ├── PROPAGATION_REQUIRES_NEW:
  │           │   ├── suspend(transaction)  → 挂起当前事务
  │           │   └── startTransaction(def, transaction, ...)
  │           │         └── doBegin() → 开启新的物理事务
  │           │
  │           ├── PROPAGATION_NESTED:
  │           │   ├── useSavepointForNestedTransaction()?
  │           │   │   ├── YES (JDBC) → createAndHoldSavepoint()
  │           │   │   └── NO  (JTA) → startTransaction() with nested=true
  │           │   └── 返回嵌套事务状态
  │           │
  │           └── PROPAGATION_REQUIRED / SUPPORTS / MANDATORY:
  │                 └── 参与现有事务 (不创建新事务)
  │                       └── prepareTransactionStatus(def, transaction, ...)
  ```

### 4.2 commit / rollback 流程

```
AbstractPlatformTransactionManager.commit(status)
  │
  ├── status.isCompleted()? → 已提交/回滚 → 抛异常
  │
  ├── status.isLocalRollbackOnly()?
  │     ├── YES → 直接 rollback (见下方)
  │     └── NO:
  │           ├── status.isGlobalRollbackOnly()?
  │           │     ├── YES → 标记回滚 + rollback
  │           │     └── NO:
  │           │           ├── triggerBeforeCommit(status)  ← 触发同步回调 beforeCommit(false)
  │           │           ├── triggerBeforeCompletion()     ← 触发 beforeCompletion()
  │           │           │
  │           │           ├── status.isNewTransaction()?    ← 是否是此管理器创建的新事务
  │           │           │     ├── YES → doCommit(status)  ← 子类实现: Connection.commit()
  │           │           │     └── NO  → 不提交 (等待外部事务)
  │           │           │
  │           │           ├── 成功后: triggerAfterCommit()   ← 触发 afterCommit()
  │           │           └── 成功后: triggerAfterCompletion()
  │           │
  │           └── 失败时: doRollbackOnCommitFailure()? → 可能回滚
  │
  └── finally: cleanupAfterCompletion(status)
        ├── doCleanupAfterCompletion(status)  ← 子类清理 (关闭 Connection 等)
        └── resume(previousTransaction)       ← 恢复之前挂起的事务

AbstractPlatformTransactionManager.rollback(status)
  │
  ├── triggerBeforeCompletion()
  ├── status.isNewTransaction()?
  │     ├── YES → doRollback(status)  ← 子类实现: Connection.rollback()
  │     └── NO:
  │           ├── status.hasTransaction()? → doSetRollbackOnly(status)  ← 标记外层事务为 rollback-only
  │           └── 否则 → 什么都不做
  ├── status.isNewTransaction()? → triggerAfterCompletion(STATUS_ROLLED_BACK)
  └── cleanupAfterCompletion(status)
```

### 4.3 TransactionInterceptor（@Transactional AOP 拦截）

```
TransactionInterceptor.invoke(MethodInvocation invocation)
  │
  └── TransactionAspectSupport.invokeWithinTransaction(method, targetClass, invocation)
        │
        ├── ① 获取事务属性: getTransactionAttributeSource().getTransactionAttribute(method, targetClass)
        │     └── AnnotationTransactionAttributeSource:
        │           ├── 解析方法上的 @Transactional
        │           ├── 解析类上的 @Transactional (方法覆盖类)
        │           ├── 解析接口上的 @Transactional
        │           └── 解析 @Transactional.rollbackFor / noRollbackFor → RollbackRuleAttribute
        │
        ├── ② 获取事务管理器: determineTransactionManager(txAttr)
        │     ├── @Transactional("tmName") → 按名查找 Bean
        │     ├── @Transactional.value     → 同上 (别名)
        │     └── 默认 → 按类型查找 TransactionManager Bean
        │
        ├── ③ 创建事务:
        │     ├── 命令式 → tm.getTransaction(txAttr) → TransactionStatus
        │     └── 响应式 → ReactiveTransactionManager.getReactiveTransaction(txAttr)
        │
        ├── ④ 执行目标方法: invocation.proceed()
        │     ├── 成功 → ⑤ commitTransactionAfterReturning(status)
        │     │           └── tm.commit(status)
        │     └── 抛出异常:
        │           ├── 检查 rollbackFor / noRollbackFor 规则:
        │           │   ├── 匹配 rollbackFor → rollback
        │           │   ├── 匹配 noRollbackFor → commit
        │           │   └── 默认: RuntimeException/Error → rollback, checked → commit
        │           └── completeTransactionAfterThrowing(status, ex)
        │                 └── tm.rollback(status) 或 tm.commit(status)
        │
        └── ⑥ 清理事务上下文 (TransactionAspectSupport.cleanupTransactionInfo)
```

### 4.4 TransactionTemplate（编程式事务）

```
TransactionTemplate.execute(TransactionCallback<T> action)
  │
  ├── tm.getTransaction(this)   ← this 就是 TransactionDefinition (TransactionTemplate 继承 DefaultTransactionDefinition)
  │     └── AbstractPlatformTransactionManager.getTransaction()
  │           └── 根据 propagation 行为创建 / 参与事务
  │
  ├── 执行回调: action.doInTransaction(status)
  │     ├── 成功 → tm.commit(status)
  │     └── 异常 (RuntimeException/Error) → tm.rollback(status)
  │           └── 检查 rollbackOn() 默认对 checked exception 不自动回滚
  │
  └── 返回结果
```

### 4.5 事务同步机制（命令式 ThreadLocal）

```
TransactionSynchronizationManager
  │  (所有字段均为 static final ThreadLocal)
  │
  ├── resources: ThreadLocal<Map<Object, Object>>           — 资源持有者 (ConnectionHolder, SessionHolder)
  ├── synchronizations: ThreadLocal<Set<TransactionSynchronization>> — 同步回调集合
  ├── currentTransactionName: ThreadLocal<String>            — 当前事务名
  ├── currentTransactionReadOnly: ThreadLocal<Boolean>       — 只读标记
  ├── currentTransactionIsolationLevel: ThreadLocal<Integer> — 隔离级别
  └── actualTransactionActive: ThreadLocal<Boolean>          — 实际事务活跃标记

TransactionSynchronization 接口:
  ├── suspend()          — 挂起同步 (如解绑 Session)
  ├── resume()           — 恢复同步
  ├── flush()            — 刷新会话
  ├── beforeCommit(readOnly)  — 提交前回调
  ├── beforeCompletion()      — 完成前回调 (无论提交/回滚)
  ├── afterCommit()           — 提交后回调
  ├── afterCompletion(status) — 完成后回调 (无论成功/失败)
  └── afterRollback() (default) — 回滚后 (6.1+)
```

### 4.6 响应式事务（Reactor Context 传播）

```
命令式 vs 响应式事务对比:

  命令式 (PlatformTransactionManager)        响应式 (ReactiveTransactionManager)
  ─────────────────────────────────────      ─────────────────────────────────────
  传播: ThreadLocal                          传播: Reactor Context (ContextView)
  资源: TransactionSynchronizationManager   资源: TransactionSynchronizationManager (响应式版)
  获取: tm.getTransaction(def)              获取: tm.getReactiveTransaction(def) → Mono<ReactiveTransaction>
  提交: tm.commit(status)                   提交: tm.commit(tx) → Mono<Void>
  回滚: tm.rollback(status)                 回滚: tm.rollback(tx) → Mono<Void>

TransactionalOperator (响应式编程式事务):
  TransactionalOperator.transactional(flux)
    │
    └── TransactionalOperatorImpl.transactional(flux)
          │
          ├── Flux.usingWhen(
          │     Mono.defer(() -> tm.getReactiveTransaction(def)),  ← 获取事务
          │     tx -> flux,                                         ← 执行
          │     tx -> tm.commit(tx),                                ← 成功提交
          │     (tx, err) -> tm.rollback(tx),                       ← 异常回滚
          │     tx -> tm.rollback(tx)                               ← 取消回滚
          │   )
          │
          └── Reactor Context 传递 TransactionContext
```

---

## 五、事务传播行为速查

| 传播行为 | 常量值 | 有现存事务 | 无现存事务 |
|---------|--------|-----------|-----------|
| **REQUIRED** | 0 | 参与 | 新建 |
| **SUPPORTS** | 1 | 参与 | 无事务执行 |
| **MANDATORY** | 2 | 参与 | 抛异常 |
| **REQUIRES_NEW** | 3 | 挂起旧事务, 新建 | 新建 |
| **NOT_SUPPORTED** | 4 | 挂起, 无事务执行 | 无事务执行 |
| **NEVER** | 5 | 抛异常 | 无事务执行 |
| **NESTED** | 6 | 嵌套 (Savepoint) | 新建 |

---

## 六、隔离级别速查

| 隔离级别 | 常量值 | 脏读 | 不可重复读 | 幻读 |
|---------|--------|------|-----------|------|
| **DEFAULT** | -1 | 由数据库默认值决定 | | |
| **READ_UNCOMMITTED** | 1 | ✓ | ✓ | ✓ |
| **READ_COMMITTED** | 2 | ✗ | ✓ | ✓ |
| **REPEATABLE_READ** | 4 | ✗ | ✗ | ✓ |
| **SERIALIZABLE** | 8 | ✗ | ✗ | ✗ |

---

## 七、关键类速查

| 类/接口 | 包 | 说明 |
|---------|-----|------|
| `PlatformTransactionManager` | `transaction` | 命令式事务管理器接口 |
| `ReactiveTransactionManager` | `transaction.reactive` | 响应式事务管理器接口 |
| `TransactionDefinition` | `transaction` | 事务定义 (传播/隔离/超时/只读) |
| `TransactionStatus` | `transaction` | 事务状态 (含 Savepoint 管理) |
| `AbstractPlatformTransactionManager` | `transaction.support` | 命令式事务管理器基类 (1363 行) |
| `TransactionTemplate` | `transaction.support` | 编程式事务模板 |
| `TransactionSynchronizationManager` | `transaction.support` | 命令式同步管理器 (ThreadLocal) |
| `TransactionInterceptor` | `transaction.interceptor` | @Transactional AOP 拦截器 |
| `TransactionAspectSupport` | `transaction.interceptor` | 事务切面基类 (1139 行) |
| `AnnotationTransactionAttributeSource` | `transaction.interceptor` | 注解事务属性源 |
| `TransactionalOperator` | `transaction.reactive` | 响应式编程式事务操作符 |
| `AbstractReactiveTransactionManager` | `transaction.reactive` | 响应式事务管理器基类 |
| `TransactionContextManager` | `transaction.reactive` | 响应式事务上下文管理器 |
| `JtaTransactionManager` | `transaction.jta` | JTA 事务管理器 |
| `DataAccessException` | `dao` | DAO 异常基类 |

---

## 八、依赖关系

```
spring-tx
  ├── api: spring-beans
  ├── api: spring-core
  ├── optional: jakarta.transaction:jakarta.transaction-api  (JTA)
  ├── optional: jakarta.resource:jakarta.resource-api        (JCA)
  ├── optional: io.projectreactor:reactor-core               (响应式)
  ├── optional: io.smallrye.reactive:mutiny                  (响应式)
  └── optional: org.jetbrains.kotlin:kotlin-stdlib

---

## 九、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | BeanFactory、DI |
| 上游 | [spring-core](L1-spring-core.md) | L1 核心 | 反射、工具类 |
| 下游 | [spring-jdbc](L6-spring-jdbc.md) | L6 数据 | DataSourceTransactionManager |
| 下游 | [spring-orm](L6-spring-orm.md) | L6 数据 | JPA/Hibernate 事务管理 |
| 下游 | [spring-r2dbc](L6-spring-r2dbc.md) | L6 数据 | 响应式事务 |
| 下游 | [spring-jms](L6-spring-jms.md) | L6 消息 | JMS 事务管理 |
| 下游 | [spring-context-support](L4-spring-context-support.md) | L4 上下文 | 事务感知缓存 |
```
