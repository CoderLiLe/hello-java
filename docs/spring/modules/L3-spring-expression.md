# spring-expression 模块功能文档

---

## 一、模块定位

spring-expression 是 Spring 的 **表达式语言（SpEL）模块**，123 个 Java 文件，负责：

- **表达式解析**：将字符串表达式解析为可执行的 AST（抽象语法树）
- **表达式求值**：在给定的 EvaluationContext 中对表达式求值，支持读/写属性
- **丰富的语法支持**：字面量、属性访问、方法调用、运算符、集合投影/选择、变量、函数、Bean 引用、三元表达式、Elvis 运算符、模板表达式等
- **编译优化**：运行时将热点表达式编译为 JVM 字节码（ASM）
- **可扩展解析/求值策略**：PropertyAccessor、MethodResolver、ConstructorResolver、TypeConverter 等均可自定义

**依赖**：`spring-core`

---

## 二、模块全景图

```
spring-expression (123 files)
│
├── org.springframework.expression/                 # 核心接口 (25 files)
│   ├── ExpressionParser                            — 表达式解析器接口
│   ├── Expression                                  — 已解析表达式接口 (getValue / setValue / getValueType)
│   ├── EvaluationContext                           — 求值上下文 (变量、函数、类型定位器、PropertyAccessor 等)
│   ├── ParserContext                               — 解析上下文 (模板前缀/后缀)
│   ├── PropertyAccessor                            — 属性读写策略接口
│   ├── IndexAccessor                               — 索引访问策略接口
│   ├── MethodResolver                              — 方法解析策略接口
│   ├── ConstructorResolver                         — 构造器解析策略接口
│   ├── BeanResolver                                — Bean 名字解析策略接口
│   ├── TypeLocator                                 — 类型定位策略接口
│   ├── TypeConverter                               — 类型转换策略接口
│   ├── TypeComparator                              — 类型比较策略接口
│   ├── OperatorOverloader                          — 运算符重载策略接口
│   ├── TypedValue                                  — 带类型的值封装
│   ├── Operation                                   — 运算符枚举 (ADD, SUB, DIV, etc.)
│   └── EvaluationException / ParseException         — 异常体系
│
├── org.springframework.expression.common/          # 通用实现 (6 files)
│   ├── TemplateAwareExpressionParser               — 模板解析抽象基类 (#{...} 格式)
│   ├── CompositeStringExpression                   — 混合模板表达式 (文本 + #{})
│   ├── LiteralExpression                           — 纯文本字面量
│   └── TemplateParserContext                        — 默认模板解析上下文
│
├── org.springframework.expression.spel/            # SpEL 核心 (13 files)
│   ├── SpelExpression                              — SpEL 表达式实现
│   ├── SpelNode                                    — AST 节点接口
│   ├── ExpressionState                             — 求值状态 (管理上下文、变量、操作数栈)
│   ├── SpelParserConfiguration                     — 解析配置 (编译模式、自动增长等)
│   ├── CodeFlow                                    — 编译模式下的字节码生成上下文
│   └── SpelEvaluationException / SpelMessage       — SpEL 异常与消息枚举
│
├── org.springframework.expression.spel.standard/   # 标准实现 (8 files)
│   ├── SpelExpressionParser                        — ★ 用户入口: SpEL 解析器
│   ├── InternalSpelExpressionParser                 — ★ 内部解析器 (1061 行，递归下降解析)
│   ├── SpelCompiler                                — JIT 编译器 (ASM)
│   ├── SpelCompilerMode                            — 编译模式 (OFF / IMMEDIATE / MIXED)
│   └── Tokenizer / Token / TokenKind                — 词法分析 (分词)
│
├── org.springframework.expression.spel.ast/         # AST 节点 (53 files)
│   │
│   ├── 节点基类:
│   │   └── SpelNodeImpl                            — 所有 AST 节点抽象基类
│   │
│   ├── 字面量:
│   │   ├── BooleanLiteral / IntLiteral / LongLiteral / FloatLiteral
│   │   ├── RealLiteral / StringLiteral / NullLiteral
│   │   └── Literal                                   — 字面量基类
│   │
│   ├── 标识符与访问:
│   │   ├── Identifier                                — 简单标识符 (变量/Bean)
│   │   ├── QualifiedIdentifier                       — 限定标识符 (a.b.c)
│   │   ├── PropertyOrFieldReference                  — 属性/字段引用 (a.b)
│   │   └── VariableReference                         — 变量引用 (#var)
│   │
│   ├── 引用:
│   │   ├── BeanReference                             — Bean 引用 (@beanName)
│   │   ├── MethodReference                           — 方法调用
│   │   ├── ConstructorReference                      — 构造器调用
│   │   ├── FunctionReference                         — 函数调用 (#fn())
│   │   └── TypeReference                             — 类型引用 (T(package.Class))
│   │
│   ├── 集合:
│   │   ├── InlineList                                — 内联 List ({1,2,3})
│   │   ├── InlineMap                                 — 内联 Map ({key:value})
│   │   ├── Indexer                                   — 索引访问 ([0], ['key'])
│   │   ├── Projection                                — 集合投影 (.![expr])
│   │   └── Selection                                 — 集合选择 (.?[expr])
│   │
│   ├── 运算符 (35+ 种):
│   │   ├── OpPlus / OpMinus / OpMultiply / OpDivide / OpModulus / OpPower
│   │   ├── OpEQ / OpNE / OpLT / OpLE / OpGT / OpGE
│   │   ├── OpAnd / OpOr / OperatorNot
│   │   ├── OpInc / OpDec                               — 自增/自减 (++ / --)
│   │   ├── OperatorBetween / OperatorInstanceof / OperatorMatches
│   │   ├── Assign                                      — 赋值 (=)
│   │   └── CompoundExpression                          — 复合表达式 (a; b)
│   │
│   ├── 条件:
│   │   ├── Ternary                                     — 三元表达式 (?:)
│   │   └── Elvis                                       — Elvis (?:)
│   │
│   └── 其他:
│       ├── TypeCode                                    — 基本类型代码
│       └── ValueRef                                    — 可写值引用
│
└── org.springframework.expression.spel.support/     # 标准策略实现 (18 files)
    ├── StandardEvaluationContext                     — ★ 标准求值上下文 (功能完备)
    ├── SimpleEvaluationContext                       — 受限求值上下文 (构建器模式)
    ├── ReflectivePropertyAccessor                    — 反射属性访问器
    ├── MapAccessor                                   — Map 属性访问
    ├── ReflectiveIndexAccessor                       — 反射索引访问器
    ├── ReflectiveMethodResolver                      — 反射方法解析
    ├── ReflectiveConstructorResolver                 — 反射构造器解析
    ├── DataBindingPropertyAccessor                   — 数据绑定属性访问
    ├── DataBindingMethodResolver                     — 数据绑定方法解析
    ├── StandardTypeLocator                           — 标准类型定位 (基于 ClassLoader)
    ├── StandardTypeConverter                         — 标准类型转换 (委托 ConversionService)
    ├── StandardTypeComparator                        — 标准类型比较
    ├── StandardOperatorOverloader                    — 标准运算符重载
    └── ReflectionHelper                              — 反射辅助工具
```

