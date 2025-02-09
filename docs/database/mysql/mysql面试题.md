# mysql经典面试题
## 1. 在mysql中，如何定位慢查询？
### 方案一：开源工具
- 调试工具：Arthas
- 运维工具：Prometheus、Skywalking

![](asserts/mysql面试题/1.1Prometheus.png)

![](asserts/mysql面试题/1.2Skywalking.png)

### 方案二：MySQL自带慢查询
慢查询日志记录了所有执行时间超过指定参数（long_query_time，单位：秒，默认10秒）的所有SQL语句的日志  
如果要开启慢查询日志，需要在MySQL的配置文件（/etc/my.cnf）中配置如下信息：
```text
# 开启MySQL慢日志查询开关 
slow_query_log=1
# 设置慢日志的时间为2秒，SQL语句执行时间超过2秒，就会视为慢查询，记录慢查询日志
long_query_time=2
```

配置完毕之后，通过以下指令重新启动MySQL服务器进行测试，查看慢日志文件中记录的信息 /var/lib/mysql/localhost-slow.log。

## 2. 那这个SQL语句执行很慢，如何分析呢？
可以采用<font color=red size=3>EXPLAIN</font> 或者 <font color=red size=3>DESC</font>命令获取 MySQL 如何执行 SELECT 语句的信息
![](asserts/mysql面试题/2.1explain.png)
 - type 这条sql的连接的类型

| type类型 | 含义   |
|--------|------|
| system | 查询系统中的表 |
| const  | 根据主键查询 |     
| eq_ref | 主键索引查询或唯一索引查询 |
| ref    | 普通索引查询 |
| range  | 范围查询 |
| index  | 索引树扫描 |
| all    | 全表扫描 |

- possible_key 当前sql可能会使用到的索引
- key 当前sql实际命中的索引
- key_len 索引占用的大小
- Extra 额外的优化建议

|Extra|含义|
|---|---|
|Using where; Using Index|查找使用了索引，需要的数据都在索引列中能找到，不需要回表查询数据|
|Using index condition|查找使用了索引，但是需要回表查询数据|
> 如果一条SQL执行很慢，我们通常会使用MySQL的 Explain 命令来分析这条SQL的执行情况。  
> 通过 key 和 key_len 可以检查是否命中了索引，如果已经添加了索引，也可以判断索引是否有效。  
> 通过 type 字段可以查看 SQL 是否有优化空间，比如是否存在全索引扫描或全表扫描。  
> 通过 extra 建议可以判断是否出现回表情况，如果出现，可以尝试添加索引 或 修改返回字段来优化。

## 3. 谈谈你对索引的理解
索引(index)是帮助MySQL高效获取数据的数据结构（有序）。在数据之外，数据库系统还维护着满足特定查找算法的数据结构，这些数据结构以某种方式引用（指向）数据，这样就可以在这些数据结构上实现高级查找算法，这种数据结构就是索引。  

MySQL默认使用的索引底层数据结构是B+树。

先看一下树相关的数据结构：
![](asserts/mysql面试题/3.1树相关数据结构.png)
以上几种数据结构在节点很多时树的深度会很深，查询的效率会降低。

B-Tree，B树是一种多叉平衡查找树，相对于二叉树，B树每个节点可以有多个分支，即多叉。  
以一棵最大度数（max-degree）为5（5阶）的B-tree为例，这个B树每个节点最多存储4个key。
![](asserts/mysql面试题/3.2B树.png)
从上图可以看出来，如果要进行范围查找，B树会比较麻烦，而B+树则比较简单。

B+Tree是在BTree基础上的一种优化，使其更适合实现外存储索引结构，InnoDB存储引擎就是用B+Tree实现其索引结构
![](asserts/mysql面试题/3.3B+树.png)

B树与B+树的区别：  
① 磁盘读写代价B+树更低；  
② 查询效率B+树更加稳定；  
③ B+树便于扫库和区间查询  

> 索引在项目中非常常见，它是一种帮助MySQL高效获取数据的数据结构，主要用来提高数据检索效率，降低数据库的I/O成本。  
> 同时，索引列可以对数据进行排序，降低数据排序的成本，也能减少CPU的消耗。
> 
> MySQL的默认存储引擎InnoDB使用的是B+树作为索引的存储结构。  
> 选择B+树的原因包括：节点可以有更多子节点，路径更短；磁盘读写代价更低，非叶子节点只存储键值和指针，叶子节点存储数据；B+树适合范围查询和扫描，因为叶子节点形成了一个双向链表。
