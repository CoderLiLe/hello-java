# Spring FactoryBean 机制源码深度解析

> 本文深入分析 Spring FactoryBean 的设计原理与源码实现，覆盖 FactoryBean 接口、`&` 前缀机制、getObjectForBeanInstance() 完整链路、SmartFactoryBean 提前初始化以及 factoryBeanObjectCache 缓存策略。
> 相关模块文档：[spring-beans](../modules/L2-spring-beans.md)

---

## 一、FactoryBean 是什么

**FactoryBean 不是普通的 Bean**。当从容器中通过 beanName 获取时，拿到的是 `getObject()` 返回的对象，而非 FactoryBean 自身。它是 Spring 中工厂模式的实现——将复杂 Bean 的创建逻辑封装在一个 Bean 中，由容器管理其生命周期。

```java
// 获取 FactoryBean 生产的对象
context.getBean("myFactory");   // → T

// 获取 FactoryBean 自身
context.getBean("&myFactory");  // → FactoryBean<T>
```

---

## 二、核心接口

```java
public interface FactoryBean<T> {

    // 工厂生产的对象类型（用于 bean 查找时的类型判断）
    String OBJECT_TYPE_ATTRIBUTE = "factoryBeanObjectType";

    // ★ 返回工厂创建的对象
    @Nullable
    T getObject() throws Exception;

    // 返回 getObject() 创建的对象的类型
    @Nullable
    Class<?> getObjectType();

    // 创建的对象是否为单例（默认 true）
    default boolean isSingleton() {
        return true;
    }
}
```

### 关键子接口

```java
// SmartFactoryBean: 指示是否在容器启动时就要初始化
public interface SmartFactoryBean<T> extends FactoryBean<T> {
    default boolean isEagerInit() { return false; }
    default boolean isPrototype() { return false; }
}
```

---

## 三、`&` 前缀机制

### 3.1 常量定义

```java
// BeanFactory 接口
String FACTORY_BEAN_PREFIX = "&";
```

### 3.2 BeanName 转换

```java
// AbstractBeanFactory.transformedBeanName()
protected String transformedBeanName(String name) {
    // 去除 & 前缀（可能有多个）
    String canonicalName = BeanFactoryUtils.transformedBeanName(name);

    // 如果是 FactoryBean 的别名，也需要转换
    ...
    return canonicalName;
}

// BeanFactoryUtils.transformedBeanName()
public static String transformedBeanName(String name) {
    if (!name.startsWith(BeanFactory.FACTORY_BEAN_PREFIX)) {
        return name;
    }
    // 循环去除所有 & 前缀
    return transformedBeanNameCache.computeIfAbsent(
        name, beanName -> {
            do {
                beanName = beanName.substring(FACTORY_BEAN_PREFIX.length());
            } while (beanName.startsWith(FACTORY_BEAN_PREFIX));
            return beanName;
        });
}
```

### 3.3 是否是 FactoryBean 引用

```java
// BeanFactoryUtils.isFactoryDereference()
public static boolean isFactoryDereference(String name) {
    return name != null && name.startsWith(BeanFactory.FACTORY_BEAN_PREFIX);
}
```

---

## 四、getBean() 完整处理链路

### 4.1 doGetBean() 中的处理

```
doGetBean(name, requiredType, args, typeCheckOnly):
  │
  ├── ① 转换 beanName: transformedBeanName(name)
  │     └── "&myFactoryBean" → "myFactoryBean"
  │
  ├── ② 从缓存获取: getSingleton(beanName)
  │     └── 此时得到的是 FactoryBean 实例本身
  │
  ├── ③ 如果缓存未命中 → createBean() → doCreateBean()
  │     └── 创建 FactoryBean 实例 (和普通 Bean 一样走完整生命周期)
  │
  └── ④ ★ getObjectForBeanInstance(sharedInstance, name, beanName, mbd):
        └── 判断是否需要解引用 FactoryBean (§4.2)
```

### 4.2 getObjectForBeanInstance() — 核心解引用

```java
protected Object getObjectForBeanInstance(
        Object beanInstance, String name, String beanName, RootBeanDefinition mbd) {

    // ① 如果 name 以 & 开头 → 返回 FactoryBean 自身
    if (BeanFactoryUtils.isFactoryDereference(name)) {
        if (beanInstance instanceof NullBean) {
            return beanInstance;
        }
        if (!(beanInstance instanceof FactoryBean)) {
            throw new BeanIsNotAFactoryException(beanName, beanInstance.getClass());
        }
        // 标记此 BeanDefinition 为 FactoryBean
        if (mbd != null) {
            mbd.isFactoryBean = true;
        }
        return beanInstance;
    }

    // ② 如果不是 FactoryBean → 直接返回
    if (!(beanInstance instanceof FactoryBean<?> factoryBean)) {
        return beanInstance;
    }

    // ③ 是 FactoryBean 且不是 & 前缀 → 需要获取 getObject() 的结果
    Object object = null;
    if (mbd != null) {
        mbd.isFactoryBean = true;
    }

    // ④ 尝试从 factoryBeanObjectCache 获取
    object = getCachedObjectForFactoryBean(beanName);

    // ⑤ 缓存未命中 → 调用 factoryBean.getObject()
    if (object == null) {
        object = getObjectFromFactoryBean(factoryBean, beanName, !synthetic);
    }

    return object;
}
```

