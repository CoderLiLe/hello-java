# Redis 原理

本文深入 Redis 底层，讲解 Redis 的数据结构实现、网络模型、通信协议与内存回收机制。

## 1. Redis 数据结构底层实现

### 1.1 动态字符串 SDS

Redis 中保存的 Key 是字符串，value 往往是字符串或字符串的集合，字符串是 Redis 最常用的数据结构。

Redis 没有直接使用 C 语言字符串，因为 C 字符串存在以下问题：

- 获取字符串长度需要遍历运算
- 非二进制安全
- 不可修改

Redis 构建了一种新的字符串结构——**简单动态字符串 SDS（Simple Dynamic String）**。SDS 是一个结构体，具备动态扩容能力。例如给内容为 "hi" 的 SDS 追加 ",Amy"，会先申请新内存：

- 若新字符串小于 1M，新空间为扩展后字符串长度的两倍 + 1。
- 若新字符串大于 1M，新空间为扩展后字符串长度 + 1M + 1。

这称为**内存预分配**。

### 1.2 整数集合 intset

IntSet 是 Redis 中 Set 集合的一种实现方式，基于整数数组实现，具备长度可变、有序等特征。

- encoding 分三种模式（int16、int32、int64），表示存储整数大小不同。
- 数组中的整数按升序保存在 contents 数组中。
- 当插入超出当前编码范围的整数（如向 int16 插入 50000）时，自动升级编码并扩容。

IntSet 特点：

- 保证元素唯一、有序
- 具备类型升级机制，节省内存
- 底层采用二分查找查询

### 1.3 字典 Dict

Redis 是键值型数据库，键与值的映射关系通过 Dict 实现。Dict 由三部分组成：哈希表（DictHashTable）、哈希节点（DictEntry）、字典（Dict）。

添加键值对时，先根据 key 计算 hash 值 h，再利用 `h & sizemask` 计算存储的数组索引位置。

**Dict 的扩容**：Dict 每次新增键值对时检查负载因子 `LoadFactor = used / size`，满足以下条件时触发扩容：

- `LoadFactor >= 1`，且服务器没有执行 BGSAVE/BGREWRITEAOF 等后台进程；
- `LoadFactor > 5`。

**Dict 的 rehash**：扩容或收缩都会创建新哈希表，需对每个 key 重新计算索引并插入新表，这个过程称为 rehash。关键点：

- 扩容大小：第一个大于等于 `used + 1` 的 2^n；收缩大小：第一个大于等于 `used` 的 2^n（不小于 4）。
- Dict 包含两个哈希表 `ht[0]`（平时用）和 `ht[1]`（rehash 用）。
- 采用**渐进式 rehash**：每次访问 Dict 时执行一次 rehash，避免一次性 rehash 阻塞。
- rehash 期间 `ht[0]` 只减不增，新增操作只写 `ht[1]`，查询/修改/删除在两个哈希表中依次查找。

### 1.4 压缩列表 ZipList

ZipList 是一种特殊的"双端链表"，由一系列特殊编码的**连续内存块**组成，可在任意一端进行压入/弹出，时间复杂度 O(1)。

结构由五部分组成：

| 属性   | 长度   | 用途                                                     |
| ------ | ------ | -------------------------------------------------------- |
| zlbytes | 4 字节 | 记录整个压缩列表占用内存字节数                             |
| zltail  | 4 字节 | 记录表尾节点距起始地址的偏移量                             |
| zllen   | 2 字节 | 记录节点数量（最大值 65534，超过需遍历计算）               |
| entry   | 不定   | 各个节点                                                 |
| zlend   | 1 字节 | 特殊值 0xFF，标记压缩列表末端                             |

ZipList 的 Entry 不记录前后节点指针（两个指针需 16 字节），而是记录：

- `previous_entry_length`：前一节点长度，1 或 5 字节。
- `encoding`：编码属性，记录 content 数据类型及长度，1/2/5 字节。
- `contents`：节点数据。

**连锁更新（Cascade Update）**：当存在连续多个长度在 250~253 字节之间的 entry 时，若某节点长度变化导致 `previous_entry_length` 从 1 字节升级为 5 字节，可能引发连续的多次空间扩展。新增、删除都可能导致连锁更新。

ZipList 特性：

- 可看作连续内存空间的"双向链表"，通过记录长度寻址，内存占用低。
- 数据过多导致链表过长，查询性能下降。
- 增删较大数据可能发生连锁更新。

### 1.5 快速列表 QuickList

ZipList 虽节省内存，但要求连续空间，内存占用较多时申请效率低。于是需要限制 ZipList 长度和 entry 大小；同时用多个 ZipList 分片存储大量数据。

