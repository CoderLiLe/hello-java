# spring-aspects 模块功能文档

---

## 一、模块定位

spring-aspects 是 Spring 的 **AspectJ 编译时/加载时织入切面模块**，22 个源文件（12 个 `.aj` 切面 + 10 个 `.java` 文件），负责：

- **依赖注入织入**：`@Configurable` 注解支持，通过 `new` 或反序列化创建的域对象自动装配
- **事务织入**：Spring `@Transactional` 和 JTA `@Transactional` 的 AspectJ 实现
- **缓存织入**：`@Cacheable/@CacheEvict/@CachePut` 和 JCache 注解的 AspectJ 实现
- **异步织入**：Spring `@Async` 的 AspectJ 实现

**依赖**：`spring-aop`、`spring-beans`、`spring-context`、`spring-context-support`、`spring-tx`（均为 optional）

---

## 二、模块全景图

```
spring-aspects (22 files)
│
├── org.springframework.beans.factory.aspectj/         # 依赖注入切面 (6 files)
│   ├── AbstractDependencyInjectionAspect.aj            — 抽象注入基础切面 (pre/post 构造)
│   ├── AbstractInterfaceDrivenDependencyInjectionAspect.aj — 基于接口的注入 + 反序列化支持
│   ├── AnnotationBeanConfigurerAspect.aj               — ★ @Configurable 具体切面
│   ├── GenericInterfaceDrivenDependencyInjectionAspect.aj — 泛型接口驱动注入
│   └── ConfigurableObject.java                         — ConfigurableObject 接口
│
├── org.springframework.cache.aspectj/                  # 缓存切面 (5 files)
│   ├── AbstractCacheAspect.aj                          — 抽象缓存基础切面
│   ├── AnnotationCacheAspect.aj                        — ★ @Cacheable/@CacheEvict/@CachePut 切面
│   ├── JCacheCacheAspect.aj                            — JSR-107 JCache 切面
│   ├── AspectJCachingConfiguration.java                — Spring 缓存切面配置
│   ├── AspectJJCacheConfiguration.java                 — JCache 切面配置
│   └── AnyThrow.java                                   — 异常解包工具
│
├── org.springframework.scheduling.aspectj/             # 异步切面 (3 files)
│   ├── AbstractAsyncExecutionAspect.aj                 — 抽象异步执行基础切面
│   ├── AnnotationAsyncExecutionAspect.aj               — ★ @Async 切面
│   └── AspectJAsyncConfiguration.java                  — 异步切面配置
│
├── org.springframework.transaction.aspectj/            # 事务切面 (4 files)
│   ├── AbstractTransactionAspect.aj                    — 抽象事务基础切面
│   ├── AnnotationTransactionAspect.aj                  — ★ Spring @Transactional 切面
│   ├── JtaAnnotationTransactionAspect.aj              — JTA @Transactional 切面
│   ├── AspectJTransactionManagementConfiguration.java  — 事务切面配置
│   └── AspectJJtaTransactionManagementConfiguration.java — JTA 事务切面配置
│
├── org.springframework.context.annotation.aspectj/     # 启用注解 (3 files)
│   ├── EnableSpringConfigured.java                     — @EnableSpringConfigured 启用注解
│   └── SpringConfiguredConfiguration.java              — 配置器注册
│
└── resources/META-INF/
    └── aop.xml                                         — AspectJ LTW 描述符 (6 个切面自动织入)
```

---

## 三、核心流程

### 3.1 @Configurable 依赖注入织入

```
对象创建: new MyDomainObject()
  │
  ├── AnnotationBeanConfigurerAspect 织入 initialization() 连接点
  │     └── 所有 @Configurable 类型被 declare parents 实现 ConfigurableObject
  │
  ├── AbstractDependencyInjectionAspect 判断构造时机:
  │     ├── preConstructionCondition()  → 构造前注入 (preConstruction=true 时)
  │     └── postConstructionCondition() → 构造后注入 (默认)
  │
  ├── configureBean(targetObject)
  │     └── BeanConfigurerSupport.configureBean()
  │           ├── AnnotationBeanWiringInfoResolver 从 @Configurable 提取 beanName
  │           ├── BeanFactory.getBean(beanName) 获取或创建 bean 定义
  │           └── AutowiredAnnotationBeanPostProcessor.autowire() 执行注入
  │
  └── 反序列化支持:
        └── AbstractInterfaceDrivenDependencyInjectionAspect
              ├── declare parents: ConfigurableObject+ && Serializable+ 
              │     implements ConfigurableDeserializationSupport
              └── 织入 readResolve() → 反序列化时自动调用 configureBean()
```

### 3.2 事务织入

