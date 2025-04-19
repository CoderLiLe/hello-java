# 一、概述
JUC包下提供了另外一套实现加锁、同步操作的 API：总代表就是java.util.concurrent.locks.Lock接口<br/>
Lock接口最经典的实现类是ReentrantLock

<br/>



# 二、HelloWorld
把卖票的例子用 Lock 系列 API 再重新写一遍：
```java
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Demo01SaleTicket {

    private int ticketStock = 100;

    // 创建锁对象
    private Lock lock = new ReentrantLock();

    public void saleTicket() {

        try {
            // 加锁操作
            lock.lock();

            if (ticketStock > 0) {
                System.out.println(Thread.currentThread().getName() + " 窗口卖了一张票，还剩：" + --ticketStock);
                TimeUnit.MILLISECONDS.sleep(100);
            } else {
                System.out.println(Thread.currentThread().getName() + " 窗口报告：票卖完啦！");
            }
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            // 放在 finally 块中是为了保证解锁操作能够被执行到，加锁和解锁操作一定要配套、成对儿出现
            // 解锁操作
            lock.unlock();
        }
    }

    public static void main(String[] args) {

        // 创建当前类的对象
        Demo01SaleTicket demo = new Demo01SaleTicket();

        // 创建三个线程代表三个窗口执行卖票操作
        new Thread(()->{
            for (int i = 0; i < 40; i++) {
                demo.saleTicket();
            }
        }, "thread-a").start();

        new Thread(()->{
            for (int i = 0; i < 40; i++) {
                demo.saleTicket();
            }
        }, "thread-b").start();

        new Thread(()->{
            for (int i = 0; i < 40; i++) {
                demo.saleTicket();
            }
        }, "thread-c").start();

    }

}
```

<br/>



# 三、Lock接口中的各个方法
|方法名| 作用                                                                                     |
|---|----------------------------------------------------------------------------------------|
|void lock();| 申请锁，如果没有申请到，那么就会一直等待、不断重试，直到申请成功为止                                                     |
|void unlock();| 解锁                                                                                     |
|boolean tryLock();| 尝试申请锁，申请成功返回true，申请失败返回false                                                           |
|boolean tryLock(long time, TimeUnit unit) throws InterruptedException;| 尝试申请锁，在指定的时间内等待、重试，申请成功返回true，申请失败返回false。<br/>声明抛出InterruptedException异常表示等待的过程可以被打断。 |
|void lockInterruptibly() throws InterruptedException;|申请锁，如果申请不到就一直等、不断重试，等待的状态可以被打断|
|Condition newCondition();|返回Condition对象，用于线程间通信|

<br/>



# 四、ReentrantLock类
## 1、类名说明
Reentrant：重入<br/>
ReentrantLock：意思就是这个锁支持可重入<br/>



## 2、可重入性验证

```java
// 1、创建 Lock 对象
Lock lock = new ReentrantLock();

try {
    // 2、外层加锁操作
    lock.lock();

    System.out.println("外层操作开始了！");

    // 3、内层加锁操作
    lock.lock();

    System.out.println("内层操作开始了！");
} finally {
    // 4、内层解锁操作
    lock.unlock();

    System.out.println("内层解锁了！");

    // 5、外层解锁操作
    lock.unlock();

    System.out.println("外层解锁了！");
}
```

<br/>



## 3、尝试获取锁

```java
// 1、创建锁对象
Lock lock = new ReentrantLock();

// 2、创建 A 线程申请锁成功，且占用锁
new Thread(()->{
    boolean tryResult = lock.tryLock();

    if (tryResult) {
        System.out.println(Thread.currentThread().getName() + " 线程成功获取到了锁！");
    }

    // 为了长期占用锁，所以这里是故意不写解锁操作 ...

}, "thread-a").start();

// 为了确保 A 线程先拿到锁，让主线程睡一会儿
TimeUnit.MILLISECONDS.sleep(100);

// 3、创建 B 线程申请锁失败
new Thread(()->{

    boolean tryResult = lock.tryLock();

    System.out.println("tryResult = " + tryResult);

}, "thread-b").start();
```



## 4、尝试获取锁带等待时间

