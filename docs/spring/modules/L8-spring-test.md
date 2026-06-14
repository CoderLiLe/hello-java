# spring-test 模块功能文档

---

## 一、模块定位

spring-test 是 Spring 的 **集成测试支持模块**，416 个 Java 文件，负责：

- **TestContext 框架**：TestContextManager 编排测试生命周期，TestExecutionListener 链式回调
- **JUnit Jupiter 集成**：SpringExtension 将 TestContext 框架接入 JUnit 5
- **MockMvc**：服务器端 Spring MVC 测试（无需启动 Servlet 容器）
- **WebTestClient**：响应式 Web 测试客户端
- **事务测试支持**：@Transactional + 自动回滚，TestTransaction 编程式控制
- **Bean 覆盖**：@MockitoBean / @TestBean 在测试中替换 Spring Bean
- **断言工具**：ReflectionTestUtils、JSON/XML 断言、HttpHeaders 断言
- **JDBC 测试工具**：JdbcTestUtils 数据清理

**依赖**：`spring-core`、`spring-web`、`spring-webmvc`、`spring-webflux`（均为 optional）

---

## 二、模块全景图

```
spring-test (416 files)
│
├── org.springframework.test.context/                  # TestContext 框架核心 (33 files)
│   ├── TestContextManager                              — ★ 测试上下文管理器 (704 lines)
│   ├── TestContext                                     — 测试上下文接口 (216 lines)
│   ├── TestExecutionListener                           — 测试执行监听器 SPI (287 lines)
│   ├── @ContextConfiguration                           — ★ 上下文配置注解 (311 lines)
│   ├── MergedContextConfiguration                     — 合并上下文配置 (621 lines)
│   └── ContextCustomizer / ContextCustomizerFactory    — 上下文自定义 SPI
│
├── org.springframework.test.context.support/          # 框架实现 (32 files)
│   ├── DefaultTestContext                              — 默认测试上下文 (278 lines)
│   ├── AbstractTestContextBootstrapper                 — 引导器基类 (623 lines)
│   ├── DependencyInjectionTestExecutionListener        — ★ DI 监听器 (Order=2000)
│   ├── DirtiesContextTestExecutionListener             — @DirtiesContext 处理
│   └── ContextLoader / SmartContextLoader              — 上下文加载器 SPI
│
├── org.springframework.test.context.transaction/       # 事务测试 (8 files)
│   ├── TransactionalTestExecutionListener              — ★ 事务监听器 (Order=4000)
│   ├── TestTransaction                                 — 编程式事务控制 (149 lines)
│   └── TransactionContext / TransactionContextHolder   — 事务上下文
│
├── org.springframework.test.context.jdbc/             # SQL 脚本执行 (7 files)
│   ├── SqlScriptsTestExecutionListener                — ★ @Sql 执行 (Order=5000)
│   ├── @Sql / @SqlConfig / @SqlGroup                  — 脚本声明注解
│   └── MergedSqlConfig                                 — 合并 SQL 配置
│
├── org.springframework.test.context.junit.jupiter/    # JUnit Jupiter (9 files)
│   ├── SpringExtension                                 — ★ JUnit 5 扩展 (654 lines)
│   ├── @SpringJUnitConfig                             — 组合注解 (108 lines)
│   └── @EnabledIf / @DisabledIf                        — 条件执行
│
├── org.springframework.test.context.bean.override/     # Bean 覆盖 (31 files)
│   ├── mockito/: @MockitoBean, @MockitoSpyBean, @MockitoBeans
│   ├── convention/: @TestBean
│   └── BeanOverrideTestExecutionListener               — Order=1950
│
├── org.springframework.test.context.event/            # 测试事件 (24 files)
│   ├── EventPublishingTestExecutionListener            — Order=10000
│   └── @BeforeTestClass / @AfterTestMethod etc.
│
├── org.springframework.test.web.servlet/              # MockMvc (13 files)
│   ├── MockMvc                                        — ★ MockMvc 入口 (244 lines)
│   ├── MockMvcRequestBuilders                         — 请求构建器工厂
│   ├── MockMvcResultMatchers                          — 结果匹配器工厂
│   ├── MockMvcResultHandlers                          — 结果处理器
│   └── setup/: MockMvcBuilders                        — MockMvc 构建器
│
├── org.springframework.test.web.reactive.server/      # WebTestClient (25 files)
│   ├── WebTestClient                                  — ★ 响应式测试客户端 (1179 lines)
│   ├── DefaultWebTestClient                           — 默认实现 (~550 lines)
│   ├── ExchangeResult                                 — 交换结果
│   └── StatusAssertions / HeaderAssertions / BodyAssertions
│
├── org.springframework.test.json/                     # JSON 断言 (13 files)
│   ├── JsonContentAssert                              — ★ AssertJ JSON 断言 (581 lines)
│   └── JsonComparator / JsonPathExpectationsHelper
│
├── org.springframework.test.util/                     # 测试工具 (11 files)
│   ├── ReflectionTestUtils                            — ★ 反射工具 (548 lines)
│   ├── AopTestUtils                                    — AOP 代理解包
│   ├── JsonPathExpectationsHelper / XpathExpectationsHelper
│   └── TestSocketUtils                                — TCP 端口查找
│
└── org.springframework.test.jdbc/                     # JDBC 工具 (2 files)
    └── JdbcTestUtils                                  — 数据清理工具 (236 lines)
```

