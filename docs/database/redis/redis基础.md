# Redis 基础

## 1. Redis 概述

Redis（Remote Dictionary Server）是一个开源的、基于内存的键值存储系统，常用作数据库、缓存和消息代理。

### 1.1 核心特性
- **高性能**：基于内存，读写速度极快（10W+ QPS）
- **丰富的数据结构**：String、List、Set、ZSet、Hash、Stream 等
- **持久化**：RDB 快照 + AOF 日志
- **高可用**：主从复制 + Sentinel 哨兵
- **集群**：Redis Cluster 分片

### 1.2 数据结构
- **String**：最简单的 KV 结构
- **List**：双向链表，可用作队列
- **Set**：无序集合，支持交并差运算
- **ZSet**：有序集合，按 score 排序
- **Hash**：存储对象属性
- **Stream**：消息队列数据结构

## 2. 应用场景

- 缓存（热点数据、Session）
- 分布式锁
- 计数器
- 排行榜
- 消息队列
- 位图统计
