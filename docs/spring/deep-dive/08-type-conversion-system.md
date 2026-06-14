# Spring 类型转换体系源码深度解析

> 本文深入分析 Spring 类型转换的三层体系：JDK PropertyEditor、Spring Converter/ConverterFactory/GenericConverter、TypeConverter 统一门面，以及它们在 BeanWrapper 属性绑定中的协同工作方式。
> 相关模块文档：[spring-core](../modules/L1-spring-core.md)、[spring-beans](../modules/L2-spring-beans.md)

---

## 一、三层转换体系概览

```
                     ┌─────────────────────────────┐
                     │      TypeConverter           │  ← ★ Spring 统一门面
                     │   (SimpleTypeConverter)      │
                     └──────────┬──────────────────┘
                                │ 内部持
                    ┌───────────┴───────────┐
                    │                       │
        ┌───────────▼──────────┐  ┌────────▼─────────────────┐
        │  PropertyEditor      │  │  ConversionService       │
        │  (JDK 标准)          │  │  (Spring 自定义)          │
        │                     │  │                          │
        │  String ↔ Object    │  │  Converter<S,T>          │
        │  setAsText / getAsText│  │  ConverterFactory        │
        │                     │  │  GenericConverter         │
        └─────────────────────┘  └──────────────────────────┘

分工:
  PropertyEditor:    主要处理 String → Object (文本配置 → Bean 属性)
  ConversionService: 通用类型转换 (任意类型 → 任意类型)
  TypeConverter:     统一门面, 优先 PropertyEditor, 回退 ConversionService
```

---

## 二、PropertyEditor (JDK 标准)

### 2.1 核心接口

```java
// java.beans.PropertyEditor
public interface PropertyEditor {
    void setAsText(String text);         // ★ String → Object
    String getAsText();                  // Object → String
    void setValue(Object value);
    Object getValue();
    String getJavaInitializationString();
    String[] getTags();                  // 可选值列表 (如 true/false)
    // ... 监听器方法
}

// Spring 推荐继承 PropertyEditorSupport 而非直接实现 PropertyEditor
public class PropertyEditorSupport implements PropertyEditor {
    private Object value;
    @Override
    public void setAsText(String text) { setValue(text); } // 默认直接赋值
    @Override
    public String getAsText() { return this.value != null ? this.value.toString() : null; }
}
```

### 2.2 自定义 PropertyEditor

```java
// 将 String "1:张三" 转换为 User{id=1, name="张三"}
public class StringToUserPropertyEditor extends PropertyEditorSupport {
    @Override
    public void setAsText(String text) {
        String[] parts = text.split(":");
        User user = new User();
        user.setId(Long.parseLong(parts[0]));
        user.setName(parts[1]);
        setValue(user);
    }
}
```

### 2.3 注册到 Spring

**方式一：CustomEditorConfigurer（传统 XML/Java Config）**

```java
@Bean
public CustomEditorConfigurer customEditorConfigurer() {
    CustomEditorConfigurer configurer = new CustomEditorConfigurer();
    Map<Class<?>, Class<? extends PropertyEditor>> editors = new HashMap<>();
    editors.put(User.class, StringToUserPropertyEditor.class);
    configurer.setCustomEditors(editors);
    return configurer;
}
```

**方式二：PropertyEditorRegistrar（编程式）**

```java
// 在 BeanFactoryPostProcessor 中注册
beanFactory.addPropertyEditorRegistrar(registry -> {
    registry.registerCustomEditor(User.class, new StringToUserPropertyEditor());
});
```

### 2.4 Spring 内置 PropertyEditor

| PropertyEditor | 功能 |
|---------|------|
| `CustomDateEditor` | String ↔ java.util.Date (需指定格式) |
| `CustomBooleanEditor` | "true"/"false"/"on"/"off" → Boolean |
| `CustomNumberEditor` | String → Integer/Long/Double 等 |
| `CharsetEditor` | String → java.nio.charset.Charset |
| `ClassEditor` | 全限定类名 String → Class |
| `CurrencyEditor` | String → java.util.Currency |
| `FileEditor` | String → File (ResourceEditor 替代方案) |
| `InputStreamEditor` | String → InputStream (ResourceEditor 链) |
| `LocaleEditor` | "zh_CN" → Locale |
| `PatternEditor` | String → java.util.regex.Pattern |
| `ResourceEditor` | "classpath:xxx" → Resource |
| `URLEditor` | String → URL |
| `UUIDEditor` | String → UUID |
| `TimeZoneEditor` | String → TimeZone |
| `ZoneIdEditor` | String → ZoneId |

---

## 三、Spring Converter 体系

### 3.1 三种转换器接口