```java
// 1、创建锁对象
Lock lock = new ReentrantLock();

// 2、创建 A 线程：占用锁一段时间
new Thread(()->{
    try {
        lock.lock();
        System.out.println(Thread.currentThread().getName() + " 得到了锁，开始占用");
        TimeUnit.SECONDS.sleep(5);
        System.out.println(Thread.currentThread().getName() + " 得到了锁，占用结束");
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    } finally {
        lock.unlock();
    }
}, "thread-a").start();

TimeUnit.MILLISECONDS.sleep(100);

// 3、创建 B 线程：尝试申请锁并且愿意等一段时间
new Thread(()->{

    boolean tryResult = false;

    try {
        tryResult = lock.tryLock(3, TimeUnit.SECONDS);

        if (tryResult) {
            System.out.println(Thread.currentThread().getName() + " 得到了锁");
        } else {
            System.out.println(Thread.currentThread().getName() + " 没有得到锁");
        }
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    } finally {
        if (tryResult) {
            lock.unlock();
        }
    }

}, "thread-b").start();
```

<br/>



## 5、lockInterruptibly()

### ①概念：响应中断
如果线程进入某个状态之后，调用线程对象的 interrupt() 方法能够打断这个状态，那么我们就可以说：这个状态支持响应中断。

<br/>



### ②TIMED_WAITING状态支持响应中断

```java
// 1、创建线程对象
Thread thread = new Thread(() -> {
        try {
        System.out.println("a 线程开始执行，即将入睡");
        Thread.sleep(10000);
        } catch (InterruptedException e) {
        throw new RuntimeException(e);
        }
        }, "thread-a");

// 2、启动线程
        thread.start();

// 3、主线程过一会儿去打断 thread TIMED_WAITING的状态
        TimeUnit.SECONDS.sleep(3);

// ※把线程当前所处的状态打断
        thread.interrupt();
```

<br/>



### ③BLOCKED状态不支持响应中断

```java
// 1、创建一个对象作为锁对象
Object lock = new Object();

// 2、创建 A 线程占用锁
new Thread(()->{
    synchronized (lock) {
        while (true) {}
    }
}, "thread-a").start();

TimeUnit.SECONDS.sleep(1);

// 3、创建 B 线程，申请锁
Thread thread = new Thread(() -> {
    synchronized (lock) {

    }
}, "thread-b");

// 4、启动线程 B
thread.start();

// 5、主线程等一会儿
TimeUnit.SECONDS.sleep(3);

// 6、尝试打断线程 B 的阻塞状态
System.out.println("尝试打断线程 B 的阻塞状态");
thread.interrupt();
```

<br/>



### ④lockInterruptibly()申请锁失败后的状态支持响应中断

```java
// 1、创建锁对象
Lock lock = new ReentrantLock();

// 2、创建 A 线程占用锁
new Thread(()->{lock.lock();}, "thread-a").start();

TimeUnit.SECONDS.sleep(1);

// 3、创建 B 线程申请锁，但是申请不到
Thread thread = new Thread(() -> {
    try {
        lock.lockInterruptibly();
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
}, "thread-b");

thread.start();

TimeUnit.SECONDS.sleep(1);

// 4、打断 B 线程的 WAITING(parking) 状态
thread.interrupt();
```



## 6、公平锁

```java
public class Demo08FairLock {

    // 公平锁：在锁上等待时间最长的线程下一次获取锁时有最高优先级
    // 相对非公平锁，公平锁的吞吐量更小，性能上没有优势
    // 创建公平锁对象，在构造器中传入 true
    private Lock lock = new ReentrantLock(true);

    public void someOperation() {
        try {
            lock.lock();
            System.out.println(Thread.currentThread().getName() + " 线程开始了！");
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            lock.unlock();
        }
    }

    public static void main(String[] args) {
        Demo08FairLock demo = new Demo08FairLock();

        for (int i = 0; i < 10; i++) {
            new Thread(()->{
                for (int j = 0; j < 10; j++) {
                    demo.someOperation();
                }
            }, "thread-" + i).start();
        }

    }

}
```

<br/>



# 五、读写锁

## 1、概述
- 读锁：共享锁 读操作可以共享，写操作不行
- 写锁：独占锁

<br/>



### ①多线程执行

- 读锁：多个线程可以同时读，但是不能写（读锁释放之后，才能加写锁）
- 写锁：其它线程不管是申请读锁还是写锁，都必须等当前线程手里的写锁释放



### ②线程内部

- 读锁：先加了读锁，读锁尚未释放，不能申请写锁
  - 支持可重入
- 写锁：先加了写锁，即使写锁不释放，也可以申请读锁
  - 支持可重入

<br/>



### ③说明

Java 代码本身其实并没有办法区分操作是读操作还是写操作，申请到锁之后，具体是读还是写，由开发人员自己决定

