# 聚合函数

## [550.游戏玩法分析 IV](https://leetcode.cn/problems/game-play-analysis-iv/description/)

### 方法一
算法：

1、求出所有用户首次登录的第二天的时间。方法是查询出 Activity 表中每个用户的第一天时间并加上 1，将此表命名为 Expected。

2、从 Activity 表中查询 event_date 与 Expected.sencond_date 重叠的部分，注意此判定要限定在用户相同的前提下。这部分用户即为在首次登录后第二天也登录了的用户。将此表命名为 Result

3、得到 Result 表中用户的数量，以及 Activity 表中用户的数量，相除并保留两位小数即可

```sql
select IFNULL(round(count(distinct(Result.player_id)) / count(distinct(Activity.player_id)), 2), 0) as fraction
from (
  select Activity.player_id as player_id
  from (
    select player_id, DATE_ADD(MIN(event_date), INTERVAL 1 DAY) as second_date
    from Activity
    group by player_id
  ) as Expected, Activity
  where Activity.event_date = Expected.second_date and Activity.player_id = Expected.player_id
) as Result, Activity;
```

### 方法二
算法：

先过滤出每个用户的首次登陆日期，然后左关联，筛选次日存在的记录的比例

在avg的计算中加上is not null就变成了计算布尔值，如果不加就变成计算日期的平均值

```sql
select round(avg(a.event_date is not null), 2) fraction
from (
    select player_id, min(event_date) as login from Activity group by player_id
) p left join Activity a 
on p.player_id = a.player_id and datediff(a.event_date, p.login) = 1;
```