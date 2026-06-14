# spring-core 模块功能文档

---

## 一、模块定位

spring-core 是 Spring Framework 的**基石模块**，731 个 Java 文件，为上层所有模块提供：

- IoC 无关的基础抽象（`Ordered`、`ResolvableType`、`MethodParameter`）
- 类型系统与元数据（ASM 类读取、注解合并、类型解析）
- 类型转换服务（`Converter` / `ConversionService`）
- 资源抽象（`Resource` / `ResourceLoader`）
- 环境与属性（`Environment` / `PropertySource`）
- 反应式编解码器（`Encoder` / `Decoder`）
- AOT 编译提示（GraalVM `RuntimeHints`）
- 内嵌三方库：ASM、CGLIB、Objenesis、JavaPoet（重打包避免冲突）

**依赖**：`spring-jcl`（Commons Logging，已移除）。无其他模块依赖。

---

## 二、模块全景图

```
spring-core (731 files)
├── org.springframework.core/              # 核心抽象 (50 files)
│   ├── 类型抽象: ResolvableType, MethodParameter, GenericTypeResolver
│   ├── 排序体系: Ordered, PriorityOrdered, OrderComparator
│   ├── 代理标记: DecoratingProxy, InfrastructureProxy
│   ├── 反应式桥接: ReactiveAdapterRegistry, ReactiveAdapter
│   ├── 别名注册: AliasRegistry, SimpleAliasRegistry
│   ├── 版本信息: SpringVersion, SpringProperties
│   ├── 异常基类: NestedRuntimeException, NestedCheckedException
│   └── 其他: AttributeAccessor, Constants, Conventions, etc.
│
├── org.springframework.core.annotation/   # 注解支持 (34 files)
│   ├── MergedAnnotation: 注解合并与属性解析
│   ├── AnnotationUtils: 注解查找工具
│   ├── AnnotatedElementUtils: 元素注解处理
│   └── AnnotationAwareOrderComparator: 注解感知排序
│
├── org.springframework.core.convert/      # 类型转换 (67 files)
│   ├── converter/ 子包: Converter, ConverterFactory, GenericConverter
│   └── support/ 子包: DefaultConversionService 及大量内置转换器
│
├── org.springframework.core.codec/        # 编解码器 (26 files)
│   ├── Encoder / Decoder 抽象
│   └── 实现: ByteArray, ByteBuffer, String, Resource, NettyByteBuf
│
├── org.springframework.core.env/          # 环境抽象 (26 files)
│   ├── Environment / ConfigurableEnvironment
│   ├── PropertySource 层次: Map, System, Enumerable, CommandLine
│   ├── Profiles: 逻辑表达式支持
│   └── PropertyResolver: 属性占位解析
│
├── org.springframework.core.io/           # 资源I/O (61 files)
│   ├── Resource 层次: FileSystem, ClassPath, Url, ByteArray, InputStream
│   ├── ResourceLoader / ResourcePatternResolver
│   ├── WritableResource, ContextResource
│   ├── buffer/ 子包: DataBuffer, DataBufferFactory (Netty 5 based)
│   └── support/ 子包: PropertySourceFactory, EncodedResource
│
├── org.springframework.core.task/         # 任务执行 (16 files)
│   ├── TaskExecutor 接口
│   └── support/ 子包: SimpleAsyncTaskExecutor, ConcurrentTaskExecutor
│
├── org.springframework.core.type/         # 类元数据 (30 files)
│   ├── ClassMetadata, MethodMetadata, AnnotationMetadata
│   └── classreading/ 子包: SimpleMetadataReaderFactory (ASM based)
│
├── org.springframework.core.log/          # 日志工具 (6 files)
│   ├── LogDelegateFactory: 日志委托创建
│   └── LogFormatUtils: 日志格式化
│
├── org.springframework.core.metrics/      # 应用度量 (8 files)
│   ├── ApplicationStartup: 启动步骤跟踪
│   └── jfr/ 子包: Java Flight Recorder 集成
│
├── org.springframework.core.retry/        # 重试模板 (12 files)
│   ├── RetryTemplate / RetryCallback / RetryPolicy
│   └── support/ 子包: RetrySimulation
│
├── org.springframework.core.serializer/   # 序列化 (10 files)
│   ├── Serializer / Deserializer
│   └── support/ 子包: JDK, JSON 序列化支持
│
├── org.springframework.core.style/        # 对象样式 (8 files)
│   └── ToStringCreator: 生成 toString 描述
│
│  # --- 三方库内嵌（重打包，避免 classpath 冲突）---
│
├── org.springframework.asm/               # ASM 字节码库 (34 files)
├── org.springframework.cglib/             # CGLIB 代理库 (140 files)
├── org.springframework.objenesis/         # Objenesis 实例化库 (2 files)
├── org.springframework.javapoet/          # JavaPoet 代码生成 (1 file)
│
│  # --- 语言扩展 ---
│
├── org.springframework.lang/              # 语言注解 (7 files)
│   ├── @Nullable, @NonNullApi, @NonNullFields
│   └── @UsesJava8, @UsesJava9, etc.
│
│  # --- AOT 编译 ---
│
├── org.springframework.aot/               # AOT 编译支持 (82 files)
│   ├── hint/: RuntimeHints (反射/资源/序列化/代理)
│   ├── generate/: 代码生成
│   └── nativex/: GraalVM Native Image 配置
│
│  # --- 工具类 ---
│
└── org.springframework.util/              # 通用工具 (113 files)
    ├── 反射: ReflectionUtils, ClassUtils
    ├── 集合: CollectionUtils, LinkedMultiValueMap, ConcurrentReferenceHashMap
    ├── 字符串: StringUtils, AntPathMatcher, MimeType, PropertyPlaceholderHelper
    ├── I/O: StreamUtils, FileCopyUtils, FileSystemUtils
    ├── 断言: Assert
    ├── 并发: ConcurrentLruCache, CustomizableThreadCreator
    └── 其他: StopWatch, IdGenerator, DigestUtils, SerializationUtils
```