---

## 三、核心概念关系

```
                    ┌──────────────────────┐
                    │  ExpressionParser    │  ← SpEL 解析入口
                    │  (接口)              │
                    └──────────┬───────────┘
                               │ 实现
                    ┌──────────▼───────────┐
                    │ SpelExpressionParser │  ← 用户直接使用的类
                    │  extends T.A.E.P.    │
                    └──────────┬───────────┘
                               │ 委托
                    ┌──────────▼────────────────┐
                    │ InternalSpelExpressionParser│  ← 递归下降解析器 (1061行)
                    │  - 词法分析 Tokenizer     │
                    │  - 语法分析 eat*() 系列    │
                    │  - AST 构建 SpelNodeImpl   │
                    └──────────┬────────────────┘
                               │ 产生
                    ┌──────────▼───────────┐
                    │   SpelExpression     │  ← 已解析的表达式
                    │   implements Expression│
                    └──────────┬───────────┘
                               │ getValue(context)
                    ┌──────────▼───────────┐
                    │ SpelNodeImpl.getValue()│← AST 根节点递归求值
                    │  (递归遍历 AST 树)    │
                    └──────────┬───────────┘
                               │ 使用
                    ┌──────────▼───────────┐
                    │  EvaluationContext   │  ← 提供变量、方法、类型、转换等
                    │  (接口)              │
                    └──────────────────────┘
```

