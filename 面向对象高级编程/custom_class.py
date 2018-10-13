#定制类


'''
__str__
'''

class Student(object):
    def __init__(self,name):
        self.name=name
    def __str__(self):
        return 'Student object (name: %s)' % self.name

s=Student('Rust')
print(s)

s

'''
这是因为直接显示变量调用的不是__str__()，而是__repr__()，两者的区别是__str__()返回用户看到的字符串，
而__repr__()返回程序开发者看到的字符串，也就是说，__repr__()是为调试服务的。
解决办法是再定义一个__repr__()。但是通常__str__()和__repr__()代码都是一样的，所以，有个偷懒的写法：
'''
class Student(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return 'Student object (name=%s)' % self.name
    __repr__ = __str__


'''
__iter__
'''

'''
如果一个类想被用于for ... in循环，类似list或tuple那样，就必须实现一个__iter__()方法，
该方法返回一个迭代对象，然后，Python的for循环就会不断调用该迭代对象的__next__()方法拿到循环的下一个值，
直到遇到StopIteration错误时退出循环
'''
class Fib(object):
    """docstring for [object Object]."""
    def __init__(self):
        self.a,self.b=0,1
    def __iter__(self):
        return self
    def __next__(self):
        self.a,self.b=self.b,self.a+self.b
        if self.a > 1000:
            raise StopIteration
        return self.a
        
f=Fib()
for n in f:
    print(n)

'''
__gititem__
'''
#要表现得像list那样按照下标取出元素，需要实现__getitem__()方法：
class Fib(object):
    """docstring for [object Object]."""
    def __init__(self):
        self.a,self.b=0,1
    def __iter__(self):
        return self
    def __next__(self):
        self.a,self.b=self.b,self.a+self.b
        if self.a > 1000:
            raise StopIteration
        return self.a
    def __getitem__(self,n):
        a,b=1,1
        for x in range(n):
            a,b=b,a+b
        return a

f=Fib()
print(f[6])

#list有个切片方法：
print(list(range(100))[88:100])

#对于Fib却报错。原因是__getitem__()传入的参数可能是一个int，也可能是一个切片对象slice，所以要做判断：
class Fib(object):

    """docstring for [object Object]."""
    def __init__(self):
        self.a,self.b=0,1
    def __iter__(self):
        return self
    def __next__(self):
        self.a,self.b=self.b,self.a+self.b
        if self.a > 1000:
            raise StopIteration
        return self.a

    def __getitem__(self,n):
        if isinstance(n, int): # n是索引
            a, b = 1, 1
            for x in range(n):
                a, b = b, a + b
            return a
        if isinstance(n,slice):
            start=n.start
            stop=n.stop
            if start is None:
                start = 0
            a,b=1,1
            L = []
            for x in range(stop):
                if x > start:
                    L.append(a)
                    a,b=b,a+b
        return L

#现在试试Fib的切片
print(Fib()[0:10])

#step
f=Fib()
print(f[:10:2])
"""
也没有对负数作处理，所以，要正确实现一个__getitem__()还是有很多工作要做的。

此外，如果把对象看成dict，__getitem__()的参数也可能是一个可以作key的object，例如str。

与之对应的是__setitem__()方法，把对象视作list或dict来对集合赋值。最后，还有一个__delitem__()方法，用于删除某个元素。

总之，通过上面的方法，我们自己定义的类表现得和Python自带的list、tuple、dict没什么区别，这完全归功于动态语言的“鸭子类型”，不需要强制继承某个接口。
"""

#__getattr__
#正常情况下，当我们调用类的方法或属性时，如果不存在，就会报错。比如定义Student类：
class Student(object):
    """docstring for [object Object]."""
    def __init__(self):
        self.name = 'Michael'

s=Student()
print(s.name)
#调用name属性，没问题，但是，调用不存在的score属性，就有问题了：
#print(s.score)
"""
错误信息很清楚地告诉我们，没有找到score这个attribute。

要避免这个错误，除了可以加上一个score属性外，Python还有另一个机制，那就是写一个__getattr__()方法，动态返回一个属性。修改如下：
"""
class Student(object):
    """docstring for [object Object]."""
    def __init__(self):
        self.name = 'Michael'
    def __getattr__(self, attr):
        if attr=='score':
            return 99

s=Student()

print(s.score)

"""
返回函数也是完全可以的：
"""
class Student(object):
    def __getattr__(self,arg):        
        if arg=='age':
            return lambda: 25
s=Student()
"""
只是调用方式要变为：
"""
print(s.age())      


"""
注意，只有在没有找到属性的情况下，才调用__getattr__，已有的属性，
比如name，不会在__getattr__中查找。
此外，注意到任意调用如s.abc都会返回None，这是因为我们定义的__getattr__默认返回就是None。
要让class只响应特定的几个属性，我们就要按照约定，抛出AttributeError的错误：
"""



class Student(object):
    
    def __getattr__(self,arg):        
        if arg=='age':
            return lambda: 25
#        raise AttributeError('\'Student\' object has no attribute \'%s\'' % arg)        

s=Student()
print(s.haha)

"""
现在很多网站都搞REST API，比如新浪微博、豆瓣啥的，调用API的URL类似：
"""
#利用完全动态的__getattr__，我们可以写出一个链式调用：

class Chain(object):
    def __init__(self, path=''):
        self._path = path
    def __getattr__(self, path):
        return Chain('%s/%s' % (self._path, path))
    
    def __str__(self):
        return self._path
        
    __repr__=__str__
    
print(Chain().status.user.timeline.list)

"""
这样，无论API怎么变，SDK都可以根据URL实现完全动态的调用，而且，不随API的增加而改变！

还有些REST API会把参数放到URL中，比如GitHub的API：

GET /users/:user/repos
调用时，需要把:user替换为实际用户名。如果我们能写出这样的链式调用：

Chain().users('michael').repos
就可以非常方便地调用API了。有兴趣的童鞋可以试试写出来。
"""


###__call__
"""
一个对象实例可以有自己的属性和方法，当我们调用实例方法时，我们用instance.method()来调用。
能不能直接在实例本身上调用呢？在Python中，答案是肯定的。

任何类，只需要定义一个__call__()方法，就可以直接对实例进行调用。请看示例：
"""

class Student(object):
    """docstring for [object Object]."""
    def __init__(self, name):
        self.name = name
        
    def __call__(self):
        print('My name is %s' % self.name)        

s=Student('Michael')

s()#self参数不要传入

"""
__call__()还可以定义参数。对实例进行直接调用就好比对一个函数进行调用一样，所以你完全可以把对象看成函数，
把函数看成对象，因为这两者之间本来就没啥根本的区别。

如果你把对象看成函数，那么函数本身其实也可以在运行期动态创建出来，因为类的实例都是运行期创建出来的，
这么一来，我们就模糊了对象和函数的界限。

那么，怎么判断一个变量是对象还是函数呢？其实，更多的时候，我们需要判断一个对象是否能被调用，
能被调用的对象就是一个Callable对象，比如函数和我们上面定义的带有__call__()的类实例：
"""

print(callable(Student('m')))
print(callable(max))
print(callable([1,2,3]))
print(callable(None))
print(callable('str'))

#通过callable()函数，我们就可以判断一个对象是否是“可调用”对象。















