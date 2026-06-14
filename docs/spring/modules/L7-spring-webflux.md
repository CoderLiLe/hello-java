# spring-webflux 模块功能文档

---

## 一、模块定位

spring-webflux 是 Spring 的 **响应式 Web 框架模块**，275 个 Java 文件，负责：

- **DispatcherHandler**：响应式前端控制器（对比 DispatcherServlet）
- **WebClient**：响应式非阻塞 HTTP 客户端（对比 RestTemplate）
- **函数式 Web 模型**：RouterFunction + HandlerFunction（声明式路由）
- **注解驱动模型**：@RequestMapping 的响应式版本（共享 spring-web 基础设施）
- **响应式 WebSocket**：WebSocketHandler + HandshakeWebSocketService
- **视图与结果处理**：ViewResolutionResultHandler、Rendering API

**依赖**：`spring-core`、`spring-beans`、`spring-context`、`spring-web`

---

## 二、模块全景图

```
spring-webflux (275 files)
│
├── org.springframework.web.reactive/                  # 核心 (8 files)
│   ├── DispatcherHandler                              — ★ 响应式前端控制器 (220 lines)
│   ├── HandlerMapping                                 — 处理器映射接口 (109 lines)
│   ├── HandlerAdapter                                 — 处理器适配接口 (73 lines)
│   ├── HandlerResultHandler                           — 结果处理器接口 (48 lines)
│   ├── HandlerResult                                  — 处理器结果 (142 lines)
│   └── DispatchExceptionHandler                       — 异常处理 (53 lines)
│
├── org.springframework.web.reactive.config/           # Java 配置 (16 files)
│   ├── @EnableWebFlux                                 — 启用 WebFlux 注解
│   ├── WebFluxConfigurationSupport                   — 核心配置类
│   ├── WebFluxConfigurer                              — 配置回调接口
│   └── DelegatingWebFluxConfiguration                 — 委托模式
│
├── org.springframework.web.reactive.function/         # 函数式 Web (6 files)
│   ├── client/                                        # WebClient (24 files)
│   │   ├── WebClient                                  — ★ 响应式 HTTP 客户端接口 (961 lines)
│   │   ├── DefaultWebClient                           — 默认实现 (768 lines)
│   │   ├── ExchangeFunction                           — 交换函数 (@FunctionalInterface, 68 lines)
│   │   ├── ExchangeFilterFunction                     — 交换过滤器 (98 lines)
│   │   └── ExchangeStrategies                         — 编码策略 (108 lines)
│   │
│   └── server/                                        # 函数式服务端 (24 files)
│       ├── RouterFunction                             — ★ 路由函数 (@FunctionalInterface, 162 lines)
│       ├── HandlerFunction                            — ★ 处理函数 (@FunctionalInterface, 39 lines)
│       ├── RouterFunctions                            — 路由工具类 (1502 lines)
│       ├── RequestPredicates                          — 请求谓词工厂 (1508 lines)
│       ├── ServerRequest                              — 服务器请求抽象 (653 lines)
│       ├── ServerResponse                             — ★ 服务器响应抽象 (535 lines)
│       ├── RequestPredicate                           — 请求谓词 (@FunctionalInterface, 98 lines)
│       └── support/:
│             ├── RouterFunctionMapping                 — 函数式 HandlerMapping
│             ├── HandlerFunctionAdapter                — 函数式 HandlerAdapter
│             └── ServerResponseResultHandler           — ServerResponse HandlerResultHandler
│
├── org.springframework.web.reactive.result/           # 结果处理 (4 files)
│   ├── condition/                                     # 请求匹配条件 (16 files)
│   │     ├── PatternsRequestCondition / PathPatternsRequestCondition
│   │     ├── ProducesRequestCondition / ConsumesRequestCondition
│   │     └── HeadersRequestCondition / ParamsRequestCondition
│   │
│   ├── method/annotation/                             # 注解驱动 (40 files)
│   │     ├── RequestMappingHandlerMapping             — ★ @RequestMapping 处理器映射 (548 lines)
│   │     ├── RequestMappingHandlerAdapter             — ★ @RequestMapping 处理器适配 (370 lines)
│   │     ├── ResponseEntityResultHandler              — ResponseEntity 结果处理 (209 lines, Order=0)
│   │     ├── ResponseBodyResultHandler                — @ResponseBody 结果处理 (121 lines, Order=100)
│   │     └── Argument Resolvers (30+):
│   │           ├── @RequestBody / @RequestParam / @PathVariable / @RequestHeader ...
│   │           └── ServerWebExchange / WebSession / Principal ...
│   │
│   └── view/                                          # 视图解析 (19 files)
│       ├── ViewResolutionResultHandler                — 视图结果处理 (619 lines, Order=MAX_VALUE)
│       ├── Rendering                                  — ★ 程序化渲染 API (164 lines)
│       ├── RedirectView / FragmentsRendering
│       └── freemarker/ / script/                      — 模板引擎集成
│
├── org.springframework.web.reactive.handler/          # HandlerMapping 基础设施 (5 files)
│   ├── AbstractHandlerMapping                         — 抽象基类 (~150 lines)
│   ├── AbstractUrlHandlerMapping / SimpleUrlHandlerMapping
│   └── WebSocketHandlerMapping
│
├── org.springframework.web.reactive.resource/         # 静态资源 (27 files)
│   ├── ResourceWebHandler                             — 资源处理器
│   └── 资源解析器链 (VersionResourceResolver, GzipResourceResolver 等)
│
├── org.springframework.web.reactive.accept/           # 内容协商 (16 files)
│   └── RequestedContentTypeResolver / ParameterContentTypeResolver
│
└── org.springframework.web.reactive.socket/           # WebSocket (6 files)
    ├── WebSocketHandler                               — WebSocket 处理器 (125 lines)
    ├── WebSocketSession                               — WebSocket 会话 (137 lines)
    ├── WebSocketService                               — WebSocket 服务接口 (46 lines)
    ├── server/support/:
    │   ├── HandshakeWebSocketService                  — ★ 握手服务 (282 lines)
    │   └── WebSocketHandlerAdapter                    — HandlerAdapter 桥接 (111 lines)
    ├── server/upgrade/: 各运行时升级策略 (6 files)
    └── adapter/: 各运行时会话适配 (11 files)
```

