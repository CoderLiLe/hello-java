
# 一、ShardingProxy快速使用

ShardingProxy的功能同样是分库分表，但是他是一个独立部署的服务端，提供统一的数据库代理服务。注意，ShardingProxy目前只支持MySQL和PostgreSQL。并且，客户端连接ShardingProxy时，最好使用MySQL的JDBC客户端。下面我们来部署一个ShardingProxy服务。

## 1、ShardingProxy部署

ShardingProxy在windows和Linux上提供了一套统一的部署发布包。我们可以从ShardingSphere官网下载4.1.1版本的ShardingProxy发布包apache-shardingsphere-4.1.1-sharding-proxy-bin.tar.gz，解压到本地目录。`配套资料中已经提供`

> 注意不要有中文路径

首先，我们需要把MySQL的JDBC驱动包mysql-connector-java-8.0.20.jar手动复制到ShardingProxy的lib目录下。ShardingProxy默认只附带了PostgreSQL的JDBC驱动包，而不包含MySQL的JDBC驱动包。

然后，我们需要到conf目录下，修改server.yaml，将配置文件中的authentication和props两段配置的注释打开。

```yaml
authentication:
  users:
    root:
      password: root
    sharding:
      password: sharding 
      authorizedSchemas: sharding_db

props:
  max.connections.size.per.query: 1
  acceptor.size: 16  # The default value is available processors count * 2.
  executor.size: 16  # Infinite by default.
  proxy.frontend.flush.threshold: 128  # The default value is 128.
    # LOCAL: Proxy will run with LOCAL transaction.
    # XA: Proxy will run with XA transaction.
    # BASE: Proxy will run with B.A.S.E transaction.
  proxy.transaction.type: LOCAL
  proxy.opentracing.enabled: false
  proxy.hint.enabled: false
  query.with.cipher.column: true
  sql.show: false
  allow.range.query.with.inline.sharding: false
```

然后，我们修改conf目录下的config-sharding.yaml，这个配置文件就是shardingProxy关于分库分表部分的配置。整个配置和之前我们使用ShardingJDBC时的配置大致相同，我们在最下面按照自己的数据库环境增加以下配置：

```yaml
schemaName: sharding_db

dataSources:
  m1:
    url: jdbc:mysql://localhost:3306/userdb?serverTimezone=GMT%2B8&useSSL=false
    username: root
    password: root
    connectionTimeoutMilliseconds: 30000
    idleTimeoutMilliseconds: 60000
    maxLifetimeMilliseconds: 1800000
    maxPoolSize: 50

shardingRule:
  tables:
    course:
      actualDataNodes: m1.course_$->{1..2}
      tableStrategy:
        inline:
          shardingColumn: cid
          algorithmExpression: course_$->{cid%2+1}
      keyGenerator:
        type: SNOWFLAKE
        column: cid
```

> 这一段就是按照我们之前的application01.properties文件中的规则配置的。可以看到，整个配置其实是大同小异的。

然后，还一个小问题要注意，我们进入ShardingProxy的Lib目录，里面会有些jar包因为名字太长了，导致有些文件的后缀被截断了，我们要手动把他们的文件后缀给修改过来。



然后，我们就可以启动ShardingProxy的服务了。启动脚本在bin目录下。其中，windows平台对应的脚本是start.bat，Linux平台对应的脚本是start.sh和stop.sh

启动时，我们可以直接运行start.bat脚本，这时候，ShardingProxy默认占用的是3307端口。为了不跟我们之前搭建的多个MySQL服务端口冲突，我们定制下启动端口，改为3316端口。

```shell
start.bat 3316
```

> 为什么windows平台上没有stop.bat呢？因为start.bat会独占一个命令行窗口，把命令行窗口关闭，就停止了ShardingProxy的服务。

启动完成后，可以看到几行关键的日志标识服务启动成功了。

    [INFO ] 20:46:53.930 [main] c.a.d.xa.XATransactionalResource - resource-1-m1: refreshed XAResource
    [INFO ] 20:46:54.580 [main] ShardingSphere-metadata - Loading 1 logic tables' meta data.
    [INFO ] 20:46:54.717 [main] ShardingSphere-metadata - Loading 8 tables' meta data.
    [INFO ] 20:46:56.953 [nioEventLoopGroup-2-1] i.n.handler.logging.LoggingHandler - [id: 0xc90e0eef] REGISTERED
    [INFO ] 20:46:56.958 [nioEventLoopGroup-2-1] i.n.handler.logging.LoggingHandler - [id: 0xc90e0eef] BIND: 0.0.0.0/0.0.0.0:3316
    [INFO ] 20:46:56.960 [nioEventLoopGroup-2-1] i.n.handler.logging.LoggingHandler - [id: 0xc90e0eef, L:/0:0:0:0:0:0:0:0:3316] ACTIVE

## 2、ShardingProxy使用

这样，我们就可以像连接一个标准MySQL服务一样连接ShardingProxy了。

    D:\dev-hook\mysql-8.0.20-winx64\bin>mysql.exe -P3316 -uroot -p
    Enter password: ****
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    Your MySQL connection id is 1
    Server version: 8.0.20-Sharding-Proxy 4.1.0

    Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

    Oracle is a registered trademark of Oracle Corporation and/or its
    affiliates. Other names may be trademarks of their respective
    owners.

    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

    mysql> show databases;
    +-------------+
    | Database    |
    +-------------+
    | sharding_db |
    +-------------+
    1 row in set (0.03 sec)

    mysql> use sharding_db
    Database changed
    mysql> show tables;
    +--------------------+
    | Tables_in_coursedb |
    +--------------------+
    | course             |
    | t_dict             |
    +--------------------+
    2 rows in set (0.16 sec)

    mysql> select * from course;
    +--------------------+-------+---------+---------+
    | cid                | cname | user_id | cstatus |
    +--------------------+-------+---------+---------+
    | 545730330389118976 | java  |    1001 | 1       |
    | 545730330804355072 | java  |    1001 | 1       |
    | 545730330842103808 | java  |    1001 | 1       |
    | 545730330879852544 | java  |    1001 | 1       |
    | 545730330917601280 | java  |    1001 | 1       |
    +--------------------+-------+---------+---------+
    5 rows in set (0.08 sec)

> 之前在ShardingJDBC部分完成了的其他几种分库分表策略以及读写分离策略，就请大家自行验证了。

