# Spring 事件发布与监听机制源码深度解析

> 本文深入分析 Spring 事件系统的完整实现，覆盖 ApplicationEvent 层次、ApplicationListener 与 @EventListener 两种监听方式、ApplicationEventMulticaster 广播机制、泛型事件精确匹配、异步事件执行以及启动早期事件缓冲回放机制。
> 相关模块文档：[spring-context](../modules/L4-spring-context.md)、[spring-beans](../modules/L2-spring-beans.md)

---

## 一、事件系统核心接口

```
┌─────────────────────────────┐
│   ApplicationEvent          │  ← 事件基类 (extends EventObject)
│   - timestamp               │
│   - source                  │
├─────────────────────────────┤
│   ApplicationListener<E>    │  ← 监听器接口 (extends EventListener)
│   - onApplicationEvent(E)   │
├─────────────────────────────┤
│   ApplicationEventPublisher │  ← 事件发布接口
│   - publishEvent(Object)    │
├─────────────────────────────┤
│   ApplicationEventMulticaster│  ← ★ 事件广播器 (核心)
│   - multicastEvent(event)   │
│   - addApplicationListener  │
│   - removeApplicationListener│
└─────────────────────────────┘
```

---

## 二、ApplicationEvent 事件层次

### 2.1 内置事件

```
EventObject (JDK)
  └── ApplicationEvent
        ├── ApplicationContextEvent
        │     ├── ContextRefreshedEvent    — refresh() 完成后
        │     ├── ContextStartedEvent      — start() 调用后
        │     ├── ContextStoppedEvent      — stop() 调用后
        │     └── ContextClosedEvent       — close() 调用后
        │
        ├── RequestHandledEvent            — 请求处理完成 (已废弃)
        │
        └── PayloadApplicationEvent<T>    — ★ 通用 payload 事件 (Spring 4.2+)
              └── 包装任意 Object 为事件
```

### 2.2 自定义事件

```java
// 方式一: 继承 ApplicationEvent (传统)
public class OrderCreatedEvent extends ApplicationEvent {
    private final Order order;
    public OrderCreatedEvent(Object source, Order order) {
        super(source);
        this.order = order;
    }
    public Order getOrder() { return order; }
}

// 方式二: 任意 POJO (Spring 4.2+, 自动包装为 PayloadApplicationEvent)
// 不需要继承 ApplicationEvent!
public class OrderCancelledEvent {
    private final Long orderId;
    // ...
}

// 发布
context.publishEvent(new OrderCancelledEvent(12345L));
// 自动包装为: new PayloadApplicationEvent<>(source, payload)
```

---

## 三、ApplicationEventMulticaster 广播机制

### 3.1 SimpleApplicationEventMulticaster

```java
public class SimpleApplicationEventMulticaster extends AbstractApplicationEventMulticaster {

    @Nullable
    private Executor taskExecutor;   // 如果设置 → 异步广播
    @Nullable
    private ErrorHandler errorHandler;  // 异步模式下的异常处理

    @Override
    public void multicastEvent(ApplicationEvent event, ResolvableType eventType) {
        ResolvableType type = (eventType != null ? eventType : resolveDefaultEventType(event));

        // ① 收集匹配的监听器
        Collection<ApplicationListener<?>> listeners = getApplicationListeners(event, type);

        // ② 逐个执行
        for (ApplicationListener<?> listener : listeners) {
            Executor executor = getTaskExecutor();
            if (executor != null) {
                // ★ 异步执行
                executor.execute(() -> invokeListener(listener, event));
            } else {
                // 同步执行 (默认)
                invokeListener(listener, event);
            }
        }
    }

    protected void invokeListener(ApplicationListener<?> listener, ApplicationEvent event) {
        ErrorHandler errorHandler = getErrorHandler();
        if (errorHandler != null) {
            try {
                doInvokeListener(listener, event);
            } catch (Throwable err) {
                errorHandler.handleError(err);
            }
        } else {
            doInvokeListener(listener, event);
        }
    }

    private void doInvokeListener(ApplicationListener listener, ApplicationEvent event) {
        listener.onApplicationEvent(event);
    }
}
```

### 3.2 泛型事件精确匹配 — resolveDefaultEventType()

