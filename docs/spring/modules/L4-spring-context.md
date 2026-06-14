# spring-context 模块功能文档

---

## 一、模块定位

spring-context 是 Spring 的**应用上下文核心模块**，625 个 Java 文件，负责：

- **ApplicationContext**：高级 IoC 容器接口，继承 BeanFactory + 事件发布 + 国际化 + 资源加载
- **Java 配置支持**：`@Configuration`、`@Bean`、`@ComponentScan`、`@Import`、`@Conditional`
- **BeanFactoryPostProcessor 处理**：配置类解析、属性占位符替换
- **事件系统**：ApplicationEvent 发布/监听，`@EventListener` 注解驱动
- **国际化**：MessageSource 层次（ResourceBundle → 父 MessageSource）
- **调度支持**：`@Scheduled`（定时任务）、`@Async`（异步执行）
- **缓存抽象**：`@Cacheable` / `@CacheEvict` / `@CachePut`
- **校验集成**：Bean Validation（`@Valid` / `@Validated`）方法校验
- **格式化支持**：`@DateTimeFormat`、`@NumberFormat`
- **JMX / JNDI / Scripting / EJB** 等传统企业集成
- **SpEL 集成**：上下文级 ExpressionEvaluator
- **AOT 支持**：编译期 ApplicationContext 初始化代码生成

**依赖**：`spring-aop`、`spring-beans`、`spring-expression`、`spring-core`、`micrometer-observation`

---

## 二、模块全景图

