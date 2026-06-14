# Spring Environment 环境抽象与属性解析源码深度解析

> 本文深入分析 Spring Environment 环境抽象，覆盖 PropertySource 层次链、Profile 逻辑表达式匹配、PropertySourcesPlaceholderConfigurer 占位符替换、@PropertySource 属性文件加载以及 Environment 在容器启动时的角色。
> 相关模块文档：[spring-core](../modules/L1-spring-core.md)、[spring-context](../modules/L4-spring-context.md)

---

## 一、Environment 接口层次

```
PropertyResolver                          — 属性解析: getProperty, resolvePlaceholders
  │
  └── ConfigurablePropertyResolver       — 可配置解析器
        │
        ├── Environment                    — ★ 环境抽象根接口
        │     └── ConfigurableEnvironment  — 可配置环境
        │           └── AbstractEnvironment
        │                 ├── StandardEnvironment        (非 Web)
        │                 └── StandardServletEnvironment (Web, 含 Servlet 属性源)
        │
        └── ConfigurableWebEnvironment    — Web 环境接口扩展
```

### 核心方法

```java
public interface Environment extends PropertyResolver {
    // ★ Profile 相关
    String[] getActiveProfiles();
    String[] getDefaultProfiles();
    boolean acceptsProfiles(Profiles profiles);

    // 继承自 PropertyResolver:
    // boolean containsProperty(String key);
    // String getProperty(String key);
    // String getProperty(String key, String defaultValue);
    // <T> T getProperty(String key, Class<T> targetType);
    // <T> T getProperty(String key, Class<T> targetType, T defaultValue);
    // String resolvePlaceholders(String text);
    // String resolveRequiredPlaceholders(String text);
}
```

---

## 二、PropertySource 层次链

### 2.1 PropertySource 抽象

```java
public abstract class PropertySource<T> {
    protected final String name;
    protected final T source;

    public abstract Object getProperty(String key);

    // 静态工厂方法
    public static PropertySource<?> named(String name) { ... }
}
```

### 2.2 内置 PropertySource 实现

| 实现 | 来源 | 说明 |
|------|------|------|
| `MapPropertySource` | `Map<String, Object>` | 通用 Map 属性源 |
| `SystemEnvironmentPropertySource` | `System.getenv()` | OS 环境变量 |
| `PropertiesPropertySource` | `Map<String, Object>` (copy) | 与 MapPropertySource 类似，但复制 |
| `CommandLinePropertySource` | 命令行参数 `--key=value` | Spring Boot 提供 |
| `ServletConfigPropertySource` | `ServletConfig.getInitParameters()` | Web 环境 |
| `ServletContextPropertySource` | `ServletContext.getInitParameters()` | Web 环境 |
| `JndiPropertySource` | JNDI 查找 | 企业环境 |
| `CompositePropertySource` | 多个 PropertySource 迭代 | 组合模式 |
| `StubPropertySource` | 占位符 | JNDI 未找到时的兜底 |

### 2.3 PropertySources — 有序链式查找

```java
public interface PropertySources extends Iterable<PropertySource<?>> {
    boolean contains(String name);
    PropertySource<?> get(String name);
}

// 核心实现: 有序列表, 先添加的优先级更高
public class MutablePropertySources implements PropertySources {
    private final List<PropertySource<?>> propertySourceList = new CopyOnWriteArrayList<>();

    public void addFirst(PropertySource<?> propertySource) { ... }
    public void addLast(PropertySource<?> propertySource) { ... }
    public void addBefore(String relativeName, PropertySource<?> propertySource) { ... }
    public void addAfter(String relativeName, PropertySource<?> propertySource) { ... }
}
```

### 2.4 StandardEnvironment 默认 PropertySource 顺序

