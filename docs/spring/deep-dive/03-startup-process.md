# Spring 容器启动流程源码深度解析

> 本文深入分析 Spring ApplicationContext 启动的完整流程，覆盖 AbstractApplicationContext.refresh() 12 步模板方法、ConfigurationClassPostProcessor 配置类解析、BeanFactoryPostProcessor 执行排序、以及事件发布与监听器注册机制。
> 相关模块文档：[spring-context](../modules/L4-spring-context.md)、[spring-beans](../modules/L2-spring-beans.md)

---

## 一、启动流程全景

```
ApplicationContext 构造
  │
  └── refresh() ← ★ 核心入口, 12 步模板方法
        │
        ├── ① prepareRefresh()                     — 准备刷新
        ├── ② obtainFreshBeanFactory()              — 获取 BeanFactory
        ├── ③ prepareBeanFactory()                  — 准备 BeanFactory
        ├── ④ postProcessBeanFactory()              — 子类扩展点
        ├── ⑤ invokeBeanFactoryPostProcessors()      — ★ 执行 BFPP
        ├── ⑥ registerBeanPostProcessors()           — 注册 BPP
        ├── ⑦ initMessageSource()                   — 国际化
        ├── ⑧ initApplicationEventMulticaster()      — 事件广播器
        ├── ⑨ onRefresh()                           — 子类扩展点
        ├── ⑩ registerListeners()                   — 注册监听器
        ├── ⑪ finishBeanFactoryInitialization()      — ★ 实例化所有单例
        └── ⑫ finishRefresh()                       — 完成刷新
```

---

## 二、逐步深入分析

### 2.1 prepareRefresh() — 准备刷新

```
prepareRefresh():
  │
  ├── 记录启动时间: this.startupDate = System.currentTimeMillis()
  ├── 设置状态: this.closed = false, this.active = true
  │
  ├── initPropertySources():
  │     └── 子类扩展点: 初始化 PropertySource (如 WebApplicationContext 初始化 ServletContext/ServletConfig 属性)
  │
  ├── getEnvironment().validateRequiredProperties():
  │     └── 校验标记为 required 的属性是否存在
  │
  ├── 创建 earlyApplicationEvents 集合:
  │     └── 用于暂存 multicaster 就绪前发布的事件 (后续回放)
  │
  └── 创建 earlyApplicationListeners 集合:
        └── 用于暂存早期 ApplicationListener Bean
```

### 2.2 obtainFreshBeanFactory() — 获取 BeanFactory

```
obtainFreshBeanFactory():
  │
  ├── 容器类型不同, 行为不同:
  │
  ├── GenericApplicationContext (注解容器):
  │     ├── refreshBeanFactory():
  │     │     ├── 如果已有 BeanFactory → 销毁单例、清空缓存
  │     │     └── 返回已持有的 DefaultListableBeanFactory (构造函数中创建)
  │     └── getBeanFactory() → 返回上述 BeanFactory
  │
  └── AbstractRefreshableApplicationContext (XML 容器):
        ├── refreshBeanFactory():
        │     ├── 如果已有 → 销毁并关闭
        │     ├── 创建新的 DefaultListableBeanFactory
        │     └── loadBeanDefinitions(beanFactory) → 加载 XML
        └── getBeanFactory() → 返回新建的 BeanFactory
```

### 2.3 prepareBeanFactory() — 配置 BeanFactory

```
prepareBeanFactory(beanFactory):
  │
  ├── ① 设置 ClassLoader: beanFactory.setBeanClassLoader(getClassLoader())
  │
  ├── ② 设置表达式解析器: StandardBeanExpressionResolver
  │     └── 用于解析 #{...} SpEL 表达式
  │
  ├── ③ 注册 PropertyEditor: ResourceEditorRegistrar
  │     └── Resource → ResourceEditor
  │
  ├── ④ 添加 ApplicationContextAwareProcessor:
  │     └── 注入 ApplicationContextAware / EnvironmentAware / ResourceLoaderAware 等
  │
  ├── ⑤ 设置忽略的依赖接口 (自动注入时跳过):
  │     beanFactory.ignoreDependencyInterface(
  │       ResourceLoaderAware, ApplicationEventPublisherAware, 
  │       MessageSourceAware, ApplicationContextAware, EnvironmentAware)
  │
  ├── ⑥ 注册可解析依赖:
  │     registerResolvableDependency(BeanFactory.class, beanFactory)
  │     registerResolvableDependency(ResourceLoader.class, this)
  │     registerResolvableDependency(ApplicationEventPublisher.class, this)
  │     registerResolvableDependency(ApplicationContext.class, this)
  │
  ├── ⑦ 添加 ApplicationListenerDetector:
  │     └── 检测 Bean 是否实现 ApplicationListener → 自动注册
  │
  └── ⑧ 注册环境相关 Bean:
        ├── 如果存在 loadTimeWeaver → 注册 LoadTimeWeaverAwareProcessor
        └── 注册 environment / systemProperties / systemEnvironment 为单例
```

