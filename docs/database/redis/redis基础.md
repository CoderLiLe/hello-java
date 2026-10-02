# Redis 基础

Redis（**Re**mote **D**ictionary **S**erver，远程字典服务器）诞生于 2009 年，作者是 Antirez，是一个开源的、基于内存的键值型 NoSQL 数据库，常用作缓存、数据库和消息代理。官网：https://redis.io/

## 1. Redis 概述

### 1.1 认识 NoSQL

**NoSQL** 可以翻译为 Not Only SQL（不仅仅是 SQL），是相对于传统关系型数据库而言有很大差异的一类数据库，因此也称之为**非关系型数据库**。

与关系型数据库（如 MySQL）相比，主要有以下几点差异：

**（1）结构化与非结构化**

- 关系型数据库是**结构化数据**，每张表都有严格的约束信息（字段名、数据类型、约束等），插入的数据必须遵守这些约束。
- NoSQL 对数据格式没有严格约束，形式松散、自由。可以是键值型、文档型、图格式等。

**（2）关联与非关联**

- 关系型数据库的表与表之间往往存在关联（如外键）。
- 非关系型数据库不存在关联关系，要维护关系要么靠代码中的业务逻辑，要么靠数据之间的耦合。

**（3）查询方式**

- 关系型数据库基于 SQL 语句做查询，语法有统一标准。
- 不同的非关系型数据库查询语法差异极大。

**（4）事务**

- 关系型数据库能满足事务 ACID 原则。
- 非关系型数据库往往不支持事务，或不能严格保证 ACID 特性，只能实现基本的一致性。

**（5）存储方式与扩展性**

| 维度   | 关系型数据库（SQL）            | 非关系型数据库（NoSQL）                  |
| ------ | ------------------------------ | ---------------------------------------- |
| 存储方式 | 基于磁盘，大量磁盘 IO          | 更多依赖内存，读写快，性能好             |
| 扩展性   | 一般主从垂直扩展               | 可数据拆分水平扩展，保存海量数据         |
| 数据约束 | 严格约束                      | 松散自由                                 |

### 1.2 Redis 特征

- **键值（key-value）型**：value 支持多种不同数据结构，功能丰富。
- **单线程**：每个命令具备原子性。
- **低延迟、速度快**：基于内存、IO 多路复用、良好的编码。
- **支持数据持久化**：RDB + AOF。
- **支持主从集群、分片集群**：高可用与水平扩展。
- **支持多语言客户端**。

### 1.3 核心特性概览

- **高性能**：基于内存，读写速度极快（10W+ QPS）。
- **丰富的数据结构**：String、List、Set、ZSet、Hash、Stream、BitMap、GEO、HyperLogLog 等。
- **持久化**：RDB 快照 + AOF 日志。
- **高可用**：主从复制 + Sentinel 哨兵。
- **集群**：Redis Cluster 分片。

## 2. 安装 Redis

大多数企业基于 Linux 服务器部署，Redis 官方未提供 Windows 版本安装包。

### 2.1 依赖库

Redis 基于 C 语言编写，需要先安装 gcc 依赖：

```sh
yum install -y gcc tcl
```

### 2.2 编译安装

```sh
# 上传安装包后解压
tar -xzf redis-6.2.6.tar.gz
cd redis-6.2.6
# 编译并安装
make && make install
```

默认安装路径在 `/usr/local/bin`，该目录已配置到环境变量，可在任意目录运行：

- `redis-cli`：命令行客户端
- `redis-server`：服务端启动脚本
- `redis-sentinel`：哨兵启动脚本

### 2.3 启动方式

**默认启动（前台）**：直接执行 `redis-server`，会阻塞整个会话窗口，不推荐。

**指定配置启动（后台）**：修改 `redis.conf` 后启动：

```properties
# 允许访问的地址，生产环境不要设置为 0.0.0.0
bind 0.0.0.0
# 守护进程，yes 后台运行
daemonize yes
# 密码
requirepass 123321
```

其它常见配置：

```properties
# 监听端口
port 6379
# 工作目录（日志、持久化文件保存目录）
dir .
# 数据库数量，默认 16 个库，编号 0~15
databases 1
# 最大内存
maxmemory 512mb
# 日志文件
logfile "redis.log"
```

启动与停止：

```sh
redis-server redis.conf          # 启动
redis-cli -u 123321 shutdown     # 停止（通过 shutdown 命令）
```

### 2.4 开机自启

新建系统服务文件 `/etc/systemd/system/redis.service`：

