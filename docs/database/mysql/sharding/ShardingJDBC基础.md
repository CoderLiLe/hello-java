[TOC]

# 一、MySQL高可用集群介绍

## 1、数据库主从架构与分库分表

随着现在互联网的应用越来越大，数据库会频繁的成为整个应用的性能瓶颈。而我们经常使用的MySQL数据库，也会不断面临数据量太大、数据访问太频繁、数据读写速度太快等一系列的问题。所以，我们需要设计复杂的应用架构来保护孱弱的数据库，例如添加Redis缓存，增加MQ进行流量削峰等等。但是，数据库本身如果不能得到提升，这就相当于是水桶理论中的最短板。

而要提升数据库的性能，一种思路，当然是对数据库本身进行优化，例如对MySQL进行优化配置，或者干脆换成ClickHouse这一类的针对大数据的产品。另一方面就是跟微服务架构的思路一样，从单体架构升级到集群架构，这样才能真正全方位解放数据库的性能瓶颈。而我们后续要学习的分库分表就是一种非常常见的数据库集群架构管理方案。

但是就像微服务架构并不是简单的将服务从单机升级为就能一样，分库分表也并不只是字面意义上的将数据分到多个库或者多个表这么简单，他也是基于数据库产品的一系列分布式解决方案。在不同的应用场景下，针对不同的数据库产品，分库分表也有不同的落地方式。而我们后续，会以最为常见的MySQL数据库以及ShardingSphere框架来了解分库分表要如何进行。

## 2、MySQL主从同步原理

既然要解决MySQL数据库的分布式集群化问题，那就不能不先了解MySQL自身提供的主从同步原理。这是构建MySQL集群的基础，也是后续进行分库分表的基础，更是MySQL进行生产环境部署的基础。

其实数据库的主从同步，就是为了要保证多个数据库之间的数据保持一致。最简单的方式就是使用数据库的导入导出工具，定时将主库的数据导出，再导入到从库当中。这是一种很常见，也很简单易行的数据库集群方式。也有很多的工具帮助我们来做这些事情。但是这种方式进行数据同步的实时性比较差。

而如果要保证数据能够实时同步，对于MySQL，通常就要用到他自身提供的一套通过Binlog日志在多个MySQL服务之间进行同步的集群方案。基于这种集群方案，一方面可以提高数据的安全性，另外也可以以此为基础，提供读写分离、故障转移等其他高级的功能。

![](./asserts/1.1.png)

即在主库上打开Binlog日志，记录对数据的每一步操作。然后在从库上打开RelayLog日志，用来记录跟主库一样的Binlog日志，并将RelayLog中的操作日志在自己数据库中进行重演。这样就能够更加实时的保证主库与从库的数据一致。

> MySQL的Binlog默认是不打开的。

他的实现过程是在从库上启动一系列IO线程，负责与主库建立TCP连接，请求主库在写入Binlog日志时，也往从库传输一份。这时，主库上会有一个IO Dump线程，负责将Binlog日志通过这些TCP连接传输给从库的IO线程。而从库为了保证日志接收的稳定性，并不会立即重演Binlog数据操作，而是先将接收到的Binlog日志写入到自己的RelayLog日志当中。然后再异步的重演RelayLog中的数据操作。

MySQL的BinLog日志能够比较实时的记录主库上的所有日志操作，因此他也被很多其他工具用来实时监控MySQL的数据变化。例如Canal框架，可以模拟一个slave节点，同步MySQL的Binlog，然后将具体的数据操作按照定制的逻辑进行转发。例如转发到Redis实现缓存一致，转发到Kafka实现数据实时流转等。而ClickHouse也支持将自己模拟成一个MySQL的从节点，接收MySQL的Binlog日志，实时同步MySQL的数据。`这个功能目前还在实验阶段。`

# 二、动手搭建MySQL主从集群

## 1、基础环境搭建

以下实验准备两台服务器，来搭建一个MySQL的主从集群。均安装CentOS7操作系统。 192.168.232.128将作为MySQL主节点，192.168.232.129将作为MySQL的从节点。

然后在两台服务器上均安装MySQL服务，MySQL版本采用mysql-8.0.20版本。

## 2、安装MySQL服务

### 1、初始化MySQL

MySQL的安装有很多种方式，具体可以参考官网手册：<https://dev.mysql.com/doc/refman/8.0/en/binary-installation.html>

我们这里采用对系统环境依赖最低，出问题的可能性最小的tar包方式来安装。

上传mysql压缩包到worker2机器的root用户工作目录/root下，然后按照下面的指令，解压安装mysql

```shell
groupadd mysql
useradd -r -g mysql -s /bin/false mysql  #这里是创建一个mysql用户用于承载mysql服务，但是不需要登录权限。
tar -zxvf mysql-8.0.20-el7-x86_64.tar.gz #解压
ln -s mysql-8.0.20-el7-x86_64 mysql #建立软链接
cd mysql
mkdir mysql-files
chown mysql:mysql mysql-files
chmod 750 mysql-files
bin/mysqld --initialize --user=mysql #初始化mysql数据文件 注意点1
bin/mysql_ssl_rsa_setup
bin/mysqld_safe --user=mysql 

cp support-files/mysql.server /etc/init.d/mysql.server
```

> **注意点：**
>
> 1、初始化过程中会初始化一些mysql的数据文件，经常会出现一些文件或者文件夹权限不足的问题。如果有文件权限不足的问题，需要根据他的报错信息，创建对应的文件或者文件夹，并配置对应的文件权限。
>
> 2、初始化过程如果正常完成，日志中会打印出一个root用户的默认密码。这个密码需要记录下来。
>
>     2025-04-30T020:05:28.948043Z 6 [Note] [MY-010454] [Server] A temporary password is generated for root@localhost: P6kigsT6Lg>=

