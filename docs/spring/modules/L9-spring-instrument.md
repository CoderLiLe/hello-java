# spring-instrument 模块功能文档

---

## 一、模块定位

spring-instrument 是 Spring 的 **Java Instrumentation Agent**，2 个 Java 文件，负责：

- **保存 Instrumentation 实例**：在 JVM 启动时通过 `-javaagent` 参数加载，将 `java.lang.instrument.Instrumentation` 保存为静态字段
- **供其他模块使用**：`ReflectiveLoadTimeWeaver` 等通过 `InstrumentationSavingAgent.getInstrumentation()` 获取 Instrumentation 实例，实现类加载时织入（Load-Time Weaving）

**依赖**：无（独立 Java Agent JAR）

---

## 二、源码文件清单

```
spring-instrument/src/main/java/org/springframework/instrument/
├── InstrumentationSavingAgent.java  — Java Agent 入口 (Premain-Class)
└── package-info.java
```

---

## 三、核心流程

```
JVM 启动: java -javaagent:spring-instrument.jar ...
  │
  └── InstrumentationSavingAgent.premain(agentArgs, instrumentation)
        │
        └── 保存 Instrumentation 实例到静态字段
              └── InstrumentationSavingAgent.instrumentation = instrumentation

后续使用:
  ReflectiveLoadTimeWeaver
    └── InstrumentationSavingAgent.getInstrumentation()
          └── 返回之前保存的 Instrumentation 实例
                └── instrumentation.addTransformer(classFileTransformer)
                      └── AspectJ 织入器在此注册
```

---

## 四、MANIFEST.MF 配置

```
Premain-Class: org.springframework.instrument.InstrumentationSavingAgent
Can-Redefine-Classes: true
Can-Retransform-Classes: true
```

---

## 五、依赖关系

```
spring-instrument (无 api 依赖，独立 Java Agent JAR)

---

## 六、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 下游 | [spring-context](L4-spring-context.md) | L4 上下文 | ReflectiveLoadTimeWeaver 通过此获取 Instrumentation |
| 同级 | [spring-aspects](L9-spring-aspects.md) | L9 辅助 | AspectJ 加载时织入依赖此 Agent |
```
