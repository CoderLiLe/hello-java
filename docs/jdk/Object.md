# Object源码

所有类的基类——java.lang.Object
- Object 类是所有类的基类，当一个类没有直接继承某个类时，默认继承Object类
- Object 类属于 java.lang 包，此包下的所有类在使用时无需手动导入，系统会在程序编译期间自动导入。

思考：Object是如何成为默认父类的？

推测：

情况1：编译器处理

在编译源代码时，当一个类没有显式标明继承的父类时，编译器会为其指定一个默认的父类（一般为Object），而交给虚拟机处理这个类时，由于这个类已经有一个默认的父类了，因此，VM仍然会按照常规的方法像处理其他类一样来处理这个类。

情况2：虚拟机处理

编译器仍然按照实际代码进行编译，并不会做额外的处理，即如果一个类没有显式地继承于其他类时，编译后的代码仍然没有父类。然后由虚拟机运行二进制代码时，当遇到没有父类的类时，就会自动将这个类看成是Object类的子类

验证：
![](./assets/1.1.png)

使用JDK自带的工具（javap）反汇编

**结论：<font color=red>JDK无论版本，都是由编译器在编译阶段就已经织入了Object</font>**

## Object类结构图
![](./assets/1.2.png)

这里有7个native方法：registerNatives()、getClass()、hashCode()、clone()、notify()、notifyAll()、wait(long)

什么是native方法？官方给的说明是"A native method is a Java method whose implementation is provided by non-java code."

通俗的说，native表示该方法的实现java本身并没有完成，而是有c/c++来完成，放在.dll动态库文件中。

Object源码如下 : 
```java
package java.lang;


public class Object {

    /**
     * 一个本地方法,具体是用C(C++)在DLL中实现的,然后通过JNI调用
     */
    private static native void registerNatives();

    /**
     * 对象初始化时自动调用此方法
     */
    static {
        registerNatives();
    }

    /**
     * 返回此Object的运行时类
     */
    public final native Class<?> getClass();

    /**
     * hashCode的常规协定是：
     * 1.在java应用程序执行期间,在对同一对象多次调用hashCode()方法时,必须一致地返回相同的整数,前提是将对象进行equals比较时所用的信息没有被修改。
     * 从某一应用程序的一次执行到同一应用程序的另一次执行,该整数无需保持一致。
     * 2.如果根据equals(object)方法,两个对象是相等的,那么对这两个对象中的每个对象调用hashCode方法都必须生成相同的整数结果。
     * 3.如果根据equals(java.lang.Object)方法,两个对象不相等,那么对这两个对象中的任一对象上调用hashCode()方法不要求一定生成不同的整数结果。
     * 但是,应该意识到,为不相等的对象生成不同整数结果可以提高哈希表的性能。
     */
    public native int hashCode();

    /**
     * 这里比较的是对象的内存地址
     */
    public boolean equals(Object obj) {
        return (this == obj);
    }

    /**
     * 本地clone方法,用于对象的复制
     */
    protected native Object clone() throws CloneNotSupportedException;

    /**
     * 返回该对象的字符串表示,非常重要的方法
     * getClass().getName();获取字节码文件的对应全路径名例如java.lang.Object
     * Integer.toHexString(hashCode());将哈希值转成16进制数格式的字符串。
     */
    public String toString() {
        return getClass().getName() + "@" + Integer.toHexString(hashCode());
    }

    /**
     * 不能被重写，用于唤醒一个在因等待该对象（调用了wait方法）被处于等待状态（waiting 或 time_wait）的线程，该方法只能同步     * 方法或同步块中调用
     */
    public final native void notify();

    /**
     * 不能被重写，用于唤醒所有在因等待该对象（调用wait方法）被处于等待状态（waiting或time_waiting）的线程，该方法只能同步方      * 法或同步块中调用
     */
    public final native void notifyAll();

    /**
     * 不能被重写，用于在线程调用中，导致当前线程进入等待状态（time_waiting)，timeout单位为毫秒,该方法只能同步方法或同步块中     * 调用,超过设置时间后线程重新进入可运行状态
     */
    public final native void wait(long timeout) throws InterruptedException;


    public final void wait(long timeout, int nanos) throws InterruptedException {
        if (timeout < 0) {
            throw new IllegalArgumentException("timeout value is negative");
        }

        if (nanos < 0 || nanos > 999999) {
            throw new IllegalArgumentException(
                    "nanosecond timeout value out of range");
        }

        if (nanos > 0) {
            timeout++;
        }

        wait(timeout);
    }

    /**
     * 在其他线程调用此对象的notify()方法或notifyAll()方法前,导致当前线程等待。换句话说,此方法的行为就好像它仅执行wait(0)调       用一样。
     * 当前线程必须拥有此对象监视器。
     * 该线程发布对此监视器的所有权并等待,直到其他线程通过调用notify方法或notifyAll方法通知在此对象的监视器上等待的线程醒来,
     * 然后该线程将等到重新获得对监视器的所有权后才能继续执行。
     */
    public final void wait() throws InterruptedException {
        wait(0);
    }

    /**
     * 这个方法用于当对象被回收时调用，这个由JVM支持，Object的finalize方法默认是什么都没有做，如果子类需要在对象被回收时执行        一些逻辑处理，则可以重写finalize方法。
     */
    protected void finalize() throws Throwable {
    }
}
```
### 补充说明：关键字 Native
问题：为什么要用 native 来修饰方法，这样做有什么用？