---

## 三、核心流程

### 3.1 DispatcherHandler 请求分发

```
HttpHandler.handle(ServerHttpRequest, ServerHttpResponse)
  │  (HttpWebHandlerAdapter)
  │
  ├── ① HttpWebHandlerAdapter.handle():
  │     ├── ForwardedHeaderTransformer 处理代理头
  │     ├── 创建 DefaultServerWebExchange (含 session/codec/locale)
  │     └── 委托给 WebHandler chain
  │
  ├── ② ExceptionHandlingWebHandler (异常处理)
  │     └── WebExceptionHandler 链
  │
  ├── ③ FilteringWebHandler (WebFilter 链)
  │     └── DefaultWebFilterChain:
  │           ├── WebFilter.security(), WebFilter.cors(), WebFilter.logging()...
  │           └── DispatcherHandler
  │
  ├── ④ DispatcherHandler.handle(exchange):
  │     │
  │     ├── Flux.fromIterable(handlerMappings)
  │     │     .concatMap(mapping → mapping.getHandler(exchange))
  │     │     .next()                                    ← 取第一个匹配
  │     │     .switchIfEmpty(createNotFoundError())      ← 无匹配 → 404
  │     │
  │     ├── handleRequestWith(exchange, handler):
  │     │     ├── Flux.fromIterable(handlerAdapters)
  │     │     │     .concatMap(adapter → adapter.handle(exchange, handler))
  │     │     │     .next()                              ← 取第一个支持的适配器
  │     │     └── 返回 Mono<HandlerResult>
  │     │
  │     └── handleResult(exchange, result):
  │           └── Flux.fromIterable(resultHandlers)
  │                 .concatMap(handler → handler.handleResult(exchange, result))
  │                 .next()
  │
  └── ⑤ HandlerResultHandler (按 Order 排序):
        ├── 0: ResponseEntityResultHandler  → ResponseEntity/HttpEntity
        ├── 100: ResponseBodyResultHandler  → @ResponseBody
        └── MAX: ViewResolutionResultHandler → view name / Rendering
```

### 3.2 WebClient 请求流程

