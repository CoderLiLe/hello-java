# spring-beans 模块功能文档

---

## 一、模块定位

spring-beans 是 Spring Framework 的 **IoC 容器核心**，336 个 Java 文件，负责：

- **BeanFactory**：最底层的 IoC 容器接口与实现
- **BeanDefinition**：Bean 的配置元数据模型
- **Bean 生命周期管理**：实例化 → 属性填充 → 初始化 → 销毁
- **依赖注入（DI）**：`@Autowired`、`@Qualifier`、构造器注入、setter 注入
- **BeanPostProcessor**：Bean 实例创建前后的拦截扩展点
- **类型转换与属性绑定**：`BeanWrapper`、`PropertyEditor`
- **XML 配置解析**：`<bean>` 标签解析
- **AOT 支持**：Bean 注册的编译期代码生成

**依赖**：`spring-core`

---

## 二、模块全景图

```
spring-beans (336 files)
│
├── org.springframework.beans/                         # JavaBeans 基础设施 (48 files)
│   ├── BeanWrapper / BeanWrapperImpl                  — 属性访问与类型转换
│   ├── PropertyAccessor                              — 属性访问接口
│   ├── MutablePropertyValues                         — 可变属性值集合
│   ├── PropertyValue, PropertyMatches                — 属性值表示
│   ├── AbstractNestablePropertyAccessor              — 嵌套属性访问
│   ├── TypeConverter / TypeConverterSupport          — 类型转换器
│   └── CachedIntrospectionResults                    — JavaBean 内省缓存
│
├── org.springframework.beans.factory/                # BeanFactory 核心接口 (35 files)
│   ├── BeanFactory                                   — IoC 容器根接口
│   ├── ListableBeanFactory                           — 可枚举的 BeanFactory
│   ├── HierarchicalBeanFactory                      — 层次化容器
│   ├── ConfigurableBeanFactory                       — 可配置的容器
│   ├── ConfigurableListableBeanFactory               — 完整功能容器接口
│   ├── FactoryBean<T>                                — Bean 工厂模式
│   ├── ObjectFactory<T>                              — 延迟获取器
│   ├── ObjectProvider<T>                             — 增强延迟获取（含 Stream）
│   ├── InitializingBean                              — 初始化回调
│   ├── DisposableBean                                — 销毁回调
│   ├── Aware 系列接口                                — 容器感知注入
│   ├── BeanNameAware                                 — 注入 beanName
│   ├── BeanFactoryAware                              — 注入 BeanFactory
│   └── BeanClassLoaderAware                          — 注入 ClassLoader
│
├── org.springframework.beans.factory.annotation/     # 注解驱动注入 (18 files)
│   ├── Autowired / Qualifier / Value / Lookup        — 注入注解
│   ├── AutowiredAnnotationBeanPostProcessor          — @Autowired 处理器
│   ├── InitDestroyAnnotationBeanPostProcessor        — @PostConstruct / @PreDestroy
│   ├── InjectionMetadata                             — 注入元数据模型
│   └── QualifierAnnotationAutowireCandidateResolver  — @Qualifier 解析
│
├── org.springframework.beans.factory.config/         # Bean 配置定义 (49 files)
│   ├── BeanDefinition                                — Bean 定义接口
│   ├── BeanPostProcessor                             — Bean 后处理扩展点
│   ├── BeanFactoryPostProcessor                      — 容器后处理扩展点
│   ├── InstantiationAwareBeanPostProcessor           — 实例化前拦截
│   ├── DestructionAwareBeanPostProcessor             — 销毁前拦截
│   ├── ConfigurableBeanFactory                       — 可配置容器接口
│   ├── Scope                                          — 作用域接口
│   ├── ConstructorArgumentValues                     — 构造器参数
│   ├── BeanReference                                  — Bean 引用
│   └── PropertyPlaceholderConfigurer                  — 属性占位符
│
├── org.springframework.beans.factory.support/        # 核心实现 (54 files)
│   ├── DefaultListableBeanFactory                     — ★ 默认容器实现
│   ├── AbstractBeanFactory                            — 容器抽象基类
│   ├── AbstractAutowireCapableBeanFactory             — ★ Bean 创建核心
│   ├── DefaultSingletonBeanRegistry                  — 单例注册表
│   ├── FactoryBeanRegistrySupport                     — FactoryBean 支持
│   ├── ConstructorResolver                            — 构造器/工厂方法解析
│   ├── RootBeanDefinition                             — 合并后的 Bean 定义
│   ├── GenericBeanDefinition                          — 通用 Bean 定义
│   ├── BeanDefinitionRegistry                        — Bean 定义注册接口
│   ├── BeanDefinitionReader                           — Bean 定义读取器接口
│   ├── InstantiationStrategy                          — 实例化策略
│   ├── CglibSubclassingInstantiationStrategy          — CGLIB 实例化
│   └── BeanDefinitionValueResolver                   — 属性值解析
│
├── org.springframework.beans.factory.parsing/         # 配置解析 (24 files)
│   ├── ReaderContext / ReaderEventListener             — 解析事件监听
│   └── AbstractBeanDefinitionParser                   — Bean 定义解析器
│
├── org.springframework.beans.factory.xml/             # XML 配置 (27 files)
│   ├── XmlBeanDefinitionReader                        — XML 读取器
│   ├── DefaultBeanDefinitionDocumentReader            — 默认文档解析
│   └── NamespaceHandler / NamespaceHandlerResolver    — 命名空间处理
│
├── org.springframework.beans.factory.aot/             # AOT 编译 (31 files)
│   ├── BeanDefinitionPropertyValueCodeGenerator        — 属性值代码生成
│   ├── BeanFactoryBeanRegistrationAotProcessor         — Bean 注册 AOT
│   └── BeanRegistrationsAotContribution                 — AOT 贡献
│
├── org.springframework.beans.factory.groovy/          # Groovy 支持 (4 files)
├── org.springframework.beans.factory.serviceloader/   # ServiceLoader 桥 (5 files)
├── org.springframework.beans.factory.wiring/          # 类型注解布线 (5 files)
├── org.springframework.beans.propertyeditors/         # 属性编辑器 (29 files)
└── org.springframework.beans.support/                 # 工具支持 (7 files)
```

