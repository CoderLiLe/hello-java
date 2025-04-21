# 20-Management UI

## 1、Overview选项卡

### ①Totals

#### [1]单一实例

![image-20240112152422111](assets/20/image-20240112152422111.png)

#### [2]集群

![image-20240112160136024](assets/20/image-20240112160136024.png)

### ②Global Counts

![image-20240112152606590](assets/20/image-20240112152606590.png)

### ③Nodes

#### [1]外部摘要信息

- 单一实例

![image-20240112152720220](assets/20/image-20240112152720220.png)

- 集群

![image-20240112160241426](assets/20/image-20240112160241426.png)

#### [2]Overview

- 单一实例

![image-20240112152825577](assets/20/image-20240112152825577.png)

- 集群中某个实例

![image-20240112160355480](assets/20/image-20240112160355480.png)

#### [3]Process statistics

![image-20240112153022257](assets/20/image-20240112153022257.png)

#### [4]Persistence statistics

![image-20240112153547282](assets/20/image-20240112153547282.png)



#### [5]I/O statistics

![image-20240112153717380](assets/20/image-20240112153717380.png)


#### [6]Churn statistics

![image-20240112153900611](assets/20/image-20240112153900611.png)

#### [7]Cluster links

- 单一实例

![image-20240112170315275](assets/20/image-20240112170315275.png)



- 集群

![image-20240112170337626](assets/20/image-20240112170337626.png)

#### [8]Memory Details

![image-20240112170415395](assets/20/image-20240112170415395.png)

#### [9]Binary references

![image-20240112170529715](assets/20/image-20240112170529715.png)

#### [10]Advanced

![image-20240112170626788](assets/20/image-20240112170626788.png)

![image-20240112170648345](assets/20/image-20240112170648345.png)

![image-20240112170726349](assets/20/image-20240112170726349.png)

![image-20240112170739481](assets/20/image-20240112170739481.png)

![image-20240112170840162](assets/20/image-20240112170840162.png)

![image-20240112170754254](assets/20/image-20240112170754254.png)

### ④Churn statistics

![image-20240112172429334](assets/20/image-20240112172429334.png)

### ⑤Ports and contexts

![image-20240112172519704](assets/20/image-20240112172519704.png)

### ⑥Export definitions

![image-20240112173038905](assets/20/image-20240112173038905.png)

```json
{
    "rabbit_version":"3.12.8",
    "rabbitmq_version":"3.12.8",
    "product_name":"RabbitMQ",
    "product_version":"3.12.8",
    "users":[
        {
            "name":"guest",
            "password_hash":"E76Z2NmF08kv9ovR2AuNS4QRY3XDUm3W6f2Aeok9v3Qb0Vgs",
            "hashing_algorithm":"rabbit_password_hashing_sha256",
            "tags":[
                "administrator"
            ],
            "limits":{

            }
        }
    ],
    "vhosts":[
        {
            "name":"/"
        }
    ],
    "permissions":[
        {
            "user":"guest",
            "vhost":"/",
            "configure":".*",
            "write":".*",
            "read":".*"
        }
    ],
    "topic_permissions":[

    ],
    "parameters":[

    ],
    "global_parameters":[
        {
            "name":"internal_cluster_id",
            "value":"rabbitmq-cluster-id-n3E1YptmxZYUQ_03R6vruA"
        }
    ],
    "policies":[

    ],
    "queues":[
        {
            "name":"jmeterQueue",
            "vhost":"/",
            "durable":true,
            "auto_delete":false,
            "arguments":{

            }
        },
        {
            "name":"queue.quorum.test",
            "vhost":"/",
            "durable":true,
            "auto_delete":false,
            "arguments":{
                "x-queue-type":"quorum"
            }
        },
        {
            "name":"atguigu.queue.test",
            "vhost":"/",
            "durable":true,
            "auto_delete":false,
            "arguments":{

            }
        }
    ],
    "exchanges":[
        {
            "name":"exchange.quorum.test",
            "vhost":"/",
            "type":"direct",
            "durable":true,
            "auto_delete":false,
            "internal":false,
            "arguments":{

            }
        },
        {
            "name":"exchange.cluster.test",
            "vhost":"/",
            "type":"direct",
            "durable":true,
            "auto_delete":false,
            "internal":false,
            "arguments":{

            }
        },
        {
            "name":"atguigu-exchange-test",
            "vhost":"/",
            "type":"direct",
            "durable":true,
            "auto_delete":false,
            "internal":false,
            "arguments":{

            }
        },
        {
            "name":"jmeterExchange",
            "vhost":"/",
            "type":"direct",
            "durable":true,
            "auto_delete":false,
            "internal":false,
            "arguments":{

            }
        }
    ],
    "bindings":[
        {
            "source":"atguigu-exchange-test",
            "vhost":"/",
            "destination":"atguigu.queue.test",
            "destination_type":"queue",
            "routing_key":"atguigu.routing.key.test",
            "arguments":{

            }
        },
        {
            "source":"exchange.quorum.test",
            "vhost":"/",
            "destination":"queue.quorum.test",
            "destination_type":"queue",
            "routing_key":"routing.key.quorum.test",
            "arguments":{

            }
        },
        {
            "source":"jmeterExchange",
            "vhost":"/",
            "destination":"jmeterQueue",
            "destination_type":"queue",
            "routing_key":"jmeterRoutingKey",
            "arguments":{

            }
        }
    ]
}
```

### ⑦Import definitions

![image-20240112173214186](assets/20/image-20240112173214186.png)

## 2、Connections选项卡

### ①All connections

![image-20240112173612481](assets/20/image-20240112173612481.png)

### ②Connection细节

![image-20240112173722254](assets/20/image-20240112173722254.png)

![image-20240112173748337](assets/20/image-20240112173748337.png)

![image-20240113103809357](assets/20/image-20240113103809357.png)

![image-20240113103838362](assets/20/image-20240113103838362.png)

## 3、Channel选项卡

![image-20240113104437616](assets/20/image-20240113104437616.png)

![image-20240113104506953](assets/20/image-20240113104506953.png)

![image-20240113104540135](assets/20/image-20240113104540135.png)

## 4、Exchanges选项卡

![image-20240113104614885](assets/20/image-20240113104614885.png)

![image-20240113110113544](assets/20/image-20240113110113544.png)

## 5、Queues And Streams选项卡

![image-20240113110700362](assets/20/image-20240113110700362.png)

![image-20240113110640019](assets/20/image-20240113110640019.png)