# spring-orm 模块功能文档

---

## 一、模块定位

spring-orm 是 Spring 的 **对象关系映射（ORM）集成模块**，64 个 Java 文件（~14800 行），负责：

- **JPA 集成**：JpaTransactionManager、JpaDialect SPI、SharedEntityManagerCreator
- **Hibernate 原生集成**：HibernateTransactionManager、LocalSessionFactoryBean、SpringSessionContext
- **JPA Vendor 适配**：HibernateJpaVendorAdapter、EclipseLinkJpaVendorAdapter
- **EntityManager 管理**：LocalContainerEntityManagerFactoryBean、OpenEntityManagerInView
- **异常转换**：JPA/Hibernate 异常 → Spring DataAccessException 体系

**依赖**：`spring-core`、`spring-beans`、`spring-context`、`spring-tx`、`spring-jdbc`

---

## 二、模块全景图

```
spring-orm (64 files, ~14812 lines)
│
├── org.springframework.orm/                           # 顶层异常 (3 files)
│   ├── ObjectOptimisticLockingFailureException         — 乐观锁失败异常 (159 lines)
│   └── ObjectRetrievalFailureException                 — 对象检索失败异常 (133 lines)
│
├── org.springframework.orm.jpa/                        # JPA 核心 (19 files)
│   ├── JpaTransactionManager                           — ★ JPA 事务管理器 (811 lines)
│   ├── AbstractEntityManagerFactoryBean               — ★ EMF 抽象工厂 Bean (794 lines)
│   ├── SharedEntityManagerCreator                     — ★ 共享 EM 动态代理 (642 lines)
│   ├── ExtendedEntityManagerCreator                   — 扩展 EM 代理创建器 (510 lines)
│   ├── EntityManagerFactoryUtils                      — EM 工厂工具 (666 lines)
│   ├── LocalContainerEntityManagerFactoryBean         — ★ 容器引导 EMF (507 lines)
│   ├── LocalEntityManagerFactoryBean                  — 独立引导 EMF (288 lines)
│   ├── PersistenceAnnotationBeanPostProcessor         — ★ @PersistenceContext/@PersistenceUnit 处理
│   ├── JpaDialect                                     — JPA 方言 SPI (172 lines)
│   ├── DefaultJpaDialect                              — 默认 JPA 方言 (217 lines)
│   ├── EntityManagerFactoryInfo                       — EMF 元数据接口
│   └── EntityManagerHolder                            — EM 资源持有者
│
├── org.springframework.orm.jpa.hibernate/             # Hibernate 集成 (14 files)
│   ├── HibernateTransactionManager                    — ★ Hibernate 事务管理器 (848 lines)
│   ├── LocalSessionFactoryBean                        — ★ SessionFactory Bean (655 lines)
│   ├── LocalSessionFactoryBuilder                     — SessionFactory 构建器 (443 lines)
│   ├── SpringSessionContext                           — ★ Hibernate CurrentSessionContext (268 lines)
│   ├── SpringBeanContainer                            — Hibernate BeanContainer SPI (282 lines)
│   ├── HibernateExceptionTranslator                   — ★ Hibernate 异常转换 (226 lines)
│   ├── SharedSessionCreator                           — 共享 Session 代理 (158 lines)
│   ├── SpringSessionSynchronization                   — Session 事务同步 (165 lines)
│   ├── SessionHolder                                  — Session 资源持有者 (112 lines)
│   ├── SpringFlushSynchronization                     — Flush 事务同步 (64 lines)
│   ├── SpringJtaSessionContext                        — JTA Session 上下文 (49 lines)
│   └── ConfigurableJtaPlatform                        — JTA 平台配置 (112 lines)
│
├── org.springframework.orm.jpa.persistenceunit/       # 持久化单元 (15 files)
│   ├── DefaultPersistenceUnitManager                  — 默认持久化单元管理器
│   ├── PersistenceUnitManager                         — 持久化单元管理器接口
│   └── SmartPersistenceUnitInfo                       — 智能持久化单元信息
│
├── org.springframework.orm.jpa.support/               # JPA 支持 (6 files)
│   ├── OpenEntityManagerInViewFilter                  — ★ 视图层 EM 保持过滤器 (255 lines)
│   ├── OpenEntityManagerInViewInterceptor             — 视图层 EM 保持拦截器 (159 lines)
│   ├── SharedEntityManagerBean                        — 共享 EM Bean (123 lines)
│   ├── EntityManagerFactoryAccessor                   — EMF 访问器基类 (180 lines)
│   └── AsyncRequestInterceptor                        — 异步请求拦截器 (124 lines)
│
└── org.springframework.orm.jpa.vendor/                # Vendor 适配 (7 files)
    ├── JpaVendorAdapter                               — JPA 供应商适配器 SPI (161 lines)
    ├── AbstractJpaVendorAdapter                       — 抽象 Vendor 适配器 (163 lines)
    ├── HibernateJpaVendorAdapter                      — ★ Hibernate Vendor 适配器 (282 lines)
    ├── HibernateJpaDialect                            — ★ Hibernate JPA 方言 (277 lines)
    ├── EclipseLinkJpaVendorAdapter                   — EclipseLink Vendor 适配器 (119 lines)
    ├── EclipseLinkJpaDialect                          — EclipseLink JPA 方言 (202 lines)
    └── Database                                       — 数据库类型枚举 (62 lines)
```

