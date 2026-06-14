# Spring 事务实现源码深度解析

> 本文深入分析 Spring 声明式事务的实现原理，覆盖 @Transactional 注解解析、TransactionInterceptor AOP 拦截、AbstractPlatformTransactionManager 传播/提交/回滚机制、以及 TransactionSynchronizationManager ThreadLocal 事务同步。
> 相关模块文档：[spring-tx](../modules/L5-spring-tx.md)、[spring-aop](../modules/L3-spring-aop.md)

---

## 一、事务核心概念关系

```
┌──────────────────┐     ┌──────────────────────┐
│ @Transactional   │     │ PlatformTransactionMgr│
│ (注解声明)       │     │ (事务管理器接口)      │
│  propagation     │     │  getTransaction()     │
│  isolation       │     │  commit()             │
│  timeout         │     │  rollback()           │
│  readOnly        │     └──────────┬───────────┘
│  rollbackFor     │                │
└────────┬─────────┘     ┌──────────▼───────────┐
         │               │ AbstractPlatform     │
         │               │ TransactionManager   │
         │               │ (Template Method)    │
         │               └──────────┬───────────┘
         │                          │
┌────────▼──────────────────────────▼───────────┐
│          TransactionInterceptor               │
│  invoke() → invokeWithinTransaction()         │
│    1. 获取 @Transactional 属性                 │
│    2. 获取 TransactionManager                  │
│    3. tm.getTransaction(def)                  │
│    4. invocation.proceed()                    │
│    5. tm.commit() / tm.rollback()             │
└───────────────────────────────────────────────┘
```

---

## 二、@Transactional 注解解析

### 2.1 开启声明式事务

```
@EnableTransactionManagement
  → @Import(TransactionManagementConfigurationSelector)
    → 默认 ProxyTransactionManagementConfiguration (代理模式)
      → 注册 3 个核心 Bean:
          ① TransactionAttributeSource (解析 @Transactional)
          ② TransactionInterceptor (AOP 拦截器)
          ③ BeanFactoryTransactionAttributeSourceAdvisor (Pointcut Advisor)
```

### 2.2 AnnotationTransactionAttributeSource 解析链

```java
// 解析方法/类/接口上的 @Transactional, 合并属性
public TransactionAttribute getTransactionAttribute(Method method, Class<?> targetClass) {
    // ① 优先查找方法上的 @Transactional
    // ② 方法没有 → 查找类上的 @Transactional
    // ③ 类没有 → 查找接口上的 @Transactional
    // ④ 方法属性覆盖类属性
}
```

**解析优先级（方法 → 类 → 接口）**：

```
方法 @Transactional(propagation=REQUIRES_NEW)    ← 最高优先级
  └── 类 @Transactional(propagation=REQUIRED, readOnly=true)
        └── 接口 @Transactional(propagation=SUPPORTS)  ← 最低优先级

结果属性: propagation=REQUIRES_NEW, readOnly=true
```

### 2.3 RollbackRuleAttribute 回滚规则

```java
// RuleBasedTransactionAttribute.noRollbackOn(Throwable ex)
// 判断异常是否触发回滚:
//   ① 先检查 NoRollbackRule: 匹配 → 不回滚
//   ② 再检查 RollbackRule:   匹配 → 回滚
//   ③ 默认规则: RuntimeException / Error → 回滚, checked exception → 不回滚
```

---

## 三、TransactionInterceptor 拦截链路

### 3.1 入口：invoke()

