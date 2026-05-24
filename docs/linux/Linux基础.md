# Linux 基础

## 1. Linux 简介

### 1.1 什么是 Linux
Linux 是一种自由和开放源代码的类 UNIX 操作系统，由 Linus Torvalds 于 1991 年创建。

### 1.2 Linux 特点
- 开放性、多用户、多任务
- 丰富的网络功能
- 可靠的系统安全
- 良好的可移植性
- 标准兼容性

### 1.3 发行版本
- **Red Hat Linux**：企业级，RHEL/CentOS/Fedora
- **Ubuntu Linux**：桌面友好，基于 Debian
- **Debian Linux**：稳定
- **SUSE Linux**：欧洲流行

## 2. Linux 文件系统

### 2.1 目录结构
```
/       - 根目录
/bin    - 二进制可执行命令
/sbin   - 系统管理命令
/etc    - 配置文件
/dev    - 设备文件
/var    - 可变数据(日志)
/home   - 用户主目录
/root   - root 用户主目录
/tmp    - 临时文件
/usr    - 用户程序
/opt    - 可选应用程序
/proc   - 进程信息虚拟文件系统
```

### 2.2 文件类型
- `-` 普通文件
- `d` 目录
- `l` 符号链接
- `c` 字符设备
- `b` 块设备
- `s` 套接字
- `p` 管道

### 2.3 文件操作
| 命令 | 说明 | 示例 |
|------|------|------|
| `touch` | 创建文件 | `touch file.txt` |
| `rm` | 删除文件 | `rm file.txt` |
| `mv` | 移动/重命名 | `mv a.txt b.txt` |
| `cp` | 复制 | `cp a.txt b.txt` |
| `cat` | 查看文件 | `cat file.txt` |
| `head` | 查看文件头 | `head -n 20 file.txt` |
| `tail` | 查看文件尾 | `tail -f file.log` |
| `less` | 分页查看 | `less file.txt` |
| `more` | 分页查看 | `more file.txt` |

### 2.4 目录操作
- `cd`：切换目录
- `pwd`：显示当前路径
- `mkdir`：创建目录
- `rmdir`：删除空目录
- `rm -rf`：递归强制删除

### 2.5 软/硬链接
- **硬链接**：多个文件名指向同一 inode，不能跨文件系统
  - `ln source link`
- **软链接**：快捷方式，可跨文件系统
  - `ln -s source link`

## 3. 用户与权限

### 3.1 用户和组
- UID：用户 ID（root=0，系统用户 1~499，普通用户 500+）
- GID：组 ID
- 相关命令：`id`, `groups`, `useradd`, `usermod`, `userdel`, `groupadd`

### 3.2 文件权限
```
-rwxr-xr-x
-   文件类型
rwx  所有者权限(7)
r-x  所属组权限(5)
r-x  其他人权限(5)
```

权限数字表示：r=4, w=2, x=1

### 3.3 权限管理命令
- `chmod`：修改权限（`chmod 755 file` 或 `chmod u+x file`）
- `chown`：修改所有者（`chown user:group file`）
- `chgrp`：修改所属组

## 4. 常用命令

### 4.1 查找与搜索
- `find <path> -name <pattern>` - 查找文件
- `grep <pattern> <file>` - 搜索内容
- `locate <name>` - 快速查找（依赖数据库）
- `which <cmd>` - 查找命令路径
- `whereis <cmd>` - 查找命令及文档

### 4.2 压缩与归档
- `tar -czf archive.tar.gz dir/` - 打包压缩
- `tar -xzf archive.tar.gz` - 解压
- `zip -r archive.zip dir/` - ZIP 压缩
- `unzip archive.zip` - ZIP 解压

### 4.3 网络命令
- `ping`, `ifconfig`/`ip`, `netstat`, `ss`, `curl`, `wget`, `ssh`

### 4.4 进程管理
- `ps`：查看进程
- `top`/`htop`：实时监控
- `kill`：终止进程
- `bg`/`fg`：前后台切换
- `nohup`：后台运行

### 4.5 系统信息
- `uname -a`：内核信息
- `df -h`：磁盘空间
- `du -sh`：目录大小
- `free -h`：内存使用
- `lscpu`：CPU 信息

## 5. 文本编辑 vim

### 5.1 三种模式
- **命令模式**：默认，移动光标、复制粘贴
- **插入模式**：按 `i` 进入，编辑文本
- **末行模式**：按 `:` 进入，保存退出

### 5.2 常用操作
- `:w` 保存，`:q` 退出，`:wq` 保存退出，`:q!` 强制退出
- `dd` 删除行，`yy` 复制行，`p` 粘贴
- `/pattern` 搜索，`n` 下一个，`N` 上一个
- `:%s/old/new/g` 全局替换

## 6. Shell 脚本基础

### 6.1 变量
```bash
name="world"
echo "Hello, $name"
```

### 6.2 条件判断
```bash
if [ -f "$file" ]; then
    echo "文件存在"
fi
```

### 6.3 循环
```bash
for i in {1..5}; do
    echo $i
done
```

### 6.4 函数
```bash
function hello() {
    echo "Hello, $1"
}
hello "World"
```
