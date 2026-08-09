# Seata 基础

## 1. Seata 概述

Seata（Simple Extensible Autonomous Transaction Architecture）是阿里巴巴开源的分布式事务解决方案，提供高性能、易于使用的分布式事务服务。

### 1.1 核心模式
- **AT 模式**：自动补偿型事务，基于本地事务的自动回滚（推荐）
- **TCC 模式**：Try-Confirm-Cancel，两阶段补偿型
- **Saga 模式**：长事务补偿，正向服务 + 补偿服务
- **XA 模式**：基于 XA 协议的两阶段提交

### 1.2 核心组件
- **TC（Transaction Coordinator）**：事务协调器，维护全局事务状态
- **TM（Transaction Manager）**：事务管理器，定义全局事务边界
- **RM（Resource Manager）**：资源管理器，管理分支事务

## 2. AT 模式原理
1. **一阶段**：执行本地事务并生成 undo log
2. **二阶段-提交**：异步删除 undo log
3. **二阶段-回滚**：通过 undo log 回滚本地事务
