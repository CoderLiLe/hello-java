# 自动提交使用指南

## 📋 概述

本仓库配置了自动提交系统，可以自动检测更改、提交并推送到GitHub。系统包括：

1. **自动提交脚本** (`scripts/auto_commit.py`)
2. **GitHub Actions工作流** (CI和质量检查)
3. **定时任务配置** (可选)

## 🚀 快速开始

### 1. 手动运行自动提交

```bash
# 进入仓库目录
cd hello-java

# 运行自动提交
python3 scripts/auto_commit.py --run

# 干运行模式（只检查不执行）
python3 scripts/auto_commit.py --dry-run
```

### 2. 交互模式

```bash
python3 scripts/auto_commit.py
```

然后选择：
- `1`: 运行自动提交
- `2`: 干运行模式
- `3`: 查看配置
- `4`: 设置定时任务
- `5`: 退出

## ⚙️ 配置

配置文件: `.auto_commit_config.json`

```json
{
  "auto_commit": true,
  "commit_message_prefix": "[Auto] ",
  "branch": "main",
  "push_to_remote": true,
  "remote_name": "origin",
  "check_interval_minutes": 30,
  "max_commit_size_mb": 10,
  "exclude_patterns": [
    "*.log",
    "*.tmp",
    "*.bak",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "auto_commit_log.json"
  ]
}
```

### 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `auto_commit` | 是否启用自动提交 | `true` |
| `commit_message_prefix` | 提交消息前缀 | `"[Auto] "` |
| `branch` | 目标分支 | `"main"` |
| `push_to_remote` | 是否推送到远程 | `true` |
| `remote_name` | 远程仓库名称 | `"origin"` |
| `check_interval_minutes` | 检查间隔（分钟） | `30` |
| `max_commit_size_mb` | 最大提交大小（MB） | `10` |
| `exclude_patterns` | 排除文件模式 | 见上 |

## ⏰ 定时任务

### 方法1: Cron (推荐)

```bash
# 编辑crontab
crontab -e
```

添加以下行（每30分钟检查一次）：
```
*/30 * * * * cd /path/to/hello-java && python3 scripts/auto_commit.py --run
```

### 方法2: Systemd服务

1. 复制服务文件：
   ```bash
   sudo cp /tmp/hello-java-auto-commit.service /etc/systemd/system/
   ```

2. 启用并启动服务：
   ```bash
   sudo systemctl enable hello-java-auto-commit
   sudo systemctl start hello-java-auto-commit
   ```

3. 查看服务状态：
   ```bash
   sudo systemctl status hello-java-auto-commit
   ```

### 方法3: 使用脚本设置

```bash
python3 scripts/auto_commit.py --setup-cron
```

## 📊 日志

自动提交日志保存在 `auto_commit_log.json` 中，包含：

- 时间戳
- 是否有更改
- 提交状态
- 推送状态
- 消息和错误

查看日志：
```bash
# 查看最新日志
tail -f auto_commit_log.json

# 使用jq格式化查看
jq . auto_commit_log.json
```

## 🔧 GitHub Actions

仓库配置了两个GitHub Actions工作流：

### 1. CI工作流 (`.github/workflows/ci.yml`)
- 在push和pull request时运行
- 运行测试和代码检查
- 确保代码质量

### 2. 质量检查工作流 (`.github/workflows/quality-check.yml`)
- 每天凌晨2点运行
- 检查大文件
- 检查敏感数据
- 检查文件权限
- 生成质量报告

## 🛠️ 故障排除

### 常见问题

#### 1. 脚本没有执行权限
```bash
chmod +x scripts/auto_commit.py
```

#### 2. Python版本问题
```bash
# 检查Python版本
python3 --version

# 需要Python 3.7+
```

#### 3. Git认证失败
```bash
# 检查Git配置
git config --list

# 设置用户名和邮箱
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

#### 4. 推送权限不足
- 确保有仓库的写入权限
- 检查SSH密钥或令牌配置

### 调试模式

```bash
# 详细输出
python3 scripts/auto_commit.py --run --verbose

# 查看Git状态
git status
git log --oneline -5
```

## 📈 最佳实践

### 1. 提交频率
- 建议每30-60分钟检查一次
- 避免过于频繁的提交
- 确保每次提交都有实际意义

### 2. 提交大小
- 单个提交不超过10MB
- 大文件应该使用Git LFS
- 避免提交二进制文件

### 3. 代码质量
- 自动提交前确保代码通过测试
- 使用pre-commit钩子检查代码质量
- 定期运行质量检查

### 4. 备份策略
- 重要更改手动提交
- 定期创建备份
- 使用分支进行功能开发

## 🔄 工作流程

```
本地更改 → 自动检测 → 暂存更改 → 创建提交 → 推送到GitHub
    ↓           ↓           ↓           ↓           ↓
  编辑文件    git status   git add .   git commit   git push
```

## 📝 自定义

### 修改提交消息格式

编辑 `.auto_commit_config.json`：
```json
{
  "commit_message_prefix": "[Auto-Update] "
}
```

### 添加排除模式

```json
{
  "exclude_patterns": [
    "*.log",
    "*.tmp",
    "*.bak",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "auto_commit_log.json",
    "*.pdf",           // 新增
    "*.docx",          // 新增
    "temp/"            // 新增
  ]
}
```

### 禁用自动推送

```json
{
  "push_to_remote": false
}
```

## 🤝 贡献

如果您有改进建议：
1. 提交Issue
2. 创建Pull Request
3. 更新相关文档

## 📞 支持

如有问题：
- 查看GitHub Issues
- 查看本文档
- 联系维护者

---

*最后更新: 2026-03-18*