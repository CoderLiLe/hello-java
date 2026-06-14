# spring-web 模块功能文档

---

## 一、模块定位

spring-web 是 Spring 的 **Web 基础设施模块**，789 个 Java 文件，负责：

- **HTTP 抽象层**：HttpHeaders、MediaType、HttpMethod、HttpStatus、HttpCookie 等
- **HTTP 消息转换**：HttpMessageConverter 层次（JSON / XML / Form / Protobuf / YAML 等）
- **HTTP 客户端**：RestClient（6.1+ 现代流式 API）、RestTemplate（传统模板）
- **响应式 HTTP 客户端**：WebClient（spring-webflux 中定义，spring-web 提供 connector）
- **CORS 支持**：CorsConfiguration、CorsProcessor、CorsFilter
- **多部件上传**：MultipartFile、MultipartResolver、StandardServletMultipartResolver
- **Servlet 过滤器链**：OncePerRequestFilter、DelegatingFilterProxy、CorsFilter 等
- **响应式 Web 基础**：HttpHandler、WebHandler、WebFilter、ServerWebExchange
- **HTTP 接口声明**：@HttpExchange + HttpServiceProxyFactory（声明式 HTTP 客户端）
- **内容协商**：ContentNegotiationStrategy、ContentNegotiationManager
- **Web 上下文**：WebApplicationContext、RequestContextHolder、RequestAttributes
- **数据绑定**：WebDataBinder、@RequestMapping 注解基础、WebBindingInitializer
- **Web 工具**：UriComponentsBuilder、UriTemplate、UrlPathHelper、CookieGenerator

**依赖**：`spring-beans`、`spring-core`

---

## 二、模块全景图

