

## 静态方法

### 1. 方法的概念

> 概念：实现特定功能的一段代码，可反复使用。

### 2.方法的定义

> 方法的定义：一系列代码指令的集合 用于解决特定的问题 可以反复调用
> 
> public static 返回值方法名(){}
>
> 方法名命名规范：小写驼峰 见名知义

### 3.方法的调用

> 在需要调用方法的位置直接书写方法名()即可调用。

### 4. 使用方法优化诗句(1)

> 没有参数的方法：使用方法优化诗句打印

```java
/**
 *  编写方法优化诗句分析：将四处位置实现的打印10个横线的效果 编写在方法内 然后重复调用4次即可
 *
 */
public class TestMethodNoParam {
    public static void main(String[] args) {
        System.out.println("床前明月光");
        printSign();

        System.out.println("疑是地上霜");
        printSign();

        System.out.println("举头望明月");
        printSign();

        System.out.println("低头思故乡");
        printSign();
    }

    public static void printSign(){
        for (int i=1; i <= 10; i++) {
            System.out.print("-");
        }
        System.out.println();
    }
}
```

### 5. 参数

> 多数情况下，方法与调用者之间需要数据的交互；调用者必须提供必要的数据，才能使方法完成相应的功能。
>
> 形参：形式参数 表示在方法定义的时候书写的参数 形参规定了参数的  个数、类型、顺序
>
> 表示实参必须遵循形参的规定 即必须传入对应 个数 类型 顺序的 实参
>
> 实参：实际参数  表示方法在调用的时候实际传入的参数

#### 5.1 单个参数

```java
/**
 *  使用单个参数优化打印诗句： 使用户可以灵活自主的控制横线'-'的个数
 *
 */
public class TestMethodSingleParam {
    public static void main(String[] args) {
        System.out.println("床前明月光");
        int num = 7;
        printSign(num); // num为实参


        System.out.println("疑是地上霜");
        printSign(10); // 10为实参

        System.out.println("举头望明月");
        int a = 3;
        int b = 2;
        int sum = a + b;
        printSign(sum); // sum为实参

        System.out.println("低头思故乡");
        printSign(9); // 9为实参
    }

    public static void printSign(int count){
        for(int i = 1;i <= count;i++){
            System.out.print("-");
        }
        System.out.println();
    }
}

```

#### 5.2 多个参数

```java
/**
 *  使用多个参数优化诗句：使用户可以灵活自主的控制   符号的类型   以及   符号的个数
 */
public class TestMethodManyParam {
    public static void main(String[] args) {
        System.out.println("床前明月光");
        int count = 5;
        String sign = "*";
        printSign(count,sign);


        System.out.println("疑是地上霜");
        printSign(6, "&");

        System.out.println("举头望明月");
        printSign(8, "$");

        System.out.println("低头思故乡");
        printSign(6,"@");
    }

    /**
     * 目前我们定义了两个形参 分别表示
     * @param count 符号的个数
     * @param sign  符号的类型
     * 这两个参数 称之为形参列表 依然规定了参数的个数、类型、和顺序 表示实参必须遵循这个规定
     */
    public static void printSign(int count,String sign){
        for (int i = 1; i <= count; i++) {
            System.out.print(sign);
        }
        System.out.println();
    }
}

```



### 6. return关键字

> return关键字表示结束方法 并且 返回内容
>
>
> 方法返回值的位置 可以写任何的数据类型 八种基本数据类型 或者 引用数据类型
>
> 总结：你需要当前方法执行完以后返回什么数据 那么就定义什么返回值类型即可
>
>
> 只要方法声明返回值不是void 那么必须在方法体中使用return关键字返回对应的结果
>
> 如果返回值声明是void 也可以使用return 此时return只表示结束方法 不能返回内容
>
>
> return 之后的数据 必须 和方法声明返回值的类型相匹配

> return关键字返回结果情况1：返回值类型不是void 使用return返回结果

```java
/**
 * 需求：编写方法实现计算两个int类型整数之和，然后在main方法判断最终的和是奇数还是偶数
 */
public class TestReturnedValue {
    public static void addition(int a, int b) {
        System.out.println("a与b之和是：" + (a + b));
    }

    public static int add(int a, int b) {
        System.out.println("有返回值的add方法获取最终的和：" + (a + b));
        return a + b;
    }

    public static void main(String[] args) {
        addition(12321320, 23213211);

        int result = 31;
        System.out.println(result % 2 == 0 ? "偶数" : "奇数");
        System.out.println("----------------------------------------------------");
        int sum = add(11, 21);
        System.out.println(sum  % 2 == 0 ? "偶数" : "奇数");
    }


}

```

