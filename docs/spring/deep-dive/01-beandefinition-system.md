# Spring BeanDefinition 体系源码深度解析

> 本文深入分析 Spring BeanDefinition 从注册、合并到使用的完整生命周期，覆盖 BeanDefinition 接口继承层次、XML 与注解两种注册方式的全链路、RootBeanDefinition 合并机制以及 BeanDefinitionRegistry 核心实现。
> 相关模块文档：[spring-beans](../modules/L2-spring-beans.md)、[spring-context](../modules/L4-spring-context.md)

---

## 一、BeanDefinition 是什么

BeanDefinition 是 Spring IoC 容器中描述一个 Bean 的**元数据蓝图**。它承载了"如何创建、配置、管理某个 Bean"的全部信息，是连接配置源与运行时 Bean 实例的桥梁。

```
[配置源: XML / @Bean / @Component / API]
        │
        ▼  解析
┌──────────────────────────┐
│    BeanDefinition         │  ← 元数据模型
│  - beanClassName          │
│  - scope                  │
│  - lazyInit               │
│  - propertyValues         │
│  - constructorArgValues   │
│  - initMethodName         │
│  - destroyMethodName      │
│  - ...                    │
└──────────┬───────────────┘
           │
           ▼  注册
┌──────────────────────────┐
│   BeanDefinitionRegistry  │
│   (DefaultListableBF)     │
│   - beanDefinitionMap     │
│   - beanDefinitionNames   │
└──────────┬───────────────┘
           │
           ▼  合并 + 使用
        Bean 实例
```

---

## 二、接口继承层次

```
AttributeAccessor              — 属性访问 (getAttribute / setAttribute)
  │
  └── BeanMetadataElement      — 获取元数据来源 (getSource)
        │
        └── BeanDefinition     — ★ 核心接口, 描述 Bean 的元数据
              │
              └── AbstractBeanDefinition  — 抽象基类, 提供大部分默认实现
                    │
                    ├── RootBeanDefinition       — ★ 合并后的最终定义
                    ├── ChildBeanDefinition      — (已废弃, 仅用于 XML 父子 bean)
                    └── GenericBeanDefinition    — ★ 标准通用定义 (现代推荐)
```

### 各实现类的用途

| 类型 | 用途 | parent 支持 |
|------|------|------------|
| `GenericBeanDefinition` | 标准通用定义，XML `<bean>` 和注解扫描均生成此类型 | ✅ 通过 setParentName |
| `RootBeanDefinition` | 合并后的最终定义，所有 Bean 在实例化前都转为此类型 | ❌ 不支持 parent |
| `ChildBeanDefinition` | 已废弃，仅在解析 XML 父子 `<bean>` 时使用 | ✅ |
| `AnnotatedGenericBeanDefinition` | 注解方式的 @Configuration 类 | ❌ |
| `ScannedGenericBeanDefinition` | @ComponentScan 扫描到的类 | ❌ |
| `ConfigurationClassBeanDefinition` | @Bean 方法生成的 Bean 定义 | ❌ |

---

## 三、BeanDefinition 核心属性

```java
public interface BeanDefinition extends AttributeAccessor, BeanMetadataElement {
    String SCOPE_SINGLETON = "singleton";
    String SCOPE_PROTOTYPE = "prototype";
    int ROLE_APPLICATION = 0;   // 用户定义的 Bean
    int ROLE_SUPPORT = 1;        // 支持性 Bean (如 ConfigurationClassPostProcessor)
    int ROLE_INFRASTRUCTURE = 2; // 基础设施 Bean

    void setBeanClassName(String beanClassName);
    void setScope(String scope);
    void setLazyInit(boolean lazyInit);
    void setDependsOn(String... dependsOn);
    void setAutowireCandidate(boolean autowireCandidate);
    void setPrimary(boolean primary);
    void setFactoryBeanName(String factoryBeanName);
    void setFactoryMethodName(String factoryMethodName);
    ConstructorArgumentValues getConstructorArgumentValues();
    MutablePropertyValues getPropertyValues();
    void setInitMethodName(String initMethodName);
    void setDestroyMethodName(String destroyMethodName);
    void setRole(int role);
    void setDescription(String description);
    ResolvableType getResolvableType();
    boolean isSingleton();
    boolean isPrototype();
    boolean isAbstract();
    String getParentName();
}
```

---

## 四、XML 方式注册 BeanDefinition 全链路

### 4.1 入口

```
ClassPathXmlApplicationContext 构造函数
  → refresh()
    → obtainFreshBeanFactory()
      → refreshBeanFactory()
        → createBeanFactory() → 创建 DefaultListableBeanFactory
        → ★ loadBeanDefinitions(beanFactory):
              └── XmlBeanDefinitionReader.loadBeanDefinitions(configLocations)
```