```
@Transactional 方法调用:
  │
  ├── AnnotationTransactionAspect 切入点:
  │      executionOfAnyPublicMethodInAtTransactionalType()    ← 类级别 @Transactional
  │      || executionOfTransactionalMethod()                  ← 方法级别 @Transactional
  │
  ├── AbstractTransactionAspect.around(txObject):
  │     ├── 提取 MethodSignature
  │     ├── invokeWithinTransaction(method, targetClass, callback)
  │     │     ├── AnnotationTransactionAttributeSource 解析事务属性
  │     │     ├── PlatformTransactionManager.getTransaction()
  │     │     ├── callback 执行: proceed(txObject)
  │     │     │     └── Rethrower 内部类 → 类型擦除传播检查型异常
  │     │     └── commit / rollback
  │     └── 返回结果
  │
  └── JtaAnnotationTransactionAspect 流程相同，匹配 jakarta.transaction.Transactional
```

### 3.3 缓存织入

```
@Cacheable 方法调用:
  │
  ├── AnnotationCacheAspect.around(cachedObject):
  │     ├── 构建 CacheOperationInvoker 包装 proceed()
  │     └── execute(invoker, target, method, args)
  │           ├── AnnotationCacheOperationSource 解析缓存注解
  │           ├── CacheManager.getCache(name)
  │           ├── 缓存命中 → 返回缓存值 (不执行方法)
  │           └── 缓存未命中 → 执行方法 → put 到缓存
  │
  └── JCacheCacheAspect (JSR-107):
        └── 匹配 @CacheResult / @CachePut / @CacheRemove / @CacheRemoveAll
```

### 3.4 异步织入

```
@Async 方法调用:
  │
  ├── AnnotationAsyncExecutionAspect.around():
  │     ├── 确定 AsyncTaskExecutor
  │     ├── 无执行器 → proceed() 同步执行
  │     └── 有执行器 → doSubmit(task, executor, returnType)
  │           ├── 返回 Future / CompletableFuture
  │           ├── 返回 void → 返回 null
  │           └── handleError() 异步异常处理
  │
  └── 编译时验证:
        └── declare error: 返回类型不是 void/Future → 编译错误
```

---

## 四、与 Spring AOP 的对比

| 特性 | Spring AOP (代理) | AspectJ (本模块) |
|------|-------------------|------------------|
| 织入时机 | 运行时 (JDK/CGLIB 代理) | 编译时 / 加载时 |
| 拦截范围 | 仅公共方法 | 所有方法 + 构造函数 |
| 自调用拦截 | ❌ (代理限制) | ✅ (直接织入) |
| `new` 对象注入 | ❌ | ✅ (@Configurable) |
| 反序列化注入 | ❌ | ✅ (readResolve 织入) |
| 性能 | 代理反射开销 | 零开销 (直接字节码) |
| 配置复杂度 | 低 (纯 Spring) | 高 (需 AspectJ 编译器/LTW agent) |

---

## 五、使用方式

### 编译时织入

```gradle
// build.gradle
plugins {
    id 'io.freefair.aspectj' version 'x.y.z'
}
dependencies {
    implementation 'org.springframework:spring-aspects'
}
```

### 加载时织入

```java
@Configuration
@EnableLoadTimeWeaving
@EnableSpringConfigured  // 启用 @Configurable 支持
public class AppConfig {}
```

```xml
<!-- META-INF/aop.xml (模块内置，自动启用 6 个切面) -->
<aspectj>
    <aspects>
        <aspect name="...AnnotationBeanConfigurerAspect"/>
        <aspect name="...AnnotationAsyncExecutionAspect"/>
        <aspect name="...AnnotationTransactionAspect"/>
        <aspect name="...JtaAnnotationTransactionAspect"/>
        <aspect name="...AnnotationCacheAspect"/>
        <aspect name="...JCacheCacheAspect"/>
    </aspects>
</aspectj>
```

---

## 六、依赖关系

```
spring-aspects
  ├── api: org.aspectj:aspectjweaver
  ├── compile: org.aspectj:aspectjrt
  ├── optional: spring-aop
  ├── optional: spring-beans
  ├── optional: spring-context
  ├── optional: spring-context-support  (JCache 支持)
  ├── optional: spring-tx
  ├── optional: spring-orm
  ├── optional: jakarta.transaction:jakarta.transaction-api
  └── optional: javax.cache:cache-api

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-aop](L3-spring-aop.md) | L3 增强 | AOP 基础设施、AspectJExpressionPointcut |
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | @Configurable 依赖注入 |
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
| 上游 | [spring-tx](L5-spring-tx.md) | L5 事务 | @Transactional AspectJ 实现 |
| 上游 | [spring-context-support](L4-spring-context-support.md) | L4 上下文 | JCache 缓存切面 |
| 同级 | [spring-instrument](L9-spring-instrument.md) | L9 辅助 | Java Agent（LTW 依赖） |
```
