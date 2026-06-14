# spring-context-support 模块功能文档

---

## 一、模块定位

spring-context-support 是 Spring 的**第三方集成支持模块**，87 个 Java 文件，负责：

- **缓存集成**：Caffeine 缓存、JCache（JSR-107）、事务感知缓存装饰器
- **邮件发送**：JavaMail 集成（MimeMessageHelper、MailSender）
- **模板引擎**：FreeMarker 集成（FreeMarkerConfigurer）
- **任务调度**：Quartz Scheduler 集成（QuartzJobBean、SchedulerFactoryBean）
- **UI 上下文**：FreeMarker UI 宏支持

**依赖**：`spring-beans`、`spring-core`、`spring-context`、`spring-tx`

---

## 二、模块全景图

```
spring-context-support (87 files)
│
├── org.springframework.cache.caffeine/              # Caffeine 缓存 (4 files)
│   ├── CaffeineCacheManager                          — Caffeine 缓存管理器
│   └── CaffeineCache                                 — Caffeine 缓存实现
│
├── org.springframework.cache.jcache/                 # JCache (JSR-107) (16 files)
│   ├── JCacheCache / JCacheCacheManager              — JCache 缓存实现
│   ├── config/: JCacheConfigurer / JCacheConfig      — XML 配置支持
│   └── interceptor/: JCacheInterceptor / JCacheOperation — 注解拦截
│
├── org.springframework.cache.transaction/            # 事务感知缓存 (2 files)
│   ├── TransactionAwareCacheDecorator                — 事务感知缓存装饰器
│   └── TransactionAwareCacheManagerProxy             — 事务感知缓存管理器代理
│
├── org.springframework.mail/                         # 邮件核心 (8 files)
│   ├── MailSender                                    — 邮件发送器接口
│   ├── MailMessage                                   — 邮件消息接口
│   ├── SimpleMailMessage                             — 简单邮件消息 (纯文本)
│   ├── MailException / MailSendException             — 邮件异常体系
│   └── MailPreparationException / MailParseException
│
├── org.springframework.mail.javamail/                # JavaMail 集成 (15 files)
│   ├── JavaMailSender / JavaMailSenderImpl           — ★ JavaMail 发送器
│   ├── MimeMailMessage                               — MIME 邮件消息
│   ├── MimeMessagePreparator                         — MimeMessage 准备回调
│   ├── MimeMessageHelper                             — ★ MIME 消息辅助类 (内嵌图片/附件)
│   ├── InternetAddressEditor                         — 地址编辑器
│   ├── ConfigurableMimeFileTypeMap                  — 可配置 MIME 文件类型映射
│   └── SmartMimeMessage                               — 智能 MimeMessage
│
├── org.springframework.scheduling.quartz/            # Quartz 调度 (15 files)
│   ├── SchedulerFactoryBean                          — ★ Quartz Scheduler 工厂 Bean
│   ├── QuartzJobBean                                  — Quartz Job 基类 (依赖注入支持)
│   ├── MethodInvokingJobDetailFactoryBean             — 方法调用 Job 工厂
│   ├── CronTriggerFactoryBean                         — Cron 触发器工厂
│   ├── SimpleTriggerFactoryBean                       — 简单触发器工厂
│   ├── JobDetailFactoryBean                           — JobDetail 工厂
│   ├── SchedulerAccessor                              — Scheduler 访问器基类
│   ├── SpringBeanJobFactory                           — Job 工厂 (从 ApplicationContext 获取)
│   ├── AdaptableJobFactory                            — 可适配 Job 工厂
│   ├── DelegatingJob                                  — 委托 Job
│   └── ResourceLoaderClassLoadHelper                  — 资源加载类加载辅助
│
└── org.springframework.ui.freemarker/                # FreeMarker 集成 (8 files)
    ├── FreeMarkerConfigurer                           — ★ FreeMarker 配置器
    ├── FreeMarkerConfigurationFactoryBean             — FreeMarker 配置工厂
    ├── FreeMarkerTemplateUtils                        — 模板工具类
    └── SpringTemplateLoader                           — Spring 资源模板加载器
```

---

## 三、核心流程

### 3.1 JavaMail 邮件发送

