# Docker 集群管理

## 1. Docker Swarm

### 1.1 基本概念
- **Manager 节点**：管理集群状态，调度任务
- **Worker 节点**：运行任务
- **Service**：服务定义
- **Task**：任务实例（容器）
- **Stack**：多层服务组合

### 1.2 集群初始化
```bash
# Manager 节点
docker swarm init --advertise-addr <manager-ip>

# Worker 节点加入
docker swarm join --token <token> <manager-ip>:2377

# 管理节点
docker node ls
docker node promote <node>
docker node demote <node>
```

### 1.3 Service 管理
```bash
docker service create --name nginx --replicas 3 -p 80:80 nginx
docker service ls
docker service ps nginx
docker service scale nginx=5
docker service rm nginx
docker service logs -f nginx
docker service update --image nginx:1.21 nginx
```

### 1.4 Stack 部署
```yaml
version: '3.8'
services:
  web:
    image: nginx
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
    ports:
      - "80:80"
```
```bash
docker stack deploy -c docker-compose.yml myapp
docker stack ls
docker stack ps myapp
docker stack rm myapp
```

## 2. Docker 安全

### 2.1 安全基线
- 使用非 root 用户运行容器
- 镜像签名验证
- 限制容器资源
- 只读根文件系统
- 禁用特权模式

### 2.2 安全配置
```bash
# 资源限制
docker run --memory="512m" --cpus="0.5" nginx

# 只读文件系统
docker run --read-only nginx

# 安全选项
docker run --security-opt=no-new-privileges nginx
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx
```

## 3. Docker 监控与日志

### 3.1 监控命令
```bash
docker stats                  # 实时资源监控
docker top <container>        # 进程查看
docker events                 # 事件流
docker system df              # 磁盘使用
docker system prune           # 清理
```

### 3.2 日志管理
```bash
# 配置日志驱动
docker run --log-driver json-file --log-opt max-size=10m nginx

# 查看日志
docker logs -f --tail 100 <container>
```

## 4. Docker Registry

### 4.1 私有仓库
```bash
# 运行 Registry
docker run -d -p 5000:5000 --name registry \
  -v /data/registry:/var/lib/registry registry:2

# 推送镜像
docker tag myapp:1.0 localhost:5000/myapp:1.0
docker push localhost:5000/myapp:1.0
```

### 4.2 Harbor
- 企业级 Registry
- 权限管理
- 镜像复制
- 漏洞扫描
- Webhook
- AD/LDAP 集成

## 5. 容器编排对比

| 特性 | Swarm | Kubernetes |
|------|-------|------------|
| 安装复杂度 | 简单 | 复杂 |
| 功能丰富度 | 基础 | 丰富 |
| 社区生态 | 小 | 大 |
| 学习曲线 | 低 | 高 |
| 资源消耗 | 低 | 高 |
| 适用场景 | 小规模 | 大规模 |

## 6. 生产最佳实践

- 使用 CI/CD 自动构建镜像
- 标签使用语义化版本
- 实施镜像安全扫描
- 日志集中管理（ELK）
- 监控告警（Prometheus + Grafana）
- 定期备份数据卷
- 滚动更新策略
- 健康检查与自动恢复
