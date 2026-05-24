# Maven 项目构建工具

## 1. 项目构建工具演进

- **Make**：C 项目，Makefile
- **Ant**：Java 项目，build.xml，需要手动管理依赖
- **Maven**：约定优于配置，POM 管理依赖，自动依赖传递
- **Gradle**：基于 Groovy/Kotlin DSL，更灵活高效

## 2. Maven 基本概念

### 2.1 什么是 Maven
Maven 是基于项目对象模型（POM）的项目管理和构建工具，主要功能：
- 依赖管理（自动下载、版本管理、依赖传递）
- 项目构建（编译、测试、打包、部署）
- 项目信息管理
- 多模块项目管理

### 2.2 核心优势
- **依赖管理**：自动下载和解决依赖冲突
- **统一构建**：标准化构建流程
- **项目信息**：自动生成文档、报告
- **仓库机制**：本地/中央/远程仓库
- **生命周期**：clean -> compile -> test -> package -> install -> deploy

## 3. POM 详解

### 3.1 坐标
```xml
<groupId>com.company</groupId>
<artifactId>project-name</artifactId>
<version>1.0.0</version>
<packaging>jar</packaging>
```

### 3.2 常用标签
- **parent**：继承父 POM
- **properties**：定义属性变量
- **dependencies**：依赖管理
- **dependencyManagement**：统一版本管理（不引入依赖）
- **build**：构建配置（plugins、resources）
- **profiles**：多环境配置
- **repositories**：仓库配置

### 3.3 依赖范围 scope
| scope | 编译 | 测试 | 运行 | 示例 |
|-------|------|------|------|------|
| compile | ✓ | ✓ | ✓ | 默认 |
| provided | ✓ | ✓ | ✗ | servlet-api |
| runtime | ✗ | ✓ | ✓ | JDBC 驱动 |
| test | ✗ | ✓ | ✗ | JUnit |
| system | ✓ | ✓ | ✗ | 本地 jar |

## 4. 依赖机制

### 4.1 依赖传递
A -> B -> C（A 间接依赖 C）

### 4.2 依赖冲突解决
- **最短路径优先**：路径短的优先
- **最先声明优先**：同等路径下先声明的优先
- **排除依赖**：使用 exclusions 排除
- **可选依赖**：optional=true 不传递

### 4.3 排除依赖
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>example</artifactId>
    <version>1.0</version>
    <exclusions>
        <exclusion>
            <groupId>com.old</groupId>
            <artifactId>old-lib</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 4.4 查看依赖树
```bash
mvn dependency:tree
mvn dependency:tree -Dverbose -Dincludes=groupId:artifactId
```

## 5. 生命周期与插件

### 5.1 三套生命周期
- **clean**：pre-clean -> clean -> post-clean
- **default**：compile -> test -> package -> install -> deploy
- **site**：pre-site -> site -> post-site -> site-deploy

### 5.2 常用插件
- **maven-compiler-plugin**：编译配置
- **maven-surefire-plugin**：测试
- **maven-jar-plugin**：打包
- **maven-assembly-plugin**：自定义打包
- **maven-source-plugin**：源码包
- **maven-deploy-plugin**：部署
- **maven-shade-plugin**：Uber JAR

## 6. 仓库

### 6.1 仓库类型
- **本地仓库**：~/.m2/repository
- **中央仓库**：Maven Central
- **私有仓库**：Nexus / Artifactory

### 6.2 配置远程仓库
```xml
<repositories>
    <repository>
        <id>aliyun</id>
        <url>https://maven.aliyun.com/repository/public</url>
    </repository>
</repositories>
```

### 6.3 settings.xml 配置
```xml
<settings>
    <localRepository>/path/to/repo</localRepository>
    <mirrors>
        <mirror>
            <id>aliyun</id>
            <mirrorOf>central</mirrorOf>
            <url>https://maven.aliyun.com/repository/public</url>
        </mirror>
    </mirrors>
    <servers>
        <server>
            <id>releases</id>
            <username>admin</username>
            <password>admin</password>
        </server>
    </servers>
</settings>
```

## 7. 多模块项目

### 7.1 父 POM
```xml
<packaging>pom</packaging>
<modules>
    <module>module-a</module>
    <module>module-b</module>
</modules>
```

### 7.2 子模块继承
```xml
<parent>
    <groupId>com.company</groupId>
    <artifactId>parent</artifactId>
    <version>1.0.0</version>
</parent>
```

## 8. Profiles 多环境
```xml
<profiles>
    <profile>
        <id>dev</id>
        <properties>
            <env>dev</env>
        </properties>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
    </profile>
    <profile>
        <id>prod</id>
        <properties>
            <env>prod</env>
        </properties>
    </profile>
</profiles>
```
```bash
mvn package -Pprod
```

## 9. 常用命令
```bash
mvn clean                    # 清理
mvn compile                  # 编译
mvn test                     # 测试
mvn package                  # 打包
mvn install                  # 安装到本地仓库
mvn deploy                   # 部署到远程仓库
mvn clean install -U         # 强制更新快照
mvn dependency:tree          # 依赖树
mvn help:effective-pom       # 查看有效 POM
```