---

## 三、核心子系统代码流程

### 3.1 类型系统（ResolvableType）

```
ResolvableType.forField(field)
  │
  ├── ResolvableType.forType(field.getGenericType(), ...)
  │     │
  │     ├── 缓存查找: ConcurrentReferenceHashMap<Type, ResolvableType>
  │     │
  │     ├── Class → ResolvableType(variableResolver)
  │     ├── ParameterizedType → 解析泛型参数
  │     ├── TypeVariable → 通过 VariableResolver 解析
  │     ├── GenericArrayType → 解析数组组件类型
  │     └── WildcardType → 解析上下界
  │
  ├── 导航方法:
  │   getSuperType()   → 父类型（含泛型参数）
  │   getInterfaces()  → 接口类型
  │   getGeneric(i)    → 第 i 个泛型参数
  │   as(Type)         → 视为指定父类型
  │   asMap()          → 视为 Map<K,V>
  │   asCollection()   → 视为 Collection<E>
  │
  └── resolve()        → 最终解析为 Class<?>
      resolveGeneric(index) → 解析泛型参数为 Class
```

**关键类**：`ResolvableType`, `ResolvableTypeProvider`, `GenericTypeResolver`, `SerializableTypeWrapper`

### 3.2 排序体系（Ordered）

```
Ordered 接口
  ├── getOrder() → int (越小越优先)
  │
  ├── PriorityOrdered (extends Ordered)
  │     └── 优先级高于普通 Ordered
  │
  └── OrderComparator
        ├── 对 Ordered 对象排序
        ├── AnnotationAwareOrderComparator
        │     ├── 解析 @Order 注解
        │     ├── 解析 @Priority 注解
        │     └── 支持 javax.annotation.Priority
        └── 用于 @EventListener, @ControllerAdvice 等排序
```

### 3.3 类型转换（ConversionService）