```
webClient.get().uri("/api/users").accept(APPLICATION_JSON).retrieve()
         .bodyToFlux(User.class)
  │
  ├── ① DefaultRequestBodyUriSpec 构建:
  │     ├── HTTP method, URI
  │     ├── headers (Accept, etc.)
  │     ├── cookies, attributes
  │     └── retrieve() → 创建 DefaultResponseSpec
  │
  ├── ② exchange() 内部:
  │     ├── 构建 ClientRequest (HTTP method + URL + headers + body)
  │     │
  │     ├── 构建 Filter 链:
  │     │     └── ExchangeFilterFunction.andThen() 组合
  │     │           ├── 用户自定义 filters
  │     │           └── ObservationFilterFunction (Micrometer)
  │     │
  │     └── filterFunction.apply(exchangeFunction):
  │           │
  │           ├── 最内层: ExchangeFunctions.create(connector):
  │           │     └── ClientHttpConnector.connect(method, uri, callback)
  │           │           ├── ReactorClientHttpConnector (默认, Reactor Netty)
  │           │           ├── JettyClientHttpConnector
  │           │           └── JdkClientHttpConnector (Java 11+)
  │           │
  │           └── 返回 Mono<ClientResponse>
  │
  ├── ③ DefaultResponseSpec:
  │     ├── onStatus() 状态码处理
  │     ├── bodyToMono(Class) → 解码为单个对象
  │     ├── bodyToFlux(Class) → 解码为流
  │     ├── toEntity(Class) → ResponseEntity<T>
  │     └── toBodilessEntity() → ResponseEntity<Void>
  │
  └── ④ ExchangeStrategies 编码:
        ├── List<HttpMessageReader<?>>  → 响应解码
        └── List<HttpMessageWriter<?>>  → 请求编码
```

**WebClient Builder 配置：**
```java
WebClient.builder()
    .baseUrl("https://api.example.com")
    .defaultHeader("X-API-Key", "xxx")
    .filter(logFilter())
    .filter(authFilter())
    .clientConnector(new ReactorClientHttpConnector())
    .codecs(configurer → configurer.defaultCodecs().maxInMemorySize(512*1024))
    .build();
```

### 3.3 函数式 Web 路由

```
RouterFunction<UserHandler> route = RouterFunctions.route()
    .path("/api/users", () → route()
        .GET("", handler::listUsers)
        .GET("/{id}", handler::getUser)
        .POST("", handler::createUser)
        .PUT("/{id}", handler::updateUser)
        .DELETE("/{id}", handler::deleteUser)
    )
    .build();
  │
  ├── ① RouterFunction.route(ServerRequest) → Mono<HandlerFunction>
  │     ├── RequestPredicate 匹配:
  │     │     ├── MethodPredicate (GET/POST/...)
  │     │     ├── PathPredicate (AntPath/PathPattern)
  │     │     ├── ContentTypePredicate
  │     │     ├── AcceptPredicate
  │     │     └── and() / or() / negate() 组合
  │     │
  │     └── 嵌套路由: nest(RequestPredicate, RouterFunction)
  │           └── RequestPredicate.nest() 转换 ServerRequest
  │
  ├── ② HandlerFunction.handle(ServerRequest) → Mono<ServerResponse>
  │     ├── ServerRequest 提供: pathVariables(), queryParams(), headers(), bodyToMono()
  │     └── ServerResponse 构建:
  │           ├── ServerResponse.ok().bodyValue(body)
  │           ├── ServerResponse.created(uri).build()
  │           ├── ServerResponse.notFound().build()
  │           └── ServerResponse.status(400).bodyValue(error)
  │
  └── ③ ServerResponseResultHandler 写入响应:
        └── ServerResponse.writeTo(exchange, context)
              ├── 设置 status code
              ├── 设置 headers
              └── 写入 body (通过 BodyInserter)
```

### 3.4 响应式 WebSocket 流程

```
HttpRequest (WebSocket upgrade) 到达
  │
  ├── HandlerMapping → WebSocketHandlerAdapter (HandlerAdapter, Order=2)
  │     └── supports(handler) → handler instanceof WebSocketHandler
  │
  ├── WebSocketHandlerAdapter.handle(exchange, handler):
  │     └── WebSocketService.handleRequest(exchange, webSocketHandler)
  │
  ├── HandshakeWebSocketService.handleRequest():
  │     │
  │     ├── ① 自动检测 RequestUpgradeStrategy:
  │     │     ├── Reactor Netty → ReactorNettyRequestUpgradeStrategy
  │     │     ├── Jetty → JettyRequestUpgradeStrategy
  │     │     ├── Tomcat → TomcatRequestUpgradeStrategy
  │     │     └── Standard → StandardWebSocketUpgradeStrategy (JSR-356)
  │     │
  │     ├── ② 校验 WebSocket handshake:
  │     │     ├── HTTP method: GET or CONNECT
  │     │     ├── Upgrade: websocket / Connection: Upgrade
  │     │     └── Sec-WebSocket-Key
  │     │
  │     ├── ③ 协商子协议:
  │     │     └── handler.getSubProtocols() ∩ handshakeInfo
  │     │
  │     └── ④ upgradeStrategy.upgrade(exchange, handler, subProtocol, handshakeInfo):
  │           └── ReactorNetty: HttpServerResponse.sendWebsocket()
  │                 ├── WebSocketHandler.handle(session)
  │                 │     ├── session.receive()  → Flux<WebSocketMessage>
  │                 │     └── session.send(flux) → Mono<Void>
  │                 └── 返回 Mono<Void> (流完成后自动 close)
```