---

## 三、BeanFactory 类继承层次

```
BeanFactory                          — 根接口: getBean(String), containsBean, isSingleton
  ├── HierarchicalBeanFactory       — 父子容器: getParentBeanFactory()
  ├── ListableBeanFactory           — 枚举: getBeanNamesForType, getBeansOfType
  │     └── ConfigurableListableBeanFactory  — 完整功能接口 (合并以下所有)
  │
  └── ConfigurableBeanFactory       — 配置: addBeanPostProcessor, registerScope
        └── AbstractBeanFactory     — 抽象基类 (getBean 模板方法)
              ├── FactoryBeanRegistrySupport  — FactoryBean 支持
              │
              └── AbstractAutowireCapableBeanFactory  — ★ Bean 创建核心
                    └── DefaultListableBeanFactory     — ★ 默认容器实现
                          ├── 实现 ConfigurableListableBeanFactory
                          ├── 实现 BeanDefinitionRegistry
                          └── 继承 DefaultSingletonBeanRegistry

DefaultSingletonBeanRegistry         — 单例管理: singletonObjects (ConcurrentHashMap)
  └── SimpleAliasRegistry           — 别名管理: aliasMap
        └── AliasRegistry (spring-core 接口)
```

---

## 四、核心流程

### 4.1 Bean 定义加载流程

```
Resource[] resources = ...
  │
  ├── XmlBeanDefinitionReader.loadBeanDefinitions(resources)
  │     │
  │     ├── DefaultBeanDefinitionDocumentReader.registerBeanDefinitions(doc, ctx)
  │     │     │
  │     │     ├── 解析 <beans> → 处理 profile 条件
  │     │     ├── 解析 <bean>     → BeanDefinitionParserDelegate.parseBeanDefinitionElement()
  │     │     │                      └── 生成 GenericBeanDefinition
  │     │     ├── 解析 <alias>    → registerAlias()
  │     │     ├── 解析 <import>   → 递归加载
  │     │     └── 解析自定义命名空间 → NamespaceHandler
  │     │
  │     └── BeanDefinitionReaderUtils.registerBeanDefinition(bdHolder, registry)
  │           │
  │           ├── beanDefinitionMap.put(beanName, beanDefinition)
  │           └── beanDefinitionNames.add(beanName)
  │
  └── 注解扫 ─→ AnnotatedBeanDefinitionReader.registerBean(Class)
        └── ClassPathBeanDefinitionScanner.scan(basePackages)
              └── 解析 @Component, @Service, @Repository, @Controller
                    └── ScannedGenericBeanDefinition
```

### 4.2 Bean 创建生命周期（核心）

