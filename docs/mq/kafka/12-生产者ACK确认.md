# 12-生产者ACK确认

## 一、提出问题

生产者发送消息到broker，在这个过程中，消息到底有没有发送到broker上？

为了确认消息发送结果，我们需要引入ACK确认机制。

ACK：acknowledge单词的缩写，意思是确认、承认



## 二、应对策略

spring.kafka.producer.acks，可选值如下：

- 0：生产者发送数据后就不管了，不会等待broker的ack，这个延迟最低但是数据一致性的保证最弱。当server挂掉的时候就会丢数据
- 1：默认值，生产者会等待ack值 ，leader确认接收到消息后发送ack，不需要follower确认。但是如果leader挂掉后他不确保消息是否同步到了所有的follower中，新leader也会导致数据丢失，可靠性中等，效率中等。
- -1(all)：生产者会等所有的follower的副本收到数据后才会收到leader发出的ack，也即Leader和ISR队列里面所有Follwer应答，可靠性最高、效率最低



如果没有接收到ack，生产者端会考虑参照retries参数执行重试操作



## 三、YAML配置举例

```yaml
spring:
  kafka:
    bootstrap-servers: 192.168.200.100:7000,192.168.200.100:8000,192.168.200.100:9000
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: -1
```



## 四、应用场景

| 取值         | 场景                                                         |
| ------------ | ------------------------------------------------------------ |
| acks=0       | 几乎不用                                                     |
| acks=1       | 一般用于传输普通日志，允许丢个别数据                         |
| acks=-1(all) | 一般用于传输重要不能丢失的数据(例如：钱、订单、积分等)，对可靠性要求比较高的场景 |