```
spring-context (625 files)
│
├── org.springframework.context/                    # 核心接口 (25 files)
│   ├── ApplicationContext                           — 应用上下文根接口 (6 大父接口)
│   ├── ConfigurableApplicationContext               — 可配置上下文 SPI
│   ├── Lifecycle / SmartLifecycle / LifecycleProcessor — 生命周期管理
│   ├── MessageSource / HierarchicalMessageSource    — 国际化消息源
│   ├── ApplicationEventPublisher                    — 事件发布接口
│   ├── ApplicationEvent                             — 事件基类
│   ├── ApplicationListener                          — 事件监听器接口
│   ├── ApplicationContextInitializer                — 容器初始化回调
│   └── Phased                                       — 阶段排序接口
│
├── org.springframework.context.annotation/          # Java 配置 (68 files)
│   ├── Configuration                                — @Configuration 注解
│   ├── Bean / Scope / Lazy / Primary / DependsOn    — Bean 定义注解
│   ├── ComponentScan / FilterType                   — 组件扫描
│   ├── ConfigurationClassPostProcessor              — ★ 配置类后处理器 (1101 行)
│   ├── ConfigurationClassParser                     — ★ 配置类解析器 (1176 行)
│   ├── ConfigurationClassEnhancer                   — @Configuration CGLIB 增强
│   ├── ConfigurationClassBeanDefinitionReader       — @Bean 方法注册
│   ├── ClassPathBeanDefinitionScanner               — 类路径 Bean 扫描
│   ├── AnnotatedBeanDefinitionReader                — 注解 Bean 注册
│   ├── Import / ImportSelector / ImportBeanDefinitionRegistrar — 导入机制
│   ├── Conditional / Condition / ConditionEvaluator  — 条件装配
│   ├── Profile / ProfileCondition                    — Profile 条件
│   ├── PropertySource / PropertySources              — 属性源注解
│   ├── DeferredImportSelector                        — 延迟导入选择器
│   ├── CommonAnnotationBeanPostProcessor            — @Resource / @PostConstruct / @PreDestroy
│   ├── AnnotationConfigApplicationContext           — 注解驱动容器实现
│   └── AnnotationBeanNameGenerator                  — 注解 Bean 命名
│
├── org.springframework.context.event/               # 事件系统 (25 files)
│   ├── ApplicationEventMulticaster                  — 事件广播器接口
│   ├── SimpleApplicationEventMulticaster            — 默认广播器 (支持 Executor)
│   ├── AbstractApplicationEventMulticaster          — 广播器抽象基类
│   ├── EventListener                                — @EventListener 注解
│   ├── EventListenerMethodProcessor                 — @EventListener 处理器
│   ├── ApplicationListenerMethodAdapter             — 将 @EventListener 适配为 ApplicationListener
│   ├── GenericApplicationListener / SmartApplicationListener — 泛型监听器
│   ├── ApplicationContextEvent                      — 上下文事件基类
│   ├── ContextRefreshedEvent / ContextClosedEvent   — 刷新/关闭事件
│   ├── ContextStartedEvent / ContextStoppedEvent    — 启动/停止事件
│   └── PayloadApplicationEvent                      — 泛型 Payload 事件
│
├── org.springframework.context.support/             # 核心实现 (55 files)
│   ├── AbstractApplicationContext                   — ★ 容器抽象基类 (1673 行, refresh() 模板)
│   ├── GenericApplicationContext                    — ★ 通用容器实现
│   ├── GenericXmlApplicationContext                 — XML 配置容器
│   ├── AnnotationConfigApplicationContext           — 注解配置容器
│   ├── AbstractRefreshableApplicationContext        — 可刷新容器抽象
│   ├── AbstractXmlApplicationContext                 — XML 容器抽象
│   ├── GenericGroovyApplicationContext              — Groovy DSL 容器
│   ├── PostProcessorRegistrationDelegate            — BPP/BFPP 注册代理 (排序逻辑)
│   ├── ApplicationContextAwareProcessor             — ApplicationContextAware 回调
│   ├── DefaultLifecycleProcessor                    — 默认生命周期处理器
│   ├── ResourceBundleMessageSource                  — 资源文件消息源
│   ├── ReloadableResourceBundleMessageSource        — 可重载消息源
│   ├── PropertySourcesPlaceholderConfigurer         — 属性占位符配置器
│   ├── ConversionServiceFactoryBean                 — 类型转换服务工厂
│   ├── ClassPathXmlApplicationContext               — 类路径 XML 容器
│   └── FileSystemXmlApplicationContext              — 文件系统 XML 容器
│
├── org.springframework.context.expression/           # SpEL 集成 (5 files)
│   ├── StandardBeanExpressionResolver               — Bean 表达式解析器
│   └── EnvironmentAwareExpressionParser              — 环境感知解析器
│
├── org.springframework.context.i18n/                 # 国际化 (4 files)
│   ├── LocaleContext / LocaleContextHolder           — 区域上下文
│   └── TimeZoneAwareLocaleContext                    — 时区感知区域
│
├── org.springframework.context.index/                # 编译期索引 (5 files)
│   └── CandidateComponentsIndex / CandidateComponentsIndexLoader — 候选组件索引
│
├── org.springframework.context.weaving/              # LoadTimeWeaving (4 files)
│   └── LoadTimeWeaverAware / DefaultContextLoadTimeWeaver / AspectJWeavingEnabler
│
├── org.springframework.context.config/               # XML 命名空间 (8 files)
│   └── ContextNamespaceHandler / PropertyPlaceholderBeanDefinitionParser
│
├── org.springframework.context.aot/                  # AOT 编译 (23 files)
│   └── ApplicationContextAotGenerator / ContextClassGenerator / etc.
│
├── org.springframework.stereotype/                   # 构造型注解 (6 files)
│   ├── Component / Service / Repository / Controller — 分层标记注解
│   └── Indexed                                       — 编译期索引标记
│
├── org.springframework.cache/                        # 缓存抽象 (41 files)
│   ├── Cache / CacheManager                         — 缓存核心接口
│   ├── annotation/: @Cacheable / @CacheEvict / @CachePut
│   ├── interceptor/: CacheInterceptor / CacheAspectSupport
│   ├── config/: CacheNamespaceHandler
│   └── support/: NoOpCacheManager / ConcurrentMapCacheManager
│
├── org.springframework.scheduling/                   # 调度支持 (44 files)
│   ├── TaskScheduler / Trigger                       — 调度核心接口
│   ├── annotation/: @Scheduled / @Async / ScheduledAnnotationBeanPostProcessor
│   ├── concurrent/: ThreadPoolTaskExecutor / ThreadPoolTaskScheduler
│   ├── config/: ScheduledTaskRegistrar / ScheduledTaskHolder
│   └── support/: CronExpression / CronTrigger / PeriodicTrigger
│
├── org.springframework.validation/                   # 校验支持 (30 files)
│   ├── Validator / Errors / BindingResult           — 校验核心接口
│   ├── DataBinder / WebDataBinder                    — 数据绑定 + 校验
│   ├── beanvalidation/: SpringValidatorAdapter      — Bean Validation 适配
│   ├── method/: MethodValidationPostProcessor       — 方法参数校验
│   └── annotation/: @Validated                       — 校验注解
│
├── org.springframework.format/                       # 格式化 (17 files)
│   ├── Formatter / Printer / Parser                 — 格式化核心接口
│   ├── annotation/: @DateTimeFormat / @NumberFormat  — 格式化注解
│   ├── datetime/: DateFormatter / DateTimeFormatFactory
│   ├── number/: NumberFormatter / CurrencyStyleFormatter
│   └── support/: FormattingConversionService         — 格式化转换服务
│
├── org.springframework.jmx/                          # JMX 支持 (28 files)
│   ├── MBeanServerConnectionFactoryBean              — MBean 连接工厂
│   └── export/: MBeanExporter / AnnotationMBeanExporter
│
├── org.springframework.jndi/                         # JNDI 支持 (8 files)
│   └── JndiTemplate / JndiObjectFactoryBean
│
├── org.springframework.scripting/                    # 脚本支持 (14 files)
│   ├── ScriptFactory / ScriptEvaluator               — 脚本执行
│   └── groovy/ bsh/ support/                         — 各语言支持
│
├── org.springframework.instrument/                   # 类加载时织入 (8 files)
│   └── classloading/: InstrumentationLoadTimeWeaver / ReflectiveLoadTimeWeaver
│
├── org.springframework.ejb/                          # EJB 支持 (9 files)
│   └── LocalStatelessSessionProxyFactoryBean
│
├── org.springframework.resilience/                   # 韧性重试 (5 files)
│   └── retry/: RetryTemplate / RetryRecoveryCallback
│
└── org.springframework.ui/                           # UI 支持 (8 files)
    └── Model / ExtendedModelMap / ModelMap
```

