# JDK8新特性

- [1. 介绍](#1-介绍)
- [2. 集合相关](#2-集合相关)
- [3. 接口相关](#3-接口相关)
- [4. 函数式接口](#4-函数式接口)
- [5. lambda表达式](#5-lambda表达式)
- [6. 方法引用](#6-方法引用)
- [7. Stream流式编程](#7-stream流式编程)
  - [7.1 创建方式](#71-创建方式)
  - [7.2 中间操作](#72-中间操作)
  - [7.3 终止操作](#73-终止操作)
- [8. Optional类](#8-optional类)

## 1. 介绍

> 在JDK8版本中 引入了很多新的内容 分为
>
> 新的语法
>
> 新的功能
>
> 新的底层实现
>
> 等等

## 2. 集合相关

> ArrayList 被设计为了懒加载的模式 初始化无参构造 只维护一个空列表 当我们第一次添加元素 才将数组初始化为10
>
> HashMap加入了红黑树数据结构

## 3. 接口相关

> 接口中可以书写普通方法 使用default关键字修饰 加在返回值类型之前 访问修饰符之后 
>
> 接口中可以书写静态方法 

```java
public interface A {
    public default void m1(){

    }

    public static void m2(){
        
    }
}
```

## 4. 函数式接口

> 函数式接口：即一个接口中只有一个抽象方法 这样的接口称之为  SAM接口 Single Abstract Method  这样的接口可以使用注解@FunctionalInterface修饰 称之为函数式接口
>
> `只要一个接口中只有一个抽象方法，即可称之为函数式接口`
>
> 函数式编程属于一种编程思想  就像面向过程 面向对象 等等 都属于编程思想
>
> 函数式编程的代表语言是Haskell  更强调函数(方法)可以实现什么操作，执行了什么功能，不注重是哪个角色调用了这个函数（方法）
>
> 使用函数式编程 即表示前提必须为函数式接口 

## 5. lambda表达式

> lambda表达式即函数式编程的最终实现   
>
>  回顾匿名内部类  ：即我们可以”直接new“接口 或者抽象类 相当于创建一个匿名内部类
>
> 使用了lambda表达式以后 之前匿名内部类书写格式混乱的问题 可以得到解决
>
> 前提：lambda表达式只能用于函数式接口
>
> 写法越简洁 前期越难理解 后期使用越方便
>
> lambda表达式格式：()-> 

```java
/**
 *  回顾匿名内部类  ：即我们可以”直接new“接口 或者抽象类 相当于创建一个匿名内部类
 *  使用了lambda表达式以后 之前匿名内部类书写个数混乱的问题 可以得到解决
 *  前提：lambda表达式只能用于函数式接口
 *
 *  写法越简洁 前期越难理解 后期使用越方便
 */
public class B {
    public static void main(String[] args) {
        C c1 = new C() {
            @Override
            public void m1() {
                System.out.println("匿名内部类的方式重写m1方法");
            }
        };

        c1.m1();

        // 无参 无返回值 只有一条语句
        C c2 = ()-> System.out.println("lambda表达式的方式重写m1方法");


        c2.m1();

        // 有一个参数 无返回值 只有一条语句
        D d1 = (a)-> System.out.println("lambda表达式方式重写D接口m1方法" + a);


        d1.m1(100);
        // 有两个个参数 无返回值 只有一条语句
        E e1 = (a,b)-> System.out.println("lambda表达式方式重写E接口m1方法" + a + b);
        e1.m1(123, "abc");

        // 有两个参数 有返回值 只有一条语句
        F f1 = (a,b)-> a + b;
        System.out.println(f1.m1(10, 20));

        // 有一个参数 有返回值 有多条语句
        F f2 = (a,b)->{
            System.out.println(a + b);
            return a + b;
        };
    }
}

interface F {
    int m1(int a,int b);
}
interface E {
    void m1(int a,String b);
}
interface D {
    void m1(int a);
}
interface C {
    void m1();
}

```

## 6. 方法引用

> 方法引用  ：在lambda表达式的基础上 使用其他的方法的方法体 来作为 lambda表达式(函数式接口中)
>
> 抽象方法的方法体
>
>
> 具体细节：被引用的方法体 原本的方法 返回值  形参列表 必须和 函数式接口中抽象方法的返回值 形参列表 完全匹配
>
> 否则 将无法引用
>
>
> 方法引用格式 ::
>
> 构造方法引用 类名 :: new;
>
> 静态方法引用 类名 :: 方法名;
>
> 实例方法引用 对象名 :: 方法名;

```java
/**
 *  方法引用  ：在lambda表达式的基础上 使用其他的方法的方法体 来作为 lambda表达式(函数式接口中)
 *  抽象方法的方法体
 *
 *  具体细节：被引用的方法体 原本的方法 返回值  形参列表 必须和 函数式接口中抽象方法的返回值 形参列表 完全匹配
 *  否则 将无法引用
 *
 *  方法引用格式 ::
 *  构造方法引用 类名 :: new;
 *  静态方法引用 类名 :: 方法名;
 *  实例方法引用 对象名 :: 方法名;
 */
public class TestMethodReference {
    public static void main(String[] args) {
        A a1 = ()-> System.out.println("");

        A a2 = Student :: new;
        a2.m1();


        B b1 = Student :: new;

        b1.m1("赵四");

        C c1 = Student :: new;
        c1.m1("a", 20);

        // 思考：哪个方法首先为静态方法
        // 并且参数为布尔类型 返回值为String类型的
        D<String,Boolean> d1 = String :: valueOf;
        System.out.println(d1.m1(true).length());

        D<Double,Double> d2 = Math :: abs;
        System.out.println(d2.m1(20.0));

        D<Integer,Float> d3 = Math :: round;

        System.out.println(d3.m1(3.5F));

        System.out.println("-----------------------------------------------------");

        String str = "abc";
        D<Boolean,String> d4 = str :: startsWith;
        System.out.println(d4.m1("def"));

        D<Boolean,String> d5 = str :: endsWith;
        System.out.println(d5.m1("c"));

        E<String> e1 = System.out :: println;
        e1.m1("hello world");
    }
}

interface E<P> {
    void m1(P p);
}
interface D<R,P> {
    R m1(P p);
}
interface C {
    void m1(String str,int num);
}
interface B {
    void m1(String str);
}
class Student {
    private String name;
    private int age;

    public Student(String name) {
        this.name = name;
        System.out.println("单个参数name属性的构造方法");
    }

    public Student(String name, int age) {
        this.name = name;
        this.age = age;
        System.out.println("两个参数 name age属性的构造方法");
    }

    public Student() {
        System.out.println("无参构造方法");
    }
}
interface A {
    void m1();
}
```



> JDK提供的函数式接口位于 java.util.function 这个包中
>
> 这些函数式接口可以大致分为四类
>
> 消费型接口：Consumer<T> accept(T t)  只接受参数没有返回值
>
> 功能型接口：Function<T,R> R apply(T t) 有参数 有返回值
>
> 供给型接口：Supplier<T>  T get() 没有参数 但是有返回值
>
> 断言型接口：Predicate<T> boolean test(T t) 有参数有返回值 但是返回值固定为布尔类型

```java
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 *  JDK提供的函数式接口位于 java.util.function 这个包中
 *  这些函数式接口可以大致分为四类
 *  消费型接口：Consumer<T> accept(T t)  只接受参数没有返回值
 *  功能型接口：Function<T,R> R apply(T t) 有参数 有返回值
 *  供给型接口：Supplier<T>  T get() 没有参数 但是有返回值
 *  断言型接口：Predicate<T> boolean test(T t) 有参数有返回值 但是返回值固定为布尔类型
 */
public class TestFunctional {
    public static void main(String[] args) {
        Consumer<Integer> consumer = System.out::println;
        consumer.accept(100);

        Function<String,Integer> function = Integer :: parseInt;
        System.out.println(function.apply("123"));

        Supplier<Double> supplier = Math ::random;
        System.out.println(supplier.get());

        Predicate<String> predicate = String :: isEmpty;

        System.out.println(predicate.test("abc"));
    }
}

```



## 7. Stream流式编程

> Java8中有两大最为重要的改变。第一个是 Lambda 表达式；另外一个则是 Stream API。
>
> Stream API ( java.util.stream) 把真正的函数式编程风格引入到Java中。这是目前为止对Java类库最好的补充，因为Stream API可以极大提高Java程序员的生产力，让程序员写出高效率、干净、简洁的代码。
>
> Stream 是 Java8 中处理集合的关键抽象概念，它可以指定你希望对集合进行的操作，可以执行非常复杂的查找、过滤和映射数据等操作。 使用Stream API 对集合数据进行操作，就类似于使用 SQL 执行的数据库查询。也可以使用 Stream API 来并行执行操作。简言之，Stream API 提供了一种高效且易于使用的处理数据的方式。
>
> Stream是数据渠道，用于操作数据源（集合、数组等）所生成的元素序列。“集合讲的是数据，负责存储数据，Stream流讲的是计算，负责处理数据！”
>
> 注意：
>
> ①Stream 自己不会存储元素。
>
> ②Stream 不会改变源对象。每次处理都会返回一个持有结果的新Stream。
>
> ③Stream 操作是延迟执行的。这意味着他们会等到需要结果的时候才执行。

> 1- 创建 Stream：通过一个数据源（如：集合、数组），获取一个流
>
> 2- 中间操作：每次处理都会返回一个持有结果的新Stream，即中间操作的方法返回值仍然是Stream类型的对象，因此中间操作可以是个操作链，可对数据源的数据进行n次处理，但是在终结操作前，并不会真正执行。
>
> 3- 终止操作：终止操作的方法返回值类型就不再是Stream了，因此一旦执行终止操作，就结束整个Stream操作了。一旦执行终止操作，就执行中间操作链，最终产生结果并结束Stream。

### 7.1 创建方式

> `创建 Stream方式一：通过集合`
>
> Java8 中的 Collection 接口被扩展，提供了两个获取流的方法：
> default Stream<E> stream() : 返回一个顺序流
>
>
>
> `创建 Stream方式二：通过数组`
>
> Java8 中的 Arrays 的静态方法 stream() 可以获取数组流：
>
> static <T> Stream<T> stream(T[] array): 返回一个流
>
>
>
> `创建 Stream方式三：通过Stream的of()`
>
> 可以调用Stream类静态方法 of(), 通过显示值创建一个流。它可以接收任意数量的参数。
>
> public static<T> Stream<T> of(T... values) : 返回一个流
>
>
>
> `创建 Stream方式四：创建无限流`**`(了解)`**
>
> 可以使用静态方法 Stream.iterate() 和 Stream.generate(), 创建无限流。
>
> public static<T> Stream<T> generate(Supplier<T> s) 

### 7.2 中间操作

| **方  法**                | **描  述**                                                   |
| ------------------------- | ------------------------------------------------------------ |
| **`filter(Predicate p)`** | 保存符合指定条件的元素                                       |
| **`distinct()`**          | 筛选，通过流所生成元素的equals() 去除重复元素                |
| **`limit(long maxSize)`** | 保留指定个数的前                                             |
| **`skip(long n)`**        | 跳过元素，返回一个扔掉了前 n 个元素的流。若流中元素不足 n 个，则返回一个空流。与 limit(n) 互补 |
| **`sorted()`**            | 产生一个新流，其中按自然顺序排序                             |
| **`map(Function f)`**     | 接收一个函数作为参数，该函数会被应用到每个元素上，并将其映射成一个新的元素。 |
| **`flatMap(Function f)`** | 接收一个函数作为参数，将流中的每个值都换成另一个流，然后把所有流连接成一个流 |

### 7.3 终止操作

| **方法**                                  | **描述**                 |
| ----------------------------------------- | ------------------------ |
| **boolean** **allMatch(Predicate p)**     | 检查是否匹配所有元素     |
| **boolean** **anyMatch**(**Predicate p**) | 检查是否至少匹配一个元素 |
| **boolean** **noneMatch(Predicate  p)**   | 检查是否没有匹配所有元素 |
| **Optional<T>** **findFirst()**           | 返回第一个元素           |
| **long** **count()**                      | 返回流中元素总数         |
| **Optional<T>** **max()**                 | 返回流中最大值           |
| **Optional<T>** **min()**                 | 返回流中最小值           |
| **void** **forEach(Consumer c)**          | 迭代                     |

## 8. Optional类

> 到目前为止，空指针异常是导致Java应用程序失败的最常见原因。以前，为了解决空指针异常，Google公司著名的Guava项目引入了Optional类，Guava通过使用检查空值的方式来防止代码污染，它鼓励程序员写更干净的代码。受到Google Guava的启发，Optional类已经成为Java 8类库的一部分。
>
>    Optional实际上是个容器：它可以保存类型T的值，或者仅仅保存null。Optional提供很多有用的方法，这样我们就不用显式进行空值检测。

| 方法                                                 | 描述                                                         |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| of(Object obj)                                       | 根据传入对象获取一个Optional对象，此对象不能为null           |
| empty()                                              | 包装一个保存有null的Optional对象                             |
| ofNullable(Object obj)                               | 根据传入对象获取一个Optional对象，此对象可以为null           |
| get()                                                | 获取Optional中保存的对象，如果为null，则报空指针异常         |
| isPresent()                                          | 表示判断Optional是否为null，为null结果为false，不为null结果为true |
| ifPresent(Consumer<? super T> consumer)              | 如果Optional对象中的对象不为null，则消费此对象，否则不消费   |
| orElse(T other)                                      | 如果当前Optional对象中保存对象为null，则使用传入对象         |
| orElseGet(Supplier<? extends T> other)               | 如果当前Optional对象中为null则获取到另外一个对象，否则不获取 |
| orElseThrow(Supplier<? extends X> exceptionSupplier) | 如果当前Optional对象中为null则抛出异常，否则不抛出           |



