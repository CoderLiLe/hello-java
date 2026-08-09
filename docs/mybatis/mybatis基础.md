# MyBatis 基础

## 1. MyBatis 概述

MyBatis 是一款优秀的持久层框架，支持自定义 SQL、存储过程以及高级映射。MyBatis 消除了几乎所有的 JDBC 代码和参数的手工设置以及结果集的检索。

### 1.1 核心特性
- **SQL 与代码分离**：SQL 写在 XML 或注解中
- **动态 SQL**：基于 OGNL 的表达式的灵活 SQL 拼接
- **映射**：自动将 ResultSet 映射为 POJO
- **插件机制**：通过拦截器扩展功能

### 1.2 核心组件
- **SqlSessionFactory**：创建 SqlSession 的工厂
- **SqlSession**：执行 SQL、获取 Mapper 接口
- **Mapper 接口**：映射 SQL 的 Java 接口
- **Executor**：底层 SQL 执行器

## 2. 与 JPA/Hibernate 对比
| 维度 | MyBatis | Hibernate |
|------|---------|-----------|
| SQL 控制 | 手写 SQL | 自动生成 |
| 学习成本 | 低 | 高 |
| 灵活性 | 高 | 受限于 ORM |
| 适用场景 | 复杂查询 | 标准 CRUD |