```
spring-web (789 files)
│
├── org.springframework.http/                        # HTTP 抽象 (62 files)
│   ├── HttpHeaders                                   — HTTP 头集合 (2358 行, 支持 quality-value 排序)
│   ├── MediaType / MediaTypeFactory                  — MIME 类型 (解析 Content-Type / Accept)
│   ├── HttpMethod                                    — HTTP 方法枚举 (GET / POST / PUT / DELETE / PATCH/...)
│   ├── HttpStatus / HttpStatusCode                   — HTTP 状态码 (200 OK / 404 NOT_FOUND / ...)
│   ├── HttpCookie / ResponseCookie                   — HTTP Cookie 抽象
│   ├── HttpInputMessage / HttpOutputMessage          — HTTP 消息读写接口
│   ├── HttpRequest / ResponseEntity                  — 请求/响应实体
│   ├── ContentDisposition                            — Content-Disposition 解析
│   ├── CacheControl                                  — Cache-Control 构建器
│   ├── MimeType                                      — MIME 类型解析 (核心, spring-core)
│   ├── RequestEntity / ResponseEntity                — 请求/响应实体封装
│   └── Range / HttpRange                             — Range 请求支持
│
├── org.springframework.http.converter/               # 消息转换器 (57 files)
│   ├── HttpMessageConverter<T>                       — ★ 消息转换器接口
│   ├── SmartHttpMessageConverter<T>                  — 增强消息转换器 (6.2+)
│   ├── GenericHttpMessageConverter<T>                — 泛型消息转换器
│   ├── StringHttpMessageConverter                    — String ↔ text/plain
│   ├── FormHttpMessageConverter                      — MultiValueMap ↔ application/x-www-form-urlencoded
│   ├── ByteArrayHttpMessageConverter                 — byte[] ↔ application/octet-stream
│   ├── ResourceHttpMessageConverter                  — Resource ↔ all
│   ├── AbstractGenericHttpMessageConverter<T>         — 泛型基类
│   ├── json/: MappingJackson2HttpMessageConverter    — JSON (Jackson)
│   ├── json/: GsonHttpMessageConverter                — JSON (Gson)
│   ├── xml/: MappingJackson2XmlHttpMessageConverter   — XML (Jackson)
│   ├── xml/: Jaxb2RootElementHttpMessageConverter     — XML (JAXB)
│   ├── protobuf/: ProtobufHttpMessageConverter       — Protobuf
│   ├── smile/: SmileHttpMessageConverter              — Smile 二进制 JSON
│   ├── cbor/: CborHttpMessageConverter                — CBOR
│   ├── yaml/: YamlHttpMessageConverter                — YAML
│   └── support/: AllEncompassingFormHttpMessageConverter / BufferedImageHttpMessageConverter
│
├── org.springframework.http.client/                  # 同步 HTTP 客户端 (26 files)
│   ├── ClientHttpRequestFactory                      — 请求工厂接口
│   ├── ClientHttpRequest / ClientHttpResponse        — 请求/响应接口
│   ├── ClientHttpRequestInterceptor                  — 客户端拦截器
│   ├── ClientHttpRequestInitializer                  — 请求初始化器
│   ├── SimpleClientHttpRequestFactory                — JDK HttpURLConnection
│   ├── JdkClientHttpRequestFactory                    — JDK HttpClient (Java 11+)
│   ├── HttpComponentsClientHttpRequestFactory         — Apache HttpComponents
│   ├── JettyClientHttpRequestFactory                  — Jetty HttpClient
│   ├── ReactorNettyClientRequestFactory               — Reactor Netty
│   ├── JmsClientHttpRequestFactory                    — JMS (测试用)
│   ├── InterceptingClientHttpRequestFactory          — 拦截器包装工厂
│   └── observation/: DefaultClientRequestObservationConvention
│
├── org.springframework.http.client.reactive/          # 响应式 HTTP 客户端 (10 files)
│   ├── ClientHttpConnector                           — 响应式客户端连接器
│   └── ReactorClientHttpConnector / JettyClientHttpConnector / JdkClientHttpConnector
│
├── org.springframework.http.server/                  # 同步 HTTP 服务端 (5 files)
│   └── ServerHttpRequest / ServerHttpResponse         — 服务端请求/响应接口
│
├── org.springframework.http.server/reactive/          # 响应式 HTTP 服务端 (20 files)
│   ├── HttpHandler                                   — ★ 响应式 HTTP 处理器
│   ├── ServerHttpRequest / ServerHttpResponse         — 响应式服务端请求/响应
│   └── ReactorHttpHandlerAdapter / JettyHttpHandlerAdapter / ...
│
├── org.springframework.http.codec/                   # 响应式编解码器 (45 files)
│   ├── Encoder<T> / Decoder<T>                        — 编解码器接口
│   ├── HttpMessageReader<T> / HttpMessageWriter<T>   — HTTP 消息读写器
│   ├── CodecConfigurer                               — 编解码器配置器
│   ├── json/: Jackson2JsonEncoder/Decoder
│   ├── xml/: Jaxb2XmlEncoder/Decoder
│   ├── multipart/: MultipartHttpMessageReader
│   └── support/: BaseDefaultCodecs / CodecConfigurerFactory
│
├── org.springframework.web.client/                   # REST 客户端 (24 files)
│   ├── RestClient                                    — ★ 现代 REST 客户端 (6.1+, 1159 行)
│   ├── RestTemplate                                  — ★ 传统 REST 模板 (1059 行)
│   ├── RestClientInterceptor                         — RestClient 拦截器
│   ├── ResponseExtractor<T>                           — 响应提取器 (RestTemplate)
│   ├── ResponseErrorHandler                          — 错误处理 (默认: DefaultResponseErrorHandler)
│   ├── HttpMessageConverterExtractor<T>              — 消息转换提取器
│   ├── RestClientResponseException                   — REST 异常
│   └── support/: RestClientAdapter / RestTemplateAdapter
│
├── org.springframework.web.cors/                     # CORS (10 files)
│   ├── CorsConfiguration                             — CORS 配置 (825 行)
│   ├── CorsProcessor                                 — CORS 处理器接口
│   ├── DefaultCorsProcessor                          — 默认 CORS 处理
│   ├── CorsFilter                                    — Servlet CORS 过滤器
│   ├── UrlBasedCorsConfigurationSource               — URL 模式匹配配置源
│   └── reactive/: DefaultCorsProcessor / CorsWebFilter
│
├── org.springframework.web.filter/                   # Servlet 过滤器 (39 files)
│   ├── OncePerRequestFilter                          — 每请求执行一次基类
│   ├── DelegatingFilterProxy                         — 委托给 Spring Bean 的过滤器
│   ├── CharacterEncodingFilter                       — 字符编码过滤器
│   ├── CorsFilter                                     — CORS 过滤器
│   ├── ForwardedHeaderFilter                          — 转发头过滤器 (X-Forwarded-*)
│   ├── ShallowEtagHeaderFilter                        — 浅 ETag 过滤器
│   ├── FormContentFilter                              — Form 内容过滤器
│   ├── HiddenHttpMethodFilter                         — 隐藏 HTTP 方法 (_method 参数)
│   ├── RequestContextFilter                           — 请求上下文暴露
│   ├── CompositeFilter                                — 组合过滤器
│   ├── RelativeRedirectFilter                         — 相对重定向过滤器
│   └── reactive/: ServerHttpObservationFilter / ...   — 响应式过滤器
│
├── org.springframework.web.context/                  # Web 上下文 (30 files)
│   ├── WebApplicationContext                         — Web 容器接口
│   ├── ConfigurableWebApplicationContext             — 可配置 Web 容器
│   ├── ContextLoaderListener                         — Web 容器启动监听器
│   ├── ContextLoader                                 — 容器加载器
│   ├── WebApplicationContextInitializer              — 容器初始化器
│   ├── ServletContextAware / ServletConfigAware      — Servlet 感知接口
│   ├── RequestContextHolder / RequestAttributes       — 请求上下文持有者 (ThreadLocal)
│   ├── request/async/: AsyncRequestTimeoutException / DeferredResult / ...
│   └── support/: GenericWebApplicationContext / ServletContextResource
│
├── org.springframework.web.multipart/                # 多部件上传 (18 files)
│   ├── MultipartFile                                 — 上传文件接口
│   ├── MultipartResolver                             — 多部件解析器接口
│   ├── StandardServletMultipartResolver              — Servlet 3.0+ 标准解析器
│   ├── CommonsMultipartResolver                      — Apache Commons FileUpload
│   ├── MultipartHttpServletRequest                   — 多部件请求封装
│   ├── MultipartException                            — 多部件异常
│   └── support/: ByteArrayMultipartFileEditor / StringMultipartFileEditor
│
├── org.springframework.web.bind/                     # Web 数据绑定 (18 files)
│   ├── WebDataBinder                                 — Web 数据绑定器
│   ├── ServletRequestDataBinder                     — Servlet 请求数据绑定
│   ├── WebBindingInitializer                         — Web 绑定初始化器
│   ├── ConfigurableWebBindingInitializer             — 可配置绑定初始化器
│   ├── annotation/: RequestMapping / GetMapping / PostMapping / ...
│   └── support/: WebRequestDataBinder / ...
│
├── org.springframework.web.server/                   # 响应式 Web 服务端 (17 files)
│   ├── WebHandler                                    — ★ 响应式 Web 处理器接口
│   ├── WebFilter / WebFilterChain                    — 响应式 Web 过滤器链
│   ├── ServerWebExchange                             — 服务端 Web 交换 (请求+响应)
│   ├── ServerWebInputMessage / ServerHttpResponse     — 输入/输出消息
│   ├── handler/: DefaultWebFilterChain / FilteringWebHandler
│   ├── session/: WebSessionManager / WebSession
│   ├── i18n/: LocaleContextResolver
│   └── adapter/: WebHttpHandlerBuilder
│
├── org.springframework.web.service/                  # HTTP 接口声明 (8 files)
│   ├── HttpServiceProxyFactory                       — ★ @HttpExchange 代理工厂
│   ├── HttpExchangeAdapter                           — HTTP 交换适配器 (RestClient/RestTemplate/WebClient)
│   ├── HttpServiceMethod                             — 服务方法元数据
│   ├── annotation/: HttpExchange / GetExchange / PostExchange / ...
│   └── invoker/: HttpServiceMethodAdapter / HttpExchangeAdapterMethod
│
├── org.springframework.web.accept/                   # 内容协商 (9 files)
│   ├── ContentNegotiationStrategy                   — 内容协商策略接口
│   ├── ContentNegotiationManager                     — 内容协商管理器 (责任链)
│   ├── HeaderContentNegotiationStrategy             — Accept 头策略
│   ├── ParameterContentNegotiationStrategy           — 参数策略 (?format=json)
│   └── FixedContentNegotiationStrategy               — 固定策略
│
├── org.springframework.web.method/                   # Web 方法处理 (10 files)
│   ├── HandlerMethod                                 — ★ 处理器方法封装
│   ├── InvocableHandlerMethod                        — 可调用处理器方法
│   └── annotation/: ModelAttribute / ExceptionHandler / InitBinder
│
├── org.springframework.web.util/                     # Web 工具 (27 files)
│   ├── UriComponentsBuilder                          — URI 构建器
│   ├── UriTemplate / UriTemplateHandler              — URI 模板
│   ├── DefaultUriBuilderFactory                      — 默认 URI 构建工厂
│   ├── UrlPathHelper                                 — URL 路径辅助
│   ├── CookieGenerator                               — Cookie 生成器
│   ├── HtmlUtils / JavaScriptUtils                   — HTML/JS 转义
│   ├── WebUtils                                      — Web 工具类
│   └── pattern/: PathPattern / PathPatternParser     — ★ 路径模式匹配 (6.0+)
│
└── org.springframework.web.server/                   # ...
    └── handler/: ResourceWebHandler / ...
```

