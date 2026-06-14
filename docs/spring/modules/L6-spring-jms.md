# spring-jms 模块功能文档

---

## 一、模块定位

spring-jms 是 Spring 的 **Jakarta Messaging (JMS) 集成模块**，122 个 Java 文件（~22740 行），负责：

- **JmsTemplate**：同步 JMS 操作模板（发送/接收/浏览），处理连接/会话生命周期
- **消息监听容器**：DefaultMessageListenerContainer（动态消费）和 SimpleMessageListenerContainer（简单消费）
- **@JmsListener 注解**：声明式 JMS 消息监听，自动创建容器
- **事务集成**：JmsTransactionManager（本地 JMS 事务）+ JTA/XA 支持
- **连接工厂包装**：SingleConnectionFactory、CachingConnectionFactory（会话/生产者/消费者缓存）
- **异常转换**：jakarta.jms.JMSException → Spring JmsException 体系

**依赖**：`spring-core`、`spring-beans`、`spring-context`、`spring-messaging`、`spring-tx`

---

## 二、模块全景图

```
spring-jms (122 files, ~22740 lines)
│
├── org.springframework.jms/                           # 异常体系 (14 files)
│   ├── JmsException                                   — JMS 异常基类 (101 lines)
│   └── 12 个子异常: IllegalStateException, InvalidDestinationException, ... UncategorizedJmsException
│
├── org.springframework.jms.annotation/                # 注解支持 (7 files)
│   ├── JmsListener                                    — ★ @JmsListener 注解 (144 lines)
│   ├── EnableJms                                      — ★ @EnableJms 启用注解 (272 lines)
│   └── JmsListenerAnnotationBeanPostProcessor         — ★ BPP 扫描 @JmsListener (364 lines)
│
├── org.springframework.jms.config/                    # 配置层 (15 files)
│   ├── DefaultJmsListenerContainerFactory             — 默认监听容器工厂 (165 lines)
│   ├── MethodJmsListenerEndpoint                      — 方法级监听端点 (221 lines)
│   ├── JmsListenerEndpointRegistry                    — 端点注册表 (278 lines)
│   └── JmsListenerEndpointRegistrar                    — 端点注册器 (204 lines)
│
├── org.springframework.jms.connection/                # 连接管理 (13 files)
│   ├── SingleConnectionFactory                        — ★ 单连接工厂 (819 lines)
│   ├── CachingConnectionFactory                       — ★ 缓存连接工厂 (632 lines)
│   ├── JmsTransactionManager                          — ★ JMS 事务管理器 (445 lines)
│   ├── ConnectionFactoryUtils                         — ★ 连接生命周期工具 (449 lines)
│   ├── TransactionAwareConnectionFactoryProxy         — 事务感知代理 (358 lines)
│   ├── DelegatingConnectionFactory                    — 委托连接工厂 (203 lines)
│   └── UserCredentialsConnectionFactoryAdapter       — 凭证适配 (374 lines)
│
├── org.springframework.jms.core/                     # 核心操作 (11 files)
│   ├── JmsTemplate                                    — ★ JMS 操作模板 (1244 lines)
│   ├── JmsOperations                                  — JMS 操作接口 (517 lines)
│   ├── JmsClient / DefaultJmsClient                   — ★ 6.1+ 流式 API (317 + 217 lines)
│   ├── JmsMessagingTemplate                           — Spring Messaging 集成 (582 lines)
│   └── JmsGatewaySupport                              — 网关支持 (120 lines)
│
├── org.springframework.jms.listener/                  # 监听容器 (10 files)
│   ├── DefaultMessageListenerContainer                — ★ DMLC (1604 lines, 最复杂)
│   ├── SimpleMessageListenerContainer                 — SMLC (387 lines)
│   ├── AbstractMessageListenerContainer               — 抽象消息监听容器 (1027 lines)
│   ├── AbstractPollingMessageListenerContainer       — 抽象轮询容器 (521 lines)
│   └── AbstractJmsListeningContainer                  — 抽象监听容器 (724 lines)
│
├── org.springframework.jms.listener.adapter/          # 监听适配器 (6 files)
│   ├── MessageListenerAdapter                         — 经典反射适配器 (312 lines)
│   ├── MessagingMessageListenerAdapter               — Spring Messaging 适配器 (164 lines)
│   └── AbstractAdaptableMessageListener              — 可适配抽象监听器 (588 lines)
│
├── org.springframework.jms.listener.endpoint/         # JCA 端点 (6 files)
│   ├── JmsMessageEndpointManager                      — JCA 消息端点管理器 (234 lines)
│   └── JmsActivationSpecConfig                        — JCA 激活规范配置 (291 lines)
│
├── org.springframework.jms.support/                   # 支持工具 (7 files)
│   ├── JmsAccessor                                    — 基础访问器 (244 lines)
│   ├── JmsUtils                                       — JMS 工具类 (311 lines)
│   ├── SimpleJmsHeaderMapper                          — 头映射器 (258 lines)
│   └── JmsMessageHeaderAccessor                       — 消息头访问器 (137 lines)
│
└── org.springframework.jms.support.converter/         # 消息转换 (8 files)
    ├── SimpleMessageConverter                          — 简单消息转换 (224 lines)
    ├── MappingJackson2MessageConverter                — Jackson JSON 转换 (547 lines)
    ├── MarshallingMessageConverter                    — OXM 编组转换 (317 lines)
    └── MessagingMessageConverter                      — Messaging 转换 (149 lines)
```

