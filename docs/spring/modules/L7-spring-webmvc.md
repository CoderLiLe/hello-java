# spring-webmvc 模块功能文档

---

## 一、模块定位

spring-webmvc 是 Spring 的 **Servlet 栈 Web 框架模块**，363 个 Java 文件，负责：

- **DispatcherServlet**：Servlet 前端控制器，`doDispatch()` 12 步请求分发
- **注解驱动 MVC**：@RequestMapping、@Controller、@ResponseBody、@ExceptionHandler
- **视图解析**：ViewResolver 链、InternalResourceView、RedirectView、ContentNegotiatingViewResolver
- **HandlerMapping 体系**：AbstractHandlerMethodMapping + MappingRegistry 注册与查找
- **HandlerAdapter 体系**：RequestMappingHandlerAdapter（30 参数解析器 + 20 返回值处理器）
- **拦截器链**：HandlerInterceptor preHandle / postHandle / afterCompletion
- **异常处理**：ExceptionHandlerExceptionResolver → ResponseStatusExceptionResolver → DefaultHandlerExceptionResolver

**依赖**：`spring-core`、`spring-beans`、`spring-context`、`spring-web`

---

## 二、模块全景图

```
spring-webmvc (363 files)
│
├── org.springframework.web.servlet/                   # 核心 (21 files)
│   ├── DispatcherServlet                              — ★ 前端控制器 (1408 lines)
│   ├── FrameworkServlet                               — 抽象基类 (1212 lines)
│   ├── HttpServletBean                                — HttpServlet + BeanWrapper (244 lines)
│   ├── HandlerMapping                                 — 处理器映射接口 (182 lines)
│   ├── HandlerAdapter                                 — 处理器适配接口 (79 lines)
│   ├── HandlerInterceptor                             — ★ 拦截器接口 (159 lines)
│   ├── HandlerExecutionChain                          — 处理器执行链 (212 lines)
│   ├── HandlerExceptionResolver                       — 异常解析器接口 (55 lines)
│   ├── ViewResolver                                   — 视图解析器接口 (58 lines)
│   ├── ModelAndView / ModelAndViewContainer           — 模型与视图
│   ├── FlashMap / FlashMapManager                     — Flash 属性
│   └── View / AbstractView / SmartView                — 视图接口
│
├── org.springframework.web.servlet.handler/           # 处理器基础设施 (23 files)
│   ├── AbstractHandlerMapping                         — ★ 抽象 HandlerMapping 基类 (824 lines)
│   ├── AbstractHandlerMethodMapping<T>                — ★ 抽象方法映射 + MappingRegistry (819 lines)
│   ├── AbstractUrlHandlerMapping                      — URL 映射基类 (555 lines)
│   ├── SimpleUrlHandlerMapping                        — 简单 URL 映射 (191 lines)
│   ├── MappedInterceptor                             — ★ 路径模式拦截器包装 (353 lines)
│   └── AbstractHandlerExceptionResolver               — 异常解析器基类 (305 lines)
│
├── org.springframework.web.servlet.mvc/               # MVC 类型 (14 files)
│   ├── method/annotation/                             # 注解驱动 (55 files)
│   │   ├── RequestMappingHandlerMapping               — ★ @RequestMapping 注册 (601 lines)
│   │   ├── RequestMappingInfo                         — ★ 请求映射信息 (1084 lines)
│   │   ├── RequestMappingHandlerAdapter               — ★ 适配器 (1096 lines)
│   │   │
│   │   ├── ExceptionHandlerExceptionResolver          — ★ @ExceptionHandler (566 lines)
│   │   │
│   │   ├── Argument Resolvers (30+):
│   │   │     ├── RequestParamMethodArgumentResolver, PathVariableMethodArgumentResolver
│   │   │     ├── RequestResponseBodyMethodProcessor  — @RequestBody/@ResponseBody
│   │   │     ├── ServletModelAttributeMethodProcessor, HttpEntityMethodProcessor
│   │   │     ├── MatrixVariableMethodArgumentResolver, SessionAttributeMethodArgumentResolver
│   │   │     └── ServletRequestMethodArgumentResolver, ServletResponseMethodArgumentResolver
│   │   │
│   │   └── Return Value Handlers (20+):
│   │         ├── RequestResponseBodyMethodProcessor, ResponseEntityReturnValueHandler
│   │         ├── ModelAndViewMethodReturnValueHandler, ViewMethodReturnValueHandler
│   │         ├── CallableMethodReturnValueHandler, DeferredResultMethodReturnValueHandler
│   │         └── StreamingResponseBodyReturnValueHandler
│   │
│   ├── condition/                                     # 请求匹配条件 (17 files)
│   │     ├── PatternsRequestCondition / PathPatternsRequestCondition
│   │     ├── ProducesRequestCondition (378 lines)
│   │     ├── ConsumesRequestCondition (291 lines)
│   │     ├── RequestMethodsRequestCondition (196 lines)
│   │     ├── ParamsRequestCondition (192 lines)
│   │     └── HeadersRequestCondition (198 lines)
│   │
│   ├── DefaultHandlerExceptionResolver                — ★ 标准异常 → HTTP 状态 (710 lines)
│   ├── ResponseStatusExceptionResolver               — @ResponseStatus (161 lines)
│   └── RedirectAttributes / RedirectAttributesModelMap
│
├── org.springframework.web.servlet.view/              # 视图 (19 files)
│   ├── AbstractCachingViewResolver                    — 视图缓存 (312 lines)
│   ├── UrlBasedViewResolver                           — URL 视图解析 (608 lines)
│   ├── InternalResourceViewResolver                   — JSP 视图解析 (117 lines)
│   ├── ContentNegotiatingViewResolver                — ★ 内容协商视图 (371 lines)
│   ├── BeanNameViewResolver / ViewResolverComposite
│   └── document/ feed/ freemarker/ groovy/ json/ xml/ xslt/ — 各类视图
│
├── org.springframework.web.servlet.resource/          # 静态资源 (30 files)
│   ├── ResourceHttpRequestHandler                     — 资源处理器
│   └── ResourceUrlProvider / ResourceTransformer 链
│
├── org.springframework.web.servlet.function/          # 函数式 Web (33 files)
│   ├── RouterFunction / HandlerFunction               — 函数式路由 (Servlet 版本)
│   ├── ServerRequest / ServerResponse                 — 请求/响应抽象
│   ├── RequestPredicates / RouterFunctions            — 谓词工具类
│   └── support/: RouterFunctionMapping, HandlerFunctionAdapter
│
├── org.springframework.web.servlet.config/            # 配置 (36 files)
│   ├── annotation/:
│   │   ├── @EnableWebMvc                              — 启用 MVC 注解驱动
│   │   ├── WebMvcConfigurationSupport                 — ★ 核心配置类 (所有 Bean 创建)
│   │   ├── WebMvcConfigurer                           — ★ 配置回调接口 (20+ 方法)
│   │   ├── InterceptorRegistry / ViewControllerRegistry / ViewResolverRegistry
│   │   └── ResourceHandlerRegistry / AsyncSupportConfigurer / CorsRegistry
│   │
│   └── XML namespace parsers (13 files)
│
├── org.springframework.web.servlet.support/           # Servlet 支持 (14 files)
│   ├── AbstractFlashMapManager                        — Flash Map 管理 (271 lines)
│   ├── SessionFlashMapManager                         — Session 存储 (69 lines)
│   ├── DispatcherServletInitializer                   — Servlet 初始化器
│   └── RequestContext / RequestContextUtils
│
├── org.springframework.web.servlet.i18n/              # 国际化 (8 files)
│   ├── AcceptHeaderLocaleResolver / SessionLocaleResolver / CookieLocaleResolver
│   └── LocaleChangeInterceptor
│
├── org.springframework.web.servlet.tags/              # JSP 标签 (47 files)
│   ├── BindTag / EvalTag / ThemeTag ...
│   └── form/: FormTag / InputTag / SelectTag / CheckboxesTag / RadiobuttonTag ...
│
└── org.springframework.web.servlet.view/              # 特殊视图实现
    ├── json/: MappingJackson2JsonView
    ├── xml/: MarshallingView
    └── xslt/: XsltView
```