---

## 三、核心 HTTP 抽象层次

```
HttpHeaders                                  — HTTP 头集合 (MultiValueMap<String, String>, 2358 行)
  ├── getContentType() → MediaType
  ├── getAccept() → List<MediaType>
  ├── getContentLength() / setContentLength()
  ├── getHost() / setHost()
  ├── getOrigin() / setOrigin()
  ├── getETag() / setETag()
  └── ...

MediaType                                   — MIME 类型 (application/json;charset=UTF-8)
  ├── 预定义常量: APPLICATION_JSON, APPLICATION_XML, TEXT_PLAIN, ...
  ├── 质量值: getQualityValue() (q=0.8)
  └── MediaTypeFactory: 根据文件扩展名/Resource 推断 MediaType

HttpMethod                                  — HTTP 方法枚举
  GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS, TRACE

HttpStatus / HttpStatusCode                 — HTTP 状态码
  ├── HttpStatus: 枚举式常量 (OK=200, NOT_FOUND=404, ...)
  └── HttpStatusCode: 接口 (支持自定义状态码, 6.0+)
```

---

## 四、核心流程

### 4.1 RestClient 请求流程（6.1+ 现代 API）

```
RestClient restClient = RestClient.create();
String result = restClient.get()
    .uri("https://api.example.com/users/{id}", 42)
    .accept(MediaType.APPLICATION_JSON)
    .retrieve()
    .body(String.class);

内部流程:
  │
  ├── ① 构建请求: DefaultRestClient.RequestBodySpec
  │     ├── uri → UriBuilderFactory.expand() → URI
  │     ├── header → HttpHeaders
  │     └── body → Object (由 HttpMessageConverter 序列化)
  │
  ├── ② 执行请求: InternalRestClient.exchange()
  │     │
  │     ├── 创建请求: ClientHttpRequestFactory.createRequest(uri, method)
  │     │     ├── SimpleClientHttpRequestFactory → HttpURLConnection
  │     │     ├── JdkClientHttpRequestFactory    → java.net.http.HttpClient
  │     │     ├── HttpComponentsClientHttpRequestFactory → Apache HttpClient
  │     │     └── ReactorNettyClientRequestFactory → Reactor Netty
  │     │
  │     ├── 应用拦截器链: ClientHttpRequestInterceptor.intercept()
  │     ├── 序列化请求体: HttpMessageConverter.write(body, contentType, request)
  │     │
  │     ├── 执行请求: request.execute() → ClientHttpResponse
  │     │
  │     ├── 错误处理: DefaultResponseErrorHandler.hasError(response)?
  │     │     └── YES → handleError() → 解析错误响应 → 抛出 RestClientResponseException
  │     │
  │     └── 反序列化响应体: HttpMessageConverter.read(type, response)
  │
  └── ③ 返回结果
```

