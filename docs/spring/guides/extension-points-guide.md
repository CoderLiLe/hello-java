# Spring 扩展点实战指南

> 本文整理 Spring Framework 中的关键扩展点、执行时机和使用场景，帮助开发者在实际项目中正确选择和实现扩展接口。
> 参考文档：[spring-beans 模块](../modules/L2-spring-beans.md)、[spring-context 模块](../modules/L4-spring-context.md)

---

## 一、扩展点总览

```
ApplicationContextInitializer          ← 容器 refresh() 之前
  │
  ▼
BeanDefinitionRegistryPostProcessor    ← 可注册新的 BeanDefinition
  │
  ▼
BeanFactoryPostProcessor               ← 可修改已注册的 BeanDefinition
  │
  ▼
InstantiationAwareBeanPostProcessor    ← 实例化前后拦截
  │
  ▼
Bean 实例化 + 属性填充
  │
  ▼
Aware 回调 (BeanName → BeanFactory → ApplicationContext)
  │
  ▼
BeanPostProcessor.postProcessBeforeInitialization  ← @PostConstruct 在此
  │
  ▼
InitializingBean.afterPropertiesSet() + init-method
  │
  ▼
BeanPostProcessor.postProcessAfterInitialization   ← ★ AOP 代理在此
  │
  ▼
SmartInitializingSingleton.afterSingletonsInstantiated()  ← 所有单例就绪
  │
  ▼
ApplicationListener / @EventListener   ← 容器事件
  │
  ▼
SmartLifecycle.start()                 ← 容器启动完成
```

---

## 二、各扩展点详解

### 2.1 ApplicationContextInitializer

**时机**：`refresh()` 被调用之前

**用途**：在容器刷新前自定义 Environment（激活 Profile、添加 PropertySource）

```java
public class MyInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {
    @Override
    public void initialize(ConfigurableApplicationContext context) {
        context.getEnvironment().setActiveProfiles("dev");
        context.getEnvironment().getPropertySources()
            .addLast(new MapPropertySource("custom", Map.of("app.name", "MyApp")));
    }
}

// 注册方式 1: spring.factories
// META-INF/spring.factories:
// org.springframework.context.ApplicationContextInitializer=com.example.MyInitializer

// 注册方式 2: SpringApplication (Spring Boot)
// SpringApplication application = new SpringApplication(App.class);
// application.addInitializers(new MyInitializer());
```

### 2.2 BeanDefinitionRegistryPostProcessor

**时机**：所有 BeanDefinition 加载完成后，但在 Bean 实例化之前（优先于普通 BFPP）

**用途**：动态注册新的 BeanDefinition

```java
@Component
public class MyBeanRegistryPostProcessor implements BeanDefinitionRegistryPostProcessor {
    @Override
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) {
        // 动态注册一个 Bean
        BeanDefinitionBuilder builder = BeanDefinitionBuilder
            .genericBeanDefinition(MyService.class);
        registry.registerBeanDefinition("myService", builder.getBeanDefinition());
    }

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
        // 这里只能修改已注册的 BeanDefinition
    }
}
```

**典型内置实现**：`ConfigurationClassPostProcessor`（处理 @Configuration、@ComponentScan）

### 2.3 BeanFactoryPostProcessor

**时机**：BeanDefinition 注册完成后，Bean 实例化之前

**用途**：修改已注册的 BeanDefinition（如修改 scope、property 值）

```java
@Component
public class MyBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
        // 获取某个 BeanDefinition 并修改
        BeanDefinition bd = beanFactory.getBeanDefinition("userService");
        bd.setLazyInit(true);
        bd.getPropertyValues().add("timeout", 3000);
    }
}
```

**典型内置实现**：`PropertySourcesPlaceholderConfigurer`（替换 `${...}` 占位符）

### 2.4 InstantiationAwareBeanPostProcessor

**时机**：每个 Bean 实例化前后、属性填充时

**用途**：在实例化前创建代理、在属性填充时处理自定义注解

```java
@Component
public class MyInstantiationAwareBPP implements InstantiationAwareBeanPostProcessor {

    // ① 实例化前: 返回非 null 可短路后续流程
    @Override
    public Object postProcessBeforeInstantiation(Class<?> beanClass, String beanName) {
        if (beanClass == MyService.class) {
            // 返回自定义代理, 跳过 Spring 的实例化和初始化
            return Proxy.newProxyInstance(beanClass.getClassLoader(),
                beanClass.getInterfaces(), (p, m, a) -> "stub");
        }
        return null;  // null = 继续正常流程
    }

    // ② 实例化后: 返回 false 可跳过属性填充
    @Override
    public boolean postProcessAfterInstantiation(Object bean, String beanName) {
        return true;  // true = 继续填充属性
    }

    // ③ 属性填充: 处理自定义注入
    @Override
    public PropertyValues postProcessProperties(PropertyValues pvs, Object bean, String beanName) {
        // Spring 内置: AutowiredAnnotationBeanPostProcessor 在此处理 @Autowired
        //             CommonAnnotationBeanPostProcessor 在此处理 @Resource
        return pvs;
    }
}
```

**典型内置实现**：`AutowiredAnnotationBeanPostProcessor`（@Autowired、@Value 注入）

### 2.5 BeanPostProcessor

**时机**：每个 Bean 初始化前后

