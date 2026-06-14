# Spring MVC 请求生命周期源码深度解析

> 本文深入分析 Spring MVC 一次 HTTP 请求的完整处理链路，覆盖 DispatcherServlet.doDispatch() 12 步分发流程、HandlerMapping 映射查找与匹配条件排序、HandlerAdapter 参数解析与返回值处理、拦截器链生命周期以及异常解析器链。
> 相关模块文档：[spring-webmvc](../modules/L7-spring-webmvc.md)、[spring-web](../modules/L7-spring-web.md)

---

## 一、请求处理全景

```
HTTP Request
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│                 DispatcherServlet                        │
│                                                         │
│  doDispatch(request, response)                          │
│    │                                                    │
│    ├── ① checkMultipart(request)                        │
│    ├── ② getHandler(request)      ← HandlerMapping 链    │
│    ├── ③ getHandlerAdapter(handler) ← HandlerAdapter 链  │
│    ├── ④ applyPreHandle()         ← 拦截器 preHandle     │
│    ├── ⑤ ha.handle()              ← ★ 调用处理器         │
│    ├── ⑥ applyPostHandle()        ← 拦截器 postHandle    │
│    └── ⑦ processDispatchResult()  ← 异常解析 + 渲染      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、DispatcherServlet 类层次

```
HttpServlet (Servlet API)
  └── HttpServletBean
        ├── 将 ServletConfig init-params 通过 BeanWrapper 映射为属性
        └── initServletBean() (抽象方法)
              │
              └── FrameworkServlet
                    ├── initWebApplicationContext():
                    │     ├── 创建/查找 WebApplicationContext
                    │     ├── context.refresh()
                    │     └── onRefresh()  ← 触发策略初始化
                    │
                    ├── service() → processRequest():
                    │     └── doService() (抽象方法, 子类实现)
                    │
                    └── DispatcherServlet
                          ├── onRefresh() → initStrategies():  ← 初始化 9 大策略
                          │     ├── initMultipartResolver()
                          │     ├── initLocaleResolver()
                          │     ├── initThemeResolver()
                          │     ├── initHandlerMappings()
                          │     ├── initHandlerAdapters()
                          │     ├── initHandlerExceptionResolvers()
                          │     ├── initRequestToViewNameTranslator()
                          │     ├── initViewResolvers()
                          │     └── initFlashMapManager()
                          │
                          └── doService() → doDispatch()  ← ★ 核心分发
```

---

## 三、doDispatch() 逐步分析

### 3.1 checkMultipart() — 文件上传检测

```
processedRequest = checkMultipart(request):
  │
  ├── multipartResolver != null && multipartResolver.isMultipart(request)?
  │     ├── YES → multipartResolver.resolveMultipart(request)
  │     │         └── StandardServletMultipartResolver:
  │     │               └── request.getParts() → 包装为 StandardMultipartHttpServletRequest
  │     └── NO  → 返回原始 request
  │
  └── 设置 request attribute: org.springframework.web.multipart.MultipartResolver.RESOLVED
```

### 3.2 getHandler() — 处理器查找

```
mappedHandler = getHandler(processedRequest):
  │
  └── 遍历 this.handlerMappings (List<HandlerMapping>):
        ├── ① BeanNameUrlHandlerMapping:     "/foo" → Bean
        ├── ② RequestMappingHandlerMapping:  @RequestMapping 注解方法
        ├── ③ RouterFunctionMapping:         RouterFunction (函数式)
        └── ④ SimpleUrlHandlerMapping:       URL 映射配置
        │
        └── handlerMapping.getHandler(request):
              └── AbstractHandlerMapping.getHandler(request):
                    │
                    ├── getHandlerInternal(request) → handler
                    │     │
                    │     └── AbstractHandlerMethodMapping.getHandlerInternal():
                    │           └── lookupHandlerMethod(lookupPath, request):
                    │                 │
                    │                 ├── MappingRegistry 查找:
                    │                 │     ├── 直接路径匹配: pathLookup.get(lookupPath)
                    │                 │     ├── 模式匹配: 遍历所有 mapping, getMatchingCondition()
                    │                 │     └── 排序: compareTo() → 更具体的优先
                    │                 │
                    │                 └── 歧义检测: 如果前两名匹配置信度相同 → 抛异常
                    │
                    └── getHandlerExecutionChain(handler, request):
                          ├── 创建 HandlerExecutionChain(handler)
                          └── 添加匹配的拦截器:
                                └── MappedInterceptor.matches(request):
                                      ├── includePatterns: 路径匹配
                                      └── excludePatterns: 排除路径
