# XML

## 1、名称简介
XML：e<span style="color:blue;font-weight:bold;">X</span>tensible <span style="color:blue;font-weight:bold;">M</span>arkup <span style="color:blue;font-weight:bold;">L</span>anguage 可扩展标记语言

<br/>

- 可扩展：XML允许自定义标签
- 标记语言：主要由标签组成

<br/>



## 2、应用场景
- <del>跨平台数据传输格式</del>（目前已经被 JSON 取代）
- 配置文件
	- Tomcat：server.xml、context.xml
	- Mybatis：mybatis-config.xml、EmployeeMapper.xml
	- 后端Web应用：web.xml
	- Spring框架：applicationContext.xml
	- ……

<br/>



```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee https://jakarta.ee/xml/ns/jakartaee/web-app_5_0.xsd"
         version="5.0">
    <servlet>
        <servlet-name>EmpServlet</servlet-name>
        <servlet-class>com.atguigu.servlet.EmpServlet</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>EmpServlet</servlet-name>
        <url-pattern>/EmpServlet</url-pattern>
    </servlet-mapping>

</web-app>
```

<br/>



## 3、XML语法规则
- XML文档开头必须有XML声明
- 根标签有且只能有一个
- 双标签必须正确关闭
- 标签可以嵌套但不能交叉嵌套
- 注释不能嵌套
- 属性必须有值
- 属性值必须加引号，单引号、双引号都可以
- 不区分大小写

<br/>



## 4、XML约束
XML约束规定了XML文档中可以包含哪些标签、标签有哪些子标签、标签有哪些属性、属性有哪些值……常用的两种约束形式是：
- DTD约束
- Schema约束

<br/>

所以虽然XML允许自定义标签，但是官方通过XML约束做好规定之后，我们就必须按照约束的要求来写，不能随便写了。

<br/>

这也解释了为什么XML语法规则和HTML这么像：XML语法规则+HTML约束=HTML语法规则

<br/>



## 5、XML学习目标
在 IDEA 的辅助下能够完成 XML 代码编写即可。