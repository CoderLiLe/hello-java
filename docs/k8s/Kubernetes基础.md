# Kubernetes（K8s）基础

## 1. Kubernetes 概述

Kubernetes 是 Google 开源的容器编排平台，用于自动化部署、扩展和管理容器化应用。

### 1.1 核心能力
- **服务发现与负载均衡**
- **存储编排**
- **自动部署与回滚**
- **自动弹性伸缩**
- **自我修复**
- **配置与密钥管理**

### 1.2 架构
```
Control Plane (Master)
├── kube-apiserver      # API 入口
├── kube-controller-manager  # 控制器
├── kube-scheduler      # 调度器
└── etcd               # 分布式存储

Node (Worker)
├── kubelet            # 节点代理
├── kube-proxy         # 网络代理
└── Container Runtime  # 容器运行时
```

## 2. 核心资源对象

### 2.1 Pod
最小的部署单元，包含一个或多个容器。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

### 2.2 Deployment
声明式更新 Pod 和 ReplicaSet。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
---  # 滚动更新策略
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

### 2.3 Service
提供 Pod 的稳定网络访问入口。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP  # ClusterIP | NodePort | LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080  # NodePort 时指定
```

### 2.4 ConfigMap & Secret
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  application.yml: |
    server:
      port: 8080
    spring:
      datasource:
        url: jdbc:mysql://db:3306/app

---
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: app-secret
data:
  db-password: cm9vdA==  # base64
```

### 2.5 Ingress
HTTP/HTTPS 路由规则。

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8080
```

## 3. 存储

### 3.1 Volume 类型
- **emptyDir**：临时存储
- **hostPath**：宿主机目录
- **PV/PVC**：持久化存储
- **ConfigMap/Secret**：配置注入

### 3.2 PV 与 PVC
```yaml
# PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  nfs:
    path: /data
    server: nfs-server

# PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```

### 3.3 StorageClass
动态创建 PV：
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  fsType: ext4
```

## 4. 服务发现与负载均衡

### 4.1 DNS
```
<service>.<namespace>.svc.cluster.local
```

### 4.2 kube-proxy 模式
- **userspace**：用户态代理
- **iptables**：默认（使用 iptables NAT）
- **IPVS**：高性能（支持更多调度算法）

## 5. 集群管理

### 5.1 Node 管理
```bash
kubectl get nodes
kubectl describe node <node>
kubectl cordon <node>          # 节点维护（禁止调度）
kubectl drain <node>           # 排空节点
kubectl uncordon <node>        # 恢复调度
kubectl taint nodes <node> key=value:NoSchedule
```

### 5.2 命名空间
```bash
kubectl create namespace dev
kubectl get namespaces
```

### 5.3 资源配额
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "10"
```

## 6. 监控与日志

### 6.1 监控方案
- **Metrics Server**：资源指标
- **Prometheus**：指标采集
- **Grafana**：可视化

### 6.2 日志方案
- **EFK/ELK**：Elasticsearch + Fluentd/Filebeat + Kibana
- **Loki**：轻量级日志方案

## 7. Helm

K8s 包管理器——Chart 是 Helm 的软件包格式。

```yaml
# Chart.yaml
apiVersion: v2
name: my-app
version: 1.0.0
```

```bash
# 常用操作
helm repo add bitnami https://charts.bitnami.com/bitnami
helm search repo nginx
helm install my-nginx bitnami/nginx
helm upgrade my-nginx bitnami/nginx
helm rollback my-nginx 1
helm list
helm uninstall my-nginx
```

## 8. 网络方案

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| Flannel | 简单、VXLAN | 小规模 |
| Calico | BGP、NetworkPolicy | 大规模、安全 |
| Cilium | eBPF 技术 | 高性能 |
| Weave | 简单部署 | 快速搭建 |

## 9. 生产最佳实践

- **资源限制**：为容器设置 requests/limits
- **健康检查**：配置 liveness/readiness probe
- **优雅关闭**：配置 preStop hook
- **Pod 反亲和**：分散 Pod 到不同节点
- **PodDisruptionBudget**：保证可用 Pod 数量
- **安全上下文**：禁止特权容器
- **HPA**：配置自动扩缩容
- **RBAC**：最小权限原则
- **etcd 备份**：定期备份集群状态