```
用户调用: conversionService.convert(source, TargetType.class)
  │
  ├── GenericConversionService.convert(source, sourceType, targetType)
  │     │
  │     ├── 缓存查找 ConvertersForPair
  │     │     └── 无缓存 → findConverters(sourceType, targetType)
  │     │
  │     ├── Converter 匹配优先级:
  │     │   1. GenericConverter (完全匹配 sourceType → targetType)
  │     │   2. ConverterFactory (创建 sourceType → targetType 转换器)
  │     │   3. Converter<S, T> (简单一对一)
  │     │
  │     └── 执行 convert: converter.convert(source, sourceType, targetType)
  │
  ├── 内置转换器 (DefaultConversionService 注册):
  │   ├── String → Number / Enum / Boolean / Character
  │   ├── Number → Number
  │   ├── Collection → Collection / Array / String
  │   ├── Array → Collection / String
  │   ├── Map → Map
  │   ├── Object → String (toString)
  │   └── Object → Object (no-op)
  │
  └── Converter 类型层次:
        Converter<S, T>           → 简单单向转换
        ConverterFactory<S, R>    → 工厂 (String → Enum)
        GenericConverter          → 多类型对转换 (支持 TypeDescriptor)
        ConditionalGenericConverter → 条件性转换
```

### 3.4 环境抽象（Environment）

```
Environment (extends PropertyResolver)
  │
  ├── ConfigurableEnvironment
  │     ├── getPropertySources() → MutablePropertySources
  │     └── setActiveProfiles() / setDefaultProfiles()
  │
  ├── AbstractEnvironment
  │     ├── customizePropertySources() ← 子类覆盖
  │     └── 默认 profile 解析:
  │           spring.profiles.active   → activeProfiles
  │           spring.profiles.default  → defaultProfiles
  │
  ├── StandardEnvironment
  │     ├── systemProperties (JVM -D)
  │     └── systemEnvironment (OS env)
  │
  └── PropertySource 层次:
        ├── MapPropertySource
        ├── SystemEnvironmentPropertySource
        ├── PropertiesPropertySource
        ├── CommandLinePropertySource
        ├── EnumerablePropertySource
        └── CompositePropertySource
```

### 3.5 资源抽象（Resource）

```
Resource (extends InputStreamSource)
  │
  ├── AbstractResource
  │     ├── exists(), isReadable(), isOpen(), isFile()
  │     ├── getURL(), getURI(), getFile(), getFilePath()
  │     ├── contentLength(), lastModified()
  │     ├── createRelative(relativePath)
  │     └── getFilename(), getDescription()
  │
  ├── 实现类:
  │   ├── FileSystemResource       → java.io.File
  │   ├── ClassPathResource        → classpath: 协议
  │   ├── UrlResource              → http:, ftp: 等 URL
  │   ├── ByteArrayResource        → byte[]
  │   ├── InputStreamResource      → InputStream (一次性)
  │   ├── AbstractFileResolvingResource → 文件路径解析
  │   └── DescriptiveResource      → 仅描述，无实际内容
  │
  ├── WritableResource
  │     └── FileSystemResource, FileUrlResource
  │
  └── ResourceLoader
        ├── DefaultResourceLoader
        └── ResourcePatternResolver
              └── PathMatchingResourcePatternResolver (ant 模式)
```

### 3.6 注解元数据（MergedAnnotation）

```
AnnotatedElementUtils.getMergedAnnotation(element, Ann.class)
  │
  ├── AnnotationsScanner.scan(element, ...)
  │     │
  │     ├── 扫描策略:
  │     │   1. 直接注解 (element.getAnnotation)
  │     │   2. 元注解 (@AliasFor 属性别名)
  │     │   3. 组合注解 (注解上的注解)
  │     │   4. 继承层次 (父类 + 接口)
  │     │
  │     └── MergedAnnotation<T> 返回
  │           ├── getRoot()       → 根注解类型
  │           ├── getType()       → 当前合并注解类型
  │           ├── getSource()     → 原始声明位置
  │           ├── getAttributes() → 合并属性
  │           └── synthesize()    → JDK 动态代理合成
  │
  └── AnnotationTypeMappings
        └── @AliasFor 属性别名图 (有向无环图 + 循环检测)
```