```java
// ① 简单转换器: S → T
@FunctionalInterface
public interface Converter<S, T> {
    @Nullable
    T convert(S source);
}

// ② 工厂转换器: 同一转换逻辑适用于多个子类型
public interface ConverterFactory<S, R> {
    <T extends R> Converter<S, T> getConverter(Class<T> targetType);
}

// ③ 通用转换器: 支持多对多类型转换 + 条件匹配
public interface GenericConverter {
    // 返回支持的源→目标类型组合
    Set<ConvertiblePair> getConvertibleTypes();

    // ★ 核心转换方法，含字段级上下文
    @Nullable
    Object convert(@Nullable Object source, TypeDescriptor sourceType, TypeDescriptor targetType);
}

// GenericConverter 的可选扩展接口
public interface ConditionalGenericConverter extends GenericConverter, ConditionalConverter {
    // matches(sourceType, targetType) 决定是否匹配
}
```

### 3.2 三种接口对比

| 接口 | 灵活性 | 使用场景 |
|------|--------|---------|
| `Converter<S,T>` | 低（固定类型对） | 简单类型转换，如 String→Integer |
| `ConverterFactory` | 中（同族类型） | String→Enum、String→Number |
| `GenericConverter` | 高（多类型对+上下文） | 集合/数组转换、Object→String |

### 3.3 内置 Converter 示例

```
StringToBooleanConverter:      "true" → Boolean.TRUE
StringToNumberConverterFactory: String → Integer/Long/Double/...
StringToEnumConverterFactory:  "RED" → Color.RED
StringToCharsetConverter:      "UTF-8" → Charset.forName("UTF-8")
StringToUUIDConverter:         "..." → UUID.fromString(...)
StringToCurrencyConverter:     "CNY" → Currency.getInstance(...)
StringToLocaleConverter:       "zh_CN" → Locale(...)
StringToTimeZoneConverter:     "GMT+8" → TimeZone.getTimeZone(...)
StringToPropertiesConverter:   "a=1\nb=2" → Properties

ObjectToStringConverter:       Object → obj.toString()  (兜底)

ArrayToCollectionConverter:    T[] → List<T>
CollectionToArrayConverter:    List<T> → T[]
MapToMapConverter:             Map<K,V> → Map<K,V> (跨类型)
ObjectToOptionalConverter:     T → Optional<T>
StreamConverter:               Collection<T> → Stream<T>
IdToEntityConverter:           id → JPA Entity (@Converter 风格)
```

---

## 四、ConversionService

### 4.1 核心接口

```java
public interface ConversionService {
    boolean canConvert(@Nullable Class<?> sourceType, Class<?> targetType);
    boolean canConvert(@Nullable TypeDescriptor sourceType, TypeDescriptor targetType);
    <T> T convert(@Nullable Object source, Class<T> targetType);
    Object convert(@Nullable Object source, TypeDescriptor sourceType, TypeDescriptor targetType);
}
```

### 4.2 DefaultConversionService

```java
// 万能转换服务: 聚合了所有内置 Converter
DefaultConversionService conversionService = new DefaultConversionService();

// 自定义注册
conversionService.addConverter(new StringToUserConverter());

// 使用
User user = conversionService.convert("1:张三", User.class);
```

**内部注册的内置 Converter（共 70+ 个）**在 `DefaultConversionService.addDefaultConverters()` 中添加。

### 4.3 Spring 容器中的 ConversionService

```
AbstractApplicationContext.refresh()
  → finishBeanFactoryInitialization():
      if (beanFactory.containsBean("conversionService")) {
          beanFactory.setConversionService(conversionService);
      }

自定义注册:
  @Bean
  public ConversionService conversionService() {
      DefaultConversionService service = new DefaultConversionService();
      service.addConverter(new StringToUserConverter());
      return service;
  }
```

`FormattingConversionService` 扩展 `DefaultConversionService`，增加了 `Formatter` 注册支持（用于 `@DateTimeFormat`、`@NumberFormat` 等）。

---

## 五、TypeConverter — 统一门面

### 5.1 核心接口

```java
public interface TypeConverter {
    <T> T convertIfNecessary(@Nullable Object value, @Nullable Class<T> requiredType);
    <T> T convertIfNecessary(@Nullable Object value, @Nullable Class<T> requiredType, 
                             @Nullable MethodParameter methodParam);
    <T> T convertIfNecessary(@Nullable Object value, @Nullable Class<T> requiredType, 
                             @Nullable Field field);
}
```

### 5.2 TypeConverterSupport (桥接 PropertyEditor + ConversionService)

```java
public abstract class TypeConverterSupport extends PropertyEditorRegistrySupport implements TypeConverter {

    @Nullable
    TypeConverterDelegate typeConverterDelegate;  // 委托对象

    @Override
    public <T> T convertIfNecessary(Object value, Class<T> requiredType, Field field) {
        return doConvert(value, requiredType, TypeDescriptor.valueOf(requiredType), 
                         new TypeDescriptor(field));
    }

    private <T> T doConvert(Object value, Class<T> requiredType,
                            TypeDescriptor sourceType, TypeDescriptor targetType) {
        // ① 先尝试 PropertyEditor (registeredCustomEditors)
        // ② 再尝试 ConversionService
        // ③ 最后使用 Spring 默认转换逻辑
        return this.typeConverterDelegate.convertIfNecessary(...);
    }
}
```

