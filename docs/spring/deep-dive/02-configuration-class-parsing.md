# Spring 配置类解析源码深度解析

> 本文深入分析 Spring @Configuration 配置类的完整解析流程，覆盖 ConfigurationClassPostProcessor 处理链路、@ComponentScan 扫描机制、@Import 导入体系（ImportSelector / ImportBeanDefinitionRegistrar）、@Conditional 条件装配以及 @Bean 方法注册。
> 相关模块文档：[spring-context](../modules/L4-spring-context.md)、[spring-beans](../modules/L2-spring-beans.md)

---

## 一、配置体系概览

```
Spring 的 Bean 定义来源:

  ┌──────────────────────────────────────────────────────┐
  │ XML 配置 (<bean>)                                     │
  │   └── XmlBeanDefinitionReader                         │
  ├──────────────────────────────────────────────────────┤
  │ ★ Java 配置 (@Configuration + @Bean)                  │
  │   └── ConfigurationClassPostProcessor                 │
  ├──────────────────────────────────────────────────────┤
  │ ★ 组件扫描 (@ComponentScan → @Component/@Service/...) │
  │   └── ClassPathBeanDefinitionScanner                 │
  ├──────────────────────────────────────────────────────┤
  │ ★ 导入机制 (@Import)                                  │
  │   └── ConfigurationClassParser                       │
  ├──────────────────────────────────────────────────────┤
  │ 函数式注册 (Supplier)                                 │
  │   └── BeanDefinitionBuilder                          │
  └──────────────────────────────────────────────────────┘
```

---

## 二、ConfigurationClassPostProcessor

### 2.1 核心角色

```java
public class ConfigurationClassPostProcessor 
    implements BeanDefinitionRegistryPostProcessor, PriorityOrdered, ... {
    
    // 优先级: 最早执行
    public int getOrder() { return Ordered.LOWEST_PRECEDENCE;  // Integer.MAX_VALUE }
    
    // Phase 1: 注册新的 BeanDefinition
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) {
        processConfigBeanDefinitions(registry);
    }
    
    // Phase 2: 增强 @Configuration 类
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) {
        enhanceConfigurationClasses(beanFactory);
    }
}
```

### 2.2 processConfigBeanDefinitions() — 主流程

```
processConfigBeanDefinitions(registry):
  │
  ├── ① 收集 @Configuration 类:
  │     └── for beanDef in registry:
  │           if (isConfigurationClass(beanDef)):
  │             configCandidates.add(beanName)
  │           → 检查 annotation metadata: 是否有 @Configuration 注解
  │
  ├── ② 排序: Ordered / @Order 排序配置类
  │
  ├── ③ 创建 ConfigurationClassParser:
  │     └── 注入 PropertySourceRegistry, ImportStack, ConditionEvaluator 等
  │
  ├── ④ ★ parse(configCandidates): 解析每个 @Configuration 类
  │     └── 见 §三 解析详细流程
  │
  ├── ⑤ ★ loadBeanDefinitions(configClasses): 注册 @Bean 方法
  │     └── 见 §五 @Bean 注册流程
  │
  ├── ⑥ 注册 ImportRegistry 中的额外定义
  │
  └── ⑦ 清理: 标记配置类为 "已处理"
```

### 2.3 enhanceConfigurationClasses() — CGLIB 增强

```
enhanceConfigurationClasses(beanFactory):
  │
  └── for each @Configuration(proxyBeanMethods=true) class:
        │
        ├── 创建 ConfigurationClassEnhancer
        │     └── 使用 CGLIB Enhancer 创建子类
        │           └── 设置 CallbackFilter: BeanMethodInterceptor
        │
        ├── 增强后的类标记为: EnhancedConfiguration
        │
        └── 替换 BeanDefinition:
              原 beanClass → 增强后的子类
              

增强效果:
  @Configuration
  public class AppConfig {
      @Bean A a() { return new A(b()); }  // b() 调用被拦截
      @Bean B b() { return new B(); }
  }

拦截行为:
  a() 内调用 b():
    → BeanMethodInterceptor 拦截
    → 检查容器中是否已有 "b" bean
    → 有 → 返回已有单例
    → 无 → 调用父类 b() 方法创建
```

