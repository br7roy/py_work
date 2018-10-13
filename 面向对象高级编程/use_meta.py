#使用元类
#!/bin/bash python
import sys

"""
type()

动态语言和静态语言最大的不同，就是函数和类的定义，不是编译时定义的，而是运行时动态创建的。

比方说我们要定义一个Hello的class，就写一个hello.py模块：
"""
class Hello(object):
    def hello(self, name='world'):
        print('Hello, %s' % name)

h=Hello()
h.hello()

"""
type()函数可以查看一个类型或变量的类型
"""
#Hello是一个class，它的类型就是type
print(type(Hello))
#h是一个实例，它的类型就是class Hello
print(type(h))

"""
type()函数既可以返回一个对象的类型，又可以创建出新的类型，
比如，我们可以通过type()函数创建出Hello类，而无需通过class Hello(object)...的定义：
"""
#先定义函数
def fn(self, name='world'):
    print("Hello, %s" % name)

#创建Hello 函数
Hello = type("Hello",(object,),dict(hello2=fn))
h=Hello()
h.hello2()

print(type(Hello))
print(type(h))

"""
要创建一个class对象，type()函数依次传入3个参数：

1.class的名称；
2.继承的父类集合，注意Python支持多重继承，如果只有一个父类，别忘了tuple的单元素写法；
3.class的方法名称与函数绑定，这里我们把函数fn绑定到方法名hello上。
"""

"""
通过type()函数创建的类和直接写class是完全一样的，因为Python解释器遇到class定义时
仅仅是扫描一下class定义的语法，然后调用type()函数创建出class。

正常情况下，我们都用class Xxx...来定义类，但是，type()函数也允许我们动态创建出类来
也就是说，动态语言本身支持运行期动态创建类，这和静态语言有非常大的不同，要在静态语言运行期创建类
必须构造源代码字符串再调用编译器，或者借助一些工具生成字节码实现，本质上都是动态编译，会非常复杂。
"""


#metaclass
"""
除了使用type()动态创建类以外，要控制类的创建行为，还可以使用metaclass。

metaclass，直译为元类，简单的解释就是：

当我们定义了类以后，就可以根据这个类创建出实例，所以：先定义类，然后创建实例。

但是如果我们想创建出类呢？那就必须根据metaclass创建出类，所以：先定义metaclass，然后创建类。

连接起来就是：先定义metaclass，就可以创建类，最后创建实例。

所以，metaclass允许你创建类或者修改类。换句话说，你可以把类看成是metaclass创建出来的“实例”。

metaclass是Python面向对象里最难理解，也是最难使用的魔术代码。正常情况下，你不会碰到需要使用metaclass的情况，所以，以下内容看不懂也没关系，因为基本上你不会用到。

我们先看一个简单的例子，这个metaclass可以给我们自定义的MyList增加一个add方法：

定义ListMetaclass，按照默认习惯，metaclass的类名总是以Metaclass结尾，以便清楚地表示这是一个metaclass：
"""
#metaclass是类的模板，所以必须从'type'类型派生
class ListMetaclass(type):
    def __new__(cls, name, bases, attrs):
        #为通过元类生成的对象增加一个add方法
        attrs['add'] = lambda self, value:self.append(value)
        return type.__new__(cls, name, bases, attrs)

class MyList(list,metaclass=ListMetaclass):
    pass

L = MyList()
#测试MyList是否可以使用add方法
L.add(1)
print(L)

L2 = list()
#普通的list没有add方法
#L2.add(1)

"""
动态修改有什么意义？直接在MyList定义中写上add()方法不是更简单吗？正常情况下
确实应该直接写，通过metaclass修改纯属变态。

但是，总会遇到需要通过metaclass修改类定义的。ORM就是一个典型的例子。

ORM全称“Object Relational Mapping”，即对象-关系映射，就是把关系数据库的一行映射为一个
对象，也就是一个类对应一个表，这样，写代码更简单，不用直接操作SQL语句。

要编写一个ORM框架，所有的类都只能动态定义，因为只有使用者才能根据表的结构定义出对应的类
来。

让我们来尝试编写一个ORM框架。

编写底层模块的第一步，就是先把调用接口写出来。比如，使用者如果使用这个ORM框架，想定义
一个User类来操作对应的数据库表User，我们期待他写出这样的代码：
"""



"""
其中，父类Model和属性类型StringField、IntegerField是由ORM框架提供的，剩下的魔术方法比如save()全部由metaclass自动完成。虽然metaclass的编写会比较复杂，但ORM的使用者用起来却异常简单。

现在，我们就按上面的接口来实现该ORM。

"""

#首先来定义Field类，它负责保存数据库表的字段名和字段类型：
class Field(object):
    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type
        
    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)
        
# 在Field的基础上，进一步定义各种类型的Field，比如StringField，IntegerField

class StringField(Field):
    def __init__(self, name):
        super(StringField, self).__init__(name, 'varchar(100)')        
class IntegerField(Field):
    def __init__(self, name):
        super(IntegerField, self).__init__(name, 'bigint')        

# 下一步，就是编写最复杂的ModelMetaclass了：
class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name=='Model':
            return type.__new__(cls, name, bases, attrs)
        print('Found model: %s' % name)
        mappings = dict()
        for k, v in attrs.items():
            if isinstance(v, Field):
                print('Found Mapping: %s ==> %s' % (k, v))
                mappings[k] = v
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = name #假设表明和类名一致
        return type.__new__(cls, name, bases, attrs)
        
# 以及基类 Model:
class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)        
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(r"'Model' object has no attribute ' %s'" % key)
    def __setattr__(self, key, value):
            self[key] = value
            
    def save(self):
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))
        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
        print('SQL: %s' % sql)
        print('ARGS: %s' % str(args))
                


class User(Model):
    # 定义类的属性到列的映射
    id = IntegerField('id')        
    name = StringField('username')
    email = StringField('email')
    password = StringField('password')
    
# 创建一个实例
u = User(id=12345, name='Michael', email='teset@orm.org', password='my-pwd')
# 保存到数据库
u.save()






        
            














