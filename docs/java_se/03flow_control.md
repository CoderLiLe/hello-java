- [流程控制](#流程控制)
  - [1. 基本if结构](#1-基本if结构)
  - [2.if-else结构](#2if-else结构)
  - [3. 多重if结构](#3-多重if结构)
  - [4. 嵌套if](#4-嵌套if)
  - [5. switch](#5-switch)
  - [6. 多重if和switch对比](#6-多重if和switch对比)
  - [7. while循环](#7-while循环)
  - [8.do-while循环](#8do-while循环)
  - [9. while循环和do-while循环的区别？](#9-while循环和do-while循环的区别)
  - [10.for循环](#10for循环)
  - [11.三种循环对比](#11三种循环对比)
  - [12.break关键字](#12break关键字)
  - [13.continue关键字](#13continue关键字)
  - [14.break和continue对比](#14break和continue对比)
  - [15.debug调试](#15debug调试)
  - [16. 多重循环](#16-多重循环)
  - [17.break关键字补充](#17break关键字补充)


## 流程控制

### 1. 基本if结构

> ```
> if (布尔表达式) {
>     // 代码块1
> }
> ```

> 对布尔表达式进行判断:
> 
> - 结果为true，则先执行代码块1，再执行后续代码。
> - 结果为false，则跳过代码块1，直接执行后续代码。

```java
/**
 *  需求：提示用户输入年龄 根据年龄判断 用户是否成年
 */
public class TestIfInputAge {
    public static void main(String[] args) {
        // 将光标移动到Scanner单词结尾 alt + 回车 导包(注意不要选错)
        Scanner input = new Scanner(System.in);

        System.out.println("请输入您的年龄");

        int age = input.nextInt();

        if(age >= 18){
            System.out.println("恭喜你，成年了");
        }
        System.out.println("程序结束");
    }
}

```

### 2.if-else结构

> ```
> if (布尔表达式) {
>     // 代码块1
> } else {
>     // 代码块2
> }
> ```

> 对布尔表达式进行判断
> 
> - 结果为true，则先执行代码块1，再退出整个结构，执行后续代码。
> - 结果为false，则先执行代码块2，再退出整个结构，执行后续代码。

```java
/**
 *  需求：使用if-else结构  根据用户输入的分数判断是否可以获得奖励
 *
 *
 *  如果
 *  java成绩大于90分 并且 数据库成绩大于80分
 *  或者
 *  css成绩大于85 并且 js成绩等于100分
 *  获得奖励苹果14袋
 */
public class TestIfElseInputScore {
    public static void main(String[] args) {
        Scanner input =new Scanner(System.in);

        System.out.println("请输入java成绩");

        double javaScore = input.nextDouble(); // 这里可以接收int类型的整数 将实现自动类型提升

        System.out.println("请输入数据库成绩");

        double dbScore = input.nextDouble();

        System.out.println("请输入css成绩");

        double cssScore = input.nextDouble();

        System.out.println("请输入js成绩");

        double jsScore = input.nextDouble();

        if((javaScore > 90 && dbScore > 80) ||   (cssScore > 85 && jsScore == 100)){
            System.out.println("奖励苹果14袋");
        }else{
            System.out.println("继续加油~");
        }

        System.out.println("程序结束");
    }
}

```

### 3. 多重if结构

> ```
> if (布尔表达式1) {
>     // 代码块1
> } else if (布尔表达式2) {
>     // 代码块2
> } else if (布尔表达式3) {
>     // 代码块3
> } else {
>     // 代码块4
> }
> ```

> 执行流程：
> 
> 表达式1为true，则执行代码块1，再退出整个结构。
>
> 表达式2为true，则执行代码块2，再退出整个结构。
>
> 表达式3为true，则执行代码块3，再退出整个结构。
>
> 以上均为false，则执行代码块4，再退出整个结构。
>
> 注意：相互排斥，有一个为true，其他均不再执行，
> 适用于区间判断。

```java
/**
 *  多重if
 *  需求：根据名次进行奖励
 *  第一名 奖励夏令营一个月
 *  第二名 奖励苹果14袋
 *  第三名 奖励笔记本一本
 *  第四名 口头表扬一次
 *
 *  分析：以上需求有多个条件 使用基本if结构 或者 if-else结构均不能实现
 *  必须使用多重if结构实现
 *  多重if中的else if 是没有个数限制的 根据需求书写
 *  多重if中的else 是可选的 根据需求是否书写 如果书写了else 表示多选1
 *  如果没有书写 可能为多选0 或者 多选1
 *
 *  这个类中的需求 不涉及到区间判断 所以对条件的顺序 没有要求
 *  但是推荐写为升序的 因为阅读性更高
 *
 *
 */
public class TestManyIf {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("请输入您的名次");

        int number = input.nextInt();

        if (number == 2) {
            System.out.println("奖励苹果14袋");
        } else if (number == 1) {
            System.out.println("奖励夏令营一个月");
        } else if (number == 4) {
            System.out.println("口头表扬一次");
        } else if (number == 3) {
            System.out.println("奖励笔记本一本");
        } else {
            System.out.println("继续努力");
        }

        System.out.println("程序结束");
    }
}

```


````java
/**
 *  使用多重if实现根据分数进行等级判断
 *  分数大于90分 优秀
 *  分数大于80分 良好
 *  分数大于70分 中等
 *  分数大于59分 及格
 *  小于60分 不及格
 *
 *
 *  分析：以上需求对分数做判断 属于连续的区间的操作 判断条件必须是升序的 或者 降序
 *  不能为乱序的
 */
public class TestManyIfInputScore {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("请输入您的分数");

        double score = input.nextDouble();

        if(score > 80 ){
            System.out.println("良好");
        }else if(score > 90){
            System.out.println("优秀");
        }else if(score > 59){
            System.out.println("及格");
        }else if(score > 70){
            System.out.println("中等");
        }else {
            System.out.println("不及格");
        }

        System.out.println("程序结束");
    }
}

````

### 4. 嵌套if

> 嵌套if ： 一个完整的if结构中 嵌套另外一个if结构  支持任意组合
>
> 格式正确的情况 支持任意组合 通常不会超过三层


```java
/**
 *  需求：学校举行百米跑步比赛 根据跑步时间决定是否可以进入决赛 跑步时间小于14秒
 *  然后再根据性别分别分组 男子组 或者 女子组
 *
 */
public class TestInnerIf {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("请输入你的跑步时间");

        double time = input.nextDouble();

        if (time < 14) {
            System.out.println("请输入你的性别");
            String sex = input.next();
            // 表示开始分组 进行性别判断
            // 对字符串进行判断 必须使用equals方法
            // 用法： 变量名.equals("比较的内容")
            if (sex.equals("男")) {
                System.out.println("恭喜进入男子组");
            } else if (sex.equals("女")) {
                System.out.println("恭喜进入女子组");
            } else {
                System.out.println("性别不合适");
            }
        } else {
            System.out.println("很遗憾，没有进入决赛");
        }

        System.out.println("程序结束");
    }
}
```

### 5. switch

> ```
> switch (变量|表达式) {
> 	case 值1:
> 		逻辑代码1;
> 	case 值2:
> 		逻辑代码2;
> 	case 值n:
> 		逻辑代码n;
> 	default:
> 		未满足时的逻辑代码;
> }
> ```
> 执行逻辑：
> 
> - 如果变量中的值等于值1，则执行逻辑代码1。
> - 如果变量中的值等于值2，则执行逻辑代码2。
> - 如果变量中的值等于值n，则执行逻辑代码n。
> - 如果变量中的值没有匹配的case值时，执行default中的逻辑代码。
>
> **所有case的取值不可相同**。


> switch 结构
>
> 支持的数据类型“byte short int char String(JDK7+) 枚举
>
> switch用来判断某个值属于固定等值的情况
>
>
> break ： 单词意思-打破 折断
>
> 用于在switch中 表示跳出switch结构
>
>
> default 关键字在switch中是可选的 根据需求是否书写
>
> 如果需要每种情况都是相互独立的 那么需要在每个case之后加上break
>
> 因为default位置不固定 所以也要求default之后加上break(前提是每个情况都独立)
>
> 加上break还可以提高代码的阅读性

```java
/**
 *  需求：根据名次进行奖励
 *    第一名 奖励夏令营一个月
 *    第二名 奖励苹果14袋
 *    第三名 奖励笔记本一本
 *    第四名 口头表扬一次
 */
public class TestSwitch1 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("请输入你的名次");

        int number = input.nextInt();

        switch(number){
            case 2:
                System.out.println("奖励苹果14袋");
                break;
            case 1:
                System.out.println("奖励夏令营一个月");
                break;
            case 4:
                System.out.println("口头表扬一次");
                break;
            case 3:
                System.out.println("奖励笔记本一本");
                break;
            default:
                System.out.println("继续加油");
                break;
        }

        System.out.println("程序结束");

    }
}

```

> switch 结构
>
> 支持的数据类型“byte short int char String(JDK7+) 枚举
>
> switch用来判断某个值属于固定等值的情况

```java
/**
 *  需求：根据名次进行奖励
 *    第一名 奖励夏令营一个月
 *    第二名 奖励夏令营一个月
 *    第三名 奖励夏令营一个月
 *    第四名 口头表扬一次
 *
 * 我们可以根据需求合理的利用switch结构case穿透的特点来实现我们的需求
 * 多重if 和 switch 都可以处理 连续区间 或者是固定等值的情况
 * 但是多重if处理连续区间更合适
 * switch处理固定等值更合适
 */
public class TestSwitch2 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("请输入你的名次");

        int number = input.nextInt();

        switch (number) {
            case 1:
            case 2:
            case 3:
                System.out.println("奖励夏令营一个月");
                break;
            case 4:
                System.out.println("口头表扬一次");
                break;
            default:
                System.out.println("继续加油");
                break;
        }

        System.out.println("程序结束");
    }
}

```



>  switch 结构
>
> 支持的数据类型 byte short int char String(JDK7+) 枚举

```java
public class TestSwitch3 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        byte b1 = 1;
        short s1 = 2;
        int i1 = 3;
        char ch1 = '中'; // 注意char类型有三种赋值方式 所以case之后的值 也有三种写法
        String str = "5";


        switch (str) {
            case "5":
                System.out.println("变量值为1");
                break;
            case "b":
                System.out.println("变量值为2");
                break;
            case "d":
                System.out.println("变量值为3");
                break;
            case "c":
                System.out.println("变量值为4");
                break;
            default:
                System.out.println("变量值不为1234");
                break;
        }

        System.out.println("程序结束");
    }
}

```

### 6. 多重if和switch对比

> 多重if  和 switch 都可以处理 连续区间 或者是固定等值的情况
>
> 但是 多重if处理连续区间更合适
>
> switch处理固定等值更合适

### 7. while循环

> ```
> 计数器初始化；
> while ( 循环条件 ) {
>     循环操作；
>     计数器变化；
> }
> ```

>
> while单词：当……
>
> 任何循环都有四个必不可少的部分：
>
> - 1.计数器初始化
>
> - 2.循环条件
>
> - 3.循环体
>
> - 4.计数器变化
>
> 结合while循环两个案例总结：while循环可以用于处理循环次数确定 以及 循环次数不确定的情况
>
> 通常用来处理循环次数不确定的情况 因为循环次数确定的情况使用for循环更为简洁
>
>
> **while循环特点：先判断 后执行 如果条件不成立 则一次都不执行**


```java
/**
 *  while循环
 *  while单词：当……
 *  任何循环都有四个必不可少的部分：
 *      1.计数器初始化
 *      2.循环条件
 *      3.循环体
 *      4.计数器变化
 *
 *  使用while循环实现打印100遍好好学习
 */
public class TestWhile {
    public static void main(String[] args) {
        int i = 1; // 计数器初始化

        while(i <= 0){ // 判断条件
            System.out.println("第" + i + "次好好学习，天天向上"); // 循环体
            ++i; // 计数器变化
        }

        System.out.println("程序结束");
    }
}

```
示例2:

```java
/**
 *  需求：老师每天检查赵四的学习任务是否合格，如果不合格，则继续进行。
 *  老师给赵四安排的每天的学习任务为：
 *  上午阅读教材，学习理论部分，下午上机编程，掌握代码部分。
 *
 *  结合while循环两个案例总结：while循环可以用于处理循环次数确定 以及 循环次数不确定的情况
 *  通常用来处理循环次数不确定的情况 因为循环次数确定的情况使用for循环更为简洁
 *
 *  while循环特点：先判断 后执行 如果条件不成立 则一次都不执行
 *
 */
public class TestCheckStudy {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("请输入你的学习任务是否合格？y/n");

        String answer = input.next(); // 相当于计数器初始化

        while (answer.equals("n")) { // 判断条件
            // 循环体
            System.out.println("上午阅读教材，学习理论知识");
            System.out.println("下午敲代码，掌握代码知识");

            System.out.println("请输入你的学习任务是否合格？y/n");
            // 计数器变化
            answer = input.next();

        }


//        if (answer.equals("n")) {
//            System.out.println("上午阅读教材，学习理论知识");
//            System.out.println("下午敲代码，掌握代码知识");
//        } else {
//            System.out.println("恭喜你，完成任务");
//        }

        System.out.println("恭喜你，完成任务");

        System.out.println("程序结束");
    }
}

```

### 8.do-while循环

> ```
> 计数器初始化；
> do {
>     循环操作；
>     计数器变化；
> } while (循环条件);
> ```

```java
/**
 * 经过几天的学习，老师给赵四一道测试题，让他先上机编写程序完成，
 * 然后老师再检查是否合格。如果不合格，则继续编写……
 */
public class TestCheckStudy {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        String answer;
        do {
            System.out.println("上机编写测试题……");
            System.out.println("请输入成绩是否合格？y/n");
            answer = input.next();
        } while(answer.equals("n"));

//        if (answer.equals("n")) {
//            System.out.println("不合格，继续上机编写测试题");
//        } else {
//            System.out.println("恭喜你，完成任务");
//        }
        System.out.println("恭喜你，完成任务");
        System.out.println("程序结束");
    }
}

```


```java
/**
 *  使用do-while循环实现打印100次好好学习
 *
 *  do-while循环可以用于实现循环次数确定 以及 循环次数不确定的情况
 *  通常用于处理循环次数不确定的情况 因为循环次数确定 for循环更为简洁
 *
 *  while循环和do-while循环的区别？
 *  while循环是先判断后执行 条件不成立一次都不执行
 *  do-while先执行后判断 不管条件是否成立 至少执行一次
 *
 *
 */
public class TestDoWhile {
    public static void main(String[] args) {
        int i = 1;
        do{
            System.out.println("第" + i + "次好好学习");
            i++;
        }while(i <= 100);
        System.out.println("程序结束 " );
    }
}

```

### 9. while循环和do-while循环的区别？

> while循环是先判断后执行 条件不成立一次都不执行
>
> do-while先执行后判断 不管条件是否成立 至少执行一次

### 10.for循环

>  ```
>  for (计数器初始化; 循环条件; 计数器变化) { 
>      循环体;
>  }
>  ```

>  for循环 ： for 为了……
>
> 循环次数确定的情况 使用for循环 更加简洁
>
> 注意for循环的执行顺序：
>
> 第一轮：
>
> 1.执行计数器初始化 并且只执行一次
>
> 2.判断条件
>
> 3.执行循环体
>
> 4.执行计数器变化
>
> 后续轮：
>
> 直接从第2步开始执行

```java
/**
 *  需求：使用for循环打印100次好好学习
 */
public class TestForPrint {
    public static void main(String[] args) {
        for (int i = 1;i <= 10000;i++) {
            System.out.println("第" + i + "次好好学习");
        }
        System.out.println("程序结束");
    }
}

```

```java
/**
 *  使用for循环录入某同学的5门成绩  计算平均分
 */
public class TestInputScore {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        System.out.println("请输入名字：");
        String name = input.next();
        double sum = 0; // 用于累计所有的成绩
        for (int i = 1; i <= 5; i++) {
            System.out.println("请输入第" + i + "门成绩");
            double score = input.nextDouble();
            sum = sum +  score; //sum += score;
        }

        System.out.println(name + "同学的平均分为：" + sum / 5);
        System.out.println("程序结束");
    }
}

```

> 在循环中，如何实现递减的效果：使用一个固定的数减去一个递增的值

```java
/**
 *  根据用户输入的数字打印加法表
 *
 *  如何实现递减的效果：
 *  使用一个固定的数减去一个递增的值
 *
 */
public class TestAddition {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        System.out.println("请输入一个数字");
        int number = input.nextInt();
        for (int i = 0; i <= number; i++) {
            System.out.println(i + "+" + (number - i) + "=" + number);
        }
    }
}
```

### 11.三种循环对比

> 执行顺序 
>
> while 循环：先判断，再执行
>
> do-while循环：先执行，再判断
>
> for循环：先判断，再执行
> 
>
> 适用情况
>
> 循环次数确定的情况，通常选用for循环
>
> 循环次数不确定的情况，通常选用while或do-while循环

### 12.break关键字

> break关键字：可以用于switch或者循环结构中 分别表示跳出switch结构 或者 中断(跳出)循环
>
> 未执行完的循环次数 不再执行 在循环结构中通常(99%)要结合分支语句来使用

```java
/**
 *  使用for循环模拟跑步10圈 当跑完第8圈 退出
 */
public class TestBreak {
    public static void main(String[] args) {
        for (int i = 1; i <= 10; i++) {
            System.out.println("跑步第" + i + "圈");

            if (i == 8) {
                System.out.println("退出比赛");
                break;
            }

        }
        System.out.println("------------------------------------------------");

        int i = 1;
        while (i <= 10) {
            System.out.println("跑步第" + i + "圈");
            if (i == 5) {
                break;
            }
            i++;
        }
        System.out.println("------------------------------------------------");

        i = 1;
        do {
            System.out.println("跑步第" + i + "圈");
            if (i == 5) {
                break;
            }
            i++;
        } while (i <= 10);

        System.out.println("程序结束");
    }
}


```

```java
/**
 * 循环录入某学生5门课的成绩并计算平均分，如果某分数录入为负，停止录入并提示录入错误
 */
public class TestInputScore {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        double sum = 0;

        boolean flag = true; // 定义布尔类型变量 初始值为true

        for (int i = 1; i <= 5; i++){
            System.out.println("请输入第" + i + "门成绩");
            double score = input.nextDouble();
            if(score < 0){
                flag = false;
                System.out.println("分数录入有误，停止录入");
                break;
            }
            sum += score;
        }

        if (flag) {
            System.out.println("平均分为：" + sum / 5);
        } else {
            System.out.println("分数录入有误，不再计算平均分");
        }
    }
}

```

```java
/**
 *  1~10之间的整数相加，得到累加值大于20的当前数
 */
public class TestAddition {
    public static void main(String[] args) {
        int sum = 0;
        for (int i = 1; i <= 10; i++) {
            sum += i;
            if (sum > 20) {
                break;
            }
        }
        System.out.println("sum = " + sum);
    }
}

```

### 13.continue关键字

> continue：单词 继续  只能用在循环中 表示跳过本次循环 继续执行下一次循环

```java
public class TestContinue {
    public static void main(String[] args) {
        for(int i  =1;i <= 10;i++){
            if(i == 5){
                break;
            }
            System.out.println("i = " + i);
        }

        System.out.println("----------------------------------");

        for (int i  =1; i <= 10; i++) {
            if (i == 5) {
                continue;
            }
            System.out.println("i = " + i);
        }
    }
}

```


```java
/**
 *  循环录入Java课的学生成绩，统计分数大于等于80分的学生比例
 */
public class TestInputScore {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);
        System.out.println("请输入人数");
        int count = input.nextInt();
        double sum = 0; // 定义sum变量 用于统计大于80分的人数

        for (int i = 1; i <= count; i++) {
            System.out.println("请输入第" + i + "个人的成绩");
            double score = input.nextDouble();
            if (score <= 80) {
                continue;
            }
            sum++;
        }
        System.out.println("大于80分的人数占比为：" + sum / count * 100 + "%" );
    }
}

```


```java
/**
 *  求1~10之间的所有偶数和
 */
public class TestAddition {
    public static void main(String[] args) {
        int sum = 0;
        for (int i = 1;i <= 10;i++) {
            if (i % 2 == 1) {
                continue; 
            }
            sum += i;
        }
        System.out.println("sum = " + sum);

        sum = 0;

        for (int i = 0; i <= 10; i+=2) {
            sum +=i;
        }
        System.out.println("sum = " + sum);

        sum = 0;

        for (int i = 1; i <= 10; i++) {
            if(i % 2 == 0){
                sum += i;
            }
        }

        System.out.println("sum = " + sum);
    }
}

```

### 14.break和continue对比

> 使用场合：
> 
> - break用于switch结构和循环结构中
> - continue用于循环结构中
>
> 作用（循环结构中）：
>
> - break语句终止某个循环，程序跳转到循环块外的下一条语句
> - continue跳出本次循环，进入下一次循环
> - 双重循环亦如此 

### 15.debug调试

![](assets/flow_control/debug调试.png)

### 16. 多重循环

> 关于多重循环执行过程：外层循环变量变化一次  内层循环变量 变化一轮
>
> 关于多重循环打印图案的规律：
>
> - 外层循环控制行数
> - 内层循环控制列数


打印矩形

```java
/**
 *  分别使用单层循环 以及 双重循环 打印矩形
 *
 *  关于多重循环执行过程：外层循环变量变化一次  内层循环变量 变化一轮
 *  关于多重循环打印图案的规律：
 *  外层循环控制行数
 *  内层循环控制列数
 *
 */
public class PrintRectangle {
    public static void main(String[] args) {
        for (int i =1; i <= 5; i++) {
            System.out.println("*****");
        }
        System.out.println("--------------------------------------------------------");

        for (int j = 1; j <= 8; j++) {
            for (int i = 1; i <= 4; i++) {
                System.out.print("*");
            }
            System.out.println();
        }
    }
}

```

打印平行四边形

```java
/**
 *  关于多重循环打印图案的规律：
 *  外层循环控制行数
 *  内层循环控制列数
 *
 */
public class PrintParallelogram {
    public static void main(String[] args) {
        for (int i=1; i <=5; i++) { // 外层循环 控制行数
            // 左半部分
            for (int j = 5; j >= i; j--) {
                System.out.print("$");
            }
            // 右半部分
            for (int j = 1; j <= 5; j++) {
                System.out.print("*");
            }
            // 换行
            System.out.println();
        }
    }
}

```

打印三角形

```java
/**
 *  打印三角形规律：
 *  （1）第一行元素的个数决定计数器的初始值
 *  （2）如果元素个数越来越多 那么计数器就++  此时必须设置一个上限 也就是判断条件必须为小于或者小于等于某个值
 *  （3）如果元素个数越来越少 那么计数器就--  此时必须设置一个下限 也就是判断条件必须为大于或者大于等于某个值
 */
public class PrintTriangle {
    public static void main(String[] args) {
        for (int i = 1; i <= 5; i++) { // 外层循环5次  5行
            // 左半部分
            for (int j = 5; j >= i; j--) {
                System.out.print("%");
            }

            // 右半部分
            // 每一行元素的个数 为 行数 * 2 - 1
            for (int j = 1; j <= 2 * i - 1; j++) {
                System.out.print("*");
            }

            // 换行
            System.out.println();
        }
    }
}

```

### 17.break关键字补充

> break关键字分别表示跳出switch结构 或者 循环结构
>
> 默认情况下 只会中断离其最近的结构
>
> 也可以自定义标记 使用break 关键字 跳出指定标记的结构

```java
public class TestBreak {
    public static void main(String[] args) {

        abc: for (int i = 1; i <= 5; i++) {
            for (int j = 1; j <= 5; j++) {
                System.out.print(j + "\t");
                if (j == 3) {
                    break abc;
                }
            }
            System.out.println();
        }
    }
}

```