---

## 三、核心流程

### 3.1 TestContext 测试生命周期

```
JUnit 发现测试类 @SpringJUnitConfig
  │
  ├── ① SpringExtension.beforeAll():
  │     └── BootstrapUtils.resolveTestContextBootstrapper(testClass)
  │           ├── 解析 @BootstrapWith 或默认 DefaultTestContextBootstrapper
  │           └── buildTestContext():
  │                 ├── buildMergedContextConfiguration() — 合并 @ContextConfiguration / @ActiveProfiles / @TestPropertySource
  │                 └── 创建 DefaultTestContext (含 CacheAwareContextLoaderDelegate)
  │     └── getTestExecutionListeners() — 排序 (SpringFactoriesLoader 默认 12 个)
  │     └── TestContextManager.beforeTestClass()
  │
  ├── ② 实例化测试类 → prepareTestInstance():
  │     └── DependencyInjectionTestExecutionListener (Order=2000):
  │           ├── 加载 ApplicationContext (缓存命中 / 创建新实例)
  │           ├── autowireBeanProperties(testInstance)
  │           └── initializeBean(testInstance)
  │
  ├── ③ @BeforeEach → beforeTestMethod():
  │     └── TransactionalTestExecutionListener:
  │           ├── 检查 @Transactional → 解析 TransactionManager
  │           ├── 执行 @BeforeTransaction 方法
  │           └── 启动事务
  │
  ├── ④ beforeTestExecution() → ★ 测试方法执行 ★ → afterTestExecution()
  │
  ├── ⑤ @AfterEach → afterTestMethod():
  │     └── TransactionalTestExecutionListener:
  │           ├── 事务回滚 (默认 @Rollback(true)) 或提交 (@Rollback(false) / @Commit)
  │           └── 执行 @AfterTransaction 方法
  │
  └── ⑥ afterTestClass():
        └── 标记 ApplicationContext 为 unused (7.0+)
```

**默认 TestExecutionListener 链（按 Order 排序）：**

| Order | Listener | 职责 |
|-------|----------|------|
| 1000 | ServletTestExecutionListener | 设置 Mock 请求/响应 |
| 1500 | DirtiesContextBeforeModes | 测试前 @DirtiesContext |
| 1900 | ApplicationEventsTestExecutionListener | 记录 ApplicationEvents |
| 1950 | BeanOverrideTestExecutionListener | 注入 @MockitoBean |
| **2000** | **DependencyInjectionTestExecutionListener** | **自动装配测试实例** |
| 2500 | MicrometerObservationRegistryTestExecutionListener | Observation 注册 |
| 3000 | DirtiesContextTestExecutionListener | 测试后 @DirtiesContext |
| 3500 | CommonCachesTestExecutionListener | 清理通用缓存 |
| **4000** | **TransactionalTestExecutionListener** | **事务管理** |
| **5000** | **SqlScriptsTestExecutionListener** | **@Sql 脚本执行** |
| 10000 | EventPublishingTestExecutionListener | 发布测试生命周期事件 |
| 10500 | MockitoResetTestExecutionListener | 重置 Mockito mock |

### 3.2 ApplicationContext 缓存

```
DefaultTestContext.getApplicationContext()
  │
  ├── CacheAwareContextLoaderDelegate.loadContext(mergedConfig)
  │     ├── contextCache.get(mergedConfig) — 命中?
  │     │     └── YES: 返回缓存上下文, 记录使用
  │     │
  │     └── NO: loadContextInternal()
  │           ├── SmartContextLoader.loadContext(mergedConfig)
  │           │     ├── 解析 XML/Groovy locations 或 classes
  │           │     ├── 应用 ApplicationContextInitializer
  │           │     └── 创建并刷新 ApplicationContext
  │           └── contextCache.put(mergedConfig, context)
  │
  └── DefaultContextCache:
        ├── MergedContextConfiguration 作为 cache key
        ├── 全局 static 缓存 (JVM 范围内所有测试共享)
        ├── 失效阈值: 连续失败 N 次 → 不再重试
        └── 7.0+ 追踪 context usage (哪些测试类在使用哪个上下文)
```