**用途**：包装 Bean、自定义初始化逻辑

```java
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) {
        if (bean instanceof MyService) {
            System.out.println(beanName + " 初始化前");
        }
        return bean;  // 可返回包装对象
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        if (bean instanceof MyService) {
            System.out.println(beanName + " 初始化后");
        }
        return bean;  // ★ AOP 在此返回代理对象
    }
}
```

**典型内置实现**：
- `ApplicationContextAwareProcessor`（注入 ApplicationContext 等 Aware）
- `AbstractAutoProxyCreator`（AOP 代理创建）

### 2.6 Aware 系列接口

**时机**：属性填充完成后、初始化之前

**用途**：让 Bean 获取 Spring 容器基础设施

```java
@Component
public class MyService implements ApplicationContextAware, BeanNameAware {

    private ApplicationContext context;
    private String beanName;

    @Override
    public void setBeanName(String name) { this.beanName = name; }

    @Override
    public void setApplicationContext(ApplicationContext ctx) { this.context = ctx; }

    @PostConstruct
    public void init() {
        // 此时所有 Aware 已注入完毕
        System.out.println("Bean: " + beanName + " in context: " + context.getId());
    }
}
```

### 2.7 InitializingBean / DisposableBean

```java
@Component
public class MyService implements InitializingBean, DisposableBean {

    @Override
    public void afterPropertiesSet() {
        // 属性注入完毕, 可做校验和初始化
    }

    @Override
    public void destroy() {
        // 容器关闭时清理资源
    }
}
```

### 2.8 SmartInitializingSingleton

**时机**：所有非懒加载单例 Bean 初始化完成之后

**用途**：在所有 Bean 就绪后执行一次性逻辑

```java
@Component
public class MyInitializer implements SmartInitializingSingleton {
    @Override
    public void afterSingletonsInstantiated() {
        // 所有单例 Bean 已就绪
        // 典型场景: 预热缓存、启动定时任务
    }
}
```

### 2.9 ApplicationListener / @EventListener

```java
// 方式 1: 接口
@Component
public class MyListener implements ApplicationListener<ContextRefreshedEvent> {
    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        System.out.println("容器刷新完成");
    }
}

// 方式 2: 注解 (更灵活)
@Component
public class MyEventHandler {
    @EventListener
    @Async  // 异步执行
    public void handleUserCreated(UserCreatedEvent event) {
        // 处理用户创建事件
    }

    @EventListener(condition = "#event.amount > 10000")
    public void handleLargeOrder(OrderEvent event) {
        // 只处理大额订单
    }
}
```

### 2.10 SmartLifecycle

**时机**：容器 refresh() 完成后（所有 Bean 就绪后）

**用途**：控制启动/停止顺序

```java
@Component
public class MyLifecycle implements SmartLifecycle {
    private volatile boolean running = false;

    @Override
    public void start() {
        this.running = true;
        System.out.println("自定义启动逻辑");
    }

    @Override
    public void stop() { this.running = false; }

    @Override
    public boolean isRunning() { return running; }

    @Override
    public int getPhase() { return 0; }  // 数字越大越晚启动, 越早停止
}
```

---

## 三、扩展点选择决策表

| 需求 | 推荐扩展点 |
|------|----------|
| 在容器启动前配置环境 | `ApplicationContextInitializer` |
| 动态注册新的 Bean | `BeanDefinitionRegistryPostProcessor` |
| 修改已有 Bean 的配置元数据 | `BeanFactoryPostProcessor` |
| 对特定 Bean 做包装/代理 | `BeanPostProcessor` |
| 处理自定义注入注解 | `InstantiationAwareBeanPostProcessor.postProcessProperties()` |
| 在实例化前拦截（提前返回代理） | `InstantiationAwareBeanPostProcessor.postProcessBeforeInstantiation()` |
| 获取 BeanFactory/ApplicationContext 引用 | `BeanFactoryAware` / `ApplicationContextAware` |
| Bean 初始化后校验 | `InitializingBean.afterPropertiesSet()` 或 `@PostConstruct` |
| 容器就绪后统一执行 | `SmartInitializingSingleton` 或 `ApplicationListener<ContextRefreshedEvent>` |
| 控制启动/停止顺序 | `SmartLifecycle` |

---

## 四、执行顺序注意事项

1. **多个同类型扩展点** 通过 `Ordered` / `@Order` / `PriorityOrdered` 排序
2. `PriorityOrdered` > `Ordered` > 无排序接口
3. `BeanDefinitionRegistryPostProcessor` **先于** `BeanFactoryPostProcessor` 执行
4. `BeanPostProcessor` 作用于**所有** Bean（包括 Spring 内部 Bean）
5. FactoryBean.getObject() 返回的对象只经过 `postProcessAfterInitialization()`

---

## 五、相关文档

| 文档 | 说明 |
|------|------|
| [Bean 生命周期](deep-dive/04-bean-lifecycle.md) | 各扩展点完整执行时序 |
| [容器启动流程](deep-dive/03-startup-process.md) | refresh() 中 BFPP/BPP 注册 |
| [AOP 实现](deep-dive/12-aop-implementation.md) | AbstractAutoProxyCreator 扩展点 |
| [事件系统](deep-dive/11-event-system.md) | @EventListener 详细机制 |