**JNI：Java Native Interface**

一般情况下，我们完全可以使用 Java 语言编写程序，但某些情况下，Java 可能会不满足应用程序的需求，或者是不能更好的满足需求，比如：

① 标准的 Java 类库不支持应用程序平台所需的平台相关功能。

② 我们已经用另一种语言编写了一个类库，如何用Java代码调用？

③ 某些运行次数特别多的方法代码，为了加快性能，我们需要用更接近硬件的语言（比如汇编）编写。

上面这三种需求，其实说到底就是如何用 Java 代码调用不同语言编写的代码。那么 JNI 应运而生了。

![](./assets/1.3.png)

native 用来修饰方法，用 native 声明的方法表示告知 JVM 调用，该方法在外部定义，我们可以用任何语言去实现它。 简单地讲，一个native Method就是一个 Java 调用非 Java 代码的接口。

## 类构造器

一个类必须要有一个构造器的存在，如果没有显示声明，那么系统会默认创造一个无参构造器，在JDK的Object类源码中，是看不到构造器的，系统会自动添加一个无参构造器。我们可以通过：
```java
// 构造一个Object类的对象。
Object obj = new Object();
```

## equals 方法

- 面试： equals() 方法和 == 运算符的区别？
- 思考：有没有重写过equals？
- 思考：为何重写equals() 就得重写hashCode方法？
  
Object 类中的equals 方法：
```java
public boolean equals(Object obj) {
     
     return (this == obj);
 }
```

**结论：**

- 在 Object 类中，== 运算符和 equals 方法是等价的，都是比较两个对象的引用是否相等，从另一方面来讲，如果两个对象的引用相等，那么这两个对象一定是相等的
- 对于我们自定义的一个对象，如果不重写 equals 方法，那么在比较对象的时候就是调用 Object 类的 equals 方法，也就是用 == 运算符比较两个对象

测试程序：
```java
public class JDKTest{
    
    public static void main(String[] args) {
        String test1 = new String("test");
        String test2 = new String("test");

        System.out.println(test1.equals(test2));
    }
}
```

String类重写equals方法：
```java
public boolean equals(Object anObject) {     
    //如果内存地址相等，那必须equal
    if (this == anObject) {
        return true;
    }
     
    //如果对象是String类型 
    if (anObject instanceof String) {
        String anotherString = (String)anObject;
        // 获取调用方的字符串长度赋值给n
        int n = value.length;
        //判断长度相等
        if (n == anotherString.value.length) {
            char v1[] = value;
            char v2[] = anotherString.value;
            int i = 0;
            //那我们就逐个字符的比较
            while (n-- != 0) {
                //从前往后，任意一个字符不匹配，直接返回false
                if (v1[i] != v2[i])
                    return false;
                i++;
            }
            //全部匹配结束，返回true
            return true;
        }
    }
    return false;
}
```

String 是引用类型，比较时不能比较引用是否相等，重点是字符串的内容是否相等。所以 String 类定义两个对象相等的标准是**字符串内容都相同**。

在Java规范中，对 equals 方法的使用必须遵循以下几个原则：

