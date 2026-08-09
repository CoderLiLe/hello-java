# MongoDB 基础

## 1. MongoDB 概述

MongoDB 是一个开源的文档型 NoSQL 数据库，使用 BSON 格式存储数据。

### 1.1 核心特性
- **文档模型**：类 JSON 的 BSON 格式，灵活的数据结构
- **水平扩展**：原生分片支持
- **高可用**：副本集自动故障转移
- **丰富的查询**：支持聚合管道、全文搜索、地理空间查询

### 1.2 核心概念
| SQL 概念 | MongoDB 概念 |
|----------|-------------|
| Database | Database |
| Table | Collection |
| Row | Document |
| Column | Field |
| Index | Index |
| Join | $lookup |

## 2. 适用场景

- 内容管理（CMS）
- 日志存储与分析
- 物联网时序数据
- 用户画像与个性化推荐
- 移动应用后端