### 3.3 MockMvc 请求处理

```
mockMvc.perform(get("/api/users").accept(MediaType.APPLICATION_JSON))
       .andExpect(status().isOk())
       .andExpect(jsonPath("$[0].name").value("John"))
  │
  ├── ① MockHttpServletRequestBuilder 构建 MockHttpServletRequest
  │     └── 设置 method, URI, headers, content, params, session
  │
  ├── ② MockFilterChain.doFilter(request, response):
  │     ├── 执行配置的 Filter 链
  │     └── TestDispatcherServlet.service(request, response)
  │           └── 标准 DispatcherServlet 处理:
  │                 ├── HandlerMapping → 查找 Handler
  │                 ├── HandlerAdapter → 调用 Handler
  │                 └── ViewResolver → 渲染视图
  │
  ├── ③ 应用 globalResultMatchers / globalResultHandlers
  │
  └── ④ 返回 ResultActions:
        ├── andExpect(ResultMatcher)  — 自定义断言
        ├── andDo(ResultHandler)      — print(), log()
        └── andReturn()               — 返回 MvcResult
```

### 3.4 WebTestClient 请求处理

```
webTestClient.get().uri("/api/users").exchange()
             .expectStatus().isOk()
             .expectBodyList(User.class).hasSize(3)
  │
  ├── ① DefaultWebTestClient 构建 ClientRequest
  ├── ② ExchangeFunction 链: user filters → observation filter
  │     └── WiretapConnector 拦截请求/响应用于断言
  ├── ③ 连接到 Mock 处理器或实际服务器
  └── ④ ResponseSpec 执行所有断言 (expectStatus/expectHeader/expectBody)
```

### 3.5 事务测试控制

```
@Transactional 测试方法:
  │
  ├── TransactionalTestExecutionListener.beforeTestMethod():
  │     ├── AnnotationTransactionAttributeSource 解析 @Transactional
  │     ├── 解析 PlatformTransactionManager (支持 @Transactional("qualifier"))
  │     └── TransactionContext.startTransaction() → tm.getTransaction()
  │
  ├── 测试方法执行 (所有 DB 操作在事务内)
  │
  └── TransactionalTestExecutionListener.afterTestMethod():
        └── TransactionContext.endTransaction()
              ├── 默认: tm.rollback() — @Rollback(true)
              └── 显式: tm.commit()  — @Rollback(false) 或 @Commit

编程式控制:
  TestTransaction.isActive()
  TestTransaction.flagForRollback()  // 标记回滚
  TestTransaction.flagForCommit()    // 标记提交
  TestTransaction.start() / end()    // 手动控制边界
```

---

## 四、ReflectionTestUtils

```
ReflectionTestUtils.setField(target, "privateField", value)
  │
  ├── AopUtils.getUltimateTargetObject() 解包 AOP 代理
  ├── ReflectionUtils.findField() → 包括父类
  ├── ReflectionUtils.makeAccessible()
  └── field.set(target, value)

同样支持:
  ├── getField(target, name)                  — 获取私有字段
  ├── invokeMethod(target, name, args...)     — 调用私有方法
  ├── invokeSetterMethod(target, name, value) — 调用 setter
  └── invokeGetterMethod(target, name)        — 调用 getter
```

---

## 五、依赖关系

```
spring-test
  ├── api: spring-core
  ├── optional: spring-beans / spring-context / spring-web / spring-webmvc / spring-webflux
  ├── optional: spring-jdbc
  ├── optional: org.junit.jupiter:junit-jupiter-api
  ├── optional: org.junit.vintage:junit-vintage-engine (JUnit 4)
  ├── optional: org.testng:testng
  ├── optional: jakarta.servlet:jakarta.servlet-api
  ├── optional: org.assertj:assertj-core
  ├── optional: org.mockito:mockito-core
  ├── optional: io.micrometer:micrometer-observation
  └── optional: org.htmlunit:htmlunit

---

## 六、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | spring-core ~ spring-webflux | L1~L7 | 所有上层模块（均为 optional） |
| 同级 | [spring-core-test](L8-spring-core-test.md) | L8 测试 | AOT RuntimeHints 测试 |
```
