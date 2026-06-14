# spring-messaging 模块功能文档

---

## 一、模块定位

spring-messaging 是 Spring 的 **消息传递抽象模块**，245 个 Java 文件（~35000 行），负责：

- **消息抽象**：Message\<T\>、MessageHeaders、MessageChannel、MessageHandler
- **消息模板**：SimpMessagingTemplate 用于发送 STOMP/WebSocket 消息
- **注解消息处理**：@MessageMapping、@SubscribeMapping、@Payload、@Header
- **STOMP 协议**：StompEncoder/Decoder、StompHeaderAccessor 双向映射
- **消息分发**：AbstractMethodMessageHandler → 参数解析 → 方法调用 → 返回值处理
- **Broker 抽象**：SimpleBrokerMessageHandler（内存）、StompBrokerRelayMessageHandler（外部）
- **用户目标解析**：/user/ 前缀 → 按用户会话路由

**依赖**：`spring-core`、`spring-beans`、`spring-context`

---

## 二、模块全景图

```
spring-messaging (245 files, ~35000 lines)
│
├── org.springframework.messaging/                     # 核心抽象 (8 files)
│   ├── Message<T>                                     — 消息接口 (Payload + Headers)
│   ├── MessageHeaders                                 — 不可变消息头 (343 lines, ID/Timestamp 自动生成)
│   ├── MessageChannel                                 — ★ 消息通道 (@FunctionalInterface)
│   ├── SubscribableChannel                            — 可订阅通道 (subscribe/unsubscribe)
│   ├── PollableChannel                                — 可轮询通道 (receive)
│   ├── MessageHandler                                 — 消息处理器 (@FunctionalInterface)
│   └── MessagingException / MessageDeliveryException  — 异常体系
│
├── org.springframework.messaging.support/             # 消息支持 (18 files)
│   ├── GenericMessage<T>                              — 标准 Message 实现 (119 lines)
│   ├── ErrorMessage                                   — 错误消息 (144 lines)
│   ├── MessageBuilder<T>                              — 流式消息构建器 (215 lines)
│   ├── MessageHeaderAccessor                          — ★ 消息头可变访问器 (697 lines)
│   ├── NativeMessageHeaderAccessor                    — 原生头支持 (302 lines)
│   ├── ChannelInterceptor                             — 通道拦截器 SPI
│   └── GenericMessagingTemplate                       — 通用消息模板
│
├── org.springframework.messaging.core/                # 消息操作 (18 files)
│   ├── AbstractMessagingTemplate<D>                   — 抽象模板 (117 lines)
│   ├── GenericMessagingTemplate                       — 通用模板 (362 lines)
│   ├── MessageRequestReplyOperations                  — 请求-回复操作接口
│   └── CachingDestinationResolverProxy                — 目标解析缓存
│
├── org.springframework.messaging.converter/            # 消息转换 (21 files)
│   ├── MessageConverter                               — 转换器 SPI (63 lines)
│   ├── SmartMessageConverter                          — 智能转换器 (带 conversionHint)
│   ├── AbstractMessageConverter                       — 抽象基类 (319 lines)
│   ├── SimpleMessageConverter                         — 简单类型直通
│   ├── StringMessageConverter                         — String ↔ byte[]
│   ├── ByteArrayMessageConverter                      — byte[] 直通
│   ├── MappingJackson2MessageConverter               — Jackson JSON (351 lines, 7.0 废弃)
│   └── CompositeMessageConverter                      — 组合转换器链 (115 lines)
│
├── org.springframework.messaging.simp/                # SiMP 协议 (71 files)
│   ├── SimpMessagingTemplate                          — ★ SiMP 消息发送模板 (269 lines)
│   ├── SimpMessageHeaderAccessor                      — SiMP 头访问器 (305 lines)
│   ├── SimpMessageType                                — 消息类型枚举
│   ├── SimpAttributes / SimpSessionScope              — WebSocket Session Scope
│   │
│   ├── simp/stomp/                                    # STOMP 协议
│   │   ├── StompEncoder                               — STOMP 编码器 (268 lines)
│   │   ├── StompDecoder                               — STOMP 解码器 (365 lines)
│   │   ├── StompHeaderAccessor                        — ★ STOMP 头访问器 (548 lines)
│   │   ├── StompCommand                               — STOMP 命令枚举 (91 lines)
│   │   ├── StompBrokerRelayMessageHandler             — ★ 外部 Broker 中继 (1202 lines)
│   │   └── DefaultStompSession                        — STOMP 客户端会话 (745 lines)
│   │
│   ├── simp/broker/                                   # Broker
│   │   ├── SimpleBrokerMessageHandler                 — ★ 内存 Broker (533 lines)
│   │   ├── AbstractBrokerMessageHandler               — Broker 抽象基类 (383 lines)
│   │   ├── DefaultSubscriptionRegistry               — 订阅注册表 (545 lines)
│   │   └── SubscriptionRegistry                       — 订阅注册接口 (56 lines)
│   │
│   ├── simp/user/                                     # 用户目标
│   │   ├── UserDestinationMessageHandler              — 用户目标处理器
│   │   ├── DefaultUserDestinationResolver             — 用户目标解析器
│   │   └── UserSessionRegistry                        — 用户会话注册
│   │
│   └── simp/annotation/                               # 注解支持
│       ├── @SubscribeMapping                          — 订阅映射注解
│       ├── @SendToUser                                — 发送给用户注解
│       ├── SimpAnnotationMethodMessageHandler          — ★ SiMP 注解消息处理器 (558 lines)
│       ├── SendToMethodReturnValueHandler             — @SendTo 返回值处理
│       └── SubscriptionMethodReturnValueHandler        — 订阅返回值处理
│
├── org.springframework.messaging.handler/              # 注解处理基础设施 (63 files)
│   ├── annotation/:
│   │   ├── @MessageMapping                            — ★ 消息映射注解 (127 lines)
│   │   ├── @Payload / @Header / @Headers              — 参数注解
│   │   └── @DestinationVariable                       — 目标变量注解
│   │
│   ├── annotation/support/:
│   │   ├── PayloadMethodArgumentResolver               — Payload 参数解析 (229 lines)
│   │   ├── HeaderMethodArgumentResolver                — Header 参数解析
│   │   └── MessageMethodArgumentResolver               — Message 参数解析 (152 lines)
│   │
│   ├── invocation/:
│   │   ├── AbstractMethodMessageHandler<T>             — ★ 方法消息处理器基类 (732 lines)
│   │   ├── HandlerMethodArgumentResolver               — 参数解析器接口 (54 lines)
│   │   ├── HandlerMethodReturnValueHandler             — 返回值处理器接口
│   │   └── InvocableHandlerMethod                      — 可调用处理器方法
│   │
│   └── MessageCondition / DestinationPatternsMessageCondition — 消息匹配条件
│
├── org.springframework.messaging.rsocket/              # RSocket 支持 (31 files)
│   └── RSocketRequester / RSocketStrategies etc.
│
└── org.springframework.messaging.tcp/                  # TCP 连接抽象 (12 files)
    ├── TcpOperations / TcpConnection                  — TCP 操作/连接接口
    └── reactor/                                       — Reactor Netty 实现
```