```
SimpleApplicationEventMulticaster 继承 AbstractApplicationEventMulticaster, 
其构造函数设置了默认的 ListenerRetriever:

AbstractApplicationEventMulticaster:
  ├── defaultRetriever: ListenerRetriever
  │     └── applicationListeners: Set<ApplicationListener<?>>
  │     └── applicationListenerBeans: Set<String> (beanName, 延迟获取)
  │
  └── retrieverCache: Map<ListenerCacheKey, ListenerRetriever>
        └── 缓存: (eventType, sourceType) → 匹配的 listeners

getApplicationListeners(event, eventType):
  │
  ├── ① 构造缓存 key: new ListenerCacheKey(eventType, sourceType)
  ├── ② 从 retrieverCache 获取缓存的 listeners → 命中则返回
  │
  └── ③ 缓存未命中 → 匹配 + 缓存:
        ├── 遍历 defaultRetriever.applicationListeners:
        │     └── supportsEvent(listener, eventType, sourceType):
        │           │
        │           ├── GenericApplicationListener → supportsEventType()
        │           │
        │           └── 普通 ApplicationListener:
        │                 └── ResolvableType 解析泛型参数:
        │                       ApplicationListener<OrderCreatedEvent>
        │                         → 解析泛型得出 OrderCreatedEvent
        │                         → eventType.isAssignableFrom(OrderCreatedEvent)?
        │                           YES → 匹配!
        │
        └── 排序: AnnotationAwareOrderComparator.sort(allListeners)
              └── 返回排序后的列表
```

### 3.3 泛型事件匹配示例

```java
// 监听泛型 Payload 事件
@Component
public class OrderEventListener implements ApplicationListener<PayloadApplicationEvent<OrderCreatedEvent>> {
    @Override
    public void onApplicationEvent(PayloadApplicationEvent<OrderCreatedEvent> event) {
        OrderCreatedEvent payload = event.getPayload();  // 类型安全
        // ...
    }
}

Spring 解析:
  ApplicationListener<PayloadApplicationEvent<OrderCreatedEvent>>
    → ResolvableType.forClass(this.getClass()).as(ApplicationListener.class).getGeneric(0)
    → 解析为: PayloadApplicationEvent<OrderCreatedEvent>

匹配时:
  event = PayloadApplicationEvent(source, OrderCreatedEvent(...))
  eventType = ResolvableType.forInstance(event)  → PayloadApplicationEvent<OrderCreatedEvent>
  → isAssignableFrom → YES ✓
```

---

## 四、@EventListener 注解驱动

### 4.1 注解定义

```java
@Target({ElementType.METHOD, ElementType.ANNOTATION_TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface EventListener {
    @AliasFor("classes")
    Class<?>[] value() default {};           // 监听的事件类型
    @AliasFor("value")
    Class<?>[] classes() default {};
    String condition() default "";            // ★ SpEL 条件
    String id() default "";                   // 唯一标识符
}
```

### 4.2 使用示例

```java
@Component
public class OrderEventHandler {

    // ① 基本用法: 方法参数类型决定监听的事件类型
    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        System.out.println("订单创建: " + event.getOrderId());
    }

    // ② SpEL 条件过滤
    @EventListener(condition = "#event.amount > 10000")
    public void handleLargeOrder(OrderCreatedEvent event) {
        System.out.println("大额订单: " + event.getAmount());
    }

    // ③ 监听多个事件类型
    @EventListener({OrderCreatedEvent.class, OrderCancelledEvent.class})
    public void handleOrderEvent(Object event) { ... }

    // ④ 方法返回值 → 发布新事件 (事件链)
    @EventListener
    public OrderConfirmedEvent handle(OrderCreatedEvent event) {
        // 返回非 null → 自动发布新事件
        return new OrderConfirmedEvent(event.getOrder());
    }

    // ⑤ 异步执行
    @EventListener
    @Async
    public void handleAsync(OrderCreatedEvent event) { ... }

    // ⑥ 监听泛型 Payload
    @EventListener
    public void handleStringPayload(PayloadApplicationEvent<String> event) {
        String payload = event.getPayload();
    }
}
```

### 4.3 EventListenerMethodProcessor — 注册流程

