# Redis数据安全性分析

# 一、Redis性能压测脚本介绍

&#x9;Redis的所有数据是保存在内存当中的，得益于内存高效的读写性能，Redis的性能是非常强悍的。但是，内存的缺点是断电即丢失，所以，在实际项目中，Redis一旦需要保存一些重要的数据，就不可能完全使用内存保存数据。因此，在真实项目中要使用Redis，一定需要针对应用场景，对Redis的性能进行估算，从而在数据安全性与读写性能之间找到一个平衡点。

&#x9;Redis提供了压测脚本redis-benchmark，可以对Redis进行快速的基准测试。

```shell
# 20个线程，100W个请求，测试redis的set指令(写数据)
redis-benchmark -a 123qweasd -t set -n 1000000 -c 20
	...
Summary:
  throughput summary: 116536.53 requests per second   ##平均每秒11W次写操作。
  latency summary (msec):
          avg       min       p50       p95       p99       max
        0.111     0.032     0.111     0.167     0.215     3.199
```

> redis-benchmark更多参数，使用redis-benchmark --help指令查看

&#x9;后续逐步调整Redis的各种部署架构后，建议大家自行多进行几次对比测试。