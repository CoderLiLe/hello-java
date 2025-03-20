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