### 5.3 BeanWrapperImpl (实际使用)

```java
// BeanWrapper 继承层次:
PropertyEditorRegistry (接口)
  → PropertyEditorRegistrySupport (基类: 管理 PropertyEditor)
    → TypeConverterSupport (基类: 加入 ConversionService)
      → AbstractNestablePropertyAccessor (嵌套属性访问)
        → AbstractPropertyAccessor
          → ConfigurablePropertyAccessor
            → BeanWrapper
              → BeanWrapperImpl  ← ★ 最终实现
```

`BeanWrapperImpl` 同时实现了 `PropertyAccessor` 和 `TypeConverter`：
- `PropertyAccessor`：`getPropertyValue("name")` / `setPropertyValue("name", "张三")`
- `TypeConverter`：`convertIfNecessary("123", Integer.class)`

### 5.4 类型转换查找顺序

```
convertIfNecessary(value, requiredType):
  │
  ├── ① 检查是否已有默认编辑器 (registeredDefaultEditors)
  │     └── 如 Charset.class → CharsetEditor
  │
  ├── ② 检查是否已注册自定义编辑器 (customEditors)
  │     └── 如 User.class → StringToUserPropertyEditor
  │
  ├── ③ 检查目标类型是否有通用编辑器
  │     └── PropertyEditorManager.findEditor(requiredType)
  │
  ├── ④ ★ 如果 BeanWrapper 关联了 ConversionService:
  │     └── conversionService.convert(value, sourceType, targetType)
  │
  ├── ⑤ 尝试数组/集合转换
  │
  ├── ⑥ 检查 value 是否可强制转型 (requiredType.isInstance(value))
  │
  └── ⑦ 最终: String → 使用 valueOf() / 构造器反射
```

---

## 六、格式化集成（FormattingConversionService）

### 6.1 Formatter 接口

```java
// 位于 spring-context 的 org.springframework.format
public interface Formatter<T> extends Printer<T>, Parser<T> { }

public interface Printer<T> {
    String print(T object, Locale locale);  // T → String
}
public interface Parser<T> {
    T parse(String text, Locale locale);    // String → T
}
```

### 6.2 注解驱动格式化

```
@DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate date;
@NumberFormat(pattern = "#,###.##")     BigDecimal amount;

底层:
  FormattingConversionService 内置:
    ├── DateTimeFormatterRegistrar  → 注册 JSR-310 / Joda / Date Formatters
    ├── NumberFormatAnnotationFormatterFactory  → 注册 Number Formatter
    └── 根据注解属性创建对应的 Formatter
```

### 6.3 注册 Formatter

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addFormatters(FormatterRegistry registry) {
        registry.addFormatter(new DateFormatter("yyyy-MM-dd"));
    }
}
```

---

## 七、三者关系总结

```
┌─────────────────────────────────────────────────────────────┐
│                     TypeConverter                          │
│                   (Spring 统一门面)                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            PropertyEditor (JDK)                       │  │
│  │  主要: String → Object                               │  │
│  │  优先级: ★ 最高 (先检查)                              │  │
│  │  工作方式: setAsText(String) → setValue(result)      │  │
│  │  Spring 内置: 20+ 种 (Date, Boolean, Number, Charset) │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓ 未命中时                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          ConversionService (Spring)                   │  │
│  │  任意类型 → 任意类型                                  │  │
│  │  优先级: 次优先                                       │  │
│  │  组件: Converter + ConverterFactory + GenericConverter│  │
│  │  扩展: FormattingConversionService (Formatter)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

使用场景:
  属性绑定 (@Value, XML <property>) → TypeConverter
  参数解析 (@RequestParam, @PathVariable) → ConversionService (WebDataBinder)
  消息转换 (@RequestBody/@ResponseBody) → HttpMessageConverter (不经过 TypeConverter)
```

---

## 八、ConditionalGenericConverter 示例

```java
// 仅在 String → User 的转换时生效
public class StringToUserConverter implements ConditionalGenericConverter {
    @Override
    public boolean matches(TypeDescriptor sourceType, TypeDescriptor targetType) {
        return sourceType.getType() == String.class 
            && targetType.getType() == User.class;
    }
    @Override
    public Set<ConvertiblePair> getConvertibleTypes() {
        return Collections.singleton(new ConvertiblePair(String.class, User.class));
    }
    @Override
    public Object convert(Object source, TypeDescriptor sourceType, TypeDescriptor targetType) {
        String[] parts = ((String) source).split(":");
        User user = new User();
        user.setId(Long.parseLong(parts[0]));
        user.setName(parts[1]);
        return user;
    }
}
```

---

## 九、相关文档

| 文档 | 说明 |
|------|------|
| [spring-core 模块文档](../modules/L1-spring-core.md) | Converter、ConversionService 完整参考 |
| [spring-beans 模块文档](../modules/L2-spring-beans.md) | BeanWrapper、PropertyEditor 绑定 |
| [依赖注入深度解析](06-dependency-injection.md) | @Value 注入时的类型转换 |