---

## 四、核心流程

### 4.1 表达式解析与求值总流程

```
用户代码:
  ExpressionParser parser = new SpelExpressionParser();
  Expression exp = parser.parseExpression("name.toUpperCase() + ' - ' + (age + 1)");
  String result = exp.getValue(context, rootObject, String.class);

内部流程:
  │
  ├── ① 解析阶段: SpelExpressionParser.parseExpression(exprString)
  │     │
  │     ├── TemplateAwareExpressionParser.parseExpression()
  │     │     │
  │     │     ├── 检测是否含模板语法 #{...}
  │     │     │   ├── 纯表达式 → doParseExpression(expressionString, null)
  │     │     │   └── 模板混合 → 分解为文本片段 + #{expr}
  │     │     │       └── 返回 CompositeStringExpression
  │     │     │
  │     │     └── doParseExpression() → InternalSpelExpressionParser
  │     │
  │     └── InternalSpelExpressionParser.doParseExpression()
  │           │
  │           ├── Tokenizer 词法分析: 字符串 → List<Token>
  │           │   └── 生成 Token 流: IDENTIFIER("name"), DOT("."), IDENTIFIER("toUpperCase"),
  │           │       LPAREN, RPAREN, PLUS, LITERAL_STRING(" - "), PLUS, ...
  │           │
  │           ├── 语法分析: 递归下降解析
  │           │   eatLogicalOrExpression()
  │           │   → eatRelationalExpression()
  │           │   → eatSumExpression()
  │           │   → eatProductExpression()
  │           │   → eatPowerExpression()
  │           │   → eatUnaryExpression()
  │           │   → eatPrimaryExpression()  ← 基础单元
  │           │
  │           └── 构建 AST: 返回 SpelNodeImpl 根节点 (CompoundExpression 或具体运算符节点)
  │
  ├── ② 编译阶段 (可选): SpelCompiler.compile(expression)
  │     │
  │     ├── 条件: compilerMode != OFF
  │     │   ├── IMMEDIATE: 首次求值前立即编译
  │     │   └── MIXED: 解释执行 N 次后 (默认 100) 触发编译
  │     │
  │     └── 生成: ASM 字节码 → CompiledExpression (直接 JVM 执行)
  │
  └── ③ 求值阶段: SpelExpression.getValue(context, rootObject)
        │
        ├── 编译模式 → 直接调用编译后的字节码
        │
        └── 解释模式 → SpelNodeImpl.getValue(ExpressionState state)
              │
              ├── ExpressionState 管理:
              │   ├── EvaluationContext 引用
              │   ├── rootObject
              │   ├── 操作数栈 (ArrayDeque)
              │   └── 变量作用域 (activeVariables)
              │
              └── 每个 SpelNodeImpl.getValue(state) 自递归求值:
                    ├── CompoundExpression: 依次求值每个子表达式
                    ├── PropertyOrFieldReference: PropertyAccessor 链查找
                    ├── MethodReference: MethodResolver 链解析 + 反射调用
                    ├── OpPlus: 左子节点 + 右子节点 (含字符串拼接)
                    ├── Ternary: 条件求值 → 真分支 / 假分支
                    └── ...
```