<br/>



## 2、创建读写锁锁对象

```java
// 创建读写锁对象
private ReentrantReadWriteLock readWriteLock = new ReentrantReadWriteLock();

// 通过读写锁对象获取读锁
private ReentrantReadWriteLock.ReadLock readLock = readWriteLock.readLock();

// 通过读写锁对象获取写锁
private ReentrantReadWriteLock.WriteLock writeLock = readWriteLock.writeLock();
```



## 3、多线程执行

```java
public class Demo09MultiThreadRead {

    // 创建读写锁对象
    private ReentrantReadWriteLock readWriteLock = new ReentrantReadWriteLock();

    // 通过读写锁对象获取读锁
    private ReentrantReadWriteLock.ReadLock readLock = readWriteLock.readLock();

    // 通过读写锁对象获取写锁
    private ReentrantReadWriteLock.WriteLock writeLock = readWriteLock.writeLock();

    public void readOperation() {
        try {
            // 加读锁
            readLock.lock();

            System.out.println(Thread.currentThread().getName() + " 线程开始执行『读』操作~~~");

            TimeUnit.SECONDS.sleep(1);

            System.out.println(Thread.currentThread().getName() + " 线程已经完成『读』操作~~~");
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            // 释放读锁
            readLock.unlock();
        }
    }

    public void writeOperation() {
        try {
            // 加写锁
            writeLock.lock();

            System.out.println(Thread.currentThread().getName() + " 线程开始执行【写】操作~~~");

            TimeUnit.SECONDS.sleep(1);

            System.out.println(Thread.currentThread().getName() + " 线程已经完成【写】操作~~~");
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            // 释放写锁
            writeLock.unlock();
        }
    }

    public static void main(String[] args) {

        Demo09MultiThreadRead demo = new Demo09MultiThreadRead();

        // 创建 5 个线程执行写操作
        // 写锁是独占的，一个线程得到写锁之后，其它线程不管是读还是写都需要等写锁释放
        for (int i = 0; i < 5; i++) {
            new Thread(()->{
                demo.writeOperation();
            }, "thread-write-" + i).start();
        }

        // 创建 5 个线程执行读操作
        // 读锁是共享的，多个线程可以分别获取到读锁，而想要获取写锁，就必须等所有读锁都释放
        for (int i = 0; i < 5; i++) {
            new Thread(()->{
                demo.readOperation();
            }, "thread-read-" + i).start();
        }

    }

}
```

<br/>



## 4、一个线程内部

### ①读锁不能升级为写锁
```java
// 1、创建读写锁对象
ReentrantReadWriteLock readWriteLock = new ReentrantReadWriteLock();

// 2、通过读写锁对象获取读锁对象
ReentrantReadWriteLock.ReadLock readLock = readWriteLock.readLock();

// 3、通过读写锁对象获取写锁对象
ReentrantReadWriteLock.WriteLock writeLock = readWriteLock.writeLock();

// 4、申请读锁
readLock.lock();

System.out.println("读锁到手~~~");

// 5、在读锁尚未释放的情况下，申请写锁
// 实际运行效果：程序到这里会被阻塞，因为申请写锁需要等读锁释放
// 背后的逻辑：开始拿到读锁，相当于申请到了一个小的权限，现在再申请写锁，等于要扩大权限，这个不允许
writeLock.lock();

System.out.println("写锁到手~~~");
```

<br/>



### ②写锁内再申请读锁

```java
// 1、创建读写锁对象
ReentrantReadWriteLock readWriteLock = new ReentrantReadWriteLock();

// 2、通过读写锁对象获取读锁对象
ReentrantReadWriteLock.ReadLock readLock = readWriteLock.readLock();

// 3、通过读写锁对象获取写锁对象
ReentrantReadWriteLock.WriteLock writeLock = readWriteLock.writeLock();

// 4、申请写锁
writeLock.lock();

System.out.println("写锁到手~~~");

// 5、在写锁尚未释放的情况下，申请读锁
readLock.lock();

System.out.println("读锁到手~~~");
```



### ③读锁支持可重入

```java
ReentrantReadWriteLock readWriteLock = new ReentrantReadWriteLock();

ReentrantReadWriteLock.ReadLock readLock = readWriteLock.readLock();

readLock.lock();

System.out.println("外层加锁成功~~~");

readLock.lock();

System.out.println("内层加锁成功~~~");
```

<br/>



### ④写锁支持可重入