```
TransactionInterceptor.invoke(MethodInvocation invocation)
  │
  └── TransactionAspectSupport.invokeWithinTransaction(method, targetClass, invocation)
        │
        ├── ① getTransactionAttributeSource().getTransactionAttribute(method, targetClass)
        │     └── 见 §2.2 解析过程
        │
        ├── ② determineTransactionManager(attr)
        │     ├── @Transactional("beanName") / @Transactional(value = "beanName")
        │     │   → 按名称查找 TransactionManager Bean
        │     ├── 如未指定 → 按类型查找 (PlatformTransactionManager / ReactiveTransactionManager)
        │     └── 多个同类型 → 通过 qualifier / @Primary 决策
        │
        ├── ③ 命令式: TransactionInfo txInfo = createTransactionIfNecessary(tm, attr, methodName)
        │     └── tm.getTransaction(attr)  → AbstractPlatformTransactionManager.getTransaction()
        │           └── 见 §四 传播行为处理
        │
        ├── ④ 执行目标方法:
        │     try {
        │         retVal = invocation.proceed();   // ★ 调用下一个拦截器 / 目标方法
        │     } catch (Throwable ex) {
        │         completeTransactionAfterThrowing(txInfo, ex);  // 决定回滚/提交
        │         throw ex;
        │     } finally {
        │         cleanupTransactionInfo(txInfo);   // 恢复旧事务上下文
        │     }
        │
        ├── ⑤ 成功提交: commitTransactionAfterReturning(txInfo)
        │     └── tm.commit(txInfo.getTransactionStatus())
        │
        └── ⑥ 返回结果
```

### 3.2 异常回滚决策

```
completeTransactionAfterThrowing(txInfo, ex):
  │
  ├── txAttr.rollbackOn(ex)?
  │     ├── YES → tm.rollback(status)
  │     └── NO  → tm.commit(status)    ← 即便抛异常, 也提交事务!
  │
  └── 默认规则:
        RuntimeException / Error → rollback
        checked Exception         → commit (不回滚)
        
        @Transactional(rollbackFor = Exception.class)      → checked 也回滚
        @Transactional(noRollbackFor = SpecificEx.class)  → RuntimeException 也不回滚
```

---

## 四、AbstractPlatformTransactionManager 传播行为

### 4.1 getTransaction() 完整流程

```
getTransaction(TransactionDefinition definition)
  │
  ├── ① doGetTransaction()  ← 子类实现, 获取当前事务对象
  │     └── DataSourceTransactionManager:
  │           从 TransactionSynchronizationManager.getResource(dataSource) 
  │           获取当前线程绑定的 ConnectionHolder
  │
  ├── ② isExistingTransaction(transaction)?
  │     │
  │     ├── NO (无现存事务):
  │     │   ├── PROPAGATION_MANDATORY → throw IllegalTransactionStateException
  │     │   ├── PROPAGATION_REQUIRED / REQUIRES_NEW / NESTED:
  │     │   │   ├── suspend(null)   // 挂起空事务 (清理 ThreadLocal)
  │     │   │   └── startTransaction(def, transaction, ...):
  │     │   │         ├── doBegin(transaction, definition):
  │     │   │         │   └── DataSourceTransactionManager:
  │     │   │         │         DataSource.getConnection()
  │     │   │         │         → 设置 autoCommit = false
  │     │   │         │         → 设置 isolationLevel
  │     │   │         │         → 设置 readOnly
  │     │   │         │         → bindResource(dataSource, ConnectionHolder)
  │     │   │         │            (绑定到 ThreadLocal)
  │     │   │         └── prepareSynchronization() → 注册 TransactionSynchronization
  │     │   ├── PROPAGATION_SUPPORTS / NOT_SUPPORTED / NEVER:
  │     │   │   └── "空" 事务状态 (无实际 JDBC 事务)
  │     │   └── 返回 DefaultTransactionStatus
  │     │
  │     └── YES (有现存事务):
  │           ├── PROPAGATION_NEVER → throw IllegalTransactionStateException
  │           ├── PROPAGATION_NOT_SUPPORTED:
  │           │   ├── suspend(transaction)  → doSuspend() 解绑资源
  │           │   └── 返回空事务状态 (以无事务方式执行)
  │           ├── PROPAGATION_REQUIRES_NEW:
  │           │   ├── suspend(transaction)  → doSuspend() 解绑 + 暂存
  │           │   └── startTransaction()    → doBegin() 新连接
  │           ├── PROPAGATION_NESTED:
  │           │   ├── useSavepointForNestedTransaction()?
  │           │   │   ├── YES (JDBC) → status.createAndHoldSavepoint()
  │           │   │   └── NO (JTA)  → startTransaction(nested=true)
  │           │   └── 返回嵌套事务状态
  │           └── PROPAGATION_REQUIRED / SUPPORTS / MANDATORY:
  │                 └── 参与现有事务 (不新开连接)
  │                       validateExistingTransaction(): isolation 校验, readOnly 校验
```