```
StandardEnvironment (非 Web):
  ① systemProperties         — System.getProperties() (如 java.version)
  ② systemEnvironment        — System.getenv()        (如 PATH, HOME)

StandardServletEnvironment (Web):
  ① servletConfigInitParams  — ServletConfig init-params (最高优先级)
  ② servletContextInitParams — ServletContext init-params
  ③ jndiProperties           — JNDI (如果可用)
  ④ systemProperties         — JVM 系统属性
  ⑤ systemEnvironment        — OS 环境变量

@PropertySource 加载的属性 → addLast() 添加到最后 (最低优先级)
```

### 2.5 属性查找顺序

```
getProperty("app.name"):
  │
  └── 遍历 MutablePropertySources.propertySourceList (顺序):
        ├── ① servletConfigInitParams    → 找到? → 返回
        ├── ② servletContextInitParams   → 找到? → 返回
        ├── ③ systemProperties           → 找到? → 返回
        ├── ④ systemEnvironment          → 找到? → 返回
        ├── ⑤ @PropertySource("app.properties") → 找到? → 返回
        ├── ⑥ @PropertySource("db.properties")  → 找到? → 返回
        └── ⑦ 未找到 → null (或抛 IllegalStateException 如果 required)
```

---

## 三、Profiles 机制

### 3.1 Profile 配置方式

```java
// 编程式
context.getEnvironment().setActiveProfiles("dev", "mysql");
System.setProperty("spring.profiles.active", "dev");

// @Profile 注解
@Configuration
@Profile("dev")
public class DevConfig { ... }

// 逻辑表达式
@Profile("dev & mysql")     // 需要同时满足 dev 和 mysql
@Profile("dev | prod")       // 满足 dev 或 prod
@Profile("!test")             // 非 test
@Profile("(dev | prod) & mysql")  // 复合表达式
```

### 3.2 Profiles 解析

```java
// AbstractEnvironment.acceptsProfiles(Profiles profiles)
// Profiles 接口 (支持逻辑表达式):
public interface Profiles {
    boolean matches(Predicate<String> activeProfiles);
}

// Profiles.of("dev & (mysql | postgres)"):
//   内部解析为: and(equals("dev"), or(equals("mysql"), equals("postgres")))
//   matches: activeProfiles 包含 "dev" 且 (包含 "mysql" 或 "postgres")
```

### 3.3 Profile 决定 Bean 是否注册

```
ConfigurationClassPostProcessor 解析 @Configuration 类时:
  │
  ├── 类级 @Profile → 检查是否匹配:
  │     ├── 匹配 → 继续解析类中的 @Bean 方法
  │     └── 不匹配 → 跳过整个类 (不注册其 @Bean)
  │
  └── 方法级 @Profile → 检查是否匹配:
        ├── 匹配 → 注册 @Bean
        └── 不匹配 → 跳过
```

---

## 四、@PropertySource 属性文件加载

### 4.1 注解定义

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Repeatable(PropertySources.class)
public @interface PropertySource {
    String name() default "";
    String[] value();                        // 文件路径 (支持 classpath: / file:)
    boolean ignoreResourceNotFound() default false;
    String encoding() default "";
    Class<? extends PropertySourceFactory> factory() 
        default DefaultPropertySourceFactory.class;
}
```

### 4.2 加载流程

```
ConfigurationClassParser 解析 @PropertySource:
  │
  ├── ① 获取 @PropertySource 注解属性
  │
  ├── ② 解析文件路径: resolvePlaceholders("classpath:${env}/app.properties")
  │
  ├── ③ ResourceLoader.getResources(location) → Resource[]
  │
  ├── ④ PropertySourceFactory.createPropertySource(name, encodedResource):
  │     └── DefaultPropertySourceFactory → PropertiesPropertySource
  │
  └── ⑤ ★ 添加到 Environment:
        environment.getPropertySources().addLast(propertySource)
        └── addLast: 添加到最后, systemProperties 优先级高于它