```
JavaMailSenderImpl sender = new JavaMailSenderImpl();
sender.setHost("smtp.example.com");
sender.setPort(587);

// 简单邮件
SimpleMailMessage msg = new SimpleMailMessage();
msg.setTo("user@example.com");
msg.setSubject("Hello");
msg.setText("Message body");
sender.send(msg);

// MIME 邮件 (HTML, 附件, 内嵌图片)
MimeMessage mimeMsg = sender.createMimeMessage();
MimeMessageHelper helper = new MimeMessageHelper(mimeMsg, true, "UTF-8");
helper.setTo("user@example.com");
helper.setSubject("Hello");
helper.setText("<html><body><h1>Hello</h1></body></html>", true);  // HTML
helper.addAttachment("file.pdf", new File("report.pdf"));          // 附件
helper.addInline("logo", new FileSystemResource("logo.png"));      // 内嵌图片

内部流程:
  sender.send(MimeMessage)
    │
    ├── 获取 Session: Session.getInstance(properties)
    ├── 创建 Transport: session.getTransport(protocol)
    ├── 连接 SMTP 服务器: transport.connect(host, port, username, password)
    ├── 发送: transport.sendMessage(msg, recipients)
    │     └── MimeMessagePreparator.prepare(mimeMsg)  ← 回调设置
    └── 关闭 Transport
```

### 3.2 Quartz 调度集成

```
SchedulerFactoryBean schedulerFactory = new SchedulerFactoryBean();
schedulerFactory.setTriggers(cronTrigger, simpleTrigger);
schedulerFactory.afterPropertiesSet();  // 初始化 Scheduler
schedulerFactory.start();               // 启动调度

// Job 定义 (支持 Spring DI)
public class MyJob extends QuartzJobBean {
    @Autowired
    private MyService service;

    @Override
    protected void executeInternal(JobExecutionContext ctx) {
        service.doSomething();
    }
}

SchedulerFactoryBean 生命周期:
  │
  ├── afterPropertiesSet():
  │     ├── 创建 SchedulerFactory
  │     ├── 设置 SpringBeanJobFactory (使 Job 支持 @Autowired)
  │     ├── 注册 JobDetails 和 Triggers
  │     ├── 注册 SchedulerListeners
  │     └── 启动 Scheduler: scheduler.start()
  │
  └── destroy():
        └── scheduler.shutdown(waitForJobsToComplete)
```

### 3.3 FreeMarker 集成

```
FreeMarkerConfigurer configurer = new FreeMarkerConfigurer();
configurer.setTemplateLoaderPath("classpath:/templates/");
configurer.afterPropertiesSet();

// 获取模板
Configuration cfg = configurer.getConfiguration();
Template template = cfg.getTemplate("email.ftl");

// 渲染
String html = FreeMarkerTemplateUtils.processTemplateIntoString(
    template, Map.of("user", user));

FreeMarkerConfigurer 内部:
  │
  ├── 创建 Configuration (FreeMarker)
  ├── 设置 TemplateLoader → SpringTemplateLoader (支持 classpath: 等 Spring Resource)
  ├── 加载 settings (通过 Properties)
  ├── 注册共享变量 (freemarkerVariables)
  └── 注册宏库 (autoImport / autoInclude)
```

### 3.4 事务感知缓存

```
TransactionAwareCacheDecorator
  │
  ├── put(key, value): 不直接写入缓存
  │     └── 注册 TransactionSynchronization.afterCommit()
  │           └── 事务提交后 → targetCache.put(key, value)
  │
  ├── evict(key): 不直接删除
  │     └── 注册 TransactionSynchronization.afterCommit()
  │           └── 事务提交后 → targetCache.evict(key)
  │
  └── get(key): 直接读取 (读操作无需延迟)
```

---

## 四、依赖关系

```
spring-context-support
  ├── api: spring-beans
  ├── api: spring-core
  ├── api: spring-context
  ├── api: spring-tx
  ├── optional: com.github.ben-manes.caffeine:caffeine       (Caffeine 缓存)
  ├── optional: javax.cache:cache-api                         (JCache)
  ├── optional: com.sun.mail:jakarta.mail                     (JavaMail)
  ├── optional: org.freemarker:freemarker                     (FreeMarker)
  ├── optional: org.quartz-scheduler:quartz                   (Quartz)
  └── optional: org.jetbrains.kotlin:kotlin-stdlib

---

## 五、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-context](L4-spring-context.md) | L4 上下文 | ApplicationContext |
| 上游 | [spring-tx](L5-spring-tx.md) | L5 事务 | 事务感知缓存 |
| 下游 | [spring-aspects](L9-spring-aspects.md) | L9 辅助 | JCache AspectJ 切面 |
```