### 4.2 RestClient vs RestTemplate 对比

```
RestClient (6.1+, 现代)                     RestTemplate (传统)
─────────────────────────────────────      ────────────────────────
流式 Builder API                           模板方法 API
支持同步 + 异步                             仅同步
集成 Observation (Micrometer)               无内置 observability
内置 URI 变量扩展                           同
支持 exchange() 低级别访问                   同
可自定义 HttpMessageConverter              同
支持拦截器 (ClientHttpRequestInterceptor)   同
建议用于新项目                               向后兼容

使用示例:
  // RestClient                              // RestTemplate
  RestClient.create()                        RestTemplate rt = new RestTemplate();
    .get()                                   String result = rt.getForObject(
    .uri(url)                                  url, String.class);
    .retrieve()
    .body(String.class);
```

### 4.3 @HttpExchange 声明式 HTTP 客户端（6.0+）

```
@HttpExchange("/users")
interface UserService {
    @GetExchange("/{id}")
    User getUser(@PathVariable Long id);

    @PostExchange
    User createUser(@RequestBody User user);

    @DeleteExchange("/{id}")
    void deleteUser(@PathVariable Long id);
}

HttpServiceProxyFactory proxyFactory = HttpServiceProxyFactory
    .builderFor(RestClientAdapter.create(restClient))
    .build();
UserService service = proxyFactory.createClient(UserService.class);

内部流程:
  │
  ├── ① 解析接口: HttpServiceProxyFactory.createClient()
  │     │
  │     ├── 解析 @HttpExchange 基础 URL
  │     ├── 遍历每个方法 → HttpServiceMethod
  │     │     ├── 解析 @GetExchange / @PostExchange 等注解
  │     │     ├── 解析 @PathVariable / @RequestParam / @RequestBody
  │     │     ├── 解析返回类型 (直接类型 / ResponseEntity<T> / Flux<T> / ...)
  │     │     └── 创建 HttpServiceMethodAdapter
  │     │
  │     └── JDK 动态代理 → InvocationHandler
  │
  └── ② 方法调用:
        ├── 构建 HTTP 请求 (URL / Method / Headers / Body)
        ├── 通过 HttpExchangeAdapter 执行请求
        │     ├── RestClientAdapter (同步)
        │     ├── RestTemplateAdapter (同步)
        │     └── WebClientAdapter (响应式)
        └── 反序列化响应
```