```

---

## 五、PropertySourcesPlaceholderConfigurer

### 5.1 角色

`PropertySourcesPlaceholderConfigurer` 是 BeanFactoryPostProcessor，负责在 BeanDefinition 加载后、Bean 实例化前，替换 `${...}` 占位符。

### 5.2 处理流程

```
PropertySourcesPlaceholderConfigurer.postProcessBeanFactory(beanFactory):
  │
  ├── ① 获取 Environment (自动集成)
  │     └── 将 MutablePropertySources 作为查找源
  │
  ├── ② 创建 StringValueResolver:
  │     └── PropertyPlaceholderHelper.replacePlaceholders(value, placeholderResolver)
  │           │
  │           └── placeholderResolver:
  │                 ├── ① 从 environment 查找 key
  │                 ├── ② 从 localProperties 查找 (setProperties)
  │                 └── ③ 从 systemProperties (合并)
  │
  └── ③ ★ 注册为 EmbeddedValueResolver:
        ((AbstractBeanFactory) beanFactory).addEmbeddedValueResolver(valueResolver)
        └── 之后所有 Bean 的 @Value("${...}") 都会被此 Resolver 解析
```

### 5.3 占位符解析示例

```
@Value("${app.name:defaultApp}")
  │
  └── EmbeddedValueResolver.resolveStringValue("${app.name:defaultApp}"):
        └── PropertyPlaceholderHelper.replacePlaceholders():
              │
              ├── 查找 key = "app.name"
              │     ├── environment.getProperty("app.name")
              │     │     └── MutablePropertySources 链式查找 (见 §2.4)
              │     └── 找到? → 返回 value
              │
              ├── 未找到 → 使用默认值 ":defaultApp"
              │
              └── 未找到且无默认值 → throw IllegalArgumentException
```

### 5.4 占位符递归解析

```
占位符支持嵌套:
  @Value("${app.${env}.name}")

解析过程:
  ① 先解析 ${env} → "prod"
  ② 再解析 ${app.prod.name} → "MyApp"
```

---

## 六、@Value 表达式完整解析链

```
@Value("${server.port:8080}")
int port;

解析链:
  AutowiredAnnotationBeanPostProcessor.resolveFieldValue()
    → resolveDependency()
      → EmbeddedValueResolver.resolveStringValue("${server.port:8080}")
        → PropertyPlaceholderHelper.replacePlaceholders("${server.port:8080}")
            ├── 先尝试 environment.getProperty("server.port")
            ├── 未找到 → environment.getProperty("server.port:8080")
            │              → MutablePropertySources 链式查找
            │              → 未找到 → 使用默认值 "8080"
            └── 返回 "8080"
        → TypeConverter.convertIfNecessary("8080", int.class)
          → Integer.parseInt("8080") → 8080
```

---

## 七、Environment 在 Spring Boot 中的扩展

Spring Boot 在 StandardEnvironment 基础上添加了更多 PropertySource：

```
Spring Boot ApplicationEnvironment (扩展 StandardEnvironment):
  ① DevToolsPropertyDefaultsPropertySource  (DevTools 默认值)
  ② @TestPropertySource                        (测试)
  ③ @SpringBootTest properties (测试)
  ④ commandLineArgs                            (--server.port=8080)
  ⑤ servletConfig/servletContext               (Web)
  ⑥ systemProperties
  ⑦ OS environment variables
  ⑧ random                                     (${random.int})
  ⑨ application-{profile}.properties          (外部配置)
  ⑩ application-{profile}.yml / yaml          (外部配置)
  ⑪ @PropertySource                            (注解配置)
  ⑫ application.properties / application.yml   (默认配置)
```

---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| [spring-core 模块文档](../modules/L1-spring-core.md) | Environment、PropertySource 接口 |
| [spring-context 模块文档](../modules/L4-spring-context.md) | @PropertySource、Profile 解析 |
| [容器启动流程深度解析](03-startup-process.md) | PropertySourcesPlaceholderConfigurer 执行时机 |
| [依赖注入深度解析](06-dependency-injection.md) | @Value 占位符解析链 |
