# static关键字和方法重写

- [1 static关键字](#1-static关键字)
  - [1.1 修饰属性](#11-修饰属性)
  - [1.2 修饰方法](#12-修饰方法)
  - [1.3 修饰代码块](#13-修饰代码块)
- [2. static修饰属性练习题](#2-static修饰属性练习题)
- [3. 方法重写](#3-方法重写)
- [4. Object类](#4-object类)
  - [4.1 重写toString方法](#41-重写tostring方法)
  - [4.2 重写equals方法](#42-重写equals方法)
  - [4.3 重写hashCode方法](#43-重写hashcode方法)
- [5. 类类型的属性](#5-类类型的属性)


## 1 static关键字

![](img/对象创建过程.png)

> 对象创建的过程：
>
> 1.将当前对象所属类对应的class文件加载到方法区
>
> - 在加载类信息文件(class文件)之前 会先判断 此类是否已经被加载过
> - 如果加载过 则直接执行第2步
> - 如果没有加载过 则先加载
> - 类只加载一次
> - 加载类的同时会在方法区的静态区初始化静态相关的信息 此时 静态相关的信息将有初始值
>
> 2.在堆中开辟空间创建对象  此时实例级别的属性将有默认值
>
> 3.将堆中的地址赋值给栈中的引用 完成对象的创建

### 1.1 修饰属性

> static修饰属性，称之为静态属性，也叫静态变量，也叫类变量
>
> 被static修饰的属性 不属于任何对象 属于当前类 可以被此类的所有对象共享 在内存中只存在一份
>
> 静态属性：本类中直接访问  其他类通过类名加点访问
>
> 静态属性推荐使用类名加点访问 因为静态属性不属于任何对象 不推荐使用对象名加点的方式访问

```java
/**
 *  人类：实现模拟饮水机接水的效果
 *
 *  创建对象也叫实例(真真实实存在的一个个例)化  对象级别 也称之为实例级别
 *
 *  对象创建的过程：
 *  1.将当前对象所属类对应的class文件加载到方法区
 *      在加载类信息文件(class文件)之前 会先判断 此类是否已经被加载过
 *      如果加载过 则直接执行第2步
 *      如果没有加载过 则先加载
 *      类只加载一次
 *  加载类的同时会在方法区的静态区初始化静态相关的信息 此时 静态相关的信息将有初始值
 *  2.在堆中开辟空间创建对象  此时实例级别的属性将有默认值
 *  3.将堆中的地址赋值给栈中的引用 完成对象的创建
 */
public class Person {
    String name;
    static int capacity = 100; // 单位L

    public void getWater(){
        if(capacity > 0){
            capacity -= 2;
            System.out.println(name + "接水2L，还剩余" + capacity + "L");
        }else{
            System.out.println("没水了");
        }
    }

    public static void main(String[] args) {
        Person p1 = new Person();
        p1.name = "赵四";
        p1.getWater();

        p1 = null;

        Person p2 = new Person();
        p2.name = "大拿";
        p2.getWater();
        p2.getWater();

        Person p3 = new Person();
        p3.name = "小宝";
        p3.getWater();
    }
}

```

```java
public class Student {
    String name;
    int age;
    static String country = "中华人民共和国";

    public static void main(String[] args) {
        Student stu1 = new Student();
        stu1.name = "赵四";
        stu1.age = 20;
        stu1.country = "中国";
        System.out.println(stu1.country);

        Student stu2 = new Student();
        stu2.name = "大拿";
        stu2.age = 21;
        System.out.println(stu2.country);

        Student stu3 = new Student();
        stu3.name = "小宝";
        stu3.age = 22;
        System.out.println(stu3.country);
    }
}

```

### 1.2 修饰方法

> 静态方法：本类中直接调用 其他类通过类名加点调用
>
>
> 静态方法 不同于静态属性 因为方法只有调用的过程 调用就会进栈
>
> 虽然静态方法访问更加简单 但并不取代实例方法 因为实例方法属于对象级别的  我们面向对象的操作 通常是需要根据不同的对象 做出不同的功能实现 所以 不能仅仅因为静态方法调用简单 就使用静态方法  
>
>
> 静态属性方法，实例属性方法互相访问规则：
>
> - 相同级别互相直接访问 ：静态访问静态：直接访问、实例访问实例：直接访问
> - 静态访问实例：必须先new对象 通过对象名加点访问(回顾main方法)
> - 实例访问静态：直接访问

```java
public class TestStaticMethod {

    String field1;

    static String field2;

    public void m2(){
        System.out.println(field1);
        System.out.println(field2);
    }

    public static void m3(){}
    public static void m1(){
        System.out.println(field2);
        m3();
        TestStaticMethod method = new TestStaticMethod();
        System.out.println(method.field1);
        method.m2();
        System.out.println("静态方法m1");
    }

    public static void main(String[] args) {
        m1();
    }

}
class Test{
    public static void main(String[] args) {
        TestStaticMethod.m1();
    }
}

```

### 1.3 修饰代码块

> static修饰代码块：随着JVM加载类而执行 多个静态代码块按照书写顺序执行 每个只执行一次 因为类只加载一次
>
>
> 什么时候会加载类？
>
> - 1.new对象
> - 2.访问类中的静态属性 或者 静态方法
>
>
> 静态代码块适用场景：当我们需要执行一些前置的操作 并且这个操作只需要执行一次
>
> 比如 初始化数据 连接数据库 等等
>
> 普通/实例代码块是随着对象的创建而执行的 每创建一个对象 就执行一次

```java
public class TestStaticCode {
    static{
        System.out.println("静态代码块1");
    }

    static{
        System.out.println("静态代码块2");
    }

    {
        System.out.println("普通代码块/实例代码块1");
    }

    {
        System.out.println("普通代码块/实例代码块2");
    }

    public TestStaticCode() {
        System.out.println("TestStaticCode构造方法执行了");
    }

    static int num = 100;

    public static void  m1(){
        System.out.println("static修饰的m1方法");
    }

    public static void main(String[] args) {
        TestStaticCode testStaticCode1 = new TestStaticCode();
        TestStaticCode testStaticCode2 = new TestStaticCode();
        TestStaticCode testStaticCode3 = new TestStaticCode();

        System.out.println(num);

            m1();
    }

}

```

## 2. static修饰属性练习题

```java
/**
 *  模拟实现选民投票过程：一群选民进行投票，每个选民只允许投一次票，
 *  并且当投票总数达到100时，就停止投票
 */
public class Voter {
    String voterName;
    static int ticketCount = 100; // 因为是多个选民共享一个投票总数 所以定义为static修饰
    public Voter(String voterName) {
        this.voterName = voterName;
    }
    public boolean voteFor(){
        if(ticketCount > 0){
            ticketCount --;
            System.out.println(voterName + "投出了第" + (100 - ticketCount) + "张票，还剩余" + (ticketCount) + "张票");
            return true;
        }else{
            System.out.println("投票结束");
            return false;
        }
    }
    public static void main(String[] args) {
        Voter zs = new Voter("赵四");
        zs.voteFor();

        Voter gk = new Voter("广坤");
        gk.voteFor();

        for(int i = 1;i <= 120;i++){
            Voter v1 = new Voter(i + "号选民");
            System.out.println(v1);
//            boolean  result = v1.voteFor();
//            if(result == false){
//                break;
//            }

            if(!v1.voteFor()){
                break;
            }

        }

    }


}

```

## 3. 方法重写

> 方法重写属于对父类方法的覆盖，所以如果需要继续使用父类方法的功能，则必须在子类中使用super关键字调用
>
> 1.存在于父子类之间
>
> 2.方法名称相同
>
> 3.参数列表相同
>
> 4.返回值相同     或者是其子类
>
> 5.访问权限不能严于父类 (不能窄化父类的访问权限)
>
> 6.静态方法可以被继承，但是不能被重写
>
> 7.不能抛出、声明比父类更多的异常

> @Override 注解 此注解只能加在方法上 表示此方法属于重写父类的方法 如果没有正确重写 则编译报错
>
> 添加此注解可以提高代码的阅读性

```java
/**
 *  宠物父类：
 *  父类中书写各个子类共有的属性 和 方法
 *  子类中书写独有的属性 和 方法
 */
public class Pet {
    protected String name;
    protected int health;
    protected int love;

    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public int getHealth() {
        return health;
    }
    public void setHealth(int health) {
        this.health = health;
    }
    public int getLove() {
        return love;
    }
    public void setLove(int love) {
        this.love = love;
    }

    public Pet(){}

    public void print(){
        System.out.println("宠物的名字是：" + name);
        System.out.println("宠物的健康值是：" + health);
        System.out.println("宠物的亲密值是：" + love);
    }

}

```

```java
/**
 *  狗狗类：
 *      名字 健康值 亲密值 品种
 *      打印狗狗信息
 *      无参构造
 */
public class Dog extends Pet {
    private String strain;
    public String getStrain() {
        return strain;
    }
    public void setStrain(String strain) {
        this.strain = strain;
    }


    /**
     *  1.存在于父子类之间
     *  2.方法名称相同
     *  3.参数列表相同
     *  4.返回值相同     或者是其子类
     *  5.访问权限不能严于父类 (不能窄化父类的访问权限)
     *  6.静态方法可以被继承，但是不能被重写
     *
     *  7.不能抛出、声明比父类更多的异常
     * @Override 注解
     */
    @Override
    public void print(){
        super.print();
        System.out.println("狗狗的品种是：" + strain);
    }
}

```

```java
/**
 *  企鹅类：
 *      姓名 健康值 亲密值 性别
 *      打印企鹅信息
 *      无参构造
 */
public class Penguin extends Pet {
    private char sex;
    public char getSex() {
        return sex;
    }
    public void setSex(char sex) {
        this.sex = sex;
    }

    public void print(){
        super.print();
        System.out.println("企鹅的性别是：" + sex);
    }
}

```

## 4. Object类

### 4.1 重写toString方法

> 直接打印一个对象 相当于调用此对象的toString方法 toString方法从顶层父类Object类中继承而来
>
> 我们在实际开发中通常需要重写toString方法 用于将本类中的属性名 和 属性值 进行拼接 以方便直接打印对象
>
> 实现输出 属性信息的效果

```java
/**
 *  名字 年龄
 *  直接打印一个对象 相当于调用此对象的toString方法 toString方法从顶层父类Object类中继承而来
 *  我们在实际开发中通常需要重写toString方法 用于将本类中的属性名 和 属性值 进行拼接 以方便直接打印对象
 *  实现输出 属性信息的效果
 */
public class Student {
    String name;
    int age;
    char sex;
    double height;
    String hobby;

    @Override
    public String toString() {
        String s = super.toString();
        return s + "Student{" +
                "name='" + name + '\'' +
                ", age=" + age +
                ", sex=" + sex +
                ", height=" + height +
                ", hobby='" + hobby + '\'' +
                '}';
    }
    //    public String toString(){
//        return "Student[name = '"+ name +"',age = " + age +",sex = '"+sex +"',height = " + height + ",hobby = '"+hobby+"' ]";
//    }
//
//    public String printStudent(){
//        return "Student[name = '"+ name +"',age = " + age +",sex = '"+sex +"',height = " + height + ",hobby = '"+hobby+"' ]";
//    }

    public static void main(String[] args) {
        Student stu1 = new Student();
        stu1.name = "赵四";
        stu1.age = 20;
        stu1.height = 175;
        stu1.hobby = "尬舞";
        stu1.sex = '男';

        System.out.println(stu1);
        System.out.println(stu1.toString());

        System.out.println(stu1.name);
        System.out.println(stu1.age);
        System.out.println(stu1.height);
        System.out.println(stu1.hobby);
        System.out.println(stu1.sex);
    }
}

```

### 4.2 重写equals方法

> 面试题：==和equals的区别？
>
> ==比较基本数据类型 比较值
>
> ==比较引用数据类型 比较地址
>
> equals()方法底层实现依然使用==比较地址
>
> 但是我们可以重写equals方法 自定义比较规则   String类就是对equals方法进行了重写
>
> 将原本的比较地址 重写为了比较地址 并且比较 内容

> `只要是new出来的两个对象 地址是绝对不相同的  ==比较就为false`

>  模拟String类书写equals方法

```java
/**
 *  模拟String类书写equals方法
 */
public class MyString {
    public static void main(String[] args) {
        System.out.println(myEquals("abc", "abcd"));
    }

    public static boolean myEquals(String str1,String str2){
        if(str1 == str2){
            return true;
        }
        // String类的length()方法  表示获取字符串的长度
        // 数组的length 为属性 注意区分
        if (str1.length() != str2.length()) {
            return false;
        }
        // 将两个字符串转换为char数组
        char[] v1 = str1.toCharArray();
        char[] v2 = str2.toCharArray();

        for(int i = 0;i < v1.length;i++){
            if(v1[i] != v2[i]){
                return false;
            }
        }
        return true;
    }
}

```

> 人类
>
> 场景：如果现在有这样的"两个人" 这"两个人"名字和身份证号都相同 实际为同一个人
>
> 那么在程序中就表现为两个对象 所以我们应该重写equals方法 将两个对象的比较结果为true

```java
/**
 *  equals()方法：比较两个对象是否为同一个对象(比较地址)
 *  面试题：==和equals的区别？
 *      ==比较基本数据类型 比较值
 *      ==比较引用数据类型 比较地址
 *      equals()方法底层实现依然使用==比较地址
 *
 *  但是我们可以重写equals方法 自定义比较规则   String类就是对equals方法进行了重写
 *  将原本的比较地址 重写为了比较地址 并且比较 内容
 *
 *  记住：只要是new出来的两个对象 地址是绝对不相同的  ==比较就为false
 *
 *
 *  人类
 *  场景：如果现在有这样的"两个人" 这"两个人"名字和身份证号都相同 实际为同一个人
 *  那么在程序中就表现为两个对象 所以我们应该重写equals方法 将两个对象的比较结果为true
 *
 */
public class Person {
    private String name;
    private String idCard;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getIdCard() {
        return idCard;
    }

    public void setIdCard(String idCard) {
        this.idCard = idCard;
    }

    public Person(String name, String idCard) {
        this.name = name;
        this.idCard = idCard;
    }

    public Person() {
    }

    public boolean equals(Object obj){
        if(this == obj){
            return true;
        }
        // 因为形参为Object类型的 而Object类中没有任何属性 所以不能直接访问 name  以及 idCard
        // 如需访问 必须 向下转型(强制类型转换)
        Person p1 = (Person)obj;
        // 如何确定调用的方法属于哪个类的方法？
        // 根据调用方法的对象 所属的类型来判断
        if(this.name.equals(p1.name) && this.idCard.equals(p1.idCard)){
            return true;
        }
        return false;
    }

    public static void main(String[] args) {
        Person p1 = new Person("赵四", "4578925985324539875421");
        Person p2 = new Person("赵四", "4578925985324539875421");

        System.out.println(p1 == p2); // false
        System.out.println(p1.equals(p2)); // false
    }
}

```

### 4.3 重写hashCode方法

> 什么是hashCode(哈希值) ？
>
> - hash值是根据杂凑算法所计算出来的一个数值
> - hash值并不是地址值 而是根据对象的地址等一些信息 使用杂凑算法所计算出来的一个十进制的数值
> - Java中的地址值我们是无法获取的 计算hash值的方式也无法获取
>
> 为什么要重写hashCode()方法？
>
> - >1.因为默认情况下 两个对象equals比较为true 则hashCode必须是相同的
>   >
>   >现在 我们重写了equals 改变了对象的比较规则 所以应当继续重写hashCode 以
>   >
>   >维持 **两个对象equals比较为true 则hashCode必须是相同的** 这个规则
>
> - 2.在后续学习的集合类中 默认是以equals比较为true 并且hashCode相同作为去除重复元素的依据

```java
public class Person {
    private String name;
    private String idCard;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getIdCard() {
        return idCard;
    }

    public void setIdCard(String idCard) {
        this.idCard = idCard;
    }

    public Person(String name, String idCard) {
        this.name = name;
        this.idCard = idCard;
    }

    public Person() {
    }

    public boolean equals(Object obj){
        if(this == obj){
            return true;
        }
        // 因为形参为Object类型的 而Object类中没有任何属性 所以不能直接访问 name  以及 idCard
        // 如需访问 必须 向下转型(强制类型转换)
        Person p1 = (Person)obj;
        // 如何确定调用的方法属于哪个类的方法？
        // 根据调用方法的对象 所属的类型来判断
        if(this.name.equals(p1.name) && this.idCard.equals(p1.idCard)){
            return true;
        }
        return false;
    }

    /**
     *  分析： 因为我们要保证在equals比较为true的情况下 两个对象hashCode相同
     *  又因为equals方法是根据人的名字和身份证号比较的
     *  所以我们也要根据人的名字和身份证号来计算hash值
     * @return
     */
    public  int hashCode(){
        int result = 1; // 作为最终返回的结果
        int prime = 334421; // 权重
        result = result * prime + (this.name == null ? 0 : this.name.hashCode());
        result = result * prime + (this.idCard == null ? 0 : this.idCard.hashCode());
        return result;
    }


    public static void main(String[] args) {
        Person p1 = new Person("赵四", "457892598532453");
        Person p2 = new Person("赵四", "457892598532453");


        System.out.println(p1 == p2); // false
        System.out.println(p1.equals(p2)); // false


        System.out.println(p1.hashCode());
        System.out.println(p2.hashCode());
    }
}

```

> 为什么计算hashCode要使用31作为权重
>
> 1.因为JDK也使用31
>
> 2.因为31是一个特殊的质数 任何数乘以31 等于这个数左移5位 减去这个数 本身
>
> n * 31 = (n << 5) - n
>
> 位运算符效率是最高 但是优先级是最低的
>
> 总结：因为使用31计算hash值效率更高

```java
public class TestPrime {
    public static void main(String[] args) {
        int a = 11;
        System.out.println(a * 31);
        System.out.println((a << 5) - a);
    }
}

```

## 5. 类类型的属性

![](img/自定义类型属性.png)

> 关于对象关系：ORM框架  Object Relation Mapping (对象关系映射)  MyBatis 、 MyBatis-Plus   
>
> 一对一 ：一个学生对应一个地址
>
> 一对多：一个学生对应多个爱好
>
> 多对一：多个爱好对应一个学生
>
> 多对多：多个学生对应多个爱好/多个地址

```java
/**
 *  万物皆对象
 *  自定义类型的属性  和 自定义类型的数组属性
 */
public class Student {
    private String name;
    private int age;
    private Address address;  // 中国深圳  深圳市宝安区  草围三巷十号
    private Hobby[] hobbies;

    public void setHobbies(Hobby [] hobbies){
        this.hobbies = hobbies;
    }
    public Hobby[] getHobbies(){
        return hobbies;
    }


    public void setAddress(Address address){
        this.address = address;
    }
    public Address getAddress(){
        return address;
    }


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

    @Override
    public String toString() {
        return "Student{" +
                "name='" + name + '\'' +
                ", age=" + age +
                ", address=" + address +
                ", hobbies=" + Arrays.toString(hobbies) +
                '}';
    }
}

```

```java
/**
 *  爱好类 爱好类型 爱好名称 爱好场地 ……
 */
public class Hobby {
    private String hobbyType;
    private String hobbyName;

    public String getHobbyType() {
        return hobbyType;
    }

    public void setHobbyType(String hobbyType) {
        this.hobbyType = hobbyType;
    }

    public String getHobbyName() {
        return hobbyName;
    }

    public void setHobbyName(String hobbyName) {
        this.hobbyName = hobbyName;
    }

    @Override
    public String toString() {
        return "Hobby{" +
                "hobbyType='" + hobbyType + '\'' +
                ", hobbyName='" + hobbyName + '\'' +
                '}';
    }
}

```

```java
/**
 *  地址类
 *      省份
 *      城市
 *      区域
 *      街道
 *      邮编
 */
public class Address {
    private String province;
    private String city;
    private String area;
    private String street;
    private String zipCode;

    public String getProvince() {
        return province;
    }

    public void setProvince(String province) {
        this.province = province;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getArea() {
        return area;
    }

    public void setArea(String area) {
        this.area = area;
    }

    public String getStreet() {
        return street;
    }

    public void setStreet(String street) {
        this.street = street;
    }

    public String getZipCode() {
        return zipCode;
    }

    public void setZipCode(String zipCode) {
        this.zipCode = zipCode;
    }

    @Override
    public String toString() {
        return "Address{" +
                "province='" + province + '\'' +
                ", city='" + city + '\'' +
                ", area='" + area + '\'' +
                ", street='" + street + '\'' +
                ", zipCode='" + zipCode + '\'' +
                '}';
    }
}

```

```java
public class TestStudent {
    public static void main(String[] args) {
        Student stu1 = new Student();
        stu1.setName("赵四");
        stu1.setAge(20);

        Address address = new Address();
        address.setProvince("广东省");
        address.setCity("深圳市");
        address.setArea("宝安区");
        address.setStreet("航城街道");
        address.setZipCode("895645");

        stu1.setAddress(address);
        System.out.println("------------------------------------------------------------");
        // 关于空指针异常
        // 只要使用指向为null的引用 调用任何的属性或者方法 就会产生空指针异常
        Hobby [] hobbies = new Hobby[3];

        hobbies[0] = new Hobby();
        hobbies[0].setHobbyType("电子竞技");
        hobbies[0].setHobbyName("LOL");

        hobbies[1] = new Hobby();
        hobbies[1].setHobbyType("文艺类");
        hobbies[1].setHobbyName("尬舞");

        hobbies[2] = new Hobby();
        hobbies[2].setHobbyType("体育类");
        hobbies[2].setHobbyName("唱跳RAP 篮球");

        for (int i = 0; i < hobbies.length; i++) {
            System.out.println(hobbies[i]);
        }

        stu1.setHobbies(hobbies);

        System.out.println("------------------------------------------------------------");

        System.out.println(stu1.getName());
        System.out.println(stu1.getAge());
        System.out.println(stu1.getAddress());
        System.out.println(stu1.getAddress().getProvince());
        System.out.println(stu1.getAddress().getCity());
        System.out.println(stu1.getAddress().getArea());
        System.out.println(stu1.getAddress().getStreet());
        System.out.println(stu1.getAddress().getZipCode());

        System.out.println("------------------------------------------------------------");

        Hobby[] hobbies1 = stu1.getHobbies();

        for (int i = 0; i < hobbies1.length; i++) {
            System.out.println(hobbies1[i]);
            System.out.println(hobbies1[i].getHobbyType());
            System.out.println(hobbies1[i].getHobbyName());
        }

        System.out.println("------------------------------------------------------------");

        System.out.println(stu1);
    }
}

```