### 4.4 CORS 处理流程

```
请求 → CorsFilter.doFilter()
  │
  ├── 查找 CorsConfiguration: corsConfigurationSource.getCorsConfiguration(request)
  │     └── UrlBasedCorsConfigurationSource:
  │           └── 路径匹配: /api/** → CorsConfiguration
  │
  ├── Preflight (OPTIONS) 请求:
  │     CorsProcessor.processRequest(config, request, response)
  │       │
  │       ├── 验证 Origin → allowedOrigins
  │       ├── 验证 Method → allowedMethods (Access-Control-Request-Method)
  │       ├── 验证 Headers → allowedHeaders (Access-Control-Request-Headers)
  │       ├── 设置响应头:
  │       │   Access-Control-Allow-Origin
  │       │   Access-Control-Allow-Methods
  │       │   Access-Control-Allow-Headers
  │       │   Access-Control-Allow-Credentials
  │       │   Access-Control-Max-Age
  │       └── 返回 200 (无需继续过滤器链)
  │
  └── 普通 CORS 请求:
        CorsProcessor.processRequest(config, request, response)
          ├── 验证 Origin
          ├── 设置响应头:
          │   Access-Control-Allow-Origin
          │   Access-Control-Expose-Headers
          │   Access-Control-Allow-Credentials
          └── 继续过滤器链
```