```java
ReentrantReadWriteLock readWriteLock = new ReentrantReadWriteLock();

ReentrantReadWriteLock.WriteLock writeLock = readWriteLock.writeLock();

writeLock.lock();

System.out.println("外层加锁成功~~~");

writeLock.lock();

System.out.println("内层加锁成功~~~");
```



# 六、线程间通信

## 1、常规操作
```java
package com.atguigu.juc.day02;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Demo14Communication {

    private int number = 0;

    private Lock lock = new ReentrantLock();

    private Condition condition = lock.newCondition();

    public void doAdd() {
        try {
            // 1、加锁
            lock.lock();

            // 2、在条件不满足时，让当前线程等待（同样需要注意虚假唤醒问题）
            while (number >= 1) {
                condition.await();
            }

            // 3、条件满足时执行核心操作
            System.out.println(Thread.currentThread().getName() + " 执行+1操作：" + ++number);

            TimeUnit.MILLISECONDS.sleep(100);

            // 4、唤醒其它线程
            condition.signalAll();

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            lock.unlock();
        }
    }

    public void doSub() {
        try {
            // 1、加锁
            lock.lock();

            // 2、在条件不满足时，让当前线程等待（同样需要注意虚假唤醒问题）
            while (number < 1) {
                condition.await();
            }

            // 3、条件满足时执行核心操作
            System.out.println(Thread.currentThread().getName() + " 执行-1操作：" + --number);

            TimeUnit.MILLISECONDS.sleep(100);

            // 4、唤醒其它线程
            condition.signalAll();

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            lock.unlock();
        }
    }

    public static void main(String[] args) {

        Demo14Communication demo = new Demo14Communication();

        // 创建两个线程执行加法
        new Thread(()->{
            for (int i = 0; i < 30; i++) {
                demo.doAdd();
            }
        }, "thread-add-01").start();
        new Thread(()->{
            for (int i = 0; i < 30; i++) {
                demo.doAdd();
            }
        }, "thread-add-02").start();

        // 创建两个线程执行减法
        new Thread(()->{
            for (int i = 0; i < 30; i++) {
                demo.doSub();
            }
        }, "thread-sub-01").start();
        new Thread(()->{
            for (int i = 0; i < 30; i++) {
                demo.doSub();
            }
        }, "thread-sub-02").start();

    }
}

```

<br/>



## 2、精确唤醒

```java
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 四个线程轮番、交替打印：
 * 1a*$
 * 2b*$
 * 3c*$
 * 4d*$
 * 5e*$
 * ……
 *
 * 第一个线程负责打印数字 conditionDigital
 * 第二个线程负责打印字母 conditionAlphabet
 * 第三个线程负责打印星号 conditionStar
 * 第四个线程负责打印美元 conditionDollar
 */
public class Demo15ExactSignal {

    private Lock lock = new ReentrantLock();
    private Condition conditionDigital = lock.newCondition();
    private Condition conditionAlphabet = lock.newCondition();
    private Condition conditionStar = lock.newCondition();
    private Condition conditionDollar = lock.newCondition();

    // 总体执行的步骤的数量
    private int step = 1;

    // 总体上要打印的数字
    private int digital = 1;

    // 总体上要打印的字母
    private char alphabet = 'A';

    public void printDigital() {

        try {
            lock.lock();

            // 1、如果条件不满足，则当前线程等待
            while (step % 4 != 1) {
                conditionDigital.await();
            }

            // 2、如果条件满足，则执行核心操作
            System.out.print(digital++);

            // 3、总步骤 +1
            step++;

            // 4、精准的唤醒下一个该干活的线程
            conditionAlphabet.signal();

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {

            lock.unlock();

        }
    }

    public void printAlphabet() {

        try {
            lock.lock();

            // 1、如果条件不满足，则当前线程等待
            while (step % 4 != 2) {
                conditionAlphabet.await();
            }

            // 2、如果条件满足，则执行核心操作
            System.out.print(alphabet++);

            // 3、总步骤 +1
            step++;

            // 4、精准的唤醒下一个该干活的线程
            conditionStar.signal();

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {

            lock.unlock();

        }
    }

    public void printStar() {

        try {
            lock.lock();

            // 1、如果条件不满足，则当前线程等待
            while (step % 4 != 3) {
                conditionStar.await();
            }

            // 2、如果条件满足，则执行核心操作
            System.out.print("*");

            // 3、总步骤 +1
            step++;

            // 4、精准的唤醒下一个该干活的线程
            conditionDollar.signal();

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {

            lock.unlock();

        }
    }

    public void printDollar() {

        try {
            lock.lock();

            // 1、如果条件不满足，则当前线程等待
            while (step % 4 != 0) {
                conditionDollar.await();
            }

            // 2、如果条件满足，则执行核心操作
            System.out.println("$");

            // 3、总步骤 +1
            step++;

            // 4、精准的唤醒下一个该干活的线程
            conditionDigital.signal();

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {

            lock.unlock();

        }
    }

    public static void main(String[] args) {

        Demo15ExactSignal demo = new Demo15ExactSignal();

        new Thread(()->{
            for (int i = 0; i < 50; i++) {
                demo.printDigital();
            }
        }, "thread-digital").start();

        new Thread(()->{
            for (int i = 0; i < 50; i++) {
                demo.printAlphabet();
            }
        }, "thread-alphabet").start();

        new Thread(()->{
            for (int i = 0; i < 50; i++) {
                demo.printStar();
            }
        }, "thread-star").start();

        new Thread(()->{
            for (int i = 0; i < 50; i++) {
                demo.printDollar();
            }
        }, "thread-dollar").start();
    }

}

```



