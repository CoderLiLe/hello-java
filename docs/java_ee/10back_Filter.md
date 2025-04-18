## 1、提出问题
![images](./images/img005.png)

<br/>

## 2、三要素
### ①拦截
作为过滤器这样的组件，首先需要能够把请求拦截住，然后才能做后续的相关操作。

<br/>

### ②过滤
通常是基于业务功能的需要，在拦截到请求之后编写特定的代码，对请求进行相关的处理或检查。<br/>

最典型的就是登录检查：检查当前请求是否已经登录。

<br/>

### ③放行
如果当前请求满足过滤条件，那么就应该放行：让请求继续去找它原本要访问的资源。

<br/>

## 3、HelloWorld
### ①创建Filter类
要求实现接口：jakarta.servlet.Filter。更简洁的做法是继承jakarta.servlet.http.HttpFilter类。

<br/>

```java
/**  
 * 假设请求中携带一个特定的请求参数表示用户已经登录，可以访问私密资源。  
 * 特定请求参数名称：message，特定的值：monster  
 */public class Filter01HelloWorld extends HttpFilter {  
  
    @Override  
    public void doFilter(HttpServletRequest request, HttpServletResponse response, FilterChain chain) throws ServletException, IOException {  
  
        // 1、获取请求参数  
        String message = request.getParameter("message");  
  
        // 2、检查请求参数是否满足预设的要求  
        if ("monster".equals(message)) {  
            // 3、满足条件的请求放行  
            chain.doFilter(request, response);  
        } else {  
            // 4、不满足预设条件就把请求转发到拒绝页面  
            request.getRequestDispatcher("/WEB-INF/pages/forbidden.html").forward(request, response);  
        }  
  
    }  
}
```

### ②注册Filter类
```xml
<!-- 注册 Filter --><filter>  
    <!-- Filter 友好名称 -->  
    <filter-name>Filter01HelloWorld</filter-name>  
  
    <!-- Filter 全类名 -->  
    <filter-class>com.atguigu.filter.filter.Filter01HelloWorld</filter-class>  
</filter>  
<filter-mapping>  
    <!-- 引用 Filter 友好名称 -->  
    <filter-name>Filter01HelloWorld</filter-name>  
  
    <!-- 当前 Filter 要拦截的请求的 URL 地址的匹配模式 -->  
    <url-pattern>/private/*</url-pattern>  
</filter-mapping>
```

<br/>

## 4、Filter生命周期
| |Servlet生命周期|Filter生命周期|
|---|---|---|
|创建对象|<span style="color:blue;font-weight:bolder;">第一次接收到请求</span>创建对象<br/>通过反射调用无参构造器<br/>执行一次|<span style="color:blue;font-weight:bolder;">Web应用启动</span>时创建对象<br/>通过反射调用无参构造器<br/>执行一次|
|初始化|创建对象之后立即执行<br/>init()方法<br/>执行一次|创建对象之后立即执行<br/>init()方法<br/>执行一次|
|干活|每一次接收到请求，处理请求<br/><span style="color:blue;font-weight:bolder;">service()</span>方法<br/>可能多次|每一次拦截到请求，过滤请求<br/><span style="color:blue;font-weight:bolder;">doFilter()</span>方法<br />可能多次|
|销毁|Web应用卸载时执行<br/>destroy()方法<br/>执行一次|Web应用卸载时执行<br/>destroy()方法<br/>执行一次|

<br/>

```java  
import jakarta.servlet.FilterChain;  
import jakarta.servlet.ServletException;  
import jakarta.servlet.http.HttpFilter;  
import jakarta.servlet.http.HttpServletRequest;  
import jakarta.servlet.http.HttpServletResponse;  
  
import java.io.IOException;  
  
public class Filter02LifeCycle extends HttpFilter {  
  
    // 生命周期相关：无参构造器  
    public Filter02LifeCycle() {  
        System.out.println("Filter02LifeCycle 执行了无参构造器！创建了对象！");  
    }  
  
    // 生命周期相关：初始化操作  
    @Override  
    public void init() throws ServletException {  
        System.out.println("Filter02LifeCycle 执行了init()方法，初始化完成！");  
    }  
  
    // 生命周期相关：清理或销毁操作  
    @Override  
    public void destroy() {  
        System.out.println("Filter02LifeCycle 执行了destroy()方法！");  
    }  
  
    // 生命周期相关：过滤请求操作  
    @Override  
    protected void doFilter(HttpServletRequest request, HttpServletResponse response, FilterChain chain) throws IOException, ServletException {  
        System.out.println("Filter02LifeCycle 执行了doFilter()方法！");  
        chain.doFilter(request, response);  
    }  
}
```

