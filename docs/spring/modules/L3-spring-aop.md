# spring-aop 模块功能文档

---

## 一、模块定位

spring-aop 是 Spring 的 **AOP（面向切面编程）模块**，226 个 Java 文件，负责：

- **动态代理创建**：JDK 动态代理（基于接口）和 CGLIB 代理（基于类）
- **切面组装**：Advice（通知）+ Pointcut（切点）= Advisor（切面）
- **拦截器链执行**：方法调用时按序执行所有 Advisor 的拦截器
- **自动代理**：通过 BeanPostProcessor 自动为匹配的 Bean 创建代理
- **@AspectJ 支持**：解析 `@Aspect`、`@Before`、`@After`、`@Around` 等注解
- **内置拦截器**：异步执行、性能监控、并发节流、跟踪日志等

**依赖**：`spring-core`、`spring-beans`、AOP Alliance（`org.aopalliance:aopalliance`，内嵌 fork）

---

## 二、模块全景图

```
spring-aop (226 files)
│
├── org.springframework.aop/                         # 核心抽象 (25 files)
│   ├── Pointcut                                    — 切点 (ClassFilter + MethodMatcher)
│   ├── Advisor                                     — 切面 (Advice 容器)
│   ├── PointcutAdvisor                             — 基于切点的切面
│   ├── IntroductionAdvisor                         — 引介切面 (添加接口)
│   ├── Advice 体系:                                 — 通知接口层次
│   │   ├── BeforeAdvice / MethodBeforeAdvice       — 前置通知
│   │   ├── AfterReturningAdvice                    — 返回后通知
│   │   ├── ThrowsAdvice                            — 异常通知
│   │   └── MethodInterceptor (来自 AOP Alliance)    — 环绕通知
│   ├── TargetSource                                — 目标对象来源
│   ├── ClassFilter / MethodMatcher                 — 过滤匹配器
│   └── SpringProxy / RawTargetAccess               — 标记接口
│
├── org.springframework.aop.framework/               # 代理创建核心 (26 files)
│   ├── AopProxy                                    — 代理接口 (getProxy)
│   ├── AopProxyFactory                             — 代理工厂接口
│   ├── DefaultAopProxyFactory                      — ★ 默认工厂 (JDK vs CGLIB)
│   ├── JdkDynamicAopProxy                          — ★ JDK 动态代理 (InvocationHandler)
│   ├── CglibAopProxy / ObjenesisCglibAopProxy      — ★ CGLIB 代理 (MethodInterceptor)
│   ├── AdvisedSupport                              — ★ 代理配置基类
│   ├── ProxyConfig                                 — 代理配置 (proxyTargetClass, exposeProxy, etc)
│   ├── ProxyCreatorSupport                         — 代理创建器基类
│   ├── ProxyFactory                                — 编程式代理工厂
│   ├── ProxyFactoryBean                            — 声明式代理 FactoryBean
│   ├── ReflectiveMethodInvocation                   — ★ 方法调用执行链
│   ├── DefaultAdvisorChainFactory                   — 拦截器链工厂
│   └── AopContext                                   — 当前代理上下文 (ThreadLocal)
│
├── org.springframework.aop.framework.autoproxy/     # 自动代理 (11 files)
│   ├── AbstractAutoProxyCreator                     — ★ 自动代理处理器基类
│   ├── AbstractAdvisorAutoProxyCreator              — Advisor 自动代理
│   ├── DefaultAdvisorAutoProxyCreator               — 默认 Advisor 自动代理
│   ├── InfrastructureAdvisorAutoProxyCreator        — 基础设施 Advisor 代理
│   ├── BeanNameAutoProxyCreator                     — 按名称自动代理
│   └── target/ 子包:                                — 目标对象创建器
│       └── AbstractBeanFactoryBasedTargetSourceCreator, LazyInitTargetSourceCreator
│
├── org.springframework.aop.framework.adapter/       # Advice 适配器 (13 files)
│   ├── AdvisorAdapterRegistry                      — 适配器注册表
│   ├── DefaultAdvisorAdapterRegistry               — 默认实现 (注册所有适配器)
│   ├── MethodBeforeAdviceAdapter                   — BeforeAdvice → MethodInterceptor
│   ├── AfterReturningAdviceAdapter                 — AfterReturning → MethodInterceptor
│   ├── ThrowsAdviceAdapter                         — ThrowsAdvice → MethodInterceptor
│   └── MethodBeforeAdviceInterceptor / AfterReturningAdviceInterceptor / ThrowsAdviceInterceptor
│
├── org.springframework.aop.aspectj/                 # 原生 AspectJ 支持 (24 files)
│   ├── AspectJExpressionPointcut                   — AspectJ 表达式切点
│   ├── AspectJMethodBeforeAdvice, etc.              — 原生 AspectJ Advice 实现
│   └── annotation/ 子包 (18 files):                 — @AspectJ 注解处理
│       ├── AnnotationAwareAspectJAutoProxyCreator   — ★ @AspectJ 自动代理
│       ├── AspectJAdvisorFactory                    — @Aspect 类 → Advisor 列表
│       ├── ReflectiveAspectJAdvisorFactory          — 反射式 Advisor 工厂
│       └── AspectJAnnotationAutoProxyCreator        — @AspectJ 注解代理创建
│
├── org.springframework.aop.aspectj.autoproxy/       # AspectJ 自动代理 (3 files)
│   └── AspectJAwareAdvisorAutoProxyCreator          — 排序时 AspectJ 感知
│
├── org.springframework.aop.config/                   # XML 配置解析 (18 files)
│   ├── AopNamespaceHandler                          — <aop:*> 命名空间处理器
│   └── ConfigBeanDefinitionParser                   — <aop:config> XML 解析
│
├── org.springframework.aop.interceptor/              # 内置拦截器 (14 files)
│   ├── AsyncExecutionInterceptor                   — @Async 异步执行
│   ├── PerformanceMonitorInterceptor               — 性能监控
│   ├── ConcurrencyThrottleInterceptor              — 并发节流
│   ├── CustomizableTraceInterceptor                — 可定制跟踪日志
│   ├── SimpleTraceInterceptor                      — 简单跟踪日志
│   └── ExposeInvocationInterceptor                 — 暴露当前 MethodInvocation
│
├── org.springframework.aop.support/                  # 工具支持 (29 files)
│   ├── AopUtils                                     — AOP 工具类
│   ├── DefaultPointcutAdvisor                       — 默认切面实现
│   ├── NameMatchMethodPointcut                      — 方法名匹配切点
│   ├── JdkRegexpMethodPointcut                      — 正则匹配切点
│   ├── ControlFlowPointcut                          — 控制流切点
│   ├── ComposablePointcut                           — 可组合切点 (union/intersection)
│   ├── AnnotationMatchingPointcut                   — 注解匹配切点
│   └── annotation/ 子包: @Transactional 等注解匹配
│
├── org.springframework.aop.target/                   # TargetSource 实现 (15 files)
│   ├── SingletonTargetSource                        — 单例目标
│   ├── PrototypeTargetSource                        — 原型目标 (每次新建)
│   ├── ThreadLocalTargetSource                      — 线程隔离目标
│   ├── CommonsPool2TargetSource                     — 对象池目标
│   ├── HotSwappableTargetSource                     — 热替换目标
│   └── dynamic/ 子包: 动态刷新目标源
│
└── org.springframework.aop.scope/                    # Scoped Bean 代理 (6 files)
    └── ScopedProxyFactoryBean                        — 作用域代理 FactoryBean
```