---

## 三、核心流程

### 3.1 JmsTemplate 消息发送流程

```
jmsTemplate.send(destination, session → session.createTextMessage("hello"))
  │
  ├── ① execute(SessionCallback, startConnection=false)
  │     │
  │     ├── ConnectionFactoryUtils.doGetTransactionalSession()
  │     │     ├── 查找 TransactionSynchronizationManager → JmsResourceHolder
  │     │     ├── 找到 → 复用事务 Session (参与外部事务)
  │     │     └── 未找到 → 创建新 Connection + Session
  │     │
  │     └── action.doInJms(session)
  │           │
  │           └── ② doSend(session, destination, messageCreator)
  │                 ├── 创建 MessageProducer
  │                 ├── messageCreator.createMessage(session)
  │                 ├── doSend(producer, message)
  │                 │     ├── 应用 deliveryDelay
  │                 │     └── 应用 QoS (deliveryMode, priority, timeToLive)
  │                 ├── 如 sessionTransacted 且 locallyTransacted → commit
  │                 └── 关闭 MessageProducer
  │
  └── ③ finally: 关闭 Session, 释放 Connection
```

### 3.2 DefaultMessageListenerContainer 动态伸缩消费

```
容器初始化:
  │
  ├── doInitialize()
  │     └── 创建 concurrentConsumers 个 AsyncMessageListenerInvoker
  │           └── taskExecutor.execute(invoker)
  │
  └── 每个 invoker 线程运行 run():
        │
        ├── 无限循环:
        │     ├── initResourcesIfNecessary()
        │     │     └── 依据 cacheLevel 创建/复用 Session, MessageConsumer
        │     │           CACHE_NONE(0) → 每次新建
        │     │           CACHE_CONNECTION(1) → 共享 Connection
        │     │           CACHE_SESSION(2) → 共享 Session
        │     │           CACHE_CONSUMER(3) → 共享 Consumer (默认用于本地事务)
        │     │           CACHE_AUTO(4) → 自动选择 (外部 TM → CACHE_NONE)
        │     │
        │     ├── receiveAndExecute(invoker, session, consumer)
        │     │     ├── 如配置外部 transactionManager:
        │     │     │     tm.getTransaction() → doReceiveAndExecute() → commit/rollback
        │     │     └── 否则直接 doReceiveAndExecute()
        │     │           ├── receiveMessage(consumer)  // consumer.receive(timeout)
        │     │           ├── 收到消息:
        │     │           │     ├── Micrometer observation 创建
        │     │           │     ├── bind LocallyExposedJmsResourceHolder (如 exposeListenerSession)
        │     │           │     ├── doExecuteListener(session, message)
        │     │           │     │     └── invokeListener() → MessageListener.onMessage()
        │     │           │     ├── commitIfNecessary(session) / rollbackOnExceptionIfNecessary()
        │     │           │     └── handleListenerException(ex) 失败时
        │     │           │
        │     │           └── 消息来时:
        │     │                 ├── messageReceived(invoker) → scheduleNewInvokerIfAppropriate()
        │     │                 │     └── currentCount < maxConcurrentConsumers → 扩展
        │     │                 └── 长时间空闲: self-remove (invoker 自我终止)
        │     │
        │     └── 异常恢复: 清理资源, BackOff 重试, 刷新连接
        │
        └── 退出条件: 空闲超时 / 关闭信号

动态伸缩策略:
  扩展: messageReceived() → currentInvokerCount < maxConcurrentConsumers → add invoker
  收缩: idleReceivesPerTaskLimit 次连续空闲 → invoker self-terminate
```