<br/>

```xml
<filter>  
    <filter-name>Filter02LifeCycle</filter-name>  
    <filter-class>com.atguigu.filter.filter.Filter02LifeCycle</filter-class>  
</filter>  
<filter-mapping>  
    <filter-name>Filter02LifeCycle</filter-name>  
    <!-- 拦截当前 Web 应用下的所有资源 -->  
    <url-pattern>/*</url-pattern>  
</filter-mapping>
```

## 5、Filter链
### ①Filter链的形成
当多个Filter拦截同一个资源，那么访问这个资源的请求就需要逐个经过各个Filter。<br/>

![images](./images/img006.png)

<br/>

### ②Filter链的执行
- 每个Filter都放行，请求才能到达原本要访问的目标资源
- 有任何一个Filter没有放行，那么后面的Filter和目标资源就都不会被执行
- Filter如果没有放行，那么需要给出响应。例如：转发、重定向等方式。
- Filter如果没有放行，也没有给出响应，那么浏览器窗口就是一片空白。

<br/>

### ③Filter链执行的顺序
参考web.xml中filter-mapping的顺序：
- filter-mapping靠前的：Filter执行时在外层（先执行：先开始，后结束）
- filter-mapping靠后的：Filter执行时在内层（后执行：后开始，先结束）

<br/>

本质上来说，同一个Filter链中的各个方法都是在同一个线程里依次调用的方法：

<br/>

![images](./images/img007.png)

<br/>

### ④引申
- 方法栈：同一个线程内，先调用的方法后结束；后调用的方法先结束
- 同一个线程内，所有操作本质上都是按顺序执行的。前面操作没有执行完，后面操作就需要等待。
- 在不同线程（或进程）内，各个操作都不需要等待其它线程中操作的执行。

<br/>

- 同步：操作之间<span style="color:blue;font-weight:bolder;">需要彼此等待</span>，按顺序依次执行
- 异步：操作之间<span style="color:blue;font-weight:bolder;">不需要彼此等待</span>，同时各自执行

<br/>

## 6、登录检查练习
### ①需求说明
凡是对Soldier增删改查操作，都需要登录才能访问。这里我们要拦截的资源地址：

- <span style="color:blue;font-weight:bolder;">/SoldierServlet/</span>showList
- <span style="color:blue;font-weight:bolder;">/SoldierServlet/</span>toAddPage
- <span style="color:blue;font-weight:bolder;">/SoldierServlet/</span>saveSoldier
- <span style="color:blue;font-weight:bolder;">/SoldierServlet/</span>toEditPage
- <span style="color:blue;font-weight:bolder;">/SoldierServlet/</span>remove

<br/>

### ②创建Filter类
```java  
import com.demo.entity.User;  
import jakarta.servlet.FilterChain;  
import jakarta.servlet.ServletException;  
import jakarta.servlet.http.HttpFilter;  
import jakarta.servlet.http.HttpServletRequest;  
import jakarta.servlet.http.HttpServletResponse;  
import jakarta.servlet.http.HttpSession;  
  
import java.io.IOException;  
  
public class LoginFilter extends HttpFilter {  
  
    @Override  
    protected void doFilter(HttpServletRequest request, HttpServletResponse response, FilterChain chain) throws IOException, ServletException {  
        HttpSession session = request.getSession();  
        User loginUser = (User) session.getAttribute("loginUser");  
        if (loginUser == null) {  
            request.setAttribute("message", "请登录后再操作！");  
            request.getRequestDispatcher("/UserServlet/toLoginPage").forward(request, response);  
        } else {  
            chain.doFilter(request, response);  
        }  
    }  
}
```

<br/>

### ③注册Filter类
```xml
<filter>  
    <filter-name>loginFilter</filter-name>  
    <filter-class>com.atguigu.demo.filter.LoginFilter</filter-class>  
</filter>  
<filter-mapping>  
    <filter-name>loginFilter</filter-name>  
    <url-pattern>/SoldierServlet/*</url-pattern>  
</filter-mapping>
```