# 高级查询和连接
## [180.连续出现的数字](https://leetcode.cn/problems/consecutive-numbers/description/?envType=study-plan-v2&envId=sql-free-50)

```sql
SELECT DISTINCT
    l1.Num AS ConsecutiveNums
FROM
    Logs l1,
    Logs l2,
    Logs l3
WHERE
    l1.Id = l2.Id - 1
    AND l2.Id = l3.Id - 1
    AND l1.Num = l2.Num
    AND l2.Num = l3.Num
;
```

```sql
SELECT DISTINCT Num ConsecutiveNums
FROM(
SELECT *,
      ROW_NUMBER() OVER (PARTITION BY Num ORDER BY Id) rownum,
      ROW_NUMBER() OVER (ORDER BY Id) id2
FROM LOGS
) t
GROUP BY (id2-rownum), Num 
HAVING COUNT(*)>=3;
```

```sql
select 
    distinct Num as ConsecutiveNums 
from  
    (select Num,
            if(@pre=Num,@count := @count+1,@count := 1) as nums,
            @pre:=Num
        from Logs as l ,
            (select @pre:= null,@count:=1) as pc
      ) as n
where nums >=3;
```

```sql
select distinct Num as ConsecutiveNums from (
    select Num, count(1) as SerialCount from
    (
        select Id, Num, 
        row_number() over(order by id) - row_number() over(partition by Num order by Id) as SerialNumberSubGroup
        from Logs
    ) as Sub
    group by Num, SerialNumberSubGroup
    having count(1) >= 3
) as Result
```