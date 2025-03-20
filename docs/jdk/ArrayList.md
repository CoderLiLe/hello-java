# ArrayList源码

## ArrayList类结构图

**ArrayList 是一个用数组实现的集合，支持随机访问，元素有序且可以重复。**

（1）ArrayList 是一种变长的集合类，基于定长数组实现。

（2）ArrayList 允许空值和重复元素，当往 ArrayList 中添加的元素数量大于其底层数组容量时，其会通过扩容机制重新生成一个更大的数组。

（3）ArrayList 底层基于数组实现，所以其可以保证在 O(1) 复杂度下完成随机查找操作。

（4）ArrayList 是非线程安全类，并发环境下，多个线程同时操作 ArrayList，会引发不可预知的异常或错误。

```java
public class ArrayList<E> extends AbstractList<E> implements List<E>, RandomAccess, Cloneable, java.io.Serializable
```

![](./asserts/2.1.png)

① 实现 RandomAccess 接口

这是一个标记接口，一般此标记接口用于 List实现，以表明它们支持快速（通常是恒定时间）的随机访问

② 实现 Cloneable 接口

Cloneable 和 RandomAccess 接口一样也是一个标记接口，接口内无任何方法体和常量的声明，也就是说如果想克隆对象，必须要  实现 Cloneable 接口，表明该类是可以被克隆的。

③ 实现 Serializable 接口

标记接口，表示能被序列化

④ 实现 List 接口

这个接口是 List 类集合的上层接口，定义了实现该接口的类都必须要实现的一组方法

![](./asserts/2.2.png)

## 字段属性
```java
// 集合的默认大小 
private static final int DEFAULT_CAPACITY = 10;
// 空的数组实例 
private static final Object[] EMPTY_ELEMENTDATA = {};
// 这也是一个空的数组实例，和EMPTY_ELEMENTDATA空数组相比是用于了解添加元素时数组膨胀多少
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};
// 存储 ArrayList集合的元素，集合的长度即这个数组的长度
// 1、当 elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA 时将会清空 ArrayList
// 2、当添加第一个元素时，elementData 长度会扩展为 DEFAULT_CAPACITY=10
transient Object[] elementData;
// 表示集合的长度
private int size;
```

## 类构造器

### 无参构造
```java
public ArrayList() {
    this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
```
此无参构造函数将创建一个 DEFAULTCAPACITY_EMPTY_ELEMENTDATA 声明的数组，注意此时初始容量是0，而不是大家以为的 10。

**注意：根据默认构造函数创建的集合，ArrayList list = new ArrayList();此时集合长度是0.**

### 重载：有参构造ArrayList(int initialCapacity)
```java
public ArrayList(int initialCapacity) {
    if (initialCapacity > 0) {
        this.elementData = new Object[initialCapacity];
    } else if (initialCapacity == 0) {
        this.elementData = EMPTY_ELEMENTDATA;
    } else {
        throw new IllegalArgumentException("Illegal Capacity: "+ initialCapacity);
    }
}
```

初始化集合大小创建 ArrayList 集合。当大于0时，给定多少那就创建多大的数组；当等于0时，创建一个空数组；当小于0时，抛出异常。

### 重载：ArrayList(Collection<? extends E> c)

```java
public ArrayList(Collection<? extends E> c) {
    elementData = c.toArray();
    if ((size = elementData.length) != 0) {
        // c.toArray might (incorrectly) not return Object[] (see 6260652)
        if (elementData.getClass() != Object[].class)
                elementData = Arrays.copyOf(elementData, size, Object[].class);
    } else {
        // replace with empty array.
        this.elementData = EMPTY_ELEMENTDATA;
    }
}
```

将已有的集合复制到 ArrayList 集合中

### 思考：无参构造和0长度构造有什么区别
```java
@Test
public void test(){
    // 两种方式构建list，有什么区别？
    ArrayList list1 = new ArrayList();
    ArrayList list2 = new ArrayList(0);

    // 打印对象头
    System.out.println(ClassLayout.parseInstance(list1).toPrintable());
    System.out.println(ClassLayout.parseInstance(list2).toPrintable());

    System.out.println("========");

    // add一个元素之后再来打印试试
    list1.add(1);
    list2.add(1);

    System.out.println(ClassLayout.parseInstance(list1).toPrintable());
    System.out.println(ClassLayout.parseInstance(list2).toPrintable());
}
```

![](./asserts/2.3.png)

原理：

```java
// calculateCapacity
// 每次元素变动，比如add，会调用该函数判断容量情况
private static int calculateCapacity(Object[] elementData, int minCapacity) {
    // 定义default empty数组的意义就在这里！用于扩容时判断当初采用的是哪种构造函数
    if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
        // 如果是无参的构造函数，用的就是该default empty
        // 那么第一次add时候，容量取default和min中较大者
        return Math.max(DEFAULT_CAPACITY, minCapacity);
    }
    // 如果是另外两个构造函数，比如指定容量为5，或者初始参数collection为5
    // 那就直接返回5，一定程度上，节约了内存空间
    return minCapacity;
}
```