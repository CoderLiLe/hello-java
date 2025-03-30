# mysql使用innodb引擎，请简述mysql索引的最左前缀如何优化orderby语句

## 关键点：

1. 如果排序字段不在索引列上，filesort有两种算法： mysql就要启动双路排序和单路排序
2. **无过滤不索引**
3. order by非最左 filesort
4. 顺序错 filesort
5. 方向反  filesort
6. 记不住多动手做实验，熟练使用explain，必要时使用optimizer_trace
7. 更多参考尚硅谷mysql课程



## **答案：**
1. 首先要对sql进行分析检查必要的查询字段，过滤字段，排序字段是否按顺序创建好了索引
2. 如果查询字段不再索引中可能会产生回表操作会导致filesort，降低性能
3. 一定要有过滤字段不然不能使用索引
4. 排序字段和索引顺序不一致会导致filesort，降低性能
5. 多个字段排序时如果方向不一致也会导致filesort，降低性能
6. 使用explain观察查询类型和索引利用情况
7. 尽可能减少不必要的filesort

## **实验准备**：向表中插入50w条数据
在做优化之前，要准备大量数据。接下来创建两张表，并往员工表里插入50W数据，部门表中插入1W条数据。

怎么快速插入50w条数据呢？ `存储过程`

怎么保证插入的数据不重复？`函数`

**部门表：**

- id：自增长
- deptName：随机字符串，允许重复
- address：随机字符串，允许重复
- CEO：1-50w之间的任意数字

**员工表：**

- id：自增长
- empno：可以使用随机数字，或者`从1开始的自增数字`，不允许重复
- name：随机生成，允许姓名重复
- age：区间随机数
- deptId：1-1w之间随机数

**总结：**需要产生随机字符串和区间随机数的函数。

### **创建表**

```sql
CREATE TABLE `dept` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`deptName` VARCHAR(30) DEFAULT NULL,
	`address` VARCHAR(40) DEFAULT NULL,
	ceo INT NULL ,
	PRIMARY KEY (`id`)
) ENGINE=INNODB AUTO_INCREMENT=1;

CREATE TABLE `emp` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`empno` INT NOT NULL ,
	`name` VARCHAR(20) DEFAULT NULL,
	`age` INT(3) DEFAULT NULL,
	`deptId` INT(11) DEFAULT NULL,
	PRIMARY KEY (`id`)
	#CONSTRAINT `fk_dept_id` FOREIGN KEY (`deptId`) REFERENCES `t_dept` (`id`)
) ENGINE=INNODB AUTO_INCREMENT=1;
```

### 创建函数

```sql
-- 查看mysql是否允许创建函数：
SHOW VARIABLES LIKE 'log_bin_trust_function_creators';
-- 命令开启：允许创建函数设置：（global-所有session都生效）
SET GLOBAL log_bin_trust_function_creators=1; 
```



```sql
-- 随机产生字符串
DELIMITER $$
CREATE FUNCTION rand_string(n INT) RETURNS VARCHAR(255)
BEGIN    
	DECLARE chars_str VARCHAR(100) DEFAULT 'abcdefghijklmnopqrstuvwxyzABCDEFJHIJKLMNOPQRSTUVWXYZ';
	DECLARE return_str VARCHAR(255) DEFAULT '';
	DECLARE i INT DEFAULT 0;
	WHILE i < n DO  
		SET return_str =CONCAT(return_str,SUBSTRING(chars_str,FLOOR(1+RAND()*52),1));  
		SET i = i + 1;
	END WHILE;
	RETURN return_str;
END $$

-- 假如要删除
-- drop function rand_string;
```

```sql
-- 用于随机产生区间数字
DELIMITER $$
CREATE FUNCTION rand_num (from_num INT ,to_num INT) RETURNS INT(11)
BEGIN   
 DECLARE i INT DEFAULT 0;  
 SET i = FLOOR(from_num +RAND()*(to_num -from_num+1));
RETURN i;  
END$$

-- 假如要删除
-- drop function rand_num;
```

### 创建存储过程

```sql
-- 插入员工数据
DELIMITER $$
CREATE PROCEDURE  insert_emp(START INT, max_num INT)
BEGIN  
	DECLARE i INT DEFAULT 0;   
	#set autocommit =0 把autocommit设置成0  
	SET autocommit = 0;    
	REPEAT  
		SET i = i + 1;  
		INSERT INTO emp (empno, NAME, age, deptid ) VALUES ((START+i) ,rand_string(6), rand_num(30,50), rand_num(1,10000));  
		UNTIL i = max_num  
	END REPEAT;  
	COMMIT;  
END$$
 
-- 删除
-- DELIMITER ;
-- drop PROCEDURE insert_emp;
```

```sql
-- 插入部门数据
DELIMITER $$
CREATE PROCEDURE insert_dept(max_num INT)
BEGIN  
	DECLARE i INT DEFAULT 0;   
	SET autocommit = 0;    
	REPEAT  
		SET i = i + 1;  
		INSERT INTO dept ( deptname,address,ceo ) VALUES (rand_string(8),rand_string(10),rand_num(1,500000));  
		UNTIL i = max_num  
	END REPEAT;  
	COMMIT;  
END$$
 
-- 删除
-- DELIMITER ;
-- drop PROCEDURE insert_dept;
```

