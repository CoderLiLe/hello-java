# MySQL 基础

## 1. MySQL 概述

MySQL 是最流行的开源关系型数据库管理系统（RDBMS），由 Oracle 公司维护。

### 1.1 核心特性
- **ACID 事务**：支持 InnoDB 存储引擎的事务
- **多版本并发控制（MVCC）**：提高并发读写性能
- **复制**：主从复制、组复制
- **分区**：表分区优化查询

### 1.2 存储引擎
- **InnoDB**：默认引擎，支持事务、行锁、外键
- **MyISAM**：不支持事务，表锁，适合读多写少
- **Memory**：数据存储在内存，适合临时表

## 2. 数据类型

- **数值**：INT、BIGINT、DECIMAL
- **字符串**：VARCHAR、CHAR、TEXT
- **日期时间**：DATE、DATETIME、TIMESTAMP
- **JSON**：原生 JSON 类型

## 3. 索引

- B-Tree 索引
- 哈希索引
- 全文索引
- 空间索引

## 4. SQL 语句分类

- DDL（数据定义语言）
- DML（数据操作语言）
- DCL（数据控制语言）
- TCL（事务控制语言）
