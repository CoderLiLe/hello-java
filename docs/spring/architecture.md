# Spring Framework 项目架构图

```
                        ┌─────────────────────────────────────────┐
                        │           Testing & Tooling             │
                        │  ┌──────────────┐  ┌────────────────┐  │
                        │  │ spring-test  │  │ spring-core-   │  │
                        │  │  (TestContext│  │     test       │  │
                        │  │  Framework)  │  │ (RuntimeHints) │  │
                        │  └──────────────┘  └────────────────┘  │
                        └─────────────────────────────────────────┘
                                        ↑ (optional deps on all web modules)

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              WEB TIER                                           │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────────────────────┐    │
│  │spring-websocket│  │spring-webmvc │  │       spring-webflux              │    │
│  │  (WebSocket)   │  │  (Servlet MVC)│  │    (Reactive Web)                 │    │
│  │               │  │               │  │    reactor-core                   │    │
│  └───────┬───────┘  └───────┬───────┘  └────────┬─────────────────────────┘    │
│          │                  │                    │                               │
│          └──────────┬───────┴────────────────────┘                               │
│                     ↓                                                            │
│            ┌─────────────────────────────────────┐                              │
│            │           spring-web                │                              │
│            │   (HTTP, Multipart, REST Client,    │                              │
│            │    WebSocket common, CORS, Codecs)  │                              │
│            └────────────────┬────────────────────┘                              │
└─────────────────────────────┼───────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────────────────────┐
│                      MESSAGING TIER                                             │
│  ┌───────────────┐         │                                                    │
│  │   spring-jms  │         │                                                    │
│  │  (JMS Support)│─────────┼──────┐                                             │
│  └───────┬───────┘         │      │                                             │
│          ↓                 │      │                                             │
│  ┌─────────────────────────┼──────┘                                             │
│  │    spring-messaging     │                                                    │
│  │  (Message, Channel,     │                                                    │
│  │   Handler, WebSocket)   │                                                    │
│  └────────────┬────────────┘                                                    │
└───────────────┼─────────────────────────────────────────────────────────────────┘
                │
┌───────────────┼─────────────────────────────────────────────────────────────────┐
│               │            CONTEXT TIER                                         │
│  ┌────────────┼────────────┐   ┌──────────────────────┐                        │
│  │ spring-context-support   │   │  spring-context-indexer│                      │
│  │ (Caching, Mail, FreeMarker│   │  (Compile-time Index)  │                      │
│  │  Quartz, Scheduling)     │   └──────────────────────┘                        │
│  └────────────┼────────────┘                                                    │
│               ↓                                                                 │
│  ┌──────────────────────────────────────────────┐                               │
│  │              spring-context                  │                               │
│  │  (ApplicationContext, DI, Event, Scheduling, │                               │
│  │   Validation, JNDI, SpEL integration)        │                               │
│  │  api: micrometer-observation                 │                               │
│  └───────┬──────────────────┬───────────────────┘                               │
│          │                  │                                                    │
└──────────┼──────────────────┼───────────────────────────────────────────────────┘
           │                  │
┌──────────┼──────────────────┼───────────────────────────────────────────────────┐
│          ↓                  ↓         AOP + EXPRESSION TIER                     │
│  ┌───────────────┐  ┌──────────────────────┐                                    │
│  │ spring-aop    │  │ spring-expression    │                                    │
│  │ (AOP Alliance,│  │     (SpEL)           │                                    │
│  │  Proxy, Aspect│  └──────────┬───────────┘                                    │
│  │  J)           │             │                                                │
│  └───────┬───────┘             │                                                │
└──────────┼─────────────────────┼────────────────────────────────────────────────┘
           │                     │
           └──────────┬──────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CORE TIER (IoC Container)                               │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────┐                       │
│  │                   spring-beans                        │                       │
│  │  (BeanFactory, BeanWrapper, PropertyEditor,          │                       │
│  │   TypeConverter, Annotation Metadata)                │                       │
│  └────────────────────────┬─────────────────────────────┘                       │
│                           ↓                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           spring-core                                    │   │
│  │  (Utils, Reflection, Converter, Codec, Reactive Streams bridge,          │   │
│  │   AOT, GraalVM, ASM, CGLIB, Kotlin support)                              │   │
│  └──────────────────────────────┬──────────────────────────────────────────┘   │
│                                 ↓                                               │
│  ┌──────────────────────────────────────────────┐                               │
│  │                spring-jcl                     │                               │
│  │          (Commons Logging Bridge)             │                               │
│  └──────────────────────────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                       DATA ACCESS TIER (right side)                             │
│                                                                                 │
│  ┌───────────────┐                                                              │
│  │   spring-tx   │  ← depends on spring-beans, spring-core                      │
│  │ (Transaction  │                                                              │
│  │  Management)  │                                                              │
│  └───┬───┬───┬───┘                                                              │
│      │   │   │                                                                  │
│      ↓   │   └──────────────────────┐                                           │
│  ┌──────────────┐                   │                                           │
│  │ spring-jdbc  │                   │                                           │
│  │ (JDBC, Data- │                   │                                           │
│  │  Source, Jdbc│                   │                                           │
│  │  Template)   │                   │                                           │
│  └──────┬───────┘                   │                                           │
│         ↓                           │                                           │
│  ┌──────────────┐                   │                                           │
│  │  spring-orm  │                   │                                           │
│  │  (Hibernate, │                   │                                           │
│  │   JPA)       │                   │                                           │
│  └──────────────┘                   │                                           │
│                                     ↓                                           │
│                            ┌──────────────────┐   ┌──────────────┐              │
│                            │  spring-r2dbc    │   │  spring-oxm  │              │
│                            │  (Reactive       │   │  (Object/XML │              │
│                            │   RDBMS)         │   │   Marshall)  │              │
│                            └──────────────────┘   └──────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────┘

                  ┌──────────────────────┐
                  │  Instrumentation     │
                  │  ┌────────────────┐  │
                  │  │spring-instrument│  │  ← Java Agent (Premain-Class)
                  │  │spring-aspects  │  │  ← AspectJ compile-time weaving
                  │  └────────────────┘  │
                  └──────────────────────┘
```