### 2.4 postProcessBeanFactory() — 子类扩展

```
postProcessBeanFactory(beanFactory):
  └── 空实现, 留给子类

典型子类实现:
  ├── GenericWebApplicationContext:
  │     └── 注册 ServletContextAwareProcessor
  │     └── 设置忽略 ServletContextAware 接口
  │     └── 注册 ServletContext / ServletConfig 等 scope
  │
  └── AnnotationConfigServletWebServerApplicationContext (Spring Boot):
        └── 执行 AutoConfigurationImportSelector 等
```

### 2.5 invokeBeanFactoryPostProcessors() — 执行 BFPP

这是启动中最重要的步骤, 负责处理所有 @Configuration 类和相关注解。

```
invokeBeanFactoryPostProcessors(beanFactory):
  │
  └── PostProcessorRegistrationDelegate.invokeBeanFactoryPostProcessors(beanFactory, getBeanFactoryPostProcessors()):
        │
        ├── Phase 1: 执行 BeanDefinitionRegistryPostProcessor (可注册新 BeanDefinition)
        │   │
        │   ├── ① 执行编程式注册的 BFPP (getBeanFactoryPostProcessors(), 已在 ApplicationContext 构造器中加入)
        │   │
        │   ├── ② 从 BeanFactory 中查找 BeanDefinitionRegistryPostProcessor 类型的 Bean:
        │   │     ├── PriorityOrdered → 排序 → invokeBeanDefinitionRegistryPostProcessors()
        │   │     │     └── ★ ConfigurationClassPostProcessor 在此执行!
        │   │     │           处理 @Configuration / @ComponentScan / @Import / @Bean
        │   │     ├── Ordered  → 排序 → invokeBeanDefinitionRegistryPostProcessors()
        │   │     └── 其他 → invokeBeanDefinitionRegistryPostProcessors()
        │   │
        │   └── ③ 循环处理: 上面步骤可能注册新的 BeanDefinitionRegistryPostProcessor
        │         └── 再次查找并执行 (循环直到无新增)
        │
        └── Phase 2: 执行普通 BeanFactoryPostProcessor (只能修改已注册的 BeanDefinition)
              │
              ├── ④ 执行 BeanDefinitionRegistryPostProcessor 上的 BeanFactoryPostProcessor 部分
              │
              └── ⑤ 从 BeanFactory 中查找 BeanFactoryPostProcessor 类型的 Bean:
                    ├── PriorityOrdered → 排序 → postProcessBeanFactory()
                    ├── Ordered → 排序 → postProcessBeanFactory()
                    └── 其他 → postProcessBeanFactory()
                          └── PropertySourcesPlaceholderConfigurer 在此替换 ${...}
```

### 2.6 registerBeanPostProcessors() — 注册 BPP

```
registerBeanPostProcessors(beanFactory):
  │
  └── PostProcessorRegistrationDelegate.registerBeanPostProcessors(beanFactory, this):
        │
        ├── 按 PriorityOrdered → Ordered → 普通 → MergedBeanDefinition → internal 顺序注册
        │
        ├── 核心注册的 BPP:
        │     ├── AutowiredAnnotationBeanPostProcessor      — @Autowired, @Value
        │     ├── CommonAnnotationBeanPostProcessor          — @Resource, @PostConstruct, @PreDestroy
        │     ├── AnnotationAwareAspectJAutoProxyCreator     — AOP 代理创建
        │     ├── AsyncAnnotationBeanPostProcessor           — @Async
        │     ├── ScheduledAnnotationBeanPostProcessor       — @Scheduled
        │     ├── PersistenceExceptionTranslationPostProcessor — 持久化异常翻译
        │     └── EventListenerMethodProcessor               — @EventListener
        │
        └── 最后注册 ApplicationListenerDetector (内部 BPP)
```