---

## 三、ApplicationContext 类继承层次

```
ApplicationContext                          — 根接口: getBean + getEnvironment + publishEvent + getMessage
  ├── extends EnvironmentCapable           — getEnvironment()
  ├── extends ListableBeanFactory          — getBeansOfType, getBeanNamesForType
  ├── extends HierarchicalBeanFactory      — getParentBeanFactory()
  ├── extends MessageSource                — getMessage(code, args, default, locale)
  ├── extends ApplicationEventPublisher    — publishEvent(Object)
  └── extends ResourcePatternResolver      — getResources("classpath*:...")

ConfigurableApplicationContext              — SPI: refresh(), close(), addBeanFactoryPostProcessor()
  └── extends Lifecycle, Closeable

AbstractApplicationContext                  — ★ 抽象基类 (1673 行, refresh() 模板方法)
  ├── GenericApplicationContext            — 通用实现 (持有 DefaultListableBeanFactory)
  │     ├── AnnotationConfigApplicationContext  — 注解配置
  │     │     ├── register(Class) → AnnotatedBeanDefinitionReader
  │     │     └── scan(pkg) → ClassPathBeanDefinitionScanner
  │     ├── GenericXmlApplicationContext    — XML 配置
  │     │     └── AbstractXmlApplicationContext
  │     │           ├── ClassPathXmlApplicationContext
  │     │           └── FileSystemXmlApplicationContext
  │     └── GenericGroovyApplicationContext — Groovy DSL
  │
  └── AbstractRefreshableApplicationContext — 可刷新容器 (支持多次 refresh)
        └── AbstractXmlApplicationContext
```

---

## 四、核心流程

### 4.1 refresh() 生命周期（12 步模板方法）