```

### 3.3 RequestMappingInfo 匹配条件

```
RequestMappingInfo.getMatchingCondition(request):
  │
  ├── ① PatternsRequestCondition: AntPathMatcher 匹配
  │     /api/{id}  ←→  /api/123  → {id=123}
  │
  ├── ② RequestMethodsRequestCondition: GET/POST/PUT/DELETE
  │
  ├── ③ ConsumesRequestCondition: Content-Type 匹配
  │     consumes = "application/json"  ←→  Content-Type: application/json
  │
  ├── ④ ProducesRequestCondition: Accept 匹配
  │     produces = "application/json"  ←→  Accept: application/json
  │
  ├── ⑤ ParamsRequestCondition: 请求参数匹配
  │     params = "type=admin"  ←→  ?type=admin
  │
  ├── ⑥ HeadersRequestCondition: 请求头匹配
  │     headers = "X-API-Version=1"  ←→  X-API-Version: 1
  │
  └── ⑦ CustomRequestCondition (扩展)
```

### 3.4 HandlerMapping 查找关键点

```
多 HandlerMapping 映射时的优先级:

RequestMappingHandlerMapping:
  用于 @RequestMapping 注解 → HandlerMethod

匹配冲突时排序规则:
  ① 路径更具体的优先
  ② 条件更精确的优先
  ③ 最终: AbstractHandlerMethodMapping.MappingComparator 比较
```

### 3.5 getHandlerAdapter() — 适配器选择

```
handlerAdapter = getHandlerAdapter(handler):
  │
  └── 遍历 this.handlerAdapters:
        ├── ① RequestMappingHandlerAdapter:     supports(HandlerMethod) → YES
        ├── ② HttpRequestHandlerAdapter:        supports(HttpRequestHandler) → YES
        ├── ③ SimpleControllerHandlerAdapter:   supports(Controller) → YES
        └── ④ HandlerFunctionAdapter:           supports(HandlerFunction) → YES

选择第一个 supports() 返回 true 的适配器
```

### 3.6 applyPreHandle() — 拦截器前置处理

```
mappedHandler.applyPreHandle(request, response):
  │
  └── for (i = 0; i < interceptors.length; i++):
        └── interceptor.preHandle(request, response, this.handler):
              ├── true  → 继续下一个
              └── false → triggerAfterCompletion(i)  ← 触发已执行拦截器的 afterCompletion
                          return false → DispatcherServlet 直接返回, 不调用 handler
```

**注意**：任一 `preHandle` 返回 `false`，后续处理器都不会执行，请求在此终止。

### 3.7 ha.handle() — 实际处理器调用

```
mv = ha.handle(processedRequest, response, mappedHandler.getHandler()):
  │
  └── RequestMappingHandlerAdapter.handleInternal(request, response, handlerMethod):
        │
        ├── checkRequest(request): HTTP method 校验
        │
        └── invokeHandlerMethod(request, response, handlerMethod):
              │
              ├── ① 设置异步处理: AsyncWebRequest, CallableProcessingInterceptor
              │
              ├── ② 创建 WebDataBinderFactory:
              │     ├── @InitBinder 方法 (Controller + @ControllerAdvice)
              │     └── ConversionService, Validator
              │
              ├── ③ 创建 ModelFactory:
              │     ├── @ModelAttribute 方法 (全局 → 局部)
              │     └── modelFactory.initModel() → 执行 @ModelAttribute 方法
              │
              ├── ④ 创建 ServletInvocableHandlerMethod:
              │     ├── 设置 ArgumentResolvers (30+)
              │     └── 设置 ReturnValueHandlers (20+)
              │
              └── ⑤ invocableMethod.invokeAndHandle(webRequest, mavContainer):
                    │
                    ├── invokeForRequest(request, mavContainer, args):
                    │     │
                    │     └── getMethodArgumentValues(request, mavContainer, args):
                    │           └── for each parameter:
                    │                 ├── 遍历 ArgumentResolvers
                    │                 ├── resolver.supportsParameter(param)?
                    │                 │     └── YES → resolver.resolveArgument()
                    │                 └── 返回 resolvedArgs[]
                    │
                    ├── doInvoke(args): method.invoke(bean, args)
                    │
                    └── handleReturnValue(returnValue, returnType, mavContainer):
                          └── 遍历 ReturnValueHandlers:
                                └── handler.supportsReturnType() → handler.handleReturnValue()
