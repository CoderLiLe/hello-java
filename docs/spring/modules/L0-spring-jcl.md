# spring-jcl 模块功能文档

> **状态：已移除** — commit `3db1b94465`（2024-12-12）将 spring-jcl 替换为标准的 Apache Commons Logging 1.3（`org.apache.commons:commons-logging`）。
> 原 spring-jcl 是一个最小化 JCL 桥接层（Log4j → SLF4J → JUL 自动检测），现已不再维护，所有功能由上游标准库直接提供。
> 以下内容基于被移除前的源码，仅供历史参考。

---

## 一、模块定位

spring-jcl 是 Spring Framework 对 **Apache Commons Logging（JCL）** API 的自实现变体。它不是完整的 JCL 实现，而是一个**最小化桥接层**：

- 提供 `Log` 接口和 `LogFactory` 工厂类，与原始 JCL API 源码/二进制兼容
- 运行时自动检测 classpath 中的日志框架（Log4j 2.x → SLF4J → JUL），无需手动排除 JCL jar 或引入额外桥接包
- 自身无外部依赖；Log4j 和 SLF4J 均为 `optional` 依赖

## 二、源码文件清单

```
spring-jcl/src/main/java/org/apache/commons/logging/
├── Log.java                    # 日志接口 (6 级别)
├── LogFactory.java             # 静态工厂 (入口)
├── LogAdapter.java             # 核心适配器 (provider 检测 + 4 种内部实现)
├── LogFactoryService.java      # META-INF/services SPI 实现 (已废弃)
└── impl/
    ├── NoOpLog.java            # 空实现 (丢弃所有日志)
    ├── SimpleLog.java          # 已废弃，等同于 NoOpLog
    └── package-info.java

spring-jcl/src/main/resources/META-INF/services/
└── org.apache.commons.logging.LogFactory   # SPI 声明
```

## 三、核心类职责

| 类 | 可见性 | 职责 |
|---|--------|------|
| `Log` | public | 日志接口，定义 trace/debug/info/warn/error/fatal 六个级别 |
| `LogFactory` | public abstract | 静态工厂，提供 `getLog(Class/String)` 入口；兼容旧式 `getFactory()/getInstance()` 方法 |
| `LogAdapter` | package-private final | **核心**：静态初始化时检测日志提供者，选择创建策略；内含 Log4jLog / Slf4jLog / Slf4jLocationAwareLog / JavaUtilLog 四个内部类 |
| `LogFactoryService` | public（已废弃） | 当标准 commons-logging.jar 意外存在时，用 META-INF 服务发现机制替代标准 LogFactory |
| `NoOpLog` | public | 空操作实现，所有方法为空 |
| `SimpleLog` | public（已废弃） | 继承 NoOpLog，仅在构造时打印废弃警告 |

## 四、代码流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           调用入口                                           │
│                                                                             │
│   LogFactory.getLog(Class)    LogFactory.getLog(String)                     │
│         │                          │                                        │
│         └──────────┬───────────────┘                                        │
│                    ↓                                                        │
│         LogAdapter.createLog(name)                                          │
│                    │                                                        │
│                    ↓                                                        │
│         ┌──────────────────────┐                                            │
│         │ createLog.apply(name) │  ← Function<String, Log>                  │
│         └──────────────────────┘                                            │
│                    │                                                        │
│                    ↓                                                        │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │     createLog 在 LogAdapter 静态初始化时被绑定到以下之一:            │    │
│   │                                                                    │    │
│   │  ┌─────────────────────────────────────────────────────────────┐   │    │
│   │  │          静态初始化块 Provider 检测逻辑                       │   │    │
│   │  │                                                             │   │    │
│   │  │  isPresent("o.a.l.log4j.spi.ExtendedLogger")?               │   │    │
│   │  │       │                                                     │   │    │
│   │  │       ├── YES                                               │   │    │
│   │  │       │     │                                               │   │    │
│   │  │       │     ├── log4j-to-slf4j bridge 存在?                  │   │    │
│   │  │       │     │     ├── YES → Slf4jAdapter::createLocationAwareLog │
│   │  │       │     │     └── NO  → Log4jAdapter::createLog           │   │    │
│   │  │       │     │          (Log4jLog)                             │   │    │
│   │  │       │                                                      │   │    │
│   │  │       └── NO                                                │   │    │
│   │  │             │                                                │   │    │
│   │  │             isPresent("o.s.spi.LocationAwareLogger")?       │   │    │
│   │  │             │                                                │   │    │
│   │  │             ├── YES → Slf4jAdapter::createLocationAwareLog   │   │    │
│   │  │             │          (Slf4jLocationAwareLog)               │   │    │
│   │  │             │                                                │   │    │
│   │  │             └── NO                                          │   │    │
│   │  │                   │                                          │   │    │
│   │  │                   isPresent("org.slf4j.Logger")?            │   │    │
│   │  │                   │                                          │   │    │
│   │  │                   ├── YES → Slf4jAdapter::createLog          │   │    │
│   │  │                   │          (Slf4jLog)                      │   │    │
│   │  │                   │                                          │   │    │
│   │  │                   └── NO → JavaUtilAdapter::createLog        │   │    │
│   │  │                              (JavaUtilLog)  ← 最终兜底       │   │    │
│   │  └─────────────────────────────────────────────────────────────┘   │    │
│   └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

                            日志实现内部流转细节
                            ═══════════════════

┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────────────┐
│    Log4jLog      │     │  Slf4jLocationAwareLog│    │      JavaUtilLog         │
│                  │     │                     │     │                          │
│ 依赖:            │     │ 继承: Slf4jLog       │     │ 依赖:                    │
│ ExtendedLogger   │     │ 实现: LocationAware  │     │ java.util.logging.Logger │
│ (Log4j 2.x)      │     │                     │     │                          │
│                  │     │ log(msg):           │     │ log(msg):                │
│ log(msg):        │     │  String →           │     │  String →                │
│  String →        │     │  logger.log(FQCN,   │     │  new LogRecord()         │
│  logger.logIf-   │     │    LEVEL_INT, msg,  │     │  → logger.log(record)    │
│  Enabled(FQCN,   │     │    null, exception) │     │                          │
│    level, null,  │     │                     │     │ 含 LocationResolving-     │
│    msg, exc)     │     │ fatal → error       │     │ LogRecord 用于延迟解析    │
│                  │     │                     │     │ 调用者位置信息            │
│ fatal: 原生支持  │     │                     │     │                          │
└──────────────────┘     └─────────────────────┘     └──────────────────────────┘

┌─────────────────────┐
│      Slf4jLog       │
│                     │
│ 依赖: org.slf4j.Logger
│
│ log(msg):
│  String → logger.xxx(msg)
│  (无位置感知)
│
│ fatal → error
└─────────────────────┘

┌──────────┐
│ NoOpLog  │  ← SimpleLog 继承它（已废弃）
│ (全部空) │
└──────────┘
```

## 五、Provider 检测优先级

| 优先级 | 检测条件 | 创建策略 | 位置感知 |
|--------|---------|---------|----------|
| 1 | Log4j 2.x SPI 存在 **且** log4j-to-slf4j 桥存在 **且** SLF4J SPI 存在 | `Slf4jLocationAwareLog` | 是 |
| 2 | Log4j 2.x SPI 存在 | `Log4jLog` | 是（通过 FQCN） |
| 3 | SLF4J LocationAwareLogger 存在 | `Slf4jLocationAwareLog` | 是 |
| 4 | SLF4J Logger 存在 | `Slf4jLog` | 否 |
| 5 | 以上皆无 | `JavaUtilLog` | 是（通过堆栈解析） |

**设计考量**：
- 优先级 1 避免 log4j-to-slf4j 桥双重包装（Log4j → SLF4J → 再包装一次 SLF4J）
- Log4j 优先级高于纯 SLF4J，因为纯 SLF4J API 无位置感知能力
- JUL 为最终兜底，即使在 JDK 9+ 的 `java.logging` 模块未加载时也能安全降级（使用懒初始化）

## 六、Log 接口日志级别映射

| JCL Level | Log4j 2.x | SLF4J | JUL |
|-----------|-----------|-------|-----|
| `fatal` | `Level.FATAL` | → `error` | → `SEVERE` |
| `error` | `Level.ERROR` | `ERROR` | `SEVERE` |
| `warn` | `Level.WARN` | `WARN` | `WARNING` |
| `info` | `Level.INFO` | `INFO` | `INFO` |
| `debug` | `Level.DEBUG` | `DEBUG` | `FINE` |
| `trace` | `Level.TRACE` | `TRACE` | `FINEST` |

> SLF4J 和 JUL 不原生支持 `fatal` 级别，均映射到 `error` / `SEVERE`。

## 七、关键设计点

1. **静态绑定一次**：`LogAdapter` 的 `createLog` 是 `static final Function<String, Log>`，在类加载时确定，之后每次 `getLog()` 只是 `Function.apply(name)`，无锁、无反射、无分支。

2. **序列化安全**：所有内部 Log 实现都实现 `Serializable`，并通过 `readResolve()` 反序列化时重新通过 `LogAdapter` 获取 Logger（防止 transient 字段丢失）。

3. **Log4j 参数展开绕过**：`Log4jLog.log()` 判断 `message instanceof String`，若为 String 则显式传递为 text 参数，避免 Log4j 将 `{}` 序列误解析为参数占位符（SPR-16226）。

4. **JUL 调用者位置延迟解析**：`LocationResolvingLogRecord` 覆写 `getSourceClassName()/getSourceMethodName()`，在首次调用时通过堆栈解析，且通过 `writeReplace()` 确保序列化时产出一个普通 `LogRecord`。

5. **SPI 兜底**：`LogFactoryService`（META-INF/services）在标准 commons-logging.jar 意外存在时，通过 SPI 发现并代理到 `LogAdapter.createLog()`，同时打印警告提示移除 commons-logging.jar。

## 八、依赖关系

```
spring-jcl (无 api 依赖)
  ├── optional: org.apache.logging.log4j:log4j-api
  └── optional: org.slf4j:slf4j-api
```

所有依赖均为 `optional`，使用者按需引入。默认不引入任何外部日志库时，走 JUL 兜底。

---

## 九、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 下游 | [spring-core](L1-spring-core.md) | L1 核心 | 唯一使用者，日志门面 |

> 注意：该模块已移除，`spring-core` 现直接依赖标准 Apache Commons Logging 1.3。
