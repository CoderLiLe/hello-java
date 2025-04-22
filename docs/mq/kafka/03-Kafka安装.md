# 03-Kafka安装

## 一、安装

### 1、上传

上传到/opt目录下：

- jdk-8u121-linux-x64.tar.gz
- kafka_2.13-3.6.0.tgz



### 2、解压JDK

```shell
cd /opt
tar -zxvf jdk-8u121-linux-x64.tar.gz
tar -zxvf kafka_2.13-3.6.0.tgz
```



### 3、配置环境变量

```shell
cd /etc
cp profile profile.bak
vim /etc/profile
```



在文件最后增加配置环境变量的内容：

```shell
JAVA_HOME=/opt/jdk1.8.0_121
KAFKA_HOME=/opt/kafka_2.13-3.6.0
PATH=$JAVA_HOME/bin:$KAFKA_HOME/bin:$PATH
export JAVA_HOME KAFKA_HOME PATH
```



### 4、激活

```shell
source /etc/profile
```



### 5、测试

查看Kafka版本：

```shell
kafka-topics.sh -version
```



## 二、配置

### 1、打开配置文件

```shell
cd /opt/kafka_2.13-3.6.0/config/
cp server.properties server.properties.bak
vim /opt/kafka_2.13-3.6.0/config/server.properties
```



### 2、修改配置项

#### ①外部访问地址

```properties
listeners=PLAINTEXT://192.168.200.100:9092
```



#### ②内部广播地址

```properties
advertised.listeners=PLAINTEXT://192.168.200.100:9092
```



#### ③Zookeeper访问地址

```properties
zookeeper.connect=localhost:2181
```

或

```properties
zookeeper.connect=192.168.200.100:2181
```



## 三、启动

### 1、启动Zookeeper

#### ①前台启动

```shell
zookeeper-server-start.sh /opt/kafka_2.13-3.6.0/config/zookeeper.properties
```



#### ②后台启动

```shell
zookeeper-server-start.sh -daemon /opt/kafka_2.13-3.6.0/config/zookeeper.properties
```



### 2、启动Kafka

#### ①前台启动

```shell
kafka-server-start.sh /opt/kafka_2.13-3.6.0/config/server.properties
```



#### ②后台启动

```shell
kafka-server-start.sh -daemon /opt/kafka_2.13-3.6.0/config/server.properties
```



### 3、停止

#### ①停止Zookeeper

```shell
zookeeper-server-stop.sh
```



#### ②停止Kafka

```shell
kafka-server-stop.sh
```



### 4、验证

```shell
lsof -i:9092
lsof -i:2181
```