```

### 3.8 参数解析器 (Argument Resolvers)

```
常用参数解析器及解析内容:

RequestParamMethodArgumentResolver   → @RequestParam / MultipartFile
PathVariableMethodArgumentResolver   → @PathVariable
RequestResponseBodyMethodProcessor   → @RequestBody (HttpMessageConverter)
ServletModelAttributeMethodProcessor → @ModelAttribute (对象绑定)
HttpEntityMethodProcessor            → HttpEntity / RequestEntity
MatrixVariableMethodArgumentResolver → @MatrixVariable
SessionAttributeMethodArgumentReslvr→ @SessionAttribute
ServletRequestMethodArgumentResolver → HttpServletRequest / InputStream / Reader
ServletResponseMethodArgumentResolver→ HttpServletResponse / OutputStream / Writer
ModelMethodProcessor                 → Model / ModelMap
MapMethodProcessor                   → Map
ErrorsMethodArgumentResolver         → Errors / BindingResult
SessionStatusMethodArgumentResolver  → SessionStatus
RedirectAttributesMethodArgumentResolver → RedirectAttributes
PrincipalMethodArgumentResolver      → Principal
```

### 3.9 返回值处理器 (Return Value Handlers)

```
常用返回值处理器及处理:

RequestResponseBodyMethodProcessor    → @ResponseBody: HttpMessageConverter 写响应
ModelAndViewMethodReturnValueHandler → ModelAndView: 设置 view + model
ViewMethodReturnValueHandler         → View: 直接设置 view
ResponseEntityReturnValueHandler     → ResponseEntity: status + headers + body
HttpHeadersReturnValueHandler        → HttpHeaders: 设置响应头
CallableMethodReturnValueHandler     → Callable: 异步处理
DeferredResultMethodReturnValueHandler → DeferredResult: 异步处理
StreamingResponseBodyReturnValueHandler → StreamingResponseBody
MapMethodReturnValueHandler          → Map: 默认视图名 + model
ModelAttributeMethodProcessor        → @ModelAttribute: 添加到 model
```

### 3.10 applyDefaultViewName() — 默认视图名

```
如果没有设置视图名 → applyDefaultViewName(request, mv):
  └── RequestToViewNameTranslator.getViewName(request):
        └── DefaultRequestToViewNameTranslator:
              /app/UserController/list → "userController/list"
              /app/user/list.html       → "user/list"
              /app/user/                → "user/index"
```

### 3.11 applyPostHandle() — 拦截器后置处理

```
mappedHandler.applyPostHandle(request, response, mv):
  └── for (i = interceptors.length - 1; i >= 0; i--):
        └── interceptor.postHandle(request, response, handler, mv)