### 4.2 XML 解析链

```
XmlBeanDefinitionReader.loadBeanDefinitions(configLocations):
  │
  └── doLoadBeanDefinitions():
        │
        ├── ① doLoadDocument(): XML → DOM Document
        │
        └── ② registerBeanDefinitions(doc, resource):
              └── DefaultBeanDefinitionDocumentReader.registerBeanDefinitions(doc, readerContext):
                    │
                    └── doRegisterBeanDefinitions(root):
                          │
                          ├── 处理 <beans> profile 属性
                          │
                          └── parseBeanDefinitions(root, delegate):
                                │
                                ├── 默认命名空间 (<bean>, <alias>, <import>):
                                │     └── processBeanDefinition(ele, delegate):
                                │           │
                                │           ├── parseBeanDefinitionElement():
                                │           │     ├── 解析 id / name / class / scope
                                │           │     ├── 解析 lazy-init / depends-on / autowire
                                │           │     ├── 解析 init-method / destroy-method
                                │           │     ├── 解析 <property> → propertyValues
                                │           │     ├── 解析 <constructor-arg> → constructorArgs
                                │           │     └── ★ 创建 GenericBeanDefinition
                                │           │
                                │           └── ★ registerBeanDefinition():
                                │                 ├── beanDefinitionMap.put(beanName, beanDef)
                                │                 └── beanDefinitionNames.add(beanName)
                                │
                                └── 自定义命名空间 (<tx:>, <aop:>, <mvc:>):
                                      └── NamespaceHandler.parse() → 委托给各自解析器
```

---

## 五、注解方式注册 BeanDefinition 全链路

### 5.1 @Component / @Service / @Repository / @Controller

```
AnnotationConfigApplicationContext 构造函数
  │
  ├── ① 创建 AnnotatedBeanDefinitionReader:
  │     └── AnnotationConfigUtils.registerAnnotationConfigProcessors():
  │           └── 注册 ConfigurationClassPostProcessor 等基础设施 Bean
  │
  ├── ② 创建 ClassPathBeanDefinitionScanner
  │
  ├── ③ register(annotatedClasses): 注册配置类本身
  │     └── reader.register(componentClass):
  │           └── doRegisterBean():
  │                 ├── 创建 AnnotatedGenericBeanDefinition
  │                 ├── 解析 @Scope / @Lazy / @Primary / @DependsOn / @Role / @Description
  │                 └── registry.registerBeanDefinition(beanName, beanDef)
  │
  └── ④ ★ refresh() → invokeBeanFactoryPostProcessors():
        └── ConfigurationClassPostProcessor.postProcessBeanDefinitionRegistry():
              └── processConfigBeanDefinitions(registry):
                    │
                    ├── ConfigurationClassParser.parse(configCandidates):
                    │     │
                    │     ├── 解析 @ComponentScan:
                    │     │     └── ClassPathBeanDefinitionScanner.doScan():
                    │     │           ├── findCandidateComponents(): 扫描 .class 文件
                    │     │           ├── ASM MetadataReader 读取注解 (不加载类)
                    │     │           ├── 生成 ScannedGenericBeanDefinition
                    │     │           └── registry.registerBeanDefinition()
                    │     │
                    │     └── 解析 @Bean 方法 → 收集元数据 (稍后注册)
                    │
                    └── ConfigurationClassBeanDefinitionReader.loadBeanDefinitions():
                          └── 将 @Bean 方法注册为 ConfigurationClassBeanDefinition
                                ├── factoryBeanName = @Configuration 类 beanName
                                ├── factoryMethodName = @Bean 方法名
                                └── registry.registerBeanDefinition()
```

### 5.2 两种注解方式对比

| | @Component / @ComponentScan | @Bean 方法 |
|------|------|------|
| BeanDefinition 类型 | `ScannedGenericBeanDefinition` | `ConfigurationClassBeanDefinition` |
| 实例化方式 | 反射构造器 | 工厂方法调用 |
| class 来源 | ASM 读取 .class 文件 | @Bean 方法返回值类型 |
| 注册时机 | @ComponentScan 扫描时 | ConfigurationClassBeanDefinitionReader 处理时 |

---

## 六、BeanDefinitionRegistry 核心实现

### 6.1 DefaultListableBeanFactory 中的存储结构