> ① 自反性：对于任何非空引用值 x，x.equals(x) 都应返回 true。
>
> ② 对称性：对于任何非空引用值 x 和 y，当且仅当 y.equals(x) 返回 true 时，x.equals(y) 才应返回 true。
>
> ③ 传递性：对于任何非空引用值 x、y 和 z，如果 x.equals(y) 返回 true，并且 y.equals(z) 返回 true，那么 x.equals(z) 应返回 true。
>
>④ 一致性：对于任何非空引用值 x 和 y，多次调用 x.equals(y) 始终返回 true 或始终返回 false，前提是对象上 equals 比较中所用的信息没有被修改
>
>⑤ 对于任何非空引用值 x，x.equals(null) 都应返回 false。

<font color="red" size=4>注意：无论何时重写此方法，通常都必须重写hashCode方法，以维护hashCode方法的一般约定，该方法声明相等对象必须具有相同的哈希代码</font>

## hashCode 方法

源码 Object 类中定义如下：
```java
// 是一个用 native 声明的本地方法，作用是返回对象的散列码，是 int 类型的数值。
public native int hashCode();
```

思考：为什么要有hashCode方法，意义?

思考：hashCode如何被计算出来的？存储在对象内存结构中的那部分中？

作用：

HashCode的存在主要是为了查找的快捷性，HashCode是用来在散列存储结构中确定对象的存储地址

例：比如使用集合 List,Set，还有 Map，List集合一般是存放的元素是有序可重复的，Set 存放的元素则是无序不可重复的，而 Map 集合存放的是键值对。

前面我们说过判断一个元素是否相等可以通过 equals 方法，没增加一个元素，那么我们就通过 equals 方法判断集合中的每一个元素是否重复，但是如果集合中有10000个元素了，但我们新加入一个元素时，那就需要进行10000次equals方法的调用，这显然效率很低。

于是，Java 的集合设计者就采用了 哈希表 来实现。哈希算法也称为散列算法，是将数据依特定算法产生的结果直接指定到一个地址上。这个结果就是由 hashCode 方法产生。这样一来，当集合要添加新的元素时，先调用这个元素的 hashCode 方法，就一下子能定位到它应该放置的物理位置上。

![](./assets/1.4.png)

① 如果这个位置上没有元素，它就可以直接存储在这个位置上，不用再进行任何比较了；

② 如果这个位置上已经有元素了，就调用它的equals方法与新元素进行比较，相同的话就不存了；

③ 不相同的话，也就是发生了Hash key相同导致冲突的情况，那么就在这个Hash key的地方产生一个链表，将所有产生相同HashCode的对象放到这个单链表

## HashCode是如何产生的？
思考：hashCode到底是什么？是不是对象的内存地址？
```java
public class HashCodeTest {
    //目标：只要发生重复，说明hashcode不是内存地址，但还需要证明（JVM代码证明）
    public static void main(String[] args) {
        List<Integer> integerList = new ArrayList<Integer>();
        int num = 0;
        for (int i = 0; i < 150000; i++) {
            //创建新的对象
            Object object = new Object();
            if (integerList.contains(object.hashCode())) {
                num++;//发生重复（内存地址肯定不会重复）
            } else {
                integerList.add(object.hashCode());//没有重复
            }
        }
        System.out.println(num + "个hashcode发生重复");
        System.out.println("List合计大小" + integerList.size() + "个");

    }
}
```
15万个循环，发生了重复，说明hashCode不是内存地址（严格的说，肯定不是直接取的内存地址）
![](./assets/1.5.png)

### HashCode存储位置
### 对象内存布局
当一个对象在堆内存中分配好并且初始化完成之后的结构是什么样的呢？

![](./assets/1.6.png)

1、添加对求填充是为了保证对象的总大小是8的整数倍个字节。

2、类型指针占4个字节是因为默认开启了指针压缩，如果不开启指针压缩，则占8个字节

> hashCode的值存在Java对象头里的，那么什么是Java对象头呢？
> 
>Hotspot虚拟机的对象头主要包括两部分数据：Mark Word（标记字段）、Class Pointer（类型指针）。其中 Class Pointer是对象指向它的类元数据的指针，虚拟机通过这个指针来确定这个对象是哪个类的实例，Mark Word用于存储对象自身的运行时数据，它是实现轻量级锁和偏向锁的关键。

