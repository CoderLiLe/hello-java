# TiDB 基础

## 1. TiDB 概述

TiDB 是 PingCAP 设计的分布式 NewSQL 数据库，支持水平弹性扩展、ACID 事务、标准 SQL 语法。

### 1.1 核心特性
- **MySQL 兼容**：高兼容性，可直接迁移
- **弹性扩展**：计算/存储分离，按需扩缩容
- **分布式事务**：乐观/悲观事务
- **高可用**：Raft 协议，故障自恢复
- **HTAP**：OLTP + OLAP 混合负载

### 1.2 架构组件
```
                       TiDB Server (SQL 层)
                       /        |        \
                 Placement Driver (PD)
                       |        |        |
              TiKV Node-1  TiKV Node-2  TiKV Node-3 (存储层)
                       \        |        /
                   TiFlash (列式存储，可选)
```

- **TiDB Server**：无状态 SQL 层，解析 SQL，生成执行计划
- **PD (Placement Driver)**：集群管理，元数据存储，时间戳分配
- **TiKV**：分布式 Key-Value 存储引擎（RocksDB + Raft）
- **TiFlash**：列式存储引擎，加速分析查询

## 2. 数据存储

### 2.1 Region 与 Raft
- 表数据按 Key 范围切分为 Region（默认 96MB）
- 每个 Region 默认 3 副本
- Raft 协议保证强一致性
- Region 自动分裂与合并

### 2.2 数据读写流程
```
写入：
Client -> TiDB（生成 Key-Value）-> TiKV Leader -> Raft 复制 -> 返回 ACK

读取：
Client -> TiDB -> TiKV（Leader/Follower 都可读）
```

## 3. SQL 使用

### 3.1 创建表
```sql
CREATE TABLE user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    INDEX idx_name (name)
);
```

### 3.2 分区表
```sql
-- Range 分区
CREATE TABLE orders (
    id BIGINT,
    order_date DATE
) PARTITION BY RANGE (YEAR(order_date)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025)
);

-- Hash 分区
CREATE TABLE logs (
    id BIGINT,
    content TEXT
) PARTITION BY HASH(id) PARTITIONS 4;
```

### 3.3 聚簇表
```sql
-- TiDB v5.0+ 默认使用聚簇索引
CREATE TABLE t (a INT PRIMARY KEY, b VARCHAR(100));
-- 与 MySQL 不同，TiDB 的 PK 即为数据行 ID
```

## 4. 事务

### 4.1 乐观事务
```sql
-- 默认使用乐观锁
BEGIN;
UPDATE account SET balance = balance - 100 WHERE id = 1;
UPDATE account SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

### 4.2 悲观事务
```sql
-- 显式开启悲观事务
BEGIN PESSIMISTIC;
SELECT * FROM account WHERE id = 1 FOR UPDATE;
UPDATE account SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

## 5. 集群运维

### 5.1 TiUP 工具
```bash
# 安装 TiUP
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh

# 部署集群
tiup cluster deploy my-cluster v6.5.0 ./topology.yaml

# 集群管理
tiup cluster start my-cluster
tiup cluster stop my-cluster
tiup cluster scale-out my-cluster scale.yaml
tiup cluster display my-cluster
tiup cluster exec my-cluster --command "uptime"
```

### 5.2 扩容缩容
```yaml
# scale.yaml
tikv_servers:
  - host: 192.168.1.4
    port: 20160
    status_port: 20180
    deploy_dir: /data/tidb/tikv
```

### 5.3 备份恢复
```bash
# BR 备份
tiup br backup full --pd "192.168.1.1:2379" \
  --storage "s3://backup-bucket/2023-01" \
  --ratelimit 128

# BR 恢复
tiup br restore full --pd "192.168.1.1:2379" \
  --storage "s3://backup-bucket/2023-01"
```

## 6. 监控与诊断

### 6.1 监控面板
- TiDB Dashboard（PD 内置，默认 2379）
- Grafana（TiUP 部署内置）
- Key Visualizer：热点可视化
- Slow Query：慢查询分析
- Statements：SQL 分析

### 6.2 慢查询排查
```sql
-- 查询慢 SQL
SELECT * FROM information_schema.slow_query
WHERE time > '2023-01-01'
ORDER BY query_time DESC;
```

## 7. 生产部署拓扑

```yaml
# topology.yaml
global:
  user: "tidb"
  ssh_port: 22
  deploy_dir: "/data/tidb"
  data_dir: "/data/tidb/data"

pd_servers:
  - host: 192.168.1.1
  - host: 192.168.1.2
  - host: 192.168.1.3

tikv_servers:
  - host: 192.168.1.1
  - host: 192.168.1.2
  - host: 192.168.1.3

tidb_servers:
  - host: 192.168.1.4
  - host: 192.168.1.5

monitoring_servers:
  - host: 192.168.1.6

grafana_servers:
  - host: 192.168.1.6
```

## 8. TiDB vs 其他方案

| 特性 | TiDB | MySQL | CockroachDB | YugabyteDB |
|------|------|-------|-------------|------------|
| 兼容性 | MySQL | 原生 | PostgreSQL | PostgreSQL |
| 扩展性 | 水平 | 垂直为主 | 水平 | 水平 |
| 一致性 | 强一致 | 主从异步 | 强一致 | 强一致 |
| 事务 | 分布式 | 单机 | 分布式 | 分布式 |
| 部署 | 复杂 | 简单 | 中等 | 中等 |

## 9. 最佳实践

- 使用 TiDB Lightning 快速导入数据
- 监控热点 Region，使用 SHARD_ROW_ID_BITS 打散
- 大表使用分区表
- 避免长事务
- Region 规划：128MB ~ 256MB 适中
- 配置合适的 GC 时间（默认 10 分钟）
