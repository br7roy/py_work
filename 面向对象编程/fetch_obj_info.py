#获取对象信息
'''
当我们拿到一个对象的引用时，如何知道这个对象是什么类型、有哪些方法呢？

使用type()
'''
#!/usr/bin/bash

print(type(222))
print(type('str22'))
print(type(None))

"""如果一个变量指向函数或者类，也可以用type()判断："""

print(type(abs))

'''
但是type()函数返回的是什么类型呢？它返回对应的Class类型。如果我们要在if语句中判断，就需要比较两个变量的type类型是否相同：
'''
print(type(123)==type(456))

print(type(123)==int)

print(type('abc')==type('123'))

print(type('abc')==str)

print(type('abc')==type(123))

'''
判断基本数据类型可以直接写int，str等，但如果要判断一个对象是否是函数怎么办？
可以使用types模块中定义的常量：
'''

import types
def fn():
    pass
    
print(type(fn)==types.FunctionType)
print(type(abs)==types.BuiltinFunctionType)
print(type(lambda x : x)==types.LambdaType)
print(type (( x for i in range(10)))==types.GeneratorType)


'''
使用isinstance()
对于class的继承关系来说，使用type()就很不方便。我们要判断class的类型，可以使用isinstance()函数。
我们回顾上次的例子，如果继承关系是
'''
class Animal(object):
    """docstring for [object Object]."""
    def __init__(self):
        pass
        
class Dog(Animal):
    """docstring for [object Object]."""
    def __init__(self):
        pass
    def __len__(self):
        return 100

class Husky(Dog) :
    """docstring for [object Object]."""
    def __init__(self):
        pass
        
a=Animal()
d=Dog()
h=Husky()

print(isinstance(h,Dog))

#实际类型是Dog的d也是Animal类型：
print(isinstance(d,Dog) and isinstance(d,Animal))

#能用type()判断的基本类型也可以用isinstance()判断：
print(isinstance('a', str))

print(isinstance(123, int))

print(isinstance(b'a', bytes))

#并且还可以判断一个变量是否是某些类型中的一种，比如下面的代码就可以判断是否是list或者tuple：
print(isinstance('hive',(str,tuple)))

'''
使用dir()
如果要获得一个对象的所有属性和方法，可以使用dir()函数，它返回一个包含字符串的list，
比如，获得一个str对象的所有属性和方法：
'''
print(dir("ABC"))

'''
类似__xxx__的属性和方法在Python中都是有特殊用途的，比如__len__方法返回长度。在Python中，
如果你调用len()函数试图获取一个对象的长度，实际上，在len()函数内部，
它自动去调用该对象的__len__()方法，所以，下面的代码是等价的：
'''
print(len("ABC"))
print("ABC".__len__())
print(len(d))

'''
剩下的都是普通属性或方法，比如lower()返回小写的字符串：
'''
print("ABC".lower())




'''
仅仅把属性和方法列出来是不够的，配合getattr()、setattr()以及hasattr()，
我们可以直接操作一个对象的状态：
'''

class MyObject(object):
    """docstring for [object Object]."""
    def __init__(self):
        self.x = 9
    def power(self):
        return self.x * self.x
        
obj = MyObject()

print(hasattr(obj,'x')) # 有属性'x'吗？

print(obj.x)

print(hasattr(obj,'y')) # 有属性'y'吗？

setattr(obj, 'y', 19) # 设置一个属性'y'

print(hasattr(obj, 'y')) # 有属性'y'吗？

print(getattr(obj, 'y')) # 获取属性'y'

print(obj.y) # 获取属性'y'

'''
如果试图获取不存在的属性，会抛出AttributeError的错误：
'''
#print(getattr(obj,'z'))

'''
可以传入一个default参数，如果属性不存在，就返回默认值：'''

print(getattr(obj,'z','default'))

'''
也可以获得对象的方法：
'''

print(hasattr(obj, 'power')) # 有属性'power'吗？
print(getattr(obj, 'power'))# 获取属性'power'
fn = getattr(obj, 'power') # 获取属性'power'并赋值到变量fn
print(fn) # fn指向obj.power
print(fn()) # 调用fn()与调用obj.power()是一样的

'''
小结

通过内置的一系列函数，我们可以对任意一个Python对象进行剖析，拿到其内部的数据。要注意的是，只有在不知道对象信息的时候，我们才会去获取对象信息。如果可以直接写：
'''




