```
EventListenerMethodProcessor implements SmartInitializingSingleton:
  │
  └── afterSingletonsInstantiated():  ← 所有单例 Bean 创建完成后
        │
        └── 遍历所有单例 Bean:
              └── processBean(beanName, beanType):
                    │
                    ├── 查找 @EventListener 方法
                    │     └── AnnotatedElementUtils.hasAnnotation(method, EventListener.class)
                    │
                    ├── 对每个方法创建 ApplicationListenerMethodAdapter:
                    │     │
                    │     ├── 解析监听事件类型:
                    │     │     ├── @EventListener(value = {A.class, B.class}) → 直接使用
                    │     │     └── 未指定 → 从方法第一个参数推导 (sourceClass)
                    │     │
                    │     ├── 解析条件: @EventListener(condition = "SpEL")
                    │     │     → EventExpressionEvaluator (SpEL)
                    │     │
                    │     ├── 解析标识: @EventListener(id = "xxx")
                    │     │
                    │     ├── 解析排序: @Order 注解
                    │     │
                    │     └── 解析异步: @Async 注解
                    │           └── 如果方法上有 @Async → 标记为异步执行
                    │
                    └── 注册到 ApplicationEventMulticaster:
                          applicationEventMulticaster.addApplicationListener(adapter)
```

### 4.4 ApplicationListenerMethodAdapter

```java
public class ApplicationListenerMethodAdapter implements GenericApplicationListener {

    private final String beanName;
    private final Method method;
    private final Method targetMethod;       // 桥接方法回到原始方法
    private final int order;
    private final String listenerId;
    private final ResolvableType declaredEventType;  // 已解析的泛型事件类型
    @Nullable
    private final String condition;          // SpEL 条件

    @Override
    public void onApplicationEvent(ApplicationEvent event) {
        processEvent(event);
    }

    public void processEvent(ApplicationEvent event) {
        // ① 获取方法参数
        Object[] args = resolveArguments(event);
        // ② 检查 SpEL 条件
        if (shouldHandle(event, args)) {
            // ③ 反射调用
            Object result = doInvoke(args);
            // ④ 如果有返回值 → 发布为新事件
            if (result != null) {
                handleResult(result);
            }
        }
    }

    // SpEL 条件判断
    private boolean shouldHandle(ApplicationEvent event, Object[] args) {
        if (condition == null) return true;
        EvaluationContext context = new StandardEvaluationContext();
        context.setVariable("event", event);              // #event
        context.setVariable("args", args);                 // #args
        context.setVariable("rootObject", ...);            // #root
        // 预编译 + 缓存 SpEL
        return evaluator.condition(condition, event, targetMethod, ...);
    }

    // 返回值处理: 非 null → 发布新事件
    private void handleResult(Object result) {
        if (eventPublisher != null) {
            eventPublisher.publishEvent(result);
        }
    }
}
```

---

## 五、事件发布完整链路

### 5.1 publishEvent() 流程

```
AbstractApplicationContext.publishEvent(Object event):
  │
  ├── ① 包装事件:
  │     ├── ApplicationEvent → 直接使用
  │     └── 普通 Object → 包装为 PayloadApplicationEvent<>(this, event)
  │
  ├── ② 早期事件处理:
  │     └── if (applicationEventMulticaster == null):
  │           → this.earlyApplicationEvents.add(event)
  │           → return  (暂存, 待步骤⑩回放)
  │
  └── ③ 广播事件 (multicaster 已就绪):
        ├── getApplicationEventMulticaster().multicastEvent(event, eventType)
        │     └── SimpleApplicationEventMulticaster.multicastEvent():
        │           ├── 收集匹配的 listeners (§3.2)
        │           ├── 排序: AnnotationAwareOrderComparator
        │           └── 执行: Executor? → async : sync
        │
        └── ④ 传播到父容器:
              if (getParent() != null && event instanceof ApplicationEvent):
                  getParent().publishEvent(event)
```

### 5.2 早期事件缓冲与回放

