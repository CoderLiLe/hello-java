# 06-客户端原生API

## 一、生产者

### 1、创建主题

```shell
kafka-topics.sh --bootstrap-server 192.168.200.100:9092 --create --topic topic-java-client
```



### 2、启动消费者监听主题

```shell
kafka-console-consumer.sh --bootstrap-server 192.168.200.100:9092 --topic topic-java-client
```



### 3、引入依赖

```xml
<!-- kafka-clients 2023.10-->
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.6.0</version>
</dependency>
```



### 4、Java程序

```java
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.util.Properties;

public class MyProducerDemo{
    public static final String TOPIC_NAME = "topic-java-client";

    public static void main(String[] args) {
        // 1. 创建Kafka生产者的配置对象
        Properties properties = new Properties();
        
        // 2. 给Kafka配置对象添加配置信息：bootstrap.servers
        properties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "192.168.200.100:9092");
        
        // key,value序列化（必须）：key.serializer，value.serializer
        properties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer");
        
        properties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer");
        
        // 3. 创建Kafka生产者对象
        KafkaProducer kafkaProducer = new KafkaProducer(properties);
        
        // 4. 调用send方法,发送消息
        for (int i = 0; i < 5; i++) {
            kafkaProducer.send(new ProducerRecord<>(TOPIC_NAME, "hello-kafka-from-java-client~" + i));
        }
        
        System.out.println("----MyProducerDemo发送完毕");
        // 5. 关闭资源
        kafkaProducer.close();
    }
}
```



ProducerRecord参数说明：

```java
public class ProducerRecord<K, V> {
    //主题名称，必选参数
    private final String topic;
    
    //分区号，大于等于0的整数，可选参数。
    private final Integer partition;
    
    //消息的头信息，类型是RecordHeaders，可选属性。
    private final Headers headers;
    
    //键，可选参数。
    private final K key;
    
    //消息内容，必选参数。
    private final V value;
    
    //每条消息都有一个时间戳，可选参数
    private final Long timestamp;
}
```



### 5、send()方法返回值

KafkaProducer的send()方法返回Future类型的对象，可以调用Future的get()方法同步获取任务执行结果。

此时程序就成了前一个消息发送完成再发送后一个的同步模式。

也就是说不调用get()方法就是异步模式。

```java
// 同步
for (int i = 0; i < 5; i++) {
    // 发送消息的任务交给子线程去做
    Future future = kafkaProducer.send(new ProducerRecord<>(TOPIC_NAME, "hello-kafka-from-java-client~~~" + i));

    TimeUnit.SECONDS.sleep(1);

    // 但是因为调用了 get() 方法，就变成子线程必须执行完发送消息的任务
    // for 循环的本次循环体才算执行完，才能继续执行下一次循环
    // 下一次循环就是发送下一条消息
    future.get();
}
```





### 6、获取消息发送结果

给KafkaProducer的send()方法再传入一个CallBack类型的参数，以异步回调的方式获取消息发送结果，从而得知消息发送是成功还是失败。



#### ①Java代码

```java
kafkaProducer.send(new ProducerRecord<>(TOPIC_NAME, "hello-kafka-from-java-client*******"), new Callback() {

    // onCompletion() 方法在发送消息操作完成时被调用
    // 参数 RecordMetadata recordMetadata：发送消息相关的元数据
    // 参数 Exception e：发送消息失败时，失败原因封装的异常信息
    @Override
    public void onCompletion(RecordMetadata recordMetadata, Exception e) {

        if (e == null) {
            long offset = recordMetadata.offset();
            System.out.println("offset = " + offset);

            int partition = recordMetadata.partition();
            System.out.println("partition = " + partition);

            long timestamp = recordMetadata.timestamp();
            System.out.println("timestamp = " + timestamp);

            String topic = recordMetadata.topic();
            System.out.println("topic = " + topic);

        } else {
            System.out.println("e = " + e);
        }
    }
});
```



#### ②失败情况举例

把broker地址改成错的：

> e = org.apache.kafka.common.errors.TimeoutException: Topic topic-java-client not present in metadata after 60000 ms.



## 二、消费者

```java
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

import java.time.Duration;
import java.util.Arrays;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

public class MyConsumerDemo {
    public static final String TOPIC_NAME = "topic-java-client";
    public static void main(String[] args) throws InterruptedException {
        // 1、创建Kafka消费者的配置对象
        Properties properties = new Properties();
        
		// 2、给Kafka配置对象添加配置信息：bootstrap.servers
        properties.put("bootstrap.servers", "192.168.200.100:9092");
        properties.setProperty("group.id", "test");
        properties.setProperty("enable.auto.commit", "true");
        properties.setProperty("auto.commit.interval.ms", "1000");
        properties.setProperty("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        properties.setProperty("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");

        // 3、创建消费者对象
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(properties);
        
        // 4、订阅指定主题
        consumer.subscribe(Arrays.asList(TOPIC_NAME));

        while (true) {
            // 5、从broker拉取信息
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records)
                System.out.printf("offset = %d, key = %s, value = %s%n", record.offset(), record.key(), record.value());
            
            // 6、每隔 1 秒做一次打印，让消费端程序持续运行
            TimeUnit.SECONDS.sleep(1);
            System.out.println("....进行中");
        }
    }
}
```