### 3.3 @JmsListener 注解处理流程

```
ApplicationContext 启动:
  │
  ├── ① @EnableJms → 导入 JmsBootstrapConfiguration
  │     └── 注册 JmsListenerAnnotationBeanPostProcessor + JmsListenerEndpointRegistry
  │
  ├── ② BPP.postProcessAfterInitialization(bean):
  │     └── MethodIntrospector.selectMethods() 扫描 @JmsListener 方法
  │           ├── 创建 MethodJmsListenerEndpoint
  │           ├── 解析: destination, selector, subscription, concurrency
  │           └── JmsListenerEndpointRegistrar.registerEndpoint(endpoint, factory)
  │
  ├── ③ BPP.afterSingletonsInstantiated():
  │     └── registrar.afterPropertiesSet()
  │           └── 对每个 endpoint:
  │                 ├── factory.createListenerContainer(endpoint)
  │                 │     └── 创建 DefaultMessageListenerContainer
  │                 │     └── setupMessageListener(MessagingMessageListenerAdapter)
  │                 │           └── InvocableHandlerMethod (包装 @JmsListener 方法)
  │                 └── registry.registerListenerContainer(id, container)
  │                       └── autoStartup → container.start()
  │
  └── ④ 消息消费时:
        MessagingMessageListenerAdapter.onMessage(jmsMessage, session):
          ├── toMessagingMessage(jmsMessage)         // JMS → Spring Message
          ├── invokeHandler(message, jmsMessage, session)
          │     └── handlerMethod.invoke()            // 调用 @JmsListener 方法
          └── 如有返回值 → handleResult()
                └── 发送 reply 到 JMSReplyTo / @SendTo destination
```

### 3.4 事务集成

```
JmsTransactionManager (本地 JMS 事务):
  │
  ├── doBegin():
  │     ├── 创建 Connection + transacted Session
  │     ├── 包装为 JmsResourceHolder
  │     └── 绑定到 TransactionSynchronizationManager
  │
  ├── doCommit(): session.commit()
  ├── doRollback(): session.rollback()
  └── doCleanupAfterCompletion(): 解绑 + 关闭资源

外部 JTA 事务 (DMLC + PlatformTransactionManager):
  │
  ├── DMLC 配置外部 transactionManager
  ├── receiveAndExecute() 包装:
  │     └── tm.getTransaction() → 接收消息 → 执行业务 → commit/rollback
  ├── CACHE_AUTO → CACHE_NONE (每次创建新资源以参与 XA)
  └── 业务异常 → status.setRollbackOnly() → JMS 消息不确认 (redelivery)

JmsTemplate 事务参与:
  ├── execute() → ConnectionFactoryUtils.doGetTransactionalSession()
  ├── 找到事务 JmsResourceHolder → 复用相同 Session
  └── 未找到 → 创建新连接/会话, 自行提交
```

