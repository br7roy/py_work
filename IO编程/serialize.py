#序列化

d = dict(name='Bob', age=20, score=88)

#序列化
"""
可以随时修改变量，比如把name改成'Bill'，但是一旦程序结束，变量所占用的内存就被
操作系统全部回收。如果没有把修改后的'Bill'存储到磁盘上，下次重新运行程序，变量
又被初始化为'Bob'。

我们把变量从内存中变成可存储或传输的过程称之为序列化，在Python中叫pickling，
在其他语言中也被称之为serialization，marshalling，flattening等等，都是一个意思。
"""

#反序列化
"""
序列化之后，就可以把序列化后的内容写入磁盘，或者通过网络传输到别的机器上。

反过来，把变量内容从序列化的对象重新读到内存里称之为反序列化，即unpickling。

Python提供了pickle模块来实现序列化。

首先，我们尝试把一个对象序列化并写入文件：
"""

# 序列化

import pickle

d=dict(name='Bob',age='20',score=88)
print(pickle.dumps(d))

dp = 'D:\\Users\\futanghang004\\Desktop\\dumps.log'


f = open(dp, 'wb')

pickle.dump(d,f)
f.close()


# 反序列化
f = open(dp, 'rb')
c = dict()
c = pickle.load(f)
f.close()
print(c)

"""
Pickle的问题和所有其他编程语言特有的序列化问题一样，就是它只能用于Python，
并且可能不同版本的Python彼此都不兼容，因此，只能用Pickle保存那些不重要的数据，不能成功地反序列化也没关系。
"""

#JSON
"""
如果我们要在不同的编程语言之间传递对象，就必须把对象序列化为标准格式，比如XML，但更好
的方法是序列化为JSON，因为JSON表示出来就是一个字符串，可以被所有语言读取，也可以
方便地存储到磁盘或者通过网络传输。JSON不仅是标准格式，并且比XML更快，而且可以直接
在Web页面中读取，非常方便。

JSON表示的对象就是标准的JavaScript语言的对象，JSON和Python内置的
数据类型对应如下：
"""

import json

d = dict(name='Bob', age='20', score=80)
print(json.dumps(d))

"""
dumps()方法返回一个str，内容就是标准的JSON。类似的，dump()方法可以直
接把JSON写入一个file-like Object。
"""

"""
要把JSON反序列化为Python对象，用loads()或者对应的load()方法，前者
把JSON的字符串反序列化，后者从file-like Object中读取字符串并反序列化：
"""

json_str = '{"age": 20, "score": 88, "name": "Bob"}'
print(json.loads(json_str))


#JSON进阶
"""
Python的dict对象可以直接序列化为JSON的{}，不过，很多时候，我们更喜欢用
class表示对象，比如定义Student类，然后序列化：
"""
class Student(object):
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

s = Student('Bob', 20, 88)
# print(json.dumps(s))
# 运行代码，毫不留情地得到一个TypeError：
# 错误的原因是Student对象不是一个可序列化为JSON的对象。
# 如果连class的实例对象都无法序列化为JSON，这肯定不合理！
# 别急，我们仔细看看dumps()方法的参数列表，可以发现，除了第一个必须的obj参数外，
# dumps()方法还提供了一大堆的可选参数：

"""
这些可选参数就是让我们来定制JSON序列化。前面的代码之所以无法把Student类实例序
列化为JSON，是因为默认情况下，dumps()方法不知道如何将Student实例变为一
个JSON的{}对象。

可选参数default就是把任意一个对象变成一个可序列为JSON的对象，我们只需要为
Student专门写一个转换函数，再把函数传进去即可：
"""

def Student2dict(std):
    return {
        'name': std.name,
        'age': std.age,
        'score': std.score,
    }

print(json.dumps(s,default=Student2dict))

# 这样，Student实例首先被student2dict()函数转换成dict，然后再被
# 顺利序列化为JSON：


"""
不过，下次如果遇到一个Teacher类的实例，照样无法序列化为JSON。我们可以偷个懒，
把任意class的实例变为dict：
"""
print(json.dumps(s, default=lambda obj : obj.__dict__))
# 因为通常class的实例都有一个__dict__属性，它就是一个dict，用来存储
# 实例变量。也有少数例外，比如定义了__slots__的class。

def dict2student(d):
    return Student(d['name'], d['age'], d['score'])

print('do final')
print(json_str)

print(json.loads(json_str, object_hook=dict2student))