```
refresh() 启动时序中的事件处理:

Step ⑧: initApplicationEventMulticaster()
  └── 创建 SimpleApplicationEventMulticaster
      BUT: 尚未注册 ApplicationListener Bean (虽然 multicaster 已创建)

Step ⑩: registerListeners():
  ├── 注册静态 listeners (getApplicationListeners())
  ├── 收集 ApplicationListener Bean 的 beanName (不实例化!)
  │     └── ApplicationListenerDetector.postProcessAfterInitialization() 负责自动注册
  │
  └── ★ 回放早期事件:
        Set<ApplicationEvent> earlyEventsToProcess = this.earlyApplicationEvents;
        this.earlyApplicationEvents = null;  // 清空
        for (ApplicationEvent earlyEvent : earlyEventsToProcess) {
            getApplicationEventMulticaster().multicastEvent(earlyEvent);
        }

早期事件来源:
  - ApplicationContextInitializer 中发布的事件
  - preInstantiateSingletons() 早期阶段发布的事件
  - SmartLifecycle.start() 中的事件
```

---

## 六、ApplicationListener 发现机制

### 6.1 ApplicationListenerDetector

```java
// 这是一个内部的 BeanPostProcessor
class ApplicationListenerDetector implements DestructionAwareBeanPostProcessor, MergedBeanDefinitionPostProcessor {

    // 存储 ApplicationListener Bean 的 beanName
    private final transient Map<String, Boolean> singletonNames = new ConcurrentHashMap<>(256);

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        if (bean instanceof ApplicationListener<?> applicationListener) {
            // ★ 添加到 multicaster
            Boolean flag = this.singletonNames.get(beanName);
            if (Boolean.TRUE.equals(flag)) {
                this.applicationContext.addApplicationListener(applicationListener);
            }
        }
        return bean;
    }

    @Override
    public void postProcessBeforeDestruction(Object bean, String beanName) {
        if (bean instanceof ApplicationListener<?> applicationListener) {
            this.applicationContext.removeApplicationListener(applicationListener);
        }
    }
}
```

### 6.2 三种注册方式对比

```
方式一: implements ApplicationListener<E>
  → ApplicationListenerDetector 自动发现并注册
  → 泛型参数自动解析为监听的事件类型

方式二: @EventListener 注解
  → EventListenerMethodProcessor (SmartInitializingSingleton)
  → 包装为 ApplicationListenerMethodAdapter
  → 注册到 ApplicationEventMulticaster

方式三: 编程式注册
  → context.addApplicationListener(listener)
  → 或 spring.factories: org.springframework.context.ApplicationListener=...
```

---

## 七、异步事件执行

```
配置异步:
  @Bean
  public ApplicationEventMulticaster applicationEventMulticaster() {
      SimpleApplicationEventMulticaster multicaster = new SimpleApplicationEventMulticaster();
      multicaster.setTaskExecutor(new SimpleAsyncTaskExecutor());
      multicaster.setErrorHandler(t -> log.error("事件处理异常", t));
      return multicaster;
  }

或者对单个 @EventListener 异步:
  @EventListener
  @Async
  public void handle(OrderCreatedEvent event) {
      // 在异步线程池中执行
  }
```

---

## 八、@TransactionalEventListener

```java
@Component
public class OrderEventHandler {

    // 在事务成功提交后才执行
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onOrderCreated(OrderCreatedEvent event) {
        // 发送通知邮件 (事务已提交, 订单已持久化)
    }

    // 在事务回滚后执行
    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void onOrderFailed(OrderCreatedEvent event) { ... }
}

实现原理:
  TransactionalEventListener 的 TransactionPhase:
    - BEFORE_COMMIT     → 注册为 TransactionSynchronization.beforeCommit()
    - AFTER_COMMIT      → 注册为 TransactionSynchronization.afterCommit()
    - AFTER_ROLLBACK    → 注册为 TransactionSynchronization.afterCompletion(STATUS_ROLLED_BACK)
    - AFTER_COMPLETION   → 注册为 TransactionSynchronization.afterCompletion(any)
  
  仅在当前线程有活跃事务时才生效, 否则:
    - fallbackExecution() = true → 立即执行
    - fallbackExecution() = false → 丢弃 (默认 false)
```

---

## 九、相关文档

| 文档 | 说明 |
|------|------|
| [spring-context 模块文档](../modules/L4-spring-context.md) | ApplicationEventMulticaster 配置 |
| [容器启动流程深度解析](03-startup-process.md) | refresh() 中事件相关步骤 |
| [事务实现深度解析](13-transaction-implementation.md) | @TransactionalEventListener |
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | ApplicationListenerDetector |
