# Spring 循环依赖三级缓存源码深度解析

> 本文深入分析 Spring IoC 容器如何通过**三级缓存**解决单例 Bean 的循环依赖问题，以及 AOP 场景下三级缓存的特殊处理。
> 相关模块文档：[spring-beans](../modules/L2-spring-beans.md)、[spring-aop](../modules/L3-spring-aop.md)

---

## 一、问题的本质

### 1.1 什么是循环依赖

```
@Component
class A {
    @Autowired
    B b;
}

@Component
class B {
    @Autowired
    A a;
}
```

A 依赖 B，B 又依赖 A。Spring 在创建 A 时需要注入 B，而创建 B 时又需要注入 A——形成闭环。

### 1.2 为什么会有问题

Java 中创建 Bean 的常规流程是：

```
1. new A()            → 得到原始对象 a
2. a.b = getBean(B)   → 创建 B
  2.1 new B()         → 得到原始对象 b
  2.2 b.a = getBean(A)→ 递归创建 A → 死循环！
```

如果严格按照"先完整创建，再注入"的顺序，循环依赖会导致 StackOverflow。

### 1.3 Spring 的解决思路

**核心思想**：将"实例化"和"初始化"分离。实例化后立即暴露一个"早期引用"，让其他 Bean 可以注入这个尚未完成初始化的半成品，等所有依赖就绪后再完成初始化。

---

## 二、三级缓存数据结构

```java
// DefaultSingletonBeanRegistry.java

/** 一级缓存：完全初始化完成的单例 */
private final Map<String, Object> singletonObjects = new ConcurrentHashMap<>(256);

/** 二级缓存：提前暴露但尚未完成初始化的 Bean */
private final Map<String, Object> earlySingletonObjects = new ConcurrentHashMap<>(16);

/** 三级缓存：生成 Bean 的 ObjectFactory（Lambda 表达式） */
private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);

/** 正在创建中的 Bean 集合（用于循环依赖检测） */
private final Set<String> singletonsCurrentlyInCreation = 
    Collections.newSetFromMap(new ConcurrentHashMap<>(16));
```

### 缓存定位

| 缓存 | 存放内容 | 何时放入 | 何时移除 |
|------|---------|---------|---------|
| **一级** `singletonObjects` | 完全初始化好的 Bean（可能是代理） | `addSingleton()` 在 Bean 完全就绪后 | 容器销毁 |
| **二级** `earlySingletonObjects` | 提前暴露的早期 Bean 引用 | 从三级缓存升级而来 | Bean 完全初始化后移除 |
| **三级** `singletonFactories` | `ObjectFactory`（Lambda，按需执行） | `addSingletonFactory()` 在实例化后立即放入 | 被调用后升级到二级缓存 |

---

## 三、核心流程：getSingleton() 查找链

```java
protected Object getSingleton(String beanName, boolean allowEarlyReference) {
    // ① 查找一级缓存：完全初始化好的 Bean
    Object singletonObject = this.singletonObjects.get(beanName);
    if (singletonObject == null && isSingletonCurrentlyInCreation(beanName)) {
        // ② 查找二级缓存：早期暴露的 Bean
        singletonObject = this.earlySingletonObjects.get(beanName);
        if (singletonObject == null && allowEarlyReference) {
            synchronized (this.singletonObjects) {
                singletonObject = this.singletonObjects.get(beanName);
                if (singletonObject == null) {
                    singletonObject = this.earlySingletonObjects.get(beanName);
                    if (singletonObject == null) {
                        // ③ 查找三级缓存：ObjectFactory
                        ObjectFactory<?> singletonFactory = 
                            this.singletonFactories.get(beanName);
                        if (singletonFactory != null) {
                            // ★ 执行 Lambda 表达式，生成 Bean
                            singletonObject = singletonFactory.getObject();
                            // 升级到二级缓存
                            this.earlySingletonObjects.put(beanName, singletonObject);
                            // 从三级缓存移除
                            this.singletonFactories.remove(beanName);
                        }
                    }
                }
            }
        }
    }
    return singletonObject;
}
```

**关键设计**：
- 三级缓存的 Lambda **只在发生循环依赖时才执行**
- 执行后立即从三级升级到二级（保证同一个 Lambda 只执行一次）
- `synchronized (this.singletonObjects)` 保证线程安全

---

## 四、循环依赖解决全流程推演

以 A ↔ B 为例：

