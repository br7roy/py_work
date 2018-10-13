#错误处理

#高级语言通常都内置了一套try...except...finally...的错误处理机制，Python也不例外。

"""
try
"""
#让我们用一个例子来看看try的机制

try:
    print('try...')
    r = 10 / 0
    print('result:', r)
except ZeroDivisionError as e:
    print('except:',e)
finally:
    print('finally...')
print('END')

"""
错误应该有很多种类，如果发生了不同类型的错误，应该由不同的except语句块处理。没错，可以有多个except来捕获不同类型的错误：
"""
try:
    print('try...')
    r = 10 / int('a')
    print('result:', r)
except ValueError as e:
    print('ValueError:', e)
except ZeroDivisionError as e:
    print('ZeroDivisionError:', e)
finally:
    print('finally...')
print('END')

"""
此外，如果没有错误发生，可以在except语句块后面加一个else，当没有错误发生时，会自动执行else语句：
"""
try:
    print('try...')
    r = 10 / int('2')
    print('result:', r)
except ValueError as e:
    print('ValueError:', e)
except ZeroDivisionError as e:
    print('ZeroDivisionError:', e)
else:
    print('no error!')
finally:
    print('finally...')
print('END')

"""
Python的错误其实也是class，所有的错误类型都继承自BaseException，所以在使用except时需要
注意的是，它不但捕获该类型的错误，还把其子类也“一网打尽”。比如：
"""
try:
    # foo()
    pass
except ValueError as e:
    print('ValueError')
except UnicodeError as e:
    print('UnicodeError')
    
"""
第二个except永远也捕获不到UnicodeError，因为UnicodeError是ValueError的子类，
如果有，也被第一个except给捕获了。

Python所有的错误都是从BaseException类派生的，常见的错误类型和继承关系看这里
https://docs.python.org/3/library/exceptions.html#exception-hierarchy
"""

"""
使用try...except捕获错误还有一个巨大的好处，就是可以跨越多层调用，比如函数main()调用foo()，
foo()调用bar()，结果bar()出错了，这时，只要main()捕获到了，就可以处理：
"""
def foo(s):
    return 10 / int(s)

def bar(s):
    return foo(s) * 2

def main():
    try:
        bar('0')
    except Exception as e:
        print('Error:', e)
    finally:
        print('finally...')


"""
调用栈

如果错误没有被捕获，它就会一直往上抛，最后被Python解释器捕获，打印一个错误信息，然后程序退出。来看看err.py：
"""
# err.py:
def foo(s):
    return 10 / int(s)

def bar(s):
    return foo(s) * 2

def main():
    bar('0')

#main()

"""
记录错误

如果不捕获错误，自然可以让Python解释器来打印出错误堆栈，但程序也被结束了。既然我们能捕获错误，就可以把错误堆栈打印出来，然后分析错误原因，同时，让程序继续执行下去。

Python内置的logging模块可以非常容易地记录错误信息：
"""

# err_logging.py

import logging

def foo(s):
    return 10 / int(s)

def bar(s):
    return foo(s) * 2

def main():
    try:
        bar('0')
    except Exception as e:
        logging.exception(e)

main()
print('END')

"""
通过配置，logging还可以把错误记录到日志文件里，方便事后排查。

抛出错误

因为错误是class，捕获一个错误就是捕获到该class的一个实例。因此，错误并不是凭空产生的，
而是有意创建并抛出的。Python的内置函数会抛出很多类型的错误，我们自己编写的函数也可以抛出错误。

如果要抛出错误，首先根据需要，可以定义一个错误的class，选择好继承关系，然后，
用raise语句抛出一个错误的实例：
"""

# err_raise.py
class FooError(ValueError):
    pass

def foo(s):
    n = int(s)
    if n==0:
        raise FooError('invalid value: %s' % s)
    return 10 / n

#foo('0')#执行，可以最后跟踪到我们的自定义错误中

"""
只有在必要的时候才定义我们自己的错误类型。如果可以选择Python已有的内置的错误类型（
比如ValueError，TypeError），尽量使用Python内置的错误类型。
最后，我们来看另一种错误处理的方式：
"""
# error_reraise.py
def foo(s):
    n = int(s)
    if n==0:
        raise ValueError('invalid value: %s' % s)
    return 10/n
    
def bar():
    try:
        foo('0')
    except Exception as e:
        print('ValueError!')
        raise
bar()
"""
raise语句如果不带参数，就会把当前错误原样抛出。
此外，在except中raise一个Error，还可以把一种类型的错误转化成另一种类型：
"""
try:
    10 / 0
except ZeroDivisionError:
    raise ValueError('input error!')
"""
只要是合理的转换逻辑就可以，但是，决不应该把一个IOError转换成毫不相干的ValueError。
"""