---

## 三、核心流程

### 3.1 JpaTransactionManager 事务流程

```
JpaTransactionManager 类层次:
  AbstractPlatformTransactionManager
    └── JpaTransactionManager implements ResourceTransactionManager, BeanFactoryAware, InitializingBean

doGetTransaction()
  ├── TransactionSynchronizationManager → EntityManagerHolder (按 EMF key)
  ├── TransactionSynchronizationManager → ConnectionHolder (按 DataSource key)
  └── 返回 JpaTransactionObject

doBegin(txObj, definition)
  ├── 创建新 EntityManager (如无现有) → createEntityManagerForTransaction()
  ├── JpaDialect.beginTransaction(em, definition) → 返回 transactionData
  │     ├── DefaultJpaDialect: em.getTransaction().begin(), 支持 timeout
  │     │     └── 只读 → FlushModeType.EXPLICIT
  │     └── HibernateJpaDialect: 额外处理 isolation level + read-only JDBC Connection
  ├── 如有 DataSource: JpaDialect.getJdbcConnection(em)
  │     └── HibernateJpaDialect → HibernateConnectionHandle
  │           └── SessionImplementor.getJdbcCoordinator().getLogicalConnection().getPhysicalConnection()
  │     └── 包装为 ConnectionHolder → 绑定到 TSM (使 JDBC 代码参与同一事务)
  ├── EntityManagerHolder → 绑定到 TSM
  └── 失败时: close EntityManager after rollback

doCommit()  → em.getTransaction().commit()
doRollback() → em.getTransaction().rollback() → if pre-bound EM, call clear()

doCleanupAfterCompletion()
  ├── 解绑 EntityManagerHolder
  ├── 解绑 ConnectionHolder → releaseJdbcConnection via JpaDialect
  ├── JpaDialect.cleanupTransaction(transactionData)
  └── 新创建的 EM → close(); 预绑定的 EM → leave open
```

### 3.2 SharedEntityManagerCreator 动态代理

```
SharedEntityManagerCreator 为每个操作创建事务范围的 EntityManager 代理:

User calls: sharedEM.persist(entity)
  │
  ├── SharedEntityManagerInvocationHandler.invoke(proxy, method, args):
  │     ├── 特殊方法处理:
  │     │     ├── isOpen() → 永远返回 true
  │     │     ├── close() → 忽略 (生命周期由 JpaTransactionManager 管理)
  │     │     ├── getTransaction() → throw IllegalStateException
  │     │     └── unwrap / getEntityManagerFactory / getCriteriaBuilder → 委托
  │     │
  │     ├── 获取目标 EntityManager:
  │     │     └── EntityManagerFactoryUtils.doGetTransactionalEntityManager(emf, properties, sync)
  │     │           ├── 有活跃事务 → 返回事务绑定的 EM
  │     │           └── 无活跃事务 → 返回 null
  │     │
  │     ├── 需要事务的方法 (persist, merge, remove, flush, refresh, joinTransaction):
  │     │     └── 无活跃事务 → throw TransactionRequiredException
  │     │
  │     ├── 无事务时:
  │     │     └── 创建临时 EM (用完即关)
  │     │
  │     └── 返回 Query 时:
  │           └── 包装为 DeferredQueryInvocationHandler (延迟 EM 关闭直到 Query 执行完毕)
```