```
T0: getBean("a")
  → singletonObjects.get("a") == null  ✗
  → singletonsCurrentlyInCreation.add("a")
  → createBeanInstance("a") → new A()  — 得到原始对象 a
  → addSingletonFactory("a", () → getEarlyBeanReference("a", mbd, a))
    → singletonFactories.put("a", Lambda)
  → populateBean(a):
      → 发现 @Autowired B b
      → getBean("b")
        │
        │ T1: getBean("b")
        │   → singletonObjects.get("b") == null  ✗
        │   → singletonsCurrentlyInCreation.add("b")
        │   → createBeanInstance("b") → new B() — 得到原始对象 b
        │   → addSingletonFactory("b", () → getEarlyBeanReference(...))
        │   → populateBean(b):
        │       → 发现 @Autowired A a
        │       → getBean("a")
        │         │
        │         │ T2: getSingleton("a")
        │         │   → singletonObjects.get("a") == null  ✗
        │         │   → isSingletonCurrentlyInCreation("a") == true ✓
        │         │   → earlySingletonObjects.get("a") == null ✗
        │         │   → singletonFactories.get("a") == Lambda ✓
        │         │   → 执行 Lambda: getEarlyBeanReference("a", mbd, a)
        │         │     ├── 遍历 SmartInstantiationAwareBeanPostProcessor
        │         │     └── AOP → 创建早期代理对象 aProxy
        │         │   → earlySingletonObjects.put("a", aProxy)  ← 升级二级
        │         │   → singletonFactories.remove("a")           ← 移除三级
        │         │   → return aProxy  ← B 获得 A 的早期代理
        │         │
        │       ← b.a = aProxy  — 注入完成
        │   → initializeBean(b)
        │   → singletonObjects.put("b", b)  — B 进入一级缓存
        │   → singletonsCurrentlyInCreation.remove("b")
        │   → return b
        │
      ← a.b = b  — 注入完成
  → initializeBean(a):
      → postProcessAfterInitialization(a) 
        → AOP: a 需要代理吗？已经创建过代理了？
          → 检查 earlyProxyReferences: 如果 a 的早期代理已存在
            → 不再创建新代理，直接返回早期代理 aProxy
  → singletonObjects.put("a", aProxy)  — A 的代理进入一级缓存
  → singletonsCurrentlyInCreation.remove("a")
  → return aProxy
```

**最终结果**：
- A 的代理对象 `aProxy` 在一级缓存
- B 注入的是 `aProxy`（A 的代理）
- A 注入的是 `b`（B 的原始对象，B 无 AOP）
- 两者持有的引用指向同一个最终对象

---

## 五、AOP 与循环依赖的特殊处理

### 5.1 为什么 AOP 需要特殊处理

正常情况下，AOP 代理在 `postProcessAfterInitialization()` 阶段（初始化完成后）创建。但如果 Bean A 有循环依赖，此时 B 已经在属性填充阶段拿到了 A 的引用（原始对象）。

**问题**：如果等初始化完成后再创建 AOP 代理，B 已经持有原始对象 A 而非代理对象 AProxy，这会破坏 AOP 语义。

**解决方案**：`getEarlyBeanReference()` 在属性填充**之前**就创建好代理。

### 5.2 核心代码

```java
// AbstractAutoProxyCreator.java
@Override
public Object getEarlyBeanReference(Object bean, String beanName) {
    Object cacheKey = getCacheKey(bean.getClass(), beanName);
    // 将 beanName 标记为"已创建早期引用"
    this.earlyProxyReferences.put(cacheKey, beanName);
    // 创建代理（如果此 Bean 需要 AOP）
    return wrapIfNecessary(bean, beanName, cacheKey);
}

@Override
public Object postProcessAfterInitialization(@Nullable Object bean, String beanName) {
    if (bean != null) {
        Object cacheKey = getCacheKey(bean.getClass(), beanName);
        // 检查是否已在 getEarlyBeanReference() 中创建过代理
        if (this.earlyProxyReferences.remove(cacheKey) != beanName) {
            // 未创建过 → 现在创建
            return wrapIfNecessary(bean, beanName, cacheKey);
        }
    }
    // 已创建过 → 直接返回（不重复代理）
    return bean;
}
```

**关键判断**：`earlyProxyReferences` 集合记录了哪些 Bean 在早期引用阶段已经创建了代理。`postProcessAfterInitialization()` 检查此集合，避免重复创建代理。

### 5.3 有无 AOP 的流程对比

```
无 AOP（普通 Bean）:
  ① 实例化 → ② 三级缓存(存原始对象工厂) → ③ 属性填充 → ④ 初始化 → ⑤ 一级缓存

有 AOP（无循环依赖）:
  ① 实例化 → ② 三级缓存(存原始对象工厂) → ③ 属性填充 → ④ 初始化 
    → ⑤ postProcessAfterInitialization 创建代理 → ⑥ 一级缓存(存代理)

有 AOP（有循环依赖）:
  ① 实例化 → ② 三级缓存(存 Lambda: getEarlyBeanReference) 
    → B 请求 A → 触发 Lambda → ③ ★ 提前创建代理 ★ → 升级二级缓存(存代理)
    → ④ 属性填充 → ⑤ 初始化 
    → ⑥ postProcessAfterInitialization: 检测到 earlyProxyReferences → 跳过
    → ⑦ 一级缓存(存代理)
```

---

## 六、为什么三个缓存？两个不够吗？

### 6.1 只需要两个缓存的情形（无 AOP 循环依赖）

如果永远没有 AOP + 循环依赖的组合，一级缓存 + 三级缓存就够了：
- 一级缓存存放最终 Bean
- 三级缓存存放 `ObjectFactory`，发生循环依赖时执行生成原始对象

