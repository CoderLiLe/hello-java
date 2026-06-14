# Spring Resource 资源加载与扫描机制源码深度解析

> 本文深入分析 Spring 资源抽象体系，覆盖 Resource 接口层次、ResourceLoader/ResourcePatternResolver 资源加载、PathMatchingResourcePatternResolver 类路径扫描的实现原理、以及 ClassPathBeanDefinitionScanner 如何使用这些机制发现候选组件。
> 相关模块文档：[spring-core](../modules/L1-spring-core.md)、[spring-beans](../modules/L2-spring-beans.md)

---

## 一、Resource 接口层次

### 1.1 核心接口

```java
// 资源抽象根接口 (spring-core)
public interface Resource extends InputStreamSource {
    boolean exists();
    boolean isReadable();
    boolean isOpen();
    URL getURL() throws IOException;
    URI getURI() throws IOException;
    File getFile() throws IOException;
    long contentLength() throws IOException;
    long lastModified() throws IOException;
    Resource createRelative(String relativePath) throws IOException;
    String getFilename();
    String getDescription();
}

// 流式输入源
public interface InputStreamSource {
    InputStream getInputStream() throws IOException;
}

// 可写资源
public interface WritableResource extends Resource {
    OutputStream getOutputStream() throws IOException;
}
```

### 1.2 内置实现类

```
Resource (接口)
  │
  ├── FileSystemResource         — 文件系统资源 ("file:///path/to/file")
  ├── ClassPathResource          — 类路径资源 ("classpath:config.xml")
  ├── UrlResource                — URL 资源 ("https://example.com", "ftp://...")
  ├── ByteArrayResource          — 字节数组资源 (可写)
  ├── InputStreamResource        — 输入流资源 (一次性)
  ├── AbstractResource           — 抽象基类
  │     ├── FileSystemResource (上面已列)
  │     ├── ClassPathResource (上面已列)
  │     ├── InputStreamResource (上面已列)
  │     └── DescriptiveResource  — 纯描述性资源 (exists() 始终返回 false)
  │
  └── 子接口:
        ├── WritableResource     — 可写资源
        ├── ContextResource      — 上下文相对路径资源拓展
        └── EncodedResource      — 编码资源 (包含 charset)
```

### 1.3 典型使用

```java
// 各种前缀的资源获取
Resource fileRes = context.getResource("file:///Users/me/config.properties");
Resource httpRes = context.getResource("https://example.com/data.json");
Resource cpRes   = context.getResource("classpath:spring.xml");
Resource relRes  = context.getResource("data/schema.sql");  // 相对于 ApplicationContext 根路径

// 批量获取 (ant-style pattern)
Resource[] resources = context.getResources("classpath*:com/example/**/*.class");
```

---

## 二、ResourceLoader 体系

### 2.1 核心接口

```java
public interface ResourceLoader {
    String CLASSPATH_URL_PREFIX = "classpath:";

    Resource getResource(String location);

    @Nullable
    ClassLoader getClassLoader();
}

public interface ResourcePatternResolver extends ResourceLoader {
    String CLASSPATH_ALL_URL_PREFIX = "classpath*:";

    Resource[] getResources(String locationPattern) throws IOException;
}
```

### 2.2 ApplicationContext 的 ResourceLoader 能力

```
ApplicationContext 继承关系:
  ApplicationContext
    └── extends ResourcePatternResolver   ← getResources("classpath*:...")
          └── extends ResourceLoader       ← getResource("classpath:...")

默认实现:
  AbstractApplicationContext
    └── 内部持有 PathMatchingResourcePatternResolver (DefaultResourceLoader 的子类)
```

### 2.3 DefaultResourceLoader.getResource()

```java
public Resource getResource(String location) {
    // ① 如果以 "classpath:" 开头 → ClassPathResource
    if (location.startsWith(CLASSPATH_URL_PREFIX)) {
        return new ClassPathResource(location.substring(CLASSPATH_URL_PREFIX.length()), getClassLoader());
    }

    // ② 尝试通过 URL 解析 (包含 "file:", "http:", "ftp:" 等)
    try {
        URL url = new URL(location);
        return new UrlResource(url);
    } catch (MalformedURLException ex) {
        // ③ 当作普通文件路径 → FileSystemResource
        return new FileSystemResource(location);
    }
}
```

