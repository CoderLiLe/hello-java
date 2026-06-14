# Spring 依赖注入源码深度解析

> 本文深入分析 Spring 依赖注入的完整链路，覆盖 @Autowired 解析、注入候选查找、构造器/字段/方法注入、@Qualifier/@Primary/@Priority 歧义消解、以及 populateBean() 全流程。
> 相关模块文档：[spring-beans](../modules/L2-spring-beans.md)、[spring-context](../modules/L4-spring-context.md)

---

## 一、注入体系概览

```
Spring DI 的三种注入方式:

┌─────────────────────────────────────────────────────────┐
│ ① 构造器注入 (Constructor Injection)                    │
│    @Autowired on constructor → determineConstructors    │
│    推荐方式: 不可变、易测试、编译器友好                   │
├─────────────────────────────────────────────────────────┤
│ ② 字段注入 (Field Injection)                            │
│    @Autowired on field → postProcessProperties          │
│    简洁但不利于单测、隐藏依赖                             │
├─────────────────────────────────────────────────────────┤
│ ③ Setter 注入 (Setter Injection)                        │
│    @Autowired on setter → postProcessProperties         │
│    可选依赖、可重配置                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 二、@Autowired 元数据解析

### 2.1 解析入口: MergedBeanDefinitionPostProcessor

```
AutowiredAnnotationBeanPostProcessor:
  同时实现:
    - MergedBeanDefinitionPostProcessor    ← 解析阶段
    - InstantiationAwareBeanPostProcessor  ← 注入阶段
    - SmartInstantiationAwareBeanPostProcessor ← 构造器解析
    - BeanFactoryAware
```

### 2.2 postProcessMergedBeanDefinition() — 元数据收集

```
postProcessMergedBeanDefinition(mbd, beanType, beanName):
  │
  ├── 遍历 beanClass 的所有字段和方法
  │
  ├── findAutowiredAnnotation(field/method):
  │     @Autowired  (spring-beans)
  │     @Value       (spring-beans)
  │     @Inject      (jakarta.inject, 如果存在)
  │
  ├── 对于字段:
  │     → 创建 AutowiredFieldElement(field, required)
  │     → 加入 InjectionMetadata.injectedFields
  │
  └── 对于方法:
        → 创建 AutowiredMethodElement(method, required)
        → 加入 InjectionMetadata.injectedMethods

结果: InjectionMetadata { injectedFields, injectedMethods }
      缓存到 injectionMetadataCache (ConcurrentHashMap<Class<?>, InjectionMetadata>)
```

### 2.3 determineConstructors() — 构造器选择

```
determineConstructorsFromBeanPostProcessors(beanClass, beanName):
  │
  └── AutowiredAnnotationBeanPostProcessor.determineCandidateConstructors(beanClass, beanName):
        │
        ├── 首先检查 lookup-methods (CGLIB) → 返回 null (使用默认构造器)
        │
        ├── 查找 @Autowired 标记的构造器:
        │     ├── 0 个 @Autowired → 使用默认无参构造器 (含 Kotlin primary ctor)
        │     ├── 1 个 @Autowired(required=true) → 返回此构造器
        │     ├── 1 个 @Autowired(required=false) → 构造器列表 + 默认构造器(兜底)
        │     └── 多个 @Autowired(required=false) → 所有候选构造器列表
        │
        └── 返回: Constructor<?>[] 或 null (表示使用默认无参构造器)
```

---

## 三、构造器注入 — autowireConstructor()

### 3.1 流程概览

```
AbstractAutowireCapableBeanFactory.autowireConstructor(beanName, mbd, ctors, args):
  │
  ├── ① ConstructorResolver.autowireConstructor(beanName, mbd, ctors, args):
  │     │
  │     ├── 确定候选构造器: ctors != null ? ctors : beanClass.getDeclaredConstructors()
  │     │
  │     ├── 对每个构造器:
  │     │   ├── 检查参数数量 (minNrOfArgs 过滤)
  │     │   ├── 解析每个参数的 Bean:
  │     │   │     └── resolveAutowiredArgument(param, beanName, autowiredBeanNames, ...)
  │     │   │           └── DefaultListableBeanFactory.resolveDependency(descriptor, ...)
  │     │   │                 └── 见 §六 依赖解析链路
  │     │   └── 构造器类型匹配度评分:
  │     │         ├── 精确匹配 > 父类匹配 > 接口匹配
  │     │         └── 宽松模式: 选择 "最贪婪" 的构造器 (参数最多的)
  │     │
  │     └── 依据评分选择最佳构造器 → instantiate(beanName, mbd, chosenCtor, resolvedArgs)
  │
  └── ② 实例化: Constructor.newInstance(resolvedArgs)
```

### 3.2 参数名发现

```
ParameterNameDiscoverer 链式发现:

① StandardReflectionParameterNameDiscoverer  — 反射获取 (编译参数 -parameters)
② KotlinReflectionParameterNameDiscoverer    — Kotlin 编译器
③ LocalVariableTableParameterNameDiscoverer  — 字节码 LocalVariableTable 读取
   └── ASM ClassReader 读取 .class 文件
```

---

## 四、字段/Setter 注入 — populateBean()

### 4.1 populateBean() 完整顺序

```
AbstractAutowireCapableBeanFactory.populateBean(beanName, mbd, bw):
  │
  ├── ① InstantiationAwareBeanPostProcessor.postProcessAfterInstantiation():
  │     如果返回 false → 直接 return (短路, 不填充任何属性)
  │
  ├── ② autowireByName / autowireByType (XML 自动装配, 已过时)
  │     └── 仅当 mbd.getResolvedAutowireMode() == AUTOWIRE_BY_NAME/BY_TYPE
  │
  ├── ③ ★ InstantiationAwareBeanPostProcessor.postProcessProperties():
  │     │
  │     └── AutowiredAnnotationBeanPostProcessor.postProcessProperties():
  │           │
  │           ├── findInjectionMetadata(beanName, beanClass, pvs)
  │           │     └── 从缓存读取 InjectionMetadata (在 §2.2 中收集的)
  │           │
  │           ├── metadata.inject(bean, beanName, pvs):
  │           │     │
  │           │     ├── 注入字段 (AutowiredFieldElement):
  │           │     │     for each field:
  │           │     │       field.setAccessible(true)
  │           │     │       value = resolveFieldValue(field, bean, beanName)
  │           │     │         └── resolveDependency(descriptor, beanName, autowiredBeanNames, typeConverter)
  │           │     │       field.set(bean, value)
  │           │     │
  │           │     └── 注入方法 (AutowiredMethodElement):
  │           │           for each method:
  │           │             args = resolveMethodArguments(method, bean, beanName)
  │           │               └── resolveDependency() × N 参数
  │           │             method.invoke(bean, args)
  │           │
  │           └── CommonAnnotationBeanPostProcessor.postProcessProperties():
  │                 └── 处理 @Resource 注入 (按名查找)
  │
  └── ④ applyPropertyValues(beanName, mbd, bw, pvs):
        └── XML <property> 注入 (已过时方式)
```

---

## 五、依赖解析核心链路 — resolveDependency()

### 5.1 总体流程

```
DefaultListableBeanFactory.resolveDependency(descriptor, requestingBeanName, autowiredBeanNames, typeConverter):
  │
  ├── ① descriptor 有 @Value 注解? → resolveValue(descriptor)
  │
  ├── ② 特殊类型处理:
  │     ├── Optional<T>    → resolveOptionalDependency()
  │     ├── ObjectFactory<T>, ObjectProvider<T> → new DependencyObjectProvider(descriptor)
  │     ├── jakarta.inject.Provider<T> → new DependencyObjectProvider(descriptor)
  │     └── lazy @Autowired → new TargetSource 包装的代理 (ContextAnnotationAutowireCandidateResolver)
  │
  ├── ③ 多个候选 Bean 匹配:
  │     └── doResolveMultipleBeans(descriptor, beanName, autowiredBeanNames, typeConverter)
  │           ├── 需要按类型匹配 → findAutowireCandidates(beanName, type, descriptor)
  │           └── 如果注入的是 Collection/Map → 全部返回
  │
  └── ④ 返回
```

### 5.2 findAutowireCandidates() — 候选查找

```
findAutowireCandidates(beanName, requiredType, descriptor):
  │
  ├── ① 按类型匹配: getBeanNamesForType(requiredType, includeNonSingletons, allowEagerInit)
  │     返回: 符合条件的 beanName 列表
  │
  ├── ② 对每个 candidateBeanName:
  │     ├── isAutowireCandidate(candidateBeanName, descriptor)?
  │     │     └── isAutowireCandidate():
  │     │           ├── 检查 BeanDefinition.autowireCandidate 属性
  │     │           ├── 检查 descriptor 上的 @Qualifier
  │     │           └── 检查泛型匹配 (ResolvableType)
  │     └── YES → 添加到 result Map
  │
  ├── ③ 处理 fallback 匹配 (父类/接口不匹配时的备选):
  │     └── 宽松匹配 → 工厂方法返回类型, 泛型解析等
  │
  └── ④ 返回 result: Map<String, Object> (beanName → bean instance 或 Class)