### 3.7 反应式适配（ReactiveAdapterRegistry）

```
ReactiveAdapterRegistry.getSharedInstance()
  │
  ├── 静态初始化: 注册默认适配器
  │
  ├── 已注册适配 (按 classpath 可用性):
  │   ├── Reactor Mono<T>      ↔ Publisher<T>
  │   ├── Reactor Flux<T>      ↔ Publisher<T>
  │   ├── RxJava3 Flowable<T>  ↔ Publisher<T>
  │   ├── RxJava3 Observable<T>↔ Publisher<T>
  │   ├── SmallRye Mutiny Uni<T>    ↔ Publisher<T>
  │   ├── SmallRye Mutiny Multi<T>  ↔ Publisher<T>
  │   ├── CompletableFuture<T> → Publisher<T>
  │   ├── CompletionStage<T>   → Publisher<T>
  │   └── Kotlin Flow<T>       ↔ Publisher<T>
  │
  └── 核心方法:
        getAdapter(reactiveType) → ReactiveAdapter
          ├── fromPublisher()     → 适配到目标类型
          └── toPublisher()       → 转为 Reactive Streams Publisher
```

### 3.8 AOT RuntimeHints

```
RuntimeHints
  │
  ├── reflection()   → ReflectionHints
  │     └── registerType(type, memberCategories...)
  │         ├── INVOKE_DECLARED_CONSTRUCTORS
  │         ├── INVOKE_PUBLIC_CONSTRUCTORS
  │         ├── INVOKE_DECLARED_METHODS
  │         ├── INVOKE_PUBLIC_METHODS
  │         ├── DECLARED_FIELDS
  │         ├── PUBLIC_FIELDS
  │         └── ...
  │
  ├── resources()    → ResourceHints
  │     └── registerPattern("META-INF/**")
  │
  ├── serialization() → SerializationHints (已废弃 → reflection)
  │
  └── proxies()      → ProxyHints
        └── registerJdkProxy(interfaceTypes...)
```

### 3.9 重试模板（RetryTemplate）

```
RetryTemplate.execute(RetryCallback)
  │
  ├── 循环:
  │   ├── RetryPolicy.canRetry(context)
  │   │     ├── SimpleRetryPolicy       → 最多 N 次
  │   │     ├── TimeoutRetryPolicy      → 最多 N 毫秒
  │   │     └── MaxAttemptsRetryPolicy  → 最多 N 次尝试
  │   │
  │   ├── RetryCallback.doWithRetry(context)
  │   │     └── 成功 → 返回结果
  │   │     └── 异常 → RetryPolicy.registerThrowable(context, ex)
  │   │
  │   ├── BackOffPolicy.backOff(context)
  │   │     ├── FixedBackOffPolicy      → 固定间隔
  │   │     └── ExponentialBackOffPolicy→ 指数退避
  │   │
  │   └── RetryListener 回调
  │
  └── 最终: 重试耗尽 → 抛出最后异常
```

---

## 四、关键接口/类速查