### 3.5 异常转换

```
JmsUtils.convertJmsAccessException(JMSException):
  │
  ├── jakarta.jms.IllegalStateException       → IllegalStateException
  ├── jakarta.jms.InvalidClientIDException    → InvalidClientIDException
  ├── jakarta.jms.InvalidDestinationException → InvalidDestinationException
  ├── jakarta.jms.InvalidSelectorException    → InvalidSelectorException
  ├── jakarta.jms.JMSSecurityException        → JmsSecurityException
  ├── jakarta.jms.MessageEOFException         → MessageEOFException
  ├── jakarta.jms.MessageFormatException      → MessageFormatException
  ├── jakarta.jms.MessageNotReadableException → MessageNotReadableException
  ├── jakarta.jms.MessageNotWriteableException→ MessageNotWriteableException
  ├── jakarta.jms.ResourceAllocationException → ResourceAllocationException
  ├── jakarta.jms.TransactionInProgressException → TransactionInProgressException
  ├── jakarta.jms.TransactionRolledBackException → TransactionRolledBackException
  └── 其他 JMSException                      → UncategorizedJmsException

异常链处理: 自动解析 JMSException.getLinkedException() 合并错误消息
```

---

## 四、连接工厂对比

| 类型 | 用途 | 特点 |
|------|------|------|
| `SingleConnectionFactory` | 测试 / 简单场景 | 单连接, 忽略 close(), 支持自动重连 |
| `CachingConnectionFactory` | 生产环境 | 缓存 Session/Producer/Consumer, 按 ack-mode 分池 |
| `TransactionAwareConnectionFactoryProxy` | 事务参与 | 代理 close() 路由到 ConnectionFactoryUtils |
| `DelegatingConnectionFactory` | 装饰器基类 | 委托所有调用到 target |
| `UserCredentialsConnectionFactoryAdapter` | 凭证注入 | 包装目标, 注入 user/password |

---

## 五、消息容器对比

| 特性 | DefaultMessageListenerContainer | SimpleMessageListenerContainer |
|------|-------------------------------|-------------------------------|
| 消费模式 | 轮询 (receive) | 回调 (setMessageListener) |
| 动态伸缩 | ✅ (concurrentConsumers → maxConcurrentConsumers) | ❌ (固定消费者数) |
| 外部 TM 支持 | ✅ (PlatformTransactionManager) | ❌ |
| 自动恢复 | ✅ (BackOff 重试) | ✅ (ExceptionListener) |
| 共享连接 | ❌ | ✅ (始终共享) |
| JCA 兼容 | ❌ | ❌ (用 JmsMessageEndpointManager) |
| 消费者缓存 | ✅ (CACHE_NONE → CACHE_CONSUMER) | ❌ |

---

## 六、依赖关系

```
spring-jms
  ├── api: spring-core
  ├── api: spring-beans
  ├── api: spring-context
  ├── api: spring-messaging
  ├── api: spring-tx
  ├── optional: jakarta.jms:jakarta.jms-api
  ├── optional: com.fasterxml.jackson.core:jackson-databind  (JSON 消息转换)
  ├── optional: spring-oxm                                    (OXM 消息转换)
  ├── optional: io.micrometer:micrometer-observation           (观测)
  └── optional: org.jetbrains.kotlin:kotlin-stdlib

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-messaging](L6-spring-messaging.md) | L6 消息 | 消息抽象 |
| 上游 | [spring-tx](L5-spring-tx.md) | L5 事务 | JmsTransactionManager |
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
| 下游 | 企业消息系统 | — | JMS 消息消费者/生产者 |
```
