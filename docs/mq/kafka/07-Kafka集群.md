# 07-Kafka集群

## 一、集群搭建

### 1、重要原则

- Kafka节点只要注册到同一个Zookeeper上就代表它们是同一个集群的
- Kafka通过broker.id来区分集群中的不同节点



### 2、规划

- 简单起见，我们只使用一个VMWare虚拟机，所以各个broker实例需要设定不同端口号
- Kafka程序不需要复制，对应各自不同的配置文件启动多个进程就能组成集群
- Zookeeper还是使用原来的2181即可



| &nbsp; | 端口号 | 配置文件                             | 日志目录               |
| ------ | ------ | ------------------------------------ | ---------------------- |
| 实例01 | 7000   | /opt/k-cluster/server7000.properties | /opt/k-cluster/log7000 |
| 实例02 | 8000   | /opt/k-cluster/server8000.properties | /opt/k-cluster/log8000 |
| 实例03 | 9000   | /opt/k-cluster/server9000.properties | /opt/k-cluster/log9000 |


### 3、具体操作

#### ①创建目录

```shell
mkdir -p /opt/k-cluster/log7000
mkdir -p /opt/k-cluster/log8000
mkdir -p /opt/k-cluster/log9000
```



#### ②复制配置文件

```shell
cp /opt/kafka_2.13-3.6.0/config/server.properties /opt/k-cluster/server7000.properties
cp /opt/kafka_2.13-3.6.0/config/server.properties /opt/k-cluster/server8000.properties
cp /opt/kafka_2.13-3.6.0/config/server.properties /opt/k-cluster/server9000.properties
```



#### ③修改配置文件

##### [1]7000

```properties
broker.id=1
listeners=PLAINTEXT://192.168.200.100:7000
advertised.listeners=PLAINTEXT://192.168.200.100:7000
log.dirs=/opt/k-cluster/log7000
```



##### [2]8000

```properties
broker.id=2
listeners=PLAINTEXT://192.168.200.100:8000
advertised.listeners=PLAINTEXT://192.168.200.100:8000
log.dirs=/opt/k-cluster/log8000
```



##### [3]9000

```shell
broker.id=3
listeners=PLAINTEXT://192.168.200.100:9000
advertised.listeners=PLAINTEXT://192.168.200.100:9000
log.dirs=/opt/k-cluster/log9000
```



### 4、启动集群各实例

注意：此前需要先启动Zookeeper

```shell
kafka-server-start.sh -daemon /opt/k-cluster/server7000.properties
kafka-server-start.sh -daemon /opt/k-cluster/server8000.properties
kafka-server-start.sh -daemon /opt/k-cluster/server9000.properties
```



验证各个端口号：

```shell
lsof -i:2181
lsof -i:7000
lsof -i:8000
lsof -i:9000
```



如果因为内存不足而启动失败，可以修改对应启动脚本程序中的内存大小：

- Zookeeper启动脚本程序：zookeeper-server-start.sh
- Zookeeper中Kafka堆内存大小变量名称：KAFKA_HEAP_OPTS
- Kafka启动脚本程序：kafka-server-start.sh
- Kafka堆内存大小变量名称：KAFKA_HEAP_OPTS



### 5、停止集群

```shell
# 停止Kafka，无需指定端口号就能停止各个实例：
kafka-server-stop.sh
# 停止zk
zookeeper-server-stop.sh
```



## 二、使用集群

### 1、在集群上创建主题

```shell
kafka-topics.sh \
--bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000 \
--create \
--partitions 3 \
--replication-factor 3 \
--topic my-cluster-topic
```



### 2、查看集群主题

```shell
kafka-topics.sh \
--bootstrap-server 192.168.200.100:7000 \
--describe --topic my-cluster-topic
```

![image-20231121164358865](assets/image-20231121164358865.png)



### 3、集群消息发送

```shell
kafka-console-producer.sh \
--bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000 \
--topic my-cluster-topic
```



### 4、集群消息消费

```shell
kafka-console-consumer.sh \
--bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000  \
--from-beginning \
--topic my-cluster-topic
```



### 5、集群消息消费相关问题

#### ①问题描述

通过集群接收消息时，接收不到



#### ②问题产生原因

多个broker实例部署在同一个虚拟机上

- 192.168.200.100:7000
- 192.168.200.100:8000
- 192.168.200.100:9000



这只是我们在测试环境下，非正式的这么安排，实际开发中不会把集群的所有实例放在一个机器上



#### ③问题解决方案一

消费端接收消息时指定分区

```shell
kafka-console-consumer.sh \
--bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000  \
--from-beginning \
--partition 0 \
--topic my-cluster-topic

kafka-console-consumer.sh \
--bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000  \
--from-beginning \
--partition 1 \
--topic my-cluster-topic

kafka-console-consumer.sh \
--bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000  \
--from-beginning \
--partition 2 \
--topic my-cluster-topic
```



#### ④问题解决方案二

登录到Zookeeper服务器上，删除__consumer_offsets主题

- 第一步：把apache-zookeeper-3.9.1-bin.tar.gz上传到Linux系统/opt目录下
- 第二步：解压apache-zookeeper-3.9.1-bin.tar.gz文件

```shell
cd /opt
tar -zxvf apache-zookeeper-3.9.1-bin.tar.gz
```

- 第三步：运行zkCli.sh脚本文件，登录到Zookeeper服务器

```shell
/opt/apache-zookeeper-3.9.1-bin/bin/zkCli.sh
```

- 第四步：删除__consumer_offsets主题

```shell
deleteall /brokers/topics/__consumer_offsets
```

- 第五步：退出Zookeeper

```shell
quit
```

- 第六步：重启
  - 先关闭然后重新启动Zookeeper
  - 先关闭然后重新启动集群各实例