---

## 三、PathMatchingResourcePatternResolver

### 3.1 Ant-Style 路径匹配

```
AntPathMatcher 支持的路径模式:

?        → 匹配单个字符
*        → 匹配零个或多个字符 (不跨目录)
**       → 匹配零个或多个目录
{a,b}    → 匹配 a 或 b

示例:
  com/example/**/*.class  → 匹配 com/example/ 及其所有子目录下的 .class 文件
  com/example/*.class     → 只匹配 com/example/ 直接下的 .class 文件
  **/User*.class          → 匹配任何目录下以 User 开头的 .class
```

### 3.2 getResources() 实现

```
PathMatchingResourcePatternResolver.getResources(locationPattern):
  │
  ├── ① 如果以 "classpath*:" 开头:
  │     │
  │     ├── 去掉 "classpath*:" 前缀
  │     │
  │     ├── 确定根目录:
  │     │     ├── 模式不以 "?/*" 开头 → rootDir = 模式中最后一个非通配部分
  │     │     │     如 "com/example/**/*.class" → rootDir = "com/example/"
  │     │     └── 模式以 "?/*" 开头 → rootDir = "" (从 classpath 根开始)
  │     │
  │     └── ★ 关键: 遍历所有 ClassLoader 找到所有匹配的根目录资源:
  │           │
  │           ├── classLoader.getResources(rootDir):
  │           │     └── 合并所有 jar 包、target/classes 中的同名目录
  │           │
  │           ├── 对每个找到的根目录:
  │           │     ├── 如果是文件系统路径 → 递归遍历目录树
  │           │     │     └── AntPathMatcher 匹配每个文件
  │           │     │
  │           │     ├── 如果是 jar 包 → 遍历 jar entries
  │           │     │     └── AntPathMatcher 匹配每个 entry
  │           │     │
  │           │     └── 收集匹配的 Resource 对象
  │           │
  │           └── 返回所有匹配的 Resource[]
  │
  └── ② 如果以 "classpath:" 开头 (无 *):
        └── 只在第一个匹配的 classpath 根目录中查找
```

### 3.3 classpath* 与 classpath 的区别

```
classpath:com/example/service/*.class
  → 只从第一个匹配的 classpath 根获取 (如 target/classes)

classpath*:com/example/service/*.class  
  → 从所有 classpath 根获取 (包括 target/classes + 所有 jar 包)
  → 典型场景: 加载所有 META-INF/spring.factories
```

---

## 四、ClassPathBeanDefinitionScanner 扫描机制

### 4.1 扫描入口

```
ClassPathBeanDefinitionScanner.scan(basePackages):
  │
  └── doScan(basePackages):
        │
        └── for each basePackage:
              │
              ├── ★ findCandidateComponents(basePackage):
              │     │
              │     ├── 构建搜索模式: "classpath*:com/example/**/*.class"
              │     │
              │     ├── PathMatchingResourcePatternResolver.getResources(pattern)
              │     │     └── 获取所有 .class 文件的 Resource 对象
              │     │
              │     └── for each Resource:
              │           │
              │           ├── SimpleMetadataReaderFactory.getMetadataReader(resource):
              │           │     └── ASM ClassReader 读取字节码元数据
              │           │           ├── ClassMetadata: 类名、父类、接口、是否抽象...
              │           │           └── AnnotationMetadata: 注解信息
              │           │
              │           ├── isCandidateComponent(metadataReader):
              │           │     ├── 检查 @Component / @Service / @Repository / @Controller
              │           │     │     └── AnnotationTypeFilter 匹配
              │           │     ├── 检查 includeFilters / excludeFilters
              │           │     └── 检查 @Conditional
              │           │
              │           └── YES → 生成 ScannedGenericBeanDefinition
              │                 └── beanClass = className (String, 不加载类!)
              │
              └── 对每个候选 BeanDefinition:
                    ├── 解析 @Scope / @Lazy / @Primary / @DependsOn 等
                    ├── 生成 beanName (AnnotationBeanNameGenerator)
                    └── registry.registerBeanDefinition(beanName, beanDef)
```

