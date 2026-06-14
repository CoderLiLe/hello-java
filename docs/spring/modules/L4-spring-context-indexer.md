# spring-context-indexer 模块功能文档

---

## 一、模块定位

spring-context-indexer 是 Spring 的**编译期候选组件索引器**，13 个 Java 文件，负责：

- **编译期注解处理**：通过 `javax.annotation.processing.Processor` API 在编译期扫描 `@Indexed` 注解
- **生成 `META-INF/spring.components`**：候选组件索引文件，避免运行时类路径扫描
- **加速启动**：替代 `ClassPathBeanDefinitionScanner` 的运行时扫描，直接读取索引获取候选组件

**依赖**：无（独立的注解处理器模块）

---

## 二、源码文件清单

```
spring-context-indexer/src/main/java/org/springframework/context/index/processor/
├── CandidateComponentsIndexer.java      — ★ 注解处理器入口 (javax.annotation.processing.Processor)
├── CandidateComponentsMetadata.java     — 候选组件元数据 (类型 → 构造型枚举)
├── MetadataStore.java                   — 元数据存储 (收集扫描结果)
├── MetadataCollector.java              — 元数据收集器
├── StereotypesProvider.java            — 构造型提供者接口
├── StandardStereotypesProvider.java    — 标准构造型 (@Component/@Service/@Repository/@Controller)
├── IndexedStereotypesProvider.java     — @Indexed 注解构造型
├── PackageInfoStereotypesProvider.java — package-info 级别构造型
├── ItemMetadata.java                   — 项元数据 (type, stereotype, path)
├── PropertiesMarshaller.java           — 属性文件序列化
├── SortedProperties.java               — 排序属性
└── TypeHelper.java                     — 类型辅助工具
```

---

## 三、核心流程

```
编译期注解处理:
  javac → CandidateComponentsIndexer.process(annotations, roundEnv)
    │
    ├── ① 扫描被构造型注解标记的类:
    │     ├── StandardStereotypesProvider:
    │     │     └── 检测 @Component / @Service / @Repository / @Controller
    │     │
    │     ├── IndexedStereotypesProvider:
    │     │     └── 检测 @Indexed (一般在 spring.factories 指定的自定义构造型)
    │     │
    │     └── PackageInfoStereotypesProvider:
    │           └── 检测 package-info.java 上的构造型注解
    │
    ├── ② 收集元数据: MetadataCollector
    │     └── 对于每个匹配的类 → ItemMetadata(type, stereotype)
    │
    ├── ③ 存储元数据: MetadataStore
    │     └── Properties 格式: className = stereotype1,stereotype2
    │
    └── ④ 生成文件: META-INF/spring.components
          └── PropertiesMarshaller.write(metadata)
                └── 输出: com.example.MyService=org.springframework.stereotype.Component
```

---

## 四、生成的索引文件示例

```
# META-INF/spring.components
com.example.service.UserService=org.springframework.stereotype.Service
com.example.repo.UserRepository=org.springframework.stereotype.Repository
com.example.config.AppConfig=org.springframework.stereotype.Component
com.example.controller.UserController=org.springframework.stereotype.Controller
```

---

## 五、使用方式

```
// build.gradle
dependencies {
    annotationProcessor 'org.springframework:spring-context-indexer'
}
```

启用后，`ClassPathBeanDefinitionScanner` 会优先读取 `META-INF/spring.components` 进行候选组件发现，避免类路径扫描。

---

## 六、依赖关系

```
spring-context-indexer (无 api 依赖，独立注解处理器)

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 下游 | [spring-context](L4-spring-context.md) | L4 上下文 | 运行时读取 META-INF/spring.components 索引 |
```