### 4.2 递归下降解析（运算符优先级）

```
表达式: a + b * c > 100 && d != null

解析时严格遵守运算符优先级 (从低到高):

优先级(低→高)    方法                      对应运算符
─────────────────────────────────────────────────
  1  赋值        eatLogicalOrExpression      = (Assign)
  2  条件        eatLogicalOrExpression      ?: (Ternary), ?: (Elvis)
  3  逻辑或      eatLogicalOrExpression      or, ||
  4  逻辑与      eatRelationalExpression     and, &&
  5  关系        eatRelationalExpression     eq, ne, lt, le, gt, ge, instanceof, matches, between
  6  加减        eatSumExpression            +, -
  7  乘除取模    eatProductExpression        *, /, %
  8  幂          eatPowerExpression          ^
  9  一元        eatUnaryExpression          !, not, +, -, ++, --
  10 基础        eatPrimaryExpression        字面量, 标识符, 引用, (), [], {}, new

解析过程 (递归下降):
  eatLogicalOrExpression()
    ├── eatRelationalExpression()  → AST: (a + b * c > 100)
    │     ├── eatSumExpression()   → AST: (a + b * c)
    │     │     ├── eatProductExpression() → Identifier("a")
    │     │     ├── OpPlus
    │     │     └── eatProductExpression() → (b * c)
    │     │           ├── Identifier("b")
    │     │           ├── OpMultiply
    │     │           └── Identifier("c")
    │     ├── OpGT
    │     └── eatSumExpression() → LiteralInt(100)
    │
    ├── OpAnd
    └── eatRelationalExpression() → AST: (d != null)
          ├── Identifier("d")
          ├── OpNE
          └── NullLiteral
```

### 4.3 SpEL 语法速查表

| 类别 | 语法 | 示例 |
|------|------|------|
| **字面量** | 字符串 `'...'`, 数字 `1`, `3.14`, `0xFF`, 布尔 `true/false`, null | `'hello'`, `42`, `true` |
| **属性访问** | `.property` | `person.name` |
| **安全导航** | `?.` | `person?.address?.city` |
| **方法调用** | `.method(args)` | `'abc'.toUpperCase()` |
| **索引访问** | `[index]`, `['key']` | `list[0]`, `map['key']` |
| **内联List** | `{a, b, c}` | `{1, 2, 3, 4}` |
| **内联Map** | `{key:value}` | `{name:'Jack', age:42}` |
| **集合投影** | `.!\[expr\]` | `list.!\[name\]` → 所有 name |
| **集合选择** | `.?\[expr\]` | `list.?\[age > 18\]` → 过滤 |
| **算术** | `+ - * / % ^` | `2 ^ 10` → 1024 |
| **比较** | `eq ne lt le gt ge` 或 `== != < <= > >=` | `age >= 18` |
| **逻辑** | `and or not` 或 `&& \|\| !` | `a and b` |
| **instanceof** | `instanceof` | `obj instanceof T(String)` |
| **matches** | `matches` | `str matches '\d+'` |
| **between** | `between` | `num between {1, 10}` |
| **三元** | `?:`, `?:` (Elvis) | `a ?: 'default'` |
| **类型引用** | `T(package.Class)` | `T(java.lang.Math).PI` |
| **构造器** | `new Class(args)` | `new String('hello')` |
| **变量** | `#varName` | `#root`, `#this` |
| **Bean引用** | `@beanName` | `@myService` |
| **函数调用** | `#fn(args)` | `#max(1, 2, 3)` |
| **赋值** | `#var = value` | `#result = a + b` |
| **模板** | `text #{expr} text` | `Hello #{name}!` |

### 4.4 属性访问解析流程 (PropertyAccessor 责任链)