---

## 三、核心概念关系

```
                    ┌──────────────────────────┐
                    │        Pointcut           │
                    │  ┌──────────────────┐    │
                    │  │  ClassFilter     │     │  "在哪里切"
                    │  │  MethodMatcher   │     │
                    │  └──────────────────┘    │
                    └───────────┬──────────────┘
                                │
                ┌───────────────┼───────────────┐
                │                               │
        ┌───────▼───────┐               ┌───────▼───────┐
        │    Advice     │               │  Introduction │
        │  (通知)       │               │  (引介)       │
        │               │               │               │
        │ BeforeAdvice  │               │ 动态添加接口   │
        │ AfterReturning│               │               │
        │ ThrowsAdvice  │               └───────────────┘
        │ AroundAdvice  │
        └───────┬───────┘
                │
        ┌───────▼───────┐
        │    Advisor    │  ← Pointcut + Advice = 切面
        │ (切面)        │
        └───────┬───────┘
                │
        ┌───────▼───────┐
        │  ProxyFactory │  ← 组装 TargetSource + Advisor[] → 创建代理
        └───────┬───────┘
                │
        ┌───────▼───────┐
        │   AopProxy    │  ← JdkDynamicAopProxy 或 CglibAopProxy
        │   (代理对象)   │
        └───────────────┘
```