---

## 三、ConfigurationClassParser 解析流程

### 3.1 parse() 入口

```
ConfigurationClassParser.parse(configClasses):
  │
  └── for each configClass:
        └── doProcessConfigurationClass(configClass, sourceClass):
              │
              ├── ① 处理 @Component 嵌套类:
              │     └── 查找 @Component 注解的内部类 → 递归解析
              │
              ├── ② 处理 @PropertySource:
              │     └── processPropertySource(propertySource)
              │           └── 加载 .properties 文件 → environment.propertySources
              │
              ├── ③ 处理 @ComponentScan:
              │     └── 见 §四 组件扫描
              │
              ├── ④ 处理 @Import:
              │     └── 见 §六 @Import 处理
              │
              ├── ⑤ 处理 @ImportResource:
              │     └── 收集 XML 配置路径, 稍后加载
              │
              ├── ⑥ 处理 @Bean 方法:
              │     └── 收集方法元数据 (不立即注册)
              │
              ├── ⑦ 处理接口 default 方法:
              │     └── 查找接口上的 @Bean 方法
              │
              └── ⑧ 处理父类:
                    └── 如果父类不是 JDK 类 → 递归解析
```

### 3.2 循环 Import 检测

```
ConfigurationClassParser 使用 ImportStack 防止循环导入:

ImportStack:
  ├── push(configClass) → 入栈
  ├── pop()             → 出栈
  └── find(configClass) → 检查是否已在栈中

如果 A @Import B, B @Import A:
  push(A) → push(B) → find(A) == true
  → throw BeanDefinitionParsingException("Cycle detected")
```

---

## 四、@ComponentScan 组件扫描

### 4.1 扫描触发

```
processComponentScan(annotationMetadata, beanDef):
  │
  └── ClassPathBeanDefinitionScanner.scan(basePackages):
        │
        ├── ① doScan(basePackages):
        │     │
        │     └── for each basePackage:
        │           ├── findCandidateComponents(basePackage):
        │           │     │
        │           │     ├── 构建搜索模式: classpath*:com/example/**/*.class
        │           │     │
        │           │     ├── PathMatchingResourcePatternResolver 扫描 .class 文件
        │           │     │
        │           │     └── 对每个 .class 资源:
        │           │           ├── SimpleMetadataReader.read(Resource)
        │           │           │     └── ASM ClassReader → AnnotationMetadataReadingVisitor
        │           │           │           └── 只读注解元数据, 不加载类!
        │           │           │
        │           │           └── isCandidateComponent(metadataReader):
        │           │                 ├── 是否 annotated with @Component?
        │           │                 ├── 是否 @Conditional 条件满足?
        │           │                 └── 排除类型过滤 (excludeFilters)
        │           │
        │           └── 生成 ScannedGenericBeanDefinition
        │                 └── 设置: beanClass, scope, lazy, autowireCandidate 等
        │
        └── ② 注册到 BeanDefinitionRegistry
```

### 4.2 扫描过滤器

```
@ComponentScan 的 Include/Exclude 过滤:

FilterType.ANNOTATION:     @Component, @Service, @Repository, @Controller
FilterType.ASSIGNABLE_TYPE: 按父类/接口过滤
FilterType.ASPECTJ:         AspectJ 类型表达式
FilterType.REGEX:           正则表达式匹配类名
FilterType.CUSTOM:          自定义 TypeFilter 实现

excludeFilters:  排除哪些类
includeFilters:  包含哪些类 (默认: @Component + JSR-250/Jakarta @ManagedBean)
```

### 4.3 扫描索引加速

```
spring-context-indexer (编译期索引):
  │
  └── 编译期生成 META-INF/spring.components:
        com.example.MyService=org.springframework.stereotype.Component
        com.example.MyRepository=org.springframework.stereotype.Repository
        
运行时:
  ClassPathBeanDefinitionScanner:
    ├── 检查是否存在 CandidateComponentsIndex
    ├── 存在 → 从索引直接获取候选类 (跳过 .class 扫描)
    └── 不存在 → 正常扫描 classpath
```

