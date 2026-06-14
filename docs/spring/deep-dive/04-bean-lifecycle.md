# Spring Bean 生命周期源码深度解析

> 本文深入分析 Spring IoC 容器中一个 Bean 从无到有的完整生命周期，覆盖 `AbstractAutowireCapableBeanFactory.doCreateBean()` 为核心的全部 15 个步骤。
> 相关模块文档：[spring-beans](../modules/L2-spring-beans.md)、[spring-context](../modules/L4-spring-context.md)

---

## 一、生命周期全景

```
                                               ┌──────────────────────┐
                                               │  1. 加载 BeanDefinition │
                                               │  (XML / @Bean / @Component) │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  2. 实例化前拦截       │
                                               │  InstantiationAwareBPP │
                                               │  .postProcessBefore-   │
                                               │  Instantiation()       │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  3. 实例化 Bean        │
                                               │  createBeanInstance()  │
                                               │  Supplier / Factory    │
                                               │  Method / Constructor  │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  4. 合并 BeanDefinition │
                                               │  applyMergedBeanDef-   │
                                               │  initionPostProcessors()│
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  5. 提前暴露 (循环依赖) │
                                               │  addSingletonFactory() │
                                               │  → ObjectFactory       │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  6. 属性填充            │
                                               │  populateBean()        │
                                               │  @Autowired / @Resource│
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  7. Aware 回调         │
                                               │  BeanNameAware         │
                                               │  BeanClassLoaderAware   │
                                               │  BeanFactoryAware       │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  8. BPP.postProcess-   │
                                               │  BeforeInitialization()│
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  9. 初始化方法          │
                                               │  @PostConstruct        │
                                               │  InitializingBean      │
                                               │  init-method            │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  10. BPP.postProcess-  │
                                               │  AfterInitialization() │
                                               │  ★ AOP 代理创建在此     │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  11. 注册销毁回调       │
                                               │  @PreDestroy           │
                                               │  DisposableBean        │
                                               │  destroy-method         │
                                               └──────────────────────┘
```

---

## 二、入口：getBean() 触发链路

```
DefaultListableBeanFactory.getBean(name)
  → AbstractBeanFactory.getBean(name)
    → doGetBean(name, requiredType, args, typeCheckOnly)
      → getSingleton(beanName)                 // ① 尝试从缓存获取
        → createBean(beanName, mbd, args)       // ② 缓存未命中 → 创建
          → doCreateBean(beanName, mbd, args)   // ③ ★ 核心创建方法
```

`doGetBean()` 是单例 Bean 获取的统一入口，其关键逻辑：

1. **转换 beanName**：去除 FactoryBean 的 `&` 前缀，解析别名
2. **检查单例缓存**：`getSingleton(beanName)` — 命中则直接返回（可能返回早期引用）
3. **处理 depends-on**：先创建依赖的 Bean
4. **Scope 分支**：Singleton → `createBean()`；Prototype → 每次新建；其他 → Scope 回调
5. **类型检查**：`requiredType.cast(bean)`

---

## 三、实例化：createBeanInstance()

`createBeanInstance()` 的优先级顺序：

### 3.1 Supplier 回调（优先级最高）

```java
// AbstractAutowireCapableBeanFactory.createBeanInstance()
Supplier<?> instanceSupplier = mbd.getInstanceSupplier();
if (instanceSupplier != null) {
    return obtainFromSupplier(instanceSupplier, beanName);
}
```

通过 `BeanDefinition.setInstanceSupplier(Supplier)` 或 `registerBean(name, supplier)` 设置，适用于函数式 Bean 注册。

### 3.2 工厂方法（@Bean 方法）

```java
if (mbd.getFactoryMethodName() != null) {
    return instantiateUsingFactoryMethod(beanName, mbd, args);
}
```

`@Bean` 注解的方法被封装为 `factoryMethodName` + `factoryBeanName`，由 `ConstructorResolver.instantiateUsingFactoryMethod()` 执行。

### 3.3 构造器自动装配

```java
Constructor<?>[] ctors = determineConstructorsFromBeanPostProcessors(beanClass, beanName);
if (ctors != null || mbd.getResolvedAutowireMode() == AUTOWIRE_CONSTRUCTOR || ...) {
    return autowireConstructor(beanName, mbd, ctors, args);
}
```

`AutowiredAnnotationBeanPostProcessor` 通过 `determineCandidateConstructors()` 确定候选构造器：
- 只有一个构造器 → 直接用
- 多个构造器 → 优先 `@Autowired(required=true)` 标记的
- 都没有 → 用无参构造器

### 3..4 默认构造器（兜底）

```java
return instantiateBean(beanName, mbd);
```

