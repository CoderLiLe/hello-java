# 多态

- [1.多态概念](#1多态概念)
- [2. 向上转型](#2-向上转型)
  - [2.1 情况1](#21-情况1)
  - [2.2 情况2](#22-情况2)
  - [2.3 情况3](#23-情况3)
- [3. 向下转型](#3-向下转型)
- [4. 多态补充](#4-多态补充)
- [5. 多态实现原理](#5-多态实现原理)
- [6. java命令](#6-java命令)


## 1.多态概念

> 多态：
>
> 同一个事物，因为环境不同，产生不同的效果
>
> 同一个引用类型，使用不同的实例而执行不同操作(父类引用指向子类对象)

## 2. 向上转型

> 父类引用指向子类对象属于向上转型，此时通过父类引用，
>
> 可以访问的是子类重写或者继承父类的方法 不能访问子类独有的方法

### 2.1 情况1

> 1.父类作为形参，子类作为实参

```java
package com.atguigu.test4;

/**
 * @author WHD
 * @description TODO
 * @date 2023/8/7 14:18
 *  宠物父类：
 *  父类中书写各个子类共有的属性 和 方法
 *  子类中书写独有的属性 和 方法
 */
public class Pet {
    protected String name;
    protected int health;
    protected int love;

    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public int getHealth() {
        return health;
    }
    public void setHealth(int health) {
        this.health = health;
    }
    public int getLove() {
        return love;
    }
    public void setLove(int love) {
        this.love = love;
    }


    public void print(){
        System.out.println("宠物的名字是：" + name);
        System.out.println("宠物的健康值是：" + health);
        System.out.println("宠物的亲密值是：" + love);
    }

    /**
     *  疗养 (看病) 方法
     */
    public void cure(){
        System.out.println("宠物看病");
    }

    public Pet(String name, int health, int love) {
        this.name = name;
        this.health = health;
        this.love = love;
    }

    public Pet() {
    }
}

```

```java
/**
 *  狗狗类：
 *      名字 健康值 亲密值 品种
 *      打印狗狗信息
 *      无参构造
 */
public class Dog extends Pet {
    private String strain;
    public String getStrain() {
        return strain;
    }
    public void setStrain(String strain) {
        this.strain = strain;
    }

    @Override
    public void print(){
        super.print();
        System.out.println("狗狗的品种是：" + strain);
    }

    @Override
    public void cure() {
        System.out.println("狗狗看病，吃药，吃骨头，健康值恢复");
        this.setHealth(100);
    }

    public Dog() {
    }

    public Dog(String name, int health, int love, String strain) {
        super(name, health, love);
        this.strain = strain;
    }
}

```

```java
/**
 *  企鹅类：
 *      姓名 健康值 亲密值 性别
 *      打印企鹅信息
 *      无参构造
 */
public class Penguin extends Pet {
    private char sex;
    public char getSex() {
        return sex;
    }
    public void setSex(char sex) {
        this.sex = sex;
    }


    public void print(){
        super.print();
        System.out.println("企鹅的性别是：" + sex);
    }

    @Override
    public void cure() {
        System.out.println("企鹅看病，打针，吃小鱼，健康值恢复");
        this.setHealth(100);
    }

    public Penguin(String name, int health, int love, char sex) {
        super(name, health, love);
        this.sex = sex;
    }

    public Penguin() {
    }
}

```

```java
/**
 *  主人类
 *      1.带宠物去看病
 */
public class Master {

    public void toHospitalWithDog(Dog dog){
        dog.cure();
    }

    public void toHospitalWithPenguin(Penguin penguin){
        penguin.cure();
    }


    // 问题分析：以上代码编写了两个方法分别用于给不同的宠物子类看病 这种方式不符合开闭原则
    // 如果后续有更多的宠物子类 那么还需要编写更多的方法来实现
    // 解决方案：使用多态解决 我们应该编写一个方法 实现给所有的宠物子类看病
    // 开闭原则 ： 程序应该对扩展开放 对修改源代码关闭


    public void toHospitalWithPet(Pet pet){ // Pet pet = new Dog(); = new Penguin();
        pet.cure();
    }
}

```

### 2.2 情况2

> 2.父类作为声明返回值，实际返回值为子类类型

```java
/**
 *  主人类
 *      1.带宠物去看病
 *      2.抽奖送宠物
 *          一等奖 送企鹅一只
 *          二等奖 送狗狗一只
 *          三等奖 送猫咪一只
 *          幸运奖 送成年东北虎一只
 */
public class Master {

    public void toHospitalWithPet(Pet pet){
        pet.cure();
    }

    public Penguin givePenguin(){
        Penguin penguin = new Penguin("小白", 100, 100, '雄');
        return penguin;
    }

    public Dog giveDog(){
        Dog dog = new Dog("大黄", 100, 100, "金毛");
        return dog;
    }

    /**
     *  以上两个方法可以使用这个方法替代  
     * @param str
     * @return
     */
    public Pet givePet(String str){
        if(str.equals("一等奖")){
            Penguin penguin = new Penguin("小白", 100, 100, '雄');
            return penguin;
        }else if(str.equals("二等奖")){
            Dog dog = new Dog("大黄", 100, 100, "金毛");
            return dog;
        }else if(str.equals("三等奖")){
            return new Cat();
        }else{
            return new Tiger();
        }
    }

}

```

```java
/**
 *  向上转型
 *        1.父类作为形参，子类作为实参
 *        2.父类作为声明返回值，实际返回值为子类类型
 *        3.父类类型的数组、集合，元素为子类类型
 */
public class TestPet {
    public static void main(String[] args) {
        Master master = new Master();
        Pet pet = master.givePet("一等奖");

        System.out.println("-------------------------------------------------");
    }
}

```



### 2.3 情况3

> 3.父类类型的数组、集合，元素为子类类型

```java
/**
 *  向上转型
 *        1.父类作为形参，子类作为实参
 *        2.父类作为声明返回值，实际返回值为子类类型
 *        3.父类类型的数组、集合，元素为子类类型
 */
public class TestPet {
    public static void main(String[] args) {
        Pet [] pets = new Pet[3];
        pets[0] = new Dog();
        pets[1] = new Penguin();
        pets[2] = new Cat();
    }
}      
```



## 3. 向下转型

> 父类引用指向子类对象属于向上转型，此时通过父类引用，
>
> 可以访问的是子类重写或者继承父类的方法
>
> 不能访问子类独有的方法 如需访问 则必须向下转型
>
>
> 向下转型：
>
> - 是将指向子类对象的父类引用 转换为 子类类型
> - 而不是 将指向父类对象的父类引用 转换为子类类型
>
> 总结：必须先向上转型 才可以向下转型  否则将出现类型转换异常  ClassCastException

> 因为异常会中断程序 所以 在实际开发中我们会使用`instanceof`关键字 在类型转换之前
>
> 进行判断 如果类型正确 则转换 不正确 则不转
>
> 用法： 对象名 instanceof 类名
>
> 表示判断左侧的对象是否属于右侧的类型 是则结果为true  不是则结果为false

```java
/**
 *  宠物父类：
 *  父类中书写各个子类共有的属性 和 方法
 *  子类中书写独有的属性 和 方法
 */
public class Pet {
    protected String name;
    protected int health;
    protected int love;

    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public int getHealth() {
        return health;
    }
    public void setHealth(int health) {
        this.health = health;
    }
    public int getLove() {
        return love;
    }
    public void setLove(int love) {
        this.love = love;
    }


    public void print(){
        System.out.println("宠物的名字是：" + name);
        System.out.println("宠物的健康值是：" + health);
        System.out.println("宠物的亲密值是：" + love);
    }

    /**
     *  疗养 (看病) 方法
     */
    public void cure(){
        System.out.println("宠物看病");
    }

    public Pet(String name, int health, int love) {
        this.name = name;
        this.health = health;
        this.love = love;
    }

    public Pet() {
    }
}

```

```java
/**
 *  狗狗类：
 *      名字 健康值 亲密值 品种
 *      打印狗狗信息
 *      无参构造
 */
public class Dog extends Pet {
    private String strain;
    public String getStrain() {
        return strain;
    }
    public void setStrain(String strain) {
        this.strain = strain;
    }

    @Override
    public void print(){
        super.print();
        System.out.println("狗狗的品种是：" + strain);
    }

    @Override
    public void cure() {
        System.out.println("狗狗看病，吃药，吃骨头，健康值恢复");
        this.setHealth(100);
    }

    public Dog() {
    }

    public Dog(String name, int health, int love, String strain) {
        super(name, health, love);
        this.strain = strain;
    }

    public void playFlyDisc(){
        System.out.println("狗狗玩飞盘");
    }
}

```

```java
/**
 *  企鹅类：
 *      姓名 健康值 亲密值 性别
 *      打印企鹅信息
 *      无参构造
 */
public class Penguin extends Pet {
    private char sex;
    public char getSex() {
        return sex;
    }
    public void setSex(char sex) {
        this.sex = sex;
    }


    public void print(){
        super.print();
        System.out.println("企鹅的性别是：" + sex);
    }

    @Override
    public void cure() {
        System.out.println("企鹅看病，打针，吃小鱼，健康值恢复");
        this.setHealth(100);
    }

    public Penguin(String name, int health, int love, char sex) {
        super(name, health, love);
        this.sex = sex;
    }

    public Penguin() {
    }
}

```

```java
package com.atguigu.test6;

/**
 *  父类引用指向子类对象属于向上转型，此时通过父类引用，
 *  可以访问的是子类重写或者继承父类的方法
 *  不能访问子类独有的方法 如需访问 则必须向下转型
 *
 * 向下转型：
 * 是将指向子类对象的父类引用 转换为 子类类型
 * 而不是 将指向父类对象的父类引用 转换为子类类型
 * 总结：必须先向上转型 才可以向下转型  否则将出现类型转换异常  ClassCastException
 *
 * 因为异常会中断程序 所以 在实际开发中我们会使用instanceof关键字 在类型转换之前
 * 进行判断 如果类型正确 则转换 不正确 则不转
 *  用法： 对象名 instanceof 类名
 *  表示判断左侧的对象是否属于右侧的类型
 */
public class TestPet {
    public static void main(String[] args) {
        Pet pet = new Dog();

        if(pet instanceof  Dog){
            Dog dog = (Dog)pet;

            dog.playFlyDisc();
        }


        System.out.println("-------------------------------------------");

        Pet p1 = new Pet();

        if(p1 instanceof  Dog){
            Dog dog1 = (Dog)p1;
            System.out.println("dog1 = " + dog1);
        }else{
            System.out.println("类型不匹配");
        }

        System.out.println("程序结束");
    }
}

```



## 4. 多态补充

> 我们观察重写Object类中的equals方法，父类中的方法实现形参为Object类型，所以我们重写形参也必须为Object类型，但是这样我们通过父类类型的形参就无法访问子类中的属性或者方法，所以我们在方法中必须向下转型。
>
> 父类写为Object类型，是为了子类的通用性。
>
> 子类在重写父类方法中又向下转型，是为了实用性。

```java
/**
 *  人类
 *  场景：如果现在有这样的"两个人" 这"两个人"名字和身份证号都相同 实际为同一个人
 *  那么在程序中就表现为两个对象 所以我们应该重写equals方法 将两个对象的比较结果为true
 *
 */
public class Person {
    private String name;
    private String idCard;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getIdCard() {
        return idCard;
    }

    public void setIdCard(String idCard) {
        this.idCard = idCard;
    }

    public Person(String name, String idCard) {
        this.name = name;
        this.idCard = idCard;
    }

    public Person() {
    }

    public boolean equals(Object obj){
        if(this == obj){
            return true;
        }
        if(obj instanceof  Person){
            Person p1 = (Person)obj;
            if(this.name.equals(p1.name) && this.idCard.equals(p1.idCard)){
                return true;
            }
        }
        return false;
    }
    public static void main(String[] args) {
        Person p1 = new Person("赵四", "4578925985324539875421");
        Person p2 = new Person("赵四", "4578925985324539875421");
        Dog dog = new Dog();
        System.out.println(p1.equals(dog));
    }
}

```

## 5. 多态实现原理

> 多态原理：是由虚方法和动态绑定来实现的
>
>
> 虚方法(Virtual Method)和非虚方法(Non Virtual Method)
>
> 虚方法是指在编译期间 无法确定方法版本信息的这一类方法
>
> 可以被子类重写(可以被子类继承的实例方法)的方法就属于虚方法
>
> 因为可以被子类重写的方法 会在多个子类中进行重写 而new对象的操作是在程序运行期间才执行的
>
> 所以在编译阶段 唯独可以确定的是等号左侧的类型 而不能确定的是等号右侧的对象
>
> 虚方法调用底层是通过JVM指令：#invokevritual
>
>
> 非虚方法是指在编译期间可以确定方法版本信息的这一类方法
>
> 比如：静态方法 private修饰的方法 final修饰的方法  构造方法
>
> 非虚方法调用底层是通过JVM指令：#invokespecial
>
>
> 动态绑定和静态绑定
>
> 虚方法属于动态绑定：因为在编译期间无法确定方法的版本信息 所以必须在程序运行过程中才确定调用哪个类中的
>
> 方法，所以虚方法属于动态绑定
>
> 非虚方法属于静态绑定：在编译期间就可以确定方法的版本信息 实现静态绑定
>
>
> 方法覆盖(重写) 和 方法隐藏：
>
> 实例方法属于覆盖，即重写，也就是子类重写父类方法以后通过子类对象再无法访问父类中被覆盖的方法
>
> 静态方法属于隐藏，子类可以写同名同参数同返回值的静态方法，只是对父类相同静态方法的隐藏，无法覆盖
>
> 因为通过指向对象的父类引用还可以继续访问父类中的静态方法
>
>
> 关于方法表：方法表是一个存在于类信息文件中的数组，保存当前类中的方法、继承以及重写的方法
>
> 当我们访问某一个方法时 先从本类中查找 本类中没有 继续向父类中查找 直到找打为止

![](img/方法表.png)

## 6. java命令

> javap -verbose Note.class 查看当前class文件详细信息
>
> this被设计为了一个隐式参数，存在于本类中的所有实例方法和构造方法中，所以我们在实例方法以及构造方法中才可以使用
>
> 静态方法中没有添加此隐式参数 所以无法使用this 以及 super 

