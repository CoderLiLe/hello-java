# SpringBoot基础
## 1. SpringBoot简介
SpringBoot是一个快速开发框架，它提供了一系列的starter，通过starter可以快速引入各种依赖，简化开发。

## 2. SpringBoot自动配置原理
> Springboot中最高频的一道面试题，也是框架最核心的思想

- <font color="red">@SpringBootConfiguration</font>：该注解与 @Configuration 注解作用相同，用来声明当前也是一个配置类。
- <font color="red">@ComponentScan</font>：组件扫描，默认扫描当前引导类所在包及其子包。
- <font color="red">@EnableAutoConfiguration</font>：SpringBoot实现自动化配置的核心注解。

![](asserts/springboot高级/2.1.png)

![](asserts/springboot高级/2.2.png)

![](asserts/springboot高级/2.3.png)

> 1,  在Spring Boot项目中的引导类上有一个注解@SpringBootApplication，这个注解是对三个注解进行了封装，分别是：
> - @SpringBootConfiguration
> - @EnableAutoConfiguration
> - @ComponentScan
> 
> 2,  其中@EnableAutoConfiguration是实现自动化配置的核心注解。 该注解通过@Import注解导入对应的配置选择器。
内部就是读取了该项目和该项目引用的Jar包的的classpath路径下META-INF/spring.factories文件中的所配置的类的全类名。 在这些配置类中所定义的Bean会根据条件注解所指定的条件来决定是否需要将其导入到Spring容器中。
> 
> 3, 条件判断会有像@ConditionalOnClass这样的注解，判断是否有对应的class文件，如果有则加载该类，把这个配置类的所有的Bean放入spring容器中使用。

## 3. SpringBoot的启动流程是怎么样的？
### 3.1 SpringBoot启动的流程总览
每一个SpringBoot程序都有一个主入口，这个主入口就是main方法，而main方法中都会调用 SpringBootApplication.run 方法，查看该方法的源码可以发现启动流程主要分为两个阶段：
- 初始化SpringApplication
- 运行SpringApplication的过程
  - SpringApplicationRunListeners 引用启动监控模块
  - ConfigrableEnvironment配置环境模块和监听：包括创建配置环境、加载属性配置文件和配置监听
  - ConfigrableApplicationContext配置应用上下文：包括配置应用上下文对象、配置基本属性和刷新应用上下文

### 3.2 初始化SpringApplication
SpringApplication的初始化，**配置基本的环境变量、资源、构造器、监听器**，初始化阶段的主要作用是为运行SpringApplication实例对象启动环境变量准备以及进行必要的资源构造器的初始化动作
主要代码如下：
```java
public SpringApplication(ResourceLoader resourceLoader, Object... sources){
    this.resourceLoader = resourceLoader;
    initialize(source);
}

@SupressWarnings({"unchecked","rowtypes"})
private void initialize(Object[] sources){
    if(sources != null && sources.length > 0){
        this.sources.addAll(Arrays.asList(sources));
    }
    this.WebEnvironment = deduceWebEnvironment;
    setInitiallizers((Collection) getSpringFactoriesInstances(ApplicationContextInitiallizer.class));
    setListeners((Collection) getSpringFactoriesInstances(ApplicationListener.class));
    this.mainApplicationClass = deduceMainApplicationClass();
}
```

### 3.3 运行SpringApplication
SpringBoot正式启动加载过程，包括**启动流程监控模块、配置环境加载模块、ApplicationContext容器上下文环境加载模块**。refreshContext方法刷新应用上下文并进行自动化配置模块加载，也就是上文提到的SpringFactoriesLoader根据指定classpath加载META-INF/spring.factories文件的配置，实现自动配置核心功能。

运行SpringApplication的主要代码如下:
```java
public ConfigurableApplicationContext run(String... args) {
    ConfigurableApplicationContext context = null;
    FailureAnalyzer analyzer = null;
    configureHeadlessProperty();
    // 步骤1
    SpringApplicationRunListeners listeners = getRunListeners(args);
        listeners.starting();
    try {
        // 步骤2
        ApplicationArguments applicationArguments = new DefaultApplicationArguments(args);
        ConfigurableEnvironment environment = prepareEnvironment(listeners, applicationArguments);
        Banner printBanner = printBanner(environment);
        // 步骤3
        context = createApplicationContext();
        prepareContext(context, environment, listeners, applicationArguments, printBanner);
        refreshContext(context);
        afterRefresh(context, applicationArguments);
        listeners.finished(context, null);
        // 省略
        return context;
    }
}
```
>（1）SpringApplciationRunListener应用启动监控模块
> 
>（2）ConfigurableEnviroment 配置环境模块和监听
> 
>（3）ConfigurableApplicationContext配置应用上下文