---

## 四、核心流程

### 4.1 代理创建决策流程 (DefaultAopProxyFactory)

```
DefaultAopProxyFactory.createAopProxy(AdvisedSupport config)
  │
  ├── 判断 createCglibProxy:
  │   config.isOptimize() == true           — 设置了优化标志
  │   || config.isProxyTargetClass() == true — 强制 CGLIB
  │   || !config.hasUserSuppliedInterfaces() — 未指定接口
  │
  ├── true → 检查 targetClass:
  │   ├── targetClass == null && 无接口   → throw AopConfigException
  │   ├── targetClass.isInterface()        → JdkDynamicAopProxy (接口)
  │   ├── Proxy.isProxyClass(targetClass)  → JdkDynamicAopProxy (已是 JDK 代理)
  │   ├── ClassUtils.isLambdaClass()       → JdkDynamicAopProxy (lambda)
  │   └── 普通类                           → ObjenesisCglibAopProxy ★
  │
  └── false → JdkDynamicAopProxy
```

### 4.2 编程式代理创建流程

```
ProxyFactory proxyFactory = new ProxyFactory();
proxyFactory.setTarget(target);          // 设置目标对象
proxyFactory.addAdvisor(advisor);        // 添加切面
proxyFactory.setProxyTargetClass(true);  // 强制 CGLIB

Object proxy = proxyFactory.getProxy();
  │
  ├── ProxyCreatorSupport.createAopProxy()
  │     └── DefaultAopProxyFactory.createAopProxy(this)
  │           └── 返回 JdkDynamicAopProxy 或 ObjenesisCglibAopProxy
  │
  └── aopProxy.getProxy()
        ├── JdkDynamicAopProxy:
        │     Proxy.newProxyInstance(classLoader, proxiedInterfaces, this)
        │     └── this 即 InvocationHandler.invoke()
        │
        └── ObjenesisCglibAopProxy:
              Enhancer.create(proxySuperClass, interfaces, callback)
              └── callback 即 MethodInterceptor.intercept()
```

### 4.3 方法调用拦截链执行流程（核心）

