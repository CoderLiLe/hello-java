# spring-websocket 模块功能文档

---

## 一、模块定位

spring-websocket 是 Spring 的 **WebSocket 协议支持模块**，170 个 Java 文件（~22000 行），负责：

- **WebSocket 核心抽象**：WebSocketHandler、WebSocketSession、手部（Handshake）基础设施
- **STOMP over WebSocket**：SubProtocolWebSocketHandler 桥接 WebSocket 与 Spring Messaging 层
- **SockJS 降级支持**：HTTP 长轮询/流式传输/EventSource/HTMLFile 等传输降级
- **Java/XML 配置**：@EnableWebSocket、@EnableWebSocketMessageBroker 及对应 XML namespace
- **多运行时适配**：Reactor Netty、Tomcat、Jetty、Undertow、Jakarta WebSocket (JSR-356)
- **客户端支持**：WebSocketStompClient、SockJsClient

**依赖**：`spring-core`、`spring-beans`、`spring-context`、`spring-messaging`、`spring-web`、`spring-webmvc`

---

## 二、模块全景图

```
spring-websocket (170 files, ~22000 lines)
│
├── org.springframework.web.socket/                    # 核心接口 (11 files)
│   ├── WebSocketHandler                               — ★ WebSocket 处理器接口 (80 lines)
│   ├── WebSocketSession                               — ★ WebSocket 会话接口 (151 lines)
│   ├── WebSocketMessage<T>                            — 消息抽象 (Text/Binary/Ping/Pong)
│   ├── CloseStatus                                    — 关闭状态码 (224 lines, RFC 6455)
│   ├── WebSocketHttpHeaders                           — WebSocket HTTP 头 (191 lines)
│   └── WebSocketExtension                             — 协议扩展 (172 lines)
│
├── org.springframework.web.socket.handler/            # Handler 实现 (12 files)
│   ├── AbstractWebSocketHandler                       — 空实现基类 (78 lines)
│   ├── TextWebSocketHandler / BinaryWebSocketHandler  — 类型安全处理器
│   ├── ExceptionWebSocketHandlerDecorator             — ★ 异常包裹装饰器 (101 lines)
│   ├── LoggingWebSocketHandlerDecorator               — 日志装饰器 (75 lines)
│   ├── ConcurrentWebSocketSessionDecorator            — ★ 并发安全装饰器 (311 lines)
│   ├── PerConnectionWebSocketHandler                  — 每连接新 Handler 实例 (138 lines)
│   └── WebSocketHandlerDecorator                      — 装饰器基类 (98 lines)
│
├── org.springframework.web.socket.messaging/          # STOMP 子协议 (13 files)
│   ├── SubProtocolHandler                             — 子协议处理器 SPI (89 lines)
│   ├── StompSubProtocolHandler                        — ★ STOMP 协议处理器 (809 lines)
│   ├── SubProtocolWebSocketHandler                    — ★ WebSocket-消息桥接器 (716 lines)
│   ├── WebSocketAnnotationMethodMessageHandler        — WebSocket @ControllerAdvice (124 lines)
│   ├── DefaultSimpUserRegistry                        — 用户注册 (359 lines)
│   ├── WebSocketStompClient                           — 客户端 STOMP (583 lines)
│   └── SessionConnectEvent / SessionDisconnectEvent    — 会话事件
│
├── org.springframework.web.socket.server/             # 握手基础设施 (12 files)
│   ├── HandshakeHandler                               — 握手处理器 SPI (56 lines)
│   ├── HandshakeInterceptor                           — 握手拦截器 (62 lines)
│   ├── RequestUpgradeStrategy                         — 升级策略 (71 lines)
│   ├── support/:
│   │   ├── AbstractHandshakeHandler                   — ★ 核心握手逻辑 (363 lines)
│   │   │     ├── 校验 HTTP Method (GET/CONNECT)
│   │   │     ├── 校验 Upgrade: WebSocket / Connection: Upgrade
│   │   │     ├── 校验 Sec-WebSocket-Key
│   │   │     ├── 校验 Origin
│   │   │     ├── 协商子协议 (SubProtocolCapable)
│   │   │     └── 委托 RequestUpgradeStrategy.upgrade()
│   │   ├── DefaultHandshakeHandler                    — 自动检测运行时 (61 lines)
│   │   ├── WebSocketHttpRequestHandler                — ★ Servlet HttpRequestHandler (197 lines)
│   │   ├── HandshakeInterceptorChain                  — 拦截器链 (88 lines)
│   │   ├── OriginHandshakeInterceptor                 — Origin 校验 (149 lines)
│   │   └── HttpSessionHandshakeInterceptor            — HttpSession 拷贝 (177 lines)
│   │
│   └── standard/: StandardWebSocketUpgradeStrategy / JettyRequestUpgradeStrategy
│
├── org.springframework.web.socket.adapter/            # 会话适配器 (12 files)
│   ├── AbstractWebSocketSession<T>                    — 会话抽象基类 (158 lines)
│   ├── standard/: StandardWebSocketSession (229 lines)
│   └── jetty/: JettyWebSocketSession (256 lines)
│
├── org.springframework.web.socket.sockjs/             # SockJS (66 files)
│   ├── SockJsService                                  — SockJS 服务接口 (63 lines)
│   ├── support/: AbstractSockJsService                — ★ 路由逻辑 (666 lines)
│   │     ├── /info → JSON 服务器信息
│   │     ├── /iframe.html → SockJS iframe 页面
│   │     ├── /websocket → 原生 WebSocket
│   │     └── /{serverId}/{sessionId}/{transport} → 传输路由
│   ├── transport/:
│   │   ├── TransportHandlingSockJsService              — ★ 传输处理 (432 lines)
│   │   ├── TransportHandler / TransportType           — 传输处理器 SPI (6 种传输)
│   │   └── handler/:
│   │       ├── DefaultSockJsService                    — 预注册所有传输 (112 lines)
│   │       ├── WebSocketTransportHandler               — 原生 WebSocket (139 lines)
│   │       ├── XhrPollingTransportHandler              — 长轮询 (67 lines)
│   │       ├── XhrStreamingTransportHandler            — HTTP 流 (92 lines)
│   │       ├── XhrReceivingTransportHandler            — XHR 发送 (52 lines)
│   │       ├── EventSourceTransportHandler             — SSE (83 lines)
│   │       └── HtmlFileTransportHandler               — IE iframe (154 lines)
│   │
│   ├── transport/session/:
│   │   ├── AbstractSockJsSession                       — 会话状态机 + 心跳 (459 lines)
│   │   ├── AbstractHttpSockJsSession                   — ★ HTTP 会话 (353 lines)
│   │   ├── PollingSockJsSession / StreamingSockJsSession / WebSocketServerSockJsSession
│   │   └── SockJsWebSocketHandler                      — SockJS WebSocket 处理 (106 lines)
│   │
│   ├── frame/: SockJsFrame / SockJsMessageCodec        — SockJS 协议帧
│   └── client/: SockJsClient / XhrTransport variants   — ★ SockJS 客户端
│
├── org.springframework.web.socket.config/             # 配置支持 (26 files)
│   ├── annotation/:
│   │   ├── @EnableWebSocket                            — 启用 WebSocket (67 lines)
│   │   ├── @EnableWebSocketMessageBroker               — 启用 STOMP Broker (69 lines)
│   │   ├── WebSocketConfigurer                         — WebSocket 配置回调 (35 lines)
│   │   ├── WebSocketMessageBrokerConfigurer             — Broker 配置回调 (131 lines)
│   │   ├── WebSocketTransportRegistration              — 传输配置 (194 lines)
│   │   └── SockJsServiceRegistration                   — SockJS 配置 (317 lines)
│   │
│   ├── WebSocketHandlerMapping                         — Handler URL 映射 (135 lines)
│   └── MessageBrokerBeanDefinitionParser               — XML Broker 解析 (737 lines)
│
└── org.springframework.web.socket.client/             # WebSocket 客户端 (10 files)
    ├── WebSocketClient                                 — 客户端接口
    ├── WebSocketConnectionManager                      — 连接管理器 (178 lines)
    └── standard/: StandardWebSocketClient              — Jakarta 标准客户端 (219 lines)
```