---

## 三、核心流程

### 3.1 DispatcherServlet.doDispatch() 完整流程

```
1. checkMultipart(request)                      → 如果是 multipart → 包装为 MultipartHttpServletRequest
2. getHandler(processedRequest)                 → 遍历 HandlerMapping 链
     └── AbstractHandlerMapping.getHandler():
           ├── getHandlerInternal(request)      → 查找 Handler (@RequestMapping / URL 映射 / RouterFunction)
           ├── getHandlerExecutionChain()       → 附加拦截器链
           └── CORS 处理
3. 如果 handler == null → noHandlerFound()     → 抛 NoHandlerFoundException → 404
4. mappedHandler.applyPreHandle()               → ★ 拦截器 preHandle (正向)
     └── 任何一个返回 false → 链终止
5. getHandlerAdapter(handler)                   → 查找第一个 supports(handler) 的适配器
6. ha.handle(request, response, handler)        → ★ 适配器调用处理器
7. 如果异步已启动 → 直接返回
8. applyDefaultViewName(mv, request)            → RequestToViewNameTranslator 生成默认视图名
9. mappedHandler.applyPostHandle()              → 拦截器 postHandle (反向)
    
    ═══ 以下在 catch/processDispatchResult 中 ═══
    
10. processHandlerException():
      ├── ExceptionHandlerExceptionResolver     → @ExceptionHandler 方法
      ├── ResponseStatusExceptionResolver       → @ResponseStatus
      └── DefaultHandlerExceptionResolver       → 标准异常 → HTTP Status
11. render(mv, request, response):
      ├── resolveViewName() → ViewResolver 链
      ├── view.render(model, request, response)
      └── 设置 HTTP Status
12. mappedHandler.triggerAfterCompletion()       → 拦截器 afterCompletion (反向)
```

