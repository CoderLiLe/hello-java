# 高性能队列 Disruptor

## 1. Disruptor 概述

Disruptor 是 LMAX 公司开发的高性能无锁队列框架，是交易平台的核心组件。

### 1.1 核心优势
- 无锁设计（CAS + 内存屏障）
- 无伪共享（缓存行填充）
- 预分配内存（零 GC）
- 高效的消费者依赖图

### 1.2 性能对比
| 特性 | Disruptor | JDK BlockingQueue |
|------|-----------|-------------------|
| 锁 | 无锁 | ReentrantLock |
| GC | 零/低 | 高 |
| 延迟 | 纳秒级 | 微秒级 |
| TPS | 千万级 | 百万级 |

## 2. 核心概念

### 2.1 Ring Buffer
- 环形数组，预分配固定大小
- 序号递增，取模定位
- 避免内存分配和 GC

### 2.2 Sequence
- 序号跟踪（生产者/消费者）
- 使用 volatile + CAS
- 缓存行填充防止伪共享

### 2.3 Sequence Barrier
- 协调生产者和消费者的进度
- 决定消费者能读取哪些数据

### 2.4 Event Processor
- 处理事件的循环
- 从 Ring Buffer 读取事件

### 2.5 Event Handler
- 业务处理逻辑

### 2.6 Producer
- 写入事件到 Ring Buffer

## 3. 快速使用

### 3.1 事件定义
```java
public class OrderEvent {
    private long orderId;
    private double price;
    // getter / setter
}
```

### 3.2 事件处理器
```java
public class OrderHandler implements EventHandler<OrderEvent> {
    @Override
    public void onEvent(OrderEvent event, long sequence, boolean endOfBatch) {
        // 处理订单
        System.out.println("Process order: " + event.getOrderId());
    }
}
```

### 3.3 事件工厂
```java
public class OrderEventFactory implements EventFactory<OrderEvent> {
    @Override
    public OrderEvent newInstance() {
        return new OrderEvent();
    }
}
```

### 3.4 生产者
```java
public class OrderProducer {
    private final RingBuffer<OrderEvent> ringBuffer;
    
    public OrderProducer(RingBuffer<OrderEvent> ringBuffer) {
        this.ringBuffer = ringBuffer;
    }
    
    public void onData(long orderId, double price) {
        long sequence = ringBuffer.next();
        try {
            OrderEvent event = ringBuffer.get(sequence);
            event.setOrderId(orderId);
            event.setPrice(price);
        } finally {
            ringBuffer.publish(sequence);
        }
    }
}
```

### 3.5 组装使用
```java
// 创建 Disruptor
Disruptor<OrderEvent> disruptor = new Disruptor<>(
    new OrderEventFactory(),
    1024,                          // Ring Buffer 大小
    Executors.defaultThreadFactory(),
    ProducerType.SINGLE,           // 单生产者
    new YieldingWaitStrategy()      // 等待策略
);

// 连接处理器
disruptor.handleEventsWith(new OrderHandler());

// 启动
RingBuffer<OrderEvent> ringBuffer = disruptor.start();

// 生产
OrderProducer producer = new OrderProducer(ringBuffer);
producer.onData(1L, 99.9);

// 关闭
disruptor.shutdown();
```

## 4. 等待策略

| 策略 | 说明 | 适用 |
|------|------|------|
| BlockingWaitStrategy | 锁+条件变量 | CPU 资源优先 |
| SleepingWaitStrategy | 循环+CAS+自旋 | 延迟要求一般 |
| YieldingWaitStrategy | 自旋+yield | 高吞吐 |
| BusySpinWaitStrategy | 死循环 | 极致低延迟 |
| PhasedBackoffWaitStrategy | 混合策略 | 综合平衡 |

## 5. 消费者依赖图

```java
// 串行处理
disruptor.handleEventsWith(new HandlerA())
          .then(new HandlerB());

// 并行处理
disruptor.handleEventsWith(new HandlerA(), new HandlerB());

// 菱形依赖
disruptor.handleEventsWith(new HandlerA(), new HandlerB())
          .then(new HandlerC());

// 链式依赖
disruptor.handleEventsWith(new HandlerA());
disruptor.after(new HandlerA()).handleEventsWith(new HandlerB());
```

## 6. 多生产者

```java
Disruptor<OrderEvent> disruptor = new Disruptor<>(
    factory,
    1024,
    threadFactory,
    ProducerType.MULTI,  // 多生产者
    waitStrategy
);
```

## 7. 最佳实践

- **Ring Buffer 大小**：2 的幂次方
- **避免长时间阻塞**：Handler 中不要做阻塞操作
- **事件复用**：利用预分配，避免创建新对象
- **缓存行填充**：使用 @Contended 或手动填充
- **批量处理**：利用 endOfBatch 参数
- **异常处理**：实现 ExceptionHandler 接口

```java
// 异常处理器
disruptor.handleExceptionsFor(new ExceptionHandler<OrderEvent>() {
    @Override
    public void handleEventException(Throwable ex, long sequence, OrderEvent event) {
        log.error("处理异常", ex);
    }
    @Override
    public void handleOnStartException(Throwable ex) {}
    @Override
    public void handleOnShutdownException(Throwable ex) {}
});
```