```

**反向执行**：后注册的拦截器先执行 `postHandle`。

### 3.12 processDispatchResult() — 异常解析 + 视图渲染

```
processDispatchResult(request, response, mappedHandler, mv, dispatchException):
  │
  ├── 如果有异常 (dispatchException != null):
  │     └── processHandlerException(request, response, handler, exception):
  │           └── 遍历 HandlerExceptionResolvers:
  │                 ├── ① ExceptionHandlerExceptionResolver:
  │                 │     └── 查找 @ExceptionHandler 方法 (Controller + @ControllerAdvice)
  │                 │           ├── 按异常类型匹配 (最近超类优先)
  │                 │           ├── 支持 produces 内容协商
  │                 │           └── 返回 ModelAndView
  │                 │
  │                 ├── ② ResponseStatusExceptionResolver:
  │                 │     └── @ResponseStatus(HttpStatus.NOT_FOUND) → sendError(404)
  │                 │
  │                 └── ③ DefaultHandlerExceptionResolver:
  │                       └── 标准 Spring MVC 异常 → HTTP Status
  │                             ├── HttpRequestMethodNotSupportedException → 405
  │                             ├── HttpMediaTypeNotSupportedException   → 415
  │                             ├── MissingServletRequestParameterException → 400
  │                             ├── MethodArgumentNotValidException      → 400
  │                             └── NoHandlerFoundException              → 404
  │
  ├── render(mv, request, response):   ← 有视图时渲染
  │     ├── 如果是 redirect: → sendRedirect()
  │     ├── 否则:
  │     │     ├── resolveViewName(viewName, locale):
  │     │     │     └── 遍历 ViewResolvers:
  │     │     │           ├── ContentNegotiatingViewResolver → 根据 Accept 选择
  │     │     │           ├── InternalResourceViewResolver → JSP
  │     │     │           └── ...
  │     │     └── view.render(model, request, response):
  │     │           ├── 设置 Content-Type
  │     │           ├── 渲染内容
  │     │           └── 设置 HTTP Status
  │     └── 设置 response status (如果 view 未设置)
  │
  └── mappedHandler.triggerAfterCompletion(request, response, dispatchException):
        └── for (i = interceptorIndex; i >= 0; i--):
              └── interceptor.afterCompletion(request, response, handler, ex)
```

---

## 四、拦截器链完整生命周期

```
正常流程:
  Request  → preHandle[0] → preHandle[1] → handler → postHandle[1] → postHandle[0] → render → afterCompletion[1] → afterCompletion[0]

preHandle 返回 false:
  Request  → preHandle[0] → afterCompletion[0]  (终止)

有异常:
  Request  → preHandle[0] → preHandle[1] → handler → exception resolver → afterCompletion[1] → afterCompletion[0]
```

---

## 五、异步请求处理

```
Controller 返回 Callable<ModelAndView> 或 DeferredResult<ModelAndView>:

doDispatch():
  │
  ├── getHandler() → 正常处理
  ├── applyPreHandle() → 正常处理
  ├── ha.handle() → 检测到异步返回值:
  │     ├── 启动异步: request.startAsync()
  │     └── WebAsyncManager.startCallableProcessing(callable):
  │           ├── 提交 Callable 到 TaskExecutor
  │           └── 拦截器链: CallableProcessingInterceptor
  │
  ├── 请求线程释放 (doDispatch 返回)
  │
  └── Callable 完成时:
        └── WebAsyncManager.dispatch():
              └── request.dispatch() → 重新进入 doDispatch()
                    └── 此时 handler 返回真正的 ModelAndView
```

---

## 六、完整时序总结

| 步骤 | 方法 | 关键操作 |
|------|------|---------|
| 1 | `checkMultipart()` | 文件上传检测与包装 |
| 2 | `getHandler()` | HandlerMapping 链查找 HandlerMethod + 附加拦截器 |
| 3 | `getHandlerAdapter()` | 选择支持 handler 的适配器 |
| 4 | `applyPreHandle()` | 拦截器 preHandle 正向执行 |
| 5 | `ha.handle()` | 参数解析 → 反射调用 → 返回值处理 |
| 6 | `applyPostHandle()` | 拦截器 postHandle 反向执行 |
| 7 | `processDispatchResult()` | 异常解析 → 视图渲染 → afterCompletion |

---

## 七、相关文档

| 文档 | 说明 |
|------|------|
| [spring-webmvc 模块文档](../modules/L7-spring-webmvc.md) | DispatcherServlet 完整参考 |
| [spring-web 模块文档](../modules/L7-spring-web.md) | HTTP 抽象层、消息转换 |
| [spring-context 模块文档](../modules/L4-spring-context.md) | WebApplicationContext 层级 |
| [AOP 实现深度解析](12-aop-implementation.md) | 拦截器链责任链模式 |