### 4.2 为什么使用 ASM 而不加载类

```
方案 A: Class.forName(className) → 加载类到 JVM
  ├── 缺点: 在 PermGen/Metaspace 中加载大量类, 内存压力大
  ├── 缺点: 类的 static 初始化块会被执行
  └── 缺点: 并发场景下类加载锁竞争

方案 B: ASM ClassReader → 只读字节码元数据
  ├── 优点: 不加载类, 不占用 Metaspace
  ├── 优点: 不触发 static 初始化
  ├── 优点: 速度快, 无锁竞争
  └── ★ Spring 默认使用 ASM 方案
```

### 4.3 SimpleMetadataReaderFactory 内部流程

```
SimpleMetadataReaderFactory.getMetadataReader(resource):
  │
  └── new SimpleMetadataReader(resource, classLoader):
        │
        ├── 通过 resource.getInputStream() 获取字节码流
        │
        ├── ClassReader.accept(visitor, PARSING_OPTIONS):
        │     │
        │     ├── ClassMetadataReadingVisitor.visit():
        │     │     ├── visit(version, access, name, ...): 读取类名/修饰符
        │     │     ├── visitSource(file, debug): 读取源文件信息
        │     │     ├── visitOuterClass/visitInnerClass: 读取外部/内部类信息
        │     │     └── visitField / visitMethod: 读取字段/方法 (含注解)
        │     │
        │     └── AnnotationMetadataReadingVisitor.visitAnnotation():
        │           └── 读取所有注解 (含属性值, 但不解析注解 Class)
        │
        └── 返回 SimpleMetadataReader { classMetadata, annotationMetadata }
```

---

## 五、编码资源 (EncodedResource)

```java
// 支持带编码的资源加载
EncodedResource encoded = new EncodedResource(resource, StandardCharsets.UTF_8);
Reader reader = encoded.getReader();  // → InputStreamReader(resource.getInputStream(), UTF_8)

// XmlBeanDefinitionReader 内部使用:
// 解析 XML 时, 通过 EncodedResource 获取 Reader, 确保正确编码
```

---

## 六、PropertySourceFactory (资源到 PropertySource)

```java
// @PropertySource 注解底层使用 PropertySourceFactory
@PropertySource(value = "classpath:app.properties", factory = DefaultPropertySourceFactory.class)

// DefaultPropertySourceFactory:
public PropertySource<?> createPropertySource(String name, EncodedResource resource) {
    Properties props = new Properties();
    props.load(resource.getReader());  // 从 Resource 加载 Properties
    return new PropertiesPropertySource(name, props);
}
```

---

## 七、典型应用场景

| 场景 | API | 说明 |
|------|-----|------|
| 加载配置文件 | `new ClassPathResource("config.xml")` | 单文件加载 |
| 加载 XML Bean 定义 | `XmlBeanDefinitionReader.loadBeanDefinitions("classpath:spring.xml")` | 内部使用 ResourceLoader |
| @ComponentScan 扫描 | `ClassPathBeanDefinitionScanner.scan("com.example")` | 内部使用 PathMatchingResourcePatternResolver |
| 加载 META-INF 资源 | `getResources("classpath*:META-INF/spring.factories")` | 遍历所有 jar |
| @PropertySource | `@PropertySource("classpath:app.properties")` | 内部使用 Resource + PropertySourceFactory |
| 文件上传 | Spring MVC 使用 `CommonsMultipartFile` → 内部使用 `ByteArrayResource` | 

---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| [spring-core 模块文档](../modules/L1-spring-core.md) | Resource 接口体系 |
| [配置类解析](02-configuration-class-parsing.md) | @ComponentScan 扫描逻辑 |
| [BeanDefinition 体系](01-beandefinition-system.md) | BeanDefinition 注册 |