### 2.7 initMessageSource() — 国际化

```
initMessageSource():
  │
  ├── 查找容器中名为 "messageSource" 的 Bean
  │     ├── 存在 → 使用 (可能是自定义资源文件路径)
  │     └── 不存在 → 创建 DelegatingMessageSource
  │           └── 接受消息, 但代理到父容器解析
  │
  └── 将 messageSource 注册到容器
```

### 2.8 initApplicationEventMulticaster() — 事件广播器

```
initApplicationEventMulticaster():
  │
  ├── 查找容器中名为 "applicationEventMulticaster" 的 Bean
  │     ├── 存在 → 使用自定义广播器 (可配置 Executor 异步)
  │     └── 不存在 → 创建 SimpleApplicationEventMulticaster
  │
  └── 注册到容器
```

### 2.9 onRefresh() — 子类扩展

```
onRefresh():
  └── 空实现, 留给子类

典型子类实现:
  ├── AbstractRefreshableWebApplicationContext:
  │     └── initThemeSource()
  │
  ├── ReactiveWebServerApplicationContext (Spring Boot):
  │     └── createWebServer()
  │
  └── ServletWebServerApplicationContext (Spring Boot):
        └── createWebServer()
```

### 2.10 registerListeners() — 注册监听器

```
registerListeners():
  │
  ├── ① 将静态 ApplicationListener 注册到 multicaster:
  │     └── getApplicationListeners() (编程式添加的)
  │
  ├── ② 从 BeanFactory 中收集 ApplicationListener Bean:
  │     └── getBeanNamesForType(ApplicationListener.class)
  │           └── 只获取 beanName, 不提前实例化!
  │
  └── ③ 回放早期事件: earlyApplicationEvents → multicaster.multicastEvent()
        └── 本应在 multicaster 就绪前发布的事件 (如 earlyApplicationListeners)
```

### 2.11 finishBeanFactoryInitialization() — 实例化所有单例

```
finishBeanFactoryInitialization(beanFactory):
  │
  ├── ① 初始化 ConversionService (如果存在):
  │     └── beanFactory.setConversionService(conversionService)
  │
  ├── ② 注册默认的 EmbeddedValueResolver:
  │     └── 用于 ${...} 占位符解析
  │
  ├── ③ 冻结配置: beanFactory.freezeConfiguration()
  │     └── 不允许再注册新的 BeanDefinition
  │     └── 缓存所有 beanDefinitionNames (数组, 不再变化)
  │
  └── ④ ★ beanFactory.preInstantiateSingletons():
        │
        ├── 获取所有非抽象、非懒加载的单例 beanName 列表
        │
        ├── for each beanName:
        │     ├── FactoryBean? → getBean(FACTORY_BEAN_PREFIX + beanName) 
        │     │     └── 先创建 FactoryBean, 再创建其 getObject() 返回的 Bean
        │     └── 普通 Bean → getBean(beanName)
        │           └── AbstractBeanFactory.getBean()
        │                 └── doGetBean()
        │                       └── createBean()
        │                             └── doCreateBean()
        │                                   └── 完整 Bean 生命周期 (见 04-bean-lifecycle.md)
        │
        └── 触发 SmartInitializingSingleton.afterSingletonsInstantiated():
              └── EventListenerMethodProcessor 在此注册 @EventListener 方法
              └── 各框架扩展点
```

### 2.12 finishRefresh() — 完成刷新

```
finishRefresh():
  │
  ├── ① 清除 Resource 缓存: clearResourceCaches()
  │
  ├── ② 初始化 LifecycleProcessor (如果存在)
  │     └── DefaultLifecycleProcessor.onRefresh():
  │           ├── 查找所有 SmartLifecycle Bean
  │           ├── 按 phase 排序
  │           └── 依次调用 start()
  │
  ├── ③ 发布 ContextRefreshedEvent:
  │     └── publishEvent(new ContextRefreshedEvent(this))
  │           └── 所有 ApplicationListener<ContextRefreshedEvent> 被触发
  │
  └── ④ 注册到 LiveBeansView (JMX, 开发工具)
```

---

## 三、ConfigurationClassPostProcessor 深度分析