### 4.5 ContentNegotiation 内容协商

```
ContentNegotiationManager.resolveMediaTypes(request)
  │
  ├── 策略链 (按顺序):
  │   │
  │   ├── ① ParameterContentNegotiationStrategy: ?format=json → application/json
  │   │
  │   ├── ② HeaderContentNegotiationStrategy: Accept: application/json
  │   │     └── MediaType.parseMediaTypes(acceptHeader)
  │   │           ├── 解析 quality value: q=0.8
  │   │           └── 排序: 高 q 值优先
  │   │
  │   └── ③ FixedContentNegotiationStrategy: 固定默认类型 → application/json
  │
  └── 返回 List<MediaType> (从最偏好到最不偏好)
```

### 4.6 响应式 WebHandler / WebFilter 链

```
请求 → HttpHandler.handle(request, response) → Mono<Void>
  │
  └── WebHttpHandlerBuilder.build()
        │
        ├── WebFilter 链: filter1 → filter2 → ... → WebHandler
        │     DefaultWebFilterChain:
        │       filter.filter(exchange, chain)
        │         └── chain.filter(exchange)  ← 下一个 filter 或 WebHandler
        │
        └── WebHandler.handle(exchange) → Mono<Void>
              ├── 路由到具体 Handler
              ├── Handler 执行业务逻辑
              └── 写入响应
```

---

## 五、HttpMessageConverter 层次

