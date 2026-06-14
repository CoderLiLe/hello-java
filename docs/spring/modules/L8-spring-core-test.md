# spring-core-test 模块功能文档

---

## 一、模块定位

spring-core-test 是 Spring 的 **核心测试工具模块**，~30 个 Java 文件，负责：

- **RuntimeHints 测试 Agent**：通过 Java Agent 录制运行时的反射/资源/序列化调用，用于验证 AOT RuntimeHints 的完整性
- **测试编译器**：`TestCompiler` 用于在单元测试中动态编译 Java 源代码
- **RuntimeHints 断言**：`RuntimeHintsInvocationsAssert` 用于验证录制的调用是否被 RuntimeHints 覆盖

**依赖**：`spring-core`

---

## 二、源码文件清单

```
spring-core-test/src/main/java/org/springframework/
│
├── aot/agent/                                    # RuntimeHints 录制 Agent
│   ├── RuntimeHintsAgent.java                    — ★ Java Agent 入口
│   ├── InvocationsRecorderClassTransformer.java  — 类转换器 (ASM)
│   ├── InvocationsRecorderClassVisitor.java      — 类访问器 (ASM ClassVisitor)
│   ├── InstrumentedMethod.java                   — 被织入的方法标记
│   ├── InstrumentedBridgeMethods.java            — 桥接方法织入
│   ├── MethodReference.java                      — 方法引用
│   ├── RecordedInvocation.java                   — 录制的调用
│   ├── RecordedInvocationsListener.java          — 录制监听器 SPI
│   ├── RecordedInvocationsPublisher.java         — 录制发布器
│   └── HintType.java                             — 提示类型枚举
│
├── aot/test/agent/                               # RuntimeHints 测试工具
│   ├── RuntimeHintsRecorder.java                 — ★ RuntimeHints 录制器 (JUnit Extension)
│   ├── RuntimeHintsInvocations.java              — 录制的调用集合
│   ├── RuntimeHintsInvocationsAssert.java        — 录制调用断言
│   └── EnabledIfRuntimeHintsAgent.java           — 条件执行注解
│
├── aot/test/generate/                            # AOT 生成测试支持
│   ├── TestGenerationContext.java                — 测试生成上下文
│   └── CompilerFiles.java                        — 编译文件工具
│
└── core/test/                                    # 核心测试工具
    ├── tools/                                     — 动态编译工具
    │   ├── TestCompiler.java                      — ★ 测试编译器 (javac API)
    │   ├── SourceFile / SourceFiles               — 源码文件表示
    │   ├── ResourceFile / ResourceFiles           — 资源文件表示
    │   ├── ClassFile / ClassFiles                 — 编译后的类文件
    │   ├── DynamicFile / DynamicFiles             — 动态文件集合
    │   ├── DynamicClassFileObject                 — 动态类文件对象
    │   ├── DynamicJavaFileObject                  — 动态 Java 文件对象
    │   ├── DynamicResourceFileObject              — 动态资源文件对象
    │   ├── DynamicJavaFileManager                 — 动态 Java 文件管理器
    │   ├── DynamicClassLoader                     — 动态类加载器
    │   ├── Compiled                               — 编译结果
    │   ├── CompileWithForkedClassLoader           — 分叉类加载器注解
    │   ├── CompileWithForkedClassLoaderExtension  — 分叉类加载器扩展
    │   ├── SourceFileAssert / ResourceFileAssert / DynamicFileAssert — 文件断言
    │   └── WritableContent                        — 可写内容接口
    │
    └── io/support/
        └── MockSpringFactoriesLoader.java         — Mock spring.factories 加载器
```

---

## 三、核心流程

### 3.1 RuntimeHints 录制与验证

```
测试阶段:
  @RegisterExtension
  RuntimeHintsRecorder recorder = new RuntimeHintsRecorder();

  // 执行被测代码 (Spring AOT 激活时)
  // RuntimeHintsAgent 通过 ASM 织入所有反射/资源/序列化调用点
  // 调用被录制到 recorder 中

  // 验证
  RuntimeHintsInvocations recorded = recorder.getRecordedInvocations();
  RuntimeHints hints = new RuntimeHints();
  // ... 注册预期 hints ...
  RuntimeHintsInvocationsAssert.assertThat(recorded).match(hints);

实现原理:
  -javaagent:spring-core-test.jar → RuntimeHintsAgent.premain()
    │
    └── 注册 ClassFileTransformer: InvocationsRecorderClassTransformer
          │
          └── 对每个加载的类:
                ├── ASM ClassVisitor 扫描方法
                ├── 检测反射调用: Method.invoke(), Constructor.newInstance(), Field.set() 等
                ├── 检测资源访问: ClassLoader.getResource(), Class.getResource() 等
                └── 检测序列化: ObjectOutputStream.writeObject() 等
                      │
                      └── 织入录制逻辑: RecordedInvocationsPublisher.notify()
                            └── 通知所有 RecordedInvocationsListener
                                  └── RuntimeHintsRecorder 收集调用
```

### 3.2 TestCompiler 动态编译

```
TestCompiler compiler = TestCompiler.forSystem();
Compiled compiled = compiler.withSources(
    SourceFile.of("""
        package com.example;
        public class Hello {
            public String say() { return "Hello"; }
        }
        """)
).compile(Compiled::getClassLoader);

Class<?> helloClass = compiled.getClassLoader().loadClass("com.example.Hello");

内部流程:
  │
  ├── 创建 JavaCompiler (javax.tools.JavaCompiler)
  ├── DynamicJavaFileManager: 管理动态生成的文件
  ├── 编译: compiler.getTask(writer, fileManager, null, options, null, sourceFiles).call()
  └── 返回 Compiled: 包含 ClassLoader + ClassFiles
```

---

## 四、依赖关系

```
spring-core-test
  ├── api: spring-core
  ├── optional: org.junit.jupiter:junit-jupiter-api  (JUnit Extension)
  ├── optional: org.assertj:assertj-core              (AssertJ 断言)
  └── optional: org.ow2.asm:asm                        (ASM 字节码)

---

## 五、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-core](L1-spring-core.md) | L1 核心 | RuntimeHints 定义 |
| 同级 | [spring-test](L8-spring-test.md) | L8 测试 | TestContext 框架、MockMvc |
```
