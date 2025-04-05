# 排序和分组

## [619.只出现一次的数字](https://leetcode.cn/problems/biggest-single-number/description)

![](./assets/619.png)

* 使用聚合函数对空值进行处理时，SUM/AVG/MAX/MIN都会返回null值
* 使用ifnull对空值进行处理。(实际上并不是ifnull起作用)),输出的仍然是空值
* select语句中写入空值，直接运行select语句，我们将会得到null值
* limit语句不会输出新null值（除非表格中本身存在null值），因为limit语句对表格只是进行截取
* .where语句所带来的限制条件不会输出新的null值（除非表格中本身存在null值），同理having也是一样

**总结：**
> **（1）可以使用聚合函数进行空值null值的转换，具体的聚合函数包括SUM/AVG/MAX/MIN**
> 
> **（2）可以使用select语句进行转换，但空值应直接写在select中而非from中**
> 
> **（3）imit语句无法出现新的null值**
> 
> **（4）where和having同样无法出现新的null值**

```sql
select Max(num) as num from (
    select num from MyNumbers group by num having count(*) = 1
) t;
```
```sql
select
(
    select num from MyNumbers group by num having count(num) = 1 order by num desc limit 0, 1
) num;
```