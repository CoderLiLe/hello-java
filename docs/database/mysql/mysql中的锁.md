<font size=8>mysql中的锁🔒</font>

> 当数据库的并发很高时，可能会出现死锁，要解决死锁问题需要我们对数据库中的锁有很深入的研究。
> 
> 在MySQl中，将锁分为了两类：锁类型(lock_type)和锁模式(lock_mode)
> 
> 锁类型描述的锁的粒度，也就是把锁具体加在什么地方；而锁模式描述的时到底加的是什么锁，是读锁还是写锁。
> 
> 锁模式通常和锁类型结合使用。

<font size=6>按锁的模式分</font>
## 读锁
读锁，又叫共享锁/S锁/share locks。

读锁是某个事务（比如事务A）在进行读取操作（比如读一张表或者读取某一行）时创建出来的锁，其他的事务可以并发地读取这些数据（被加了锁的），但是不能修改这些数据（除非持有锁的用户已经释放锁）。

事务A对数据加上读锁之后，其他事务依然可以对其添加读锁（共享），但是不能添加写锁。
### 在记录上加锁
InnoDB支持表锁和行锁，在行（也就是记录）上加锁，并不是锁住该条记录，而是在记录对应的索引上加锁。如果where条件中不走索引，则会对所有的记录加锁。

显式加锁语句为：
```sql
select * from {tableName} where {condition} lock in share mode;
```
这里所说的读，是指当前读，快照读是无需加锁的。普通select读一般都是快照读，除了select...lock in share mode这样的显式加锁语句下会变成当前读，在InnoDB引擎的serializable级别下，普通select读也会变成快照读。

另外需要注意，对于行锁的加锁过程分析，要根据事务隔离级别、是否使用索引（哪种类型的索引）、记录是否存在等因素结合分析，才能判断在哪里加上了锁。

innodb引擎中的加读锁的几种情形：

| 场景 | 描述 |
| --- | --- |
| 普通查询（Serializable隔离级别） | 给记录加S锁；非事务读（auto-commit）无需加锁。唯一等值查询在记录上加S锁，非唯一条件查询在记录本身及间隙加S锁。|
| `select … in share mode` | 根据隔离级别不同行为有所区别：<br>RC：在记录上加S锁。<br>RR/Serializable：唯一等值查询在记录上加S锁，非唯一条件查询在记录及其间隙加S锁。|
| `insert`操作 | 通常不加锁，但在插入或更新时遇到duplicate key会加S锁；类似`replace into`或`insert … on duplicate`语句加X锁。|
| `insert … select` | 对`select`的表上扫描到的数据加S锁。|
| 外键检查 | 删除父表记录时，扫描子表对应记录并加S锁。|

### 在表上加锁
表锁由 MySQL服务器实现，无论存储引擎是什么，都可以使用表锁。  
一般在执行 DDL 语句时，譬如 ALTER TABLE 时就会对整个表进行加锁。  
在执行 SQL 语句时，也可以明确对某个表加锁。 给表显式加锁语句为：
```sql
# 加表读锁
lock table {tablename} read;
  
# 释放表锁
unlock tables;
  
# 查看表锁
show open table;
```

MYISAM引擎时，通常我们不需要手动加锁，因为MYISAM引擎会针对我们的sql语句自动进行加锁，整个过程不需要用户干预：
- 查询语句（select）：会自动给涉及的表加读锁；
- 更新语句（update、delete、insert）：会自动给涉及的表加写锁。

## 写锁
写锁，排他锁/X锁/exclusive locks。  
写锁的阻塞性比读锁要严格的多，一个事务对数据添加写锁之后，其他的事务对该数据，既不能读取也不能更改。

与读锁加锁的范围相同，写锁既可以加在记录上，也可以加在表上。

### 在记录上加写锁
在记录上加写锁，引擎需要使用InnoDB。 通常普通的select语句是不会加锁的（隔离级别为Serializable除外），想要在查询时添加排他锁需要使用以下语句： 
- 查询时加写锁：
```sql
select * from {tableName} where {condition} for update;
```
- 更新时加写锁：
```sql
insert/update/delete语句，会自动在该记录上加排它锁
```

### 在表上加写锁
显示给表加写锁的语句为：
```sql
# 加表写锁
lock table {tableName} write;
  
# 释放表读锁
unlock tables;
```

> 当引擎选择myisam时，insert/update/delete语句，会自动给该表加上排他锁

### 读写锁兼容性
- 读锁是共享的，它不会阻塞其他读锁，但会阻塞其他的写锁；
- 写锁是排他的，它会阻塞其他读锁和写锁；
- 总结：<font color=red>读读不互斥，读写互斥，写写互斥</font>

## 意向锁
## 自增锁

<font size=6>按锁的类型分</font>
## 全局锁
## 元数据锁
## 页级锁
## 行锁