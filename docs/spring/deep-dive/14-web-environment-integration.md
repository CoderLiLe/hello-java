# Spring Web 环境集成源码深度解析

> 本文深入分析 Spring 与 Servlet 容器的集成机制，覆盖 ContextLoaderListener 根容器创建、DispatcherServlet 子容器层级、父子容器 Bean 可见性规则、WebApplicationContext 类层次、以及 Spring Boot 如何替代传统 web.xml 配置。
> 相关模块文档：[spring-web](../modules/L7-spring-web.md)、[spring-webmvc](../modules/L7-spring-webmvc.md)、[spring-context](../modules/L4-spring-context.md)

---

## 一、两级容器架构

```
                         ┌─────────────────────────┐
                         │     Servlet Container    │
                         │       (Tomcat)           │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
          ┌─────────▼──────────┐            ┌───────────▼──────────┐
          │  ContextLoaderListener│            │  DispatcherServlet  │
          │  (ServletContextListener)│          │  (HttpServlet)      │
          └─────────┬──────────┘            └───────────┬──────────┘
                    │                                   │
          ┌─────────▼──────────┐            ┌───────────▼──────────┐
          │  Root WebApplication│            │  Servlet WebApp-    │
          │  Context (父容器)   │◄──parent──│  licationContext     │
          │                     │            │  (子容器)            │
          │  Service / DAO /    │            │                      │
          │  DataSource / Tx    │            │  Controller /        │
          │                     │            │  ViewResolver /      │
          └─────────────────────┘            │  HandlerMapping      │
                                             └─────────────────────┘

Bean 可见性:
  子容器 → 父容器: ✅ 可访问 (如 Controller 注入 Service)
  父容器 → 子容器: ❌ 不可访问 (Service 不能注入 Controller)
```

---

## 二、ContextLoaderListener 源码分析

### 2.1 类层次

```
ServletContextListener (Jakarta Servlet API)
  └── ContextLoaderListener
        └── extends ContextLoader, implements ServletContextListener
```

### 2.2 入口：contextInitialized()

```java
public class ContextLoaderListener extends ContextLoader implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent event) {
        // 委托给父类 ContextLoader 的 initWebApplicationContext()
        initWebApplicationContext(event.getServletContext());
    }

    @Override
    public void contextDestroyed(ServletContextEvent event) {
        closeWebApplicationContext(event.getServletContext());
        ContextCleanupListener.cleanupAttributes(event.getServletContext());
    }
}
```

### 2.3 ContextLoader.initWebApplicationContext() — 根容器创建

```
initWebApplicationContext(servletContext):
  │
  ├── ① 检查 ServletContext 中是否已有根容器（防止重复创建）
  │     └── servletContext.getAttribute(ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE) != null?
  │           → 抛 IllegalStateException
  │
  ├── ② createWebApplicationContext(servletContext):
  │     ├── determineContextClass() → 确定容器类型
  │     │     ├── servletContext.getInitParameter("contextClass")  ← 优先
  │     │     └── 从 ContextLoader.properties 读取默认值
  │     │           └── 默认: org.springframework.web.context.support.XmlWebApplicationContext
  │     └── BeanUtils.instantiateClass(contextClass) → 反射实例化
  │
  ├── ③ ★ configureAndRefreshWebApplicationContext(cwac, servletContext):
  │     │
  │     ├── 设置 id (可通过 contextId 参数自定义):
  │     │     └── wac.setId(ConfigurableWebApplicationContext.APPLICATION_CONTEXT_ID_PREFIX + contextId)
  │     │
  │     ├── 关联 ServletContext:
  │     │     └── wac.setServletContext(servletContext)
  │     │
  │     ├── 设置配置文件位置:
  │     │     └── wac.setConfigLocation(servletContext.getInitParameter("contextConfigLocation"))
  │     │           └── 默认: /WEB-INF/applicationContext.xml
  │     │
  │     ├── 自定义上下文: customizeContext(servletContext, wac)
  │     │     └── ApplicationContextInitializer 在此执行
  │     │
  │     └── ★ wac.refresh()  ← 触发 Spring 容器完整启动流程
  │
  ├── ④ ★ 将根容器存入 ServletContext:
  │     └── servletContext.setAttribute(
  │              WebApplicationContext.ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE,
  │              this.context)
  │           └── key = "org.springframework.web.context.WebApplicationContext.ROOT"
  │
  └── ⑤ 将根容器缓存到 ContextLoader.currentContextPerThread (ThreadLocal)
```

### 2.4 contextDestroyed() — 销毁流程

```
contextDestroyed(servletContextEvent):
  ├── closeWebApplicationContext(servletContext):
  │     ├── servletContext.removeAttribute(ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE)
  │     ├── context.close()  ← 发布 ContextClosedEvent, 销毁所有单例
  │     └── context = null
  └── ContextCleanupListener.cleanupAttributes(servletContext):
        └── 清理 ServletContext 中 "org.springframework.*" 开头的属性
              └── 防止热部署时的内存泄漏
```

---

## 三、DispatcherServlet 子容器创建

### 3.1 类层次

