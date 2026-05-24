# Groovy 语言及应用

## 1. Groovy 概述

Groovy 是 JVM 上的动态语言，与 Java 高度兼容，支持静态/动态类型、DSL、元编程等特性。

### 1.1 特点
- 兼容 Java 语法
- 闭包和函数式编程
- 元编程（MOP）
- DSL 支持
- AST 转换
- 内置 JSON/XML 处理

## 2. 基本语法

### 2.1 变量
```groovy
def name = "Groovy"        // 动态类型
String name2 = "Java"      // 静态类型
def list = [1, 2, 3]       // 列表
def map = [key: 'value']   // 映射
def range = 1..10          // 范围
```

### 2.2 字符串
```groovy
def s1 = '单引号字符串'
def s2 = "GString ${name}"  // 插值
def s3 = '''多行
字符串'''
```

### 2.3 闭包
```groovy
def closure = { param ->
    println "Hello, $param"
}
closure("World")

// 常见使用
[1, 2, 3].each { println it }
[1, 2, 3].collect { it * 2 }
[1, 2, 3].findAll { it > 1 }
```

### 2.4 类
```groovy
class Person {
    String name
    int age
    
    String toString() {
        "Person($name, $age)"
    }
}
def p = new Person(name: 'John', age: 30)
```

## 3. 元编程

### 3.1 方法注入
```groovy
// 给 String 添加方法
String.metaClass.shout = { -> delegate.toUpperCase() }
println "hello".shout()  // HELLO
```

### 3.2 DSL 构建
```groovy
// 构建器模式
def xml = new groovy.xml.MarkupBuilder()
xml.people {
    person(name: "John") {
        age(30)
        city("New York")
    }
}

// 配置 DSL
def configure(closure) {
    closure.delegate = this
    closure()
}

server {
    port 8080
    host "localhost"
}
```

## 4. 应用场景

### 4.1 构建脚本（Gradle）
```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '2.7.0'
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

### 4.2 测试（Spock）
```groovy
class CalculatorSpec extends Specification {
    def "addition"() {
        expect:
        1 + 1 == 2
    }
    
    def "parameterized"() {
        expect:
        calculator.add(a, b) == result
        
        where:
        a | b | result
        1 | 2 | 3
        3 | 4 | 7
    }
}
```

### 4.3 数据处理
```groovy
// JSON
def json = JsonOutput.toJson([name: "John", age: 30])
def obj = new JsonSlurper().parseText(json)

// XML
def xml = new XmlSlurper().parse('data.xml')
println xml.name.text()
```

## 5. 与 Java 对比

| 特性 | Java | Groovy |
|------|------|--------|
| 类型 | 强类型 | 可选类型 |
| 编译 | 静态 | 动态+静态 |
| 代码量 | 多 | 少 |
| 函数式 | Java 8+ | 原生支持 |
| 元编程 | 反射 | MOP |
