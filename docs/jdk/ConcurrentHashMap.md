# ConcurrentHashMap

思考：HashTable是线程安全的，为什么不推荐使用？

HashTable是一个线程安全的类，它使用synchronized来锁住整张Hash表来实现线程安全，即每次锁住整张表让线程独占，相当于所有线程进行读写时都去竞争一把锁，导致效率非常低下。

# ConcurrentHashMap 1.7

在JDK1.7中ConcurrentHashMap采用了数组+分段锁的方式实现。

Segment(分段锁)-减少锁的粒度

ConcurrentHashMap中的分段锁称为Segment，它即类似于HashMap的结构，即内部拥有一个Entry数组，数组中的每个元素又是一个链表,同时又是一个ReentrantLock（Segment继承了ReentrantLock）。

## 存储结构

Java 7 版本 ConcurrentHashMap 的存储结构如图：

![](./asserts/6.1.png)

![](./asserts/6.2.png)

ConcurrnetHashMap 由很多个 Segment 组合，而每一个 Segment 是一个类似于 HashMap 的结构，所以每一个 HashMap 的内部可以进行扩容。但是 Segment 的个数一旦**初始化就不能改变**，默认 Segment 的个数是 16 个，所以可以认为 ConcurrentHashMap 默认支持最多 16 个线程并发。

## 初始化

通过 ConcurrentHashMap 的无参构造探寻 ConcurrentHashMap 的初始化流程。

```java
/**
 * Creates a new, empty map with a default initial capacity (16),
 * load factor (0.75) and concurrencyLevel (16).
 */
public ConcurrentHashMap() {
    this(DEFAULT_INITIAL_CAPACITY, DEFAULT_LOAD_FACTOR, DEFAULT_CONCURRENCY_LEVEL);
}
```

无参构造中调用了有参构造，传入了三个参数的默认值，他们的值是。

```java
/**
 * 默认初始化容量,这个容量指的是Segment 的大小
 */
static final int DEFAULT_INITIAL_CAPACITY = 16;

/**
 * 默认负载因子
 */
static final float DEFAULT_LOAD_FACTOR = 0.75f;

/**
 * 默认并发级别，并发级别指的是Segment桶的个数，默认是16个并发大小
 */
static final int DEFAULT_CONCURRENCY_LEVEL = 16;
```

接着看下这个有参构造函数的内部实现逻辑。

```java
@SuppressWarnings("unchecked")
public ConcurrentHashMap(int initialCapacity,float loadFactor, int concurrencyLevel) {
    // 参数校验
    if (!(loadFactor > 0) || initialCapacity < 0 || concurrencyLevel <= 0)
        throw new IllegalArgumentException();
    // 校验并发级别大小，大于 1<<16，重置为 65536
    if (concurrencyLevel > MAX_SEGMENTS)
        concurrencyLevel = MAX_SEGMENTS;
    // Find power-of-two sizes best matching arguments
    // 2的多少次方
    int sshift = 0;//控制segment数组的大小
    int ssize = 1;
    // 这个循环可以找到 concurrencyLevel 之上最近的 2的次方值
    while (ssize < concurrencyLevel) {
        ++sshift;//代表ssize左移的次数
        ssize <<= 1;
    }
    // 记录段偏移量
    this.segmentShift = 32 - sshift;
    // 记录段掩码
    this.segmentMask = ssize - 1;
    // 设置容量   判断初始容量是否超过允许的最大容量
    if (initialCapacity > MAXIMUM_CAPACITY)
        initialCapacity = MAXIMUM_CAPACITY;
    // c = 容量 / ssize ，默认 16 / 16 = 1，这里是计算每个 Segment 中的类似于 HashMap 的容量
   //求entrySet数组的大小，这个地方需要保证entrySet数组的大小至少可以存储下initialCapacity的容量，假设initialCapacity为33，ssize为16，那么c=2,所以if语句是true，那么c=3,MIN_SEGMENT_TABLE_CAPACITY初始值是2，所以if语句成立，那么cap=4，所以每一个segment的容量初始为4，segment为16，16*4>33成立，entrySet数组的大小也需要是2的幂次方
    int c = initialCapacity / ssize;
    if (c * ssize < initialCapacity)
        ++c;
    int cap = MIN_SEGMENT_TABLE_CAPACITY;
    //Segment 中的类似于 HashMap 的容量至少是2或者2的倍数
    while (cap < c)
        cap <<= 1;
    // create segments and segments[0]
    // 创建 Segment 数组，设置 segments[0]
    Segment<K,V> s0 = new Segment<K,V>(loadFactor, (int)(cap * loadFactor),
                         (HashEntry<K,V>[])new HashEntry[cap]);
    Segment<K,V>[] ss = (Segment<K,V>[])new Segment[ssize];
    UNSAFE.putOrderedObject(ss, SBASE, s0); // ordered write of segments[0]
    this.segments = ss;
}
```

总结一下在 Java 7 中 ConcurrnetHashMap 的初始化逻辑。

1、必要参数校验。

2、校验并发级别 concurrencyLevel 大小，如果大于最大值，重置为最大值。无参构造默认值是 16.

3、寻找并发级别 concurrencyLevel 之上最近的 2 的幂次方值，作为初始化容量大小，默认是 16。

4、记录 segmentShift 偏移量，这个值为【容量 = 2 的N次方】中的 N，在后面 Put 时计算位置时会用到。默认是 32 - sshift = 28.

5、记录 segmentMask，默认是 ssize - 1 = 16 -1 = 15.

6、初始化 segments[0]，默认大小为 2，负载因子 0.75，扩容阀值是 2*0.75=1.5，插入第二个值时才会进行扩容。