---

## 依赖层级总结（从底向上）

| 层级 | 模块 | 职责 |
|------|------|------|
| **L0 基础** | `spring-jcl` | Commons Logging 桥接 |
| **L1 核心** | `spring-core` | 反射、工具类、ASM、AOT |
| **L2 Bean容器** | `spring-beans` | BeanFactory、类型转换、元数据 |
| **L3 增强** | `spring-aop`, `spring-expression` | AOP代理织入、SpEL表达式 |
| **L4 上下文** | `spring-context`, `spring-context-support`, `spring-context-indexer` | ApplicationContext、DI、事件、调度 |
| **L5 事务** | `spring-tx` | 声明式事务管理 |
| **L6 数据** | `spring-jdbc`, `spring-r2dbc`, `spring-orm`, `spring-oxm` | JDBC/ORM/R2DBC/OXM |
| **L6 消息** | `spring-messaging`, `spring-jms` | 消息通道、JMS |
| **L7 Web** | `spring-web`, `spring-webmvc`, `spring-webflux`, `spring-websocket` | HTTP、Servlet MVC、响应式Web |
| **L8 测试** | `spring-test`, `spring-core-test` | TestContext框架、AOT测试 |
| **辅助** | `spring-instrument`, `spring-aspects` | Java Agent、AspectJ切面 |

---

## 模块依赖关系（api 级别）

```
spring-jcl
  └── spring-core
        ├── spring-beans
        │     ├── spring-aop ─────────────────────────────────────────────┐
        │     ├── spring-expression ──────────────────────────────────────┤
        │     ├── spring-tx ──────────────────────────────────────────────┤
        │     ├── spring-messaging ───────────────────────────────────────┤
        │     ├── spring-web ─────────────────────────────────────────────┤
        │     ├── spring-context-support ─────────────────────────────────┤
        │     ├── spring-jdbc ────────────────────────────────────────────┤
        │     ├── spring-orm ─────────────────────────────────────────────┤
        │     ├── spring-oxm ─────────────────────────────────────────────┤
        │     ├── spring-r2dbc ───────────────────────────────────────────┤
        │     └── spring-websocket (via spring-context) ──────────────────┤
        │                                                                  │
        ├── spring-context (api: spring-aop, spring-beans, spring-expression)──┤
        │     ├── spring-context-support ────────────────────────────────┤
        │     ├── spring-webmvc (api: spring-web, spring-context) ────────┤
        │     └── spring-websocket (api: spring-context, spring-web) ─────┤
        │                                                                  │
        ├── spring-webflux (api: spring-web, reactor-core) ────────────────┤
        │                                                                  │
        ├── spring-jms (api: spring-messaging, spring-tx) ─────────────────┤
        │                                                                  │
        ├── spring-orm (api: spring-jdbc, spring-tx) ──────────────────────┤
        │                                                                  │
        └── spring-test (optional: all modules) ───────────────────────────┘
```