Mark Word用于存储对象自身的运行时数据，如：哈希码（HashCode）、GC分代年龄、锁状态标志、线程持有的锁、偏向线程 ID、偏向时间戳等

![](./assets/1.7.png)

![](./assets/1.8.png)

### HashCode生成时机
```java
@Test
public void test2() {
    Object_Test object_test = new Object_Test();
    // jvm的信息
    System.out.println(VM.current().details());
    System.out.println("-------------------------");
    // 调用之前打印object_test对象的头信息
    // 以表格的形式打印对象布局
    System.out.println(ClassLayout.parseInstance(object_test).toPrintable());

    System.out.println("-------------------------");
    // 调用后再打印object_test对象的hashcode值
    System.out.println(Integer.toHexString(object_test.hashCode()));
    System.out.println(ClassLayout.parseInstance(object_test).toPrintable());

    System.out.println("-------------------------");
    // 有线程加重量级锁的时候，再来看对象头
    new Thread(()->{
        try {
            synchronized (object_test){
                Thread.sleep(5000);
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }).start();
    new Thread(()->{
        try {
            synchronized (object_test){
                Thread.sleep(5000);
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }).start();
    System.out.println(Integer.toHexString(object_test.hashCode()));
    System.out.println(ClassLayout.parseInstance(object_test).toPrintable());
}
```

结果：

对象的内存结构（无锁状态、未调用HashCode）：

![](./assets/1.9.png)

调用对象的HashCode方法后：

![](./assets/1.10.png)

加锁，产生线程竞争后：

![](./assets/1.11.png)

## HashCode如何生成的？
源码：
```java
public native int hashCode();
```

1）先从Object.c开始找hashCode映射

src\share\native\java\lang\Object.c

```c
JNIEXPORT void JNICALL//jni调用
//全路径：java_lang_Object_registerNatives是java对应的包下方法
Java_java_lang_Object_registerNatives(JNIEnv *env, jclass cls)
{
     //jni环境调用；下面的参数methods对应的java方法
    (*env)->RegisterNatives(env, cls,
                            methods, sizeof(methods)/sizeof(methods[0]));
}
```

JAVA--------------------->C++函数对应
```cpp
//JAVA方法（返回值）----->C++函数对象
static JNINativeMethod methods[] = {
    //JAVA方法        返回值  （参数）                          c++函数
    {"hashCode",    "()I",                    (void *)&JVM_IHashCode},
    {"wait",        "(J)V",                   (void *)&JVM_MonitorWait},
    {"notify",      "()V",                    (void *)&JVM_MonitorNotify},
    {"notifyAll",   "()V",                    (void *)&JVM_MonitorNotifyAll},
    {"clone",       "()Ljava/lang/Object;",   (void *)&JVM_Clone},
};
```

2）全局检索JVM_IHashCode

完全搜不到这个方法名，只有这个还凑合有点像，那这是个啥呢？
![](./assets/1.12.png)

src\share\vm\prims\jvm.cpp

```cpp
/*
JVM_ENTRY is a preprocessor macro that
adds some boilerplate code that is common for all functions of HotSpot JVM API.
This API is a connection layer between the native code of JDK class library and the JVM.

JVM_ENTRY是一个预加载宏，增加一些样板代码到jvm的所有function中
这个api是位于本地方法与jdk之间的一个连接层。

所以，此处才是生成hashCode的逻辑！
*/
JVM_ENTRY(jint, JVM_IHashCode(JNIEnv* env, jobject handle))
  JVMWrapper("JVM_IHashCode");
  //调用了ObjectSynchronizer对象的FastHashCode
 return handle == NULL ? 0 : ObjectSynchronizer::FastHashCode (THREAD, JNIHandles::resolve_non_null(handle)) ;
JVM_END
```

3）继续，ObjectSynchronizer::FastHashCode
![](./assets/1.13.png)

先说生成流程，留个印象：