# 六、特定场景解决方案

## 1、CountDownLatch
翻译为中文：递减门闩<br/>

某个特定操作，需要在前面各个步骤完成之后再执行，借助CountDownLatch就可以在前面步骤没有完成的时候，把最后一步抑制住不执行<br/>
等前面步骤执行完，最后一步再执行

```java
// 目标：所有同学都离开教室之后，班长再锁门
// 1、创建 CountdownLatch 对象
CountDownLatch countDownLatch = new CountDownLatch(6);

for (int i = 0; i < 6; i++) {
    new Thread(()->{
        try {
            TimeUnit.SECONDS.sleep((long) (Math.random()*3));
            System.out.println(Thread.currentThread().getName() + " 同学离开教室了...");
            
            // 2、前面的步骤每完成一个，countDownLatch 就执行一次递减
            countDownLatch.countDown();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }, "thread-" + i).start();
}

// 3、调用 countDownLatch 的方法把最后一步抑制住
countDownLatch.await();

System.out.println("班长锁门~~~");
```

<br/>



## 2、CyclicBarrier

翻译为中文：循环栅栏<br/>
很多个线程在执行各自的任务，我们约定一个特定的信号，每一个线程执行到这里都进入等待，当所有线程都执行到这一步再继续执行后续操作

```java
public class Demo17CyclicBarrier {

    public static final List<List<String>> matrix = new ArrayList<>();

    static {
        matrix.add(Arrays.asList("normal","special","end01","end02","end03"));
        matrix.add(Arrays.asList("normal","normal","special","end01","end02","end03"));
        matrix.add(Arrays.asList("normal","normal","normal","special","end01","end02","end03"));
        matrix.add(Arrays.asList("normal","normal","normal","normal","special","end01","end02","end03"));
    	matrix
        .add(Arrays.asList("normal","normal","normal","normal","normal","special","end01","end02","end03"));
    }

    public static void main(String[] args) {

        // 创建 CyclicBarrier 对象，在构造器中指定参与管理的线程的数量
        CyclicBarrier cyclicBarrier = new CyclicBarrier(5);

        for (int i = 0; i < 5; i++) {
            final int index = i;
            new Thread(()->{
                try {
                    List<String> list = matrix.get(index);
                    for (int j = 0; j < list.size(); j++) {
                        String data = list.get(j);

                        System.out.println(Thread.currentThread().getName() + " " + data);

                        if ("special".equals(data)) {
                            // 在满足特定条件时，让当前线程进入等待
                            // 所有参与管理的线程都到这一步，然后再全部唤醒，执行后续操作
                            cyclicBarrier.await();
                        }
                    }
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                } catch (BrokenBarrierException e) {
                    throw new RuntimeException(e);
                }
            }, "thread-" + i).start();
        }

    }

}
```

<br/>



## 3、Semaphore

翻译为中文：信号量;信号;信号灯<br/>

多个线程争抢有限的资源，适合使用 Semaphore 来管理资源<br/>



### ①基本用法

```java
int carPosition = 3;

// 创建 Semaphore 对象时传入资源的数量
Semaphore semaphore = new Semaphore(carPosition);

// 创建 10 个线程，代表 10 个车辆，申请车位
for (int i = 0; i < 10; i++) {
    new Thread(()->{
        try {
            // 申请资源
            semaphore.acquire();

            System.out.println(Thread.currentThread().getName() + " 车辆驶入车位");

            TimeUnit.SECONDS.sleep(1);

            System.out.println(Thread.currentThread().getName() + " 车辆驶出车位");

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            // 释放资源
            semaphore.release();
        }
    }, "thread-" + i).start();
}
```