```

### 5.3 歧义消解 — determineAutowireCandidate()

```
determineAutowireCandidate(matchingBeans, descriptor):
  │
  ├── ① @Primary 检查:
  │     for each candidateBeanName:
  │       if (isPrimary(candidateBeanName, beanInstance)):
  │         primaryCount++
  │         primaryBeanName = candidateBeanName
  │     if (primaryCount == 1) → return primaryBeanName  ← ★ 唯一 @Primary 胜出
  │
  ├── ② @Priority 检查:
  │     for each candidateBeanName:
  │       priority = getPriority(beanInstance)
  │     return 最高优先级的 beanName        ← ★ @Priority 值小的优先
  │
  ├── ③ 按 name 匹配 (fallback):
  │     如果候选 beanName 中有与 descriptor.getDependencyName() 相等的 → 返回
  │
  └── ④ 无解 → throw NoUniqueBeanDefinitionException:
        "expected single matching bean but found 2: bean1, bean2"
```

---

## 六、@Qualifier 与 @Primary 详解

### 6.1 @Qualifier 机制

```
注入点: @Autowired @Qualifier("orderA") OrderService service;

resolveDependency():
  → findAutowireCandidates():
      → isAutowireCandidate(beanName, descriptor):
          → QualifierAnnotationAutowireCandidateResolver.isAutowireCandidate():
              │
              ├── 检查 Bean 的 qualifier 注解 (type-level):
              │     @Qualifier("orderA") on Bean class = qualifier value "orderA"
              │     @Qualifier 在自定义注解上也可识别 (meta-annotation)
              │
              └── 检查提供此 Bean 的 @Bean 方法上的 @Qualifier 注解

匹配逻辑:
  @Qualifier("orderA") on injection point  ←→  @Qualifier("orderA") on bean definition
  值相等 → 选中
```

### 6.2 自定义 Qualifier 注解

```java
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Qualifier
public @interface DataSourceType {
    String value();
}

// 注入端
@Autowired @DataSourceType("read") DataSource dataSource;

// 定义端
@Bean @DataSourceType("read") DataSource readDataSource() { ... }
@Bean @DataSourceType("write") DataSource writeDataSource() { ... }
```

---

## 七、@Resource 注入 (JSR-250)

### 7.1 与 @Autowired 的差异

```
@Autowired (Spring):
  ├── 默认按类型 (byType) 注入
  ├── 配合 @Qualifier → 按类型 + 限定符
  └── AutowiredAnnotationBeanPostProcessor 处理

@Resource (JSR-250 / Jakarta):
  ├── 默认按名称 (byName) 注入
  │     ├── @Resource(name="beanName") → 直接按名查找
  │     └── @Resource (无 name) → 字段名作为 bean name
  ├── 按名查找失败 → 退回到按类型查找
  └── CommonAnnotationBeanPostProcessor 处理
```

### 7.2 @Resource 解析流程

```
CommonAnnotationBeanPostProcessor.ResourceElement.inject():
  │
  ├── ① 确定 beanName:
  │     ├── @Resource(name = "xxx") → beanName = "xxx"
  │     └── @Resource (无 name)     → beanName = 字段名 / setter 属性名
  │
  ├── ② getBean(beanName, requiredType):
  │     ├── 缓存中有 → 直接返回
  │     └── 缓存无 → 按名查找
  │
  └── ③ 按名查找失败 → 按类型查找 (fallback to @Autowired behavior)
```

---

## 八、@Value 注入

### 8.1 处理流程

```
AutowiredAnnotationBeanPostProcessor 同时处理 @Value:

resolveFieldValue(field, bean, beanName):
  ├── 检查是否 @Value 注解:
  │     └── YES → resolveValue(descriptor)
  │
  └── resolveValue(descriptor):
        ├── 获取 value expression: @Value("${app.name}")
        │
        ├── StringValueResolver 链式解析:
        │     ├── PropertySourcesPlaceholderConfigurer: 解析 ${...} 占位符
        │     │     └── environment.resolvePlaceholders(value)
        │     └── EmbeddedValueResolver: 解析 #{...} SpEL 表达式
        │
        ├── TypeConverter 类型转换: String → int, long, boolean ...
        │
        └── 返回最终值
```

### 8.2 占位符解析链

```
@Value("${app.name:default}")
  │
  ├── PropertySourcesPlaceholderConfigurer.postProcessBeanFactory()
  │     └── 注册 StringValueResolver 到 EmbeddedValueResolver
  │
  └── 注入时:
        EmbeddedValueResolver.resolveStringValue(placeholder)
          └── PropertyPlaceholderHelper.replacePlaceholders(value, placeholderResolver)
                ├── 查找 key "app.name"
                │     └── environment.resolveRequiredPlaceholders("${app.name}")
                │           └── MutablePropertySources 链式查找
                │                 ① systemProperties
                │                 ② systemEnvironment
                │                 ③ application.properties
                │                 ④ ...
                ├── 未找到 key → 使用默认值 ":default"
                └── 未找到且无默认值 → throw IllegalArgumentException