### 6.2 为什么需要二级缓存

```java
// 从三级缓存取出的关键代码
singletonObject = singletonFactory.getObject();           // 执行 Lambda
this.earlySingletonObjects.put(beanName, singletonObject); // 放入二级
this.singletonFactories.remove(beanName);                  // 移除三级
```

**原因**：`ObjectFactory.getObject()` 可能包含复杂逻辑（如 `getEarlyBeanReference()` 中的 AOP 代理创建），应该只执行一次。三级缓存升级到二级缓存后：

1. 后续请求直接从二级缓存取，避免重复执行 Lambda
2. 保证所有注入方获取到的是**同一个**早期对象

### 6.3 三个缓存的完整职责

```
请求 Bean → 
  ┌─ 一级缓存 hit → 返回最终 Bean ✓
  │
  ├─ 一级 miss → 检查正在创建中 → 二级 hit → 返回早期 Bean ✓
  │
  ├─ 二级 miss → 三级 hit → 执行 Lambda → 升级二级 → 返回 ✓
  │
  └─ 三级 miss → 去创建
       ├─ 实例化 → 放入三级
       ├─ 属性填充（可能递归触发循环依赖）
       ├─ 初始化 → 移除三级 + 二级 → 放入一级
       └─ 返回
```

---

## 七、不能解决的情况

Spring 的三级缓存机制**只能**解决**单例** Bean 的 **setter/属性** 注入循环依赖。以下情况无法解决：

| 场景 | 能否解决 | 原因 |
|------|---------|------|
| 构造器注入循环依赖 | ✗ | 构造器调用在实例化阶段，此时三级缓存尚未建立 |
| Prototype scope 循环依赖 | ✗ | Prototype Bean 不进入缓存 |
| `@Lazy` + 构造器注入 | ✓ | `@Lazy` 使注入的是代理对象，打破直接依赖链 |
| `@DependsOn` 循环声明 | ✗ | `@DependsOn` 在实例化前检查，直接抛异常 |

### 7.1 构造器循环依赖失败的原因

```
@Component
class A {
    A(@Autowired B b) { ... }  // 构造器注入
}
@Component
class B {
    B(@Autowired A a) { ... }  // 构造器注入
}

T0: getBean("a")
  → 调用 new A(b) ← 需要 B → getBean("b")
    → 调用 new B(a) ← 需要 A → getBean("a")
      → singletonFactories 中还没有 A 的 Lambda! 
        (A 还没完成实例化，addSingletonFactory 尚未调用)
      → 抛出 BeanCurrentlyInCreationException
```

### 7.2 解决方案

#### 方案一：@Lazy 为构造方法参数生成代理

```java
@Component
class A {
    private B b;

    public A(@Lazy B b) {
        this.b = b;  // b 为代理对象
    }
}

@Component
class B {
    private A a;

    public B(A a) {
        this.a = a;
    }
}
```

`@Lazy` 使 Spring 注入一个代理对象，直到真正调用代理方法时才去容器中获取实际的 B，从而打破初始化时的直接依赖。

#### 方案二：ObjectProvider 延迟依赖对象的创建

```java
@Component
class A {
    private ObjectProvider<B> b;

    public A(ObjectProvider<B> b) {
        this.b = b;  // 不会触发 B 的创建
    }

    @PostConstruct
    public void init() {
        // 需要时再获取
    }
}

@Component
class B {
    private A a;

    public B(A a) {
        this.a = a;
    }
}
```

ObjectProvider 是 ObjectFactory 的子接口，支持延迟检索和流式操作。

#### 方案三：@Scope 产生代理

```java
@Component
class A {
    private B b;

    public A(B b) {
        this.b = b;
    }
}

@Scope(proxyMode = ScopedProxyMode.TARGET_CLASS)
@Component
class B {
    private A a;

    public B(A a) {
        this.a = a;
    }
}
```

通过 `@Scope(proxyMode = ScopedProxyMode.TARGET_CLASS)` 使 B 被注入为代理对象。

#### 方案四：Provider 接口

```java
@Component
class A {
    private Provider<B> b;

    public A(Provider<B> b) {
        this.b = b;
    }

    @PostConstruct
    public void init() {
        // 通过 b.get() 获取实际的 B
    }
}

@Component
class B {
    private A a;

    public B(A a) {
        this.a = a;
    }
}
```

Provider 接口来自 `javax.inject` 包，原理上与 ObjectProvider 类似，需要额外引入依赖：

```xml
<dependency>
    <groupId>javax.inject</groupId>
    <artifactId>javax.inject</artifactId>
    <version>1</version>
</dependency>
```

---

## 八、相关文档

| 文档 | 说明 |
|------|------|
| [Bean 生命周期深度解析](04-bean-lifecycle.md) | doCreateBean 完整流程 |
| [AOP 实现深度解析](12-aop-implementation.md) | 代理创建与 earlyProxyReferences |
| [依赖注入深度解析](06-dependency-injection.md) | @Autowired 注入链路 |
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanFactory、singleton 管理 |