Redis 3.2 引入 **QuickList**：一个双端链表，每个节点都是一个 ZipList。

为避免每个 ZipList entry 过多，通过 `list-max-ziplist-size` 配置限制：

- 值为正：代表 entry 个数上限。
- 值为负：代表 ZipList 最大内存大小（-1 到 -5 分别对应 4kb/8kb/16kb/32kb/64kb），默认 -2（8kb）。

QuickList 特点：

- 节点为 ZipList 的双端链表
- 节点用 ZipList 解决传统链表内存占用问题
- 控制 ZipList 大小解决连续内存申请效率问题
- 中间节点可压缩，进一步节省内存

### 1.6 跳表 SkipList

SkipList（跳表）首先是链表，但与普通链表相比：

- 元素按升序排列存储
- 节点可能包含多个指针，指针跨度不同

SkipList 特点：

- 双向链表，每个节点包含 score 和 ele 值
- 按 score 排序，score 相同按 ele 字典序排序
- 每个节点可包含多层指针，层数 1~32 之间的随机数
- 层越高跨度越大
- 增删改查效率与红黑树基本一致，实现却更简单

### 1.7 RedisObject

Redis 中任意数据类型的键和值都会被封装为一个 **RedisObject（robj）**。

从内部实现看，database 内的 key-value 映射用 dict 维护：key 固定用 SDS 表达；value 类型多样，需要一个通用数据结构来表达，这就是 redisObject。

Redis 根据存储的数据类型选择不同的编码方式，共 11 种，常用的有：

| 编码方式       | 说明               |
| -------------- | ------------------ |
| OBJ_ENCODING_RAW | raw 编码动态字符串 |
| OBJ_ENCODING_INT | long 类型整数的字符串 |
| OBJ_ENCODING_HT | hash 表（dict）    |
| OBJ_ENCODING_ZIPLIST | 压缩列表     |
| OBJ_ENCODING_INTSET | 整数集合     |
| OBJ_ENCODING_SKIPLIST | 跳表       |
| OBJ_ENCODING_EMBSTR | embstr 动态字符串 |
| OBJ_ENCODING_QUICKLIST | 快速列表   |

五种数据结构的编码方式：

| 数据类型 | 编码方式                                        |
| -------- | ----------------------------------------------- |
| String   | int、embstr、raw                                |
| List     | LinkedList+ZipList（3.2 前）、QuickList（3.2 后） |
| Set      | intset、HT                                      |
| ZSet     | ZipList、HT、SkipList                           |
| Hash     | ZipList、HT                                     |

### 1.8 String 底层实现

String 基本编码是 RAW（基于 SDS），存储上限 512MB。

- 若 SDS 长度小于 44 字节，采用 **EMBSTR** 编码，object head 与 SDS 是连续空间，只需一次内存分配。
- 若字符串是整数值且在 LONG_MAX 范围内，采用 **INT** 编码，直接保存在 RedisObject 的 ptr 指针位置（8 字节），不再需要 SDS。
- 对 string 做 `incr`/`decr` 时，若内部是 INT 编码可直接加减；若是 RAW/EMBSTR 编码，会先尝试转成 long 再加减。

### 1.9 List 底层实现

List 可从首、尾操作元素。3.2 之前采用 ZipList + LinkedList（元素数小于 512 且元素大小小于 64 字节用 ZipList，否则用 LinkedList）；3.2 之后统一采用 QuickList。

### 1.10 Set 底层实现

Set 要求元素唯一、查询效率高。采用 HT 编码（Dict），Dict 的 key 存元素，value 统一为 null。当所有数据都是整数且数量不超过 `set-max-intset-entries` 时，采用 IntSet 编码以节省内存。

### 1.11 ZSet 底层实现

ZSet（SortedSet）每个元素有 score 和 member：可按 score 排序、member 唯一、可按 member 查 score。

因此底层必须满足"键值存储、键唯一、可排序"，采用：

- **SkipList**：可排序，同时存储 score 和 member。
- **HT（Dict）**：键值存储，按 key 找 value。

当元素数量不多时（元素数 < `zset_max_ziplist_entries` 默认 128，且每个元素 < `zset_max_ziplist_value` 默认 64 字节），采用 ZipList 节省内存：score 和 element 紧挨在一起的两个 entry，element 在前、score 在后，按 score 升序排列。

### 1.12 Hash 底层实现

Hash 与 ZSet 类似，都是键值存储、按键取值、键唯一。区别：ZSet 键是 member、值是 score 且需排序；Hash 键和值都是任意值且无需排序。