### 3.3 LocalContainerEntityManagerFactoryBean 启动流程

```
afterPropertiesSet():
  │
  ├── ① 初始化 PersistenceUnitManager (如未外部提供)
  │     └── DefaultPersistenceUnitManager
  │           ├── 扫描 persistence.xml (META-INF/persistence.xml)
  │           ├── 扫描 managed classes (如配置)
  │           └── 合并 JPA 属性
  │
  ├── ② determinePersistenceUnitInfo(manager)
  │     └── 按名称解析持久化单元
  │
  ├── ③ 应用 JpaVendorAdapter 增强:
  │     └── SmartPersistenceUnitInfo.setPersistenceProviderPackageName()
  │
  ├── ④ 调用 super.afterPropertiesSet() → createNativeEntityManagerFactory()
  │     │
  │     ├── 解析 PersistenceProvider:
  │     │     ├── HibernateJpaVendorAdapter → SpringHibernateJpaPersistenceProvider
  │     │     └── 或通过 ClassUtils 加载 provider 类
  │     │
  │     └── provider.createContainerEntityManagerFactory(pui, jpaPropertyMap)
  │           └── Hibernate: 应用所有 Vendor 属性 (hibernate.dialect, hibernate.hbm2ddl.auto 等)
  │
  ├── ⑤ createEntityManagerFactoryProxy(nativeEmf)
  │     └── JDK 动态代理 → 拦截 createEntityManager() 调用
  │           └── 返回 ExtendedEntityManagerCreator 包装的 EM
  │
  ├── ⑥ SharedEntityManagerCreator.createSharedEntityManager(nativeEmf)
  │     └── 返回共享 EM 代理 (线程安全, 事务感知)
  │
  └── ⑦ (JPA 4.0) 创建 sharedEntityAgent
```

### 3.4 SpringSessionContext 流程

```
Hibernate 配置: hibernate.current_session_context_class =
    org.springframework.orm.jpa.hibernate.SpringSessionContext

SessionFactory.getCurrentSession():
  │
  ├── ① 检查 TransactionSynchronizationManager:
  │     ├── 直接绑定的 Session → 返回
  │     ├── SessionHolder → 返回 session (自动注册 SpringSessionSynchronization)
  │     └── EntityManagerHolder → 解包 JPA EntityManager.getDelegate() → Session
  │           (JpaTransactionManager 互操作性)
  │
  ├── ② 有 JTA 活跃 → 委托给 SpringJtaSessionContext
  │
  ├── ③ 有 TransactionSynchronization 活跃但无 Session → 延迟创建:
  │     ├── 如有 DataSource: sessionFactory.withOptions()
  │     │     .connection(DataSourceUtils.getConnection(dataSource)).openSession()
  │     └── 否则: sessionFactory.openSession()
  │     └── 绑定 SessionHolder 到 TSM (注册 SpringSessionSynchronization)
  │
  └── ④ 无事务上下文 → throw HibernateException

SpringSessionSynchronization 事务回调:
  ├── beforeCommit(): flush Session (除非 FlushMode.MANUAL)
  ├── beforeCompletion(): 恢复 FlushMode, 断开 JDBC Connection
  └── afterCompletion(): rollback 时 clear(), 新创建 Session → close()
```

### 3.5 HibernateExceptionTranslator 异常映射