| 类/接口 | 包 | 说明 |
|---------|-----|------|
| `Ordered` | `core` | 排序接口，值越小越优先 |
| `PriorityOrdered` | `core` | 高优先级标记（在 Ordered 之前排序） |
| `ResolvableType` | `core` | 泛型类型解析器，支持嵌套导航 |
| `MethodParameter` | `core` | 方法参数封装，含泛型信息和注解 |
| `GenericTypeResolver` | `core` | 泛型参数解析工具类 |
| `ReactiveAdapterRegistry` | `core` | 反应式类型适配注册表 |
| `SpringVersion` | `core` | 获取 Spring 版本号 |
| `NestedRuntimeException` | `core` | 嵌套运行时异常基类 |
| `MergedAnnotation` | `annotation` | 注解合并模型（含 @AliasFor 语义） |
| `AnnotationUtils` | `annotation` | 注解查找工具 |
| `AnnotatedElementUtils` | `annotation` | 元素注解处理（含组合注解） |
| `ConversionService` | `convert` | 类型转换服务入口 |
| `Converter<S,T>` | `convert.converter` | 单向转换器 |
| `GenericConverter` | `convert.converter` | 通用转换器（含 TypeDescriptor） |
| `DefaultConversionService` | `convert.support` | 预注册所有内置转换器的服务 |
| `Environment` | `env` | 环境抽象（profile + 属性） |
| `PropertySource<T>` | `env` | 属性源抽象 |
| `MutablePropertySources` | `env` | 可变的属性源集合 |
| `Resource` | `io` | 资源抽象（文件/类路径/URL/字节） |
| `ResourceLoader` | `io` | 资源加载器 |
| `DataBuffer` | `io.buffer` | 数据缓冲区抽象 |
| `Encoder<T>` | `codec` | 编码器（T → DataBuffer） |
| `Decoder<T>` | `codec` | 解码器（DataBuffer → T） |
| `TaskExecutor` | `task` | 任务执行器接口 |
| `RuntimeHints` | `aot.hint` | GraalVM Native Image 编译提示 |
| `ReflectionUtils` | `util` | 反射工具类 |
| `ClassUtils` | `util` | 类加载/检测工具 |
| `StringUtils` | `util` | 字符串工具 |
| `CollectionUtils` | `util` | 集合工具 |
| `Assert` | `util` | 断言工具 |
| `AntPathMatcher` | `util` | Ant风格路径匹配 |
| `PropertyPlaceholderHelper` | `util` | 属性占位符解析 (${...}) |
| `MimeType` | `util` | MIME 类型解析 |
| `StopWatch` | `util` | 简单计时器 |
| `ConcurrentReferenceHashMap` | `util` | 基于引用的并发 Map |

---

## 五、内嵌三方库说明

| 库 | 原始包名 | Spring 包名 | 用途 |
|----|---------|------------|------|
| **ASM** | `org.objectweb.asm` | `org.springframework.asm` | 字节码读取/操作，用于类扫描和代理生成 |
| **CGLIB** | `net.sf.cglib` | `org.springframework.cglib` | 动态代理（Enhancer），AOP 基础设施 |
| **Objenesis** | `org.objenesis` | `org.springframework.objenesis` | 无参构造器绕过实例化 |
| **JavaPoet** | `com.squareup.javapoet` | `org.springframework.javapoet` | AOT 代码生成时使用 |

> Spring 采用 **shade/repack** 策略将三方库复制到自己的包名下，避免与用户 classpath 中的同库不同版本冲突。

---

## 六、依赖关系

```
spring-core
  ├── compile: spring-jcl (已移除，替换为原生 Apache Commons Logging 1.3)
  ├── compile: kotlin-stdlib
  ├── compile: kotlinx-serialization
  ├── compile: io.micrometer:micrometer-observation
  ├── compileOnly: io.projectreactor.tools:blockhound
  ├── optional: io.projectreactor:reactor-core
  ├── optional: io.smallrye.reactive:mutiny
  ├── optional: io.reactivex.rxjava3:rxjava
  ├── optional: com.google.code.findbugs:jsr305
  ├── optional: org.reactivestreams:reactive-streams
  ├── optional: io.netty:netty-buffer
  └── (ASM / CGLIB / Objenesis / JavaPoet 内嵌在源码中)
```

所有 `optional` 依赖按需引入，函数式编程和响应式 adaptor 仅在对应库存在时才生效。

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-jcl](L0-spring-jcl.md) | L0 基础 | 日志门面（已移除） |
| 下游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | IoC 容器核心 |
| 下游 | [spring-expression](L3-spring-expression.md) | L3 增强 | SpEL 表达式 |
| 下游 | 所有上层模块 | L2~L9 | spring-core 是整个框架的基石 |