### 4.2 挂起与恢复机制

```
suspend(transaction):
  ├── doSuspend(transaction): 
  │     └── DataSourceTransactionManager:
  │           TransactionSynchronizationManager.unbindResource(dataSource)
  │           → 从 ThreadLocal 移除 ConnectionHolder
  ├── 触发 TransactionSynchronization.suspend()
  └── return SuspendedResourcesHolder (暂存旧连接, 用于后续 resume)

resume(transaction, suspendedResources):
  ├── doResume(transaction, suspendedResources):
  │     └── TransactionSynchronizationManager.bindResource(dataSource, oldHolder)
  ├── 触发 TransactionSynchronization.resume()
  └── 清理暂存的状态
```

---

## 五、commit / rollback 流程

### 5.1 commit() 完整流程

```
AbstractPlatformTransactionManager.commit(status)
  │
  ├── status.isCompleted()? → 已提交/已回滚 → throw UnexpectedRollbackException
  │
  ├── status.isLocalRollbackOnly()?
  │     ├── YES: 直接走 rollback 流程
  │     └── NO:
  │           ├── status.isGlobalRollbackOnly()?
  │           │     ├── YES: 全局回滚标记
  │           │     └── NO:
  │           │           ├── triggerBeforeCommit(status)
  │           │           │     └── for each TransactionSynchronization:
  │           │           │           sync.beforeCommit(readOnly=false)
  │           │           │
  │           │           ├── triggerBeforeCompletion()
  │           │           │
  │           │           ├── status.isNewTransaction()?  ← 此层创建的新连接?
  │           │           │     ├── YES → doCommit(status)
  │           │           │     │     └── DataSourceTransactionManager:
  │           │           │     │           ConnectionHolder.getConnection().commit()
  │           │           │     └── NO  → 不提交 (等待外层事务提交)
  │           │           │
  │           │           ├── 成功后: triggerAfterCommit(status)    ← afterCommit()
  │           │           └── 成功后: triggerAfterCompletion(status) ← STATUS_COMMITTED
  │           │
  │           └── 提交失败 → doRollbackOnCommitFailure()
  │
  └── finally: cleanupAfterCompletion(status)
        ├── doCleanupAfterCompletion(status):
        │     ├── DataSourceTransactionManager:
        │     │     ├── ConnectionHolder.clear()  → 重置隔离级别等
        │     │     ├── TransactionSynchronizationManager.unbindResource(dataSource)
        │     │     └── DataSourceUtils.releaseConnection(con, dataSource) → 归还连接
        │     └── 重置事务状态 (readOnly, isolationLevel)
        └── resume(previousTransaction) → 恢复之前挂起的事务
```

### 5.2 rollback() 流程

```
rollback(status):
  │
  ├── triggerBeforeCompletion()
  │
  ├── status.isNewTransaction()?
  │     ├── YES → doRollback(status)
  │     │     └── DataSourceTransactionManager:
  │     │           ConnectionHolder.getConnection().rollback()
  │     └── NO:
  │           ├── status.hasTransaction()? → doSetRollbackOnly(status)
  │           │     └── 标记外层事务: connectionHolder.setRollbackOnly()
  │           └── 无事务 → 什么都不做
  │
  ├── triggerAfterCompletion(STATUS_ROLLED_BACK)  ← afterCompletion(status)
  │
  └── cleanupAfterCompletion(status)
        └── 同 commit 的清理流程
```

### 5.3 rollback-only 传播机制

```
外层事务 REQUIRED
  └── 内层事务 REQUIRED (参与外层)
        └── 内层抛异常 → rollback(status)
              └── status.isNewTransaction() == false
                    → doSetRollbackOnly(status)  ← 只标记, 不 rollback
                      └── innerHolder.setRollbackOnly()

外层提交时:
  commit(outerStatus)
    → status.isGlobalRollbackOnly() == true  ← 检测到标记
      → doRollback(status)  ← 整个事务回滚!
      → throw UnexpectedRollbackException("Transaction rolled back because it has been marked as rollback-only")
```