---

## 五、@Bean 方法注册

### 5.1 方法收集

```
processBeanMethods(beanMethodMetadata):
  │
  └── 对每个 @Bean 方法:
        ├── 收集方法元数据:
        │     ├── methodName: @Bean 方法名
        │     ├── returnType: 返回类型
        │     ├── annotationAttributes: @Bean 注解属性
        │     └── isOverloaded: 是否重载方法
        │
        └── 加入 configClass.beanMethods
```

### 5.2 loadBeanDefinitionsForBeanMethod()

```
ConfigurationClassBeanDefinitionReader.loadBeanDefinitionsForBeanMethod(beanMethod):
  │
  ├── ① 创建 ConfigurationClassBeanDefinition:
  │     ├── factoryBeanName = configClass.getBeanName()
  │     ├── factoryMethodName = methodName
  │     └── factoryMethodMetadata = beanMethod 元数据
  │
  ├── ② 解析 @Bean 属性:
  │     ├── initMethod: @Bean(initMethod = "init")
  │     ├── destroyMethod: @Bean(destroyMethod = "close")
  │     ├── name / value: @Bean(name = "customName")
  │     │     └── 支持数组: @Bean(name = {"a", "b"}) → 创建别名
  │     └── autowireCandidate: @Bean(autowireCandidate = false)
  │
  ├── ③ 解析附加注解:
  │     ├── @Lazy → mbd.setLazyInit(true)
  │     ├── @Primary → mbd.setPrimary(true)
  │     ├── @DependsOn → mbd.setDependsOn(...)
  │     ├── @Role → mbd.setRole(...)
  │     ├── @Description → mbd.setDescription(...)
  │     └── @Scope → mbd.setScope(...)
  │
  └── ④ 注册: registry.registerBeanDefinition(beanName, beanDef)
```

---

## 六、@Import 导入体系

### 6.1 三类 Import 处理

```
@Import(SomeClass.class)

processImports(configClass, imports):
  │
  ├── 类型 1: ImportSelector (含 DeferredImportSelector)
  │     │
  │     ├── 实例化 ImportSelector
  │     ├── 调用 AnnotationMetadata 相关的 Aware 回调
  │     ├── selectImports(annotationMetadata) → String[] (class names)
  │     │
  │     ├── DeferredImportSelector:
  │     │     └── 延迟到所有配置类解析完成后才调用 selectImports()
  │     │           └── Spring Boot: @EnableAutoConfiguration → AutoConfigurationImportSelector
  │     │
  │     └── 递归处理返回的类名
  │
  ├── 类型 2: ImportBeanDefinitionRegistrar
  │     │
  │     ├── 保存在 configClass.importBeanDefinitionRegistrars
  │     └── 在 loadBeanDefinitions 阶段调用:
  │           registrar.registerBeanDefinitions(metadata, registry)
  │           └── AspectJAutoProxyRegistrar (注册 AnnotationAwareAspectJAutoProxyCreator)
  │           └── TransactionManagementConfigurationSelector → ProxyTransactionManagementConfig
  │
  └── 类型 3: 普通类 (被当作 @Configuration 类处理)
        └── asSourceClass(class) → doProcessConfigurationClass()
```

### 6.2 DeferredImportSelector 处理

```
DeferredImportSelector 两阶段:

Phase 1 (解析期间):
  configClass.addDeferredImportSelector(deferredImportSelector)
  → 放入 deferredImportSelectors 队列, 暂不执行

Phase 2 (所有配置类解析完):
  processDeferredImportSelectors():
    │
    ├── 对每个 deferredImportSelector:
    │     ├── deferredImportSelector.selectImports(metadata)
    │     └── 递归处理返回的类名
    │
    └── 完成后重新解析 (因为可能产生新的配置类)

典型使用者:
  @EnableAutoConfiguration → AutoConfigurationImportSelector:
    └── selectImports():
          ├── 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
          ├── 应用 @ConditionalOnClass / @ConditionalOnBean 条件
          └── 返回符合条件的自动配置类名
```

