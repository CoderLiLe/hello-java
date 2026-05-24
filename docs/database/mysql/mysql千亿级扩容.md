# MySQL 千亿级数据生产环境扩容实战

## 1. 扩容概述

### 1.1 何时需要扩容
- 单表数据量超过千万级
- 磁盘 IO 成为瓶颈
- 写入 QPS 超过单机能力
- 备份恢复时间过长

### 1.2 扩容策略
| 策略 | 说明 | 适用场景 |
|------|------|---------|
| 垂直扩容 | 升级硬件 | 短期方案 |
| 读写分离 | 一主多从 | 读多写少 |
| 分库分表 | 水平拆分 | 海量数据 |
| NewSQL | TiDB/ShardingSphere | 极致扩展 |

## 2. 平滑扩容方案

### 2.1 设计方案（双写迁移）

```
旧库 (MySQL A) <-- 双写 -- 新库 (MySQL B)
    |                         |
历史数据（全量迁移）      增量同步（实时双写）
    |                         |
    +---- 校验/切换 --------+
```

### 2.2 双写迁移步骤

**阶段一：双写准备**
```java
public class DualWriteService {
    @Autowired
    private UserMapper oldMapper;
    @Autowired
    private UserMapper newMapper;
    
    @Transactional
    public void saveUser(User user) {
        oldMapper.insert(user);
        try {
            newMapper.insert(user);
        } catch (Exception e) {
            log.error("新库写入失败", e);
            // 记录失败到补偿表
            compensateService.record(user);
        }
    }
}
```

**阶段二：全量迁移**
```bash
# 使用工具迁移历史数据
# 方案1：SELECT INTO OUTFILE + LOAD DATA
SELECT * INTO OUTFILE '/tmp/users.csv' FROM users;
LOAD DATA INFILE '/tmp/users.csv' INTO TABLE new_db.users;

# 方案2：分批迁移
# 按 ID 范围分批，10000 条一批
```

**阶段三：数据校验**
```sql
-- 校验记录数
SELECT COUNT(1) FROM old_db.users;
SELECT COUNT(1) FROM new_db.users;

-- 校验 checksum
SELECT SUM(CRC32(CONCAT(id, name, age))) FROM old_db.users;
SELECT SUM(CRC32(CONCAT(id, name, age))) FROM new_db.users;
```

**阶段四：灰度切换**
```java
// 按用户 ID 灰度
public class RouterService {
    public boolean isNewDb(long userId) {
        // 灰度百分比逐步提高
        return userId % 100 < grayPercent;
    }
}
```

### 2.3 扩容注意事项
- 双写期间做好监控
- 准备回滚方案
- 选择业务低峰期操作
- 设置合理的超时时间
- 做好容错和补偿机制

## 3. 分库分表策略

### 3.1 分片键选择
```sql
-- 按用户 ID 分片
order_id % 16 -> 16 个库
user_id % 32 -> 每个库 32 张表

-- 按时间分片
ORDER BY order_date -> 按月分表
```

### 3.2 扩容流程
```
4 库 X 32 表 -> 8 库 X 64 表
                  |
1. 创建新库表结构
2. 路由规则更新（旧->新）
3. 数据迁移（按旧路由规则读取，新规则写入）
4. 双写校验
5. 切换路由
6. 清理旧数据（可选）
```

## 4. 架构升级

### 4.1 读写分离
```yaml
# 主从配置
spring:
  datasource:
    master:
      url: jdbc:mysql://master:3306/db
    slave:
      url: jdbc:mysql://slave1:3306/db
      url: jdbc:mysql://slave2:3306/db
```

### 4.2 分库分表
```yaml
spring:
  shardingsphere:
    datasource:
      names: ds0,ds1
      ds0:
        url: jdbc:mysql://192.168.1.1:3306/db0
      ds1:
        url: jdbc:mysql://192.168.1.2:3306/db1
    sharding:
      tables:
        user:
          actualDataNodes: ds${0..1}.user_${0..15}
          databaseStrategy:
            inline:
              shardingColumn: user_id
              algorithmExpression: ds${user_id % 2}
          tableStrategy:
            inline:
              shardingColumn: user_id
              algorithmExpression: user_${user_id % 16}
```

## 5. 监控与告警

| 指标 | 告警阈值 | 说明 |
|------|---------|------|
| 延迟 | > 5 秒 | 主从延迟 |
| 慢查询 | > 1 秒 | 慢 SQL |
| 连接数 | > 80% | 连接池 |
| 磁盘 | > 85% | 空间预警 |
| TPS | > 80% 峰值 | 容量预警 |