![](./assets/1.14.jpg)
```cpp
intptr_t ObjectSynchronizer::FastHashCode (Thread * Self, oop obj) {
    //是否开启了偏向锁(Biased：偏向，倾向)
  if (UseBiasedLocking) {
    //如果当前对象处于偏向锁状态
    if (obj->mark()->has_bias_pattern()) {
      Handle hobj (Self, obj) ;
      assert (Universe::verify_in_progress() ||
              !SafepointSynchronize::is_at_safepoint(),
             "biases should not be seen by VM thread here");
            //那么就撤销偏向锁（达到无锁状态，revoke：废除）
      BiasedLocking::revoke_and_rebias(hobj, false, JavaThread::current());
      obj = hobj() ;
        //断言下，看看是否撤销成功（撤销后为无锁状态）
      assert(!obj->mark()->has_bias_pattern(), "biases should be revoked by now");
    }
  }

  // ……

  ObjectMonitor* monitor = NULL;
  markOop temp, test;
  intptr_t hash;
  //读出一个稳定的mark;防止对象obj处于膨胀状态；
  //如果正在膨胀，就等他膨胀完毕再读出来
  markOop mark = ReadStableMark (obj);

    //是否撤销了偏向锁（也就是无锁状态）（neutral：中立，不偏不斜的）
  if (mark->is_neutral()) {
    //从mark头上取hash值
    hash = mark->hash(); 
    //如果有，直接返回这个hashcode（xor）
    if (hash) {                       // if it has hash, just return it
      return hash;
    }
        //如果没有就新生成一个(get_next_hash)
    hash = get_next_hash(Self, obj);  // allocate a new hash code
    //生成后，原子性设置，将hash放在对象头里去，这样下次就可以直接取了
    temp = mark->copy_set_hash(hash); // merge the hash code into header
    // use (machine word version) atomic operation to install the hash
    test = (markOop) Atomic::cmpxchg_ptr(temp, obj->mark_addr(), mark);
    if (test == mark) {
      return hash;
    }
    // If atomic operation failed, we must inflate the header
    // into heavy weight monitor. We could add more code here
    // for fast path, but it does not worth the complexity.
    //如果已经升级成了重量级锁，那么找到它的monitor
    //也就是我们所说的内置锁(objectMonitor)，这是c里的数据类型
    //因为锁升级后，mark里的bit位已经不再存储hashcode，而是指向monitor的地址
    //而升级的markword呢？被移到了c的monitor里
  } else if (mark->has_monitor()) {
    //沿着monitor找header，也就是对象头
    monitor = mark->monitor();
    temp = monitor->header();
    assert (temp->is_neutral(), "invariant") ;
    //找到header后取hash返回
    hash = temp->hash();
    if (hash) {
      return hash;
    }
    // Skip to the following code to reduce code size
  } else if (Self->is_lock_owned((address)mark->locker())) {
    //轻量级锁的话，也是从java对象头移到了c里，叫helper
    temp = mark->displaced_mark_helper(); // this is a lightweight monitor owned
    assert (temp->is_neutral(), "invariant") ;
    hash = temp->hash();              // by current thread, check if the displaced
    //找到，返回
    if (hash) {                       // header contains hash code
      return hash;
    }
  }
    
  
  // ……
```

问：

为什么要先撤销偏向锁到无锁状态，再来生成hashcode呢？这跟锁有什么关系？

答：

mark word里，hashcode存储的字节位置被偏向锁给占了！偏向锁存储了锁持有者的线程id

