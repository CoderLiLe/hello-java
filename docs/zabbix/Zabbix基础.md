# Zabbix 服务器监控工具

## 1. Zabbix 概述

Zabbix 是一个企业级开源分布式监控解决方案，用于监控网络、服务器、云、应用程序和服务。

### 1.1 核心功能
- 指标收集（CPU、内存、磁盘、网络等）
- 告警通知（邮件、短信、微信等）
- 可视化仪表板
- 自动发现
- 分布式监控

### 1.2 架构
```
Zabbix Server (中央)
    |           |
Zabbix Proxy (可选)
    |           |
Zabbix Agent  Zabbix Agent
    |              |
目标机器        目标机器
```

## 2. 安装

### 2.1 Server 安装
```bash
# CentOS 7/8
rpm -Uvh https://repo.zabbix.com/zabbix/6.0/rhel/8/x86_64/zabbix-release-6.0-1.el8.noarch.rpm
dnf install zabbix-server-mysql zabbix-web-mysql zabbix-agent

# 创建数据库
mysql -uroot -p
create database zabbix character set utf8mb4 collate utf8mb4_bin;
grant all privileges on zabbix.* to zabbix@localhost identified by 'password';

# 导入数据
zcat /usr/share/doc/zabbix-server-mysql*/create.sql.gz | mysql -uzabbix -p zabbix

# 配置 /etc/zabbix/zabbix_server.conf
DBHost=localhost
DBName=zabbix
DBUser=zabbix
DBPassword=password

# 启动
systemctl start zabbix-server zabbix-agent httpd php-fpm
systemctl enable zabbix-server zabbix-agent httpd php-fpm
```

### 2.2 Agent 安装
```bash
rpm -Uvh https://repo.zabbix.com/zabbix/6.0/rhel/8/x86_64/zabbix-release-6.0-1.el8.noarch.rpm
yum install zabbix-agent

# 配置 /etc/zabbix/zabbix_agentd.conf
Server=192.168.1.100        # Zabbix Server IP
ServerActive=192.168.1.100
Hostname=my-server

systemctl start zabbix-agent
```

## 3. 监控项

### 3.1 常用监控项
```conf
# 系统 CPU
system.cpu.load[all,avg1]
system.cpu.util[,user]

# 内存
vm.memory.size[total]
vm.memory.size[available]

# 磁盘
vfs.fs.size[/,total]
vfs.fs.size[/,used]
vfs.dev.read[/dev/sda,ops]

# 网络
net.if.in[eth0,bytes]
net.if.out[eth0,bytes]
```

### 3.2 自定义监控项
```bash
# Agent 配置
UserParameter=myapp.health,/usr/local/bin/check_app.sh

# 脚本
#!/bin/bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health
```

## 4. 触发器

```conf
# CPU 使用率超过 90% 触发告警
{custom:system.cpu.util[,idle].last(1)} < 10

# 磁盘使用率超过 80%
{custom:vfs.fs.size[/,pused].last(1)} > 80

# 进程挂了
{custom:myapp.health.last()} <> 200
```

## 5. 告警动作

### 5.1 告警媒介
- Email
- SMS
- Webhook
- 自定义脚本

### 5.2 通知消息模板
```text
告警: {TRIGGER.NAME}
状态: {TRIGGER.STATUS}
主机: {HOST.NAME}
时间: {EVENT.DATE} {EVENT.TIME}
当前值: {ITEM.VALUE}
```

## 6. 最佳实践

- 使用模板管理（Linux/Windows/MySQL/Redis 等官方模板）
- 合理设置监控项更新时间间隔
- 配置自动发现规则
- 定期维护历史数据
- 设置告警升级
- 聚合监控视图
