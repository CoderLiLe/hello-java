# HashMap源码分析

## 定义
HashMap基于哈希表的Map接口实现，是以key-value存储形式存在，即主要用来存放键值对。HashMap的实现不是同步的，这意味着它不是线程安全的。它的key、value都可以为null。此外，HashMap中的映射不是有序的。

- JDK1.7 HashMap数据结构：数组 + 链表
- JDK1.8 HashMap数据结构：数组 + 链表 / 红黑树
  
思考：为什么1.8之后，HashMap的数据结构要增加红黑树？

## 哈希表
Hash表也称为散列表，也有直接译作哈希表，Hash表是一种根据关键字值（key - value）而直接进行访问的数据结构。也就是说它通过把关键码值映射到表中的一个位置来访问记录，以此来加快查找的速度。在链表、数组等数据结构中，查找某个关键字，通常要遍历整个数据结构，也就是O(N)的时间级，但是对于哈希表来说，只是O(1)的时间级

哈希表，它是通过把关键码值映射到表中一个位置来访问记录，以加快查找的速度。这个映射函数叫做**散列函数**，存放记录的数组叫做**散列表**，只需要O(1)的时间级

![](./asserts/4.1.png)

思考：多个 key 通过散列函数会得到相同的值，这时候怎么办？

解决：

	（1）开放地址法

	（2）链地址法

![](./asserts/4.2.png)

对于开放地址法，可能会遇到二次冲突，三次冲突，所以需要良好的散列函数，分布的越均匀越好。

对于链地址法，虽然不会造成二次冲突，但是如果一次冲突很多，那么会造成子数组或者子链表很长，那么我们查找所需遍历的时间也会很长。

## JDK8前的数据结构
- JDK 8 以前 HashMap 的实现是 **数组+链表**，即使哈希函数取得再好，也很难达到元素百分百均匀分布。
- 当 HashMap 中有大量的元素都存放到同一个桶中时，这个桶下有一条长长的链表，极端情况HashMap 就相当于一个单链表，假如单链表有 n 个元素，遍历的时间复杂度就是 O(n)，完全失去了它的优势。

![](./asserts/4.3.png)

## JDK8后的数据结构

- JDK 8 后 HashMap 的实现是 **数组+链表+红黑树**
- 桶中的结构可能是链表，也可能是红黑树，当链表长度大于阈值(或者红黑树的边界值，默认为8)并且当前数组的长度大于64时，此时此索引位置上的所有数据改为使用红黑树存储。

![](./asserts/4.4.png)

## 类构造器

```java
public class HashMap<K,V> extends AbstractMap<K,V> implements Map<K,V>, Cloneable, Serializable {
```

![](./asserts/4.5.png)

JDK 为我们提供了一个抽象类 AbstractMap ，该抽象类继承 Map 接口，所以如果我们不想实现所有的 Map 接口方法，就可以选择继承抽象类 AbstractMap 。

HashMap 集合实现了 Cloneable 接口以及 Serializable 接口，分别用来进行对象克隆以及将对象进行序列化。

注意：HashMap 类即继承了 AbstractMap 接口，也实现了 Map 接口，这样做难道不是多此一举？
> 据 java 集合框架的创始人Josh Bloch描述，这样的写法是一个失误。在java集合框架中，类似这样的写法很多，最开始写java集合框架的时候，他认为这样写，在某些地方可能是有价值的，直到他意识到错了。显然的，JDK的维护者，后来不认为这个小小的失误值得去修改，所以就这样存在下来了。

## 字段属性
```java
// 序列化和反序列化时，通过该字段进行版本一致性验证
private static final long serialVersionUID = 362498820763181265L;
// 默认 HashMap 集合初始容量为16（必须是 2 的倍数）
static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; // aka 16
// 集合的最大容量，如果通过带参构造指定的最大容量超过此数，默认还是使用此数
static final int MAXIMUM_CAPACITY = 1 << 30;
// 默认的填充因子
static final float DEFAULT_LOAD_FACTOR = 0.75f;
// 当桶(bucket)上的结点数大于这个值时会转成红黑树(JDK1.8新增)
static final int TREEIFY_THRESHOLD = 8;
// 当桶(bucket)上的节点数小于这个值时会转成链表(JDK1.8新增)
static final int UNTREEIFY_THRESHOLD = 6;
/**(JDK1.8新增)  
 * 当集合中的容量大于这个值时，表中的桶才能进行树形化 ，否则桶内元素太多时会扩容，
 * 而不是树形化 为了避免进行扩容、树形化选择的冲突，这个值不能小于 4 * TREEIFY_THRESHOLD
 */
static final int MIN_TREEIFY_CAPACITY = 64;

/**
 * 初始化使用，长度总是 2的幂
 */
transient Node<K,V>[] table;
 
/**  
 * 保存缓存的entrySet（）
 */
transient Set<Map.Entry<K,V>> entrySet;
 
/**
 * 此映射中包含的键值映射的数量。（集合存储键值对的数量）
 */
transient int size;

/**
 * 跟前面ArrayList和LinkedList集合中的字段modCount一样，记录集合被修改的次数
 * 主要用于迭代器中的快速失败
 */
transient int modCount;

/**  
 * 调整大小的下一个大小值（容量*加载因子）。capacity * load factor
 */
int threshold;

/**
 * 散列表的加载因子。
 */
final float loadFactor;
```

