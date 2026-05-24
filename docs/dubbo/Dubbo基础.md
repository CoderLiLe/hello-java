# Dubbo 基础

## 1. Dubbo 概述

Apache Dubbo 是一款高性能、轻量级的 Java RPC 框架，提供服务自动注册与发现、负载均衡、容错、服务治理等能力。

### 1.1 核心能力
- **远程通信**：向远程服务发送请求
- **集群容错**：负载均衡、重试、熔断
- **服务治理**：服务注册/发现、路由、配置

### 1.2 架构
```
Consumer -> Proxy -> Client -> Registry ...
                                |
Provider <- Server <- Exporter <- Registry
```

节点角色：
- **Provider**：服务提供者
- **Consumer**：服务消费者
- **Registry**：注册中心（ZooKeeper / Nacos）
- **Monitor**：监控中心
- **Container**：容器

## 2. 快速开始

### 2.1 接口定义
```java
public interface HelloService {
    String sayHello(String name);
}
```

### 2.2 服务提供者
```java
// 实现
@DubboService
public class HelloServiceImpl implements HelloService {
    @Override
    public String sayHello(String name) {
        return "Hello, " + name;
    }
}

// 配置 application.yml
dubbo:
  application:
    name: hello-provider
  registry:
    address: zookeeper://localhost:2181
  protocol:
    name: dubbo
    port: 20880
```

### 2.3 服务消费者
```java
@DubboReference
private HelloService helloService;

// 配置
dubbo:
  application:
    name: hello-consumer
  registry:
    address: zookeeper://localhost:2181
```

## 3. 协议

| 协议 | 优点 | 适用场景 |
|------|------|---------|
| dubbo | 长连接、高效 | 小数据量大并发 |
| http | 通用、穿透防火墙 | 异构系统 |
| thrift | 跨语言 | 性能要求高 |
| grpc | 多语言、HTTP/2 | 流式通信 |
| rest | RESTful 风格 | 开放 API |
| webservice | SOAP 标准 | 企业集成 |

## 4. 集群容错

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| Failover | 失败重试（默认） | 读操作 |
| Failfast | 快速失败 | 写操作 |
| Failsafe | 失败忽略 | 日志等不重要操作 |
| Failback | 失败后定时重试 | 消息通知 |
| Forking | 并行调用多个 | 实时性要求高 |
| Broadcast | 广播调用 | 更新缓存 |

## 5. 负载均衡

| 策略 | 说明 |
|------|------|
| Random | 随机（默认） |
| RoundRobin | 轮询 |
| LeastActive | 最少活跃数 |
| ConsistentHash | 一致性哈希 |
| ShortestResponse | 最短响应时间 |

## 6. 服务治理

### 6.1 路由
- **条件路由**：基于参数/IP 路由
- **标签路由**：基于标签分组

### 6.2 动态配置
- 权重调整
- 负载均衡策略
- 超时时间
- 重试次数

### 6.3 服务降级
```java
@DubboReference(mock = "force:return null")
private HelloService helloService;

// Mock 实现
public class HelloServiceMock implements HelloService {
    public String sayHello(String name) {
        return "服务降级";
    }
}
```

## 7. 扩展机制 SPI

Dubbo 的 SPI 机制是核心扩展点：
- **协议**：Protocol
- **拦截器**：Filter
- **路由**：Router
- **负载均衡**：LoadBalance
- **序列化**：Serialization

```java
@SPI("dubbo")
public interface Protocol {
    <T> Exporter<T> export(Invoker<T> invoker);
    <T> Invoker<T> refer(Class<T> type, URL url);
}

@Adaptive
public class AdaptiveProtocol implements Protocol {
    // 根据 URL 参数选择实现
}
```

## 8. 与 Spring Cloud 对比

| 特性 | Dubbo | Spring Cloud |
|------|-------|-------------|
| 通信协议 | Dubbo 协议（TCP） | HTTP REST |
| 性能 | 高 | 中 |
| 注册中心 | ZK/Nacos | Nacos/Eureka |
| 服务治理 | 完善 | 较完善 |
| 学习成本 | 中 | 低 |
| 语言支持 | Java 为主 | 多语言 |