- 数据项较少时采用 ZipList（相邻两个 entry 分别存 field 和 value）。
- 数据量较大时转为 HT（Dict），触发条件：元素数量超过 `hash-max-ziplist-entries`（默认 512），或任意 entry 大小超过 `hash-max-ziplist-value`（默认 64 字节）。

## 2. Redis 网络模型

### 2.1 用户空间与内核空间

Linux 系统中，进程的寻址空间划分为两部分：**内核空间**和**用户空间**。

- 用户空间只能执行受限命令（Ring3），不能直接调用系统资源，必须通过内核提供的接口访问。
- 内核空间可执行特权命令（Ring0），调用一切系统资源。

Linux 为提高 IO 效率，在用户空间和内核空间都加入缓冲区：

- 写数据：用户缓冲 → 内核缓冲 → 设备
- 读数据：设备 → 内核缓冲 → 用户缓冲

### 2.2 五种 IO 模型

《UNIX 网络编程》总结归纳了 5 种 IO 模型：阻塞 IO、非阻塞 IO、IO 多路复用、信号驱动 IO、异步 IO。

**（1）阻塞 IO**：用户进程发起读请求后，两个阶段（等待数据、数据拷贝）都处于阻塞状态。

**（2）非阻塞 IO**：`recvfrom` 立即返回结果而不阻塞。第一阶段无数据时返回异常，用户进程循环重试（忙等，CPU 空转）；第二阶段拷贝数据时仍阻塞。性能并未提高，且忙等导致 CPU 使用率暴增。

**（3）IO 多路复用**：利用单个线程同时监听多个 FD（文件描述符），在某个 FD 可读/可写时得到通知，避免无效等待。

文件描述符（FD）：一个从 0 开始的无符号整数，用来关联 Linux 中的文件（一切皆文件，包括 Socket）。

IO 多路复用的常见实现有 select、poll、epoll。

### 2.3 select / poll / epoll

**select**：

- 用户态创建 fd 集合（大小有限制，最大 1024），传给内核态。
- 内核遍历 fd，无数据就绪则休眠，有数据唤醒后再次遍历，将就绪状态写回用户态。
- 用户态需遍历 fd 集合找到就绪的节点再发起读请求。

问题：能监听 FD 上限 1024；每次需拷贝所有 FD 到内核空间；每次遍历所有 FD。

**poll**：对 select 做了简单改进，用链表存储 pollfd（理论上无上限），但依然要遍历所有 FD，监听较多时性能下降。

**epoll**：提供三个函数（`epoll_create`、`epoll_ctl`、`epoll_wait`），核心是 eventpoll 实例，内含：

- **红黑树**：记录要监听的 FD。
- **链表**：记录就绪的 FD。

epoll 解决 select/poll 问题的方式：

- 基于红黑树保存 FD，理论上无上限，增删改查效率高。
- 每个 FD 只需一次 `epoll_ctl` 加入红黑树，无需重复拷贝 FD 到内核空间。
- 利用回调机制监听 FD 状态，无需遍历所有 FD，性能不随 FD 数量增多而下降。

### 2.4 epoll 的 ET 与 LT

事件通知有两种模式：

- **LT（Level Triggered，水平触发）**：只要 FD 中有数据可读，每次调用 `epoll_wait` 都会得到通知。
- **ET（Edge Triggered，边沿触发）**：只有 FD 有状态变化时，`epoll_wait` 才会被通知。

### 2.5 信号驱动 IO 与异步 IO

**信号驱动 IO**：与内核建立 SIGIO 信号关联并设置回调，内核有 FD 就绪时发出 SIGIO 通知，用户期间可执行其它业务。但大量 IO 时信号较多，可能溢出，且频繁信号交互性能较低。

**异步 IO**：用户态发起读取后不阻塞，内核完成所有数据处理后直接写入用户态，两个阶段都非阻塞，性能极高。

### 2.6 Redis 是单线程还是多线程？

- 若只谈 Redis 核心业务（命令处理），答案是**单线程**。
- 若谈整个 Redis，答案是**多线程**。

多线程引入的两个时间节点：

- Redis v4.0：引入多线程异步处理耗时任务（如异步删除 `unlink`）。
- Redis v6.0：核心网络模型中引入多线程，提高多核 CPU 利用率。

**为什么核心用单线程？**

- 纯内存操作，性能瓶颈是网络延迟而非执行速度，多线程收益不大。
- 多线程带来上下文切换开销。
- 引入多线程面临线程安全问题，需引入锁，实现复杂度增高、性能打折扣。

### 2.7 Redis 单线程网络模型