最终通过 `InstantiationStrategy.instantiate()`：
- **SimpleInstantiationStrategy**：`Constructor.newInstance(args)` (JDK 反射)
- **CglibSubclassingInstantiationStrategy**：通过 Objenesis 绕过无参构造器

---

## 四、提前暴露与循环依赖

实例化完成后，在属性填充**之前**，Bean 被包装为 `ObjectFactory` 放入三级缓存：

```java
// AbstractAutowireCapableBeanFactory.doCreateBean()
boolean earlySingletonExposure = (mbd.isSingleton() && this.allowCircularReferences &&
        isSingletonCurrentlyInCreation(beanName));
if (earlySingletonExposure) {
    addSingletonFactory(beanName, () -> getEarlyBeanReference(beanName, mbd, bean));
}
```

`getEarlyBeanReference()` 是关键——如果 Bean 需要 AOP 代理，这里会在属性填充前创建早期代理对象。

> 详见 [循环依赖深度解析](05-circular-dependency.md)

---

## 五、属性填充：populateBean()

`populateBean()` 按以下顺序执行：

### 5.1 InstantiationAwareBeanPostProcessor 拦截

```java
for (InstantiationAwareBeanPostProcessor bp : getBeanPostProcessorCache().instantiationAware) {
    if (!bp.postProcessAfterInstantiation(bw.getWrappedInstance(), beanName)) {
        return;  // 短路：不再填充属性
    }
}
```

### 5.2 按名称 / 按类型自动装配

```java
if (mbd.getResolvedAutowireMode() == AUTOWIRE_BY_NAME) {
    autowireByName(beanName, mbd, bw, newPvs);
}
if (mbd.getResolvedAutowireMode() == AUTOWIRE_BY_TYPE) {
    autowireByType(beanName, mbd, bw, newPvs);
}
```

### 5.3 注解驱动注入（@Autowired / @Resource）

```java
for (InstantiationAwareBeanPostProcessor bp : getBeanPostProcessorCache().instantiationAware) {
    PropertyValues pvsToUse = bp.postProcessProperties(pvs, bw.getWrappedInstance(), beanName);
    // AutowiredAnnotationBeanPostProcessor 在此处理 @Autowired
    // CommonAnnotationBeanPostProcessor 在此处理 @Resource
}
```

---

## 六、依赖注入解析链

当 `@Autowired` 注入一个依赖时，完整的解析链路：

```
AutowiredAnnotationBeanPostProcessor.inject()
  → DefaultListableBeanFactory.resolveDependency()
    → doResolveDependency()
      → findAutowireCandidates()
        → 按类型查找：getBeanNamesForType()
          → 按 @Qualifier 过滤
            → 候选选择：
              ① @Primary → 唯一 Primary Bean
              ② @Priority → 最高优先级
              ③ 单一匹配 → 直接使用
              ④ 多个匹配且无歧义解析 → 抛 NoUniqueBeanDefinitionException
```

---

## 七、初始化：initializeBean()

这是生命周期中最复杂的阶段，顺序执行 4 步：

### 7.1 Aware 接口回调

```java
private void invokeAwareMethods(String beanName, Object bean) {
    if (bean instanceof Aware) {
        if (bean instanceof BeanNameAware) {
            ((BeanNameAware) bean).setBeanName(beanName);
        }
        if (bean instanceof BeanClassLoaderAware) {
            ((BeanClassLoaderAware) bean).setBeanClassLoader(getBeanClassLoader());
        }
        if (bean instanceof BeanFactoryAware) {
            ((BeanFactoryAware) bean).setBeanFactory(AbstractAutowireCapableBeanFactory.this);
        }
    }
}
```

**Aware 接口大全**：

| Aware 接口 | 注入内容 | 调用者 |
|-----------|---------|--------|
| `BeanNameAware` | `beanName` | `invokeAwareMethods()` |
| `BeanClassLoaderAware` | `ClassLoader` | `invokeAwareMethods()` |
| `BeanFactoryAware` | `BeanFactory` | `invokeAwareMethods()` |
| `ApplicationContextAware` | `ApplicationContext` | `ApplicationContextAwareProcessor` |
| `EnvironmentAware` | `Environment` | `ApplicationContextAwareProcessor` |
| `ResourceLoaderAware` | `ResourceLoader` | `ApplicationContextAwareProcessor` |
| `ApplicationEventPublisherAware` | `ApplicationEventPublisher` | `ApplicationContextAwareProcessor` |
| `MessageSourceAware` | `MessageSource` | `ApplicationContextAwareProcessor` |
| `ServletContextAware` | `ServletContext` | `ServletContextAwareProcessor` |

> 注意：`ApplicationContextAware` 等是在 `ApplicationContextAwareProcessor.postProcessBeforeInitialization()` 中回调的，而非 `invokeAwareMethods()`。