```
PropertyOrFieldReference.getValueInternal(state)
  │
  ├── 获取 context 中的 PropertyAccessor 列表
  │     ├── StandardEvaluationContext: [ReflectivePropertyAccessor, MapAccessor, ...]
  │     └── SimpleEvaluationContext: [DataBindingPropertyAccessor, MapAccessor]
  │
  ├── 遍历 PropertyAccessor:
  │   for (PropertyAccessor accessor : accessors) {
  │     if (accessor.canRead(context, target, name)) {
  │       return accessor.read(context, target, name);
  │     }
  │   }
  │
  └── 典型实现:
        ├── ReflectivePropertyAccessor:
        │     └── 通过 JavaBean 内省 → PropertyDescriptor → getter/setter
        │
        ├── MapAccessor:
        │     └── target instanceof Map → map.get(key)
        │
        └── DataBindingPropertyAccessor (SimpleEvaluationContext):
              └── 仅允许读 Map/List/数组/基本类型 (无反射)
```

### 4.5 StandardEvaluationContext vs SimpleEvaluationContext

| | StandardEvaluationContext | SimpleEvaluationContext |
|---|---|---|
| 属性访问 | 全反射 (public/private) | 限制反射 (仅 public) 或纯 Map/List |
| 方法调用 | 允许任意方法 | 默认禁用，可手动开启 |
| 构造器 | 允许 | 默认禁用 |
| 类型引用 `T(...)` | 允许 | 默认禁用 |
| Bean 引用 `@...` | 支持 (需 BeanResolver) | 默认不支持 |
| 赋值操作 `=` | 允许 | 默认禁用 |
| 用途 | Spring 内部、完整 SpEL | 用户输入、数据绑定、模板 |
| 安全性 | 低 (可执行任意方法) | 高 (默认沙箱) |
| 构建方式 | `new StandardEvaluationContext(root)` | `SimpleEvaluationContext.forReadOnlyDataBinding().build()` |

---

## 五、关键类速查

| 类/接口 | 包 | 说明 |
|---------|-----|------|
| `ExpressionParser` | `expression` | 表达式解析器接口 |
| `Expression` | `expression` | 已解析表达式接口 (getValue/setValue) |
| `EvaluationContext` | `expression` | 求值上下文接口 (8 种策略) |
| `PropertyAccessor` | `expression` | 属性访问器策略 |
| `MethodResolver` | `expression` | 方法解析器策略 |
| `SpelExpressionParser` | `spel.standard` | SpEL 解析器入口 |
| `InternalSpelExpressionParser` | `spel.standard` | 内部递归下降解析器 (1061 行) |
| `SpelExpression` | `spel` | SpEL 表达式实现 |
| `SpelNodeImpl` | `spel.ast` | 所有 AST 节点的抽象基类 (53 种节点) |
| `ExpressionState` | `spel` | 求值状态 (上下文、操作数栈、变量) |
| `SpelCompiler` | `spel.standard` | JIT 编译器 (ASM 字节码) |
| `StandardEvaluationContext` | `spel.support` | 功能完备的求值上下文 |
| `SimpleEvaluationContext` | `spel.support` | 受限求值上下文 (沙箱) |
| `ReflectivePropertyAccessor` | `spel.support` | 反射属性访问器 |
| `ReflectiveMethodResolver` | `spel.support` | 反射方法解析器 |
| `StandardTypeLocator` | `spel.support` | 包前缀搜索类型定位 |
| `StandardTypeConverter` | `spel.support` | 委托 ConversionService 的类型转换 |
| `TemplateAwareExpressionParser` | `common` | 模板表达式解析抽象基类 |

---

## 六、依赖关系

```
spring-expression
  └── api: spring-core

---

## 七、相关文档

| 方向 | 模块 | 层级 | 说明 |
|------|------|------|------|
| 上游 | [spring-core](L1-spring-core.md) | L1 核心 | 类型转换、反射、ASM |
| 下游 | [spring-context](L4-spring-context.md) | L4 上下文 | SpEL 集成：@Value、@EventListener.condition |
```
