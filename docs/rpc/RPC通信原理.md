# RPC 通信原理

## 1. RPC 概述

### 1.1 什么是 RPC
RPC（Remote Procedure Call，远程过程调用）允许程序调用另一个地址空间（通常是另一台机器）的函数或方法，就像调用本地函数一样。

### 1.2 核心目标
- 调用方式透明
- 跨网络通信
- 高性能
- 跨语言（可选）

## 2. 通信流程

```
Client                     Server
  |                          |
  |-- 1. 调用代理 --------->|  
  |    Client Stub           |
  |-- 2. 序列化参数 ------->|
  |-- 3. 网络传输 --------->|
  |    (Socket/Netty)        |
  |                          |-- 4. 反序列化
  |                          |-- 5. 调用目标方法
  |                          |-- 6. 序列化结果
  |                          |
  |<-- 7. 网络传输 ---------|
  |-- 8. 反序列化结果 ----->|
  |-- 9. 返回结果 ---------->|
```

## 3. 核心技术

### 3.1 动态代理
```java
// JDK 动态代理生成 Stub
public class RpcProxy implements InvocationHandler {
    private Class<?> interfaceClass;
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) {
        // 1. 获取方法信息
        String methodName = method.getName();
        Class<?>[] paramTypes = method.getParameterTypes();
        
        // 2. 序列化参数
        byte[] data = serialize(args);
        
        // 3. 发送网络请求
        byte[] result = sendRequest(methodName, paramTypes, data);
        
        // 4. 反序列化结果
        return deserialize(result);
    }
}
```

### 3.2 序列化

| 序列化 | 优点 | 缺点 | 场景 |
|--------|------|------|------|
| JDK | 原生支持 | 性能差，体积大 | 不推荐 |
| JSON | 可读性强 | 体积大，性能一般 | 简单场景 |
| Hessian | 跨语言 | Java 专属 | Dubbo 默认（v2） |
| Protobuf | 高性能，小体积 | 需要 .proto | 跨语言 |
| Kryo | 高性能 | Java 专属 | 高性能场景 |
| Avro | 动态模式 | 略复杂 | Hadoop |

### 3.3 网络通信

| 框架 | 模型 | 适用场景 |
|------|------|---------|
| BIO | 一连接一线程 | 连接数少 |
| NIO | 多路复用 | 高并发 |
| Netty | Reactor 模型 | 高性能 RPC |
| AIO | 异步 I/O | 大文件 |

### 3.4 连接管理
- **长连接**：连接复用，减少握手开销
- **连接池**：多路复用
- **心跳检测**：健康检查
- **重连机制**：断线自动重连

## 4. 注册中心

### 4.1 服务注册
```java
// 服务启动时注册
public void register(URL url) {
    // 1. 创建临时节点
    // 2. 写入服务地址
    // 3. 注册监听器
}

// 客户端订阅
public void subscribe(String service) {
    // 1. 获取服务列表
    // 2. 监听变化
    // 3. 更新本地缓存
}
```

### 4.2 健康检查
- 临时节点（ZooKeeper session 过期自动删除）
- 心跳上报
- 主动探测

## 5. 负载均衡

### 5.1 常见策略
```java
// 随机
Invoker selectByRandom(List<Invoker> invokers) {
    return invokers.get(ThreadLocalRandom.current().nextInt(invokers.size()));
}

// 加权轮询
Invoker selectByWeight(List<Invoker> invokers) {
    // 根据权重分配请求
}

// 最少连接
Invoker selectByLeastConnections(List<Invoker> invokers) {
    // 选择活跃连接数最少的节点
}
```

## 6. 容错机制

### 6.1 重试
```java
public Result invokeWithRetry(Invocation inv, int retries) {
    Throwable lastException = null;
    for (int i = 0; i <= retries; i++) {
        try {
            return doInvoke(inv);
        } catch (Throwable t) {
            lastException = t;
            // 等幂性检查是否可重试
        }
    }
    throw new RpcException(lastException);
}
```

### 6.2 超时控制
- 连接超时
- 读取超时
- 业务超时

### 6.3 熔断
- 错误率阈值
- 半开探测
- 滑动窗口统计

## 7. RPC vs REST

| 特性 | RPC | REST |
|------|-----|------|
| 协议 | 私有协议 | HTTP |
| 性能 | 高 | 一般 |
| 耦合 | 强（接口契约） | 弱（资源） |
| 调试 | 需工具 | 浏览器可测 |
| 跨语言 | 需 IDL | 天然支持 |
| 浏览器 | 不直接支持 | 直接支持 |
| 适用 | 内部微服务 | 开放 API |

## 8. 手写 RPC 框架核心思路

```java
// 1. 定义注解
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface RpcService {
    Class<?> interfaceClass();
}

// 2. 服务发布
public class RpcServer {
    public void publish(Object service, int port) {
        // 生成代理
        // 注册到注册中心
        // 启动 Netty
    }
}

// 3. 客户端代理
public class RpcClient {
    public <T> T refer(Class<T> interfaceClass, URL url) {
        return (T) Proxy.newProxyInstance(
            interfaceClass.getClassLoader(),
            new Class[]{interfaceClass},
            new RpcInvocationHandler(url)
        );
    }
}
```