> return关键字返回结果情况2：
>
> 在分支结构中使用return返回结果 那么必须保证每一条分支都有正确的返回值

```java
/**
 *  需求：编写方法根据用户传入的整数判断是奇数还是偶数
 */
public class TestReturnedValue1 {
    public static String isEven(int num){
        if (num % 2 == 0) {
            // 偶数
            return "偶数";
        } else {
            // 奇数
            return "奇数";
        }
    }

    public static boolean isEvenWithNumber(int number){
        if (number % 2 == 0) {
            return true;
        } else {
            return false;
        }
    }

    public static void main(String[] args) {
        String result = isEven(12);
        System.out.println("result = " + result);
        System.out.println("--------------------------------------------");
        System.out.println(isEven(666));
        System.out.println("--------------------------------------------");
        boolean flag = isEvenWithNumber(111);
        System.out.println(flag == true ? "偶数" : "奇数");
    }
}

```

> return关键字返回结果情况3：在返回值类型为void的方法中 也可以使用return 此时只表示结束方法 不能返回内容

```java
public class TestNoReturnedValue {
    public static void m1(){
        for(int i = 1;i <= 10;i++){
            if(i == 5){
                return; // 注意和break的区别
            }
            System.out.println("i = " + i);
        }

        System.out.println("m1 方法执行完毕");
    }

    public static void main(String[] args) {
        m1();
    }
}

```

### 7. 多级调用

> 方法多级调用：静态方法与静态方法之间可以互相直接调用，遇到调用方法的代码 会先将方法内的代码执行完毕 再继续向下执行

```java
public class TestMethodInvoke {
    public static void m1(){
        System.out.println("m1 method start");
        m2();
        System.out.println("m1 method end");
    }

    public static void m2() {
        System.out.println("m2 method start");
        System.out.println("m2 method end");
    }

    public static void main(String[] args) {
        m1();
    }
}

```



### 8. 方法重载

> 方法重载：同一个类中的方法 名称相同 参数列表不同(参数的个数、类型、顺序至少有一个)
>
> 即可称之为方法重载  跟返回值 以及 访问权限修饰符无关
>
> 好处：屏蔽使用差异 统一程序结构 灵活 方便
>
> 需求：编写方法实现加法计算器

```java
/**
 *  需求：编写方法实现加法计算器
 */
public class TestMethodOverload {
    public static void add(int a, int b){
        System.out.println( a + b);
    }

    public static void add(int a, String b){
        System.out.println( a + b);
    }

    public static void add(String b, int a){
        System.out.println( a + b);
    }
    public static void main(String[] args) {
        add(100, 200,30,55,66);

        add(10,20);
        add(10,"20");
        add("20",10);
    }

    public static int add(int a, int b, int c){
        return a + b + c;
    }

    public static double add(int a, int b, int c, int d){
        return a + b + c + d;
    }

    public static void add(int a, int b, int c, int d, int e){
        System.out.println(a + b + c + d + e);
    }
    // ……
}
```

### 9.递归

> 递归：可以简单的理解为自己调自己
>
>
> 递归：递进和回归
>
> 递归的两个前提：
>
> >1.有一个大的问题 可以拆分为若干个小的问题(递进)
> >
> >2.必须有正确的出口(回归)
>
> 举例： 赵四   广坤    大拿    小宝   刘能
>
> 他应用场景：
>
> - 1.汉诺塔问题
> - 2.文件遍历
> - 3.八皇后问题
> - 4.快速排序

```java
/**
 *  案例1：使用递归实现1~5之间的和
 *  案例2：使用递归计算阶乘
 */
public class TestRecursion {
    public static int getNum5(int num){
        return num + getNum4(num - 1);
    }
    public static int getNum4(int num){
        return num + getNum3(num -1);
    }
    public static int getNum3(int num){
        return num + getNum2(num -1);
    }
    public static int getNum2(int num){
        return num + getNum1(num -1);
    }
    public static int getNum1(int num){
        return num;
    }

    public static int getNum(int num){
        if(num == 1){
            return 1;
        }
        return num + getNum(num - 1);
    }

    public static int getFactorial(int num){
        if(num == 1){
            return 1;
        }
        return num * getFactorial(num - 1);
    }

    public static void main(String[] args) {
        System.out.println(getNum5(5));

        System.out.println(getNum(11));

        System.out.println(getFactorial(5));
    }
}

```