```java
public class DefaultListableBeanFactory extends ... implements BeanDefinitionRegistry {

    // ★ 核心存储: beanName → BeanDefinition
    private final Map<String, BeanDefinition> beanDefinitionMap = new ConcurrentHashMap<>(256);

    // ★ 按注册顺序记录 beanName (保证 Bean 创建顺序)
    private volatile List<String> beanDefinitionNames = new ArrayList<>(256);

    // 手动注册的单例名称 (registerSingleton)
    private volatile Set<String> manualSingletonNames = new LinkedHashSet<>(16);

    // 冻结后的 beanDefinitionNames 快照
    private volatile String[] frozenBeanDefinitionNames;
}
```

### 6.2 registerBeanDefinition() 源码

```java
@Override
public void registerBeanDefinition(String beanName, BeanDefinition beanDefinition) {
    // ① 校验 BeanDefinition
    if (beanDefinition instanceof AbstractBeanDefinition abd) {
        abd.validate();  // 校验 methodOverrides 与 factory method 不冲突
    }

    // ② 检查是否已存在同名定义
    BeanDefinition existingDefinition = this.beanDefinitionMap.get(beanName);
    if (existingDefinition != null) {
        // 不允许覆盖? → throw BeanDefinitionOverrideException
        if (!isAllowBeanDefinitionOverriding()) {
            throw new BeanDefinitionOverrideException(...);
        }
        // 允许覆盖, 记录日志
        this.beanDefinitionMap.put(beanName, beanDefinition);
    } else {
        // ③ 首次注册
        if (hasBeanCreationStarted()) {
            // 创建已开始 → 需要同步
            synchronized (this.beanDefinitionMap) {
                this.beanDefinitionMap.put(beanName, beanDefinition);
                List<String> updatedDefs = new ArrayList<>(this.beanDefinitionNames.size() + 1);
                updatedDefs.addAll(this.beanDefinitionNames);
                updatedDefs.add(beanName);
                this.beanDefinitionNames = updatedDefs;
                removeManualSingletonName(beanName);
            }
        } else {
            // ★ 创建未开始 → 直接注册 (常见路径)
            this.beanDefinitionMap.put(beanName, beanDefinition);
            this.beanDefinitionNames.add(beanName);
            removeManualSingletonName(beanName);
        }
        this.frozenBeanDefinitionNames = null;  // 清除冻结快照
    }

    // ④ 重置与此 beanName 相关的缓存
    if (existingDefinition != null || containsSingleton(beanName)) {
        resetBeanDefinition(beanName);  // 清除 mergedBeanDefinitions 缓存
    }
}
```

---

## 七、BeanDefinition 合并流程

### 7.1 为什么需要合并

在 XML 配置中，`<bean>` 可以指定 `parent` 属性继承父 Bean 的定义。即使没有显式 parent，GenericBeanDefinition 也需要转为 RootBeanDefinition 才能用于实例化。

```
合并前的定义链:
  GenericBeanDefinition(parent=baseConfig)
    └── GenericBeanDefinition(id=baseConfig) (parent=null)

合并后:
  RootBeanDefinition (所有属性已展开, parent=null)
```

### 7.2 getMergedBeanDefinition() 源码

```java
// AbstractBeanFactory
protected RootBeanDefinition getMergedBeanDefinition(String beanName, BeanDefinition bd,
        BeanDefinition containingBd) throws BeanDefinitionStoreException {

    synchronized (this.mergedBeanDefinitions) {
        RootBeanDefinition mbd = null;
        RootBeanDefinition previous = null;

        // ① 检查是否已缓存
        if (containingBd == null) {
            mbd = this.mergedBeanDefinitions.get(beanName);
        }

        if (mbd == null || mbd.stale) {
            previous = mbd;
            if (bd.getParentName() == null) {
                // ② 无父定义 → 直接复制为 RootBeanDefinition
                if (bd instanceof RootBeanDefinition rootBeanDef) {
                    mbd = rootBeanDef.cloneBeanDefinition();
                } else {
                    // GenericBeanDefinition → RootBeanDefinition
                    mbd = new RootBeanDefinition(bd);
                }
            } else {
                // ③ ★ 有父定义 → 递归合并
                BeanDefinition pbd;
                String parentBeanName = transformedBeanName(bd.getParentName());

                if (!beanName.equals(parentBeanName)) {
                    // 递归获取父 Bean 的合并定义
                    pbd = getMergedBeanDefinition(parentBeanName);
                }

                // 以父定义为模板创建 RootBeanDefinition
                mbd = new RootBeanDefinition(pbd);

                // ★ 用子定义的属性覆盖父定义
                mbd.overrideFrom(bd);
            }

            // ④ 设置默认 Scope
            if (!StringUtils.hasLength(mbd.getScope())) {
                mbd.setScope(SCOPE_SINGLETON);
            }

            // ⑤ 缓存（非内部 Bean）
            if (containingBd == null && isCacheBeanMetadata()) {
                this.mergedBeanDefinitions.put(beanName, mbd);
            }
        }
        return mbd;
    }
}
```

