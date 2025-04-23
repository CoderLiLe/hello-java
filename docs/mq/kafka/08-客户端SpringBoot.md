# 08-客户端SpringBoot

## 一、生产者

### 1、配置POM

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.1.3</version>
    <relativePath/>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
    <!--spring-kafka-->
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
    <!--hutool-->
    <dependency>
        <groupId>cn.hutool</groupId>
        <artifactId>hutool-all</artifactId>
        <version>5.8.19</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                <excludes>
                    <exclude>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                    </exclude>
                </excludes>
            </configuration>
        </plugin>
    </plugins>
</build>
```



### 2、配置YAML

```yaml
spring:
  kafka:
    bootstrap-servers: 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
```



### 3、主启动类

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class KafkaMainTypeProducer {

    public static void main(String[] args) {
        SpringApplication.run(KafkaMainType.class, args);
    }
    
}
```



### 4、配置类创建主题

```java
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaConfig {
    @Bean
    public NewTopic springTestTopic() {
        return TopicBuilder.name("topic-spring-boot") // 主题名称
                .partitions(3) // 分区数量
                .replicas(3) // 复制因子
                .build();
    }
}
```



到这里我们可以运行主启动类，看看主题是否创建成功

```shell
kafka-topics.sh --bootstrap-server 192.168.200.100:7000 --list
```



### 5、发送消息

#### ①命令行监听消息

```shell
kafka-console-consumer.sh --bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000 --topic topic-spring-boot --partition 0

kafka-console-consumer.sh --bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000 --topic topic-spring-boot --partition 1

kafka-console-consumer.sh --bootstrap-server 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000 --topic topic-spring-boot --partition 2
```



#### ②Java代码

```java
import jakarta.annotation.Resource;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.kafka.core.KafkaTemplate;

@SpringBootTest
public class KafkaTest {

    @Resource
    private KafkaTemplate kafkaTemplate;

    @Test
    public void testSendMessage() {

        String topicName = "topic-spring-boot";
        String message = "hello spring boot message";

        kafkaTemplate.send(topicName, message);
    }

}
```



## 二、消费者

### 1、配置POM

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.1.3</version>
    <relativePath/>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
    <!--spring-kafka-->
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
    <!--hutool-->
    <dependency>
        <groupId>cn.hutool</groupId>
        <artifactId>hutool-all</artifactId>
        <version>5.8.19</version>
    </dependency>
</dependencies>

<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                <excludes>
                    <exclude>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                    </exclude>
                </excludes>
            </configuration>
        </plugin>
    </plugins>
</build>
```



### 2、配置YAML

```yaml
spring:
  Kafka:
    bootstrap-servers: 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000
    consumer:
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      group-id: consumer-group
```



### 3、主启动类

```java
package com.atguigu.kafka;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class KafkaMainTypeConsumer {

    public static void main(String[] args) {
        SpringApplication.run(KafkaMainTypeConsumer.class, args);
    }

}
```



### 4、接收消息的监听器

```java
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class KafkaMessageListener {

    @KafkaListener(topics = {"topic-spring-boot"})
    public void simpleConsumerPartition(ConsumerRecord<String, String> record) {
        System.out.println("进入simpleConsumer方法");
        System.out.printf(
                "分区 = %d, 偏移量 = %d, key = %s, 内容 = %s, 时间戳 = %d%n",
                record.partition(),
                record.offset(),
                record.key(),
                record.value(),
                record.timestamp()
        );
    }

}
```



注意：这里我们没有指定具体接收哪个分区的消息，所以如果接收不到消息，那么就需要登录Zookeeper删除__consumer_offsets

```shell
deleteall /brokers/topics/__consumer_offsets
```



## 三、实体类对象类型的消息

### 1、创建实体类

```java
import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class UserDTO {
    private String name;
    private Integer age;
    private String mobile;
}
```



### 2、发送消息的方法

```java
@Test
public void testSendEntity() {
    String topicName = "topic-spring-boot230628";
    UserDTO userDTO = new UserDTO("tom", 25, "12345343");

    kafkaTemplate.send(topicName, userDTO);
}
```



### 3、异常

- 异常全类名：java.lang.ClassCastException
- 异常信息：class com.atguigu.kafka.entity.UserDTO cannot be cast to class java.lang.String (com.atguigu.kafka.entity.UserDTO is in unnamed module of loader 'app'; java.lang.String is in module java.base of loader 'bootstrap')
- 异常原因：目前使用的序列化器是StringSerializer，不支持非字符串序列化
- 解决办法：把序列化器换成支持复杂类型的



### 4、修改YAML配置

```yaml
spring:
  kafka:
    bootstrap-servers: 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      # value-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
```

