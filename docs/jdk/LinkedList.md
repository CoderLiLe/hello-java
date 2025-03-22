# LinkedList

## 类定义&数据结构
### 定义
LinkedList是一种可以在任何位置进行高效地插入和移除操作的有序序列，它是基于双向链表实现的。

### LinkedList的数据结构

![](./asserts/3.1.png)

如上图所示，LinkedList底层使用的双向链表结构，有一个头结点和一个尾结点，双向链表意味着我们可以从头开始正向遍历，或者是从尾开始逆向遍历，并且可以针对头部和尾部进行相应的操作。

### 特性
```text
Doubly-linked list implementation of the List and Deque interfaces. Implements all optional list operations, and permits all elements (including null).
```
linkedList是一个双向链表，并且实现了List和Deque接口中所有的列表操作，并且能存储任何元素，包括null，这里我们可以知道linkedList除了可以当链表使用，还可以当作队列使用，并能进行相应的操作。

```text
All of the operations perform as could be expected for a doubly-linked list. Operations that index into the list will traverse the list from the beginning or the end, whichever is closer to the specified index.
```
这个告诉我们，linkedList在执行任何操作的时候，都必须先遍历此列表来靠近通过index查找我们所需要的的值。

## 类结构图
```java
public class LinkedList<E> extends AbstractSequentialList<E> implements List<E>, Deque<E>, Cloneable, java.io.Serializable
```
![](./asserts/3.2.png)

和 ArrayList 集合一样，LinkedList 集合也实现了Cloneable接口和Serializable接口，分别用来支持克隆以及支持序列化。List 接口也不用多说，定义了一套 List 集合类型的方法规范。

注意，相对于 ArrayList 集合，LinkedList 集合多实现了一个 Deque 接口，这是一个双向队列接口，双向队列就是两端都可以进行增加和删除操作。

## 字段属性
```java
// 链表元素（节点）的个数
transient int size = 0;

/**
 *指向第一个节点的指针
 */
transient Node<E> first;
 
/**  
 *指向最后一个节点的指针
 */
transient Node<E> last;
```

![](./asserts/3.3.png)

注意这里出现了一个 Node 类，这是 LinkedList 类中的一个内部类，其中每一个元素就代表一个 Node 类对象，LinkedList 集合就是由许多个 Node 对象类似于手拉着手构成。

```java
private static class Node<E> {
    
    E item; // 实际存储的元素
    Node<E> next; // 指向上一个节点的引用
    Node<E> prev; // 指向下一个节点的引用

    // 构造函数
    Node(Node<E> prev, E element, Node<E> next) {
        this.item = element;
        this.next = next;
        this.prev = prev;
    }
}
```
![](./asserts/3.4.png)

上图的 LinkedList 是有四个元素，也就是由 4 个 Node 对象组成，size=4，head 指向第一个elementA,tail指向最后一个节点elementD。

## 类构造器

```java
public LinkedList() {

}

public LinkedList(Collection<? extends E> c) {
    this();
    addAll(c);
}
```

LinkedList 有两个构造函数，第一个是默认的空的构造函数，第二个是将已有元素的集合Collection 的实例添加到 LinkedList 中，调用的是 addAll() 方法

注意：LinkedList 是没有初始化链表大小的构造函数，因为链表不像数组，一个定义好的数组是必须要有确定的大小，然后去分配内存空间，而链表不一样，它没有确定的大小，通过指针的移动来指向下一个内存地址的分配。

## 添加元素

### addFirst(E e)

将指定元素添加到链表头
```java
// 将指定的元素附加到链表头节点
public void addFirst(E e) {
    linkFirst(e);
}

private void linkFirst(E e) {
    final Node<E> f = first; // 将头节点赋值给 f
    final Node<E> newNode = new Node<>(null, e, f); // 将指定元素构造成一个新节点，此节点的指向下一个节点的引用为头节点
    first = newNode; // 将新节点设为头节点，那么原先的头节点 f 变为第二个节点
    if (f == null) // 如果第二个节点为空，也就是原先链表是空
        last = newNode; // 将这个新节点也设为尾节点（前面已经设为头节点了）
    else
        f.prev = newNode; // 将原先的头节点的上一个节点指向新节点
    size++; // 节点数加1
    modCount++; // 和ArrayList中一样，iterator和listIterator方法返回的迭代器和列表迭代器实现使用。
}
```

### addLast(E e)和add(E e)

将指定元素添加到链表尾

```java
// 将元素添加到链表末尾
public void addLast(E e) {     
    linkLast(e);
}
  
// 将元素添加到链表末尾
public boolean add(E e) {
    linkLast(e);
    return true;
}
    
void linkLast(E e) {
    final Node<E> l = last; // 将l设为尾节点
    final Node<E> newNode = new Node<>(l, e, null); // 构造一个新节点，节点上一个节点引用指向尾节点l
    last = newNode; // 将尾节点设为创建的新节点
    if (l == null) // 如果尾节点为空，表示原先链表为空
        first = newNode; // 将头节点设为新创建的节点（尾节点也是新创建的节点）
    else
        l.next = newNode; // 将原来尾节点下一个节点的引用指向新节点
    size++; // 节点数加1
    modCount++; // 和ArrayList中一样，iterator和listIterator方法返回的迭代器和列表迭代器实现使用。
}
```

### add(int index, E element)

将指定的元素插入此列表中的指定位置

```java
// 将指定的元素插入此列表中的指定位置
public void add(int index, E element) {
    // 判断索引 index >= 0 && index <= size中时抛出IndexOutOfBoundsException异常
    checkPositionIndex(index);
    
    if (index == size) // 如果索引值等于链表大小
        linkLast(element); // 将节点插入到尾节点
    else
        linkBefore(element, node(index));
}

void linkLast(E e) {     
    final Node<E> l = last; // 将l设为尾节点
    final Node<E> newNode = new Node<>(l, e, null); // 构造一个新节点，节点上一个节点引用指向尾节点l
    last = newNode; // 将尾节点设为创建的新节点
    if (l == null) // 如果尾节点为空，表示原先链表为空
        first = newNode; // 将头节点设为新创建的节点（尾节点也是新创建的节点）
    else
        l.next = newNode; // 将原来尾节点下一个节点的引用指向新节点
    size++; // 节点数加1
    modCount++; // 和ArrayList中一样，iterator和listIterator方法返回的迭代器和列表迭代器实现使用。
}

Node<E> node(int index) {
    if (index < (size >> 1)) { // 如果插入的索引在前半部分
        Node<E> x = first; // 设x为头节点
        for (int i = 0; i < index; i++) // 从开始节点到插入节点索引之间的所有节点向后移动一位
            x = x.next;
        return x;
    } else { // 如果插入节点位置在后半部分
        Node<E> x = last; // 将x设为最后一个节点
        for (int i = size - 1; i > index; i--) // 从最后节点到插入节点的索引位置之间的所有节点向前移动一位
            x = x.prev;
        return x;
    }
}

void linkBefore(E e, Node<E> succ) {
    final Node<E> pred = succ.prev; // 将pred设为插入节点的上一个节点
    final Node<E> newNode = new Node<>(pred, e, succ); // 将新节点的上引用设为pred,下引用设为succ
    succ.prev = newNode; // succ的上一个节点的引用设为新节点
    if (pred == null) // 如果插入节点的上一个节点引用为空
        first = newNode; // 新节点就是头节点
    else
        pred.next = newNode; // 插入节点的下一个节点引用设为新节点
    size++;
    modCount++;
    }
```