# 集合

- [1. Collection接口](#1-collection接口)
  - [1.1 List接口](#11-list接口)
    - [1.1.1 ArrayList](#111-arraylist)
      - [常用方法](#常用方法)
      - [遍历方式](#遍历方式)
      - [数据结构](#数据结构)
    - [1.1.2 Vector](#112-vector)
    - [1.1.3 LinkedList](#113-linkedlist)
      - [常用方法](#常用方法-1)
      - [遍历方式](#遍历方式-1)
      - [数据结构](#数据结构-1)
  - [1.2 Set接口](#12-set接口)
    - [1.2.1 HashSet](#121-hashset)
    - [1.2.2 LinkedHashSet](#122-linkedhashset)
    - [1.2.3 TreeSet](#123-treeset)
- [2.Map接口](#2map接口)
  - [2.1 HashMap](#21-hashmap)
    - [常用方法](#常用方法-2)
    - [遍历方式](#遍历方式-2)
    - [数据结构](#数据结构-2)
    - [2.2Hashtable](#22hashtable)
  - [2.3 Properties](#23-properties)
  - [2.4 LinkedHashMap](#24-linkedhashmap)
  - [2.5 TreeMap](#25-treemap)
- [3. Set集合 HashMap中的键  去除重复的依据？](#3-set集合-hashmap中的键--去除重复的依据)


## 1. Collection接口

### 1.1 List接口

#### 1.1.1 ArrayList

##### 常用方法

> Collection
>
> List
>
> ArrayList
>
>
> 常用方法：
>
> add(E e) 添加元素  添加在末尾
>
> add(int index,E e) 在指定位置添加元素
>
> clear() 从列表中删除所有元素。
>
> contains(Object o) 如果此列表包含指定的元素，则返回 true 。
>
> get(int index) 返回此列表中指定位置的元素。
>
> indexOf(Object o) 返回此列表中指定元素的第一次出现的索引，如果此列表不包含元素，则返回-1。
>
> isEmpty() 如果此列表不包含元素，则返回 true 。
>
> iterator() 以正确的顺序返回该列表中的元素的迭代器。
>
> E remove(int index) 删除该列表中指定位置的元素。
>
> boolean remove(Object o) 从列表中删除指定元素的第一个出现（如果存在）。
>
> set(int index, E element) 用指定的元素替换此列表中指定位置的元素。
>
> size() 返回此列表中的元素数。
>
>
> 泛型：用于统一集合中的数据类型

```java
public class TestArrayListMethod {
    public static void main(String[] args) {
        ArrayList arrayList = new ArrayList();

        arrayList.add("a");
        arrayList.add(100);
        arrayList.add(2.5);
        arrayList.add(2.5F);
        arrayList.add(true);
        arrayList.add('A');
        arrayList.add(new int[]{1,2,3,4,5});

        System.out.println("-------------------------------------------------------");

        ArrayList<String> list = new ArrayList<String>();

        list.add("a");
        list.add("b");
        list.add("hello");
        list.add("world");
        list.add("6666");
        list.add("f");
        list.add("a");

        System.out.println("集合的长度，元素的个数：" + list.size());

        list.add(1, "世界你好");

        System.out.println("插入一个元素，元素的个数：" + list.size());

        System.out.println("下标0元素为：" +  list.get(0));
        System.out.println("下标1元素为：" +  list.get(1));
        System.out.println("下标2元素为：" +  list.get(2));


        System.out.println("删除下标为0的元素：" + list.remove(0));
        System.out.println("删除内容为'a'的元素：" + list.remove("a"));
        System.out.println("删除内容为'a'的元素：" + list.remove("a"));

        System.out.println("原来0的位置元素为：" + list.set(0, "123456789"));;

        System.out.println("下标0元素为：" +  list.get(0));

        System.out.println("是否包含'a'元素" + list.contains("a"));
        System.out.println("是否包含'b'元素" + list.contains("b"));

        System.out.println("集合是否为空：" + list.isEmpty());

        list.clear();

        System.out.println("集合是否为空：" + list.isEmpty());

        System.out.println(list.size());
    }
}

```



##### 遍历方式

> ArrayList遍历方式：三种
>
> 方式1：普通for循环遍历
>
> 方式2：迭代器遍历
>
> 方式3：增强for循环遍历

```java
public class TestArrayListForeach {
    public static void main(String[] args) {
        List<Integer> list = new ArrayList<Integer>(); // 热插拔思想

        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);
        list.add(5);

        // 方式1：普通for循环遍历
        for(int i = 0;i < list.size();i++){
            System.out.println(list.get(i));
        }

        System.out.println("----------------------------------------------");


        // 方式2：迭代器遍历
        // 迭代器是无法保证顺序 集合中的元素将原封不动的保存在迭代器对象中
        // 迭代器是没有下标的概念 每次遍历先查询迭代器对象中还有没有元素 如果有 则取出  然后继续遍历
        Iterator<Integer> iterator = list.iterator();
        while(iterator.hasNext()){
            System.out.println(iterator.next());
        }
        System.out.println("----------------------------------------------");

        // 方式3：增强for循环遍历 底层实现还是迭代器 是JDK1.5新增的内容 属于对迭代书写格式的简化

        for(Integer i : list){
            System.out.println("i = " + i);
        }


        System.out.println("----------------------------------------------");
        int [] nums = {1,2,3,4,5};

        for(int a : nums){
            System.out.println("a = " + a);
        }

        for (int num : nums) {
            System.out.println("num = " + num);
        }
    }
}

```



##### 数据结构

> ArrayList 集合特点：有序 有下标 允许重复 允许null元素 线程不安全
>
> 当我们调用无参构造，帮我们维护一个长度为0的空数组 注释描述为长度为10的数组 是错误的
>
> 当我们第一次添加元素 才将数组的长度改为10
>
> 集合扩容：为原来数组长度的1.5倍
>
>
> 增删改查效率：
>
> 查询 和 修改 快
>
> 添加如果需要扩容的、插入元素的情况 效率较低 因为需要复制数组 或者 移动元素
>
> 删除需要移动元素的情况 效率低

#### 1.1.2 Vector

> ArrayList 和 Vector的区别？
>
> ArrayList线程不安全  Vector线程安全
>
> ArrayList无参构造维护长度为0空数组 Vector无参构造维护长度为10的数组
>
> ArrayList扩容1.5倍  Vector扩容2倍
>
> ArrayList不允许指定增量 Vector可以指定增量
>
>
> 其他：遍历方式全部相同    

```java
public class TestVector {
    public static void main(String[] args) {
        Vector<String> list = new Vector<String>();

        list.add("a");
        list.add("b");
        list.add("hello");
        list.add("world");
        list.add("6666");
        list.add("f");
        list.add("a");

        System.out.println("集合的长度，元素的个数：" + list.size());

        list.add(1, "世界你好");


        System.out.println("插入一个元素，元素的个数：" + list.size());

        System.out.println("下标0元素为：" +  list.get(0));
        System.out.println("下标1元素为：" +  list.get(1));
        System.out.println("下标2元素为：" +  list.get(2));


        System.out.println("删除下标为0的元素：" + list.remove(0));
        System.out.println("删除内容为'a'的元素：" + list.remove("a"));
        System.out.println("删除内容为'a'的元素：" + list.remove("a"));

        System.out.println("原来0的位置元素为：" + list.set(0, "123456789"));;

        System.out.println("下标0元素为：" +  list.get(0));

        System.out.println("是否包含'a'元素" + list.contains("a"));
        System.out.println("是否包含'b'元素" + list.contains("b"));



        System.out.println("集合是否为空：" + list.isEmpty());

        list.clear();

        System.out.println("集合是否为空：" + list.isEmpty());

        System.out.println(list.size());

    }
}

```



#### 1.1.3 LinkedList

##### 常用方法

>  Collection
>
> List Deque
>
> LinkedList
>
> 除了跟ArrayList相同的方法以外 此类还单独提供了专门用于操作头部和尾部的方法
>
>
> add(E e) 添加元素  添加在末尾
>
> add(int index,E e) 在指定位置添加元素
>
> addFirst() 添加在链表的头部
>
> addLast() 添加在链表的尾部
>
> clear() 从列表中删除所有元素。
>
> contains(Object o) 如果此列表包含指定的元素，则返回 true 。
>
> get(int index) 返回此列表中指定位置的元素。
>
> getFirst() 获取链表的头部
>
> getLast() 获取链表的尾部
>
> indexOf(Object o) 返回此列表中指定元素的第一次出现的索引，如果此列表不包含元素，则返回-1。
>
> isEmpty() 如果此列表不包含元素，则返回 true 。
>
> iterator() 以正确的顺序返回该列表中的元素的迭代器。
>
> E remove(int index) 删除该列表中指定位置的元素。
>
> removeFirst() 删除链表的头部
>
> removeLast() 删除链表的尾部
>
> boolean remove(Object o) 从列表中删除指定元素的第一个出现（如果存在）。
>
> set(int index, E element) 用指定的元素替换此列表中指定位置的元素。
>
> size() 返回此列表中的元素数。

```java
public class TestLinkedListMethod {
    public static void main(String[] args) {
        LinkedList<String> list  = new LinkedList<String>();

        list.add("a");
        list.add("b");
        list.add("c");

        list.addFirst("hello");
        list.addLast("World");
        list.add(1, "666");
        System.out.println(list.size());

        System.out.println("-------------------------------------------");

        System.out.println(list.get(0));
        System.out.println(list.getFirst());
        System.out.println(list.get(1));
        System.out.println(list.get(2));
        System.out.println(list.get(3));
        System.out.println(list.get(4));
        System.out.println(list.get(5));
        System.out.println(list.getLast());
        System.out.println("-------------------------------------------");
        System.out.println(list.remove());
        System.out.println( list.remove(0));

        System.out.println(list.removeFirst());
        System.out.println(list.removeLast());
        System.out.println("-------------------------------------------");

        System.out.println(list.get(0));
        System.out.println(list.get(1));

        System.out.println(list.set(0, "123456"));
        System.out.println(list.get(0));

        System.out.println(list.size());

        System.out.println("是否包含'123456'" + list.contains("123456"));

        list.clear();

        System.out.println(list.isEmpty());
    }
}

```



##### 遍历方式

> LinkedList三种遍历方式
>
> 1.普通for循环遍历
>
> 2.迭代器遍历
>
> 3.增强for循环遍历
>
> 不推荐使用普通for循环遍历LinkedList

```java
public class TestLinkedListForeach {
    public static void main(String[] args) {
        LinkedList<Integer> list = new LinkedList<Integer>();

        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);
        list.add(5);
        // 1.普通for循环遍历
        for(int i = 0;i < list.size();i++){
            System.out.println(list.get(i));
        }

        System.out.println("--------------------------------");
        // 2.迭代器遍历
        Iterator<Integer> iterator = list.iterator();
        while(iterator.hasNext()){
            System.out.println(iterator.next());
        }

        System.out.println("--------------------------------");
        //  3.增强for循环遍历

        for (Integer i : list) {
            System.out.println("i = " + i);
        }




    }
}

```



##### 数据结构

![](img/双向链表.png)

> LinkedList集合特点：有序 空间不连续 有下标 可以重复 允许null元素 线程不安全
> *
>
> 数据结构：双向链表 没有初始大小 没有上限大小 不需要扩容
>
> 查询、修改 效率低：当我们根据下标查询某一个元素 必须先通过其相邻的元素 才能获取到我们需要的元素
>
> 所以 根据下标查询效率非常低   修改也需要先查询 所以效率也低
>
> 删除 ：不需要移动元素 只需要将删除元素的左右两边的元素进行链接即可 但是因为涉及到查询 所以效率也很低
>
> 添加 ：不需要扩容 也不需要复制元素 所以效率高
>
>
> LinkedList对get()方法优化：当查询的下标小于元素个数中间值 则从前往后查找
>
> 如果查询的下标大于等于元素个数中间值 则从后往前查找



### 1.2 Set接口

#### 1.2.1 HashSet

>  Collection
>
> Set
>
> HashSet ： 底层实现为HashMap 我们添加到HashSet中的元素 将被JDK添加到HashMap中 键的位置 值默认以null填充
>
>
> 此类中没有单个查询的方法  也没有修改的方法
>
> add(E e) 添加元素
>
> clear() 删除所有元素
>
> contains(Object o) 查看是否包含某个元素
>
> isEmpty() 判断集合长度是否为0
>
> iterator() 获取集合迭代器
>
> remove(Object o)  删除元素
>
> size() 获取元素个数

```java
public class TestHashSet {
    public static void main(String[] args) {
        // 创建集合对象
        HashSet<String> set = new HashSet<String>();

        // 添加元素 如果元素已存在 将添加失败 返回值为false  添加成功 返回值为true
        System.out.println(set.add("abc1"));
        System.out.println(set.add("abc2"));
        System.out.println(set.add("abc3"));
        System.out.println(set.add("abc4"));
        System.out.println(set.add("abc5"));

        System.out.println(set.size()); // 打印集合长度

        System.out.println(set.contains("abc1")); // 查看是否包含 "abc1" 元素

        System.out.println("是否删除成功'abc1'元素：" + set.remove("abc1"));

        System.out.println(set.contains("abc1")); // 查看是否包含 "abc1" 元素

        System.out.println("-------------------------------------------");

        // 遍历方式 2种  因为没有下标 也 没有键
        for(String element : set){
            System.out.println("element = " + element);
        }

        System.out.println("-------------------------------------------");

        Iterator<String> iterator = set.iterator();
        while(iterator.hasNext()){
            System.out.println(iterator.next());
        }
        System.out.println("-------------------------------------------");

        set.clear();

        System.out.println("集合长度是否为0:" +set.isEmpty());
    }
}

```



#### 1.2.2 LinkedHashSet

>  LinkedHashSet 有序的Set集合 顺序为根据元素插入的顺序 继承自 HashSet 底层实现为LinkedHashMap
>
> 所以 HashSet中的方法 都可以直接使用

```java
public class TestLinkedHashSet {
    public static void main(String[] args) {
        // 创建集合对象
        LinkedHashSet<String> set = new LinkedHashSet<String>();

        // 添加元素 如果元素已存在 将添加失败 返回值为false  添加成功 返回值为true
        System.out.println(set.add("abc1"));
        System.out.println(set.add("abc4"));
        System.out.println(set.add("abc5"));
        System.out.println(set.add("abc2"));
        System.out.println(set.add("abc3"));

        System.out.println(set.size()); // 打印集合长度

        System.out.println(set.contains("abc1")); // 查看是否包含 "abc1" 元素

        System.out.println("是否删除成功'abc1'元素：" + set.remove("abc1"));

        System.out.println(set.contains("abc1")); // 查看是否包含 "abc1" 元素

        System.out.println("-------------------------------------------");

        // 遍历方式 2种  因为没有下标 也 没有键
        // 增强for循环
        for(String element : set){
            System.out.println("element = " + element);
        }

        System.out.println("-------------------------------------------");

        // 迭代器遍历
        Iterator<String> iterator = set.iterator();
        while(iterator.hasNext()){
            System.out.println(iterator.next());
        }
        System.out.println("-------------------------------------------");

        set.clear();

        System.out.println("集合长度是否为0:" +set.isEmpty());
    }
}

```



#### 1.2.3 TreeSet

> TreeSet 有序的Set集合 顺序为根据元素比较的顺序  底层实现为TreeMap  最终父接口为 Set接口 所以 Set接口中的方法
>
> 都可以直接使用
>
> 我们可以根据构造方法来指定比较器

```java
public class TestTreeSet {
    public static void main(String[] args) {
        // 创建对象
        TreeSet<String> set = new TreeSet<String>();

        // 添加元素
        set.add("a");
        set.add("ad");
        set.add("ae");
        set.add("ab");
        set.add("ac");
        set.add("af");

        // 增强for循环遍历
        for (String s : set) {
            System.out.println("s = " + s);

        }


        System.out.println("---------------------------------------------------------");

        // 创建对象
        TreeSet<Student> stuSet = new TreeSet<>();
        // 创建学生对象 作为添加元素
        Student stu1 = new Student("赵四",26);
        Student stu2 = new Student("广坤",24);
        Student stu3 = new Student("大拿",22);
        Student stu4 = new Student("小宝",23);


        // 添加元素
        stuSet.add(stu1);
        stuSet.add(stu2);
        stuSet.add(stu3);
        stuSet.add(stu4);

        // 打印集合长度
        System.out.println(stuSet.size());

        System.out.println("---------------------------------------------------------");

        // 创建集合对象 指定比较器对象   
        TreeSet<Person> personSet = new TreeSet<>(new PersonComparator());
        // 创建Person对象 作为添加元素
        Person p1 = new Person("赵四", 188);
        Person p2 = new Person("小宝", 199);
        Person p3 = new Person("刘能", 155);
        Person p4 = new Person("大拿", 175);
        
        // 添加元素 
        personSet.add(p1);
        personSet.add(p2);
        personSet.add(p3);
        personSet.add(p4);

        // 打印集合长度 
        System.out.println(personSet.size());
    }
}

```



## 2.Map接口

### 2.1 HashMap

#### 常用方法

> HashMap常用方法 ：
>
> values() : 获取集合中所有的值
>
> size() ：返回元素个数
>
> replace(K key, V value) 替换元素
>
> remove(Object key) 删除元素
>
> put(K key, V value) 添加元素
>
> keySet()  获取所有的键的组合
>
> isEmpty() 判断集合是否为空
>
> get(Object key) 获取元素
>
> entrySet() 获取所有键值对的组合
>
> containsValue(Object value)是否包含某个值
>
> containsKey(Object key) 是否包含某个键
>
> clear() 清空集合

```java
public class TestHashMapMethod {
    public static void main(String[] args) {
        HashMap<String,String> map = new HashMap<String,String>();

        map.put("CN", "中国");
        map.put("RU", "俄罗斯");
        map.put("US", "美国");
        map.put("JP", "小日本");
        map.put("KR", "小棒棒");


        System.out.println(map.get("CN"));

        map.put("CN", "中华人民共和国");

        System.out.println(map.get("CN"));

        System.out.println(map.size());

        System.out.println("删除元素的值为：" + map.remove("JP"));

        map.replace("KR", "小西巴");

        System.out.println(map.get("KR"));

        System.out.println(map.containsKey("KR"));

        System.out.println(map.containsValue("小日本"));

        map.clear();

        System.out.println(map.isEmpty());
    }
}

```



#### 遍历方式

> 遍历HashMap 6种方式
>
> 1.获取所有的键 根据键获取值
>
> 2.获取所有的值
>
> 3.获取所有的键值对的组合
>
> 4.获取所有的键的迭代器
>
> 5.获取所有的值的迭代器
>
> 6.获取所有的键值对组合的迭代器

```java
public class TestHashMapForeach {
    public static void main(String[] args) {
        HashMap<String,String> map = new HashMap<String,String>();
        map.put("CN", "中国");
        map.put("RU", "俄罗斯");
        map.put("US", "美国");
        map.put("JP", "小日本");
        map.put("KR", "小棒棒");

        // 1.获取所有的键 根据键获取值
        Set<String> keys = map.keySet();
        for(String key : keys){
            System.out.println(key + "====" + map.get(key));
        }

        System.out.println("----------------------------------------------------");

        // 2.获取所有的值

        Collection<String> values = map.values();
        for(String value : values){
            System.out.println(value);
        }

        System.out.println("----------------------------------------------------");
        //  3.获取所有的键值对的组合
        Set<Map.Entry<String, String>> entries = map.entrySet();

        for (Map.Entry<String, String> entry : entries) {
            String key = entry.getKey();
            String value = entry.getValue();

            System.out.println(key + "====" + value);
        }

        System.out.println("----------------------------------------------------");

        // 4.获取所有的键的迭代器

        Iterator<String> iterator = map.keySet().iterator();

        while(iterator.hasNext()){
            String key = iterator.next();
            System.out.println(key + "====" + map.get(key));
        }

        System.out.println("----------------------------------------------------");
        // 5.获取所有的值的迭代器
        Iterator<String> iterator1 = map.values().iterator();

        while(iterator1.hasNext()){
            System.out.println(iterator1.next());
        }
        System.out.println("----------------------------------------------------");

        // 6.获取所有的键值对组合的迭代器

        Iterator<Map.Entry<String, String>> iterator2 = map.entrySet().iterator();

        while(iterator2.hasNext()){
            Map.Entry<String, String> entry = iterator2.next();

            System.out.println("entry = " + entry);

        }
    }
}

```



#### 数据结构

![](img/hashmap内存图.png)

> 回顾我们之前所学习的数据结构：
>
> ArrayList ： 数组结构    空间连续    查询 修改 快 添加 删除 慢
>
> LinkedList：双向链表结构   空间不连续 查询 修改 慢  添加 删除 快
>
>
> HashMap数据结构
>
> JDK1.7 数组 + 单向链表
>
> JDK1.8 数组 + 单向链表 + 红黑树
>
> HashMap集合特点：无序 没有下标 允许重复的值 但是不允许重复的键 允许null的键以及null的值  线程不安全
>
> 增删改查效率 通常情况下是比较高的  
>
> HashMap中的每个元素是一个Node对象  属于Entry接口的实现类 所以我们也称HashMap中的元素为Entry对象
>
> 每个Node对象中包含四部分(四个属性)：key值、value值、根据key计算出来的hash值、下一个元素的引用next
>
>
> 元素添加过程：当我们第一次添加元素 底层初始化长度为16的数组 根据hash值对数组长度-1(第一次 hash值 & (length - 1 : 15) ) 进行&与运算
>
> 得到的整数表示存放数组中的下标(0~15)
>
> 如果此下标为值为null 则直接存放
>
> 如果此下标位置不为null 则先判断是否为相同的key (判断依据：使用两个key进行equals以及hashCode比较  equals比较为true hashCode相同则认为是相同的key)
>
> 如果为相同的key 则直接覆盖
>
> ​	如果不为相同的key 判断当前节点为树节点还是链表节点
>
> ​		如果为树节点 则添加在树中
>
> ​		如果为链表 则添加在链表的末尾
>
>
>
> 转换红黑树机制：当链表的长度大于8 并且数组的长度大于64 将单向链表转换为红黑树
>
> 取消树化的机制：当链表的元素个数小于6 将红黑树转换为单向链表
>
> HashMap扩容机制：当数组的使用率达到75%就扩容  扩容为数组扩容2倍



> 了解：
>
> 虽然JDK8中加入了红黑树 但是 数组 +  单向链表 依然是HashMap中的数据结构常态
>
> 因为转换为红黑树的概率是非常低的 低于千万分之一
>
>
> 扩容以后会对数组中的元素进行重新排列 排列规则为继续使用hash值对新的长度-1进行&与运算
>
> 最终有两种结果：
>
> 1.继续保存在原来的位置
>
> 2.移动到原来的位置加上扩容的长度的位置

> 红黑树特点
>
> 1.每个节点只能是红色或者黑色。
>
>  2.根节点必须是黑色。
>
>  3.红色的节点，它的叶节点只能是黑色。
>
>  4.从任一节点到其每个叶子的所有路径都包含相同数目的黑色节点。
>
> 由以上四个特性我们可以看出一些红黑树的特点：
>
> ​        从根基节点到最远叶节点的路径（最远路径）肯定不会大于根基节点到最近节点的路径（最短路径）的两倍长。这是因为性质3保证了没有相连的红色节点，性质4保证了从这个节点出发的不管是哪一条路径必须有相同数目的黑色节点，这也保证了有一条路径不能比其他任意一条路径的两倍还要长。

#### 2.2Hashtable

> HashMap和Hashtable的区别？
>
> - HashMap是线程不安全的
> - Hashtable线程安全
> - HashMap使用懒加载思想 当我们第一次添加元素 将初始化长度为16的数组
> - Hashtable在调用无参构造即初始化长度为11数组
> - HashMap扩容为2倍
> - Hashtable扩容为2倍 +1
> - HashMap使用与运算获取应该存放的数组的下标
> - Hashtable使用取余运算获取应该存放的数组的下标
> - 与运算效率更高  
>
>
> 除以上区别以外 方法 遍历方式 完全一样

```java
public class TestHashtable {
    public static void main(String[] args) {
        Hashtable<String,String> map = new Hashtable<String,String>();

        map.put("CN", "中国");
        map.put("KR", "韩国");

        System.out.println(map.get("CN"));

        System.out.println("删除元素的值为：" + map.remove("JP"));

        map.replace("KR", "小西巴");

        System.out.println(map.get("KR"));

        map.clear();

        System.out.println(map.isEmpty());
    }
}
```



### 2.3 Properties

> Properties类用于后续读取配置文件信息  属于Hashtable的子类
>
> 因为继承自Hashtable 所以 可以直接访问父类的 put或者 putAll方法
>
> 但是不推荐使用 因为Properties类存在的意义在于 只希望用户添加键以及值都为字符串的数据
>
> 所以应该使用setProperty()方法添加数据

```java
public class TestProperties {
    public static void main(String[] args) {
        // 获取系统相关的所有的属性
        Properties properties = System.getProperties();

        // 调用list方法 传入 System.out参数 表示使用System.out 进行打印所有的系统信息
        properties.list(System.out);


        // 创建Properties对象
        Properties pro = new Properties();


        // 调用setProperty方法添加数据
        pro.setProperty("a1", "b1");
        pro.setProperty("a2", "b2");
        pro.setProperty("a3", "b3");
        pro.setProperty("a4", "b4");
        pro.setProperty("a5", "b5");

        System.out.println("-------------------------");

        // 调用getProperty() 方法 根据键 获取数据
        System.out.println(pro.getProperty("a1"));

        // 调用list方法 传入 System.out参数 表示使用System.out 进行打印所有的pro对象信息
        pro.list(System.out);
    }
}

```



### 2.4 LinkedHashMap

> LinkedHashMap一个有序的Map集合 顺序为添加顺序 继承自HashMap 所以
>
> 父类中的方法 依然可以正常使用
>
>
> 常用方法 以及 遍历方式 与HashMap完全一致

```java
public class TestLinkedHashMap {
    public static void main(String[] args) {
        // 创建LinkedHashMap对象
        LinkedHashMap<String,Integer> map = new LinkedHashMap<>();
        // 添加元素
        map.put("d", 4);
        map.put("b", 2);
        map.put("c", 3);
        map.put("e", 5);
        map.put("g", 7);
        map.put("a", 1);
        map.put("f", 6);

        // 调用entrySet方法 获取到map集合中所有的元素  返回值为set集合
        Set<Map.Entry<String, Integer>> entries = map.entrySet();

        // 遍历集合 Set集合 无序 只能通过迭代器 或者 增强for循环遍历
        for (Map.Entry<String, Integer> entry : entries) {
            System.out.println(entry); // 直接打印entry对象 调用此对象的toString方法 
        }
    }
}

```



### 2.5 TreeMap

> TreeMap 有序的Map集合 顺序为根据键比较的顺序
>
> 常用方法 、遍历方式  与HashMap完全相同

```java
public class TestTreeMap {
    public static void main(String[] args) {
        TreeMap<Integer, String> map = new TreeMap<>();

        map.put(562, "a");
        map.put(10, "a");
        map.put(20, "a");
        map.put(147, "a");
        map.put(258, "a");
        map.put(666, "a");

        // 调用entrySet()方法 获取到 所有的元素集合 返回值为Set集合
        Set<Map.Entry<Integer, String>> entries = map.entrySet();

        // 增强for循环遍历
        for (Map.Entry<Integer, String> entry : entries) {

            System.out.println(entry); // 直接调用entry对象的toString方法
        }
    }
}

```

> 如果需要使用自定义的数据类型作为TreeMap的键 则必须实现Comparable接口 重写 compareTo方法
>
> 或者 自定义比较器 实现 Comparator接口

```java
/**
 *  实现Comparable接口 泛型书写为Student 表示比较的对象为Student类型的
 */
public class Student implements  Comparable<Student>{
    private String name;
    private int age;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public Student() {
    }

    public static void main(String[] args) {
        TreeMap<Student,String> map = new TreeMap<Student,String>();
        // 调用有参构造创建对象
        Student stu1 = new Student("赵四",26);
        Student stu2 = new Student("广坤",24);
        Student stu3 = new Student("大拿",22);
        Student stu4 = new Student("小宝",23);

        // 添加元素
        map.put(stu1,"a");
        map.put(stu2,"b");
        map.put(stu3,"c");
        map.put(stu4,"d");

        // 调用方法 获取所有的 元素 集合
        Set<Map.Entry<Student, String>> entries = map.entrySet();

        // 增强for循环遍历
        for (Map.Entry<Student, String> entry : entries) {
            System.out.println("entry = " + entry); // 直接打印对象
        }


    }

    @Override
    public String toString() {
        return "Student{" +
                "name='" + name + '\'' +
                ", age=" + age +
                '}';
    }

    /**
     *  重写 compareTo方法  自定义比较规则
     * @param stu the object to be compared.
     * @return
     */
    @Override
    public int compareTo(Student stu) {
//        if(this.getAge() > stu.getAge()){ // 当前对象的年龄大于传入对象的年龄
//            return 1; // 返回正数
//        }else if(this.getAge() < stu.getAge()){ // 当前对象的年龄小于传入对象的年龄
//            return -1; // 返回负数
//        }
//        return 0; // 以上条件都不成立 表示两个对象的年龄相等 则 返回0


      // return  this.getAge() > stu.getAge() ? 1 :  (this.getAge() < stu.getAge() ? -1  : 0) ;
       return stu.getAge() - this.getAge();
    }
}

```

> 自定义Person类比较器 实现 Comparator接口
>
>
> Comparable 接口 和  Comparator接口的区别？
>
> Comparable接口属于自然排序 (直接在本类中定义比较规则)
>
> Comparator接口属于非自然排序 (需要单独定义类来编写比较规则)
>
>
> 如果我们不能修改比较对象类 则需要单独编写比较器来实现对象比较 可以使用
>
> Comparator接口

```java
public class Person {
    private String name;
    private double height;

    public Person(String name, double height) {
        this.name = name;
        this.height = height;
    }

    public Person() {
    }

    @Override
    public String toString() {
        return "Person{" +
                "name='" + name + '\'' +
                ", height=" + height +
                '}';
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public double getHeight() {
        return height;
    }

    public void setHeight(double height) {
        this.height = height;
    }
}

```

```java
/**
 *  自定义Person类比较器 实现 Comparator接口
 *
 *  Comparable 接口 和  Comparator接口的区别？
 *  Comparable接口属于自然排序 (直接在本类中定义比较规则)
 *  Comparator接口属于非自然排序 (需要单独定义类来编写比较规则)
 *
 *  如果我们不能修改比较对象类 则需要单独编写比较器来实现对象比较 可以使用
 *  Comparator接口
 *
 */
public class PersonComparator implements Comparator<Person> {
    /**
     *  重写 compare方法  自定义比较规则  最终返回值为int类型
     * @param p1 the first object to be compared.
     * @param p2 the second object to be compared.
     * @return
     */
    @Override
    public int compare(Person p1, Person p2) {
        // p1大于p2 返回正数  p1小于p2 返回负数  p1==p2 返回0
        return  p1.getHeight() > p2.getHeight() ? 1 :  (p1.getHeight() < p2.getHeight() ? -1  : 0) ;
    }
}

```

```java
public class TestPerson {
    public static void main(String[] args) {
        // 创建 TreeMap集合对象  键为Person类型
        TreeMap<Person,String> map = new TreeMap<>(new PersonComparator());

        Person p1 = new Person("赵四", 188);
        Person p2 = new Person("小宝", 199);
        Person p3 = new Person("刘能", 155);
        Person p4 = new Person("大拿", 175);

        // 添加元素
        map.put(p1,"a");
        map.put(p2,"a");
        map.put(p3,"a");
        map.put(p4,"a");

        System.out.println("集合元素个数：" + map.size());

        // 调用entrySet方法 获取所有的集合元素对象
        Set<Map.Entry<Person, String>> entries = map.entrySet();

        // 遍历集合
        for (Map.Entry<Person, String> entry : entries) {
            // 打印集合中的entry对象
            // 将调用TreeMap集合中 重写的toString方法
            // 继续调用 键 和 值的 toString方法
            // 所有 Person类型的键  也需要重写toString
            System.out.println("entry = " + entry);

        }
    }
}

```

## 3. Set集合 HashMap中的键  去除重复的依据？

> 两个对象 equals比较为true  并且hashCode相同 认为是重复的对象

```java
public class TestSet {
    public static void main(String[] args) {
        // 创建集合对象
        HashSet<Student> set = new HashSet<>();

        // 创建学生对象
        Student stu1 = new Student("赵四",26);
        Student stu2 = new Student("赵四",26);
        Student stu3 = new Student("赵四",26);
        Student stu4 = new Student("赵四",26);


        // 使用equals比较是否为true 如果Student类重写 使用本类 如果没有重写 用父类
        System.out.println(stu1.equals(stu2));
        System.out.println(stu1.equals(stu3));
        System.out.println(stu1.equals(stu4));

        //打印hash值 调用hashCode方法 如果Student类重写 使用本类 如果没有重写 用父类
        System.out.println(stu1.hashCode());
        System.out.println(stu2.hashCode());
        System.out.println(stu3.hashCode());
        System.out.println(stu4.hashCode());

        // 添加元素 重写之后 只能添加一个元素
        set.add(stu1);
        set.add(stu2);
        set.add(stu3);
        set.add(stu4);


        // 打印集合长度
        System.out.println(set.size());
    }
}

```

```java
public class Student implements  Comparable<Student>{
    private String name;
    private int age;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public Student() {
    }

    public static void main(String[] args) {
        TreeMap<Student,String> map = new TreeMap<Student,String>();
        // 调用有参构造创建对象
        Student stu1 = new Student("赵四",26);
        Student stu2 = new Student("广坤",24);
        Student stu3 = new Student("大拿",22);
        Student stu4 = new Student("小宝",23);

        // 添加元素
        map.put(stu1,"a");
        map.put(stu2,"b");
        map.put(stu3,"c");
        map.put(stu4,"d");

        // 调用方法 获取所有的 元素 集合
        Set<Map.Entry<Student, String>> entries = map.entrySet();

        // 增强for循环遍历
        for (Map.Entry<Student, String> entry : entries) {
            System.out.println("entry = " + entry); // 直接打印对象
        }
    }

    @Override
    public String toString() {
        return "Student{" +
                "name='" + name + '\'' +
                ", age=" + age +
                '}';
    }

    /**
     *  重写 compareTo方法  自定义比较规则
     * @param stu the object to be compared.
     * @return
     */
    @Override
    public int compareTo(Student stu) {
//        if(this.getAge() > stu.getAge()){ // 当前对象的年龄大于传入对象的年龄
//            return 1; // 返回正数
//        }else if(this.getAge() < stu.getAge()){ // 当前对象的年龄小于传入对象的年龄
//            return -1; // 返回负数
//        }
//        return 0; // 以上条件都不成立 表示两个对象的年龄相等 则 返回0


      // return  this.getAge() > stu.getAge() ? 1 :  (this.getAge() < stu.getAge() ? -1  : 0) ;
       return stu.getAge() - this.getAge();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Student student = (Student) o;

        if (age != student.age) return false;
        return Objects.equals(name, student.name);
    }

    @Override
    public int hashCode() {
        int result = name != null ? name.hashCode() : 0;
        result = 31 * result + age;
        return result;
    }
}

```

