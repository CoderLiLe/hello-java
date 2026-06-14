# Spring AOP 实现源码深度解析

> 本文深入分析 Spring AOP 的代理创建决策、拦截器链执行、@AspectJ 注解处理以及 CGLIB vs JDK 代理的差异。
> 相关模块文档：[spring-aop](../modules/L3-spring-aop.md)、[spring-beans](../modules/L2-spring-beans.md)

---

## 一、AOP 核心概念关系

```
    ┌──────────────┐         ┌──────────────┐
    │   Pointcut   │         │    Advice    │
    │  (哪里切)    │         │   (做什么)   │
    │              │         │              │
    │ ClassFilter  │         │ BeforeAdvice │
    │ MethodMatcher│         │ AfterReturn- │
    │              │         │ ingAdvice    │
    └──────┬───────┘         │ ThrowsAdvice │
           │                 │ AroundAdvice │
           └────────┬────────┴──────┬───────┘
                    │               │
            ┌───────▼───────────────▼───────┐
            │          Advisor              │
            │  PointcutAdvisor              │
            │   = Pointcut + Advice          │
            └───────────────┬───────────────┘
                            │
            ┌───────────────▼───────────────┐
            │        ProxyFactory           │
            │  TargetSource + Advisor[]      │
            │  → createAopProxy()            │
            └───────────────┬───────────────┘
                            │
            ┌───────────────▼───────────────┐
            │         AopProxy              │
            │  JdkDynamicAopProxy           │
            │  或 CglibAopProxy              │
            └───────────────────────────────┘
```

---

## 二、代理创建决策流程

### 2.1 DefaultAopProxyFactory.createAopProxy()

```java
public AopProxy createAopProxy(AdvisedSupport config) throws AopConfigException {
    if (!NativeDetector.inNativeImage() &&
            (config.isOptimize() || config.isProxyTargetClass() 
             || hasNoUserSuppliedInterfaces(config))) {
        Class<?> targetClass = config.getTargetClass();
        if (targetClass == null) {
            throw new AopConfigException("...");
        }
        // 即使配置了 CGLIB，以下情况也使用 JDK 代理
        if (targetClass.isInterface() || Proxy.isProxyClass(targetClass)) {
            return new JdkDynamicAopProxy(config);
        }
        // Lambda 类也用 JDK 代理
        if (ClassUtils.isLambdaClass(targetClass)) {
            return new JdkDynamicAopProxy(config);
        }
        // ★ CGLIB 代理
        return new ObjenesisCglibAopProxy(config);
    }
    // 默认：JDK 动态代理
    return new JdkDynamicAopProxy(config);
}
```

### 2.2 决策树

```
目标类有接口吗？
  ├─ YES → JdkDynamicAopProxy (默认)
  │         例外：proxyTargetClass=true → CGLIB
  │
  └─ NO  → CGLIB (必须)
              例外：target 是接口 / 已是 JDK 代理 / Lambda → JDK

最终：
  ┌─────────────────────────────────────┐
  │ @EnableAspectJAutoProxy             │
  │ proxyTargetClass=false (默认)        │
  │   → 有接口：JDK 代理                │
  │   → 无接口：CGLIB 代理              │
  │                                     │
  │ @EnableAspectJAutoProxy             │
  │ proxyTargetClass=true               │
  │   → 非接口/非JDK代理/非Lambda：CGLIB │
  │   → 接口/JDK代理/Lambda：JDK        │
  └─────────────────────────────────────┘
```

---

## 三、JDK 动态代理实现

### 3.1 JdkDynamicAopProxy 结构

```java
final class JdkDynamicAopProxy implements AopProxy, InvocationHandler, Serializable {
    
    private final AdvisedSupport advised;  // 代理配置
    
    @Override
    public Object getProxy(@Nullable ClassLoader classLoader) {
        Class<?>[] proxiedInterfaces = 
            AopProxyUtils.completeProxiedInterfaces(this.advised, true);
        return Proxy.newProxyInstance(classLoader, proxiedInterfaces, this);
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) {
        // ★ 核心拦截逻辑
    }
}
```

### 3.2 invoke() 方法核心流程

```
invoke(proxy, method, args)
  │
  ├── ① equals() / hashCode() 处理 → 比较代理对象
  │
  ├── ② Advised 接口方法 → 委托给 advised (AdvisedSupport)
  │     ├── getTargetSource()
  │     ├── getAdvisors()
  │     └── ...
  │
  ├── ③ DecoratingProxy.getDecoratedClass() → 返回目标类
  │
  ├── ④ 获取拦截器链
  │     List<Object> chain = advised.getInterceptorsAndDynamicInterceptionAdvice(method, targetClass)
  │     │
  │     └── DefaultAdvisorChainFactory.getInterceptorsAndDynamicInterceptionAdvice()
  │           ├── 遍历所有 Advisor
  │           ├── Pointcut.match(method, targetClass)?
  │           │   ├── static match → Interceptor
  │           │   └── dynamic match → InterceptorAndDynamicMethodMatcher
  │           └── Advice → 适配为 MethodInterceptor
  │
  ├── ⑤ 链为空且方法非 public → 直接反射调用
  │
  └── ⑥ ★ 创建 ReflectiveMethodInvocation 并执行拦截器链
        ReflectiveMethodInvocation invocation = new ReflectiveMethodInvocation(
            proxy, target, method, args, targetClass, chain);
        retVal = invocation.proceed();
```