### ②延时等待

```java
int carPosition = 3;

Semaphore semaphore = new Semaphore(carPosition);

for (int i = 0; i < 10; i++) {
    new Thread(()->{

        boolean acquireResult = false;

        try {
            // 尝试申请资源，如果当时没有申请到，可以等待指定的时间
            // 返回 true：申请成功
            // 返回 false：申请失败
            acquireResult = semaphore.tryAcquire(3, TimeUnit.SECONDS);

            if (acquireResult) {
                System.out.println(Thread.currentThread().getName() + " 车辆驶入车位");

                TimeUnit.SECONDS.sleep((long) (Math.random()*5));

                System.out.println(Thread.currentThread().getName() + " 车辆驶出车位");
            } else {
                System.out.println(Thread.currentThread().getName() + " 放弃了");
            }

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            if (acquireResult) {
                semaphore.release();
            }
        }

    }, "thread-" + i).start();
}
```

<br/>



## 4、Fork Join 框架

### ①概述
- fork：干草叉，在程序中代表分支
- join：合并

Fork Join 框架可以帮助我们把一个大任务拆分成很多小任务分别执行，再把小任务执行的结果合并到一起，最终得到大任务的最终结果<br/>

Fork Join 框架底层执行拆分和合并都是递归的：
- 拆分：如果没有拆分到最小颗粒，就继续拆分；拆分到最小颗粒就执行
- 合并：从最小的任务开始执行，然后按照递归拆分的反方向逐层合并

<br/>



### ②示例代码

```java
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.ForkJoinTask;
import java.util.concurrent.RecursiveTask;

public class Demo19ForkJoin {

    public static void main(String[] args) throws ExecutionException, InterruptedException {
        // 1、创建 ForkJoinPool
        ForkJoinPool forkJoinPool = new ForkJoinPool();

        // 2、把创建任务对象
        MyTask myTask = new MyTask(1, 99);

        // 3、把任务提交给 ForkJoinPool
        ForkJoinTask<Integer> forkJoinTask = forkJoinPool.submit(myTask);

        // 4、通过 ForkJoinTask 对象获取最终结果
        Integer finalResult = forkJoinTask.get();
        System.out.println("finalResult = " + finalResult);
    }

}

// 目标：执行从 1 ~ 100 的累加
// 预期结果：5050
// 任务拆分的规则：参与累加的数字在 10 以内的区间即可
class MyTask extends RecursiveTask<Integer> {

    // 任务区间的开始值
    private int begin;

    // 任务区间的结束值
    private int end;

    // 根据任务区间创建类的对象
    public MyTask(int begin, int end) {
        this.begin = begin;
        this.end = end;
    }

    // 最小任务区间范围
    public static final int ADJUST_VALUE = 10;

    // 任务执行结果
    private int result = 0;

    @Override
    protected Integer compute() {

        // 1、检查当前任务区间是否已经进入最小区间范围
        if (end - begin <= 10) {
            // 2、既然满足条件，已经拆分到了最小区间，那么我们就执行累加操作
            for (int i = begin; i <= end; i++) {
                result += i;
            }
        } else {
            // 3、如果没有没有进入最小区间，那么就继续拆分
            // 拆分的逻辑就是把 begin 和 end 定义的区间平均拆成两半
            int leftBegin = begin;

            // (end - begin)/2 + begin
            // (end - begin)/2 + 2begin/2
            // (end - begin + 2begin)/2
            // (end + begin)/2
            int leftEnd = (end + begin)/2;
            MyTask myTaskLeft = new MyTask(leftBegin, leftEnd);

            int rightBegin = leftEnd + 1;
            int rightEnd = end;
            MyTask myTaskRight = new MyTask(rightBegin, rightEnd);

            // 4、调用拆分后任务的 fork() 方法，递归执行后续拆分
            myTaskLeft.fork();
            myTaskRight.fork();

            // 5、调用拆分后任务的 join() 方法，合并子任务执行的结果
            Integer leftResult = myTaskLeft.join();
            Integer rightResult = myTaskRight.join();

            // 6、合并任务执行的结果
            result = leftResult + rightResult;

        }

        // 7、返回任务执行的结果
        return result;
    }
}
```















