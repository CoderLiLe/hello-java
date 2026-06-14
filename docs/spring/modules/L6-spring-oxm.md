# spring-oxm 模块功能文档

---

## 一、模块定位

spring-oxm 是 Spring 的 **Object/XML 映射（OXM）抽象模块**，27 个 Java 文件，负责：

- **OXM 抽象接口**：Marshaller（对象 → XML）、Unmarshaller（XML → 对象）
- **JAXB 支持**：Jaxb2Marshaller（Jakarta XML Binding）
- **XStream 支持**：XStreamMarshaller
- **MIME 扩展**：MimeMarshaller / MimeUnmarshaller（带附件的 XML 编组）
- **通用编组**：GenericMarshaller / GenericUnmarshaller（泛型感知）

**依赖**：`spring-beans`、`spring-core`

---

## 二、源码文件清单

```
spring-oxm/src/main/java/org/springframework/oxm/
├── Marshaller.java                        — 对象 → XML 接口
├── Unmarshaller.java                      — XML → 对象接口
├── GenericMarshaller.java                 — 泛型编组器 (可处理泛型)
├── GenericUnmarshaller.java               — 泛型解编器
├── MarshallingException.java             — 编组异常基类
├── MarshallingFailureException.java      — 编组失败异常
├── UnmarshallingFailureException.java    — 解编失败异常
├── ValidationFailureException.java       — 校验失败异常
├── XmlMappingException.java              — XML 映射异常基类
├── UncategorizedMappingException.java    — 未分类映射异常
│
├── jaxb/
│   ├── Jaxb2Marshaller.java              — ★ JAXB 编组器 (支持 Jakarta XML Binding)
│   └── ClassPathJaxb2TypeScanner.java    — 类路径 JAXB 类型扫描
│
├── xstream/
│   ├── XStreamMarshaller.java            — XStream 编组器
│   └── CatchAllConverter.java            — 全部捕获转换器
│
├── config/
│   ├── OxmNamespaceHandler.java          — XML 命名空间处理器
│   └── Jaxb2MarshallerBeanDefinitionParser.java — JAXB Bean 定义解析
│
├── mime/
│   ├── MimeMarshaller.java               — MIME 编组器接口
│   ├── MimeUnmarshaller.java             — MIME 解编器接口
│   └── MimeContainer.java                — MIME 容器
│
└── support/
    ├── AbstractMarshaller.java           — 编组器抽象基类
    ├── MarshallingSource.java            — 编组 Source (javax.xml.transform)
    └── SaxResourceUtils.java             — SAX 资源工具
```

---

## 三、核心接口

```
Marshaller                                — 编组器接口
  ├── supports(Class) → boolean           — 是否支持该类型
  └── marshal(Object, Result)              — 对象 → XML (写入 Result)

Unmarshaller                              — 解编器接口
  ├── supports(Class) → boolean           — 是否支持该类型
  └── unmarshal(Source) → Object           — XML → 对象 (从 Source 读取)

GenericMarshaller<T>                      — 泛型编组器 (Spring 7.0+)
  └── marshal(T, Result)

GenericUnmarshaller<T>                    — 泛型解编器 (Spring 7.0+)
  └── unmarshal(Source) → T

MimeMarshaller                            — 带附件的编组器
  └── marshal(Object, Result, MimeContainer)

MimeUnmarshaller                          — 带附件的解编器
  └── unmarshal(Source, MimeContainer) → Object
```

---

## 四、Jaxb2Marshaller 核心流程

```
Jaxb2Marshaller marshaller = new Jaxb2Marshaller();
marshaller.setPackagesToScan("com.example.dto");
marshaller.afterPropertiesSet();  // 初始化 JAXBContext

marshaller.marshal(obj, result);
  │
  ├── 从缓存获取 JAXBContext
  ├── 创建 Marshaller: jaxbContext.createMarshaller()
  ├── 设置属性: jaxb.properties (格式化输出、编码等)
  ├── 注册 ValidationEventHandler
  └── marshaller.marshal(obj, result) → XML

marshaller.unmarshal(source);
  │
  ├── 获取 JAXBContext
  ├── 创建 Unmarshaller: jaxbContext.createUnmarshaller()
  ├── 设置 ValidationEventHandler
  └── unmarshaller.unmarshal(source) → Object
```

---

## 五、依赖关系

```
spring-oxm
  ├── api: spring-beans
  ├── api: spring-core
  ├── optional: jakarta.xml.bind:jakarta.xml.bind-api  (JAXB)
  ├── optional: com.thoughtworks.xstream:xstream        (XStream)
  ├── optional: jakarta.activation:jakarta.activation-api (MIME)
  └── optional: jakarta.mail:jakarta.mail-api           (MIME)

---

## 六、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-beans](L2-spring-beans.md) | L2 Bean容器 | BeanFactory |
| 下游 | [spring-web](L7-spring-web.md) | L7 Web | HTTP 消息转换（XML） |
| 下游 | [spring-jms](L6-spring-jms.md) | L6 消息 | JMS 消息转换（XML） |
```