### 3.2 类层次与初始化

```
HttpServlet.init()
  └── HttpServletBean.init()
        ├── BeanWrapper 将 ServletConfig init-params 映射为 Bean 属性
        └── initServletBean()
              └── FrameworkServlet.initServletBean()
                    └── initWebApplicationContext()
                          ├── 创建/查找 WebApplicationContext
                          ├── context.refresh()
                          └── onRefresh()  ← ContextRefreshListener 触发
                                └── DispatcherServlet.onRefresh()
                                      └── initStrategies(context):
                                            ├── initMultipartResolver()
                                            ├── initLocaleResolver()
                                            ├── initHandlerMappings()      → 从 context 或 DispatcherServlet.properties
                                            ├── initHandlerAdapters()
                                            ├── initHandlerExceptionResolvers()
                                            ├── initRequestToViewNameTranslator()
                                            ├── initViewResolvers()
                                            └── initFlashMapManager()
```

### 3.3 RequestMappingHandlerAdapter 处理器调用

```
handleInternal(request, response, handlerMethod):
  │
  ├── ① checkRequest(request) — HTTP method 校验
  │
  ├── ② invokeHandlerMethod(request, response, handlerMethod):
  │     │
  │     ├── 设置异步处理 (AsyncWebRequest, CallableProcessingInterceptor)
  │     │
  │     ├── 创建 WebDataBinderFactory:
  │     │     ├── @InitBinder 方法 (本类 + @ControllerAdvice)
  │     │     └── 添加 ConversionService, Validator
  │     │
  │     ├── 创建 ModelFactory:
  │     │     ├── 收集 @ModelAttribute 方法 (全局 @ControllerAdvice → 局部)
  │     │     └── modelFactory.initModel() → 执行 @ModelAttribute 方法
  │     │
  │     ├── 创建 ServletInvocableHandlerMethod:
  │     │     ├── 注入 Argument Resolvers (30 个)
  │     │     └── 注入 Return Value Handlers (20 个)
  │     │
  │     ├── 构建 ModelAndViewContainer:
  │     │     └── 加载 input FlashMap attributes
  │     │
  │     └── invocableMethod.invokeAndHandle(webRequest, mavContainer):
  │           │
  │           ├── ① 解析参数 (Iterate 30 Argument Resolvers):
  │           │     └── resolver.supportsParameter(param) → resolveArgument()
  │           │
  │           ├── ② doInvoke(args): method.invoke(bean, args)
  │           │
  │           └── ③ 处理返回值 (Iterate 20 Return Value Handlers):
  │                 └── handler.supportsReturnType(returnType) → handleReturnValue()
  │                       ├── @ResponseBody → HttpMessageConverter 写入响应体
  │                       ├── ModelAndView → 视图名 + Model
  │                       ├── ResponseEntity → Status + Headers + Body
  │                       └── Callable/DeferredResult → 异步处理
  │
  └── ③ getModelAndView(mavContainer, modelFactory, webRequest):
        ├── modelFactory.updateModel() → 更新 session attributes, 写 Flash 输出
        └── 构建 ModelAndView (view name / View, model, status)
```