```
AbstractApplicationContext.refresh()
  │
  ├── ① prepareRefresh()
  │     ├── 记录启动时间 (startupDate)
  │     ├── 设置 active = true, closed = false
  │     ├── 初始化 PropertySources
  │     └── 校验必要属性 (validateRequiredProperties)
  │
  ├── ② obtainFreshBeanFactory()
  │     ├── GenericApplicationContext: 直接返回持有的 BeanFactory
  │     └── AbstractRefreshableApplicationContext: 创建新的 DefaultListableBeanFactory
  │           └── loadBeanDefinitions(beanFactory) → 加载 XML / 注解定义
  │
  ├── ③ prepareBeanFactory(beanFactory)
  │     ├── 设置 ClassLoader
  │     ├── 注册 StandardBeanExpressionResolver (SpEL)
  │     ├── 注册 ResourceEditorRegistrar (PropertyEditor)
  │     ├── 添加 ApplicationContextAwareProcessor
  │     ├── 忽略 Aware 接口 (自动注入时跳过)
  │     └── 注册环境 Bean: environment, systemProperties, systemEnvironment
  │
  ├── ④ postProcessBeanFactory(beanFactory)
  │     └── 子类扩展点: 注册特殊的 BeanPostProcessor (如 WebApplicationContext 注册 ServletContextAwareProcessor)
  │
  ├── ⑤ invokeBeanFactoryPostProcessors(beanFactory)  ← ★ 核心
  │     │
  │     ├── 先执行 BeanDefinitionRegistryPostProcessor (可注册新 BeanDefinition):
  │     │   ├── PriorityOrdered 排序 → 执行
  │     │   ├── Ordered 排序 → 执行
  │     │   └── 其余 → 执行
  │     │   └── ★ ConfigurationClassPostProcessor 在此处理 @Configuration / @Bean / @ComponentScan / @Import
  │     │
  │     └── 再执行 BeanFactoryPostProcessor (只能修改已注册的 BeanDefinition):
  │         ├── PriorityOrdered → Ordered → 其余
  │         └── PropertySourcesPlaceholderConfigurer 在此替换 ${...}
  │
  ├── ⑥ registerBeanPostProcessors(beanFactory)
  │     ├── 按 PriorityOrdered → Ordered → 其余 注册 BeanPostProcessor
  │     ├── 注册 MergedBeanDefinitionPostProcessor (AutowiredAnnotationBeanPostProcessor, etc.)
  │     └── 注册 ApplicationListenerDetector (检测 ApplicationListener Bean)
  │
  ├── ⑦ initMessageSource()
  │     └── 如果容器中有 "messageSource" Bean → 使用；否则 → DelegatingMessageSource (代理到父容器)
  │
  ├── ⑧ initApplicationEventMulticaster()
  │     └── 如果容器中有 "applicationEventMulticaster" Bean → 使用；否则 → SimpleApplicationEventMulticaster
  │
  ├── ⑨ onRefresh()
  │     └── 子类扩展点: AbstractRefreshableWebApplicationContext 在此初始化 ThemeSource
  │
  ├── ⑩ registerListeners()
  │     ├── 将静态指定的 ApplicationListener 注册到 multicaster
  │     └── 收集 ApplicationListener Bean (不提前实例化, 只登记 beanName)
  │
  ├── ⑪ finishBeanFactoryInitialization(beanFactory)  ← ★ 实例化所有非懒加载单例
  │     ├── 冻结配置: beanFactory.freezeConfiguration()
  │     ├── 设置 ConversionService bean
  │     ├── 注册默认 Environment 相关的 Bean
  │     └── beanFactory.preInstantiateSingletons()     ← 触发所有单例 Bean 的创建
  │           └── AbstractBeanFactory.getBean(beanName)
  │                 └── 完整的 Bean 创建生命周期 (见 spring-beans.md §4.2)
  │
  └── ⑫ finishRefresh()
        ├── 清除 Resource 缓存
        ├── 初始化 LifecycleProcessor: DefaultLifecycleProcessor
        │     └── lifecycleProcessor.onRefresh() → 启动所有 SmartLifecycle Bean (按 phase 排序)
        ├── 发布 ContextRefreshedEvent
        └── 注册 ApplicationContext 到 LiveBeansView (JMX)

  异常处理:
    ├── RuntimeException/Error → 销毁已创建的单例 (destroyBeans)
    ├── 停止已启动的 Lifecycle Bean
    ├── cancelRefresh(ex) → 重置 active = false
    └── 抛出原始异常
```

### 4.2 ConfigurationClassPostProcessor 处理流程

```
ConfigurationClassPostProcessor (同时实现 BeanDefinitionRegistryPostProcessor + PriorityOrdered)
  │
  └── postProcessBeanDefinitionRegistry(registry)  ← 在 refresh() 步骤⑤中被调用
        │
        ├── ① 解析 @Configuration 类: ConfigurationClassParser.parse(configClasses)
        │     │
        │     ├── 对每个 @Configuration 类:
        │     │   ├── 解析 @PropertySource → 加载属性文件到 Environment
        │     │   ├── 解析 @ComponentScan → ClassPathBeanDefinitionScanner.scan()
        │     │   │     └── 扫描指定包的 @Component/@Service/@Repository/@Controller 类
        │     │   ├── 解析 @Import:
        │     │   │   ├── 普通类 → 作为 @Configuration 类递归解析
        │     │   │   ├── ImportSelector → selectImports() → 递归加载
        │     │   │   ├── DeferredImportSelector → 延迟到所有配置类解析完成后
        │     │   │   └── ImportBeanDefinitionRegistrar → 直接注册 BeanDefinition
        │     │   ├── 解析 @ImportResource → 加载 XML 配置
        │     │   ├── 解析 @Bean 方法 → ConfigurationClassBeanDefinitionReader
        │     │   └── 解析父类/接口上的注解 (递归)
        │     │
        │     └── 处理 DeferredImportSelector (如 Spring Boot 自动配置)
        │
        ├── ② 注册 @Bean 方法: ConfigurationClassBeanDefinitionReader.loadBeanDefinitions()
        │     │
        │     └── 将每个 @Bean 方法转为 ConfigurationClassBeanDefinition
        │           ├── 设置 factoryMethodName = @Bean 方法名
        │           ├── 设置 factoryBeanName = @Configuration 类 beanName
        │           └── 解析 @Lazy / @Primary / @DependsOn / @Scope 等
        │
        └── ③ 增强 @Configuration 类: ConfigurationClassEnhancer
              │
              └── 对每个 @Configuration 类创建 CGLIB 代理子类
                    └── 拦截 @Bean 方法调用:
                          在代理中 → getBean() (确保单例, 即使方法内多次调用)
```

