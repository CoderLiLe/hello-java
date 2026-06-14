# Spring Framework 文档索引

基于 [architecture.md](architecture.md) 中的依赖层级体系，文档按类别组织在子目录中。

---

## 目录结构

```
doc/
├── INDEX.md                  — 本文件（导航索引）
├── architecture.md           — 项目架构全图 + 依赖层级
├── modules/                  — 各模块功能文档（23 个）
├── deep-dive/                — 核心机制源码深度解析（15 个）
├── diagrams/                 — 可视化架构图（3 个 HTML）
└── guides/                   — 实践指南（1 个）
```

---

## 模块文档（按层级）

### L0 基础层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L0-spring-jcl.md](modules/L0-spring-jcl.md) | spring-jcl | Commons Logging 桥接 |

### L1 核心层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L1-spring-core.md](modules/L1-spring-core.md) | spring-core | 反射、工具类、ASM、AOT、类型转换、资源抽象 |

### L2 Bean 容器层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L2-spring-beans.md](modules/L2-spring-beans.md) | spring-beans | BeanFactory、类型转换、DI、BeanPostProcessor、XML 配置 |

### L3 增强层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L3-spring-aop.md](modules/L3-spring-aop.md) | spring-aop | AOP 代理织入、拦截器链、@AspectJ 注解支持 |
| [L3-spring-expression.md](modules/L3-spring-expression.md) | spring-expression | SpEL 表达式语言、AST 解析求值、编译优化 |

### L4 上下文层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L4-spring-context.md](modules/L4-spring-context.md) | spring-context | ApplicationContext、DI、事件、调度、缓存、校验 |
| [L4-spring-context-support.md](modules/L4-spring-context-support.md) | spring-context-support | 三方集成：Caffeine、JCache、JavaMail、FreeMarker、Quartz |
| [L4-spring-context-indexer.md](modules/L4-spring-context-indexer.md) | spring-context-indexer | 编译期组件索引 |

### L5 事务层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L5-spring-tx.md](modules/L5-spring-tx.md) | spring-tx | 声明式/编程式事务管理、响应式事务、DAO 异常体系 |

### L6 数据与消息层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L6-spring-jdbc.md](modules/L6-spring-jdbc.md) | spring-jdbc | JDBC 模板、DataSource 管理、SQL 异常翻译 |
| [L6-spring-r2dbc.md](modules/L6-spring-r2dbc.md) | spring-r2dbc | 响应式 RDBMS 访问、DatabaseClient |
| [L6-spring-orm.md](modules/L6-spring-orm.md) | spring-orm | JPA / Hibernate 集成、EntityManager 管理 |
| [L6-spring-oxm.md](modules/L6-spring-oxm.md) | spring-oxm | Object/XML 映射（JAXB、XStream） |
| [L6-spring-messaging.md](modules/L6-spring-messaging.md) | spring-messaging | 消息抽象、STOMP 协议、WebSocket 消息处理 |
| [L6-spring-jms.md](modules/L6-spring-jms.md) | spring-jms | JMS 集成、消息驱动 POJO、连接缓存 |

### L7 Web 层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L7-spring-web.md](modules/L7-spring-web.md) | spring-web | HTTP 抽象层、RestClient/RestTemplate、CORS、消息转换 |
| [L7-spring-webmvc.md](modules/L7-spring-webmvc.md) | spring-webmvc | Servlet MVC 框架、DispatcherServlet、@RequestMapping |
| [L7-spring-webflux.md](modules/L7-spring-webflux.md) | spring-webflux | 响应式 Web 框架、DispatcherHandler、WebClient |
| [L7-spring-websocket.md](modules/L7-spring-websocket.md) | spring-websocket | WebSocket 支持、STOMP over WebSocket、SockJS |

### L8 测试层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L8-spring-test.md](modules/L8-spring-test.md) | spring-test | TestContext 框架、MockMvc、WebTestClient、事务测试 |
| [L8-spring-core-test.md](modules/L8-spring-core-test.md) | spring-core-test | RuntimeHints 录制 Agent、TestCompiler 动态编译 |

### L9 辅助层
| 文件 | 模块 | 职责 |
|------|------|------|
| [L9-spring-instrument.md](modules/L9-spring-instrument.md) | spring-instrument | Java Agent（Premain-Class） |
| [L9-spring-aspects.md](modules/L9-spring-aspects.md) | spring-aspects | AspectJ 编译时/加载时织入切面 |

---

## 深度解析文档

