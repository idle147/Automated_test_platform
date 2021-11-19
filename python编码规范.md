# Python 编码规范

## 抄自: https://www.runoob.com/w3cnote/google-python-styleguide.html



## 文档起始标注

大部分.py文件不必以#!作为文件的开始. 根据 [PEP-394](http://www.python.org/dev/peps/pep-0394/) , 程序的main文件应该以 #!/usr/bin/python2或者 #!/usr/bin/python3开始.



## 行长度标准

每行不超过80个字符

以下情况除外：

1. 长的导入模块语句
2. 注释里的URL

**不要使用反斜杠连接行。**Python会将 [圆括号, 中括号和花括号中的行隐式的连接起来](http://docs.python.org/2/reference/lexical_analysis.html#implicit-line-joining) , 你可以利用这个特点. 如果需要, 你可以在表达式外围增加一对额外的圆括号。

```python
# 推荐方法
foo_bar(self, width, height, color='black', design=None, x='foo',
             emphasis=None, highlight=0)
     if (width == 0 and height == 0 and
         color == 'red' and emphasis == 'strong'):
        
# 如果一个文本字符串在一行放不下, 可以使用圆括号来实现隐式行连接:
	x = ('这是一个非常长非常长非常长非常长'
         '非常长非常长非常长非常长非常长非常长的字符串')
    
# 在注释中，如果必要，将长的URL放在一行上。


```

## 括号

**宁缺毋**滥的使用括号, 除非是用于实现**行连接**, 否则不要在**返回语句或条件语句**中使用括号. 不过在元组两边使用括号是可以的.

```Python
# 正确表示方法
	if foo:
         bar()
     while x:
         x = bar()
     if x and y:
         bar()
     if not x:
         bar()
     return foo
     for (x, y) in dict.items(): ...
```



## 缩进

用**4个空格**来缩进代码, 用Tab缩进请在集成开发环境(如 Pycharm)设置为等价4个空格, **不要混用**

> (一) Tab的设置方法: file--->setting，选择Editor--->python
>
> ![image-20210619104838383](C:\Users\61042\AppData\Roaming\Typora\typora-user-images\image-20210619104838383.png)

> (二) 可以为Pycharm上有缩进的每一行加上'.'以表示空格, 效果如下
>
> ![image-20210619105030351](C:\Users\61042\AppData\Roaming\Typora\typora-user-images\image-20210619105030351.png)
>
> 设置方法: Editor=》General=》Appearance，或者搜索栏中直接搜索“Appearance”
>
> ![image-20210619105105867](C:\Users\61042\AppData\Roaming\Typora\typora-user-images\image-20210619105105867.png)



## 空行

**顶级定义之间空两行, 方法定义之间空一行**

顶级定义之间空两行, 比如函数或者类定义. 方法定义, 类定义与第一个方法之间, 都应该空一行. 

函数或方法中, 某些地方要是你觉得合适, 就空一行.



## 空格

按照标准的排版规范来使用标点两边的空格

**括号内不要有空格**.

```python
Yes: spam(ham[1], {eggs: 2}, [])
No:  spam( ham[ 1 ], { eggs: 2 }, [ ] )

```

**不要在逗号, 分号, 冒号前面加空格, 但应该在它们后面加(除了在行尾).**

>```python
>Yes: if x == 4:
>         print x, y
>     x, y = y, x
>     
>No:  if x == 4 :
>         print x , y
>     x , y = y , x
>```

**参数列表, 索引或切片的左括号前不应加空格.**

> ```python
> Yes: spam(1)
> no: spam (1)
> ```

**在二元操作符两边都加上一个空格, 比如赋值(=), 比较(==, <, >, !=, <>, <=, >=, in, not in, is, is not), 布尔(and, or, not)**

> ```python
> Yes: x == 1
> No:  x<1
> ```

**当'='用于指示关键字参数或默认参数值时, 不要在其两侧使用空格.**

>```python
>Yes: def complex(real, imag=0.0): return magic(r=real, i=imag)
>No:  def complex(real, imag = 0.0): return magic(r = real, i = imag)
>```

**注释不用空格上下对齐**

> ```python
> Yes:
>      foo = 1000  # 注释
>      long_name = 2  # 注释不需要对齐
> 
>      dictionary = {
>          "foo": 1,
>          "long_name": 2,
>          }
> ```



## 注释

1. 注释应该离代码至少2个空格
2. 对于复杂的操作逻辑, *应该在其操作开始前写上若干行注释"*
3. 对于不是一目了然的代码, *应在其行尾添加注释*

**文档(py文件)注释 **

> """
>
> ​	概述
>
> ​    (空一行)
>
> ​    内容
>
> """

**函数和方法注释**

> ```python
> def fetch_bigtable_rows(big_table, keys, other_silly_variable=None):
>     """一句话描述函数的功能
> 
>     详细描述函数功能
> 
>     Args:
>         对函数每个参数进行定义
> 
>     Returns:
>         对函数的返回值进行说明(None可忽略不写)
> 
>     Raises:
>         列出与接口有关的所有异常.
> 
>     """
>     pass
> ```

**类注释**

> ```python
> class SampleClass(object):
>     """一句话概述类的作用
> 
>     详细描述
> 
>     Attributes:
>         对类的每一个公有属性(不带self的变量),进行描述
>     """
> ```

**TODO注释**: 类似于我们的书签，标记下次我们需要做的工作。

1. 为未完成的临时代码使用TODO注释(短期解决方案. 不算完美, 但足够.)

2. TODO注释

   首先, 应该在所有开头处包含"TODO"字符串, 紧跟着是用括号括起来的你的名字, email地址或其它标识符. 

   然后, 是一个可选的冒号. 接着必须有一行注释, 进行简单解释. 

   最后, 写了TODO注释并不保证写的人会亲自解决问题. 当你写了一个TODO, 请注上你的名字.

   > ```
   > # TODO(kl@gmail.com): 要做什么,还剩什么没做
   > # TODO(Zeke) 重构了代码.
   > ```

## 字符串

1. 两个能进行字符串操作的尽量使用字符串操作,而不采用格式化输入
2. 多个字符串,采用格式化输入,而不采用操作

> ```python
> Yes: x = a + b
>      x = '%s, %s!' % (imperative, expletive)
>      x = '{}, {}!'.format(imperative, expletive)
>      x = 'name: %s; score: %d' % (name, n)
>      x = 'name: {}; score: {}'.format(name, n)
> 
> No: x = '%s%s' % (a, b)  # 使用+号
>     x = '{}{}'.format(a, b)  # 使用+号
>     x = imperative + ', ' + expletive + '!'  # 格式化输入
>     x = 'name: ' + name + '; score: ' + str(n) # 格式化输入
> ```

3. 避免在循环中用+和+=操作符来累加字符串. 由于字符串是不可变的, 这样做会创建不必要的临时对象, 并且导致二次方而不是线性的运行时间. 作为替代方案, 你可以将每个子串加入列表, 然后在循环结束后用 `.join` 连接列表. (也可以将每个子串写入一个 `cStringIO.StringIO` 缓存中.)

>```python
>Yes: items = ['<table>']
>     for last_name, first_name in employee_list:
>         items.append('<tr><td>%s, %s</td></tr>' % (last_name, first_name))  # 字符串加入列表
>     items.append('</table>')  # 末尾加入 </div>标签
>     employee_table = ''.join(items)  # 列表转换成字符串
>     
>No: employee_table = '<table>'
>    for last_name, first_name in employee_list:
>        employee_table += '<tr><td>%s, %s</td></tr>' % (last_name, first_name)
>    employee_table += '</table>'
>    
>```

   4. 同一文件不要单双引号混用

   5. 为多行字符串使用三重双引号"""而非三重单引号'''. 

      当且仅当项目中使用单引号'来引用字符串时, 才可能会使用三重单引号'''为**非文档字符串的多行字符串**来标识引用

      文档字符串必须使用三重双引号""(尽可能用隐式行连接)

      >```python
      >Yes:
      >    print ("This is much nicer.\n"
      >           "Do it this way.\n")
      >           
      >No:
      >      print """This is pretty ugly.
      >  Don't do this.
      >  """
      >```



## 文件和sockets

在文件和sockets结束时, 显式的关闭它.

除文件外, sockets或其他类似文件的对象在没有必要的情况下打开, 会有许多副作用, 例如:

1. 它们可能会消耗有限的系统资源, 如文件描述符. 如果这些资源在使用后没有及时归还系统, 那么用于处理这些对象的代码会将资源消耗殆尽.
2. 持有文件将会阻止对于文件的其他诸如移动、删除之类的操作.
3. 仅仅是从逻辑上关闭文件和sockets, 那么它们仍然可能会被其共享的程序在无意中进行读或者写操作. 只有当它们真正被关闭后, 对于它们尝试进行读或者写操作将会跑出异常, 并使得问题快速显现出来.

而且, 幻想当文件对象析构时, 文件和sockets会自动关闭, 试图将文件对象的生命周期和文件的状态绑定在一起的想法, 都是不现实的. 因为有如下原因:

1. 没有任何方法可以确保运行环境会真正的执行文件的析构. 不同的Python实现采用不同的内存管理技术, 比如延时垃圾处理机制. 延时垃圾处理机制可能会导致对象生命周期被任意无限制的延长.
2. 对于文件意外的引用,会导致对于文件的持有时间超出预期(比如对于异常的跟踪, 包含有全局变量等).

**推荐使用 ["with"语句](http://docs.python.org/reference/compound_stmts.html#the-with-statement) 以管理文件:**

```python
with open("hello.txt") as hello_file:
    for line in hello_file:
        print line
```

对于不支持使用"with"语句的类似文件的对象,使用 **contextlib.closing():**

```python
import contextlib

with contextlib.closing(urllib.urlopen("http://www.python.org/")) as front_page:
    for line in front_page:
        print line
```



## 导入

1. 放在文件首页
2. 导入顺序: (1)标准库 (2)第三方库 (3)应用程序指定导入
3. 每个导入占1行
4. 每种分组中, 应该根据每个模块的完整包路径按字典序排序, 忽略大小写.

> ```Python
> Yes: import os
>      import sys
>      import foo
> 	 from foo import bar
> 	 from foo.bar import baz
> 	 from foo.bar import Quux
> 	 from Foob import ar
>      
> No:  import os, sys
> ```



## 判断语句

1. 通常每个语句应该独占一行
2. 不过, 如果测试结果与测试语句在一行放得下, 你也可以将它们放在同一行. 如果是if语句, 只有在没有else时才能这样做.
3. try和except不能放在同一行

> ```python
> Yes:
>   if foo: bar(foo)
>   
> No:
>   if foo: bar(foo)
>   else:   baz(foo)
> 
>   try:               bar(foo)
>   except ValueError: baz(foo)
> 
>   try:
>       bar(foo)
>   except ValueError: baz(foo)
> ```



## 访问控制

1. 在Python中, 对于琐碎又不太重要的访问函数, 你应该直接使用公有变量来取代它们, 这样可以避免额外的函数调用开销. 当添加更多功能时, 你可以用属性(@property)来保持语法的一致性.

   > @property装饰器来创建**只读属性**, 防止被修改
   >
   > @property修饰函数，让函数可以像属性一样访问, 不用加()。

   > ```python
   > class DataSet(object):
   >   @property
   >   def method_with_property(self): ##含有@property
   >       return 15
   >   def method_without_property(self): ##不含@property
   >       return 15
   > 
   > l = DataSet()
   > print(l.method_with_property) # 加了@property后，可以用调用属性的形式来调用方法,后面不需要加（）。
   > print(l.method_without_property())  #没有加@property , 必须使用正常的调用方法的形式，即在后面加()
   > ```
   >
   > ```python
   > class DataSet(object):
   >     def __init__(self):
   >         self._images = 1
   >         self._labels = 2 #定义属性的名称
   >     @property
   >     def images(self): #方法加入@property后，这个方法相当于一个属性，这个属性可以让用户进行使用，而且用户有没办法随意修改。
   >         return self._images 
   >     @property
   >     def labels(self):
   >         return self._labels
   > l = DataSet()
   > #用户进行属性调用的时候，直接调用images即可，而不用知道属性名_images，因此用户无法更改属性，从而保护了类的属性。
   > print(l.images) # 加了@property后，可以用调用属性的形式来调用方法,后面不需要加（）。
   > ```



## 变量命名

<font color=#FF0000 >应该避免的命名</font> 

<font color=#FF0000 >应该采用的命名</font> 

1. 所谓"内部(Internal)"表示仅模块内可用, 或者, 在类内是保护或私有的.
2. 用单下划线(_)开头表示模块变量或函数是protected的(使用import * from时不会包含).
3. 用双下划线(__)开头的实例变量或方法表示类内私有.
4. 将相关的类和顶级函数放在同一个模块里. 不像Java, 没必要限制一个类一个模块.
5. 对类名使用大写字母开头的单词(如CapWords), 但是模块名应该用小写加下划线的方式(如lower_with_under.py)

<font color=#FF0000 >规范的命名</font> 

1. 模块名： 小写字母，单词之间用_分割  ad_stats.py 

2. 包名： 和模块名一样 

3. 类名： 单词首字母大写(驼峰) AdStats

4. 全局变量(常量): 大写字母，单词之间用_分割  COLOR_WRITE

5. 普通变量： 小写字母，单词之间用_分割  this_is_a_var

6. 保护变量(只有类对象和子类对象自己能访问到这些变量):  以_开头，其他和普通变量一样  _price

7. 私有变量(只有类对象自己能访问，连子类对象也不能访问到这个数据): 以__开头（2个下划线），其他和普通变量一样 \_\_private_var

8. 专有变量： \_\_开头，\_\_结尾，一般为python的自有变量(魔法方法)，不要以这种方式命名

9. 普通函数： 和普通变量一样get_name()  

10. 私有函数: 以__开头（2个下划线），其他和普通函数一样 \_\_get_name() 

11. 缩写: 命名应当尽量使用全拼写的单词，缩写的情况有如下两种： 

    (1)常用的缩写，如XML、ID等，在命名时也应只大写首字母，如XmlParser

    (2)命名中含有长单词，对某个单词进行缩写。这时应使用约定成俗的缩写方式。

       例如： function 缩写为 fn, text 缩写为 txt, object 缩写为 obj, count 缩写为 cnt, number 缩写为 num等。



![image-20210619113949267](C:\Users\61042\AppData\Roaming\Typora\typora-user-images\image-20210619113949267.png)



## 附录:

![image-20210619114446246](C:\Users\61042\AppData\Roaming\Typora\typora-user-images\image-20210619114446246.png)

![image-20210619114500880](C:\Users\61042\AppData\Roaming\Typora\typora-user-images\image-20210619114500880.png)

