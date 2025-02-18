## 1. Spring 和Spring Boot 有什么区别？
Spring 和 Spring Boot 都是 Java 开发中非常流行的框架，它们都可以用于构建企业级应用程序。虽然它们都是 Spring 框架的一部分，但是它们之间还是有一些区别的。

### 1.1 Spring
Spring 是一个轻量级的开源框架，它提供了一种简单的方式来构建企业级应用程序。Spring 框架的核心是 IoC（Inversion of Control）和 AOP（Aspect Oriented Programming）两个概念。

IoC 是一种设计模式，它将对象的创建和依赖关系的管理从应用程序代码中分离出来，使得应用程序更加灵活和可维护。

AOP 是一种编程范式，它允许开发人员在不修改原有代码的情况下，向应用程序中添加新的功能。

Spring 框架提供了很多模块，包括核心容器、数据访问、Web、AOP、消息、测试等。开发人员可以根据自己的需求选择合适的模块来构建应用程序。#

### 1.2 Spring Boot
Spring Boot 本质上是 Spring 框架的延伸和扩展，它的诞生是为了简化 Spring 框架初始搭建以及开发的过程，使用它可以不再依赖 Spring 应用程序中的 XML 配置，为更快、更高效的开发 Spring 提供更加有力的支持。 

Spring Boot 也提供了很多特性，包括自动配置、嵌入式 Web 服务器、健康检查、度量指标、安全性等。开发人员可以通过使用 Spring Boot Starter 来快速集成常用的第三方库和框架，比如 Spring Data、Spring Security、MyBatis、Redis 等。

### 1.3 小结
Spring 和 Spring Boot 的区别在于它们的目标和用途不同。

Spring 是一个轻量级的开源框架，它提供了一种简单的方式来构建企业级应用程序。

Spring Boot 则是 Spring 框架的延伸和扩展，它提供了一种快速构建应用程序的方式。开发人员可以通过使用 Spring Boot Starter 来快速集成常用的第三方库和框架，使得开发人员可以快速构建出一个可运行的应用程序。

## 2. Spring Boot有什么优点？
### 2.1 简化配置
Spring Boot 采用约定大于配置的原则，提供了自动配置的特性，大部分情况下无需手动配置，可以快速启动和运行应用程序。

同时，Spring Boot 提供了统一的配置模型，集成了大量常用的第三方库和框架，简化了配置过程。

### 2.2 内嵌服务器
集成了常用的内嵌式服务器，如 Tomcat、Jetty 和 Undertow 等。不再需要单独安装和配置外部服务器，可以直接运行 Spring Boot 应用程序，简化了部署和发布过程。

### 2.3 自动装配
Spring Boot 提供了自动装配机制，根据应用程序的依赖关系和配置信息，智能地自动配置 Spring 的各种组件和功能，大大减少了开发人员的手动配置工作，提高了开发效率

### 2.4 起步依赖
引入了起步依赖（Starter Dependencies）的概念，它是一种可用于快速集成相关技术栈的依赖项集合。起步依赖能够自动处理依赖冲突和版本兼容性，并提供了默认的配置和依赖管理，简化了构建和管理项目的过程

### 2.5 自动化监控和管理
集成了 Actuator 模块，提供了对应用程序的自动化监控、管理和运维支持。

通过 Actuator，可以获取应用程序的健康状况、性能指标、配置信息等，方便运维人员进行故障排查和性能优化。

### 2.6 丰富的生态系统
Spring Boot 建立在 Spring Framework 的基础上，可以无缝集成 Spring 的各种功能和扩展，如 Spring Data、Spring Security、Spring Integration 等。

同时，Spring Boot 还提供了大量的第三方库和插件，可以方便地集成其他技术栈，构建全栈式应用程序。

### 2.7 可扩展性和灵活性
尽管 Spring Boot 提供了很多自动化的功能和约定，但它也保持了良好的可扩展性和灵活性。开发人员可以根据自己的需求进行自定义配置和扩展，以满足特定的业务需求。

> Spring Boot 是一个强大而又灵活的开发框架，具有简化配置、快速开发、自动化监控、微服务支持等诸多优点。
> 
> 它极大地提高了开发效率、降低了开发成本，并且在行业中得到了广泛的认可和应用。

## 3. Spring Boot 的常用注解有哪些？
|注解|说明|
|-|--|
|@SpringBootConfiguration|组合了- @Configuration注解，实现配置文件的功能|
|@EnableAutoConfiguration|打开自动配置的功能，也可以关闭某个自动配置的选项|
|@ComponentScan|Spring组件扫描|
|@RequestMapping|用于映射请求路径，可以定义在类上和方法上。用于类上，则表示类中的所有的方法都是以该地址作为父路径|
|@RequestBody|注解实现接收 http 请求的 json 数据，将 json 转换为 java 对象|
|@RequestParam|指定请求参数的名称|
|@PathVariable|从请求路径下中获取请求参数 (/user/{id})，传递给方法的形式参数|
|@ResponseBody|注解实现将 controller 方法返回对象转化为 json 对象响应给客户端|
|@RequestHeader|获取指定的请求头数据|
|@RestController|@Controller + @ResponseBody|


