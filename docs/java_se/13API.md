# 常用类


- [1. 接下来内容特点](#1-接下来内容特点)
- [2. 枚举](#2-枚举)
- [3.包装类](#3包装类)
  - [3.1 构造方法](#31-构造方法)
  - [3.2 valueOf方法](#32-valueof方法)
  - [3.3 xxxValue方法](#33-xxxvalue方法)
  - [3.4 toString方法](#34-tostring方法)
  - [3.5 parseXXX方法](#35-parsexxx方法)
- [4. 自动装箱拆箱](#4-自动装箱拆箱)
- [5. 包装类面试题](#5-包装类面试题)
- [6. Math类](#6-math类)
- [7. Random类](#7-random类)
- [8. System类](#8-system类)
- [9. 面试题](#9-面试题)
- [10. Runtime类](#10-runtime类)
- [8. String类](#8-string类)
- [9. String类相关面试题](#9-string类相关面试题)
- [10. StringBuilder \& StringBuffer](#10-stringbuilder--stringbuffer)
- [11. java.util.Date](#11-javautildate)
- [12. SimpleDateFormat类](#12-simpledateformat类)
- [13. Calendar类](#13-calendar类)
- [14. JDK8新增日期API](#14-jdk8新增日期api)
  - [14.1 LocalDate](#141-localdate)
  - [14.2 LocalTime](#142-localtime)
  - [14.3LocalDateTime](#143localdatetime)
- [15. BigInteger \& BigDecimal](#15-biginteger--bigdecimal)
- [16. 内部类](#16-内部类)
- [17. 设计模式](#17-设计模式)


## 1. 接下来内容特点

* 常用类、集合、IO、线程、网络编程、反射、注解、JDK新特性
* 关联性不强 甚至是没有
* 需要理解的集合部分比较多，线程部分比较多，其他较少
* 学习侧重点：多记忆、多理解

## 2. 枚举

> 枚举类使用enum修饰  所有的枚举类都默认继承自java.lang.Enum类
>
> 所以我们自定义的枚举类 不能继承其他类 但是可以实现接口
>
> 枚举类不能new对象
>
>
> 枚举类中默认书写的内容全部为：全局静态常量 public static final修饰的值


```java
public interface Work {
    void doWork();
}

```


```java
/**
 *  比较复杂的枚举类型
 *  员工类型
 */
public enum Employee implements Work {
    CEO("sz001","执行总裁","大拿"),
    CTO("sz002","技术总监","赵四"),
    MANAGER("sz003","经理","小宝");
    private String employeeId; // 员工编号
    private String job; // 员工职位
    private String name; // 员工名称

    public String getEmployeeId() {
        return employeeId;
    }

    public void setEmployeeId(String employeeId) {
        this.employeeId = employeeId;
    }

    public String getJob() {
        return job;
    }

    public void setJob(String job) {
        this.job = job;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }


    Employee(String employeeId, String job, String name) {
        this.employeeId = employeeId;
        this.job = job;
        this.name = name;
    }

    @Override
    public String toString() {
        return "Employee{" +
                "employeeId='" + employeeId + '\'' +
                ", job='" + job + '\'' +
                ", name='" + name + '\'' +
                "} " + super.toString();
    }

    /**
     *  枚举类自带一个 values() 方法 用于将本类中的所有属性 转化为一个数组
     * @param employeeId
     * @return
     */
    public static Employee getEmployeeById(String employeeId){
        Employee[] values = Employee.values();
        for (int i = 0; i < values.length; i++) {
            if(employeeId.equals(values[i].getEmployeeId())){
                return values[i];
            }
        }
        return null;
    }


    @Override
    public void doWork() {
        System.out.println(name + "在工作");
    }
}

```

```java
public class TestEmp {
    public static void main(String[] args) {
        Employee sz001 = Employee.getEmployeeById("sz001");

        sz001.doWork();
        System.out.println("sz001 = " + sz001);

        Employee cto = Employee.CTO;

        cto.doWork();
        System.out.println("cto = " + cto);
    }
}

```





## 3.包装类

> byte short  int     long float double boolean char
>
> Byte Short  Integer Long Float Double Boolean Character
>
> 每个基本类型在java.lang包中都有一个相应的包装类
>
> 包装类的作用
>
> 提供了一系列实用的方法
>
> 集合不允许存放基本数据类型数据，存放数字时，要用包装类型

### 3.1 构造方法

> 包装类构造方法：
>
> 所有包装类都可将与之对应的基本数据类型作为参数，来构造它们的实例
>
> 除Character类外，其他包装类可将一个字符串作为参数构造它们的实例
>
>
> 使用字符串构造Number子类实例 字符串不能为null 并且必须可以解析为正确的数值才可以 否则将报
>
> NumberFormatException

```java
public class TestConstructor {
    public static void main(String[] args) {
        Byte b1 = new Byte((byte)120);
        System.out.println("b1 = " + b1);

        byte b = 110;
        Byte b2 = new Byte(b);
        System.out.println("b2 = " + b2);

        Byte b3 = new Byte("11");
        System.out.println("b3 = " + b3);

        System.out.println("------------------------------------");

        Short s1 = new Short((short)345);
        System.out.println("s1 = " + s1);

        Short s2 = new Short("234");
        System.out.println("s2 = " + s2);

        System.out.println("------------------------------------");

        Integer i1 = new Integer(1234);
        System.out.println("i1 = " + i1);

        Integer i2 = new Integer("3456");
        System.out.println("i2 = " + i2);

        System.out.println("------------------------------------");

        Long l1 = new Long(4657);
        System.out.println("l1 = " + l1);

        Long l2 = new Long("7829092");
        System.out.println("l2 = " + l2);

        System.out.println("------------------------------------");

        Boolean bl1 = new Boolean(true);
        System.out.println("bl1 = " + bl1);

        Boolean bl2 = new Boolean(false);
        System.out.println("bl2 = " + bl2);

        // 使用字符串构造Boolean实例 不区分大小写 如果内容为true 则表示为true
        // 其他的任何字符串都表示为false 包括null
        Boolean bl3 = new Boolean(null);
        System.out.println("bl3 = " + bl3);


        System.out.println("------------------------------------");

        Character ch1 = new Character('a');

        System.out.println("ch1 = " + ch1);
    }
}

```



### 3.2 valueOf方法

> 基本数据类型 --> 包装对象
>
> 每个包装类都提供有valueOf方法 用于将基本数据类型转换为包装类对象 此方法为静态方法
>
> static valueOf()

```java
public class TestValueOf {
    public static void main(String[] args) {
        Byte aByte = Byte.valueOf((byte) 11);
        System.out.println("aByte = " + aByte);

        System.out.println("---------------------------------");

        Short aShort = Short.valueOf((short) 11);
        System.out.println("aShort = " + aShort);

        System.out.println("---------------------------------");
        Integer integer = Integer.valueOf(123);
        System.out.println("integer = " + integer);
        System.out.println("---------------------------------");

        Long aLong = Long.valueOf(12344);
        System.out.println("aLong = " + aLong);

        System.out.println("---------------------------------");

        Boolean aBoolean = Boolean.valueOf(true);
        System.out.println("aBoolean = " + aBoolean);

        System.out.println("---------------------------------");

        Character character = Character.valueOf('a');
        System.out.println("character = " + character);
    }
}

```



### 3.3 xxxValue方法

> 包装对象 --> 基本数据类型
>
> 每个包装类都提供有xxxValue()方法，用于将包装类对象，转换为基本数据类型，此方法为实例方法

```java
public class TestXXXValue {
    public static void main(String[] args) {
        Byte b1 = new Byte("123");
        byte b = b1.byteValue();
        System.out.println("b = " + b);
        System.out.println("-------------------------------");

        Short s1 = new Short("123");
        short i = s1.shortValue();
        System.out.println("i = " + i);

        System.out.println("-------------------------------");

        Integer i1 = new Integer("123");
        int i2 = i1.intValue();
        System.out.println("i2 = " + i2);

        System.out.println("-------------------------------");


        Long l1 = new Long("11234");
        long l = l1.longValue();
        System.out.println("l = " + l);

        System.out.println("-------------------------------");

        Boolean bl1 = new Boolean(true);
        boolean b2 = bl1.booleanValue();
        System.out.println("b2 = " + b2);

        System.out.println("-------------------------------");

        Character ch1 = new Character('a');
        char c = ch1.charValue();
        System.out.println("c = " + c);
    }
}

```

### 3.4 toString方法

> toString():以字符串形式返回包装对象表示的基本类型数据（基本类型->字符串）

```java
public class TestToString {
    public static void main(String[] args) {
        String s1 = Byte.toString((byte) 123);
        System.out.println("s1 = " + s1);

        String s2 = Short.toString((short) 1234);
        System.out.println("s2 = " + s2);

        String s3 = Integer.toString(123);
        System.out.println("s3 = " + s3);


        String s4 = Long.toString(123);
        System.out.println("s4 = " + s4);


        String s5 = Boolean.toString(true);
        System.out.println("s5 = " + s5);

        String s6 = Float.toString(3.5F);
        System.out.println("s6 = " + s6);

        String s7 = Double.toString(2.2);
        System.out.println("s7 = " + s7);


        String s8 = Character.toString('A');
        System.out.println("s8 = " + s8);
    }
}

```



### 3.5 parseXXX方法

>  parseXXX ： 每个包装类都提供有parseXXX方法 用于将字符串转化为基本数据类型 此方法为静态方法

```java
public class TestParseXXX {
    public static void main(String[] args) {
        byte b = Byte.parseByte("123");
        System.out.println("b = " + b);

        short i = Short.parseShort("123");
        System.out.println("i = " + i);

        int i1 = Integer.parseInt("123");
        System.out.println("i1 = " + i1);

        long l = Long.parseLong("1234");
        System.out.println("l = " + l);


        float v = Float.parseFloat("3.5F");
        System.out.println("v = " + v);

        double v1 = Double.parseDouble("123");
        System.out.println("v1 = " + v1);

        // 转换规则和Boolean包装类使用字符串构造实例相同
        boolean abc = Boolean.parseBoolean("abc");
        System.out.println("abc = " + abc);
    }
}

```

## 4. 自动装箱拆箱

> 自动装箱和拆箱：从JDK1.5开始 允许包装类对象和基本数据类型混合使用计算
>
> 装箱：将基本数据类型 包装类包装类对象
>
> 拆箱：将包装类对象 自动转换为基本数据类型

```java
public class TestAutoConvert {
    public static void main(String[] args) {
        Integer i1 = 100;// valueOf(100); // 装箱  valueOf()

        int number = i1; // intValue() // 拆箱

        System.out.println("-----------------------------------");

        Byte a = new Byte("123");

        byte b = a.byteValue();

        byte c = 1;

        System.out.println(b + c);

        System.out.println("-----------------------------------");

        Short s1 = new Short("123");

        short s2 = 123;

        System.out.println(s1 + s2);
    }
}

```



## 5. 包装类面试题

> 回顾==和equals的区别？
>
> Short Integer Long Character 包装类相关面试题：
>
> 这四个包装类 直接使用等号赋值的方式创建对象 如果在byte取值范围以内 则从缓存数组中取出对应的元素
>
> 多次取出相同数值的 为 同一个元素 所以地址相同
>
> 如果不在byte取值范围以内 则直接new新的对象 所以地址不同

```java
public class TestInterview {
    public static void main(String[] args) {

        Integer a = 127;
        Integer b = 127;
        a = 100;
        System.out.println(a == b); // true

        Integer c = -129;
        Integer d = -129;

        System.out.println(c == d); // false


        Integer e = new Integer(-128);
        Integer f = new Integer(-128);
        System.out.println(e == f); // false 只要是new的  地址永远都不相同

        Short s1 = 200;
        Short s2 = 200;
        System.out.println(s1 == s2);


        Short s3 = 100;
        Short s4 = 100;
        System.out.println(s3 == s4);

        Long l1 = 100L;
        Long l2 = 100L;
        System.out.println(l1 == l2);

        Long l3 = 128L;
        Long l4 = 128L;
        System.out.println(l3 == l4);

        Character ch1 = 28;
        Character ch2 = 28;
        System.out.println(ch1 == ch2);
    }
}

```

## 6. Math类

> Math类 数学工具类 提供了常用的数学计算的方法
>
> abs() 绝对值
>
> ceil() 向上取整
>
> floor() 向下取整
>
> round() 四舍五入
>
> max() 求最大值
>
> min() 求最小值
>
> random() 获取随机数

```java
public class TestMath {
    public static void main(String[] args) {
        System.out.println(Math.E);
        System.out.println(Math.PI);

        System.out.println(Math.abs(-123));
        System.out.println(Math.ceil(3.3));
        System.out.println(Math.floor(3.6));
        System.out.println(Math.round(3.5));
        System.out.println(Math.max(23, 33));
        System.out.println(Math.min(23, 33));

        double random = Math.random();
        System.out.println("random = " + random);
        System.out.println((int)(random * 100));

        System.out.println((int)(random * 12));
    }
}

```



## 7. Random类

> Random 专门用于生成随机数据的类

```java
public class TestRandom {
    public static void main(String[] args) {
        Random random = new Random();
        System.out.println(random.nextBoolean());
        System.out.println(random.nextInt());
        System.out.println(random.nextInt(100));
        System.out.println(random.nextFloat());
        System.out.println(random.nextDouble());
    }
}

```

## 8. System类

> System类 系统类 提供了用于获取系统信息的各种方法
>
> currentTimeMillis() 获取当前系统时间 单位为毫秒 返回long类型的  从1970年1月1日0点0分0 秒到目前
>
> arraycopy(Object src, int srcPos, Object dest, int destPos, int length) 复制数组
>
> clearProperty(String key) 根据键删除指定的属性
>
> exit(int status) 退出JVM虚拟机
>
> gc() 运行垃圾回收器
>
> getProperties() 获取当前系统所有属性
>
> getProperty(String key) 根据key获取指定属性值
>
> nanoTime() 获取当前系统时间 纳秒单位

```java
public class TestSystem {
    public static void main(String[] args) {
        System.out.println(System.currentTimeMillis());
        System.out.println(System.nanoTime());

        Properties properties = System.getProperties();
        properties.list(System.out);

        System.out.println("-------------------------------------------");

        System.out.println(System.getProperty("java.version"));
        System.out.println(System.getProperty("os.name"));
        System.out.println(System.getProperty("user.name"));
        System.out.println(System.getProperty("user.dir"));
        System.out.println(System.getProperty("hello world"));

        Student stu = new Student();

        Student [] students = new Student[1];

        students[0] = stu;

        stu = null;

        System.gc(); // 运行垃圾回收器 回收可以被回收的对象

        System.out.println(stu);

        System.exit(123);

        System.out.println("程序结束");
    }
}

```

## 9. 面试题

> final finally finalize 三者区别？
>
> - final属于java关键字 用于修饰属性 方法 或者类
>
> - finally属于java关键字 用于异常处理 表示任何情况都执行的代码块
>
> - finalize() 属于Object类中的方法 性质属于析构函数 表示当前对象被回收就自动调用的方法

## 10. Runtime类

> Runtime类 此类属于运行时类 每个Java应用程序都将自动创建此类对象 所以不能人为创建
>
> 只能通过getRuntime()方法获取到此类对象
>
>
> exec(String command) 执行本地可执行文件
>
> exit(int status)  退出JVM虚拟机
>
> freeMemory() 获取JVM空闲内存 单位为字节
>
> maxMemory() 获取JVM最大内存 单位为字节
>
> totalMemory() 获取JVM总内存 单位为字节
>
> gc() 运行垃圾回收器
>
> getRuntime() 获取此类对象

```java
public class TestRuntime {
    public static void main(String[] args) throws IOException {
        Runtime runtime = Runtime.getRuntime();

        System.out.println("空闲内存：" + runtime.freeMemory() / 1024 / 1024);
        System.out.println("最大内存：" + runtime.maxMemory()  / 1024 / 1024);
        System.out.println("总内存：" + runtime.totalMemory()  / 1024 / 1024);


        runtime.exec("D:\\funny\\10秒让整个屏幕开满玫瑰花\\点我.exe");

        runtime.gc();
        runtime.exit(1);
    }
}

```



## 8. String类

> length() 获取字符串长度
>
> equals() 比较字符串内容
>
> equalsIgnoreCase() 忽略大小写比较
>
> toLowerCase() 转换为小写
>
> toUpperCase() 转换为大写
>
> concat() 拼接字符串
>
> indexOf(String str) : 查找某个字符/字符串在字符串中第一次出现的位置 未找到返回-1 找到返回对应下标
>
> indexOf(int str) : 查找某个字符/字符串在字符串中第一次出现的位置 未找到返回-1 找到返回对应下标
>
> lastIndexOf(String str) : 查找某个字符/字符串在字符串中最后一次出现的位置 未找到返回-1 找到返回对应下标
>
> lastIndexOf(int str) : 查找某个字符/字符串在字符串中最后一次出现的位置 未找到返回-1 找到返回对应标
>
> substring(int beginIndex) : 根据指定开始下标截取字符串 截取到末尾
>
> substring(int beginIndex,int endIndex) : 根据指定开始下标截取字符串 截取到指定位置 (包前不包后)
>
> split(String str) : 根据指定条件拆分字符串
>
> charAt(int index) : 根据指定下标返回对应位置的字符
>
> contains(CharSequence s) 判断字符串是否包含某一个字符串
>
> endsWith(String suffix) 判断字符串是否以某一个字符串结尾
>
> startsWith(String prefix)  判断字符串是否以某一个字符串开头
>
> isEmpty() 判断字符串长度是否为0
>
> replace(char oldChar, char newChar) 替换字符串中指定的字符
>
> toCharArray() 将此字符串转换为新的字符数组。
>
> valueOf(Object b) 将指定内容转换为字符串



## 9. String类相关面试题

> String类相关面试题：
>
> 1.String类内底层实现
>
> String类底层帮我们维护的是一个char数组 即我们创建的每一个字符串对象都以char数组的形式来保存
>
>
>
> 2.String类对象是否可以改变？
>
> 不可改变 String对象是不可改变的 任何对String对象内容的修改
>
> 都会产生一个新的字符串对象
>
>
>
> 3.为什么String类是不可变对象
>
> 原因1：底层为char数组维护的String对象 而数组的长度是固定的
>
> 原因2:此数组为final修饰 表示不能指向新的地址 同时也使用private修饰 表示不能被外界访问
>
> 原因3：String类是final修饰的 不能被其他类继承
>
>
>
> 4.有没有什么方式改变String对象的内容？
>
> 有 使用反射可以修饰字符串对象的内容


```java
public class TestString {
    public static void main(String[] args) {
        String str1 = "abc"; // 存在字符串常量池
        String str2 = "abc"; // 存在字符串常量池
        String str3 = new String("abc"); // 存在堆中

        System.out.println(str1 == str2); // true
        System.out.println(str2 == str3); // false

        System.out.println("-------------------------------------------------------");

        String str4 = "x" + "y" + "z"; // 字面量的方式拼接字符串 在编译期间会被优化 为："xyz"
        String str5 = "xyz";
        System.out.println(str4 == str5); // true

        System.out.println("-------------------------------------------------------");

        // 关于字符串拼接规律：
        // 常量+常量 是在常量池中 先看常量池中是否存在 如果不存在 则先存放 在引用地址
        // 如果存在 则直接引用地址
        // 其他三种情况 ，都在堆中创建新的对象
        String str6 = "hello ";
        String str7 = "world";

        String str8 = str6 + str7;
        String str9 = "hello world";

        String str10 = "hello " + "world";

        String str11 = str6 + "world";
        String str12 = "hello " + str7;


        System.out.println(str8 == str9); // false
        System.out.println(str9 == str10); // true
        System.out.println(str11 == str12);// false
    }
}

```

> 5.String类中intern()方法的作用：
>
> 调用intern() 会先去字符串常量池中 检查是否有当前字符串完全相同的内容
> 如果有，则直接引用以存在常量池中的地址 
> 如果没有，则先将字符串内容存进常量池 然后再引用地址

```java
public class TestStringIntern {
    public static void main(String[] args) {

        String str2 = ("a" + "b" + "c" ).intern();
        String str1 = "abc";
        System.out.println(str1 == str2);
    }
}

```



## 10. StringBuilder & StringBuffer

> append() 追加 拼接字符串
>
> delete(int start, int end)  删除指定开始下标到结束下标的内容(包前不包后)
>
> deleteCharAt(int index) 根据指定下标删除指定字符
>
> insert(int offset, Object b) 在指定位置插入内容
>
> replace(int start, int end, String str) 用指定的String中的字符替换此序列的子字符串中的 String
>
> reverse() 翻转字符串
>
> setCharAt(int index, char ch) 修改指定下标位置的字符

> 面试题：String StringBuffer StringBuilder的区别？
>
> - String是不可变字符串对象
> - StringBuffer 和 StringBuilder属于可变字符串对象
> - String是线程不安全的  JDK1.0
> - StringBuffer是线程安全的  JDK1.0
> - StringBuilder线程不安全   JDK1.5

```java
public class TestStringBufferStringBuilder {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        sb.append('a');
        sb.append("hello");
        sb.append(123);
        sb.append(3.6F);
        sb.append(true);
        sb.append(20.5);

        System.out.println("sb = " + sb);

        sb.delete(0, 3);

        System.out.println("sb = " + sb);

        sb.deleteCharAt(3);

        System.out.println("sb = " + sb);

        sb.insert(0, 666);

        System.out.println("sb = " + sb);

        sb.replace(0, 3, "999");

        System.out.println("sb = " + sb);

        sb.setCharAt(0, 'A');

        System.out.println("sb = " + sb);

        sb.reverse();

        System.out.println("sb = " + sb);
    }
}

```



## 11. java.util.Date

> java.util.Date 日期类 此类提供有用于处理日期的各种方法
>
> 很多构造和方法已弃用 但是依然可以使用 只不过不推荐使用

```java
public class TestDate {
    public static void main(String[] args) {
        Date date1 = new Date();

        System.out.println("年份" + (date1.getYear() + 1900));
        System.out.println("月份" + (date1.getMonth() + 1));
        System.out.println("一月中的天" + date1.getDate());
        System.out.println("一周中的天" + date1.getDay());
        System.out.println("时" + date1.getHours());
        System.out.println("分" + date1.getMinutes());
        System.out.println("秒" + date1.getSeconds());

        System.out.println("date1 = " + date1);

        Date date2 = new Date(2023,7,12);

        System.out.println("date2 = " + date2);

        Date date3 = new Date(System.currentTimeMillis());

        System.out.println("date3 = " + date3);

        Date date4 = new Date(5689765975697841L);

        System.out.println("date4 = " + date4);
    }
}

```

## 12. SimpleDateFormat类

> SimpleDateFormat 日期格式化类 可以将日期和字符串互相转换
>
>
> SimpleDateFormat() 无参构造 以默认格式转换 以及 解析日期
>
> SimpleDateFormat(String pattern) 以指定的格式 转换以及 解析日期
>
>
> Date parse(String source) 将字符串转换为日期独享
>
> String format(Date date) 将日期转换为字符串对象

```java
public class TestSimpleDateFormat {
    public static void main(String[] args) throws ParseException {
        Date date1 = new Date();
        System.out.println("date1 = " + date1);

        SimpleDateFormat sdf = new SimpleDateFormat();

        String format = sdf.format(date1);

        System.out.println("format = " + format);

        Date parse = sdf.parse("22-1-11 上午12:07");

        System.out.println("parse = " + parse);


        Date date2 = new Date();

        SimpleDateFormat sdf1 = new SimpleDateFormat("yyyy年MM月dd日 HH:mm:ss");

        String format1 = sdf1.format(date2);
        System.out.println("format1 = " + format1);


        Date parse1 = sdf1.parse("2021年11月12日 12:1:1");

        System.out.println("parse1 = " + parse1);
    }
}

```



## 13. Calendar类

> Calendar 日历类 提供了常用的关于时间获取的方法

```java
public class TestCalendar {
    public static void main(String[] args) {
        Calendar calendar = Calendar.getInstance();

        System.out.println("年" + calendar.get(Calendar.YEAR));
        System.out.println("月" + calendar.get(Calendar.MONTH));
        System.out.println("日" + calendar.get(Calendar.DAY_OF_MONTH));
        System.out.println("一年中的第几天：" + calendar.get(Calendar.DAY_OF_YEAR));
        System.out.println("一周中的第几天：" + calendar.get(Calendar.DAY_OF_WEEK));
        System.out.println("时：" + calendar.get(Calendar.HOUR));
        System.out.println("分：" + calendar.get(Calendar.MINUTE));
        System.out.println("秒：" + calendar.get(Calendar.SECOND));
    }
}

```



## 14. JDK8新增日期API

### 14.1 LocalDate

> LocalDate JDK8新增的 只能表示年月日的日期工具类
>
> now() 获取当前系统时间 返回值为LocalDate 对象
>
> of(int year, int month, int dayOfMonth) 根据传入的年月日构造当前类实例

```java
public class TestLocalDate {
    public static void main(String[] args) {
        LocalDate now = LocalDate.now();
        System.out.println(now.getYear());
        System.out.println(now.getMonth());
        System.out.println(now.getDayOfMonth());
        System.out.println(now.getDayOfYear());
        System.out.println(now.getDayOfWeek());

        System.out.println("now = " + now);

        LocalDate of = LocalDate.of(2022, 11, 11);

        System.out.println("of = " + of);
    }
}

```



### 14.2 LocalTime

> LocalTime JDK8新增的日期工具类 只能表示时分秒
>
> of(int hours,int minutes,int seconds) 根据传入的参数获取当前类实例
>
> now() 获取当前时间

```java
public class TestLocalTime {
    public static void main(String[] args) {
        LocalTime now = LocalTime.now();

        System.out.println(now.getHour());
        System.out.println(now.getMinute());
        System.out.println(now.getSecond());
        System.out.println(now.getNano());

        System.out.println("now = " + now);

        LocalTime of = LocalTime.of(12, 12, 12);
        System.out.println("of = " + of);
    }
}
```

### 14.3LocalDateTime

> LocalDateTime JDK8新增的用于表示年月日时分秒的日期工具类
>
> of(int year, int month, int dayOfMonth,int hours,int minutes,int seconds) 根据传入的参数获取当前类实例
>
> now() 获取当前日期对象

```java
public class TestLocalDateTime {
    public static void main(String[] args) {
        LocalDateTime now = LocalDateTime.now();
        System.out.println(now.getYear());
        System.out.println(now.getMonth());
        System.out.println(now.getDayOfMonth());
        System.out.println(now.getDayOfYear());
        System.out.println(now.getDayOfWeek());
        System.out.println(now.getHour());
        System.out.println(now.getMinute());
        System.out.println(now.getSecond());
        System.out.println(now.getNano());
        System.out.println("now = " + now);

        LocalDateTime of = LocalDateTime.of(2008, 12, 12, 10, 15, 16);
        System.out.println("of = " + of);
    }
}

```

## 15. BigInteger & BigDecimal

> BigInteger 可以表示任意长度的整数

```java
public class TestBigInteger {
    public static void main(String[] args) {
        BigInteger bigInteger1 = new BigInteger("4557876559856565746352635265265261532243543643244135445234145324145354145243312131341531");
        BigInteger bigInteger2 = new BigInteger("45574324413544541531");


        BigInteger add = bigInteger1.add(bigInteger2);
        System.out.println("add = " + add);


        BigInteger subtract = bigInteger1.subtract(bigInteger2);
        System.out.println("subtract = " + subtract);


        BigInteger multiply = bigInteger1.multiply(bigInteger2);
        System.out.println("multiply = " + multiply);


        BigInteger divide = bigInteger1.divide(bigInteger2);
        System.out.println("divide = " + divide);
    }
}

```

> BigDecimal 可以保存任意精度 任意长度的小数

```java
public class TestBigDecimal {
    public static void main(String[] args) {
        BigDecimal bigDecimal1 = new BigDecimal("56785676578978526574852632574163526352.6598963598759652203895659565");
        BigDecimal bigDecimal2 = new BigDecimal("567826352.6598963598759");

        BigDecimal add = bigDecimal1.add(bigDecimal2);
        System.out.println("add = " + add);

        BigDecimal subtract = bigDecimal1.subtract(bigDecimal2);
        System.out.println("subtract = " + subtract);

        BigDecimal multiply = bigDecimal1.multiply(bigDecimal2);
        System.out.println("multiply = " + multiply);


        BigDecimal divide = bigDecimal1.divide(bigDecimal2, 6, RoundingMode.HALF_UP);
        System.out.println("divide = " + divide);
    }
}
```



## 16. 内部类

> 内部类 ： 一个类中又书写其他的类 包含在内的类 属于内部类
>
>
> 内部类存在的原因分析：
>
> 当我们需要使用类描述某个信息 并且这个信息属于某个类 不能被其他类直接访问
>
> 那么可以将此信息以内部类来描述
>
>
> 内部类生成的class文件名格式：外部类$内部类.class
>
>
> 内部类分类：
>
> - 普通内部类(了解)
> - 静态内部类(了解) 
> - 局部内部类(了解) 
> - 匿名内部类(掌握)

> 普通内部类(了解)

```java
public class Note {
    public static void main(String[] args) {
        Student stu = new Student();
        stu.name = "赵四";
        stu.age = 20;
        stu.address = stu.new Address();

        Student.Address address = new Student().new Address();
    }
}

class Student {
    public String name;
    public int age;
    public Address address;
    class Address{
        // 邮编  省份 城市 街道 ……
    }

}

class Order {
//    private Address address;
}
// ……
```

> 静态内部类

```java
public class Outer1 {
    private String field1;
    private int field2;

    public void m1() {
        System.out.println("外部类中的m1方法");
    }

    public static void m2() {
        System.out.println("外部类中的m2方法");
    }

    public static class Inner1 {
        private String field3;
        private int field4;

        public void m1(){
            Outer1 outer1 = new Outer1();
            System.out.println(outer1.field1);
            System.out.println(outer1.field2);
            outer1.m1();
            Outer1.m2();
            System.out.println("内部类中的m1方法");

            System.out.println(field3);
            System.out.println(field4);

        }

        public static void m2() {
            System.out.println("内部类中的m2方法");
        }
    }

    public static void main(String[] args) {
        Outer1.Inner1 inner1 = new Outer1.Inner1();

        inner1.m1();

        Outer1.Inner1.m2();
    }
}

```

> 局部内部类 ： 在局部内部类中访问外部类方法中的局部变量 此变量将默认以final修饰
>
> 表示在局部内部类中 只能访问 不能修改
>
> 因为 外部类中的局部变量 将随着方法的执行完毕 出栈 而内部类对象可能不会立即被回收掉
>
> 所以在局部内部类在中 修改一个已经出栈的数据 是行不通的

```java
public class Outer2 {
    private String field1;
    private int field2;

    public void m1(){
        System.out.println(field1);
        System.out.println(field2);
        int a = 100;
        class Inner2 {
            private String field1;
            private int field2;
            public void m2(){
                System.out.println(a);
                System.out.println("局部内部类中的m2方法");
            }

        }
        Inner2 inner2 = new Inner2();
        inner2.m2();
    }


    public static void main(String[] args) {
        Outer2 outer2 = new Outer2();
        outer2.m1();
    }

}

```

> 匿名内部类 ： 必须实现一个接口 或者 继承 一个抽象类

```java
public class Outer3 {
    public static void main(String[] args) {
        A a = new A() {
            @Override
            public void m1() {
                System.out.println("匿名内部类的方式重写m1方法");
            }

            @Override
            public void m2() {
                System.out.println("匿名内部类的方式重写m2方法");
            }

            @Override
            public void m3() {
                System.out.println("匿名内部类的方式重写m3方法");
            }

            @Override
            public void m4() {
                System.out.println("匿名内部类的方式重写m4方法");
            }
        };

        a.m1();
        System.out.println(a);

        B b = new B() {
            @Override
            public void m2() {
                System.out.println("匿名内部类方式重写m2方法");
            }
        };

        b.m2();
        System.out.println("b = " + b);

        new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("匿名内部类的方式实现Runnable实现类");
            }
        }).start();



    }
}

interface A{
    void m1();
    void m2();
    void m3();
    void m4();
}

abstract class B{
    public abstract  void m2();
}


```



## 17. 设计模式

> 设计模式  来源与一个组合 GOF (四人组) 所著的一本书《设计模式》
>
> 是有我们的前辈 在长期的开发实践当中 总结出来的一套 用于解决特定问题的方案 套路
>
>
> 设计模式七大原则：
>
> 1.依赖倒置原则 是指程序应该依赖于抽象 而非依赖于具象
>
> 2.单一职责(原则) 高内聚 一个类只描述一个事物 一个方法只实现一个功能
>
> 3.接口隔离原则  接口与接口之间 相互隔离 不应该产生过多的依赖关系
>
> 4.里式替换原则  程序中的父类可以替换为子类 实现相同或者类似的功能
>
> 5.迪米特法则 不要和陌生人说话  高内聚思想 类中的信息应该与本类直接关联  不应该间接 或者 没有关联
>
> 6.开闭原则  对扩展开放 对修改源代码关闭
>
> 7.合成复用原则 接口的组合、方法的复用、 继承关系、 代码的重用 等等
>
>
>
> 创建型模式，共五种：工厂方法模式、抽象工厂模式、单例模式、建造者模式、原型模式。
>
>
> 结构型模式，共七种：适配器模式、装饰器模式、代理模式、外观模式、桥接模式、组合模式、享元模式。
>
>
> 行为型模式，共十一种：策略模式、模板方法模式、观察者模式、迭代子模式、责任链模式、命令模式、备忘录模式、状态模式、访问者模式、中介者模式、解释器模式。



> 单例模式 ： 在内存中 只允许存在一个当前类的实例 即可以使用单例
>
> 懒汉单例

```java
public class LazySingleton {
    private static LazySingleton instance = null;

    private LazySingleton(){}

    public static LazySingleton getInstance(){
        if(instance == null){
            instance = new LazySingleton();
        }
        return instance;
    }

}

```

> 饿汉单例

```java
public class HungrySingleton {

    private static HungrySingleton instance = new HungrySingleton();

    private HungrySingleton(){}


    public static HungrySingleton getInstance(){
        return instance;
    }

}

```