### 调用存储过程

```sql
-- 执行存储过程，往dept表添加1万条数据
CALL insert_dept(10000); 

-- 执行存储过程，往emp表添加50万条数据，编号从100000开始
CALL insert_emp(100000,500000); 
```

### 批量删除表索引

```sql
-- 批量删除某个表上的所有索引
DELIMITER $$
CREATE PROCEDURE `proc_drop_index`(dbname VARCHAR(200),tablename VARCHAR(200))
BEGIN
	DECLARE done INT DEFAULT 0;
	DECLARE ct INT DEFAULT 0;
	DECLARE _index VARCHAR(200) DEFAULT '';
	DECLARE _cur CURSOR FOR SELECT index_name FROM information_schema.STATISTICS WHERE table_schema=dbname AND table_name=tablename AND seq_in_index=1 AND index_name <>'PRIMARY'  ;
	DECLARE CONTINUE HANDLER FOR NOT FOUND set done=2 ;      
	OPEN _cur;
		FETCH _cur INTO _index;
		WHILE  _index<>'' DO 
			SET @str = CONCAT("drop index ",_index," on ",tablename ); 
			PREPARE sql_str FROM @str ;
			EXECUTE sql_str;
			DEALLOCATE PREPARE sql_str;
			SET _index=''; 
			FETCH _cur INTO _index; 
		END WHILE;
	CLOSE _cur;
END$$
```

```sql
-- 执行批量删除：dbname 库名称, tablename 表名称
CALL proc_drop_index("dbname","tablename"); 
```

## 最左前缀法则示例

假设index(a,b,c)

| Where语句                                                  | 索引是否被使用                                               |
| ---------------------------------------------------------- | ------------------------------------------------------------ |
| where a = 3                                                | Y,使用到a                                                    |
| where a =  3 and b = 5                                     | Y,使用到a，b                                                 |
| where a =  3 and b = 5 and c = 4                           | Y,使用到a,b,c                                                |
| where b =  3 或者 where b = 3 and c =  4 或者 where c =  4 | N                                                            |
| where a =  3 and c = 5                                     | 使用到a， 但是c不可以，b中间断了                             |
| where a =  3 and b > 4 and c = 5                           | 使用到a和b， c不能用在范围之后，b断了                        |
| where a is  null and b is not null                         | is null 支持索引  但是is not null 不支持,所以 a 可以使用索引,但是 b不一定能用上索引（8.0） |
| where a  <> 3                                              | 不能使用索引                                                 |
| where  abs(a) =3                                           | 不能使用 索引                                                |
| where a =  3 and b like 'kk%' and c = 4                    | Y,使用到a,b,c                                                |
| where a =  3 and b like '%kk' and c = 4                    | Y,只用到a                                                    |
| where a =  3 and b like '%kk%' and c = 4                   | Y,只用到a                                                    |
| where a =  3 and b like 'k%kk%' and c =  4                 | Y,使用到a,b,c                                                |

##  一般性建议

Ø 对于单键索引，尽量选择过滤性更好的索引（例如：手机号，邮件，身份证）

Ø 在选择组合索引的时候，过滤性最好的字段在索引字段顺序中，位置越靠前越好。

Ø 选择组合索引时，尽量包含where中更多字段的索引

Ø 组合索引出现范围查询时，尽量把这个字段放在索引次序的最后面

Ø 尽量避免造成索引失效的情况

## 实验

删除索引

```
 drop index idx_age_name_deptid on emp;
```



创建索引

```
CREATE INDEX idx_age_deptid_name ON emp (age,deptid,NAME);
```

#### 

**无过滤不索引**

```

EXPLAIN SELECT * FROM emp ORDER BY age,deptid; 
EXPLAIN SELECT * FROM emp ORDER BY age,deptid LIMIT 10; 

增加过滤条件，使用上索引了。
EXPLAIN SELECT age FROM emp where age>1000 ORDER BY age,deptid,name;

```

**查询条件与筛选条件**

```
const查询排序后回表操作，不会filesort
EXPLAIN SELECT * FROM emp WHERE age=45 ORDER BY age,deptid,NAME; 

range查询，Using index condition 没有完全使用索引
EXPLAIN SELECT * FROM emp WHERE age>45 ORDER BY age,deptid,NAME;
range查询，Using where; Using index 完全使用索引
EXPLAIN SELECT age FROM emp WHERE age>45 ORDER BY age,deptid,NAME;
```

**顺序错 filesort**

```
正常情况
EXPLAIN SELECT age FROM emp WHERE age>45 ORDER BY age,deptid,NAME;
order by顺序变化会导致filesort
EXPLAIN SELECT age FROM emp WHERE age>45 ORDER BY deptid,age,NAME;

```

**order by非最左 filesort**

```
EXPLAIN SELECT age FROM emp WHERE age>45 ORDER BY deptid,NAME;
```

**方向反 必排序**

```
8.0为Backward index scan 倒序索引
EXPLAIN SELECT age FROM emp WHERE age>45 ORDER BY age desc,deptid desc,NAME desc

方向反 产生filesort
EXPLAIN SELECT age FROM emp WHERE age>45 ORDER BY age desc,deptid desc,NAME asc;

```