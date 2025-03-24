# Synchronized

## 定义

如果某一个资源被多个线程共享，为了避免因为资源抢占导致资源数据错乱，我们需要对线程进行同步，那么synchronized就是实现线程同步的关键字

**synchronized的作用是保证在同一时刻， 被修饰的代码块或方法只会有一个线程执行，以达到保证并发安全的效果。**

## 特性

- **原子性**：所谓原子性就是指一个操作或者多个操作，要么全部执行并且执行的过程不会被任何因素打断，要么就都不执行。
- **可见性**： 可见性是指多个线程访问一个资源时，该资源的状态、值信息等对于其他线程都是可见的。（通过“在执行unlock之前，必须先把此变量同步回主内存”实现）
- **有序性**：有效解决重排序问题（通过“一个变量在同一时刻只允许一条线程对其进行lock操作”）

## 用法

从语法上讲，Synchronized可以把任何一个非null对象作为"锁"，在HotSpot JVM实现中，锁有个专门的名字：**对象监视器（Object Monitor）**。

三种用法：

（1）修饰静态方法
```java
public synchronized static void helloStatic(){
    System.out.println("hello world static");
}
```

（2）修饰成员函数

```java
public synchronized void hello(){
    System.out.println("hello world");
}
```

（3）直接定义代码块

```java
public void test(){
    SynchronizedTest test = new SynchronizedTest();        
    synchronized (test){
        System.out.println("hello world");
    }
}
```