```
getBean(String name)
  │
  ├── ① 别名解析: transformedBeanName(name)  → 去掉 & 前缀，解析别名
  │
  ├── ② 单例缓存检查: getSingleton(beanName)
  │     ├── 一级缓存: singletonObjects  — 完全创建好的单例
  │     ├── 二级缓存: earlySingletonObjects  — 早期引用 (解决循环依赖)
  │     └── 三级缓存: singletonFactories  — ObjectFactory (AOP 代理)
  │     └── 命中 → 返回
  │
  ├── ③ 标记为 "正在创建": beforeSingletonCreation(beanName)
  │     └── singletonsCurrentlyInCreation.add(beanName)  — 循环依赖检测
  │
  ├── ④ 获取合并后的 BeanDefinition
  │     getMergedLocalBeanDefinition(beanName) → RootBeanDefinition
  │     mergedBeanDefinitions.put(beanName, mbd)
  │
  ├── ⑤ 依赖检查: 先创建 dependsOn 中声明的 Bean
  │     for (dep : mbd.getDependsOn()) getBean(dep)
  │
  ├── ⑥ Scope 分支:
  │     ├── Singleton: createBean(beanName, mbd, args)  → 见 4.3
  │     ├── Prototype:  createBean(beanName, mbd, args)  → 见 4.3 (不缓存)
  │     └── 其他 Scope: scope.get(scopeName, callback) → createBean() → ObjectsFactory
  │
  ├── ⑦ 类型检查: requiredType.cast(bean)
  │
  └── ⑧ 返回 bean
```

### 4.3 createBean() → doCreateBean() 详细流程 (AbstractAutowireCapableBeanFactory)

```
createBean(beanName, mbd, args)
  │
  ├── resolveBeanClass(mbd, beanName)   — 加载 Bean Class
  │
  ├── 调用 InstantiationAwareBeanPostProcessor:
  │     postProcessBeforeInstantiation(beanClass, beanName)
  │     └── 可提前返回代理对象 (如 AOP)
  │
  └── doCreateBean(beanName, mbd, args)      ← ★ 核心
        │
        ├── ① 实例化: createBeanInstance(beanName, mbd, args)
        │     │
        │     ├── 优先级:
        │     │   1. Supplier → instanceSupplier.get()
        │     │   2. Factory Method → ConstructorResolver.instantiateUsingFactoryMethod()
        │     │   3. 构造器注入 → ConstructorResolver.autowireConstructor()
        │     │   4. 默认构造器 → instantiateBean() → InstantiationStrategy
        │     │        ├── SimpleInstantiationStrategy → Constructor.newInstance()
        │     │        └── CglibSubclassingInstantiationStrategy → Objenesis (无参)
        │     │
        │     └── 返回 BeanWrapper 包裹的原始实例
        │
        ├── ② 合并 BeanPostProcessor: 收集所有 MergedBeanDefinitionPostProcessor
        │     applyMergedBeanDefinitionPostProcessors(mbd, bdType, beanName)
        │     └── 解析 @Autowired, @Resource, @PostConstruct 等元数据
        │
        ├── ③ 早期单例曝光 (解决循环依赖):
        │     addSingletonFactory(beanName, () → getEarlyBeanReference(beanName, mbd, bean))
        │     └── SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference()
        │         └── AOP 在此创建早期代理
        │
        ├── ④ 属性填充: populateBean(beanName, mbd, bw)
        │     │
        │     ├── InstantiationAwareBeanPostProcessor.postProcessAfterInstantiation()
        │     │
        │     ├── 注入模式判断:
        │     │   ├── AUTOWIRE_BY_NAME → autowireByName()
        │     │   └── AUTOWIRE_BY_TYPE → autowireByType()
        │     │
        │     └── 后处理器注入:
        │         InstantiationAwareBeanPostProcessor.postProcessProperties(pvs, bean, beanName)
        │         └── AutowiredAnnotationBeanPostProcessor 处理 @Autowired 注入
        │         └── CommonAnnotationBeanPostProcessor 处理 @Resource
        │
        ├── ⑤ 初始化: initializeBean(beanName, bean, mbd)
        │     │
        │     ├── 5a) Aware 回调:
        │     │   BeanNameAware.setBeanName()
        │     │   BeanClassLoaderAware.setBeanClassLoader()
        │     │   BeanFactoryAware.setBeanFactory()
        │     │
        │     ├── 5b) BeanPostProcessor.postProcessBeforeInitialization()
        │     │
        │     ├── 5c) InitializingBean.afterPropertiesSet()
        │     │      或 @PostConstruct 或 init-method
        │     │
        │     └── 5d) BeanPostProcessor.postProcessAfterInitialization()
        │         └── 此处 AOP 创建正常代理对象
        │
        └── ⑥ 注册销毁回调: registerDisposableBeanIfNecessary()
              └── DisposableBeanAdapter (收集 destroy 方法)
```

### 4.4 单例三级缓存与循环依赖解决