```
调用 proxy.method(args)
  │
  ├── JdkDynamicAopProxy.invoke(proxy, method, args)
  │     │
  │     ├── 0. 特殊方法处理:
  │     │   ├── equals/hashCode → 代理内部比较
  │     │   ├── Advised 接口方法 → 委托给 advised (AdvisedSupport)
  │     │   └── DecoratingProxy.getDecoratedClass() → 返回目标类
  │     │
  │     ├── 1. 获取拦截器链:
  │     │   List<Object> chain = advised.getInterceptorsAndDynamicInterceptionAdvice(method, targetClass)
  │     │   │
  │     │   │   DefaultAdvisorChainFactory.getInterceptorsAndDynamicInterceptionAdvice()
  │     │   │     │
  │     │   │     ├── 遍历所有 Advisor:
  │     │   │     │   ├── PointcutAdvisor: pointcut.match(method, targetClass)
  │     │   │     │   │   ├── 静态匹配 (isRuntime=false) → 添加拦截器
  │     │   │     │   │   └── 动态匹配 (isRuntime=true) → 添加 InterceptorAndDynamicMethodMatcher
  │     │   │     │   └── IntroductionAdvisor: classFilter.matches(targetClass)
  │     │   │     │
  │     │   │     └── Advisor → Advice → 适配为 MethodInterceptor:
  │     │   │         ├── MethodInterceptor 本身 → 直接使用
  │     │   │         ├── MethodBeforeAdvice  → MethodBeforeAdviceInterceptor
  │     │   │         ├── AfterReturningAdvice → AfterReturningAdviceInterceptor
  │     │   │         └── ThrowsAdvice         → ThrowsAdviceInterceptor
  │     │   │
  │     │   └── 若 chain 为空且非 public 方法 → 直接反射调用目标
  │     │
  │     ├── 2. 创建调用对象:
  │     │   ReflectiveMethodInvocation invocation = new ReflectiveMethodInvocation(
  │     │       proxy, target, method, args, targetClass, chain)
  │     │
  │     └── 3. 执行拦截器链:
  │           invocation.proceed()
  │             │
  │             ├── currentInterceptorIndex 递增
  │             ├── 获取当前拦截器:
  │             │   ├── InterceptorAndDynamicMethodMatcher:
  │             │   │     └── matcher.matches(method, targetClass, args) ?
  │             │   │         ├── true  → interceptor.invoke(this)
  │             │   │         └── false → proceed() 跳过
  │             │   └── MethodInterceptor:
  │             │         └── interceptor.invoke(this)  ← 递归
  │             │
  │             └── 链执行完毕 → invokeJoinpoint()
  │                   └── method.invoke(target, args)  ← 反射调用真实方法
  │
  └── CglibAopProxy 流程类似，通过 DynamicAdvisedInterceptor 实现
```

### 4.4 拦截器链执行示意图

```
调用 proxy.doSomething()
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Interceptor Chain (责任链模式)                                   │
│                                                                 │
│  invocation.proceed()                                           │
│    │                                                            │
│    ├── [0] MethodBeforeAdviceInterceptor                        │
│    │       ├── advice.before(method, args, target)              │
│    │       └── invocation.proceed() ──────────────────────┐     │
│    │                                                      │     │
│    ├── [1] ThrowsAdviceInterceptor                         │     │
│    │       ├── try {                                       │     │
│    │       │     invocation.proceed() ────────────────┐    │     │
│    │       │   } catch (Exception e) {                 │    │     │
│    │       │     advice.afterThrowing(method, args, e)│    │     │
│    │       │   }                                       │    │     │
│    │       └───────────────────────────────────────────┤    │     │
│    │                                                    │    │     │
│    ├── [2] AfterReturningAdviceInterceptor               │    │     │
│    │       ├── retVal = invocation.proceed() ───────┐    │    │     │
│    │       ├── advice.afterReturning(retVal, ...)    │    │    │     │
│    │       └── return retVal                         │    │    │     │
│    │                                                  │    │    │     │
│    ├── [3] 用户自定义 MethodInterceptor                 │    │    │     │
│    │       └── invocation.proceed() ──────────────┐   │    │    │     │
│    │                                                │   │    │    │     │
│    └── ★ invokeJoinpoint()  ← 链末端                │   │    │    │     │
│          └── method.invoke(target, args)  ← 真实调用 ◄───┘    │    │     │
│                                                               │    │     │
│          返回值逐级向上返回 ─────────────────────────────────────┘    │     │
│                                                                     │     │
└─────────────────────────────────────────────────────────────────────┘     │
```

### 4.5 自动代理流程（AbstractAutoProxyCreator）