---

## 三、核心流程

### 3.1 WebSocket 握手流程

```
HttpServletRequest 到达
  │
  ├── WebSocketHandlerMapping.getHandlerInternal()
  │     └── URL 匹配 → WebSocketHttpRequestHandler
  │
  ├── WebSocketHttpRequestHandler.handleRequest():
  │     ├── 包装为 ServerHttpRequest/ServerHttpResponse
  │     ├── HandshakeInterceptorChain.applyBeforeHandshake()
  │     │     └── 逐个 interceptor.beforeHandshake() (属性 Map 传递)
  │     │
  │     ├── HandshakeHandler.doHandshake() → AbstractHandshakeHandler:
  │     │     ├── ① 校验 HTTP Method (GET 或 CONNECT)
  │     │     ├── ② 校验 Upgrade: websocket / Connection: Upgrade
  │     │     ├── ③ 校验 Sec-WebSocket-Key 存在
  │     │     ├── ④ 校验 WebSocket 版本
  │     │     ├── ⑤ 校验 Origin (默认允许所有)
  │     │     ├── ⑥ 协商子协议:
  │     │     │     ├── SubProtocolCapable.getSubProtocols() (如 STOMP)
  │     │     │     └── 显式配置的协议
  │     │     ├── ⑦ 过滤扩展
  │     │     ├── ⑧ 确定用户 (request.getPrincipal())
  │     │     │
  │     │     └── ⑨ RequestUpgradeStrategy.upgrade():
  │     │           └── StandardWebSocketUpgradeStrategy:
  │     │                 ├── 创建 StandardWebSocketSession
  │     │                 ├── 创建 StandardWebSocketHandlerAdapter (Jakarta Endpoint)
  │     │                 ├── ServerEndpointRegistration
  │     │                 └── ServerContainer.upgradeHttpToWebSocket()
  │     │                       └── onOpen() → WebSocketHandler.afterConnectionEstablished()
  │     │
  │     └── HandshakeInterceptorChain.applyAfterHandshake()
  │
  └── 升级成功: HTTP 101 Switching Protocols
```

