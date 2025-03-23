# HashMap源码分析

## 定义
HashMap基于哈希表的Map接口实现，是以key-value存储形式存在，即主要用来存放键值对。HashMap的实现不是同步的，这意味着它不是线程安全的。它的key、value都可以为null。此外，HashMap中的映射不是有序的。

- JDK1.7 HashMap数据结构：数组 + 链表
- JDK1.8 HashMap数据结构：数组 + 链表 / 红黑树
  
思考：为什么1.8之后，HashMap的数据结构要增加红黑树？