```
AbstractAutoProxyCreator (实现 SmartInstantiationAwareBeanPostProcessor)

容器启动时，每个 Bean 创建过程中:

Bean 实例化后 → postProcessAfterInitialization() 被调用
  │
  ├── wrapIfNecessary(bean, beanName, cacheKey)
  │     │
  │     ├── ① 已处理过? → 从缓存 earlyProxyReferences 获取
  │     │
  │     ├── ② 基础设施 Bean? (Advice/Pointcut/Advisor 自身)
  │     │     └── 跳过: isInfrastructureClass(bean.getClass())
  │     │
  │     ├── ③ 不应代理? (shouldSkip)
  │     │     └── 跳过: 原始 TargetSource 目标对象等
  │     │
  │     ├── ④ 获取特定拦截器: getAdvicesAndAdvisorsForBean(beanClass, beanName, targetSource)
  │     │     │
  │     │     │   AbstractAdvisorAutoProxyCreator.findEligibleAdvisors(beanClass, beanName)
  │     │     │     │
  │     │     │     ├── 收集所有候选 Advisor: findCandidateAdvisors()
  │     │     │     │   ├── BeanFactory 中 Advisor 类型的 Bean
  │     │     │     │   └── (@AspectJ) AspectJAdvisorFactory 创建的 Advisor
  │     │     │     │
  │     │     │     └── 过滤匹配的 Advisor: findAdvisorsThatCanApply(candidateAdvisors, beanClass)
  │     │     │           └── AopUtils.canApply(advisor, targetClass)
  │     │     │               └── pointcut.getClassFilter().matches(targetClass)
  │     │     │                   && pointcut.getMethodMatcher().matches(method, targetClass)
  │     │     │
  │     │     └── 若有匹配的 Advisor → 返回它们
  │     │
  │     └── ⑤ 创建代理:
  │           ProxyFactory proxyFactory = new ProxyFactory();
  │           proxyFactory.copyFrom(this);
  │           proxyFactory.setTargetSource(targetSource);
  │           proxyFactory.addAdvisors(specificInterceptors);
  │           proxyFactory.setProxyTargetClass(...);
  │           return proxyFactory.getProxy(classLoader);
  │
  └── 返回代理或原始 Bean
```

### 4.6 @AspectJ 注解切面处理流程

```
@Aspect 类: AnnotationAwareAspectJAutoProxyCreator 注册为 BeanPostProcessor

容器启动时:
  │
  ├── findCandidateAdvisors()
  │     │
  │     ├── 1. 容器中 Advisor 类型的 Bean → 直接收集
  │     │
  │     └── 2. 扫描 @Aspect 注解的 Bean:
  │           for (beanName : beanNames) {
  │             if (isAspect(beanType)) {
  │               advisors.addAll(
  │                 aspectJAdvisorFactory.getAdvisors(aspectInstanceFactory)
  │               )
  │             }
  │           }
  │
  └── AspectJAdvisorFactory.getAdvisors()
        │
        ├── 遍历 @Aspect 类中的所有方法 (排除 @Pointcut):
        │   ├── @Before        → AspectJMethodBeforeAdvice  → Advisor
        │   ├── @After          → AspectJAfterAdvice         → Advisor
        │   ├── @AfterReturning → AspectJAfterReturningAdvice→ Advisor
        │   ├── @AfterThrowing  → AspectJAfterThrowingAdvice → Advisor
        │   └── @Around         → AspectJAroundAdvice        → Advisor
        │
        └── 每个 Advisor 的 Pointcut:
              AspectJExpressionPointcut(pointcutExpression)
              └── 解析 AspectJ 表达式: execution(* com.example.*.*(..))
```

---

## 五、JDK vs CGLIB 代理对比