### 3.2 STOMP over WebSocket 消息流

```
Client → WebSocket Text/Binary Frame
  │
  ├── ① StompSubProtocolHandler.handleMessageFromClient():
  │     ├── 获取/创建 BufferingStompDecoder (per-session)
  │     ├── StompDecoder.decode(ByteBuffer)
  │     │     ├── 处理粘包/半包 (BufferingStompDecoder)
  │     │     └── 返回 List<Message<byte[]>>
  │     │
  │     ├── 针对每个 STOMP Frame:
  │     │     ├── CONNECT → 创建 SessionInfo, 建立通道
  │     │     ├── 设置 session attributes, user, heartbeat
  │     │     ├── 标记 message 为 immutable
  │     │     │
  │     │     ├── 发布 ApplicationEvent:
  │     │     │     ├── SessionConnectEvent
  │     │     │     ├── SessionSubscribeEvent
  │     │     │     └── SessionUnsubscribeEvent
  │     │     │
  │     │     └── clientInboundChannel.send(message)
  │     │
  │     └── 错误时: 发送 STOMP ERROR frame → close PROTOCOL_ERROR
  │
  ├── ② 服务端发送到 clientOutboundChannel:
  │     └── StompSubProtocolHandler.handleMessageToClient():
  │           ├── SimpMessageType → STOMP Command 转换:
  │           │     ├── CONNECT_ACK → CONNECTED (含 user-name header)
  │           │     ├── DISCONNECT_ACK → RECEIPT/ERROR
  │           │     └── HEARTBEAT → 心跳帧
  │           ├── StompEncoder.encode() → TextMessage/BinaryMessage
  │           ├── 发布 SessionConnectedEvent / SessionDisconnectEvent
  │           └── session.sendMessage() → ConcurrentWebSocketSessionDecorator
  │
  └── ③ Session 污点检测: 60s 无子协议消息 → close session
```

### 3.3 SockJS 轮询流程

```
Client GET /{serverId}/{sessionId}/xhr
  │
  ├── SockJsHttpRequestHandler → SockJsService.handleRequest()
  │     └── AbstractSockJsService 路由:
  │           ├── 解析 3 段路径 → 提取 serverId/sessionId/transport
  │           └── TransportHandlingSockJsService.handleTransportRequest():
  │
  ├── ① 解析 TransportType = XHR
  ├── ② 获取/创建 PollingSockJsSession
  │
  ├── ③ XhrPollingTransportHandler.handleRequest():
  │     └── handleInitialRequest() (首次) 或 handleSuccessiveRequest() (后续):
  │           ├── delegateConnectionEstablished()
  │           │     └── SubProtocolWebSocketHandler.afterConnectionEstablished()
  │           │           ├── 装饰 session: ConcurrentWebSocketSessionDecorator
  │           │           └── StompSubProtocolHandler.afterSessionStarted()
  │           │
  │           ├── 写入 open frame: "o\n"
  │           ├── flushCache() → 写入缓存消息
  │           └── 如无消息: 调度心跳 → 等待
  │
  │     下次轮询:
  │           ├── flushCache() → 写入缓存的 STOMP frames
  │           └── 心跳帧: "h\n"
  │
  └── ④ 断连延迟: disconnectDelay (默认 5s) 后关闭 session
```