---

## 六、TransactionSynchronizationManager

### 6.1 ThreadLocal 存储结构

```java
// 所有字段均为 static final ThreadLocal, 保证线程隔离
public abstract class TransactionSynchronizationManager {

    // ★ 核心: 资源持有者 Map (DataSource → ConnectionHolder, SessionFactory → SessionHolder)
    private static final ThreadLocal<Map<Object, Object>> resources = 
        new NamedThreadLocal<>("Transactional resources");

    // 事务同步回调集合
    private static final ThreadLocal<Set<TransactionSynchronization>> synchronizations =
        new NamedThreadLocal<>("Transaction synchronizations");

    // 事务名 (通常为 fullyQualifiedClassName.methodName)
    private static final ThreadLocal<String> currentTransactionName =
        new NamedThreadLocal<>("Current transaction name");

    // 只读标记
    private static final ThreadLocal<Boolean> currentTransactionReadOnly =
        new NamedThreadLocal<>("Current transaction read-only status");

    // 隔离级别
    private static final ThreadLocal<Integer> currentTransactionIsolationLevel =
        new NamedThreadLocal<>("Current transaction isolation level");

    // 实际活跃事务标记
    private static final ThreadLocal<Boolean> actualTransactionActive =
        new NamedThreadLocal<>("Actual transaction active");
}
```

### 6.2 资源绑定生命周期

```
doBegin():
  Connection newCon = DataSourceUtils.getConnection(dataSource);
  ConnectionHolder conHolder = new ConnectionHolder(newCon);
  TransactionSynchronizationManager.bindResource(dataSource, conHolder);
  // → resources.get().put(dataSource, conHolder)

doCleanupAfterCompletion():
  TransactionSynchronizationManager.unbindResource(dataSource);
  // → resources.get().remove(dataSource)
  DataSourceUtils.releaseConnection(con, dataSource);
  // → 归还连接到连接池
```

### 6.3 TransactionSynchronization 回调时序

```
TransactionSynchronization 接口回调顺序 (在一个事务生命周期中):

doBegin() → registerSynchronization(sync)
  │
  ├── beforeCommit(readOnly=false)     ← 提交前 (可在此 flush session)
  ├── beforeCompletion()                ← 完成前 (无论成功/失败)
  │
  ├── 事务提交:
  │     ├── afterCommit()               ← 提交后 (适合发消息/事件)
  │     └── afterCompletion(STATUS_COMMITTED)
  │
  └── 事务回滚:
        ├── afterRollback()             ← 回滚后 (6.1+)
        └── afterCompletion(STATUS_ROLLED_BACK)
```

---

## 七、编程式事务 (TransactionTemplate)

```
TransactionTemplate.execute(TransactionCallback<T> action)
  │
  ├── ① tm.getTransaction(this)   ← TransactionTemplate 自己是 TransactionDefinition
  │     └── AbstractPlatformTransactionManager.getTransaction()
  │           └── 与声明式相同的传播处理逻辑 (§四)
  │
  ├── ② try {
  │         result = action.doInTransaction(status);    ← ★ 用户回调
  │         tm.commit(status);
  │     } catch (Throwable ex) {
  │         if (rollbackOn(ex))  // 默认: RuntimeException/Error → rollback
  │             tm.rollback(status);
  │         else
  │             tm.commit(status);
  │         throw ex;
  │     }
  │
  └── ③ return result;
```

---

## 八、JPA/Hibernate 事务集成

### 8.1 JpaTransactionManager

```
JpaTransactionManager extends AbstractPlatformTransactionManager

doBegin():
  EntityManager em = createEntityManager();
  EntityManagerHolder emHolder = new EntityManagerHolder(em);
  TransactionSynchronizationManager.bindResource(emf, emHolder);
  // JPA 事务:
  EntityTransaction tx = em.getTransaction();
  tx.begin();

doCommit():
  emHolder.getEntityManager().getTransaction().commit();

doRollback():
  emHolder.getEntityManager().getTransaction().rollback();
```

---

## 九、事务失效场景详解