---

## 四、拦截器链执行机制

### 4.1 ReflectiveMethodInvocation.proceed()

```java
public Object proceed() throws Throwable {
    // currentInterceptorIndex 从 -1 开始，每次 +1
    if (this.currentInterceptorIndex == this.interceptorsAndDynamicMethodMatchers.size() - 1) {
        // ★ 链末尾 → 调用目标方法
        return invokeJoinpoint();
    }
    Object interceptorOrInterceptionAdvice =
        this.interceptorsAndDynamicMethodMatchers.get(++this.currentInterceptorIndex);
    
    // 动态匹配检查
    if (interceptorOrInterceptionAdvice instanceof InterceptorAndDynamicMethodMatcher dm) {
        if (dm.methodMatcher.matches(this.method, this.targetClass, this.arguments)) {
            return dm.interceptor.invoke(this);
        } else {
            // 不匹配 → 跳过，继续下一节点
            return proceed();
        }
    } else {
        // ★ 静态匹配 → 调用拦截器，传入 this (链)
        return ((MethodInterceptor) interceptorOrInterceptionAdvice).invoke(this);
    }
}
```

### 4.2 责任链执行示意图

```
interceptor[0]: MethodBeforeAdviceInterceptor
  ├── advice.before(method, args, target)     // 前置通知
  └── mi.proceed() ───────────────────────┐
                                           │
interceptor[1]: ThrowsAdviceInterceptor     │
  ├── try {                                │
  │     mi.proceed() ───────────────┐      │
  │   } catch(ex) {                  │      │
  │     advice.afterThrowing(ex)     │      │
  │   }                              │      │
  └──────────────────────────────────┤      │
                                      │      │
interceptor[2]: AfterReturningAdviceInt.    │
  ├── retVal = mi.proceed() ────┐    │      │
  ├── advice.afterReturning(retVal) │    │      │
  └── return retVal                 │    │      │
                                    │    │      │
                                    ▼    ▼      ▼
                    invokeJoinpoint(): method.invoke(target, args)
```

### 4.3 Advice 适配为 MethodInterceptor

Spring AOP 的通知类型最终都适配为 AOP Alliance `MethodInterceptor`：

```
AdvisorAdapterRegistry.registerAdvisorAdapter():
  
  MethodBeforeAdvice ──→ MethodBeforeAdviceAdapter ──→ MethodBeforeAdviceInterceptor
    before()                                              invoke():
                                                          ① before()
                                                          ② mi.proceed()
  
  AfterReturningAdvice → AfterReturningAdviceAdapter → AfterReturningAdviceInterceptor
    afterReturning()                                      invoke():
                                                          ① retVal = mi.proceed()
                                                          ② afterReturning(retVal)
                                                          ③ return retVal
  
  ThrowsAdvice ────────→ ThrowsAdviceAdapter ────────→ ThrowsAdviceInterceptor
    afterThrowing()                                       invoke():
                                                          ① try { mi.proceed() }
                                                          ② catch → afterThrowing()
  
  MethodInterceptor (原生) → 直接使用 (无需适配)
```

---

## 五、@AspectJ 注解处理全链路

### 5.1 启动：扫描 @Aspect Bean

```
@EnableAspectJAutoProxy
  → @Import(AspectJAutoProxyRegistrar)
    → 注册 AnnotationAwareAspectJAutoProxyCreator (BeanPostProcessor)

容器 refresh():
  → registerBeanPostProcessors()
    → AnnotationAwareAspectJAutoProxyCreator 被注册

findCandidateAdvisors():
  ├── ① 容器中 Advisor 类型的 Bean → 直接收集
  │
  └── ② 扫描所有 @Aspect 注解的 Bean
        for each @Aspect bean:
          advisors.addAll(
            aspectJAdvisorFactory.getAdvisors(aspectInstanceFactory)
          )
```

### 5.2 解析 @Aspect → Advisor 列表

```
ReflectiveAspectJAdvisorFactory.getAdvisors(aspectInstanceFactory)
  │
  ├── 遍历 @Aspect 类中所有方法 (排除 @Pointcut 注解的方法)
  │
  ├── @Before → new AspectJMethodBeforeAdvice(method, pointcut, factory)
  │              → new InstantiationModelAwarePointcutAdvisorImpl(pointcut, advice)
  │
  ├── @After  → new AspectJAfterAdvice(...)
  │              → Advisor
  │
  ├── @AfterReturning → new AspectJAfterReturningAdvice(...)
  │              → Advisor
  │
  ├── @AfterThrowing  → new AspectJAfterThrowingAdvice(...)
  │              → Advisor
  │
  └── @Around  → new AspectJAroundAdvice(...)
                   → Advisor
  
每个 Advisor 的 Pointcut 都是 AspectJExpressionPointcut:
  "execution(* com.example.service.*.*(..))"
```

