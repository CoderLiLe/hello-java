# 异常

- [1. try-catch](#1-try-catch)
  - [1.1 情况1](#11-情况1)
  - [1.2 情况2](#12-情况2)
- [2. finally](#2-finally)
- [3. finally面试题](#3-finally面试题)
- [4. throw和throws](#4-throw和throws)
- [5. 自定义异常](#5-自定义异常)

## 1. try-catch

### 1.1 情况1

> 情况1 ：使用单个catch捕获异常 如果出现的异常和捕获的异常类型匹配 则可以正常捕获
>
> 使得程序可以顺利执行完毕 如果出现的异常和捕获的异常类型不匹配 则程序将依然中断
>
> try-catch
>
> try代码块中存放可能会出现异常的代码
>
> catch用于捕获异常
>
>
> try 或者 catch 均不能单独使用
>
> try 必须结合 catch  或者 catch -finally  或者  finally

```java
/**
 *  情况1 ：使用单个catch捕获异常 如果出现的异常和捕获的异常类型匹配 则可以正常捕获
 *  使得程序可以顺利执行完毕 如果出现的异常和捕获的异常类型不匹配 则程序将依然中断
 */
public class TestTryCatch1 {
    public static void main(String[] args) {
        try {
            Scanner in = new Scanner(System.in);
            System.out.print("请输入被除数:");
            int num1 = in.nextInt();
            System.out.print("请输入除数:");
            int num2 = in.nextInt();
            System.out.println(num1+"/"+ num2 +"="+ num1/ num2);
        } catch(InputMismatchException e){
            e.printStackTrace(); // 打印异常堆栈信息
        }

        System.out.println("感谢使用本程序！");
    }
}
```


### 1.2 情况2

> try-catch情况2：使用多个catch 块来捕获异常 按照书写顺序 从前往后匹配 只匹配第一个相符的异常
>
> 然后就退出try-catch结构
>
>
> 多个catch块书写顺序 先写子类 后写 父类

```java
/**
 *  try-catch情况2：使用多个catch 块来捕获异常 按照书写顺序 从前往后匹配 只匹配第一个相符的异常
 *  然后就退出try-catch结构
 *
 *  多个catch块书写顺序 先写子类 后写 父类
 */
public class TestTryCatch2 {
    public static void main(String[] args) {
        try {
            Scanner in = new Scanner(System.in);
            System.out.print("请输入被除数:");
            int num1 = in.nextInt();
            System.out.print("请输入除数:");
            int num2 = in.nextInt();
            System.out.println(num1+"/"+ num2 +"="+ num1/ num2);
        } catch(InputMismatchException e){
            System.err.println("出现了输入不匹配异常"); //  e.printStackTrace();
        } catch(ArithmeticException e) {
            System.err.println(e.getMessage());
            e.printStackTrace();//System.err.println("出现了算数运算异常");//
        } catch(Exception e) {
            e.printStackTrace();
        }

        System.out.println("感谢使用本程序！");
    }
}

```

## 2. finally

>  finally 表示不管是否出现异常 以及 异常是否被捕获 都将执行的代码块
>
> finally不能单独出现 必须结合 try-catch  或者 try
>
> 因为finally最终都将执行 所以通常用于执行一些关闭资源的操作 比如 关闭流 关闭数据库连接对象等等
>
>
> finally不执行的唯一情况：在执行finally之前退出JVM虚拟机
>
>
> System.exit(int status) : int类型的状态码含义：0表示正常退出 非0表示非正常退出

```java
public class TestFinally {
    public static void main(String[] args) {
        try {
            Scanner in = new Scanner(System.in);
            System.out.print("请输入被除数:");
            int num1 = in.nextInt();
            System.out.print("请输入除数:");
            int num2 = in.nextInt();
            System.out.println(num1+"/"+ num2 +"="+ num1/ num2);

            System.exit(231321);
        } catch(InputMismatchException e) {
            e.printStackTrace(); // 打印异常堆栈信息
        } finally {
            System.out.println("感谢使用本程序！");
        }
    }
}

```

## 3. finally面试题

> try中存在return 是否还执行finally ？
>
> ​	执行
>
> try-catch-finally中 如果try中已经return了值 那么finally中对返回值的操作会不会改变返回值？
>
> ​	如果为基本数据类型 不会改变
>
> ​	如果为引用数据类型 会改变

```java
public class TestFinallyInterview {
    public static int m1() {
        int num = 10;
        try {
            num++;
            return num;
        } catch(Exception e) {
            e.printStackTrace();
        } finally {
            num++;
        }
        return num;
    }

    public static int[] m2() {
        int [] nums = {1, 2, 3, 4, 5};
        try {
            return nums;
        } catch(Exception e) {
            e.printStackTrace();
        } finally {
            for (int i = 0; i < nums.length; i++) {
                nums[i]++;
            }
        }
        return nums;
    }

    public static void main(String[] args) {
        int a = m1();
        System.out.println(a);

        int[] nums = m2();
        System.out.println(Arrays.toString(nums));
    }
}

```

## 4. throw和throws

> throws: 用于在方法声明的位置 参数列表之后 声明当前方法可能会出现哪些异常  可以声明多个异常
>
> 多个异常使用逗号分割
>
> 方法调用者根据声明的异常类型不同会做出不同的处理
>
> 运行时异常(RuntimeException及其子类)：调用者不必处理
>
> 检查异常(除了运行时异常以外的其他异常就属于检查异常CheckedException)：调用者必须处理
>
> 两种处理方式：
>
> ​	1.使用try-catch处理
>
> ​	2.继续在main方法上声明 属于声明给JVM虚拟机 (其实属于不处理)
>
>
> throw:用于在方法体内抛出异常 一句只能抛出一个异常
>
> ​	根据抛出的异常类型不同 需要做出不同的处理
>
> ​	如果抛出的为运行时异常 则方法上不必声明
>
> ​	如果抛出的为检查异常 则必须在方法上声明

```java
public class TestThrowAndThrows {
    public static void m1() throws InputMismatchException, ArithmeticException {
    }

    public static void m2() throws ClassNotFoundException {
    }

    public static void m3(int age) {
        if(age < 0 || age > 130) {
            throw new RuntimeException("年龄不合法");
        }
    }
    public static void m4(int age) throws Exception {
        if(age < 0 || age > 130){
            throw new Exception("年龄不合法");
        }
    }
    public static void main(String[] args) {
        m1();
        try {
            m2();
        } catch (ClassNotFoundException e) {
            throw new RuntimeException(e);
        }


        m3(158);

        try {
            m4(188);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}

```

## 5. 自定义异常

> 当JDK提供的异常不能满足开发需求时，我们可以自定义异常
>
> 自定义异常步骤：
>
> 1.继承异常父类 Throwable 、Exception 、RuntimeException 三者其中之一
>
> 2.调用父类中的有参构造完成异常信息的初始化

```java
public class Student {
    private String name;
    private int age;

    private char sex;

    public char getSex() {
        return sex;
    }

    public void setSex(char sex) throws InputSexException {
        if(sex == '男' || sex == '女'){
            this.sex = sex;
        }else{
            throw new InputSexException("性别不合法" + sex);
        }
    }
    public void setAge(int age) {
        if (age > 0 && age < 130) {
            this.age = age;
        } else {
            throw new InputAgeOutOfBoundsException("年龄不合法" + age);
        }
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

    public static void main(String[] args) {
        Student stu1 = new Student();
        stu1.setName("赵四");
        stu1.setAge(111);
        try {
            stu1.setSex('人');
        } catch (InputSexException e) {
            e.printStackTrace();
        }
        System.out.println("程序结束");
    }
}
```



```java
/**
 *  当JDK提供的异常不能满足开发需求时，我们可以自定义异常
 *  自定义异常步骤：
 *      1.继承异常父类 Throwable 、Exception 、RuntimeException 三者其中之一
 *      2.调用父类中的有参构造完成异常信息的初始化
 */
public class InputAgeOutOfBoundsException extends RuntimeException {

    public InputAgeOutOfBoundsException(String message) {
        super(message);
    }
}

```

```java
public class InputSexException extends Exception{
    public InputSexException(String message) {
        super(message);
    }
}
```



