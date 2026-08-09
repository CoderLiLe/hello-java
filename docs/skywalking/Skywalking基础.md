# SkyWalking 基础

## 1. SkyWalking 概述

Apache SkyWalking 是一个开源的 APM（Application Performance Management）系统，提供分布式链路追踪、服务网格遥测分析、度量聚合和可视化。

### 1.1 核心特性
- **分布式追踪**：跨服务调用链路追踪
- **服务拓扑**：自动生成服务依赖拓扑图
- **性能指标**：调用延迟、吞吐量、成功率
- **告警**：自定义告警规则
- **多语言支持**：Java、.NET、Node.js、Go 等

### 1.2 核心概念
- **Service**：提供相同功能的一组实例
- **Service Instance**：服务实例（通常一个进程）
- **Endpoint**：服务中的具体接口/方法
- **Trace**：一次完整调用链
- **Span**：调用链中的一个片段

## 2. 与 Pinpoint 对比
| 维度 | SkyWalking | Pinpoint |
|------|-----------|----------|
| 探针方式 | Agent | Agent |
| 存储 | ES、H2、MySQL | HBase |
| 社区活跃度 | 高 | 中 |
| 协议 | gRPC | Thrift |
