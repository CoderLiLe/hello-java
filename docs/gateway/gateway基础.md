# Spring Cloud Gateway 基础

## 1. Gateway 概述

Spring Cloud Gateway 是基于 Spring WebFlux 的 API 网关，提供路由、过滤、限流等网关功能。

### 1.1 核心特性
- **基于 WebFlux**：非阻塞、响应式编程模型
- **动态路由**：支持从注册中心动态获取路由
- **断言（Predicate）**：基于请求路径、Header、参数等条件匹配路由
- **过滤器（Filter）**：请求预处理、响应后处理
- **集成 Sentinel / Hystrix**：限流和熔断

### 1.2 核心概念
- **Route（路由）**：网关的基本构建块，包含 ID、目标 URI、断言集合和过滤器集合
- **Predicate（断言）**：匹配 HTTP 请求的条件
- **Filter（过滤器）**：对请求和响应进行修改

## 2. 与 Zuul 对比
| 维度 | Gateway | Zuul 1.x |
|------|---------|----------|
| IO 模型 | 非阻塞 | 阻塞 Servlet |
| 线程模型 | 少量线程 | 每连接一线程 |
| 性能 | 高 | 一般 |