### 4.3 事件发布与监听流程

```
事件发布:
  ApplicationContext.publishEvent(event)
    │
    └── AbstractApplicationContext.publishEvent(event)
          │
          ├── 如果 event 不是 ApplicationEvent → PayloadApplicationEvent 包装
          │
          ├── 如果 multicaster 已初始化:
          │     getApplicationEventMulticaster().multicastEvent(event, eventType)
          │       │
          │       ├── 解析事件类型 (含泛型 ResolvableType)
          │       ├── 查找匹配的 ApplicationListener
          │       │     ├── 静态注册的 listeners (earlyApplicationListeners)
          │       │     └── BeanFactory 中的 ApplicationListener Bean (延迟获取)
          │       ├── 过滤: 类型匹配 + @Conditional 条件
          │       ├── 排序: Ordered / @Order → 按顺序执行
          │       └── 分发:
          │             ├── 有 Executor (TaskExecutor) → listener.invoke() 在线程池执行
          │             └── 无 Executor → 同步直接调用
          │
          └── 如果仍在启动中 (multicaster 未就绪):
                earlyApplicationEvents.add(event)  ← 暂存, 等 multicaster 就绪后回放
```

```
@EventListener 处理:
  EventListenerMethodProcessor (SmartInitializingSingleton)
    │
    └── afterSingletonsInstantiated()
          └── 扫描所有 Bean 中带 @EventListener 的方法
                │
                └── 为每个 @EventListener 方法创建 ApplicationListenerMethodAdapter
                      │
                      ├── 解析监听的事件类型 (从方法参数推导)
                      ├── 解析 @EventListener.condition (SpEL 条件)
                      ├── 解析 @EventListener.id (唯一标识)
                      ├── 解析 @Order 排序
                      ├── 解析 @Async (异步执行)
                      └── 注册到 ApplicationEventMulticaster

事件调用:
  ApplicationListenerMethodAdapter.onApplicationEvent(event)
    │
    ├── 检查条件 (SpEL): conditionPassed(event) → EventExpressionEvaluator
    ├── 异步 → Executor 执行
    └── 同步 → 反射调用 @EventListener 方法
          └── 参数解析: event 对象 + 可选参数注入
```

### 4.4 @Scheduled 定时任务处理

```
ScheduledAnnotationBeanPostProcessor.postProcessAfterInitialization()
  │
  ├── 扫描 Bean 中的 @Scheduled 注解方法
  │     │
  │     ├── @Scheduled(fixedDelay)  → FixedDelayTask
  │     ├── @Scheduled(fixedRate)   → FixedRateTask
  │     ├── @Scheduled(cron)        → CronTask
  │     └── @Scheduled(initialDelay + fixedDelay/fixedRate) → 组合 Task
  │
  ├── 解析 cron 表达式:
  │     CronExpression.parse(expression)  → CronField (秒/分/时/日/月/周)
  │       └── 支持 6 位 UNIX cron + 7 位 (含秒)
  │
  └── 注册到 ScheduledTaskRegistrar:
        ├── 有 TaskScheduler Bean → 使用
        │     ThreadPoolTaskScheduler → schedule(task, trigger)
        └── 无 → 创建单线程 ExecutorService
              setRemoveOnCancelPolicy(true)  ← SPR-14637

@Async 处理:
  AsyncAnnotationBeanPostProcessor (extends AbstractAdvisingBeanPostProcessor)
    │
    └── postProcessAfterInitialization()
          └── 检测 @Async 方法 → 创建 AOP 代理
                └── AsyncExecutionInterceptor.invoke()
                      ├── 获取 Executor: @Async("executorName") → 指定 Bean → 默认 TaskExecutor
                      ├── 提交 Callable → Executor
                      └── 返回 Future / CompletableFuture / ListenableFuture
```