### 7.2 BeanPostProcessor.postProcessBeforeInitialization()

```java
public Object applyBeanPostProcessorsBeforeInitialization(Object existingBean, String beanName) {
    Object result = existingBean;
    for (BeanPostProcessor processor : getBeanPostProcessors()) {
        Object current = processor.postProcessBeforeInitialization(result, beanName);
        if (current == null) return result;
        result = current;
    }
    return result;
}
```

这步的主要作用：
- `ApplicationContextAwareProcessor`：注入 `ApplicationContext` 等 Aware
- `CommonAnnotationBeanPostProcessor`：处理 `@PostConstruct`
- 用户自定义的 `BeanPostProcessor`：前置处理

### 7.3 初始化方法执行

初始化方法的执行优先级：

```
① @PostConstruct 方法 (在 CommonAnnotationBeanPostProcessor 中，步骤 7.2 执行)
② InitializingBean.afterPropertiesSet() 接口方法
③ init-method (XML 或 @Bean(initMethod = "xxx"))
```

```java
protected void invokeInitMethods(String beanName, Object bean, @Nullable RootBeanDefinition mbd) {
    // 1. InitializingBean 接口
    boolean isInitializingBean = (bean instanceof InitializingBean);
    if (isInitializingBean) {
        ((InitializingBean) bean).afterPropertiesSet();
    }
    // 2. 自定义 init-method
    if (mbd != null && bean.getClass() != NullBean.class) {
        String initMethodName = mbd.getInitMethodName();
        if (StringUtils.hasLength(initMethodName) &&
                !(isInitializingBean && "afterPropertiesSet".equals(initMethodName))) {
            invokeCustomInitMethod(beanName, bean, mbd);
        }
    }
}
```

### 7.4 BeanPostProcessor.postProcessAfterInitialization()

**这是 AOP 代理创建的关键时机：**

```java
public Object applyBeanPostProcessorsAfterInitialization(Object existingBean, String beanName) {
    Object result = existingBean;
    for (BeanPostProcessor processor : getBeanPostProcessors()) {
        Object current = processor.postProcessAfterInitialization(result, beanName);
        if (current == null) return result;
        result = current;
    }
    return result;
}
```

`AbstractAutoProxyCreator.postProcessAfterInitialization()` 在此检查 Bean 是否匹配任何 Advisor，匹配则创建代理对象。

---

## 八、销毁阶段

容器关闭时，`destroyBeans()` 触发：

```
Bean 销毁顺序:
  ① @PreDestroy 方法
  ② DisposableBean.destroy() 接口方法
  ③ destroy-method (XML 或 @Bean(destroyMethod = "xxx"))
```

生命周期方法对比：

| | @PostConstruct / @PreDestroy | InitializingBean / DisposableBean | init-method / destroy-method |
|---|---|---|---|
| 标准 | JSR-250 (Jakarta) | Spring 专属 | Spring XML / @Bean |
| 侵入性 | 注解（低） | 接口（高，耦合 Spring） | XML / 注解（低） |
| 优先级 | 最高（7.2 执行） | 中（7.3 执行） | 最低（7.3 执行） |

---

## 九、完整时序总结

| 步骤 | 方法 | 关键内容 |
|------|------|---------|
| 1 | `loadBeanDefinitions()` | 解析 XML / @Configuration / @ComponentScan |
| 2 | `postProcessBeforeInstantiation()` | 可提前返回代理对象 |
| 3 | `createBeanInstance()` | Supplier → FactoryMethod → Constructor → 默认构造器 |
| 4 | `applyMergedBeanDefinitionPostProcessors()` | 解析 @Autowired / @Resource 元数据 |
| 5 | `addSingletonFactory()` | 三级缓存提前曝光（循环依赖） |
| 6 | `populateBean()` | @Autowired / @Resource 注入 |
| 7 | `invokeAwareMethods()` | BeanName → ClassLoader → BeanFactory Aware |
| 8 | `postProcessBeforeInitialization()` | @PostConstruct 在此执行 |
| 9 | `invokeInitMethods()` | InitializingBean + init-method |
| 10 | `postProcessAfterInitialization()` | **AOP 代理创建** |
| 11 | `registerDisposableBeanIfNecessary()` | 注册 @PreDestroy / destroy 回调 |

---

## 十、相关文档

| 文档 | 说明 |
|------|------|
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanFactory、DI、BeanPostProcessor |
| [spring-context 模块文档](../modules/L4-spring-context.md) | ApplicationContext、refresh() 生命周期 |
| [循环依赖深度解析](05-circular-dependency.md) | 三级缓存机制详解 |
| [依赖注入深度解析](06-dependency-injection.md) | @Autowired 注入链路 |
| [AOP 实现深度解析](12-aop-implementation.md) | 代理创建 + 拦截器链 |