---

## 三、核心流程

### 3.1 STOMP over WebSocket 完整消息流

```
Client → WebSocket Frame
  │
  ├── ① StompDecoder.decode(ByteBuffer)
  │     ├── 检测心跳帧 (单个 \n)
  │     ├── 解析命令行 (CONNECT/SEND/SUBSCRIBE...)
  │     ├── 解析头 (STOMP 1.2 转义: \\, \:, \n, \r)
  │     └── 解析 Payload (content-length 或 NULL 结尾)
  │     └── 返回 Message<byte[]> (含 StompHeaderAccessor)
  │
  ├── ② clientInboundChannel.send(message)
  │     └── ExecutorSubscribableChannel
  │           └── CopyOnWriteArraySet<MessageHandler> 迭代调用
  │
  ├── ③ 路由分发:
  │     ├── 匹配 broker 前缀 (/topic, /queue)
  │     │     └── SimpleBrokerMessageHandler / StompBrokerRelayMessageHandler
  │     │
  │     └── 匹配 @MessageMapping
  │           └── SimpAnnotationMethodMessageHandler
  │
  ├── ④ SimpAnnotationMethodMessageHandler:
  │     ├── AbstractMethodMessageHandler 匹配 HandlerMethod
  │     │     ├── SimpMessageMappingInfo.getMatchingCondition(message)
  │     │     │     ├── SimpMessageTypeMessageCondition (MESSAGE vs SUBSCRIBE)
  │     │     │     └── DestinationPatternsMessageCondition (AntPath 匹配)
  │     │     └── 最佳匹配排序 (compareTo)
  │     │
  │     ├── Argument Resolvers 解析参数:
  │     │     ├── @Payload → MessageConverter 转换 + JSR-303 校验
  │     │     ├── @Header → header name → value
  │     │     ├── @Headers → Map<String, Object>
  │     │     ├── @DestinationVariable → URI template 变量
  │     │     ├── Principal → java.security.Principal
  │     │     └── Message / MessageHeaders 原生类型
  │     │
  │     ├── 调用 @MessageMapping 方法
  │     │
  │     └── Return Value Handlers 处理返回值:
  │           ├── @SendTo → SimpMessagingTemplate.convertAndSend(destination, result)
  │           ├── @SendToUser → /user/{username}/... 用户目标
  │           ├── SubscriptionMethodReturnValueHandler → 直接回复给订阅者
  │           └── CompletableFuture / Reactive 异步处理
  │
  ├── ⑤ Broker 转发:
  │     └── SimpleBrokerMessageHandler:
  │           ├── DefaultSubscriptionRegistry.findSubscriptions(message)
  │           │     └── AntPathMatcher 匹配订阅目标
  │           └── 向每个匹配会话发送消息
  │
  └── ⑥ clientOutboundChannel.send(message)
        └── StompEncoder.encode(message) → WebSocket Frame
```

### 3.2 MessageHeaderAccessor 可变性模式