### 4.3 getObjectFromFactoryBean() — 实际调用

```java
// FactoryBeanRegistrySupport
protected Object getObjectFromFactoryBean(FactoryBean<?> factory, String beanName, boolean shouldPostProcess) {

    // ① 单例 FactoryBean: 需要同步 + 缓存
    if (factory.isSingleton() && containsSingleton(beanName)) {
        synchronized (getSingletonMutex()) {
            // 双重检查
            Object object = this.factoryBeanObjectCache.get(beanName);
            if (object == null) {
                object = doGetObjectFromFactoryBean(factory, beanName);
                // 只有确实创建了新对象才缓存（避免缓存 null）
                Object alreadyThere = this.factoryBeanObjectCache.get(beanName);
                if (alreadyThere != null) {
                    object = alreadyThere;
                } else {
                    if (shouldPostProcess) {
                        if (isSingletonCurrentlyInCreation(beanName)) {
                            return object;  // 循环依赖：暂不后处理
                        }
                        beforeSingletonCreation(beanName);
                        try {
                            // ★ 执行 BeanPostProcessor.postProcessAfterInitialization()
                            object = postProcessObjectFromFactoryBean(object, beanName);
                        } finally {
                            afterSingletonCreation(beanName);
                        }
                    }
                    if (containsSingleton(beanName)) {
                        this.factoryBeanObjectCache.put(beanName, object);
                    }
                }
            }
            return object;
        }
    }

    // ② 原型 FactoryBean: 每次新建, 不缓存
    else {
        Object object = doGetObjectFromFactoryBean(factory, beanName);
        if (shouldPostProcess) {
            object = postProcessObjectFromFactoryBean(object, beanName);
        }
        return object;
    }
}

// ★ 实际调用 factoryBean.getObject()
private Object doGetObjectFromFactoryBean(FactoryBean<?> factory, String beanName) throws BeanCreationException {
    Object object;
    try {
        object = factory.getObject();
    } catch (FactoryBeanNotInitializedException ex) {
        throw new BeanCurrentlyInCreationException(beanName, ex.toString());
    } catch (Throwable ex) {
        throw new BeanCreationException(beanName, "FactoryBean threw exception on object creation", ex);
    }
    if (object == null) {
        if (isSingletonCurrentlyInCreation(beanName)) {
            throw new BeanCurrentlyInCreationException(
                beanName, "FactoryBean which is currently in creation returned null from getObject");
        }
        object = new NullBean();
    }
    return object;
}
```

---

## 五、容器启动时的提前初始化

### 5.1 preInstantiateSingletons() 中的 FactoryBean 处理

```java
// DefaultListableBeanFactory.preInstantiateSingletons()
public void preInstantiateSingletons() throws BeansException {
    List<String> beanNames = new ArrayList<>(this.beanDefinitionNames);

    for (String beanName : beanNames) {
        RootBeanDefinition bd = getMergedLocalBeanDefinition(beanName);

        if (!bd.isAbstract() && bd.isSingleton() && !bd.isLazyInit()) {
            // ★ 判断是否是 FactoryBean
            if (isFactoryBean(beanName)) {
                // 先实例化 FactoryBean 自身
                Object bean = getBean(FACTORY_BEAN_PREFIX + beanName);
                if (bean instanceof FactoryBean<?> factoryBean) {
                    boolean isEagerInit = false;

                    // 检查是否需要提前初始化
                    if (System.getSecurityManager() == null 
                        && factoryBean instanceof SmartFactoryBean<?> smartFactoryBean) {
                        isEagerInit = smartFactoryBean.isEagerInit();
                    }

                    // ★ 提前初始化：调用 getBean(beanName) 触发 getObject()
                    if (isEagerInit) {
                        getBean(beanName);
                    }
                }
            } else {
                // 普通 Bean: 直接创建
                getBean(beanName);
            }
        }
    }
    // ...
}
```

### 5.2 SmartFactoryBean 触发提前初始化

```
preInstantiateSingletons():
  ├── 普通 Bean (非 FactoryBean) → 直接 getBean() 创建
  │
  └── FactoryBean:
        ├── 先创建 FactoryBean 自身: getBean("&beanName")
        └── SmartFactoryBean.isEagerInit()?
              ├── true  → getBean("beanName") → 触发 getObject()
              └── false → 延迟到首次注入/获取时再调用 getObject()
```

---

## 六、缓存策略

### 6.1 factoryBeanObjectCache

