## Java概述和环境搭建

### 1. 单位换算

> 1TB = 1024GB
>
> 1GB = 1024MB
>
> 1MB = 1024KB
>
> 1KB = 1024Byte (字节)
>
> 1Byte = 8 bit(位) 
>
> 注意：一个字节占8位

### 2. DOS命令

> DOS : Disk Operation System 磁盘操作系统 即用于操作本地磁盘的系统  

| 命令               | 操作符号      |
| ------------------ | ------------- |
| 盘符切换命令       | `盘符名:`     |
| 查看当前文件夹内容 | `dir`         |
| 进入文件夹命令     | `cd 文件夹名` |
| 退出文件夹命令     | `cd ..`       |
| 退出到磁盘根目录   | `cd \`        |
| 清屏               | `cls`         |
| 退出               | `exit`        |

### 3. 名词解释

* **JVM**（Java Virtual Machine ）: Java虚拟机  JVM相当于一个软件 在不同的平台模拟相同的环境 以实现跨平台的效果
* **JRE**(Java Runtime Environment) : Java运行环境，包含`JVM` 和运行时所需要的`核心类库`。
* **JDK**(Java Development Kit) : Java开发工具包 ，包含`JRE` 和开发人员使用的工具。

> 三者关系：JDK包含 JRE  JRE包含JVM  

### 4. 安装JDK

所有选项全部下一步即可 默认安装在C盘 ：`C:\Program Files\Java` 

### 5.配置环境变量

> 右键此电脑 --> 高级系统设置 --> 高级 --> 环境变量
>
> 系统变量 --> 新建变量
>
> 名：JAVA_HOME
>
> 值： C:\Program Files\Java\jdk1.8.0_131
>
> 找到Path变量===》编辑 ====》新建
>
> 直接写值：%JAVA_HOME%\bin
>
> 所有已打开的窗口全部确定即可

### 6.测试

> 徽标 + R 输入 CMD 
>
> javac -version 
>
> java -version
>
> 以上两个命令都出现版本号表示安装JDK并且环境变量配置成功

### 7.关于配置环境变量问题补充

> 1.为什么不直接在Path变量中配置C:\Program Files\Java\jdk1.8.0_131\bin
>
> 直接在Path变量中写为C:\Program Files\Java\jdk1.8.0_131\bin 这样的格式目前也是没有问题的 也可以使用
>
> 但是后续我们使用的一些工具将默认查找JAVA_HOME变量 比如 tomcat maven等等 
>
> 2.为什么要配置环境变量？
>
> 配置环境变量相当于把bin目录下的命令通知给操作系统 便于我们使用当前目录下对应的命令
>
> 3.为什么不配置classpath ？
>
> classpath表示类路径 (即JVM加载类会寻找的路径)
>
> 早期(JDK1.5之前)的JDK都需要配置此环境变量  从JDK1.5开始 不需要人为的配置此变量 
>
> 如果配置了，一定删掉！！！

### 8.第一个Java程序

#### 8.1 源代码

```java
public class HelloWorld{
	public static void main(String [] args){ 
		System.out.print("hello world");
	}
}
```

#### 8.2 单词解释

> public 公开的
>
> class 类
>
> static 静态的
>
> void 无效的 空的
>
> main 主要的
>
> String 字符串
>
> args arguments 参数 复数形式
>
> System 系统
>
> out 出
>
> print 打印

#### 8.3 注意事项

> 1.文件名必须与类名完全保持一致 包括大小写
>
> 2.注意单词大小写 
>
> 3.代码中的标点符号默认都是英文模式的 
>
> 4.注意合适的缩进 每遇到一个大括号就缩进一个tab键的距离

### 9. 测试运行

> 在java源文件上方的地址栏中输入CMD 打开DOS命令窗口
>
> 1.输入 javac + java文件名 编译 ，将java文件编译为class文件(c 表示单词 Complier 即编译的意思)
>
> 2.输入 java + class文件名 执行class文件

### 10.关键字

* 1.什么是关键字？
  * 被Java官方赋予了特殊含义的单词 全部小写 
* 2.注意事项：
  * 关键字众多，不需要记忆，注意后续取名字避免和关键字冲突即可