```
HttpServlet (Jakarta Servlet API)
  └── HttpServletBean
        ├── 将 init-params 通过 BeanWrapper 映射为属性
        └── initServletBean() (模板方法)
              │
              └── FrameworkServlet
                    └── initWebApplicationContext():
                          │
                          ├── findWebApplicationContext():
                          │     └── 从 ServletContext 中查找根容器
                          │           → getAttribute(ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE)
                          │
                          ├── ★ createWebApplicationContext(rootContext):
                          │     │
                          │     ├── 反射实例化子容器 (默认 XmlWebApplicationContext 或 AnnotationConfigWebApplicationContext)
                          │     ├── ★ wac.setParent(parent)  ← 建立父子关系!
                          │     ├── wac.setConfigLocation(getContextConfigLocation())
                          │     │     └── 默认: /WEB-INF/<servlet-name>-servlet.xml
                          │     ├── configureAndRefreshWebApplicationContext(wac):
                          │     │     ├── wac.setServletContext(getServletContext())
                          │     │     ├── wac.setServletConfig(getServletConfig())
                          │     │     ├── wac.setNamespace(getNamespace())
                          │     │     └── wac.refresh()  ← 子容器独立启动
                          │     │
                          │     └── return wac
                          │
                          └── onRefresh(wac) → DispatcherServlet.onRefresh()
                                └── initStrategies(context)  ← 初始化 9 大策略
```

### 3.2 关键代码：setParent()

```java
protected WebApplicationContext createWebApplicationContext(ApplicationContext parent) {
    Class<?> contextClass = getContextClass();
    ConfigurableWebApplicationContext wac =
        (ConfigurableWebApplicationContext) BeanUtils.instantiateClass(contextClass);

    wac.setEnvironment(getEnvironment());
    wac.setParent(parent);  // ★ 设置父容器 — 这是父子关系的核心
    wac.setConfigLocation(getContextConfigLocation());
    configureAndRefreshWebApplicationContext(wac);

    return wac;
}
```

---

## 四、父子容器 Bean 查找机制

### 4.1 getBean() 代理到父容器

```java
// AbstractBeanFactory.doGetBean()
protected <T> T doGetBean(String name, Class<T> requiredType, Object[] args, boolean typeCheckOnly) {
    // ...

    // ① 先从当前容器查找
    Object sharedInstance = getSingleton(beanName);
    if (sharedInstance != null) {
        bean = getObjectForBeanInstance(sharedInstance, name, beanName, null);
    } else {
        // ② 当前容器没有 → 检查父容器
        BeanFactory parentBeanFactory = getParentBeanFactory();
        if (parentBeanFactory != null && !containsBeanDefinition(beanName)) {
            // ★ 委托给父容器
            return parentBeanFactory.getBean(name, requiredType);
        }

        // ③ 父容器也没有 → 在当前容器创建
        // ...
    }
}
```

### 4.2 containsBean 代理

```java
// AbstractBeanFactory.containsBean()
public boolean containsBean(String name) {
    if (containsSingleton(name) || containsBeanDefinition(name)) {
        return true;
    }
    // 当前容器没有 → 问父容器
    BeanFactory parentBeanFactory = getParentBeanFactory();
    return parentBeanFactory != null && parentBeanFactory.containsBean(name);
}
```

---

## 五、WebApplicationContext 接口层次

```
ApplicationContext
  └── WebApplicationContext
        │
        ├── 常量:
        │     ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE
        │       = "org.springframework.web.context.WebApplicationContext.ROOT"
        │     SCOPE_REQUEST  = "request"
        │     SCOPE_SESSION  = "session"
        │     SCOPE_APPLICATION = "application"
        │
        └── 方法:
              getServletContext()

实现类层次:
  ConfigurableWebApplicationContext
    ├── XmlWebApplicationContext            ← 传统 XML 方式
    │     └── 读取 /WEB-INF/applicationContext.xml
    ├── AnnotationConfigWebApplicationContext ← 注解方式
    │     └── 读取 @Configuration 类
    └── AnnotationConfigServletWebServerApplicationContext  ← Spring Boot
          └── 内嵌 Web 服务器
```

---

## 六、Spring Boot 中的演变

### 6.1 传统 web.xml 方式（已废弃）

```xml
<!-- web.xml -->
<listener>
    <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
</listener>
<context-param>
    <param-name>contextConfigLocation</param-name>
    <param-value>/WEB-INF/applicationContext.xml</param-value>
</context-param>
<servlet>
    <servlet-name>dispatcher</servlet-name>
    <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
</servlet>
```

### 6.2 Spring Boot 方式

```
Spring Boot 自动配置替代手动配置:

@SpringBootApplication  → 内嵌 Tomcat
  └── SpringApplication.run()
        └── 创建 AnnotationConfigServletWebServerApplicationContext
              │
              ├── 内置了 Web Server (Tomcat/Jetty/Undertow)
              ├── 只有一个 ApplicationContext (默认)
              ├── DispatcherServlet 通过 ServletRegistrationBean 自动注册
              └── 不再需要 ContextLoaderListener
```