| 转换器 | 支持 MediaType | 说明 |
|--------|---------------|------|
| `StringHttpMessageConverter` | text/plain, */* | String ↔ text |
| `FormHttpMessageConverter` | application/x-www-form-urlencoded | MultiValueMap ↔ Form |
| `ByteArrayHttpMessageConverter` | application/octet-stream, */* | byte[] ↔ binary |
| `ResourceHttpMessageConverter` | all | Resource ↔ binary |
| `MappingJackson2HttpMessageConverter` | application/json | JSON (Jackson) |
| `GsonHttpMessageConverter` | application/json | JSON (Gson) |
| `Jaxb2RootElementHttpMessageConverter` | application/xml, text/xml | XML (JAXB) |
| `MappingJackson2XmlHttpMessageConverter` | application/xml | XML (Jackson) |
| `ProtobufHttpMessageConverter` | application/x-protobuf | Protobuf |
| `AllEncompassingFormHttpMessageConverter` | multipart/form-data | 多部件表单 |
| `BufferedImageHttpMessageConverter` | image/* | BufferedImage ↔ Image |

---

## 六、关键过滤器速查

| 过滤器 | 说明 |
|--------|------|
| `CharacterEncodingFilter` | 设置请求/响应字符编码 |
| `CorsFilter` | CORS 请求处理 |
| `ForwardedHeaderFilter` | 处理 X-Forwarded-Proto/Host/Port 代理头 |
| `ShallowEtagHeaderFilter` | 生成浅 ETag（基于响应内容 MD5） |
| `FormContentFilter` | 使 PUT/PATCH/DELETE 也能解析 form body |
| `HiddenHttpMethodFilter` | 通过 _method 参数支持 PUT/DELETE |
| `RequestContextFilter` | 将当前请求暴露到 RequestContextHolder |
| `RelativeRedirectFilter` | 将 HTTP 位置头转为相对路径 |
| `OncePerRequestFilter` | 基类：保证每次请求只执行一次（支持 forward/include 过滤） |
| `DelegatingFilterProxy` | 将 Servlet Filter 委托给 Spring Bean |

---

## 七、关键类速查

| 类/接口 | 包 | 说明 |
|---------|-----|------|
| `HttpHeaders` | `http` | HTTP 头集合 (2358 行) |
| `MediaType` | `http` | MIME 类型解析 |
| `HttpMethod` | `http` | HTTP 方法枚举 |
| `HttpStatus` | `http` | HTTP 状态码枚举 |
| `HttpMessageConverter` | `http.converter` | 消息转换器接口 |
| `RestClient` | `web.client` | 现代 REST 客户端 (6.1+) |
| `RestTemplate` | `web.client` | 传统 REST 模板 |
| `CorsConfiguration` | `web.cors` | CORS 配置 (825 行) |
| `CorsProcessor` | `web.cors` | CORS 处理器接口 |
| `OncePerRequestFilter` | `web.filter` | 每请求一次过滤器基类 |
| `MultipartFile` | `web.multipart` | 上传文件接口 |
| `MultipartResolver` | `web.multipart` | 多部件解析器 |
| `HttpServiceProxyFactory` | `web.service` | @HttpExchange 代理工厂 |
| `ContentNegotiationManager` | `web.accept` | 内容协商管理器 |
| `HandlerMethod` | `web.method` | 处理器方法封装 |
| `UriComponentsBuilder` | `web.util` | URI 构建器 |
| `PathPattern` | `web.util.pattern` | 路径模式匹配 (6.0+) |
| `HttpHandler` | `http.server.reactive` | 响应式 HTTP 处理器 |
| `WebHandler` | `web.server` | 响应式 Web 处理器 |
| `WebApplicationContext` | `web.context` | Web 容器接口 |
| `RequestContextHolder` | `web.context.request` | 请求上下文持有者 |

---

## 八、依赖关系

```
spring-web
  ├── api: spring-beans
  ├── api: spring-core
  ├── optional: io.micrometer:micrometer-observation
  ├── optional: com.fasterxml.jackson.core:jackson-databind       (JSON)
  ├── optional: com.fasterxml.jackson.dataformat:jackson-dataformat-xml (XML)
  ├── optional: com.fasterxml.jackson.dataformat:jackson-dataformat-smile
  ├── optional: com.fasterxml.jackson.dataformat:jackson-dataformat-cbor
  ├── optional: com.fasterxml.jackson.dataformat:jackson-dataformat-yaml
  ├── optional: com.google.code.gson:gson                         (Gson)
  ├── optional: com.google.protobuf:protobuf-java                 (Protobuf)
  ├── optional: jakarta.xml.bind:jaxb-api                         (JAXB)
  ├── optional: jakarta.servlet:jakarta.servlet-api               (Servlet)
  ├── optional: io.projectreactor.netty:reactor-netty-http        (Reactor Netty)
  ├── optional: org.apache.httpcomponents:httpclient5             (Apache HttpClient 5)
  ├── optional: org.eclipse.jetty:jetty-client                    (Jetty)
  ├── optional: org.eclipse.jetty:jetty-server
  └── optional: io.undertow:undertow-core

---

## 九、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | BeanFactory |
| 上游 | [spring-core](L1-spring-core.md) | L1 核心 | 反射、类型转换 |
| 下游 | [spring-webmvc](L7-spring-webmvc.md) | L7 Web | Servlet MVC 框架 |
| 下游 | [spring-webflux](L7-spring-webflux.md) | L7 Web | 响应式 Web 框架 |
| 下游 | [spring-websocket](L7-spring-websocket.md) | L7 Web | WebSocket 支持 |
| 下游 | [spring-test](L8-spring-test.md) | L8 测试 | MockMvc、WebTestClient |
```