### 3.1 执行时机与角色

```
ConfigurationClassPostProcessor:
  实现: BeanDefinitionRegistryPostProcessor + PriorityOrdered
  顺序: highest priority (Integer.MAX_VALUE / 2 - 1 steps)
  执行: 在 refresh() 步骤⑤中自动被调用
```

### 3.2 配置类解析流程

```
ConfigurationClassParser.parse(configClasses):
  │
  ├── 对每个 @Configuration 类迭代处理:
  │   │
  │   ├── ① 解析 @PropertySource:
  │   │     └── 加载 .properties 文件到 Environment
  │   │
  │   ├── ② 解析 @ComponentScan:
  │   │     └── ClassPathBeanDefinitionScanner.scan(basePackages)
  │   │           ├── 扫描 .class 文件 → 读取 @Component 等注解
  │   │           ├── 生成 ScannedGenericBeanDefinition
  │   │           └── 注册到 BeanDefinitionRegistry
  │   │
  │   ├── ③ 解析 @Import:
  │   │     ├── 普通类: 作为 @Configuration 类递归解析
  │   │     ├── ImportSelector: selectImports() → 递归加载
  │   │     ├── DeferredImportSelector: 延迟处理 (所有配置类解析完后)
  │   │     │     └── Spring Boot: AutoConfigurationImportSelector 在此
  │   │     └── ImportBeanDefinitionRegistrar: 直接注册 BeanDefinition
  │   │
  │   ├── ④ 解析 @ImportResource:
  │   │     └── 加载 XML 配置中的 Bean 定义
  │   │
  │   ├── ⑤ 解析 @Bean 方法:
  │   │     └── 收集方法元数据 (不立即注册, 稍后统一注册)
  │   │
  │   └── ⑥ 解析父类/接口上的注解 (递归)
  │
  └── 处理 DeferredImportSelector:
        └── AutoConfigurationImportSelector (Spring Boot):
              ├── 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
              ├── 应用 @Conditional 过滤
              └── 导入符合条件的自动配置类
```

### 3.3 @Bean 方法注册

```
ConfigurationClassBeanDefinitionReader.loadBeanDefinitions(configClasses):
  │
  └── 对每个 @Bean 方法:
        │
        ├── 创建 ConfigurationClassBeanDefinition:
        │     ├── factoryBeanName = @Configuration 类 beanName
        │     ├── factoryMethodName = @Bean 方法名
        │     ├── factoryMethodMetadata = @Bean 注解属性
        │     └── 解析 @Lazy / @Primary / @DependsOn / @Scope / @Role / @Description
        │
        ├── 处理 @Bean(initMethod / destroyMethod):
        │     └── 设置 initMethodName / destroyMethodName
        │
        └── 注册: registry.registerBeanDefinition(beanName, beanDef)
```

### 3.4 @Configuration CGLIB 增强

```
ConfigurationClassEnhancer.enhance(configClass, classLoader):
  │
  └── 对 @Configuration(proxyBeanMethods=true) 的类创建 CGLIB 子类:
        │
        └── 拦截所有 @Bean 方法调用:
              └── EnhancedConfiguration 拦截器:
                    当 @Bean methodA() 内调用 @Bean methodB():
                      不执行 methodB() 的 Java 代码
                      → 改为调用 beanFactory.getBean("b") 
                      
                      确保: @Bean 方法的单例语义
                      (即便方法内多次调用, 也只创建一次 Bean)
```

---

## 四、事件系统

### 4.1 事件发布流程

```
ApplicationContext.publishEvent(event)
  │
  └── AbstractApplicationContext.publishEvent(event):
        │
        ├── ① 包装事件:
        │     ├── 如果是 ApplicationEvent → 直接使用
        │     └── 如果是普通 Object → PayloadApplicationEvent 包装
        │
        ├── ② 早期事件回放:
        │     └── 如果 applicatonEventMulticaster 未就绪:
        │           → 加入 earlyApplicationEvents (等步骤⑩注册监听器后回放)
        │
        └── ③ 广播事件:
              getApplicationEventMulticaster().multicastEvent(applicationEvent, eventType)
                │
                ├── 解析事件类型 (含泛型 ResolvableType):
                │     └── ApplicationListener<MyEvent> → 解析出 MyEvent
                │
                ├── 收集匹配的监听器: getApplicationListeners(event, type)
                │     ├── 从 applicationListenerBeans 中按类型匹配
                │     └── 支持泛型事件: GenericApplicationListener
                │
                ├── 排序: Ordered / @Order
                │
                └── 分发执行:
                      ├── 如果有 Executor: listener.invoke() 在线程池异步执行
                      └── 无 Executor: 同步直接调用 listener.onApplicationEvent(event)
```