| | JDK 动态代理 | CGLIB 代理 |
|---|-------------|-----------|
| 代理方式 | `java.lang.reflect.Proxy` | `net.sf.cglib.proxy.Enhancer` (Spring 内嵌) |
| 要求 | 目标必须实现接口 | 目标类不能是 final，方法不能是 final |
| 性能 | 创建快，调用略慢（反射） | 创建慢（生成字节码），调用快 |
| 默认策略 | 有接口时使用 | `proxyTargetClass=true` 或无接口时使用 |
| Spring 类 | `JdkDynamicAopProxy` | `ObjenesisCglibAopProxy` |
| 序列化 | 需接口可序列化 | 可序列化（有特殊处理） |
| 代理数量 | 一个代理对象代理所有接口 | 一个代理对象代理一个类 |

---

## 六、内置 Advice 适配器

Advice 类型（Before、After 等）在拦截链中必须转为 AOP Alliance `MethodInterceptor`：

```
AdvisorAdapterRegistry
  │
  ├── MethodBeforeAdviceAdapter
  │     MethodBeforeAdvice → MethodBeforeAdviceInterceptor
  │       └── 先调用 advice.before()，再 proceed()
  │
  ├── AfterReturningAdviceAdapter
  │     AfterReturningAdvice → AfterReturningAdviceInterceptor
  │       └── 先 proceed() 获取返回值，再调用 advice.afterReturning()
  │
  └── ThrowsAdviceAdapter
        ThrowsAdvice → ThrowsAdviceInterceptor
          └── try { proceed() } catch → advice.afterThrowing()
```

---

## 七、关键类速查

| 类/接口 | 包 | 说明 |
|---------|-----|------|
| `Pointcut` | `aop` | 切点抽象 = ClassFilter + MethodMatcher |
| `Advisor` | `aop` | 切面抽象 = Advice 容器 |
| `Advice` (AOP Alliance) | `aopalliance.aop` | 通知标记接口 |
| `MethodInterceptor` | `aopalliance.intercept` | 环绕通知（拦截器） |
| `TargetSource` | `aop` | 目标对象来源（解耦目标获取） |
| `DefaultAopProxyFactory` | `framework` | 代理工厂（JDK vs CGLIB 决策） |
| `JdkDynamicAopProxy` | `framework` | JDK 动态代理实现 |
| `ObjenesisCglibAopProxy` | `framework` | CGLIB 代理实现 |
| `AdvisedSupport` | `framework` | 代理配置基类 |
| `ProxyFactory` | `framework` | 编程式代理工厂 |
| `ProxyFactoryBean` | `framework` | 声明式代理 FactoryBean |
| `ReflectiveMethodInvocation` | `framework` | 方法调用执行链 |
| `DefaultAdvisorChainFactory` | `framework` | 拦截器链工厂 |
| `AbstractAutoProxyCreator` | `autoproxy` | 自动代理 BeanPostProcessor |
| `AnnotationAwareAspectJAutoProxyCreator` | `aspectj.annotation` | @AspectJ 自动代理 |
| `AspectJExpressionPointcut` | `aspectj` | AspectJ 表达式切点 |
| `DefaultAdvisorAdapterRegistry` | `adapter` | Advice 适配器注册表 |

---

## 八、依赖关系

```
spring-aop
  ├── api: spring-beans
  ├── api: spring-core
  ├── compile: org.aopalliance:aopalliance (内嵌 fork)
  ├── optional: org.aspectj:aspectjweaver    (@AspectJ 支持)
  ├── optional: org.apache.commons:commons-pool2  (CommonsPool2TargetSource)
  └── optional: org.jetbrains.kotlinx:kotlinx-coroutines-reactor (Kotlin 协程)

---

## 九、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | IoC 基础设施 |
| 上游 | [spring-core](L1-spring-core.md) | L1 核心 | 反射、工具类 |
| 下游 | [spring-context](L4-spring-context.md) | L4 上下文 | @EnableAspectJAutoProxy 集成 |
| 下游 | [spring-aspects](L9-spring-aspects.md) | L9 辅助 | AspectJ 编译时/加载时织入 |
```