```conf
[Unit]
Description=redis-server
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/redis-server /usr/local/src/redis-6.2.6/redis.conf
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```sh
systemctl daemon-reload
systemctl enable redis    # 开机自启
systemctl start redis     # 启动
systemctl stop redis      # 停止
```

### 2.5 命令行客户端 redis-cli

```sh
redis-cli [options] [commands]
```

常用 options：

- `-h 127.0.0.1`：指定 IP，默认 127.0.0.1
- `-p 6379`：指定端口，默认 6379
- `-a 123321`：指定访问密码

`ping` 命令做心跳测试，正常返回 `pong`。Redis 默认有 16 个库（0~15），通过 `select 0` 选择数据库。

## 3. Redis 常见命令

Redis 是一个 key-value 数据库，key 一般是 String 类型，value 类型多种多样。命令不必死记，可通过官网 https://redis.io/commands 或 `help [command]` 查询。

### 3.1 通用命令

通用命令是部分数据类型的、都可使用的指令：

| 命令     | 作用                                       |
| -------- | ------------------------------------------ |
| `KEYS`   | 查看符合模板的所有 key（生产环境慎用）      |
| `DEL`    | 删除一个或多个 key                          |
| `EXISTS` | 判断 key 是否存在                           |
| `EXPIRE` | 给 key 设置有效期，到期自动删除             |
| `TTL`    | 查看 key 剩余有效期（-1 永久，-2 已过期）   |

```sh
127.0.0.1:6379> keys *        # 查看所有 key
1) "name"
2) "age"
127.0.0.1:6379> keys a*       # 查看以 a 开头的 key
1) "age"
127.0.0.1:6379> del name      # 删除单个
(integer) 1
127.0.0.1:6379> exists age    # 判断是否存在
(integer) 1
127.0.0.1:6379> expire age 10 # 设置 10 秒有效期
(integer) 1
127.0.0.1:6379> ttl age       # 查看剩余有效期
(integer) 8
```

> 生产环境不推荐使用 `keys` 命令，key 过多时效率不高，建议使用 `scan`。

### 3.2 Key 的层级结构

Redis 没有类似 MySQL 的 Table 概念，为了避免不同类型 key 冲突，通过给 key 添加前缀区分，多个单词用 `:` 隔开：

- `heima:user:1` —— 用户 id 为 1
- `heima:product:1` —— 商品 id 为 1

如果 value 是 Java 对象，可序列化为 JSON 字符串存储：

| KEY              | VALUE                                  |
| ---------------- | -------------------------------------- |
| heima:user:1     | {"id":1, "name": "Jack", "age": 21}    |
| heima:product:1  | {"id":1, "name": "小米11", "price": 4999} |

### 3.3 String 类型

String 是最简单的存储类型，value 根据格式可分为 3 类：普通字符串、整数（可自增自减）、浮点数（可自增自减）。

常见命令：

- `SET` / `GET`：添加或修改 / 获取
- `MSET` / `MGET`：批量添加 / 批量获取
- `INCR`：整型自增 1
- `INCRBY`：整型自增指定步长
- `INCRBYFLOAT`：浮点自增指定步长
- `SETNX`：key 不存在才添加
- `SETEX`：添加并指定有效期

```sh
127.0.0.1:6379> set name Rose     # 不存在则新增
OK
127.0.0.1:6379> set name Jack     # 存在则修改
OK
127.0.0.1:6379> mset k1 v1 k2 v2  # 批量添加
OK
127.0.0.1:6379> mget k1 k2        # 批量获取
1) "v1"
2) "v2"
127.0.0.1:6379> set age 10
OK
127.0.0.1:6379> incr age          # 自增 1
(integer) 11
127.0.0.1:6379> incrby age 2      # 自增 2
(integer) 13
127.0.0.1:6379> decr age          # 自减 1
(integer) 12
127.0.0.1:6379> setnx name lisi   # name 已存在，添加失败
(integer) 0
127.0.0.1:6379> setex token 10 abc  # 添加并设置 10 秒有效期
OK
```

### 3.4 Hash 类型

Hash 也叫散列，value 是一个无序字典，类似 Java 的 HashMap。相比 String 存 JSON，Hash 可以把对象每个字段独立存储，方便针对单个字段做 CRUD。

常见命令：

- `HSET` / `HGET`：添加或修改 / 获取某个 field 的值
- `HMSET` / `HMGET`：批量添加 / 批量获取
- `HGETALL`：获取所有 field 和 value
- `HKEYS` / `HVALS`：获取所有 field / 所有 value
- `HINCRBY`：字段值自增指定步长
- `HSETNX`：field 不存在才添加

```sh
127.0.0.1:6379> hset heima:user:3 name Lucy
(integer) 1
127.0.0.1:6379> hset heima:user:3 age 21
(integer) 1
127.0.0.1:6379> hget heima:user:3 name
"Lucy"
127.0.0.1:6379> hmset heima:user:4 name LiLei age 20 sex man
OK
127.0.0.1:6379> hgetall heima:user:4
1) "name"
2) "LiLei"
3) "age"
4) "20"
5) "sex"
6) "man"
127.0.0.1:6379> hincrby heima:user:4 age 2
(integer) 22
```

### 3.5 List 类型

List 与 Java 的 LinkedList 类似，可看作双向链表，支持正向和反向检索。特征：有序、元素可重复、插入删除快、查询速度一般。常用于朋友圈点赞列表、评论列表等。

常见命令：

- `LPUSH` / `RPUSH`：向左侧 / 右侧插入元素
- `LPOP` / `RPOP`：移除并返回左侧 / 右侧第一个元素
- `LRANGE key start end`：返回指定角标范围内的元素
- `BLPOP` / `BRPOP`：与 LPOP/RPOP 类似，无元素时阻塞等待指定时间

```sh
127.0.0.1:6379> lpush users 1 2 3   # 左侧插入
(integer) 3
127.0.0.1:6379> rpush users 4 5 6   # 右侧插入
(integer) 6
127.0.0.1:6379> lpop users          # 左侧弹出
"3"
127.0.0.1:6379> rpop users          # 右侧弹出
"6"
127.0.0.1:6379> lrange users 1 2    # 角标 1~2 的元素
1) "1"
2) "4"
```

### 3.6 Set 类型

Set 类似 Java 的 HashSet，特征：无序、元素不可重复、查找快、支持交集/并集/差集。

常见命令：

- `SADD` / `SREM`：添加 / 移除元素
- `SCARD`：返回元素个数
- `SISMEMBER`：判断元素是否存在
- `SMEMBERS`：获取所有元素
- `SINTER` / `SDIFF` / `SUNION`：交集 / 差集 / 并集

```sh
# 张三的好友：李四、王五、赵六；李四的好友：王五、麻子、二狗
127.0.0.1:6379> sadd zs lisi wangwu zhaoliu
(integer) 3
127.0.0.1:6379> sadd ls wangwu mazi ergou
(integer) 3
127.0.0.1:6379> scard zs              # 张三好友数量
(integer) 3
127.0.0.1:6379> sinter zs ls          # 共同好友
1) "wangwu"
127.0.0.1:6379> sdiff zs ls           # 张三的好友但不是李四的好友
1) "zhaoliu"
2) "lisi"
127.0.0.1:6379> sunion zs ls          # 两人好友的并集
1) "wangwu"
2) "zhaoliu"
3) "lisi"
4) "mazi"
5) "ergou"
127.0.0.1:6379> sismember zs lisi     # 判断李四是否是张三好友
(integer) 1
```

### 3.7 SortedSet 类型

SortedSet（ZSet）是可排序的 Set，每个元素带一个 score 属性，基于 score 排序，底层是跳表（SkipList）+ hash 表。特征：可排序、元素不重复、查询快。常用于排行榜。

常见命令：

- `ZADD key score member`：添加元素（已存在则更新 score）
- `ZREM`：删除元素
- `ZSCORE`：获取元素 score
- `ZRANK` / `ZREVRANK`：获取升序 / 降序排名
- `ZCARD`：获取元素个数
- `ZCOUNT key min max`：统计 score 在范围内的元素个数
- `ZINCRBY key increment member`：元素 score 自增
- `ZRANGE` / `ZRANGEBYSCORE`：按排名 / 按 score 范围获取元素
- `ZINTER` / `ZUNION` / `ZDIFF`：交集 / 并集 / 差集

## 4. Redis 的 Java 客户端

Redis 官网提供多种语言客户端。Java 客户端常见：

- **Jedis** / **Lettuce**：提供 Redis 命令对应的 API，SpringDataRedis 对两者做了抽象封装。
- **Redisson**：在 Redis 基础上实现分布式可伸缩 Java 数据结构（Map、Queue 等），支持跨进程同步机制（Lock、Semaphore），适合分布式锁等特殊需求。

### 4.1 Jedis 快速入门

引入依赖：

```xml
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>3.7.0</version>
</dependency>
```

使用示例：

```java
private Jedis jedis;