### 4.2 内置生命周期事件

```
容器启动过程中依次发布的事件:

① ContextRefreshedEvent    — refresh() 完成时 (步骤⑫)
② ContextStartedEvent       — start() 调用时
③ ContextStoppedEvent       — stop() 调用时
④ ContextClosedEvent        — close() 调用时

RequestHandledEvent (Web):
  — 每次请求处理完成时 (需配置)
```

### 4.3 @EventListener 注册

```
EventListenerMethodProcessor (SmartInitializingSingleton):
  │
  └── afterSingletonsInstantiated():  ← 所有单例创建完成后
        │
        └── 遍历所有单例 Bean:
              └── 查找 @EventListener 注解的方法:
                    → 创建 ApplicationListenerMethodAdapter:
                        ├── 解析事件类型 (从方法参数)
                        ├── 解析 @EventListener.condition (SpEL 条件)
                        ├── 解析 @EventListener.id (唯一标识)
                        ├── 解析 @Order / @Async
                        └── 注册到 ApplicationEventMulticaster
```

---

## 五、启动时序总结

| 步骤 | 方法 | 关键操作 | 抛出异常后 |
|------|------|---------|----------|
| ① | `prepareRefresh()` | 设置 active=true, 校验必要属性 | — |
| ② | `obtainFreshBeanFactory()` | 创建/获取 BeanFactory, 加载 BeanDefinition | — |
| ③ | `prepareBeanFactory()` | 注册 Aware Processor, 设置忽略依赖 | — |
| ④ | `postProcessBeanFactory()` | 子类扩展 | — |
| ⑤ | `invokeBeanFactoryPostProcessors()` | **解析 @Configuration / @ComponentScan / @Bean** | — |
| ⑥ | `registerBeanPostProcessors()` | 注册 @Autowired / AOP / @Async 等处理器 | — |
| ⑦ | `initMessageSource()` | 国际化消息源 | — |
| ⑧ | `initApplicationEventMulticaster()` | 事件广播器 | — |
| ⑨ | `onRefresh()` | 子类扩展 | — |
| ⑩ | `registerListeners()` | 注册 ApplicationListener, 回放早期事件 | — |
| ⑪ | `finishBeanFactoryInitialization()` | **实例化所有单例 Bean** | 销毁已创建的单例 |
| ⑫ | `finishRefresh()` | 启动 Lifecycle, 发布 ContextRefreshedEvent | — |

### 异常恢复

当步骤⑤-⑫中发生异常时:

```
catch (BeansException ex):
  ├── destroyBeans()          — 销毁已创建的所有单例 Bean
  ├── cancelRefresh(ex)       — 重置 active = false
  └── throw ex  (向上传播)
```

---

## 六、关键扩展点

| 扩展点 | 时机 | 用途 |
|--------|------|------|
| `ApplicationContextInitializer` | refresh() 之前 | 自定义 Environment / 激活 Profile |
| `BeanFactoryPostProcessor` | 步骤⑤ | 修改 BeanDefinition 属性 |
| `BeanDefinitionRegistryPostProcessor` | 步骤⑤ (优先) | 注册新 BeanDefinition |
| `BeanPostProcessor` | 步骤⑪ Bean 初始化前后 | AOP、注入等 |
| `ApplicationListener<E>` | 事件发生时 | 监听容器生命周期事件 |
| `SmartLifecycle` | 步骤⑫ | 容器启动/停止时自定义逻辑 |

---

## 七、相关文档

| 文档 | 说明 |
|------|------|
| [spring-context 模块文档](../modules/L4-spring-context.md) | ApplicationContext 完整参考 |
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanFactory 与 Bean 生命周期 |
| [Bean 生命周期深度解析](04-bean-lifecycle.md) | doCreateBean 15 步骤 |
| [依赖注入深度解析](06-dependency-injection.md) | @Autowired 注入链路 |
| [AOP 实现深度解析](12-aop-implementation.md) | 代理创建时机 |
