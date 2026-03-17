# 贡献指南

感谢您考虑为 hello-java 项目做出贡献！

## 🎯 如何贡献

### 报告问题
- 使用 [GitHub Issues](https://github.com/CoderLiLe/hello-java/issues) 报告bug或提出功能请求
- 在创建issue前，请先搜索是否已有类似问题
- 提供清晰的问题描述和复现步骤
- 如果是bug，请包括：
  - 环境信息（Java版本、操作系统等）
  - 错误日志
  - 复现步骤

### 提交代码
1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

### 开发规范

#### 代码风格
- 遵循Java编码规范
- 使用4个空格缩进（不要使用Tab）
- 类名使用大驼峰命名法：`MyClass`
- 方法名和变量名使用小驼峰命名法：`myMethod`, `myVariable`
- 常量使用全大写加下划线：`MAX_SIZE`

#### 注释规范
- 类和方法需要有JavaDoc注释
- 复杂逻辑需要有行内注释
- 使用英文注释（除非特别说明）

#### 提交消息规范
使用清晰、描述性的提交消息，遵循[约定式提交](https://www.conventionalcommits.org/)：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响代码逻辑）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

示例：
```
feat: 添加Spring Boot示例代码

- 添加Spring Boot基础配置
- 添加RESTful API示例
- 添加单元测试

Closes #123
```

## 🔧 开发环境设置

### 前提条件
- Java 17 或更高版本
- Maven 3.6+ 或 Gradle 7+
- Git

### 设置步骤
1. 克隆仓库
   ```bash
   git clone https://github.com/CoderLiLe/hello-java.git
   cd hello-java
   ```

2. 导入项目到IDE
   - IntelliJ IDEA: File → Open → 选择项目目录
   - Eclipse: File → Import → Existing Maven/Gradle Project
   - VS Code: 打开项目目录，安装Java扩展

3. 构建项目
   ```bash
   # Maven
   mvn clean compile
   
   # Gradle
   ./gradlew build
   ```

4. 运行测试
   ```bash
   # Maven
   mvn test
   
   # Gradle
   ./gradlew test
   ```

## 📁 项目结构

```
hello-java/
├── src/                    # 源代码
│   ├── main/java/         # 主代码
│   └── test/java/         # 测试代码
├── docs/                  # 文档
├── examples/              # 示例代码
├── scripts/               # 脚本文件
├── .github/               # GitHub配置
│   └── workflows/         # GitHub Actions工作流
├── README.md              # 项目说明
├── CONTRIBUTING.md        # 贡献指南
├── LICENSE                # 许可证
└── .gitignore             # Git忽略文件
```

## 🧪 测试

### 单元测试
- 使用JUnit 5
- 测试类名格式：`ClassNameTest`
- 测试方法名格式：`testMethodName_Scenario_ExpectedResult`

### 集成测试
- 在`src/test/java`中创建`integration`包
- 使用Spring Boot Test（如果适用）
- 使用Testcontainers进行容器化测试

### 测试覆盖率
- 目标覆盖率：>80%
- 使用JaCoCo生成覆盖率报告

## 🔄 代码审查流程

1. **创建Pull Request**
   - 确保代码通过所有测试
   - 更新相关文档
   - 添加适当的测试

2. **代码审查**
   - 至少需要一名维护者批准
   - 审查重点：代码质量、测试覆盖、文档更新
   - 可能需要多次修改

3. **合并**
   - 所有检查通过
   - 获得批准
   - 解决所有评论

## 📝 文档

### 更新文档
- 代码变更需要更新相关文档
- 新功能需要添加使用示例
- API变更需要更新API文档

### 文档格式
- 使用Markdown格式
- 包含清晰的标题和结构
- 添加代码示例
- 使用表格展示复杂信息

## 🚀 发布流程

1. 版本号遵循[语义化版本](https://semver.org/)
2. 更新CHANGELOG.md
3. 创建Git tag
4. 发布到Maven Central（如果适用）

## ❓ 需要帮助？

如果您有任何问题：
1. 查看 [GitHub Issues](https://github.com/CoderLiLe/hello-java/issues)
2. 查看 [GitHub Discussions](https://github.com/CoderLiLe/hello-java/discussions)
3. 联系维护者

## 🙏 致谢

感谢所有贡献者的努力和付出！

---

*最后更新: 2026-03-18*