### 9.1 抛出检查异常导致事务不能正确回滚

```java
@Service
public class Service1 {
    @Autowired
    private AccountMapper accountMapper;

    @Transactional
    public void transfer(int from, int to, int amount) throws FileNotFoundException {
        int fromBalance = accountMapper.findBalanceBy(from);
        if (fromBalance - amount >= 0) {
            accountMapper.update(from, -1 * amount);
            new FileInputStream("aaa");  // 抛出 FileNotFoundException (checked)
            accountMapper.update(to, amount);
        }
    }
}
```

- **原因**：Spring 默认只会回滚 RuntimeException 和 Error，checked exception 不会触发回滚
- **解法**：`@Transactional(rollbackFor = Exception.class)`

### 9.2 业务方法内自己 try-catch 异常导致事务不能正确回滚

```java
@Service
public class Service2 {
    @Autowired
    private AccountMapper accountMapper;

    @Transactional(rollbackFor = Exception.class)
    public void transfer(int from, int to, int amount) {
        try {
            int fromBalance = accountMapper.findBalanceBy(from);
            if (fromBalance - amount >= 0) {
                accountMapper.update(from, -1 * amount);
                new FileInputStream("aaa");
                accountMapper.update(to, amount);
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace(); // 异常被吞掉，事务通知无法感知
        }
    }
}
```

- **原因**：事务通知只有捕捉到目标方法抛出的异常，才能进行回滚处理。如果目标自己 catch 掉异常，事务通知无法知悉
- **解法 1**：在 catch 块添加 `throw new RuntimeException(e);`
- **解法 2**：在 catch 块添加 `TransactionInterceptor.currentTransactionStatus().setRollbackOnly();`

### 9.3 AOP 切面顺序导致事务不能正确回滚

```java
@Service
public class Service3 {
    @Autowired
    private AccountMapper accountMapper;

    @Transactional(rollbackFor = Exception.class)
    public void transfer(int from, int to, int amount) throws FileNotFoundException {
        int fromBalance = accountMapper.findBalanceBy(from);
        if (fromBalance - amount >= 0) {
            accountMapper.update(from, -1 * amount);
            new FileInputStream("aaa");
            accountMapper.update(to, amount);
        }
    }
}

@Aspect
public class MyAspect {
    @Around("execution(* transfer(..))")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        try {
            return pjp.proceed();
        } catch (Throwable e) {
            e.printStackTrace();
            return null; // 异常被切面吞掉，事务切面无法感知
        }
    }
}
```

- **原因**：事务切面优先级最低，但如果自定义切面优先级与其相同，自定义切面在内层，若自定义切面没有正确抛出异常，事务切面无法感知
- **解法 1、2**：同 9.2
- **解法 3**：调整切面顺序，添加 `@Order(Ordered.LOWEST_PRECEDENCE - 1)`（不推荐）

### 9.4 非 public 方法导致的事务失效

```java
@Service
public class Service4 {
    @Autowired
    private AccountMapper accountMapper;

    @Transactional
    void transfer(int from, int to, int amount) throws FileNotFoundException {
        // 非 public 方法，事务不生效
        ...
    }
}
```

- **原因**：Spring 为方法创建代理、添加事务通知的前提条件是方法为 public
- **解法 1**：改为 public 方法
- **解法 2**：添加 bean 配置（不推荐）：

```java
@Bean
public TransactionAttributeSource transactionAttributeSource() {
    return new AnnotationTransactionAttributeSource(false);
}
```

### 9.5 父子容器导致的事务失效

```java
// App 配置类（父容器）
@Configuration
@ComponentScan("day04.tx.app.service")
@EnableTransactionManagement
public class AppConfig {
    // ... 有事务相关配置
}

// Web 配置类（子容器）
@Configuration
@ComponentScan("day04.tx.app")  // 扫描范围过大，包含了 service
public class WebConfig {
    // ... 无事务配置
}
```

- **原因**：子容器扫描范围过大，把未加事务配置的 service 也扫描进来
- **解法 1**：各扫描各的，不要图简便
- **解法 2**：不要用父子容器，所有 bean 放在同一容器

