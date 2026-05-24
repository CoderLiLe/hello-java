# LVS + Keepalived 高可用部署实战

## 1. LVS 概述

LVS（Linux Virtual Server）是 Linux 内核内置的负载均衡器，工作在第 4 层（传输层）。

### 1.1 工作模式
| 模式 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| NAT | 修改目标 IP | 后端任意 OS | 瓶颈在 Director |
| DR | 修改 MAC 地址 | 高性能 | 需 lo 配置 VIP |
| TUN | IP 隧道 | 跨网段 | 配置复杂 |
| FULLNAT | 修改源/目标 IP | 无需 lo 配置 | 性能略低 |

### 1.2 调度算法
| 算法 | 说明 |
|------|------|
| rr | 轮询 |
| wrr | 加权轮询 |
| lc | 最少连接 |
| wlc | 加权最少连接（默认） |
| lblc | 基于局部的最少连接 |
| dh | 目标地址哈希 |
| sh | 源地址哈希 |

## 2. DR 模式部署

### 2.1 架构
```
VIP: 192.168.1.100
        |
    Director (LVS)
        |
    RS1 (192.168.1.1)
    RS2 (192.168.1.2)
    RS3 (192.168.1.3)
```

### 2.2 Director 配置
```bash
# 配置 VIP
ifconfig eth0:0 192.168.1.100 netmask 255.255.255.255 up

# 添加虚拟服务器
ipvsadm -A -t 192.168.1.100:80 -s wrr

# 添加真实服务器（DR 模式）
ipvsadm -a -t 192.168.1.100:80 -r 192.168.1.1 -g -w 1
ipvsadm -a -t 192.168.1.100:80 -r 192.168.1.2 -g -w 2
ipvsadm -a -t 192.168.1.100:80 -r 192.168.1.3 -g -w 1

# 查看
ipvsadm -Ln
```

### 2.3 Real Server 配置
```bash
# 抑制 ARP 响应
echo 1 > /proc/sys/net/ipv4/conf/lo/arp_ignore
echo 2 > /proc/sys/net/ipv4/conf/lo/arp_announce

# lo 配置 VIP
ifconfig lo:0 192.168.1.100 netmask 255.255.255.255 up
```

## 3. Keepalived

### 3.1 配置
```conf
global_defs {
    router_id LVS_MASTER
}

vrrp_instance VI_1 {
    state MASTER              # BACKUP 为备
    interface eth0
    virtual_router_id 51      # 同一组 VRID 一致
    priority 100              # 主 > 备
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1234
    }
    virtual_ipaddress {
        192.168.1.100
    }
}

virtual_server 192.168.1.100 80 {
    delay_loop 6
    lb_algo wrr
    lb_kind DR
    protocol TCP
    
    real_server 192.168.1.1 80 {
        weight 1
        HTTP_GET {
            url { path /health }
            connect_timeout 3
        }
    }
    real_server 192.168.1.2 80 {
        weight 2
        HTTP_GET {
            url { path /health }
            connect_timeout 3
        }
    }
}
```

### 3.2 验证
```bash
# 查看 VIP
ip addr show

# 查看 Keepalived 状态
systemctl status keepalived
journalctl -u keepalived -f

# 故障转移测试
# 1. 停止 Master 的 keepalived
# 2. 检查 VIP 是否飘移到 Backup
# 3. 验证服务是否正常
```