下面我们重点介绍上面几个字段：

① **Node<K,V>[] table**

我们说 HashMap 是由数组+链表+红黑树组成，这里的数组就是 table 字段。后面对其进行初始化长度默认是 DEFAULT_INITIAL_CAPACITY= 16。而且 JDK 声明数组的长度总是 2的n次方(一定是合数)，为什么这里要求是合数，一般我们知道哈希算法为了避免冲突都要求长度是质数，这里要求是合数，下面在介绍 HashMap 的hashCode() 方法(散列函数)，我们再进行讲解。

② **size**

集合中存放key-value 的实时对数。

③ **loadFactor**

装载因子，是用来衡量 HashMap 满的程度，计算HashMap的实时装载因子的方法为：size/capacity，而不是占用桶的数量去除以capacity。capacity 是桶的数量，也就是 table 的长度length。

默认的负载因子0.75 是对空间和时间效率的一个平衡选择，建议大家不要修改，除非在时间和空间比较特殊的情况下，如果内存空间很多而又对时间效率要求很高，可以降低负载因子loadFactor 的值；相反，如果内存空间紧张而对时间效率要求不高，可以增加负载因子 loadFactor 的值，这个值可以大于1。

④ **threshold**

计算公式：capacity * loadFactor。这个值是当前已占用数组长度的最大值。过这个数目就重新resize(扩容)，扩容后的 HashMap 容量是之前容量的两倍

## 构造函数
### 默认无参构造函数
```java
/**
 * 默认构造函数，初始化加载因子loadFactor = 0.75
 */
public HashMap() {     
    this.loadFactor = DEFAULT_LOAD_FACTOR; 
}
```

### 指定初始容量的构造函数
```java
/**
 *
 * @param initialCapacity 指定初始化容量
 * @param loadFactor 加载因子 0.75
 */
public HashMap(int initialCapacity, float loadFactor) {     
    // 初始化容量不能小于 0 ，否则抛出异常
    if (initialCapacity < 0)
        throw new IllegalArgumentException("Illegal initial capacity: " + initialCapacity);
    // 如果初始化容量大于2的30次方，则初始化容量都为2的30次方
    if (initialCapacity > MAXIMUM_CAPACITY)
        initialCapacity = MAXIMUM_CAPACITY;
    // 如果加载因子小于0，或者加载因子是一个非数值，抛出异常
    if (loadFactor <= 0 || Float.isNaN(loadFactor))
        throw new IllegalArgumentException("Illegal load factor: " + loadFactor);
    this.loadFactor = loadFactor;
    this.threshold = tableSizeFor(initialCapacity);
}

// 返回大于等于initialCapacity的最小的二次幂数值。 
// >>> 操作符表示无符号右移，高位取0。
// | 按位或运算 
static final int tableSizeFor(int cap) {
    int n = cap - 1;
    n |= n >>> 1;
    n |= n >>> 2;
    n |= n >>> 4;
    n |= n >>> 8;
    n |= n >>> 16;
    return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
}
```

## 确定哈希桶数组索引位置

前面我们讲解哈希表的时候，我们知道是用散列函数来确定索引的位置。散列函数设计的越好，使得元素分布的越均匀。

HashMap 是数组+链表+红黑树的组合，我们希望在有限个数组位置时，尽量每个位置的元素只有一个，那么当我们用散列函数求得索引位置的时候，我们能马上知道对应位置的元素是不是我们想要的，而不是要进行链表的遍历或者红黑树的遍历，这会大大优化我们的查询效率。

我们看 HashMap 中的哈希算法：

```java
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}

// 这一步是在后面添加元素putVal()方法中进行位置的确定
i = (table.length - 1) & hash;
```

主要分为三步：

① 取 hashCode 值： key.hashCode()

② 高位参与运算：h>>>16

③ 取模运算：(n-1) & hash

这里获取 hashCode() 方法的值是变量，但是我们知道，对于任意给定的对象，只要它的 hashCode() 返回值相同，那么程序调用 hash(Object key) 所计算得到的 hash码 值总是相同的。

为了让数组元素分布均匀，我们首先想到的是把获得的 hash码对数组长度取模运算( hash%length)，但是计算机都是二进制进行操作，取模运算相对开销还是很大的，那该如何优化呢？

HashMap 使用的方法很巧妙，它通过 hash & (table.length -1)来得到该对象的保存位，前面说过 HashMap 底层数组的长度总是2的n次方，这是HashMap在速度上的优化。当 length 总是2的n次方时，hash & (length-1)运算等价于对 length 取模，也就是 hash%length，但是&比%具有更高的效率。比如 n % 32 = n & (32 -1)

**这也解释了为什么要保证数组的长度总是2的n次方。**

再就是在 JDK1.8 中还有个高位参与运算，hashCode() 得到的是一个32位 int 类型的值，通过hashCode()的高16位 异或 低16位实现的：(h = k.hashCode()) ^ (h >>> 16)，主要是从速度、功效、质量来考虑的，这么做可以在数组table的length比较小的时候，也能保证考虑到高低Bit都参与到Hash的计算中，同时不会有太大的开销。

下面举例说明下，n为table的长度：

![](./asserts/4.6.png)