### 6.3 Spring Boot 的单容器模型 vs 传统双容器

```
传统 (双容器):
  ContextLoaderListener  → Root WebApplicationContext (Service/DAO)
  DispatcherServlet       → Servlet WebApplicationContext (Controller)

Spring Boot (单容器, 默认):
  AnnotationConfigServletWebServerApplicationContext
    └── 所有 Bean 在同一容器中 (Service/DAO/Controller 都在同一个 context)
    └── 通过自动配置解决 Bean 可见性问题
```

### 6.4 web.xml 替代：ServletContainerInitializer

```
Jakarta Servlet 3.0+ SPI:
  META-INF/services/jakarta.servlet.ServletContainerInitializer
    └── SpringServletContainerInitializer
          └── @HandlesTypes(WebApplicationInitializer.class)
                └── 扫描所有 WebApplicationInitializer 实现
                      │
                      ├── AbstractContextLoaderInitializer   → 注册 ContextLoaderListener
                      ├── AbstractDispatcherServletInitializer → 注册 DispatcherServlet
                      └── AbstractAnnotationConfigDispatcherServletInitializer → 注解驱动
```

---

## 七、Web 作用域

### 7.1 Request Scope

```
WebApplicationContext.SCOPE_REQUEST = "request"

每次 HTTP 请求 → 创建新的 request scope Bean
  └── RequestScope:
        └── get("scopedBean", objectFactory):
              ├── 从 RequestAttributes 获取
              │     └── RequestContextHolder.getRequestAttributes()
              │           └── ServletRequestAttributes.getAttribute(beanName, SCOPE_REQUEST)
              └── 不存在 → objectFactory.getObject() → 放入 RequestAttributes
```

### 7.2 Session Scope

```
WebApplicationContext.SCOPE_SESSION = "session"

每个 HTTP Session → 创建新的 session scope Bean
  └── SessionScope:
        └── get("scopedBean", objectFactory):
              └── HttpSession.getAttribute(beanName) / setAttribute(beanName, bean)
```

---

## 八、RequestContextHolder 与 ThreadLocal

```java
// 将当前请求的 RequestAttributes 绑定到 ThreadLocal
public abstract class RequestContextHolder {
    private static final ThreadLocal<RequestAttributes> requestAttributesHolder = new NamedThreadLocal<>("Request attributes");
    private static final ThreadLocal<RequestAttributes> inheritableRequestAttributesHolder = new NamedInheritableThreadLocal<>("Request context");
}

// FrameworkServlet.processRequest():
//   在 doService() 前后设置/清除 RequestContextHolder
RequestAttributes previousAttributes = RequestContextHolder.getRequestAttributes();
RequestContextHolder.setRequestAttributes(requestAttributes);
try {
    doService(request, response);
} finally {
    RequestContextHolder.setRequestAttributes(previousAttributes);
}
```

---

## 九、关键时序总结

| 步骤 | 触发者 | 操作 |
|------|--------|------|
| 1 | Servlet Container (Tomcat) | 加载 web.xml / 扫描 ServletContainerInitializer |
| 2 | `ContextLoaderListener.contextInitialized()` | 创建根 WebApplicationContext → `refresh()` |
| 3 | 根容器 `refresh()` 完成后 | 存入 ServletContext attribute |
| 4 | `DispatcherServlet.init()` | 从 ServletContext 获取根容器作为 parent |
| 5 | `FrameworkServlet.initWebApplicationContext()` | 创建子 WebApplicationContext → `setParent(rootCtx)` → `refresh()` |
| 6 | `DispatcherServlet.onRefresh()` | 初始化 MVC 策略 (HandlerMapping 等) |
| 7 | HTTP 请求到达 | `DispatcherServlet.doDispatch()` 处理请求 |
| 8 | Servlet Container 关闭 | `ContextLoaderListener.contextDestroyed()` → `context.close()` |

---

## 十、常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Controller 注入 Service 为 null | Service 在子容器，Controller 不在子容器 | 确保 Service 在父容器（或同一个容器） |
| NoSuchBeanDefinition for Controller | 在父容器中查找子容器的 Bean | 父容器不能访问子容器 |
| Bean 被重复创建 | 父子容器都扫描了同一个包 | 分开扫描：ContextLoaderListener 扫 service，DispatcherServlet 扫 controller |
| Request scope Bean 在非 Web 线程中使用 | 没有 RequestAttributes 绑定 | 使用 `RequestContextListener` 或确保在 Web 线程中访问 |

---

## 十一、相关文档

| 文档 | 说明 |
|------|------|
| [spring-web 模块文档](../modules/L7-spring-web.md) | HTTP 抽象层、RequestContextHolder |
| [spring-webmvc 模块文档](../modules/L7-spring-webmvc.md) | DispatcherServlet、WebApplicationContext |
| [spring-context 模块文档](../modules/L4-spring-context.md) | ApplicationContext 层次与 refresh() |
| [Spring MVC 请求生命周期](15-springmvc-request-lifecycle.md) | doDispatch() 请求分发 |
| [容器启动流程深度解析](03-startup-process.md) | refresh() 完整流程 |
