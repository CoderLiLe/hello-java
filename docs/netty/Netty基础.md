# Netty 基础

## 1. Netty 概述

Netty 是一个基于 Java NIO 的异步事件驱动的网络应用框架，用于快速开发高性能、高可靠性的网络 IO 程序。

### 1.1 核心特性
- **统一的异步 IO API**：屏蔽 NIO/AIO 底层复杂性
- **Reactor 线程模型**：主从 Reactor 多线程模型
- **零拷贝**：减少内存复制
- **内存池**：ByteBuf 对象池复用
- **编解码框架**：丰富的协议编解码支持

### 1.2 核心组件
- **Channel**：网络连接的抽象
- **ChannelPipeline**：处理器链
- **ChannelHandler**：入站/出站事件处理
- **EventLoop**：处理 IO 事件的事件循环
- **ByteBuf**：字节容器

## 2. 应用场景

- RPC 框架（Dubbo、gRPC）
- 消息中间件
- 网关
- 即时通讯（IM）
