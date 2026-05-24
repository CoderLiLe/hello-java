# Nginx 基础

## 1. Nginx 概述

Nginx 是一款高性能的 HTTP 和反向代理 Web 服务器，以其高并发、低内存消耗著称。

### 1.1 核心功能
- HTTP 静态资源服务
- 反向代理
- 负载均衡
- HTTP 缓存
- SSL/TLS 终止
- WebSocket 代理
- 限流、访问控制

## 2. 安装与配置

### 2.1 安装
```bash
# CentOS
yum install epel-release nginx -y

# Ubuntu
apt-get update && apt-get install nginx -y

# 源码编译
./configure --prefix=/usr/local/nginx \
  --with-http_ssl_module \
  --with-http_v2_module \
  --with-stream
make && make install
```

### 2.2 目录结构
```
/etc/nginx/
├── nginx.conf          # 主配置文件
├── conf.d/             # 子配置
├── sites-available/    # 站点配置
├── sites-enabled/      # 启用站点
├── modules/            # 模块
└── ssl/                # SSL 证书
```

## 3. 核心配置

### 3.1 主配置 nginx.conf
```nginx
worker_processes  auto;
events {
    worker_connections  1024;
    use epoll;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile      on;
    keepalive_timeout  65;
    
    # 虚拟主机
    server {
        listen       80;
        server_name  example.com;
        
        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }
    }
}
```

### 3.2 location 匹配规则
| 规则 | 说明 | 优先级 |
|------|------|--------|
| `=` | 精确匹配 | 1 |
| `^~` | 前缀匹配（优先正则） | 2 |
| `~` | 正则匹配（区分大小写） | 3 |
| `~*` | 正则匹配（不区分大小写） | 3 |
| 无 | 前缀匹配 | 4 |

```nginx
location = / {                    # 精确匹配 /
    return 200 "Welcome";
}
location ^~ /images/ {            # 前缀匹配
    root /data;
}
location ~* \.(gif|jpg|png)$ {    # 正则匹配
    root /data/images;
}
```

## 4. 反向代理

```nginx
location /api/ {
    proxy_pass http://backend:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 5. 负载均衡

```nginx
upstream backend {
    # 负载均衡策略
    # 默认：轮询
    # weight：权重
    # ip_hash：IP 绑定
    # least_conn：最少连接
    # fair：响应时间（第三方）
    
    server 192.168.1.1:8080 weight=3;
    server 192.168.1.2:8080 weight=2;
    server 192.168.1.3:8080 backup;  # 备用
    
    keepalive 32;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

## 6. HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate     /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HTTP 自动跳转 HTTPS
    error_page 497 =301 https://$host$request_uri;
}
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## 7. 限流

```nginx
# 定义限流区域
limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

# 连接数限制
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    location /api/ {
        limit_req zone=mylimit burst=20 nodelay;
        limit_conn addr 10;
        limit_rate 1m;
        proxy_pass http://backend;
    }
}
```

## 8. 动静分离

```nginx
server {
    # 静态资源
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        root /data/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 动态请求
    location / {
        proxy_pass http://backend;
    }
}
```

## 9. 日志配置

```nginx
http {
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    '$upstream_response_time $request_time';
    
    access_log /var/log/nginx/access.log main buffer=32k;
    error_log  /var/log/nginx/error.log warn;
}
```

## 10. 性能优化

```nginx
# 进程
worker_processes auto;
worker_cpu_affinity auto;
worker_rlimit_nofile 65535;

# 事件
events {
    use epoll;
    worker_connections 65535;
    multi_accept on;
}

# HTTP
http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # 缓冲
    proxy_buffer_size 4k;
    proxy_buffers 100 8k;
    proxy_busy_buffers_size 8k;
    
    # 超时
    keepalive_timeout 65;
    client_body_timeout 10;
    send_timeout 10;
    
    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;
    gzip_comp_level 6;
    gzip_vary on;
}
```

## 11. OpenResty

OpenResty 在 Nginx 基础上集成了 LuaJIT，提供可编程 Web 平台。

```nginx
# 请求处理阶段
init_by_lua_block { ... }       # 初始化
access_by_lua_block { ... }     # 访问控制
content_by_lua_block {          # 内容生成
    ngx.say("Hello, OpenResty")
}
log_by_lua_block { ... }        # 日志

# Lua 共享内存
lua_shared_dict cache 10m;

# 动态上游
init_by_lua_block {
    upstream = require("upstream")
}
```