```
                    ┌──────────────────────────────────┐
                    │   singletonObjects (一级缓存)      │
                    │   ConcurrentHashMap<String, Object>│ ← 完全初始化完成的单例
                    └──────────────────────────────────┘
                              ↑ (bean 完全创建后)

                    ┌──────────────────────────────────┐
                    │   earlySingletonObjects (二级缓存)  │
                    │   HashMap<String, Object>         │ ← 早期引用 (已创建未填充)
                    └──────────────────────────────────┘
                              ↑ (getEarlyBeanReference 后)

                    ┌──────────────────────────────────┐
                    │   singletonFactories (三级缓存)    │
                    │   HashMap<String, ObjectFactory>  │ ← 刚实例化后注册
                    └──────────────────────────────────┘

循环依赖解决流程:
    A 创建 → 实例化 A → 暴露 A 的 ObjectFactory (三级) → 填充 A 属性
      → 发现需要 B → 创建 B → 实例化 B → 暴露 B 的 ObjectFactory (三级) → 填充 B 属性
        → 发现需要 A → getSingleton("A")
          → singletonObjects 无 → earlySingletonObjects 无 → singletonFactories 有
            → ObjectFactory.getObject() → getEarlyBeanReference() → 放入二级缓存
              → 从三级缓存移除
                → 返回 A 的早期引用
                  → B 注入 A → B 初始化完成 → B 为单例 (入一级)
                    → A 注入 B → A 初始化完成 → A 为单例 (入一级)
```

### 4.5 @Autowired 注入流程

```
AutowiredAnnotationBeanPostProcessor.postProcessProperties(pvs, bean, beanName)
  │
  ├── findAutowiringMetadata(beanName, beanClass, pvs)
  │     │
  │     ├── 扫描字段: @Autowired field
  │     │     └── 生成 AutowiredFieldElement
  │     │
  │     └── 扫描方法: @Autowired method (@Bean 方法)
  │           └── 生成 AutowiredMethodElement
  │
  └── metadata.inject(bean, beanName, pvs)
        │
        └── 遍历每个 InjectionMetadata.InjectedElement
              │
              ├── 解析依赖: beanFactory.resolveDependency(desc, beanName, autowiredBeanNames, typeConverter)
              │     │
              │     ├── @Value 解析 → embeddedValueResolver
              │     ├── @Autowired 类型匹配:
              │     │   ├── 单个 bean: getBean(beanNames[0])
              │     │   ├── 集合/数组: getBeansForType() → 排序
              │     │   └── Map<String,T>: getBeansOfType()
              │     ├── @Qualifier → QualifierAnnotationAutowireCandidateResolver
              │     └── 候选选择:  Primary > Highest Priority > single match
              │
              └── 反射注入: field.set(bean, resolved) 或 method.invoke(bean, resolved)
```

---

## 五、关键扩展点

| 扩展点 | 时机 | 用途 |
|--------|------|------|
| **BeanFactoryPostProcessor** | 所有 BeanDefinition 加载后，实例化前 | 修改 BeanDefinition（如属性占位符替换） |
| **BeanPostProcessor.postProcessBeforeInitialization** | Bean 属性填充后，init 回调前 | 自定义初始化前处理 |
| **BeanPostProcessor.postProcessAfterInitialization** | init 回调后 | AOP 代理创建、包装 |
| **InstantiationAwareBeanPostProcessor** | 实例化前后、属性填充前后 | 短路实例化，返回代理 |
| **MergedBeanDefinitionPostProcessor** | BeanDefinition 合并后 | 解析 @Autowired 等注解元数据 |
| **DestructionAwareBeanPostProcessor** | Bean 销毁前 | 清理资源 |
| **SmartInstantiationAwareBeanPostProcessor** | 预测 bean 类型、获取早期引用 | 循环依赖中的代理 |
| **InitializingBean.afterPropertiesSet()** | 属性全部设置完成后 | Bean 自定义初始化逻辑 |
| **DisposableBean.destroy()** | 容器关闭时 | Bean 资源释放 |

---

## 六、依赖关系

```
spring-beans
  ├── api: spring-core
  ├── optional: jakarta.inject:jakarta.inject-api
  ├── optional: org.apache.groovy:groovy-xml    (Groovy Bean DSL)
  ├── optional: org.jetbrains.kotlin:kotlin-reflect
  ├── optional: org.jetbrains.kotlin:kotlin-stdlib
  ├── optional: org.reactivestreams:reactive-streams
  └── optional: org.yaml:snakeyaml

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-core](L1-spring-core.md) | L1 核心 | 反射、工具类、ASM |
| 下游 | [spring-aop](L3-spring-aop.md) | L3 增强 | AOP 代理织入 |
| 下游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext 容器 |
| 下游 | [spring-tx](L5-spring-tx.md) | L5 事务 | 事务管理 |
| 下游 | [spring-messaging](L6-spring-messaging.md) | L6 消息 | 消息抽象 |
| 下游 | [spring-web](L7-spring-web.md) | L7 Web | HTTP 抽象层 |
```