### 3.4 AbstractHandlerMethodMapping + MappingRegistry

```
初始化:
  afterPropertiesSet() → initHandlerMethods():
    └── 扫描所有 Spring Bean
          ├── isHandler(beanType) → @Controller / @RequestMapping
          └── detectHandlerMethods(handler):
                └── 遍历所有方法
                      └── getMappingForMethod(method, handlerType)
                            └── RequestMappingHandlerMapping:
                                  ├── 合并类级 + 方法级 @RequestMapping
                                  ├── 创建 RequestMappingInfo
                                  └── mappingRegistry.register(mapping, handler, method)

请求时查找:
  getHandlerInternal(request) → lookupHandlerMethod(lookupPath, request):
    │
    ├── ① 直接路径查找:
    │     └── MappingRegistry.getMappingsByDirectPath(lookupPath)
    │
    ├── ② 模式匹配:
    │     └── RequestMappingInfo.getMatchingCondition(request)
    │           ├── PatternsRequestCondition: AntPath / PathPattern 匹配
    │           ├── RequestMethodsRequestCondition: GET/POST... 匹配
    │           ├── ConsumesRequestCondition: Content-Type 匹配
    │           ├── ProducesRequestCondition: Accept 匹配
    │           ├── ParamsRequestCondition: 参数匹配
    │           └── HeadersRequestCondition: Header 匹配
    │
    ├── ③ 排序: compareTo() — 更具体的模式优先
    │
    ├── ④ 歧义检测: 前两个匹配置信度相同 → 抛异常
    │
    └── ⑤ handleMatch():
          ├── 设置 URI template variables → request attributes
          └── 设置 producible media types → request attributes
```

### 3.5 HandlerExecutionChain 拦截器生命周期

```
applyPreHandle(request, response):
  正向 (0..N):
    for each interceptor:
      if (!interceptor.preHandle(request, response, handler)):
        triggerAfterCompletion(request, response, null)  ← 对已执行的回调 afterCompletion
        return false

applyPostHandle(request, response, mv):
  反向 (N..0):
    for each interceptor:
      interceptor.postHandle(request, response, handler, mv)

triggerAfterCompletion(request, response, ex):
  反向 (lastSuccessfulPreHandle..0):
    for each interceptor with successful preHandle:
      interceptor.afterCompletion(request, response, handler, ex)
```

`MappedInterceptor` 包装原始 `HandlerInterceptor` + include/exclude 路径模式，`AbstractHandlerMapping.getHandlerExecutionChain()` 检查每个拦截器是否匹配当前请求。

### 3.6 异常处理链