@BeforeEach
void setUp() {
    // 1.建立连接（或从连接池获取）
    jedis = JedisConnectionFactory.getJedis();
    // 2.设置密码
    jedis.auth("123321");
    // 3.选择库
    jedis.select(0);
}

@Test
void testString() {
    String result = jedis.set("name", "虎哥");
    String name = jedis.get("name");
    System.out.println("name = " + name);
}

@Test
void testHash() {
    jedis.hset("user:1", "name", "Jack");
    jedis.hset("user:1", "age", "21");
    Map<String, String> map = jedis.hgetAll("user:1");
    System.out.println(map);
}

@AfterEach
void tearDown() {
    if (jedis != null) {
        jedis.close();
    }
}
```

### 4.2 Jedis 连接池

Jedis 本身线程不安全，频繁创建销毁连接有性能损耗，推荐使用连接池。

```java
public class JedisConnectionFactory {
    private static final JedisPool jedisPool;

    static {
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(8);
        poolConfig.setMaxIdle(8);
        poolConfig.setMinIdle(0);
        poolConfig.setMaxWaitMillis(1000);
        jedisPool = new JedisPool(poolConfig, "192.168.150.101", 6379, 1000, "123321");
    }

    public static Jedis getJedis() {
        return jedisPool.getResource();
    }
}
```

### 4.3 SpringDataRedis

SpringDataRedis 是 Spring 对 Redis 的集成模块，官网：https://spring.io/projects/spring-data-redis

- 整合了 Lettuce 和 Jedis
- 提供 `RedisTemplate` 统一 API 操作 Redis
- 支持发布订阅、哨兵、集群、响应式编程

**使用步骤**：

1. 引入依赖 `spring-boot-starter-data-redis`（及 `commons-pool2`）。
2. 在 `application.yml` 配置 Redis 信息：

```yaml
spring:
  redis:
    host: 192.168.150.101
    port: 6379
    password: 123321
    lettuce:
      pool:
        max-active: 8   # 最大连接
        max-idle: 8     # 最大空闲连接
        min-idle: 0     # 最小空闲连接
        max-wait: 100ms # 连接等待时间