### 3.5 请求映射条件匹配

```
AbstractHandlerMethodMapping → RequestMappingHandlerMapping.getHandlerInternal():
  │
  ├── directPathMatches = MappingRegistry.getMappingsByDirectPath(lookupPath)
  │     └── 快速查找 (非模式路径)
  │
  ├── addMatchingMappings(registeredMappings, exchange):
  │     └── RequestMappingInfo.getMatchingCondition(exchange):
  │           ├── PatternsRequestCondition     → 路径匹配
  │           ├── RequestMethodsRequestCondition → HTTP method 匹配
  │           ├── ConsumesRequestCondition     → Content-Type 匹配
  │           ├── ProducesRequestCondition     → Accept 匹配
  │           ├── ParamsRequestCondition       → 参数匹配
  │           ├── HeadersRequestCondition      → Header 匹配
  │           └── CustomRequestCondition       → 自定义匹配
  │
  ├── compareTo() 排序 (更具体 → 更高优先级)
  │
  └── 模糊匹配歧义检查: 如果有两个模式匹配置信度相同 → 抛异常
```

---

## 四、DispatcherServlet vs DispatcherHandler 对比

| 特性 | DispatcherServlet (WebMVC) | DispatcherHandler (WebFlux) |
|------|---------------------------|----------------------------|
| 编程模型 | 阻塞 I/O (Servlet API) | 非阻塞 I/O (Reactive Streams) |
| 前端控制器 | `HttpServlet` 子类 | `WebHandler` 实现 |
| HandlerMapping | 返回 `HandlerExecutionChain` | 返回 `Mono<Object>` |
| HandlerAdapter | 返回 `ModelAndView` | 返回 `Mono<HandlerResult>` |
| ViewResolver | 返回 `View` (同步渲染) | 返回 `Mono<Void>` (响应式写入) |
| 策略加载 | `initStrategies()` 从 WebApplicationContext | `setApplicationContext()` 扫描 Bean |
| 异常处理 | `HandlerExceptionResolver` 链 | `DispatchExceptionHandler` + WebExceptionHandler |
| 拦截器 | `HandlerInterceptor` (同步) | `WebFilter` (响应式链式) |

---

## 五、WebClient vs RestTemplate 对比

| 特性 | RestTemplate | WebClient |
|------|-------------|-----------|
| 编程模型 | 阻塞 (每个请求占用线程) | 非阻塞 (Reactor) |
| 返回值 | 直接 POJO | Mono<T> / Flux<T> |
| 请求/响应拦截 | ClientHttpRequestInterceptor | ExchangeFilterFunction |
| URI 构建 | UriComponentsBuilder | UriBuilder |
| 错误处理 | 异常 (try/catch) | onStatus() 处理 |
| 异步支持 | AsyncRestTemplate (已废弃) | 原生异步 |
| Spring 版本 | 自 3.0 | 自 5.0 (6.1+ 推荐) |

---

## 六、依赖关系

```
spring-webflux
  ├── api: spring-core
  ├── api: spring-beans
  ├── api: spring-context
  ├── api: spring-web
  ├── optional: org.freemarker:freemarker
  ├── optional: io.projectreactor.netty:reactor-netty-http
  ├── optional: org.eclipse.jetty:jetty-server
  ├── optional: org.apache.tomcat:tomcat-websocket
  ├── optional: io.undertow:undertow-servlet
  ├── optional: io.micrometer:micrometer-observation
  └── optional: org.jetbrains.kotlinx:kotlinx-coroutines-reactor

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-web](L7-spring-web.md) | L7 Web | HTTP 抽象层、编解码器、Reactor Core |
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
| 下游 | [spring-test](L8-spring-test.md) | L8 测试 | WebTestClient |
| 同级 | [spring-webmvc](L7-spring-webmvc.md) | L7 Web | Servlet MVC（阻塞栈） |
```