```java
// FactoryBeanRegistrySupport
private final Map<String, Object> factoryBeanObjectCache = new ConcurrentHashMap<>(16);
```

**缓存条件**：
- FactoryBean.isSingleton() 返回 true
- 缓存到 factoryBeanObjectCache 中，key = beanName（不含 `&` 前缀）
- 原型 FactoryBean 不缓存，每次 getBean() 都调用 getObject()

### 6.2 缓存与单例缓存的区别

```
两种缓存, 不同用途:

singletonObjects (一级缓存):
  ├── 存放: FactoryBean 实例本身
  └── key: "myFactoryBean" (FactoryBean 自身的 beanName)

factoryBeanObjectCache:
  ├── 存放: FactoryBean.getObject() 返回的对象
  └── key: "myFactoryBean" (与 FactoryBean 共享 beanName)

获取逻辑:
  getBean("myFactoryBean")    → factoryBeanObjectCache 优先 → 未命中 → getObject()
  getBean("&myFactoryBean")  → singletonObjects 直接获取 → FactoryBean 实例
```

---

## 七、AbstractFactoryBean 模板类

```java
public abstract class AbstractFactoryBean<T>
    implements FactoryBean<T>, BeanClassLoaderAware, BeanFactoryAware, InitializingBean, DisposableBean {

    private T singletonInstance;      // 单例缓存
    private boolean initialized = false;  // 是否已初始化
    private T earlySingletonInstance;     // 早期单例引用

    // ★ getObject() 被声明为 final, 子类不能覆盖
    @Override
    public final T getObject() throws Exception {
        if (isSingleton()) {
            return (this.initialized ? this.singletonInstance : getEarlySingletonInstance());
        } else {
            return createInstance();  // → 子类实现
        }
    }

    // 子类必须实现: 单例情况下的创建逻辑
    @Override
    public final void afterPropertiesSet() throws Exception {
        if (isSingleton()) {
            this.initialized = true;
            this.singletonInstance = createInstance();
            this.earlySingletonInstance = null;
        }
    }

    // ★ 子类实现此方法, 实现对象创建
    protected abstract T createInstance() throws Exception;

    // 销毁回调
    @Override
    public void destroy() {
        if (isSingleton()) {
            destroyInstance(this.singletonInstance);  // → 子类实现
        }
    }
}
```

---

## 八、典型应用场景

### 8.1 MyBatis: SqlSessionFactoryBean

```java
public class SqlSessionFactoryBean 
    implements FactoryBean<SqlSessionFactory>, InitializingBean, ApplicationListener<ApplicationEvent> {

    private SqlSessionFactory sqlSessionFactory;

    // 注入配置
    public void setDataSource(DataSource dataSource) { ... }
    public void setConfigLocation(Resource configLocation) { ... }
    public void setMapperLocations(Resource[] mapperLocations) { ... }

    // InitializingBean: 在属性注入完成后构建 SqlSessionFactory
    @Override
    public void afterPropertiesSet() throws Exception {
        this.sqlSessionFactory = buildSqlSessionFactory();  // 复杂构建逻辑
    }

    // FactoryBean: 暴露构建好的对象
    @Override
    public SqlSessionFactory getObject() {
        return this.sqlSessionFactory;
    }
}
```

### 8.2 Spring AOP: ProxyFactoryBean

```
ProxyFactoryBean 用于声明式创建 AOP 代理:
  ├── 配置 interceptorNames (Advice 链)
  ├── 配置 target (目标对象)
  └── getObject() → 创建代理对象 (JDK / CGLIB)
```

### 8.3 JNDI: JndiObjectFactoryBean

```
JndiObjectFactoryBean:
  ├── 配置 jndiName
  └── getObject() → lookup(jndiName) 从 JNDI 获取对象
```

---

## 九、判断题

| 问题 | 答案 |
|------|------|
| `getBean("&myFactory")` 返回什么？ | FactoryBean 自身 |
| `getBean("myFactory")` 返回什么？ | `FactoryBean.getObject()` 的结果 |
| `getBean("&&myFactory")` 返回什么？ | 等价于 `getBean("&myFactory")` |
| getObject() 什么时候被调用？ | 首次 getBean() 或 SmartFactoryBean 提前初始化 |
| FactoryBean 自身是单例吗？ | 是的，按普通 Bean 生命周期管理 |
| 原型 FactoryBean 的 getObject() 会被缓存吗？ | 不会，每次调用都重新创建 |

---

## 十、相关文档

| 文档 | 说明 |
|------|------|
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanFactory、FactoryBean 接口 |
| [Bean 生命周期深度解析](04-bean-lifecycle.md) | FactoryBean 实例的创建流程 |
| [容器启动流程深度解析](03-startup-process.md) | preInstantiateSingletons 中的 FactoryBean 处理 |
| [循环依赖深度解析](05-circular-dependency.md) | FactoryBean 与循环依赖交互 |