## 4. SpringBoot如何做优雅停机？

> 优雅停机（Graceful Shutdown） 是指在服务器需要关闭或重启时，能够先处理完当前正在进行的请求，然后再停止服务的操作。优雅停机的实现步骤主要分为以下几步：
> - 停止接收新的请求：首先，系统会停止接受新的请求，这样就不会有新的任务被添加到任务队列中。
> - 处理当前请求：系统会继续处理当前已经在处理中的请求，确保这些请求能够正常完成。这通常涉及到等待正在执行的任务完成，如处理HTTP请求、数据库操作等。
> - 释放资源：在请求处理完成后，系统会释放所有已分配的资源，如关闭数据库连接、断开网络连接等。
> - 关闭服务：最后，当所有请求都处理完毕且资源都已释放后，系统会安全地关闭服务。

优雅停机的实现步骤分为以下两步：
- 使用合理的 kill 命令，给 Spring Boot 项目发送优雅停机指令。
- 开启 Spring Boot 优雅停机/自定义 Spring Boot 优雅停机的实现。

### 4.1 合理杀死进程

在 Linux 中 kill 杀死进程的常用命令有以下这些：
- **kill -2 pid**：向指定 pid 发送 SIGINT 中断信号，等同于 ctrl+c。也就说，不仅当前进程会收到该信号，而且它的子进程也会收到终止的命令。
- **kill -9 pid**：向指定 pid 发送 SIGKILL 立即终止信号。程序不能捕获该信号，最粗暴最快速结束程序的方法。
- **kill -15 pid**：向指定 pid 发送 SIGTERM 终止信号。信号会被当前进程接收到，但它的子进程不会收到，如果当前进程被 kill 掉，它的的子进程的父进程将变成 init 进程 (init 进程是那个 pid 为 1 的进程)。
- **kill pid**：等同于 kill 15 pid。

因此，在以上命令中，我们**不能使用“kill -9”来杀死进程，使用“kill”杀死进程即可**。

### 4.2 设置SpringBoot优雅停机
在 Spring Boot 2.3.0 之后，可以通过配置设置开启 Spring Boot 的优雅停机功能，如下所示：
```text
# 开启优雅停机，默认值：immediate 为立即关闭
server.shutdown=graceful

# 设置缓冲期，最大等待时间，默认：30秒
spring.lifecycle.timeout-per-shutdown-phase=60s
```
此时，应用在关闭时，Web 服务器将不再接受新请求，并等待正在进行的请求完成的缓冲时间。

然而，如果是 Spring Boot 2.3.0 之前，就需要自行扩展（线程池）来实现优雅停机了。它的核心实现实现是在系统关闭时会调用 ShutdownHook，然后在 ShutdownHook 中阻塞 Web 容器的线程池，直到所有请求都处理完毕再关闭程序，这样就实现自定义优雅线下了。

但是，不同的 Web 容器（Tomcat、Jetty、Undertow）有不同的自定义优雅停机的方法，以 Tomcat 为例，它的自定义优雅停机实现如下。

#### Tomcat 容器关闭代码
```java
public class TomcatGracefulShutdown implements TomcatConnectorCustomizer, ApplicationListener<ContextClosedEvent> {
    private volatile Connector connector;

    public void customize(Connector connector) {
        this.connector = connector;
    }

    public void onApplicationEvent(ContextClosedEvent contextClosedEvent) {
        this.connector.pause();
        Executor executor = this.connector.getProtocolHandler().getExecutor();
        if (executor instanceof ThreadPoolExecutor) {
            try {
                log.info("Start to shutdown tomcat thread pool");
                ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) executor;
                threadPoolExecutor.shutdown();
                if (!threadPoolExecutor.awaitTermination(20, TimeUnit.SECONDS)) {
                    log.warn("Tomcat thread pool did not shutdown gracefully within 20 seconds. ");
                }
            } catch (InterruptedException e) {
                log.warn("Fail to shut down tomcat thread pool ", e);
            }
        }
    }
}
```
#### 设置 Tomcat 自动装配
```java
@Configuration
@ConditionalOnClass({Servlet.class, Tomcat.class})
public static class TomcatConfiguration {
    @Bean
    public TomcatGracefulShutdown tomcatGracefulShutdown() {
        return new TomcatGracefulShutdown();
    }

    @Bean
    public EmbeddedServletContainerFactory tomcatEmbeddedServletContainerFactory(TomcatGracefulShutdown gracefulShutdown) {
        TomcatEmbeddedServletContainerFactory tomcatFactory = new TomcatEmbeddedServletContainerFactory();
        tomcatFactory.addConnectorCustomizers(gracefulShutdown);
        return tomcatFactory;
    }
}
```