### 2、启动mysql

```shell
bin/mysqld --user=mysql
```

> **注意点：**
>
> 1、这个启动过程会独占当前命令行窗口，如果要后台执行可以在后面添加一个 &。但是一般第一次启动mysql服务时，经常会出现一些错误，所以建议用独占窗口的模式跟踪下日志。
>
> Linux上安装软件经常会出现各种各样的环境问题，很难全部概括。大部分的问题，需要查百度，根据别人的经验来修改。如果安装有困难的同学，可以改为在Windows上安装MySQL，整个过程会简单很多，不会影响后续ShardingSpehre的学习。

### 3、连接MySQL

MySQL服务启动完成后，默认是只能从本机登录，远程是无法访问的。所以需要用root用户登录下，配置远程访问的权限。

```shell
cd /root/mysql
bin/mysql -uroot -p #然后用之前记录的默认密码登录
```

> **注意点：**
>
> 1、如果有同学遇到  **ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/tmp/mysql.sock' (2)**  这个报错信息，可以参照下面的配置，修改下/etc/my.cnf配置文件，来配置下socket连接文件的地址。主要是下面client部分。
>
>     [mysqld]
>     datadir=/var/lib/mysql
>     socket=/var/lib/mysql/mysql.sock
>     user=mysql
>     # Disabling symbolic-links is recommended to prevent assorted security risks
>     symbolic-links=0
>     # Settings user and group are ignored when systemd is used.
>     # If you need to run mysqld under a different user or group,
>     # customize your systemd unit file for mariadb according to the
>     # instructions in http://fedoraproject.org/wiki/Systemd
>
>     [mysqld_safe]
>     log-error=/var/log/mariadb/mariadb.log
>     pid-file=/var/run/mariadb/mariadb.pid
>
>     #
>     # include all files from the config directory
>     #
>     !includedir /etc/my.cnf.d
>
>     [client]
>     port=3306
>     socket=/var/lib/mysql/mysql.sock

登录进去后，需要配置远程登录权限：

```sql
alter user 'root'@'localhost' identified by '123456'; #修改root用户的密码
use mysql;
update user set host='%' where user='root';
flush privileges;
```

这样，Linux机器上的MySQL服务就搭建完成了。可以使用navicat等连接工具远程访问MySQL服务了。

> 如果安装MySQL确实有问题的话，推荐使用宝塔面板。<https://www.bt.cn/> 。使用这个工具可以图形化安装以及管理MySQL，非常方便。
>
> 另外，对于熟悉Docker和K8s，可以用这些虚拟化的方式来搭建，也非常简单高效。

这里需要注意下的是，搭建主从集群的多个服务，有两个必要的条件。

1、MySQL版本必须一致。

2、集群中各个服务器的时间需要同步。

## 3、搭建主从集群

接下来在这两个MySQL服务基础上，搭建一个主从集群。

### 1、配置master主服务

首先，配置主节点的mysql配置文件： /etc/my.cnf(没有的话就手动创建一个)

这一步需要对master进行配置，主要是需要打开binlog日志，以及指定severId。我们打开MySQL主服务的my.cnf文件，在文件中一行server-id以及一个关闭域名解析的配置。然后重启服务。

```ini
[mysqld]
server-id=01
#开启binlog
log_bin=master-bin
log_bin-index=master-bin.index
skip-name-resolve
# 设置连接端口
port=3306
# 设置mysql的安装目录
basedir=/usr/local/mysql
# 设置mysql数据库的数据的存放目录
datadir=/usr/local/mysql/mysql-files
# 允许最大连接数
max_connections=200
# 允许连接失败的次数。
max_connect_errors=10
# 服务端使用的字符集默认为UTF8
character-set-server=utf8
# 创建新表时将使用的默认存储引擎
default-storage-engine=INNODB
# 默认使用“mysql_native_password”插件认证
#mysql_native_password
default_authentication_plugin=mysql_native_password
```

> 配置说明：主要需要修改的是以下几个属性：
>
> server-id：服务节点的唯一标识。需要给集群中的每个服务分配一个单独的ID。
>
> log\_bin：打开Binlog日志记录，并指定文件名。
>
> log\_bin-index：Binlog日志文件

重启MySQL服务， `service mysqld restart`

然后，我们需要给root用户分配一个replication slave的权限。

```shell
#登录主数据库
mysql -u root -p
GRANT REPLICATION SLAVE ON *.* TO 'root'@'%';
flush privileges;
#查看主节点同步状态：
show master status;
```

> 在实际生产环境中，通常不会直接使用root用户，而会创建一个拥有全部权限的用户来负责主从同步。

![](./asserts/1.2.png)

这个指令结果中的File和Position记录的是当前日志的binlog文件以及文件中的索引。

而后面的Binlog\_Do\_DB和Binlog\_Ignore\_DB这两个字段是表示需要记录binlog文件的库以及不需要记录binlog文件的库。目前我们没有进行配置，就表示是针对全库记录日志。这两个字段如何进行配置，会在后面进行介绍。

> 开启binlog后，数据库中的所有操作都会被记录到datadir当中，以一组轮询文件的方式循环记录。而指令查到的File和Position就是当前日志的文件和位置。而在后面配置从服务时，就需要通过这个File和Position通知从服务从哪个地方开始记录binLog。

![](./asserts/1.3.png)