```
dispatchException 不为 null → processHandlerException():
  │
  ├── ① ExceptionHandlerExceptionResolver (Order=0):
  │     └── 在 @Controller + @ControllerAdvice 中查找 @ExceptionHandler
  │           ├── 按异常类型匹配 (最近超类优先)
  │           ├── 支持 produces 内容协商
  │           └── 将 MethodArgument 注入，调用处理方法
  │
  ├── ② ResponseStatusExceptionResolver (Order=1):
  │     ├── ResponseStatusException → 提取 HttpStatus + reason
  │     └── @ResponseStatus 注解异常 → HttpStatus + reason
  │     └── response.sendError(statusCode, reason)
  │
  └── ③ DefaultHandlerExceptionResolver (Order=2):
        └── 17 种标准 Spring MVC 异常 → HTTP Status:
              ├── HttpRequestMethodNotSupportedException → 405
              ├── HttpMediaTypeNotSupportedException → 415
              ├── HttpMediaTypeNotAcceptableException → 406
              ├── MissingServletRequestParameterException → 400
              ├── MethodArgumentNotValidException → 400
              ├── NoHandlerFoundException → 404
              ├── AsyncRequestTimeoutException → 503
              └── ... (完整映射表见文档)
```

---

## 四、关键数据结构

### RequestMappingInfo (1084 lines)

组合多个 `RequestCondition`：

| Condition | 匹配维度 |
|-----------|---------|
| `PatternsRequestCondition` | URL 路径 (AntPath) |
| `PathPatternsRequestCondition` | URL 路径 (PathPattern, 6.0+) |
| `RequestMethodsRequestCondition` | HTTP 方法 |
| `ConsumesRequestCondition` | Content-Type |
| `ProducesRequestCondition` | Accept |
| `ParamsRequestCondition` | 请求参数 |
| `HeadersRequestCondition` | 请求头 |
| `VersionRequestCondition` | API 版本 (7.0) |

### MappingRegistry 内部结构

```java
class MappingRegistry {
    Map<T, MappingRegistration<T>> registry;           // mapping → registration
    MultiValueMap<String, T> pathLookup;               // path → mappings (直接路径快速查找)
    Map<String, List<HandlerMethod>> nameLookup;       // mapping name → HandlerMethods
    Map<HandlerMethod, CorsConfiguration> corsLookup;  // 方法级 CORS
    ReentrantReadWriteLock readWriteLock;              // 读写锁
}
```

### DispatcherServlet.properties 默认策略

| 策略 | 默认实现 |
|------|---------|
| HandlerMapping | BeanNameUrlHandlerMapping, RequestMappingHandlerMapping, RouterFunctionMapping |
| HandlerAdapter | HttpRequestHandlerAdapter, SimpleControllerHandlerAdapter, RequestMappingHandlerAdapter, HandlerFunctionAdapter |
| HandlerExceptionResolver | ExceptionHandlerExceptionResolver, ResponseStatusExceptionResolver, DefaultHandlerExceptionResolver |
| ViewResolver | InternalResourceViewResolver |
| LocaleResolver | AcceptHeaderLocaleResolver |
| FlashMapManager | SessionFlashMapManager |

---

## 五、依赖关系

```
spring-webmvc
  ├── api: spring-core
  ├── api: spring-beans
  ├── api: spring-context
  ├── api: spring-web
  ├── optional: jakarta.servlet:jakarta.servlet-api
  ├── optional: jakarta.servlet.jsp:jakarta.servlet.jsp-api
  ├── optional: jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api
  ├── optional: org.freemarker:freemarker
  ├── optional: com.fasterxml.jackson.core:jackson-databind
  ├── optional: jakarta.xml.bind:jakarta.xml.bind-api
  ├── optional: io.micrometer:micrometer-observation
  └── optional: org.jetbrains.kotlin:kotlin-stdlib

---

## 六、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-web](L7-spring-web.md) | L7 Web | HTTP 抽象层、消息转换、Web 绑定 |
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
| 下游 | [spring-websocket](L7-spring-websocket.md) | L7 Web | WebSocket 握手 |
| 下游 | [spring-test](L8-spring-test.md) | L8 测试 | MockMvc |
```