Redis 通过 IO 多路复用（epoll）实现高效网络请求，将客户端并发请求转成串行执行，因此无需考虑 MySQL 的脏读、幻读等并发问题。事件处理器包括：

- 连接应答处理器：接受连接请求。
- 命令请求处理器：读取并解析命令。
- 命令回复处理器：返回执行结果。

Redis 6.0 之后，在命令回复处理器和命令请求处理器的命令转换环节使用了多线程，但命令执行本身仍是单线程。

## 3. Redis 通信协议 RESP

Redis 是 CS 架构软件，客户端与服务器通信需遵循规范，即 **RESP（Redis Serialization Protocol）** 协议。

RESP 通过首字节字符区分数据类型，常见 5 种：

| 类型         | 首字节 | 示例              |
| ------------ | ------ | ----------------- |
| 单行字符串   | `+`    | `+OK\r\n`         |
| 错误         | `-`    | `-Error message\r\n` |
| 数值         | `:`    | `:10\r\n`         |
| 多行字符串   | `$`    | `$3\r\nabc\r\n`（长度 + 数据） |
| 数组         | `*`    | `*2\r\n...`（元素个数 + 元素） |

RESP 协议支持 TCP 通信，因此可用 Socket 模拟客户端与 Redis 交互（如手工组装 `*3\r\n$3\r\nSET...` 报文发送）。

## 4. Redis 内存回收

### 4.1 过期 key 的处理

Redis 通过 `expire` 命令给 key 设置 TTL。Redis 的 database 结构体中有两个 Dict：一个记录 key-value，另一个记录 key-TTL，通过后者判断 key 是否过期。

**过期删除策略：惰性删除 + 定期删除**

**（1）惰性删除**：不是在 TTL 到期立即删除，而是在访问 key 时检查是否过期，过期才删除。

- 优点：对 CPU 友好。
- 缺点：对内存不友好，过期但一直未访问的 key 会一直占用内存。

**（2）定期删除**：通过定时任务周期性抽样部分过期 key 删除，有两种模式：

- **SLOW 模式**：`initServer()` 设置定时任务，频率受 `server.hz` 影响（默认 10，每秒 10 次），每次耗时不超过执行周期 25%（默认 25ms），抽样 20 个 key 判断是否过期，过期比例大于 10% 则再次抽样。
- **FAST 模式**：事件循环前 `beforeSleep()` 执行，两次间隔不低于 2ms，每次耗时不超过 1ms。

### 4.2 内存淘汰策略

内存淘汰：当 Redis 内存达到设置上限时，主动挑选部分 key 删除以释放内存。Redis 支持 8 种策略：

- `noeviction`：不淘汰，内存满时不允许写入新数据（默认策略）。
- `volatile-ttl`：对设置了 TTL 的 key，剩余 TTL 越小越先淘汰。
- `allkeys-random`：对全体 key 随机淘汰。
- `volatile-random`：对设置了 TTL 的 key 随机淘汰。
- `allkeys-lru`：对全体 key，基于 LRU 算法淘汰。
- `volatile-lru`：对设置了 TTL 的 key，基于 LRU 算法淘汰。
- `allkeys-lfu`：对全体 key，基于 LFU 算法淘汰。
- `volatile-lfu`：对设置了 TTL 的 key，基于 LFU 算法淘汰。

两个易混淆概念：

- **LRU（Least Recently Used）**：最近最少使用。用当前时间减去最后一次访问时间，值越大淘汰优先级越高。
- **LFU（Least Frequently Used）**：最少频率使用。统计每个 key 的访问频率，值越小淘汰优先级越高。

LFU 的访问次数是"逻辑访问次数"，通过运算得出（生成随机数 R，计算 `旧次数 * lfu_log_factor + 1` 记为 P，若 `R < P` 则计数 +1，最大 255；访问次数随 `lfu_decay_time` 时间衰减）。

**使用建议**：

- 优先使用 `allkeys-lru`，充分利用 LRU 优势，适合有明显冷热数据区分的业务。
- 数据访问频率差别不大时，用 `allkeys-random`。
- 有置顶需求时用 `volatile-lru`，置顶数据不设置过期时间。
- 有短时高频访问数据时用 `allkeys-lfu` 或 `volatile-lfu`。

## 5. 总结

- Redis 底层通过 SDS、intset、Dict、ZipList、QuickList、SkipList、RedisObject 等结构，在内存占用与查询效率之间取得平衡。
- 核心网络模型基于 epoll 的 IO 多路复用，命令执行单线程，Redis 6.0 后在网络 IO 环节引入多线程。
- 通信遵循 RESP 协议，内存回收采用"惰性删除 + 定期删除"，并辅以 8 种内存淘汰策略。