### 扩展：关于hashCode的生成算法（了解）
```java
// hashCode() generation :
// 涉及到c++算法领域，感兴趣的同学自行研究
// Possibilities:
// * MD5Digest of {obj,stwRandom}
// * CRC32 of {obj,stwRandom} or any linear-feedback shift register function.
// * A DES- or AES-style SBox[] mechanism
// * One of the Phi-based schemes, such as:
//   2654435761 = 2^32 * Phi (golden ratio)
//   HashCodeValue = ((uintptr_t(obj) >> 3) * 2654435761) ^ GVars.stwRandom ;
// * A variation of Marsaglia's shift-xor RNG scheme.
// * (obj ^ stwRandom) is appealing, but can result
//   in undesirable regularity in the hashCode values of adjacent objects
//   (objects allocated back-to-back, in particular).  This could potentially
//   result in hashtable collisions and reduced hashtable efficiency.
//   There are simple ways to "diffuse" the middle address bits over the
//   generated hashCode values:
//
static inline intptr_t get_next_hash(Thread * Self, oop obj) {
    intptr_t value = 0;
    if (hashCode == 0) {
        // This form uses an unguarded global Park-Miller RNG,
        // so it's possible for two threads to race and generate the same RNG.
        // On MP system we'll have lots of RW access to a global, so the
        // mechanism induces lots of coherency traffic.
        value = os::random ();//返回随机数
    } else if (hashCode == 1) {
        // This variation has the property of being stable (idempotent)
        // between STW operations.  This can be useful in some of the 1-0
        // synchronization schemes.
        //和地址相关，但不是地址；右移+异或算法
        intptr_t addrBits = cast_from_oop < intptr_t > (obj) >> 3;
        value = addrBits ^ (addrBits >> 5) ^ GVars.stwRandom;//随机数位移异或计算
    } else if (hashCode == 2) {
        value = 1;            // 返回1
    } else if (hashCode == 3) {
        value = ++GVars.hcSequence;//返回一个Sequence序列号
    } else if (hashCode == 4) {
        value = cast_from_oop < intptr_t > (obj);//也不是地址
    } else {
        //常用
        // Marsaglia's xor-shift scheme with thread-specific state
        // This is probably the best overall implementation -- we'll
        // likely make this the default in future releases.
        //马萨利亚教授写的xor-shift 随机数算法（异或随机算法)
        unsigned t = Self -> _hashStateX;
        t ^= (t << 11);
        Self -> _hashStateX = Self -> _hashStateY;
        Self -> _hashStateY = Self -> _hashStateZ;
        Self -> _hashStateZ = Self -> _hashStateW;
        unsigned v = Self -> _hashStateW;
        v = (v ^ (v >> 19)) ^ (t ^ (t >> 8));
        Self -> _hashStateW = v;
        value = v;
    }
}
```

![](./assets/1.15.png)

可以通过参数 -XX: hashcode=1进行修改 （JDK8默认使用最后一种）

### 总结
通过分析虚拟机源码我们证明了hashCode不是直接用的内存地址，而是采取一定的算法来生成

hashcode值的存储在mark word里，与锁共用一段bit位，这就造成了跟锁状态相关性

如果是偏向锁：
一旦调用hashcode，偏向锁将被撤销，hashcode被保存占位mark word，对象被打回无锁状态

那偏偏这会就是有线程硬性使用对象的锁呢？
对象再也回不到偏向锁状态而是升级为重量级锁。hash code跟随mark word被移动到c的object monitor，从那里取

## getClass 方法

getClass()在 Object 类中如下，作用是返回对象的运行时类。

```java
public final native Class<?> getClass();
```

这是一个用 native 关键字修饰的方法

>native 用来修饰方法，用 native 声明的方法表示告知 JVM 调用，该方法在外部定义，我们可以用任何语言去实现它。
>
>简单地讲，一个native Method就是一个 Java 调用非 Java 代码的接口。


这里我们要知道用 native 修饰的方法我们不用考虑，由操作系统帮我们实现，该方法的作用是返回一个对象的运行时类，通过这个类对象我们可以获取该运行时类的相关属性和方法

## toString 方法
```java
public String toString() {
    return getClass().getName() + "@" + Integer.toHexString(hashCode());
}
```

- getClass().getName()是返回对象的全类名（包含包名）,Integer.toHexString(hashCode()) 是以16进制无符号整数形式返回此哈希码的字符串表示形式。
- 打印某个对象时，默认是调用 toString 方法，比如 System.out.println(person),等价于 System.out.println(person.toString())

## clone方法
```java
/**
 * 本地clone方法,用于对象的复制
 */
protected native Object clone() throws CloneNotSupportedException;
```

保护方法，实现对象的浅拷贝，只有实现了Cloneable接口才可以调用该方法，否则抛出CloneNotSupportedException异常。

## finalize 方法
```java
protected void finalize() throws Throwable { 
    
}
```

当 GC 确定不再有对该对象的引用时，GC 会调用对象的 finalize() 方法来清除回收。

Java VM 会确保一个对象的 finalize() 方法只被调用一次，而且程序中不能直接调用 finalize() 方法。

finalize() 方法通常也不可预测，而且很危险，一般情况下，不必要覆盖 finalize() 方法。

## registerNatives 方法
```java
private static native void registerNatives();
```

这是一个本地方法，我们要知道一个类定义了本地方法后，想要调用操作系统的实现，**必须还要装载本地库**

```java
static {
    registerNatives();
}
```

静态代码块就是一个类在初始化过程中必定会执行的内容，所以在类加载的时候是会执行该方法的，通过该方法来注册本地方法。