```

---

## 九、@Lazy 注入

### 9.1 代理对象生成

```
@Autowired @Lazy SomeBean bean;  // 注入的是代理对象, 而非真实 Bean

resolveDependency():
  → ContextAnnotationAutowireCandidateResolver.getLazyResolutionProxyIfNecessary():
      │
      ├── 检查 descriptor 是否有 @Lazy 注解 (字段/方法参数/方法)
      │
      └── YES → 创建代理对象:
            ProxyFactory.createLazyInitProxy(descriptor, beanName)
              ├── 使用 JdkDynamicAopProxy (需要接口)
              │   └── TargetSource:
              │         在首次方法调用时 → beanFactory.getBean(beanName)
              │
              └── 无接口 → CGLIB 代理
                    └── 同上
```

### 9.2 @Lazy + 构造器注入打破循环依赖

```
@Component
class A {
    B b;
    A(@Autowired @Lazy B b) { this.b = b; }  // 注入代理
}

@Component
class B {
    A a;
    B(@Autowired A a) { this.a = a; }
}

流程:
  new A() → 注入 B 代理 (不用真正创建 B) → A 完成
  new B() → 注入 A (A 已完成, 从一级缓存取) → B 完成
  → B 代理 → getBean("b") → 返回已完成 B
```

---

## 十、@Lookup 方法注入

### 10.1 使用场景

当单例 Bean 需要每次获取一个原型 Bean 时，直接 `@Autowired` 注入只会注入一次。`@Lookup` 使 Spring 通过 CGLIB 生成代理，每次调用方法都从容器获取新的原型实例。

```java
@Component
public abstract class UserService {
    // 每次调用 createOrderService() 都返回新的 OrderService (prototype)
    @Lookup
    public abstract OrderService createOrderService();
}

@Component
@Scope("prototype")
public class OrderService { ... }
```

### 10.2 实现原理

```
createBeanInstance() 阶段:
  │
  ├── 实例化后检查 BeanDefinition 中的 methodOverrides
  │
  └── 如果有 @Lookup 方法 → CglibSubclassingInstantiationStrategy:
        └── 创建 CGLIB 代理子类, 覆盖 @Lookup 方法:
              @Override
              public OrderService createOrderService() {
                  return applicationContext.getBean("orderService", OrderService.class);
              }
```

底层机制：
```java
// @Lookup 方法在 BeanDefinition 中存储为 LookupOverride
// AbstractAutowireCapableBeanFactory.createBeanInstance():
if (mbd.hasMethodOverrides()) {
    return instantiationStrategy.instantiate(beanName, mbd, null);
}
// LookupOverride 被 CglibSubclassingInstantiationStrategy 识别
// → Enhancer 覆盖方法 → 返回 getBean() 结果
```

---

## 十一、循环依赖中的注入

### 11.1 属性注入 + 循环依赖 (三级缓存解决)

```
@Component
class A { @Autowired B b; }
@Component
class B { @Autowired A a; }

流程:
  1. createBeanInstance("a") → new A() (实例化)
  2. addSingletonFactory("a", lambda) → 三级缓存
  3. populateBean(a):
       → getBean("b")
         → createBeanInstance("b") → new B()
         → addSingletonFactory("b", lambda) → 三级缓存
         → populateBean(b):
             → getBean("a") → 缓存命中 → 返回 a (可能含 AOP 代理)
         → 注入 a 到 b
       → B 完成 → 一级缓存
  4. 注入 b 到 a
  5. initializeBean(a) → A 完成
```

> 详见 [循环依赖深度解析](05-circular-dependency.md)

---

## 十二、注入时机总结

| 注入方式 | 发生阶段 | 处理器 | 循环依赖支持 |
|---------|---------|--------|------------|
| 构造器注入 | `createBeanInstance()` | `ConstructorResolver` | 不支持(需 @Lazy) |
| 字段注入 | `populateBean()` | `AutowiredAnnotationBeanPostProcessor` | 支持 |
| Setter 注入 | `populateBean()` | `AutowiredAnnotationBeanPostProcessor` | 支持 |
| @Resource 注入 | `populateBean()` | `CommonAnnotationBeanPostProcessor` | 支持 |
| @Value 注入 | `populateBean()` | `AutowiredAnnotationBeanPostProcessor` | 支持 |
| @Lookup 注入 | `createBeanInstance()` | CglibSubclassingInstantiationStrategy | 支持 |

---

## 十三、相关文档

| 文档 | 说明 |
|------|------|
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanFactory、DI 基础设施 |
| [Bean 生命周期深度解析](04-bean-lifecycle.md) | doCreateBean 完整流程 |
| [循环依赖深度解析](05-circular-dependency.md) | 三级缓存机制 |
| [AOP 实现深度解析](12-aop-implementation.md) | 代理创建 + earlyProxyReferences |