---

## 七、@Conditional 条件装配

### 7.1 ConditionEvaluator

```
ConditionEvaluator.shouldSkip(metadata, phase):
  │
  ├── 获取 @Conditional 注解:
  │     └── metadata.getAllAnnotationAttributes(Conditional.class.getName())
  │
  ├── 对每个 Condition 实现类:
  │     ├── condition.matches(conditionContext, annotatedTypeMetadata)
  │     │
  │     ├── matches = true → 继续检查下一个
  │     └── matches = false → return true (跳过此配置类/Bean)
  │
  └── 两个评定阶段:
        ├── PARSE_CONFIGURATION: 配置类解析阶段
        │     └── 如果不满足条件 → 跳过整个配置类, 不处理其 @Bean 方法
        └── REGISTER_BEAN: Bean 注册阶段
              └── 如果不满足条件 → 只跳过特定 @Bean 方法
```

### 7.2 内置条件示例

```
@Profile("dev"):
  → ProfileCondition:
      └── environment.acceptsProfiles("dev")

@ConditionalOnClass(name = "com.example.SomeClass"):
  → OnClassCondition:
      └── ClassUtils.isPresent("com.example.SomeClass", classLoader)

@ConditionalOnMissingBean(DataSource.class):
  → OnBeanCondition:
      └── beanFactory.getBeanNamesForType(DataSource.class).length == 0
```

---

## 八、配置类解析完整时序

```
refresh()
  → invokeBeanFactoryPostProcessors()
    → ConfigurationClassPostProcessor.postProcessBeanDefinitionRegistry(registry)
      │
      ├── ① 收集 @Configuration 候选 (通过 checkConfigurationClassCandidate)
      │
      ├── ② 按 @Order 排序
      │
      ├── ③ ConfigurationClassParser.parse(configCandidates):
      │     │
      │     └── for each @Configuration class:
      │           ├── 解析 @PropertySource  → 加载配置文件
      │           ├── 解析 @ComponentScan  → 扫描 .class, 注册新 BeanDefinition
      │           ├── 解析 @Import         → 递归加载 (ImportSelector / ImportBeanDefinitionRegistrar)
      │           ├── 解析 @ImportResource → 收集 XML 路径
      │           └── 解析 @Bean 方法       → 收集方法元数据, 待注册
      │
      ├── ④ 处理 DeferredImportSelector (所有解析完成后)
      │
      ├── ⑤ ConfigurationClassBeanDefinitionReader.loadBeanDefinitions(configClasses):
      │     └── 将步骤③收集的 @Bean 方法注册为 BeanDefinition
      │           └── factoryBeanName + factoryMethodName
      │
      └── ⑥ 清理标记
```

---

## 九、关键扩展点

| 扩展点 | 接口 | 用途 |
|--------|------|------|
| 条件装配 | `@Conditional` + `Condition` | 按条件决定是否注册 Bean |
| 导入选择 | `ImportSelector` | 动态决定导入哪些配置类 |
| 延迟导入 | `DeferredImportSelector` | 所有配置类解析完后再导入 |
| Bean 注册 | `ImportBeanDefinitionRegistrar` | 直接编程式注册 BeanDefinition |
| 类型过滤 | `TypeFilter` | 自定义扫描过滤规则 |
| Bean 命名 | `BeanNameGenerator` | 自定义 Bean 命名策略 |
| Scope 解析 | `ScopeMetadataResolver` | 自定义 Scope 解析 |

---

## 十、相关文档

| 文档 | 说明 |
|------|------|
| [spring-context 模块文档](../modules/L4-spring-context.md) | ConfigurationClassPostProcessor 位置 |
| [启动流程深度解析](03-startup-process.md) | refresh() 完整流程 |
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanDefinition 注册体系 |
| [Bean 生命周期深度解析](04-bean-lifecycle.md) | @Bean 方法工厂方法实例化 |
