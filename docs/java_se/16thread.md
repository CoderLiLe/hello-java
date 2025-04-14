# 多线程

- [1. 程序](#1-程序)
- [2. 进程](#2-进程)
- [3. 线程](#3-线程)
- [4. 关于线程开辟 和 线程执行](#4-关于线程开辟-和-线程执行)
- [5. 并发和并行](#5-并发和并行)
- [6. 主线程](#6-主线程)
- [7. 创建线程的两种方式](#7-创建线程的两种方式)
  - [7.1 继承Thread类](#71-继承thread类)
  - [7.2 实现Runnable接口](#72-实现runnable接口)
- [8. 线程的状态](#8-线程的状态)
- [9.线程的优先级](#9线程的优先级)
- [10.线程的休眠](#10线程的休眠)
- [11. 线程的插队](#11-线程的插队)
- [12. 线程的礼让](#12-线程的礼让)
- [13. 练习](#13-练习)
- [14. synchronized](#14-synchronized)
  - [14.1 同步代码块](#141-同步代码块)
  - [14.2 同步方法](#142-同步方法)
- [15.生产者消费者模式](#15生产者消费者模式)
- [16. 相关面试题](#16-相关面试题)


## 1. 程序

> 一些列代码指令的集合 统称 ，应用，软件等等 都属于程序
>
> 程序运行必须依托于进程而存在，进程负责分配资源，依赖线程来运行。

## 2. 进程

> 进程 进行中应用 程序 属于资源分配的基本单位 

## 3. 线程

> 线程是包含在进程之中的  一个进程至少有一个线程 否则将无法运行 线程是CPU调度运算的基本单位

## 4. 关于线程开辟 和 线程执行

> 线程不是越多越好 要结合实际的硬件环境来决定    
>
> 在单核心CPU下  多个线程是轮流交替执行的 以windows操作系统为例  多个线程随机轮流交替执行 每个线程最多执行20ms 继续切换下一个线程  而非并行执行 因为切换的频率非常快 所以我们感知不到这个过程 宏观上 是同时执行的  实际上 是轮流交替执行的 

## 5. 并发和并行

> 并发：同时发生  轮流交替执行  宏观同时执行 微观轮流交替执行
>
> 并行：严格意义上的同时执行  

## 6. 主线程

> main方法为程序的入口 底层由main线程负责执行  由JVM自动调用执行
>
> java.lang.Thread 线程类
>
>
> currentThread() 获取当前线程对象 是一个静态方法
>
> getName() 获取线程名称
>
> setName(String name) 设置线程名称

```java
public class TestMainThread {
    public static void main(String[] args) {
        // 获取当前线程对象
        Thread thread = Thread.currentThread();

        // 打印线程名称
        System.out.println("线程的名称：" + thread.getName());

        thread.setName("主线程"); // 设置线程名城

        // 打印线程名称
        System.out.println("线程的名称：" + thread.getName());
    }
}

```

## 7. 创建线程的两种方式

> 继承Thread和实现Runnable接口的区别？
>
> - 继承Thread类 编写简单，可直接操作线程 适用于单继承
> - 实现Runnable接口 避免单继承局限性 便于共享资源
>
>
> 调用start方法和run方法的区别？
>
> - 调用start方法表示通知调度器(CPU)当前线程准备就 调度器会开启新的线程来执行任务
> - 调用run方法表示使用当前主线程来执行方法 不会开启新的线程

### 7.1 继承Thread类

> 创建线程方式1 ： 继承Thread类 重写run方法
>
>
> 创建的子线程如果没有指定名称 将默认以 Thread-0 -1 这种方式来命名

```java
public class MyThread1 extends Thread{

    @Override
    public void run() {
        for(int i = 1;i <= 20;i++){
            System.out.println(Thread.currentThread().getName() + "===" + i);
        }
    }

    public static void main(String[] args) {
        MyThread1 th1 = new MyThread1();

        MyThread1 th2 = new MyThread1();

        th1.setName("线程A");

        th2.setName("****线程B****");

        th1.start();
        th2.start();
    }
}

```


### 7.2 实现Runnable接口

> 创建线程方式2：实现Runnable接口 重写run方法  Runnable实现类可以作为参数构造Thread实例

```java
/**
 *  继承Thread和实现Runnable接口的区别？
 *      继承Thread类 编写简单，可直接操作线程 适用于单继承
 *      实现Runnable接口 避免单继承局限性 便于共享资源
 *
 *  调用start方法和run方法的区别？
 *  调用start方法表示通知调度器(CPU)当前线程准备就 调度器会开启新的线程来执行任务
 *  调用run方法表示使用当前主线程来执行方法 不会开启新的线程
 */
public class RunnableImpl implements  Runnable{
    @Override
    public void run() {
        for(int i = 1;i <= 20;i++){
            System.out.println(Thread.currentThread().getName() + "---" + i);
        }
    }


    public static void main(String[] args) {
        // 创建Runnable实现类对象 
        RunnableImpl runnable = new RunnableImpl();

        // 使用Runnable实现类对象构造Thread对象 定义线程名为 '线程A'
        Thread th1 = new Thread(runnable,"线程A");

        // 使用Runnable实现类对象构造Thread对象 
        Thread th2 = new Thread(runnable);
		
        // 重新设置线程名
        th2.setName("*****线程B*****");

        th1.start(); // 准备就绪 

        th2.start(); // 准备就绪 
    }
}

```

## 8. 线程的状态

> 线程状态：创建 就绪 运行 阻塞 死亡

```java
public class TestThreadStatus extends Thread{
    @Override
    public void run() { // 运行

        try {
            Thread.sleep(3000); // 阻塞状态
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("当前线程名称" + Thread.currentThread().getName());
        System.out.println("线程执行完毕");
        // 死亡
    }

    public static void main(String[] args) {
        // 创建
        TestThreadStatus threadStatus = new TestThreadStatus();

        // 就绪
        threadStatus.start();
    }

}

```

## 9.线程的优先级

> 线程的优先级：从1~10 1最低 10最高 默认为5  优先级高的线程只是获得CPU资源的概率较大 并不一定能够保证优先执行

```java
public class TestPriority extends Thread{
    @Override
    public void run() {
        for(int i = 1;i <= 20;i++){
            System.out.println(Thread.currentThread().getName() + "---" + i);

        }
    }

    public static void main(String[] args) {
        // 创建线程对象
        TestPriority th1 = new TestPriority();
        th1.setName("线程A"); // 设置线程名称


        TestPriority th2 = new TestPriority(); // 创建线程对象
        th2.setName("*****线程B*****"); // 设置线程名称

        // 设置线程优先级
        th1.setPriority(MAX_PRIORITY); //MAX_PRIORITY-10  NORM_PRIORITY-5  MIN_PRIORITY-1

        System.out.println("线程A优先级" + th1.getPriority()); // 打印线程优先级
        System.out.println("线程B优先级" + th2.getPriority()); // 打印线程优先级

        th1.start(); // 就绪
        th2.start(); // 就绪
    }
}

```

## 10.线程的休眠

> 线程的休眠：
>
> sleep(long millis)  让当前线程等待指定时间 然后再继续执行

```java
public class TestSleep extends Thread{
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + "线程开始执行");
        try {
            // 因为父类run方法没有声明任何异常 所以子类也不能声明任何异常
            Thread.sleep(3000); // 休眠3秒钟 到达时间  自动继续执行
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println(Thread.currentThread().getName() + "线程执行完毕");
    }

    public static void main(String[] args) {
        TestSleep thread = new TestSleep();
        thread.start();
    }
}

```



## 11. 线程的插队

> 线程的插队
>
> join()  线程插队 直到插队线程执行完毕
>
> join(long millis)  线程插队 插队指定的时间
>
> join(long millis,int nanos) 线程插队 插队指定的时间

```java
public class TestJoin extends Thread{
    @Override
    public void run() {
        for(int i = 1;i <= 20;i++){
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println(Thread.currentThread().getName() + "--" + i);
        }
    }


    public static void main(String[] args) throws InterruptedException {
        TestJoin thread = new TestJoin();

        thread.setName("****线程A****");

        thread.start();


        for(int i = 1;i <= 50;i++){
            // 当i取值为10  子线程插队
            if(i == 10){
                System.out.println("子线程插队");
                thread.join(500); // 插队指定的时间为500毫秒
            }
            System.out.println(Thread.currentThread().getName() + "====" +i);
        }
    }
}

```

## 12. 线程的礼让

> 线程的礼让
>
> yield() 当前线程向调度器发出信息 表示当前正在执行的线程愿意做出让步 但是调度器可以忽略这个信息

```java
public class TestYield extends Thread{
    @Override
    public void run() {
        for (int i = 1;i <= 20;i++){
            try {
                Thread.sleep(200);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            if(i == 10){ // 当i取值为10  则礼让 但不保证一定会礼让成功
                System.out.println(Thread.currentThread().getName() + "线程礼让了");
                Thread.yield(); // 线程礼让 
            }
            System.out.println(Thread.currentThread().getName() + "----" + i);
        }
    }

    public static void main(String[] args) {
        TestYield th1 = new TestYield();
        TestYield th2 = new TestYield();

        th1.setName("线程A");
        th2.setName("*****线程B*****");

        th1.start();
        th2.start();

    }
}

```

## 13. 练习
```java
/**
 *  模拟多人爬山
 *  分析：将run方法体的内容 作为两个角色共同执行的爬山过程 爬山的速度不一样 所以表示休眠的时间不同
 *  爬山的高度是相同的  角色名称不同 表示线程名不同   同时创建两个线程对象  分别 start方法 表示开始
 *  同时爬山 因为爬山速度不同 所以到达山顶时间是不同的
 */
public class ClimbThread extends Thread{
    private int length; // 长度 高度
    private int time; // 每爬100米耗时

    public ClimbThread(int length, int time, String name) {
        super(name);
        this.length = length;
        this.time = time;

    }

    @Override
    public void run() {
        while(length > 0){
            try {
                Thread.sleep(time);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            length -= 100;
            System.out.println(Thread.currentThread().getName() + "爬了100米，还剩余" + length + "米");
        }
        System.out.println(Thread.currentThread().getName() + "爬到了山顶");
    }


    public static void main(String[] args) {
        ClimbThread youngMan = new ClimbThread(1000, 500, "练习两年半的年轻人");
        ClimbThread oldMan = new ClimbThread(1000, 1000, "马老师");

        youngMan.start();
        oldMan.start();
    }
}

```

```java
/**
 *  某科室一天需看普通号50个，特需号10个 (执行不同的次数)
 *  特需号看病时间是普通号的2倍 (休眠时间)
 *  开始时普通号和特需号并行叫号，叫到特需号的概率比普通号高(同时start开始执行 优先级不同)
 *  当普通号叫完第10号时，要求先看完全部特需号，再看普通号 (插队)
 *  使用多线程模拟这一过程
 *
 *  分析：子线程作为特需号类  主线程作为普通号类
 */
public class Special extends Thread{

    @Override
    public void run() {
        for(int i = 1;i <= 10;i++){
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println(Thread.currentThread().getName() + "第" + i + "号在看病");
        }

        System.out.println(Thread.currentThread().getName() + "看病完毕");

    }

    public static void main(String[] args) throws InterruptedException {
        Special special = new Special();
        special.setName("*****特需号*****");
        special.setPriority(MAX_PRIORITY);
        special.start();


        Thread mainThread = Thread.currentThread();
        mainThread.setName("普通号");
        for(int i = 1;i <= 50;i++){
            Thread.sleep(500);
            System.out.println(Thread.currentThread().getName() + "第" + i + "号在看病");

            if(i == 10){
                special.join();
            }
        }

        System.out.println(Thread.currentThread().getName() + "看病完毕");
    }

}

```



## 14. synchronized

> 关于同步代码块中的this关键字：this表示当前对象 即Runnable实现类对象
>
> 同步代码快小括号中可以写任何对象 如果需要实现多个线程同步的效果
>
> 则必须保证 多个线程所使用 锁定的 是同一个对象 否则 将不能实现线程同步
>
> 通常书写为this

> 多个并发线程访问同一资源的同步代码块时
>
> 同一时刻只能有一个线程进入synchronized（this）同步代码块
>
> 当一个线程访问一个synchronized（this）同步代码块时，其他synchronized（this）同步代码块同样被锁定
>
> 当一个线程访问一个synchronized（this）同步代码块时，其他线程可以访问该资源的非synchronized（this）同步代码

> 我们之前接触到的 线程安全的类 StringBuffer  Vector  Hashtable 都是使用同步关键字修饰方法 实现的线程安全 

### 14.1 同步代码块

> 使用多线程模拟：多人抢票 三个人 抢10张票
>
> 有一个线程买票 前边的线程购买完毕 后边的线程才能继续购买
>
>
> 解决方案：多个线程必须排队买票 保证同一时间只能有一个线程买票 前边的线程购买完毕 后边的线程才能继续购买
>
>
> 同步关键字：synchronized
>
> 可以用于修代码块 ，表示同一时间只能有一个线程访问这个代码块

```java
public class BuyTicket2 implements Runnable{
    int ticketCount = 10;
    @Override
    public void run() {
        while(true){
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            synchronized (this){
                if(ticketCount == 0){
                    break;
                }
                ticketCount--;
                System.out.println(Thread.currentThread().getName() + "抢到了第"+ (10 - ticketCount) +"张票，还剩余"+ ticketCount +"张票");
            }
        }
        System.out.println("票卖完了");
    }

    public static void main(String[] args) {
       BuyTicket2 runnable = new BuyTicket2();

       Thread th1 = new Thread(runnable,"赵四");
       Thread th2 = new Thread(runnable,"广坤");
       Thread th3 = new Thread(runnable,"大拿");

       th1.start();
       th2.start();
       th3.start();
    }
}

```



### 14.2 同步方法

> 使用多线程模拟：多人抢票 三个人 抢10张票
>
> 有一个线程买票 前边的线程购买完毕 后边的线程才能继续购买
>
> 解决方案：多个线程必须排队买票 保证同一时间只能有一个线程买票 前边的线程购买完毕 后边的线程才能继续购买
>
> 同步关键字：synchronized
>
> 可以用于修饰方法 ,表示同一时间只能有一个线程访问这个方法

```java
public class BuyTicket3 implements Runnable {
    int ticketCount = 10;

    @Override
    public synchronized void run() {

        while (ticketCount > 0) {
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            ticketCount--;
            System.out.println(Thread.currentThread().getName() + "抢到了第" + (10 - ticketCount) + "张票，还剩余" + ticketCount + "张票");
        }
        System.out.println("票卖完了");
    }

    public static void main(String[] args) {
        BuyTicket3 runnable = new BuyTicket3();

        Thread th1 = new Thread(runnable, "赵四");
        Thread th2 = new Thread(runnable, "广坤");
        Thread th3 = new Thread(runnable, "大拿");

        th1.start();
        th2.start();
        th3.start();
    }
}

```

## 15.生产者消费者模式

> 生产者消费者模式：不属于设计模式 属于线程之间通信的一种现象
>
>
> 生产什么 消费什么
>
> 没有生产 不能消费(持续生产 持续消费)
>
> 必须保证产品的完整性
>
> 不能重复消费
>
>
> 产品类
>
>
> Object类中的两个方法 ：wait 和 notify方法
>
> wait()方法 表示让当前线程等待
>
> notify() 方法 唤醒正在等待的线程

```java
public class Computer {
    private String mainFrame; // 主机
    private String screen; // 显示器

    private boolean flag; // false 可以生产 不能消费  true 可以消费 不能生产

    public boolean isFlag() {
        return flag;
    }

    public void setFlag(boolean flag) {
        this.flag = flag;
    }

    public String getMainFrame() {
        return mainFrame;
    }

    public void setMainFrame(String mainFrame) {
        this.mainFrame = mainFrame;
    }

    public String getScreen() {
        return screen;
    }

    public void setScreen(String screen) {
        this.screen = screen;
    }

    public Computer() {
    }

    public Computer(String mainFrame, String screen) {
        this.mainFrame = mainFrame;
        this.screen = screen;
    }

    @Override
    public String toString() {
        return "Computer{" +
                "mainFrame='" + mainFrame + '\'' +
                ", screen='" + screen + '\'' +
                '}';
    }
}

```

```java
/**
 *  生产者线程 负责生产电脑
 */
public class Producer extends Thread{
    private Computer computer;

    public Producer(Computer computer) {
        this.computer = computer;
    }

    @Override
    public void run() {
        for(int i = 1;i <= 20;i++){

            synchronized (computer) {

                if(computer.isFlag()){
                    try {
                        computer.wait();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }

                if(i % 2 == 0){
                   computer.setMainFrame(i + "号联想主机");
                    try {
                        Thread.sleep(50);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                   computer.setScreen(i + "号联想显示器");
                    System.out.println("生产了第"+ i +"号联想电脑");
                }else{
                    computer.setMainFrame(i + "号华硕主机");
                    try {
                        Thread.sleep(500);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    computer.setScreen(i + "号华硕显示器");
                    System.out.println("生产了第"+ i +"号华硕电脑");
                }

                computer.setFlag(true);
                computer.notify();
            }
        }
    }
}

```

```java
/**
 *  消费者线程 负责消费电脑
 */
public class Consumer extends Thread{
    private Computer computer;

    public Consumer(Computer computer) {
        this.computer = computer;
    }

    @Override
    public void run() {
        for(int i = 1;i <= 20;i++){
            synchronized (computer) {
                if(computer.isFlag() == false){
                    try {
                        computer.wait();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println(computer.getMainFrame() + "===" + computer.getScreen());

                computer.setFlag(false);
                computer.notify();
            }
        }
    }
}

```

```java
public class Test {
    public static void main(String[] args) {
        Computer computer = new Computer();

        Producer producer = new Producer(computer);
        Consumer consumer = new Consumer(computer);

        producer.start();
        consumer.start();
    }
}

```

> 生产者消费者模式：不属于设计模式 属于线程之间通信的一种现象
>
>
> 生产什么 消费什么
>
> 没有生产 不能消费(持续生产 持续消费)
>
> 必须保证产品的完整性
>
> 不能重复消费
>
>
> 产品类
>
>
> ArrayBlockingQueue 基于数组的阻塞队列
>
> 队列 即FIFO First In First Out
>
> 阻塞表示队列是有长度限制的 所以当队列满了以后 将不能再添加新的数据到队列中
>
>
> add() 将数据存放在队列中
>
> take() 从队列中取出数据

```java
public class Computer {
    private String mainFrame; // 主机
    private String screen; // 显示器


    public String getMainFrame() {
        return mainFrame;
    }

    public void setMainFrame(String mainFrame) {
        this.mainFrame = mainFrame;
    }

    public String getScreen() {
        return screen;
    }

    public void setScreen(String screen) {
        this.screen = screen;
    }

    public Computer() {
    }

    public Computer(String mainFrame, String screen) {
        this.mainFrame = mainFrame;
        this.screen = screen;
    }

    @Override
    public String toString() {
        return "Computer{" +
                "mainFrame='" + mainFrame + '\'' +
                ", screen='" + screen + '\'' +
                '}';
    }
}

```

```java
/**
 * 消费者线程 负责消费电脑
 */
public class Consumer extends Thread {
    private ArrayBlockingQueue<Computer> queue;

    public Consumer(ArrayBlockingQueue<Computer> queue) {
        this.queue = queue;
    }

    @Override
    public void run() {
        for (int i = 1; i <= 20; i++) {
            try {
                System.out.println(queue.take());
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

```

```java
/**
 * 生产者线程 负责生产电脑
 */
public class Producer extends Thread {
    private ArrayBlockingQueue<Computer> queue;

    public Producer(ArrayBlockingQueue<Computer> queue) {
        this.queue = queue;
    }

    @Override
    public void run() {
        for (int i = 1; i <= 20; i++) {
            Computer computer = new Computer();
            if (i % 2 == 0) {
                computer.setMainFrame(i + "号联想主机");

                computer.setScreen(i + "号联想显示器");
                System.out.println("生产了第" + i + "号联想电脑");
                queue.add(computer);
            } else {
                computer.setMainFrame(i + "号华硕主机");
                computer.setScreen(i + "号华硕显示器");
                System.out.println("生产了第" + i + "号华硕电脑");
                queue.add(computer);
            }
        }
    }
}

```

```java
public class Test {
    public static void main(String[] args) {
        ArrayBlockingQueue<Computer> queue = new ArrayBlockingQueue<>(20);
        Producer producer = new Producer(queue);
        Consumer consumer = new Consumer(queue);

        producer.start();
        consumer.start();

    }
}

```

## 16. 相关面试题

> 1. sleep()方法和wait()方法的区别、？
>
> - sleep属于Thread类中的静态方法 wait()属于Object类中的实例方法
> - sleep不会释放锁  wait会释放锁 

> 2. notify() 方法 和 notifyAll() 方法的区别？
>
> - notify() 是随机唤醒一个等待的线程 即 执行了wait方法的线程
> - notifyAll() 是唤醒所有等待的线程 



