# Redis数据安全性分析

# 一、Redis性能压测脚本介绍

&#x9;Redis的所有数据是保存在内存当中的，得益于内存高效的读写性能，Redis的性能是非常强悍的。但是，内存的缺点是断电即丢失，所以，在实际项目中，Redis一旦需要保存一些重要的数据，就不可能完全使用内存保存数据。因此，在真实项目中要使用Redis，一定需要针对应用场景，对Redis的性能进行估算，从而在数据安全性与读写性能之间找到一个平衡点。

&#x9;Redis提供了压测脚本redis-benchmark，可以对Redis进行快速的基准测试。

```shell
# 20个线程，100W个请求，测试redis的set指令(写数据)
redis-benchmark -a 123qweasd -t set -n 1000000 -c 20
	...
Summary:
  throughput summary: 116536.53 requests per second   ##平均每秒11W次写操作。
  latency summary (msec):
          avg       min       p50       p95       p99       max
        0.111     0.032     0.111     0.167     0.215     3.199
```

> redis-benchmark更多参数，使用redis-benchmark --help指令查看

&#x9;后续逐步调整Redis的各种部署架构后，建议大家自行多进行几次对比测试。


# 二、Redis数据持久化机制详解

## 1、整体介绍Redis的数据持久化机制

&#x9;官网介绍地址： <https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/>

&#x9;Redis提供了很多跟数据持久化相关的配置，大体上，可以组成以下几种策略：

*   无持久化：完全关闭数据持久化，不保证数据安全。相当于将Redis完全当做缓存来用
*   RDB(RedisDatabase)：按照一定的时间间隔缓存Redis所有数据快照。
*   AOF(Append Only File)：记录Redis收到的每一次写操作。这样可以通过操作重演的方式恢复Redis的数据
*   RDB+AOF：同时保存Redis的数据和操作。

&#x9;两种方式的优缺点：

*   RDB

    *   优点：

        1、RDB文件非常紧凑，非常适合定期备份数据。

        2、RDB快照非常适合灾难恢复。

        3、RDB备份时性能非常快，对主线程的性能几乎没有影响。RDB备份时，主线程只需要启动一个负责数据备份的子线程即可。所有的备份工作都由子线程完成，这对主线程的IO性能几乎没有影响。

        4、与AOF相比，RDB在进行大数据量重启时会快很多。
    *   缺点：

        1、RDB不能对数据进行实时备份，所以，总会有数据丢失的可能。

        2、RDB需要fork化子线程的数据写入情况，在fork的过程中，需要将内存中的数据克隆一份。如果数据量太大，或者CPU性能不是很好，RDB方式就容易造成Redis短暂的服务停用。相比之下，AOF也需要进行持久化，但频率较低。并且你可以调整日志重写的频率。
*   AOF

    *   优点：

        1、AOF持久化更安全。例如Redis默认每秒进行一次AOF写入，这样，即使服务崩溃，最多损失一秒的操作。

        2、AOF的记录方式是在之前基础上每次追加新的操作。因此AOF不会出现记录不完整的情况。即使因为一些特殊原因，造成一个操作没有记录完整，也可以使用redis-check-aof工具轻松恢复。

        3、当AOF文件太大时，Redis会自动切换新的日志文件。这样就可以防止单个文件太大的问题。

        4、AOF记录操作的方式非常简单易懂，你可以很轻松的自行调整日志。比如，如果你错误的执行了一次 FLUSHALL 操作，将数据误删除了。使用AOF，你可以简单的将日志中最后一条FLUSHALL指令删掉，然后重启数据库，就可以恢复所有数据。
    *   缺点：

        1、针对同样的数据集，AOF文件通常比RDB文件更大。

        2、在写操作频繁的情况下，AOF备份的性能通常比RDB更慢。

整体使用建议：

1、如果你只是把Redis当做一个缓存来用，可以直接关闭持久化。

2、如果你更关注数据安全性，并且可以接受服务异常宕机时的小部分数据损失，那么可以简单的使用RDB策略。这样性能是比较高的。

3、不建议单独使用AOF。RDB配合AOF，可以让数据恢复的过程更快。


## 2、RDB详解

&#x9;**1、 RDB能干什么**

&#x9;	RDB可以在指定的时间间隔，备份当前时间点的内存中的全部数据集，并保存到餐盘文件当中。通常是dump.rdb文件。在恢复时，再将磁盘中的快照文件直接都会到内存里。

&#x9;	由于RDB存的是全量数据，你甚至可以直接用RDB来传递数据。例如如果需要从一个Redis服务中将数据同步到另一个Redis服务(最好是同版本)，就可以直接复制最近的RDB文件。

&#x9;**2、相关重要配置**

1> save策略： 核心配置

```conf
# Save the DB to disk.
#
# save <seconds> <changes> [<seconds> <changes> ...]
#
# Redis will save the DB if the given number of seconds elapsed and it
# surpassed the given number of write operations against the DB.
#
# Snapshotting can be completely disabled with a single empty string argument
# as in following example:
#
# save ""
#
# Unless specified otherwise, by default Redis will save the DB:
#   * After 3600 seconds (an hour) if at least 1 change was performed
#   * After 300 seconds (5 minutes) if at least 100 changes were performed
#   * After 60 seconds if at least 10000 changes were performed
#
# You can set these explicitly by uncommenting the following line.
#
# save 3600 1 300 100 60 10000
```

2> dir 文件目录

3> dbfilename 文件名 默认dump.rdb

4> rdbcompression 是否启用RDB压缩，默认yes。 如果不想消耗CPU进行压缩，可以设置为no

5> stop-writes-oin-bgsave-error 默认yes。如果配置成no，表示你不在乎数据不一致或者有其他的手段发现和控制这种不一致。在快照写入失败时，也能确保redis继续接受新的写入请求。

6>rdbchecksum 默认yes。在存储快照后，还可以让redis使用CRC64算法来进行数据校验，但是这样做会增加大约10%的性能消耗。如果希望获得最大的性能提升，可以关闭此功能。

&#x9;**3、何时会触发RDB备份**

1> 到达配置文件中默认的快照配置时，会自动触发RDB快照

2>手动执行save或者bgsave指令时，会触发RDB快照。 其中save方法会在备份期间阻塞主线程。bgsve则不会阻塞主线程。但是他会fork一个子线程进行持久化，这个过程中会要将数据复制一份，因此会占用更多内存和CPU。

3> 主从复制时会触发RDB备份。

&#x9;LASTSAVE指令查看最后一次成功执行快照的时间。时间是一个代表毫秒的LONG数字，在linux中可以使用date -d @{timestamp} 快速格式化。