### 5.3 代理创建：匹配判断

```
AbstractAutoProxyCreator.wrapIfNecessary(bean, beanName, cacheKey)
  │
  ├── ① 已处理过？→ 从 earlyProxyReferences 检查
  ├── ② 基础设施类？→ isInfrastructureClass() — 跳过
  ├── ③ shouldSkip？→ 跳过 TargetSource 目标对象等
  │
  ├── ④ getAdvicesAndAdvisorsForBean(beanClass, beanName, targetSource)
  │     └── findEligibleAdvisors(beanClass, beanName)
  │           ├── findCandidateAdvisors() → 所有 Advisor
  │           └── findAdvisorsThatCanApply(candidateAdvisors, beanClass)
  │                 └── AopUtils.canApply(advisor, targetClass)
  │                       ├── pointcut.getClassFilter().matches(targetClass) ?
  │                       └── pointcut.getMethodMatcher().matches(method, targetClass) ?
  │
  └── ⑤ 有匹配的 Advisor → ProxyFactory.getProxy()
```

---

## 六、CGLIB 代理实现

### 6.1 CglibAopProxy 核心结构

```java
class CglibAopProxy implements AopProxy, Serializable {
    
    @Override
    public Object getProxy(@Nullable ClassLoader classLoader) {
        Enhancer enhancer = createEnhancer();
        enhancer.setSuperclass(proxySuperClass);
        enhancer.setInterfaces(AopProxyUtils.completeProxiedInterfaces(this.advised));
        enhancer.setCallbackFilter(proxyCallbackFilter);
        enhancer.setCallbacks(callbacks);
        return enhancer.create();
    }
}
```

### 6.2 回调链

```
CGLIB 代理的回调类型:
  
  DynamicAdvisedInterceptor (AOP Alliance MethodInterceptor)
    └── intercept(proxy, method, args, methodProxy)
          └── CglibMethodInvocation.proceed()
                └── 与 JDK 代理相同的 ReflectiveMethodInvocation 链逻辑
  
  TargetInterceptor (直接调用目标方法，无 AOP)
    └── 用于被排除的 Advisor 自身方法
  
  EqualsInterceptor / HashCodeInterceptor
    └── equals/hashCode 特殊处理
```

### 6.3 Objenesis 实例化

```java
class ObjenesisCglibAopProxy extends CglibAopProxy {
    @Override
    protected Object createProxyClassAndInstance(Enhancer enhancer, Callback[] callbacks) {
        Class<?> proxyClass = enhancer.createClass();
        // 通过 Objenesis 绕过无参构造器要求
        return objenesis.newInstance(proxyClass);
    }
}
```

---

## 七、JDK vs CGLIB 对比

| 维度 | JDK 动态代理 | CGLIB 代理 |
|------|-------------|-----------|
| **机制** | `java.lang.reflect.Proxy` | ASM 字节码生成子类 |
| **要求** | 目标必须实现接口 | 目标类/方法不能是 final |
| **创建开销** | 低（直接生成） | 高（字节码生成） |
| **调用开销** | 中（反射 invoke） | 低（直接方法调用） |
| **代理类型** | 一个代理实现所有接口 | 一个代理对应一个类 |
| **this 自调用** | 不拦截（代理内部的 this 指向目标） | 不拦截 |
| **默认策略** | `proxyTargetClass=false` 且有接口 | `proxyTargetClass=true` 或无接口 |
| **final 方法** | 无限制 | 不可代理 |

### this 自调用问题

```java
@Service
public class UserService {
    @Transactional
    public void doSomething() {
        // this.doSomethingElse() 不会触发事务!
        // this 是原始对象，不是代理对象
        this.doSomethingElse();
    }
    
    @Transactional
    public void doSomethingElse() { ... }
}
```

解决方案：
```java
// 1. 注入自身代理
@Autowired
private UserService self;
self.doSomethingElse();

// 2. AopContext.currentProxy()
((UserService) AopContext.currentProxy()).doSomethingElse();

// 3. 提取到另一个 Bean
```

---

## 八、关键扩展点

| 扩展点 | 接口 | 用途 |
|--------|------|------|
| 代理创建前 | `InstantiationAwareBeanPostProcessor.postProcessBeforeInstantiation()` | 提前返回代理对象 |
| 早期引用 | `SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference()` | 循环依赖中的早期代理 |
| 初始化后 | `BeanPostProcessor.postProcessAfterInitialization()` | 正常代理创建 |
| 通知顺序 | `Ordered` / `@Order` | 控制 Advisor 执行顺序 |

---

## 九、相关文档

| 文档 | 说明 |
|------|------|
| [spring-aop 模块文档](../modules/L3-spring-aop.md) | AOP 模块完整参考 |
| [Bean 生命周期深度解析](04-bean-lifecycle.md) | 代理创建时机 |
| [循环依赖深度解析](05-circular-dependency.md) | earlyProxyReferences 机制 |
| [事务实现深度解析](13-transaction-implementation.md) | @Transactional AOP 拦截器 |