```
Hibernate Exception → Spring DataAccessException:

JDBCConnectionException       → DataAccessResourceFailureException
SQLGrammarException           → InvalidDataAccessResourceUsageException
QueryTimeoutException         → QueryTimeoutException
LockAcquisitionException      → CannotAcquireLockException
PessimisticLockException      → PessimisticLockingFailureException
ConstraintViolationException  → DataIntegrityViolationException
DataException                 → DataIntegrityViolationException
QueryException                → InvalidDataAccessResourceUsageException
NonUniqueResultException      → IncorrectResultSizeDataAccessException
NonUniqueObjectException      → DuplicateKeyException
PropertyValueException        → DataIntegrityViolationException
PersistentObjectException     → InvalidDataAccessApiUsageException
TransientObjectException      → InvalidDataAccessApiUsageException
ObjectDeletedException        → InvalidDataAccessApiUsageException
UnresolvableObjectException   → ObjectRetrievalFailureException
WrongClassException           → ObjectRetrievalFailureException
StaleObjectStateException     → ObjectOptimisticLockingFailureException
StaleStateException           → ObjectOptimisticLockingFailureException
OptimisticEntityLockException → ObjectOptimisticLockingFailureException
PessimisticEntityLockException→ PessimisticLockingFailureException / CannotAcquireLockException
JDBCException (with JDBC cause)→ SQLExceptionTranslator.translate()
TransactionException (SQL cause)→ SQLExceptionTranslator.translate()

递归处理: exception.getCause() 如为 HibernateException → 递归映射
```

### 3.6 OpenEntityManagerInView 模式

```
请求到达:
  │
  ├── OpenEntityManagerInViewFilter.doFilterInternal():
  │     │
  │     ├── 检查是否已有 EM 绑定到此 EMF → 设置 participate 标志
  │     │
  │     ├── 如未参与且非 async dispatch:
  │     │     ├── EntityManagerFactoryUtils.createEntityManager()
  │     │     ├── 包装为 EntityManagerHolder
  │     │     ├── 绑定到 TransactionSynchronizationManager
  │     │     └── 注册 AsyncRequestInterceptor (异步支持)
  │     │
  │     ├── filterChain.doFilter(request, response)
  │     │     └── 视图层懒加载不会触发 LazyInitializationException
  │     │
  │     └── finally (如非参与者):
  │           ├── 解绑 EntityManagerHolder
  │           └── 如异步未开始 → close EntityManager
```

---

## 四、JpaVendorAdapter 对比

| 特性 | HibernateJpaVendorAdapter | EclipseLinkJpaVendorAdapter |
|------|--------------------------|----------------------------|
| Provider 类 | HibernatePersistenceProvider | EclipseLink PersistenceProvider |
| Dialect 类 | HibernateJpaDialect | EclipseLinkJpaDialect |
| EM 接口 | Session.class | JpaEntityManager.class |
| EMF 接口 | SessionFactory.class | EntityManagerFactory.class |
| 支持 JDBC Connection 暴露 | ✅ (HibernateConnectionHandle) | ✅ (EclipseLinkConnectionHandle) |
| 支持 Isolation Level | ✅ (通过 JDBC Connection) | ✅ (通过 DatabaseLogin) |
| 支持 Spring Bean 注入 | ✅ (SpringBeanContainer) | ❌ |

---

## 五、依赖关系

```
spring-orm
  ├── api: spring-core
  ├── api: spring-beans
  ├── api: spring-context
  ├── api: spring-tx
  ├── api: spring-jdbc
  ├── optional: org.hibernate.orm:hibernate-core
  ├── optional: org.eclipse.persistence:eclipselink
  ├── optional: jakarta.persistence:jakarta.persistence-api
  ├── optional: jakarta.transaction:jakarta.transaction-api
  └── optional: org.jetbrains.kotlin:kotlin-stdlib

---

## 六、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-jdbc](L6-spring-jdbc.md) | L6 数据 | JDBC 基础设施 |
| 上游 | [spring-tx](L5-spring-tx.md) | L5 事务 | 事务管理器基类 |
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
| 下游 | [spring-aspects](L9-spring-aspects.md) | L9 辅助 | AspectJ 事务/缓存织入 |
```