### 9.6 调用本类方法导致传播行为失效

```java
@Service
public class Service6 {
    @Transactional(propagation = Propagation.REQUIRED, rollbackFor = Exception.class)
    public void foo() throws FileNotFoundException {
        bar(); // 直接调用本类方法，不经过代理，事务传播行为失效
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW, rollbackFor = Exception.class)
    public void bar() throws FileNotFoundException {
        ...
    }
}
```

- **原因**：本类方法调用不经过代理，因此无法增强
- **解法 1**：依赖注入自己（代理）来调用

```java
@Service
public class Service6 {
    @Autowired
    private Service6 proxy;

    @Transactional(propagation = Propagation.REQUIRED, rollbackFor = Exception.class)
    public void foo() throws FileNotFoundException {
        proxy.bar(); // 通过代理调用
    }
    ...
}
```

- **解法 2**：通过 AopContext 拿到代理对象（需 `@EnableAspectJAutoProxy(exposeProxy = true)`）

```java
((Service6) AopContext.currentProxy()).bar();
```

### 9.7 @Transactional 没有保证原子行为

```java
@Service
public class Service7 {
    @Autowired
    private AccountMapper accountMapper;

    @Transactional(rollbackFor = Exception.class)
    public void transfer(int from, int to, int amount) {
        int fromBalance = accountMapper.findBalanceBy(from); // SELECT 不阻塞
        if (fromBalance - amount >= 0) {
            accountMapper.update(from, -1 * amount);
            accountMapper.update(to, amount);
        }
    }
}
```

- **原因**：事务的原子性仅涵盖 insert、update、delete、select … for update 语句，普通 select 方法不阻塞。两个线程同时查询到足够余额，都会执行扣减，导致金额变为负数
- **解法**：使用 `select … for update` 替换普通 select

### 9.8 @Transactional 方法导致的 synchronized 失效

```java
@Service
public class Service7 {
    @Transactional(rollbackFor = Exception.class)
    public synchronized void transfer(int from, int to, int amount) {
        int fromBalance = accountMapper.findBalanceBy(from);
        if (fromBalance - amount >= 0) {
            accountMapper.update(from, -1 * amount);
            accountMapper.update(to, amount);
        }
    }
}
```

- **原因**：synchronized 保证的仅是目标方法的原子性，环绕目标方法的还有 commit 等操作，它们并未处于 sync 块内。另一个线程在 commit 之前执行查询，依然会读到未更新的数据
- **解法 1**：synchronized 范围应扩大至代理方法调用
- **解法 2**：使用 `select … for update` 替换 select

### 9.9 其他失效场景

| 场景 | 原因 | 解决方案 |
|------|------|---------|
| **多线程** | ThreadLocal 不跨线程传播 | 确保事务内代码在同一线程执行 |
| **数据库引擎不支持** | MyISAM 不支持事务 | 使用 InnoDB |
| **@Transactional 用在非 Spring Bean** | Spring 只能代理容器管理的 Bean | 确保类是 Spring Bean |

---

## 十、关键扩展点

| 扩展点 | 接口 | 用途 |
|--------|------|------|
| 事务同步 | `TransactionSynchronization` | 提交前后回调 (flush session, 清理缓存) |
| 事务管理器 | `PlatformTransactionManager` | 自定义连接获取/提交/回滚逻辑 |
| 事务定义 | `TransactionAttributeSource` | 自定义事务属性来源 (非注解) |
| 回滚规则 | `RollbackRuleAttribute` | 自定义回滚异常侧策略 |
| 事务事件 | `@TransactionalEventListener` | 事务提交后异步处理 (spring-tx 内置) |

---

## 十一、相关文档

| 文档 | 说明 |
|------|------|
| [spring-tx 模块文档](../modules/L5-spring-tx.md) | 事务模块完整参考 |
| [AOP 实现深度解析](12-aop-implementation.md) | TransactionInterceptor 作为 AOP 拦截器 |
| [循环依赖深度解析](05-circular-dependency.md) | 事务代理 + 循环依赖 |
| [spring-orm 模块文档](../modules/L6-spring-orm.md) | JPA/Hibernate 事务集成 |