### 4.5 国际化 MessageSource 层次

```
ApplicationContext.getMessage(code, args, defaultMessage, locale)
  │
  └── 查找链:
        ├── 自身 BeanFactory 中的 MessageSource Bean
        │     ├── ResourceBundleMessageSource
        │     │     └── 读取 classpath: messages.properties / messages_zh_CN.properties
        │     └── ReloadableResourceBundleMessageSource
        │           └── 支持热重载 (cacheSeconds 可配置)
        │
        └── 如果自身无 MessageSource → 代理到父容器 (getParentMessageSource())
              └── 最终兜底: StaticMessageSource 或抛出 NoSuchMessageException
```

---

## 五、关键扩展点

| 扩展点 | 时机 | 用途 |
|--------|------|------|
| **ApplicationContextInitializer** | refresh() 之前 | 在刷新前自定义 Environment / ApplicationContext |
| **BeanFactoryPostProcessor** | BeanDefinition 注册后，实例化前 | 修改 Bean 元数据（如属性占位符替换） |
| **BeanDefinitionRegistryPostProcessor** | 同上（优先于 BFPP） | 注册新的 BeanDefinition（如 @Configuration 解析） |
| **ApplicationListener\<E\>** | 事件发生时 | 监听 ContextRefreshedEvent / ContextClosedEvent 等 |
| **@EventListener** | 事件发生时 | 注解驱动事件监听（支持 SpEL 条件、异步） |
| **Lifecycle / SmartLifecycle** | 容器 start()/stop() | 控制 Bean 的启停顺序 |
| **ApplicationEventMulticaster** | 事件发布时 | 自定义事件广播策略（如全局异步） |
| **MessageSource** | 需要国际化消息时 | 自定义消息加载（如从数据库加载） |
| **ApplicationStartup** | 容器启动各阶段 | 记录启动度量数据（Step 跟踪） |

---

## 六、常用内置 Bean 名

| Bean 名 | 类型 | 说明 |
|---------|------|------|
| `bootstrapExecutor` | Executor | 启动阶段并行 Bean 创建的线程池 (6.2+) |
| `conversionService` | ConversionService | 类型转换服务 |
| `loadTimeWeaver` | LoadTimeWeaver | 加载时织入器 |
| `environment` | Environment | 环境对象 |
| `systemProperties` | Map | JVM 系统属性 |
| `systemEnvironment` | Map | OS 环境变量 |
| `applicationStartup` | ApplicationStartup | 启动度量记录 |
| `messageSource` | MessageSource | 国际化消息源 |
| `applicationEventMulticaster` | ApplicationEventMulticaster | 事件广播器 |
| `lifecycleProcessor` | LifecycleProcessor | 生命周期处理器 |
| `taskScheduler` | TaskScheduler | 定时任务调度器 (被 @Scheduled 使用) |
| `taskExecutor` | TaskExecutor | 异步任务执行器 (被 @Async 使用) |

---

## 七、依赖关系

```
spring-context
  ├── api: spring-aop
  ├── api: spring-beans
  ├── api: spring-expression
  ├── api: spring-core
  ├── api: io.micrometer:micrometer-observation
  ├── optional: jakarta.inject:jakarta.inject-api
  ├── optional: jakarta.ejb:jakarta.ejb-api
  ├── optional: jakarta.validation:jakarta.validation-api
  ├── optional: jakarta.jms:jakarta.jms-api
  ├── optional: org.aspectj:aspectjweaver
  ├── optional: io.projectreactor:reactor-core
  ├── optional: io.smallrye.reactive:mutiny
  └── optional: org.hibernate.validator:hibernate-validator

---

## 八、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-aop](L3-spring-aop.md) | L3 增强 | AOP 基础设施 |
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | BeanFactory |
| 上游 | [spring-expression](L3-spring-expression.md) | L3 增强 | SpEL 表达式 |
| 下游 | [spring-context-support](L4-spring-context-support.md) | L4 上下文 | 三方集成 |
| 下游 | [spring-webmvc](L7-spring-webmvc.md) | L7 Web | Servlet MVC |
| 下游 | [spring-websocket](L7-spring-websocket.md) | L7 Web | WebSocket 支持 |
```
