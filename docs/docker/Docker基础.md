# Docker 基础使用

## 1. Docker 简介

### 1.1 什么是 Docker
Docker 是一个开源的应用容器引擎，基于 Go 语言实现，让开发者可以打包应用及依赖到轻量级容器中，实现"一次构建，到处运行"。

### 1.2 核心概念
- **镜像（Image）**：只读模板，包含运行环境
- **容器（Container）**：镜像的运行实例
- **仓库（Registry）**：镜像存储中心（Docker Hub）
- **Dockerfile**：构建镜像的脚本
- **数据卷（Volume）**：持久化数据
- **网络（Network）**：容器通信

### 1.3 架构
```
Client (docker CLI) -> Docker Host (dockerd) -> Registry
                              |
                      Containers (Container1, Container2...)
```

## 2. 安装与配置

### 2.1 安装
```bash
# CentOS
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install docker-ce docker-ce-cli containerd.io

# Ubuntu
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io
```

### 2.2 启动与验证
```bash
systemctl start docker
systemctl enable docker
docker version
docker info
```

### 2.3 配置镜像加速
```json
{
  "registry-mirrors": ["https://<your-mirror>.mirror.aliyuncs.com"]
}
```

## 3. 镜像管理

### 3.1 常用命令
```bash
docker pull <image>:<tag>          # 拉取镜像
docker images                      # 查看镜像列表
docker rmi <image>                 # 删除镜像
docker tag <old> <new>             # 标记镜像
docker push <image>                # 推送镜像
docker save -o <file> <image>      # 导出镜像
docker load -i <file>              # 导入镜像
docker history <image>             # 查看构建历史
```

### 3.2 搜索镜像
```bash
docker search <keyword>
```

## 4. 容器管理

### 4.1 创建与运行
```bash
docker run [options] <image> [command]
# 常用选项：
# -d         后台运行
# -it        交互模式
# --name     指定名称
# -p         端口映射 (主机:容器)
# -v         数据卷挂载
# -e         设置环境变量
# --network  指定网络
# --rm       退出后自动删除

# 示例
docker run -d --name nginx -p 80:80 nginx:latest
docker run -it --name ubuntu ubuntu:22.04 /bin/bash
```

### 4.2 生命周期管理
```bash
docker ps                    # 运行中容器
docker ps -a                 # 所有容器
docker start/stop/restart    # 启停容器
docker pause/unpause         # 暂停/恢复
docker rm <container>        # 删除容器
docker logs -f <container>   # 查看日志
docker exec -it <container> bash  # 进入容器
docker inspect <container>   # 查看详细信息
docker stats                 # 资源监控
```

## 5. Dockerfile

### 5.1 常用指令
| 指令 | 说明 | 示例 |
|------|------|------|
| FROM | 基础镜像 | `FROM openjdk:11` |
| MAINTAINER | 维护者 | `MAINTAINER xxx` |
| RUN | 运行命令 | `RUN apt-get update` |
| COPY | 复制文件 | `COPY app.jar /app/` |
| ADD | 复制+解压 | `ADD app.tar.gz /app/` |
| WORKDIR | 工作目录 | `WORKDIR /app` |
| EXPOSE | 暴露端口 | `EXPOSE 8080` |
| ENV | 环境变量 | `ENV JAVA_HOME=/usr/lib/jvm` |
| CMD | 默认命令 | `CMD ["java","-jar","app.jar"]` |
| ENTRYPOINT | 入口点 | `ENTRYPOINT ["java","-jar"]` |
| VOLUME | 数据卷 | `VOLUME /data` |
| USER | 指定用户 | `USER nobody` |

### 5.2 示例
```dockerfile
FROM openjdk:11-jre-slim
WORKDIR /app
COPY target/app.jar app.jar
EXPOSE 8080
ENV SPRING_PROFILES_ACTIVE=prod
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 5.3 构建命令
```bash
docker build -t myapp:1.0 .
docker build -t myapp:1.0 -f Dockerfile.prod .
```

## 6. 数据管理

### 6.1 数据卷 Volume
```bash
docker volume create my-vol
docker volume ls
docker volume inspect my-vol

# 挂载数据卷
docker run -v my-vol:/data nginx
# 挂载主机目录
docker run -v /host/path:/container/path nginx
# 只读挂载
docker run -v /host/path:/container/path:ro nginx
```

### 6.2 数据卷容器
```bash
# 创建数据卷容器
docker create -v /data --name data-container busybox

# 挂载数据卷容器
docker run --volumes-from data-container nginx
```

## 7. 网络管理

### 7.1 网络模式
- **bridge**：默认，NAT 模式
- **host**：共享主机网络
- **none**：无网络
- **overlay**：跨主机网络（Swarm）

### 7.2 网络操作
```bash
docker network ls                    # 查看网络
docker network create --driver bridge my-net
docker network connect my-net container
docker network disconnect my-net container
docker run --network my-net nginx
```

### 7.3 端口映射
```bash
docker run -p 8080:80 nginx          # 主机8080->容器80
docker run -p 192.168.1.1:8080:80    # 指定IP
docker run -p 8080-8090:8080-8090    # 端口范围
```

## 8. Docker Compose

### 8.1 docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    depends_on:
      - app

  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=db
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: app
    volumes:
      - mysql-data:/var/lib/mysql

volumes:
  mysql-data:
```

### 8.2 常用命令
```bash
docker-compose up -d               # 启动
docker-compose down                # 停止并删除
docker-compose ps                  # 查看状态
docker-compose logs -f             # 日志
docker-compose exec app bash       # 进入容器
docker-compose build               # 重新构建
docker-compose restart             # 重启
```

## 9. 最佳实践

- 使用 `.dockerignore` 忽略不必要的文件
- 尽量使用官方镜像并指定版本
- 减少镜像层数，合并 RUN 命令
- 多阶段构建减小镜像体积
- 不要以 root 运行容器
- 容器视为无状态，数据放数据卷
- 使用健康检查
- 合理设置资源限制（--memory, --cpus）