### 7.3 overrideFrom() — 子覆盖父

```java
// RootBeanDefinition.overrideFrom(BeanDefinition other)
public void overrideFrom(BeanDefinition other) {
    if (StringUtils.hasLength(other.getBeanClassName())) {
        setBeanClassName(other.getBeanClassName());
    }
    if (StringUtils.hasLength(other.getScope())) {
        setScope(other.getScope());
    }
    if (other.isLazyInit() != isLazyInit()) {
        setLazyInit(other.isLazyInit());
    }
    // ... 逐一覆盖: dependsOn, autowireCandidate, primary, 
    //     factoryBeanName, factoryMethodName, initMethodName, destroyMethodName ...
    // PropertyValues 也会合并
    getPropertyValues().addPropertyValues(other.getPropertyValues());
    // ConstructorArgumentValues 也会合并
    getConstructorArgumentValues().addArgumentValues(other.getConstructorArgumentValues());
}
```

### 7.4 合并时机

```
合并发生在 doGetBean() 中, 实例化之前:

doGetBean(beanName):
  ├── getSingleton(beanName) → 缓存未命中
  │
  ├── ★ getMergedLocalBeanDefinition(beanName):
  │     └── getMergedBeanDefinition(beanName, bd)
  │           └── 合并 + 缓存到 mergedBeanDefinitions
  │
  ├── createBean(beanName, mbd, args):
  │     └── doCreateBean():
  │           ├── createBeanInstance()  ← 使用 RootBeanDefinition
  │           ├── populateBean()
  │           └── initializeBean()
  │
  └── 返回 bean
```

---

## 八、BeanDefinition 完整生命周期

```
┌─────────────────────────────────────────────────────┐
│  ① 配置阶段                                          │
│     XML / @ComponentScan / @Bean / registerBean()   │
│                                                     │
│  ② 解析与创建 BeanDefinition                          │
│     XmlBeanDefinitionReader                          │
│     ClassPathBeanDefinitionScanner                   │
│     ConfigurationClassParser                         │
│     → GenericBeanDefinition / ScannedGenericBDef     │
│                                                     │
│  ③ 注册到 Registry                                  │
│     registry.registerBeanDefinition(beanName, bd)    │
│     → beanDefinitionMap.put()                        │
│     → beanDefinitionNames.add()                      │
│                                                     │
│  ④ BFPP 修改 (可选)                                  │
│     BeanFactoryPostProcessor /                       │
│     BeanDefinitionRegistryPostProcessor              │
│     → 可修改已注册的 BeanDefinition                    │
│                                                     │
│  ⑤ 合并 (getMergedBeanDefinition)                    │
│     GenericBeanDefinition → RootBeanDefinition       │
│     父定义合并 + 属性覆盖                              │
│     → 缓存在 mergedBeanDefinitions                   │
│                                                     │
│  ⑥ 实例化                                            │
│     使用 RootBeanDefinition 中的元数据                  │
│     → createBeanInstance()                           │
│                                                     │
│  ⑦ 属性填充 + 初始化                                   │
│     → populateBean() + initializeBean()               │
│                                                     │
│  ⑧ Bean 就绪 → 一级缓存 singletonObjects              │
└─────────────────────────────────────────────────────┘
```

---

## 九、关键扩展点

| 扩展点 | 接口 | 用途 |
|--------|------|------|
| 自定义解析 | `NamespaceHandler` | 自定义 XML 命名空间解析 |
| Bean 注册 | `ImportBeanDefinitionRegistrar` | 编程式注册 BeanDefinition |
| 修改定义 | `BeanFactoryPostProcessor` | 修改已注册的 BeanDefinition |
| 新增定义 | `BeanDefinitionRegistryPostProcessor` | 注册新的 BeanDefinition |
| 自定义扫描过滤 | `TypeFilter` | 控制 @ComponentScan 扫描范围 |
| Bean 命名 | `BeanNameGenerator` | 自定义 Bean 命名策略 |

---

## 十、相关文档

| 文档 | 说明 |
|------|------|
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanDefinition 接口与注册体系 |
| [配置类解析](02-configuration-class-parsing.md) | @Configuration 解析与 @Bean 注册 |
| [Bean 生命周期](04-bean-lifecycle.md) | Bean 实例化时如何使用 BeanDefinition |
| [容器启动流程](03-startup-process.md) | refresh() 中 BeanDefinition 加载时机 |
