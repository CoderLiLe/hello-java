# 服务网格 ServiceMesh 实战

## 1. ServiceMesh 概述

服务网格（Service Mesh）是处理服务间通信的基础设施层，通过 Sidecar 代理实现流量管理、可观测性和安全通信。

### 1.1 架构演进
```
单体 -> SOA -> 微服务 -> ServiceMesh -> Serverless
```

### 1.2 Sidecar 模式
```
[服务A] <-> [Sidecar Envoy] <---> [Sidecar Envoy] <-> [服务B]
                     \               /
                   Control Plane (Istiod)
```

### 1.3 核心功能
- **流量管理**：路由、分流、限流、熔断
- **安全**：mTLS、RBAC
- **可观测性**：指标、日志、链路追踪
- **策略**：配额、访问控制

## 2. Istio 架构

### 2.1 组件
- **Envoy**：Sidecar 代理
- **Istiod**：控制面（整合 Pilot、Citadel、Galley）
- **Ingress/Egress Gateway**：南北向流量管理

### 2.2 部署
```bash
# 下载 Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.20.0

# 安装
istioctl install --set profile=demo -y

# 启用 Sidecar 注入
kubectl label namespace default istio-injection=enabled
```

## 3. 流量管理

### 3.1 VirtualService
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
```

### 3.2 DestinationRule
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    loadBalancer:
      simple: RANDOM
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### 3.3 灰度发布
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: canary
spec:
  hosts:
  - myapp
  http:
  - route:
    - destination:
        host: myapp
        subset: v1
      weight: 90
    - destination:
        host: myapp
        subset: v2
      weight: 10
```

## 4. 安全

### 4.1 mTLS
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT  # PERMISSIVE | STRICT
```

### 4.2 授权策略
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: httpbin
spec:
  selector:
    matchLabels:
      app: httpbin
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/sleep"]
    to:
    - operation:
        methods: ["GET"]
```

## 5. 可观测性

- **Prometheus**：指标采集
- **Grafana**：可视化
- **Kiali**：服务拓扑
- **Jaeger**：分布式追踪
- **Grafana Loki**：日志

## 6. 生产实践

- Sidecar 资源限制（CPU/Memory）
- 控制面高可用（多副本）
- 逐步启用（namespace 级别注入）
- 混合场景（部分服务网格化）
- 性能调优（Envoy 配置）
- 灰度升级控制面