```

3. 注入 `RedisTemplate`：

```java
@SpringBootTest
class RedisDemoApplicationTests {
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Test
    void testString() {
        redisTemplate.opsForValue().set("name", "虎哥");
        Object name = redisTemplate.opsForValue().get("name");
        System.out.println("name = " + name);
    }
}
```

`RedisTemplate` 将不同数据类型的操作 API 封装到不同类中：`opsForValue()`（String）、`opsForHash()`（Hash）、`opsForList()`、`opsForSet()`、`opsForZSet()` 等。

### 4.4 数据序列化器

`RedisTemplate` 可接收任意 Object 作为 value，写入前会把 Object 序列化为字节，**默认采用 JDK 序列化**，缺点是可读性差、内存占用大。

自定义 JSON 序列化：

```java
@Configuration
public class RedisConfig {
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        // JSON 序列化工具
        GenericJackson2JsonRedisSerializer jsonRedisSerializer =
                new GenericJackson2JsonRedisSerializer();
        // key 使用 String 序列化
        template.setKeySerializer(RedisSerializer.string());
        template.setHashKeySerializer(RedisSerializer.string());
        // value 使用 JSON 序列化
        template.setValueSerializer(jsonRedisSerializer);
        template.setHashValueSerializer(jsonRedisSerializer);
        return template;
    }
}
```

JSON 序列化可读性好，能自动完成对象与 JSON 的转换，但会额外记录 class 名称，带来额外内存开销。

### 4.5 StringRedisTemplate

为了减少内存消耗，可手动序列化（只存 String）。SpringDataRedis 提供了 `RedisTemplate` 的子类 `StringRedisTemplate`，其 key 和 value 默认都是 String 序列化方式。

```java
@SpringBootTest
class RedisStringTests {
    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    private static final ObjectMapper mapper = new ObjectMapper();

    @Test
    void testSaveUser() throws JsonProcessingException {
        User user = new User("虎哥", 21);
        // 手动序列化
        String json = mapper.writeValueAsString(user);
        stringRedisTemplate.opsForValue().set("user:200", json);

        // 手动反序列化
        String jsonUser = stringRedisTemplate.opsForValue().get("user:200");
        User user1 = mapper.readValue(jsonUser, User.class);
        System.out.println("user1 = " + user1);
    }
}
```

**序列化实践总结**：

- 方案一：自定义 `RedisTemplate`，序列化器改为 `GenericJackson2JsonRedisSerializer`。
- 方案二：使用 `StringRedisTemplate`，写入时手动序列化为 JSON，读取时手动反序列化。

## 5. 小结

- Redis 是基于内存的键值型 NoSQL 数据库，支持丰富的数据结构、持久化和高可用集群。
- 五种基础数据结构：String、Hash、List、Set、SortedSet，各有适用场景。
- Java 客户端常用 Jedis（+连接池）和 SpringDataRedis（RedisTemplate / StringRedisTemplate）。
- 更深入的底层原理（SDS、跳表、IO 多路复用等）参见 [redis原理](redis原理.md)；应用场景与面试题参见 [redis使用场景](redis使用场景.md)。