| 文档 | 说明 |
|------|------|
| [BeanDefinition 体系](deep-dive/01-beandefinition-system.md) | BeanDefinition 接口层次、XML/注解注册全链路、RootBeanDefinition 合并机制 |
| [配置类解析](deep-dive/02-configuration-class-parsing.md) | ConfigurationClassPostProcessor、@ComponentScan、@Import、@Conditional、@Bean 注册 |
| [容器启动流程](deep-dive/03-startup-process.md) | refresh() 12 步模板方法、BFPP/BPP 注册排序、事件发布与监听器注册 |
| [Bean 生命周期](deep-dive/04-bean-lifecycle.md) | doCreateBean() 15 步完整流程、实例化策略、Aware 回调、初始化方法、扩展点 |
| [循环依赖三级缓存](deep-dive/05-circular-dependency.md) | 三级缓存数据结构、getSingleton() 查找链、AOP 场景 earlyProxyReferences 机制 |
| [依赖注入](deep-dive/06-dependency-injection.md) | @Autowired 解析链路、构造器/字段/方法注入、@Qualifier/@Primary 歧义消解 |
| [FactoryBean 机制](deep-dive/07-factorybean-mechanism.md) | `&` 前缀解引用、getObjectForBeanInstance()、SmartFactoryBean、factoryBeanObjectCache |
| [类型转换体系](deep-dive/08-type-conversion-system.md) | PropertyEditor / Converter / ConversionService / TypeConverter 四层体系 |
| [Environment 环境抽象](deep-dive/09-environment-property-source.md) | PropertySource 链式查找、Profile 逻辑解析、占位符替换 |
| [Resource 资源加载](deep-dive/10-resource-loading.md) | Resource 接口层次、PathMatchingResourcePatternResolver、ASM 类扫描 |
| [事件发布与监听](deep-dive/11-event-system.md) | ApplicationEventMulticaster 广播、@EventListener 注解驱动、泛型事件匹配 |
| [AOP 实现](deep-dive/12-aop-implementation.md) | 代理创建决策、拦截器链执行、@AspectJ 注解处理、JDK vs CGLIB 对比 |
| [事务实现](deep-dive/13-transaction-implementation.md) | @Transactional 注解解析、TransactionInterceptor 拦截、传播行为、ThreadLocal 同步 |
| [Web 环境集成](deep-dive/14-web-environment-integration.md) | ContextLoaderListener 根容器、DispatcherServlet 子容器、父子容器 Bean 可见性 |
| [Spring MVC 请求生命周期](deep-dive/15-springmvc-request-lifecycle.md) | DispatcherServlet.doDispatch() 12 步分发、HandlerMapping 查找、参数解析 |

---

## 实践指南

| 文档 | 说明 |
|------|------|
| [Spring 扩展点实战指南](guides/extension-points-guide.md) | 10 大扩展点详解、执行时序、代码示例、决策表 |

---

## 架构图表

| 文件 | 说明 |
|------|------|
| [architecture.md](architecture.md) | 项目架构全图 + 依赖层级总结 + 模块 api 依赖关系 |
| [spring-architecture-diagram.html](diagrams/spring-architecture-diagram.html) | 可视化架构图（英文） |
| [spring-architecture-diagram-zh.html](diagrams/spring-architecture-diagram-zh.html) | 可视化架构图（中文） |
| [spring-flow-diagram.html](diagrams/spring-flow-diagram.html) | 核心流程可视化 |

---

## 阅读建议

- **新手入门**：`architecture.md` → `modules/L1-spring-core.md` → `modules/L2-spring-beans.md` → `modules/L4-spring-context.md`
- **Bean 容器机制**：`modules/L2-spring-beans.md` → `deep-dive/01-beandefinition-system.md` → `deep-dive/04-bean-lifecycle.md` → `deep-dive/05-circular-dependency.md` → `deep-dive/06-dependency-injection.md`
- **启动与配置**：`modules/L4-spring-context.md` → `deep-dive/03-startup-process.md` → `deep-dive/02-configuration-class-parsing.md`
- **AOP 与事务**：`modules/L3-spring-aop.md` → `deep-dive/12-aop-implementation.md` → `modules/L5-spring-tx.md` → `deep-dive/13-transaction-implementation.md`
- **Web 开发**：`modules/L7-spring-web.md` → `deep-dive/14-web-environment-integration.md` → `modules/L7-spring-webmvc.md` → `deep-dive/15-springmvc-request-lifecycle.md`
- **数据访问**：`modules/L5-spring-tx.md` → `deep-dive/13-transaction-implementation.md` → `modules/L6-spring-jdbc.md` / `modules/L6-spring-orm.md`
- **高级机制**：`deep-dive/07-factorybean-mechanism.md` → `deep-dive/01-beandefinition-system.md`
- **测试**：`modules/L8-spring-test.md` → `modules/L8-spring-core-test.md`