```
关键设计: MessageHeaders 不可变，但通过 escape hatch 支持可变:

MessageHeaderAccessor accessor = new MessageHeaderAccessor();
accessor.setHeader("key", "value");          // 写入 MutableMessageHeaders

MessageHeaders headers = accessor.getMessageHeaders();
// headers 的 IMMUTABLE flag 仍处于 mutable 状态

accessor.setLeaveMutable(true);  // 保持可变
// 或默认转为不可变

// 反向恢复:
StompHeaderAccessor recovered = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);
// 内幕: MutableMessageHeaders 持有 back-reference 到 MessageHeaderAccessor

层次结构:
  MessageHeaderAccessor                         — 基础可变头访问
    └── NativeMessageHeaderAccessor             — + nativeHeaders (线协议头)
          └── SimpMessageHeaderAccessor         — + SiMP 强类型头
                └── StompHeaderAccessor         — + SiMP ↔ STOMP 双向映射
```

### 3.3 SimpMessagingTemplate 发送流程

```
messagingTemplate.convertAndSend("/topic/orders", order)
  │
  ├── doConvert(payload, headers, postProcessor):
  │     └── MessageConverter.toMessage(payload, headers)
  │
  ├── doSend(destination, message):
  │     ├── SimpMessageHeaderAccessor 设置 destination / messageType
  │     ├── MessageHeaderInitializer 初始化头
  │     └── sendInternal(message)
  │
  └── sendInternal(message):
        └── messageChannel.send(message)  → brokerChannel
              └── SimpleBrokerMessageHandler 接收并转发

convertAndSendToUser("john", "/queue/reply", data):
  └── 目标变为 /user/john/queue/reply
      └── UserDestinationMessageHandler 拦截
            └── DefaultUserDestinationResolver
                  └── 转换为 per-session 目标: /queue/reply-user{sessionId}
```

### 3.4 AnnotationMessageHandler 启动流程

```
@EnableWebSocketMessageBroker → 注册 SimpAnnotationMethodMessageHandler

afterPropertiesSet():
  │
  ├── ① 扫描所有 @Controller Bean
  │     └── MethodIntrospector.selectMethods() 查找 @MessageMapping / @SubscribeMapping 方法
  │
  ├── ② 为每个方法创建 SimpMessageMappingInfo
  │     ├── 目标模式 (从 @MessageMapping value)
  │     └── 消息类型 (MESSAGE 或 SUBSCRIBE)
  │
  ├── ③ 注册到 AbstractMethodMessageHandler.MappingRegistry
  │     └── registry.register(mapping, handler, method)
  │
  ├── ④ 订阅 clientInboundChannel
  │     └── clientInboundChannel.subscribe(this)
  │
  └── ⑤ 运行时消息匹配:
        ├── 直接路径查找: MappingRegistry.getMappingsByDirectPath(destination)
        └── 模式匹配: getMatchingMapping() + 排序 + 去歧义
```

---

## 四、STOMP 命令映射

| STOMP 命令 | SiMP 消息类型 | 方向 | 用途 |
|-----------|-------------|------|------|
| CONNECT | CONNECT | C→S | 连接请求 |
| CONNECTED | CONNECT_ACK | S→C | 连接确认 |
| SUBSCRIBE | SUBSCRIBE | C→S | 订阅目标 |
| UNSUBSCRIBE | UNSUBSCRIBE | C→S | 取消订阅 |
| SEND | MESSAGE | C→S | 发送消息到服务器 |
| MESSAGE | MESSAGE | S→C | 服务器推送消息到客户端 |
| DISCONNECT | DISCONNECT | C→S | 断开连接 |
| ERROR | — | S→C | 错误通知 |
| RECEIPT | — | S→C | 接收确认 |

---

## 五、Broker 对比

| 特性 | SimpleBrokerMessageHandler | StompBrokerRelayMessageHandler |
|------|---------------------------|-------------------------------|
| 类型 | 内存 Broker | 外部 Broker 中继 (RabbitMQ/ActiveMQ) |
| 部署 | 无需外部依赖 | 需要外部消息代理 |
| 适用场景 | 单实例 / 开发环境 | 多实例 / 集群 / 生产环境 |
| 订阅存储 | DefaultSubscriptionRegistry (ConcurrentHashMap) | 外部 Broker 管理 |
| 消息路由 | 直接内存转发 | 通过 TCP 中继到外部 Broker |
| 用户目标 | 内存解析 | 外部 Broker 解析 |

---

## 六、依赖关系

```
spring-messaging
  ├── api: spring-core
  ├── api: spring-beans
  ├── api: spring-context
  ├── optional: com.fasterxml.jackson.core:jackson-databind  (JSON 转换)
  ├── optional: io.micrometer:micrometer-observation
  ├── optional: io.rsocket:rsocket-core
  ├── optional: org.jetbrains.kotlin:kotlin-stdlib
  └── optional: io.projectreactor:reactor-core

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | BeanFactory |
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
| 下游 | [spring-jms](L6-spring-jms.md) | L6 消息 | JMS 集成 |
| 下游 | [spring-websocket](L7-spring-websocket.md) | L7 Web | STOMP over WebSocket |
```
