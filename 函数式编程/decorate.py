#装饰器
'''
由于函数也是一个对象，而且函数对象可以被赋值给变量，所以，通过变量也能调用该函数。
'''

def now(args):
    print('2018-07-16')
    return args
f = now #函数对象赋值给变量

print(f('hello world!'))#通过变量调用函数

'''
函数对象有一个__name__属性，可以拿到函数的名字：
'''

print(now.__name__)

'''
现在，假设我们要增强now()函数的功能，比如，在函数调用前后自动打印日志，但又不希望修改now()函数的定义，
这种在代码运行期间动态增加功能的方式，称之为“装饰器”（Decorator）。
本质上，decorator就是一个返回函数的高阶函数。所以，我们要定义一个能打印日志的decorator，可以定义如下
'''
def log(func):
    def wrapper(*args,**kw):
        print('call %s()' % func.__name__)
        return func(*args,**kw)
    return wrapper
    
@log
def now():
    print('2015-3-25')
print(now())


def log(text):
    def decorator(func):
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator
    
@log('execute')
def now():
    print('2015-3-25')
    
print(now())
print(now.__name__)#它们的__name__已经从原来的'now'变成了'wrapper'

import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*arg,**kw):
        print('%s %s():' % (text, func.__name__))
        return func(*arg,**kw)
    return wrapper
    
'''
或者针对带参数的decorator：
'''



def log(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator

'''
import functools是导入functools模块。模块的概念稍候讲解。
现在，只需记住在定义wrapper()的前面加上@functools.wraps(func)即可。
'''

'''
练习

请设计一个decorator，它可作用于任何函数上，并打印该函数的执行时间：
'''




# -*- coding: utf-8 -*-
import time, functools
def metric(fn):
    @functools.wraps(fn)
    def wrapper(*arg,**kw):
        print('%s executed in %s ms' % (fn.__name__, 10.24))
        return fn(*arg,**kw)
    return wrapper

    


@metric
def fast(x, y):
    time.sleep(0.0012)
    return x + y;
print(fast(1,2))









