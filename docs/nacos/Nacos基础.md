# Nacos 基础

## 1. Nacos 概述

Nacos（Dynamic Naming and Configuration Service）是阿里巴巴开源的动态服务发现、配置管理和服务管理平台。

### 1.1 核心功能
- **服务发现**：服务注册与健康检查（支持 HTTP 和 DNS）
- **配置管理**：动态配置、配置版本管理、配置回滚
- **动态 DNS**：支持基于 DNS 协议的服务发现

### 1.2 核心概念
- **命名空间（Namespace）**：租户级别的隔离
- **分组（Group）**：同一命名空间下的服务分组
- **服务（Service）**：一组功能的抽象
- **实例（Instance）**：服务的具体节点
- **配置（Config）**：应用配置项

## 2. 与 Eureka 对比
| 维度 | Nacos | Eureka |
|------|-------|--------|
| CAP | CP + AP 可切换 | AP |
| 配置管理 | 支持 | 不支持 |
| 健康检查 | TCP/HTTP/MySQL | 心跳 |
| 一致性协议 | Raft / Distro | 无 |