### 3.4 SockJS 流式传输流程

```
Client POST /{serverId}/{sessionId}/xhr_streaming
  │
  ├── XhrStreamingTransportHandler → handleRequest():
  │     └── handleInitialRequest():
  │           ├── ① 写入 2049 字节 prelude: "h" * 2048 + "\n"
  │           ├── ② 写入 open frame: "o\n"
  │           ├── ③ flushCache() → 流式写入缓存消息
  │           ├── ④ 调度心跳
  │           ├── ⑤ 异步请求保持打开 (async request)
  │           └── ⑥ streamBytesLimit (128KB) 到达 → resetRequest() 回收连接
  │
  └── 服务器主动推送:
        └── sendMessageInternal() → 添加到缓存 → flushCache()
              └── 写入 frame: "a[\"message1\",\"message2\"]\n"
```

### 3.5 ConcurrentWebSocketSessionDecorator 并发控制

```
session.sendMessage(message)
  │
  ├── buffer.append(message)              // LinkedBlockingQueue
  ├── tryAcquire flushLock (ReentrantLock, sendTimeLimit=10s)
  │     ├── 获取锁成功 → flush:
  │     │     └── 逐个发送 buffer 中所有消息 → delegate.sendMessage()
  │     │
  │     └── 获取锁失败 (另一线程在发送):
  │           ├── buffer 积压 > bufferSizeLimit (512KB):
  │           │     ├── TERMINATE → close(NOT_ACCEPTABLE)
  │           │     └── DROP → 丢弃最旧消息
  │           └── 等待另一线程的 flush 完成
  │
  └── 同一时刻只有一个线程在发送 (保证消息顺序)
```

### 3.6 SockJS 六种传输类型

| 传输类型 | HTTP 方法 | 数据方向 | 特点 |
|---------|----------|--------|------|
| WEBSOCKET | GET (Upgrade) | 双向 | 原生 WebSocket，全双工 |
| XHR | POST | 服务器→客户端 | 长轮询，每次请求-响应 |
| XHR_SEND | POST | 客户端→服务器 | 发送数据 |
| XHR_STREAMING | POST | 服务器→客户端 | HTTP 流，连接保持打开 |
| EVENT_SOURCE | GET | 服务器→客户端 | Server-Sent Events |
| HTML_FILE | GET | 服务器→客户端 | IE iframe 兼容 |

---

## 四、关键设计决策

| 模式 | 应用 |
|------|------|
| **Decorator 链** | SubProtocolWebSocketHandler 装饰 session 为 ConcurrentWebSocketSessionDecorator |
| **协议桥接** | WebSocket ↔ Spring Messaging (SubProtocolWebSocketHandler + StompSubProtocolHandler) |
| **BufferingStompDecoder** | 处理 WebSocket 帧粘包/半包，per-session 缓冲区 |
| **状态机** | AbstractSockJsSession: NEW → OPEN → CLOSED |
| **心跳管理** | SockJS: ScheduledFuture 发送 "h" 帧 (25s); STOMP: heartbeat 头协商 |
| **消息缓存** | AbstractHttpSockJsSession: bounded LinkedBlockingQueue (100 条) |

---

## 五、依赖关系

```
spring-websocket
  ├── api: spring-core
  ├── api: spring-beans
  ├── api: spring-context
  ├── api: spring-messaging
  ├── api: spring-web
  ├── api: spring-webmvc
  ├── optional: org.eclipse.jetty:jetty-server
  ├── optional: org.apache.tomcat:tomcat-websocket
  ├── optional: io.undertow:undertow-servlet
  ├── optional: io.projectreactor.netty:reactor-netty-http
  ├── optional: jakarta.websocket:jakarta.websocket-api (JSR-356)
  ├── optional: com.fasterxml.jackson.core:jackson-databind
  └── optional: io.micrometer:micrometer-observation

---

## 六、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-web](L7-spring-web.md) | L7 Web | HTTP 抽象层、CORS、过滤器 |
| 上游 | [spring-webmvc](L7-spring-webmvc.md) | L7 Web | Servlet 容器集成 |
| 上游 | [spring-messaging](L6-spring-messaging.md) | L6 消息 | STOMP 协议处理 |
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
```
