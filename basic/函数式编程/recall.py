#返还函数
'''
函数作为返回值

高阶函数除了可以接受函数作为参数外，还可以把函数作为结果值返回。

我们来实现一个可变参数的求和。通常情况下，求和的函数是这样定义的：
'''
#非标准返还函数
def lazy_sum(*arg):
    def cnt(*arg):
        an = 0
        for i in arg:
            an+=i
        return an
    return cnt(*arg)
'''
如果不需要立刻求和，而是在后面的代码中，根据需要再计算怎么办？
可以不返回求和的结果，而是返回求和的函数：
'''

print(lazy_sum(1,2,3,4,5))

'''
second
#标准返还函数
'''
def lazy_sum2(*arg):
    def cnt2():
        an = 0
        for i in arg:
            an+=i
        return an
    return cnt2
f = lazy_sum2(1,2,3,4,5)
print(lazy_sum2(1,2,3,4,5)())
#返还求和函数
print(f)
#调用函数
print(f())

'''
在这个例子中，我们在函数lazy_sum中又定义了函数sum，并且，
内部函数sum可以引用外部函数lazy_sum的参数和局部变量，
当lazy_sum返回函数sum时，相关参数和变量都保存在返回的函数中，
这种称为“闭包（Closure）”的程序结构拥有极大的威力。
'''

'''
请再注意一点，当我们调用lazy_sum()时，每次调用都会返回一个新的函数，即使传入相同的参数：
'''
f1 = lazy_sum2(1,3,5,7,9)
f2 = lazy_sum2(1,3,5,7,9)
print(f1==f2)

'''
闭包

注意到返回的函数在其定义内部引用了局部变量args，所以，当一个函数返回了一个函数后，
其内部的局部变量还被新函数引用，所以，闭包用起来简单，实现起来可不容易。
另一个需要注意的问题是，返回的函数并没有立刻执行，而是直到调用了f()才执行。
我们来看一个例子：
'''
def count():
    fs = []
    for i in range(1, 4):
        def f():

            return i*i
        fs.append(f)
    return fs

f1, f2, f3 = count()
#返回闭包时牢记一点：返回函数不要引用任何循环变量，或者后续会发生变化的变量。
print(f1(),f2(),f3())
'''
如果一定要引用循环变量怎么办？方法是再创建一个函数，用该函数的参数绑定循环变量当前的值，
无论该循环变量后续如何更改，已绑定到函数参数的值不变：
'''

def count():
    def f(j):
        def g():
            return j*j
        return g
    fs = []
    for i in range(1,4):
        fs.append(f(i))
    return fs
    
f1,f2,f3 = count()
print(f1())
print(f2())
print(f3())

'''
练习

利用闭包返回一个计数器函数，每次调用它返回递增整数：
'''


def createCounter():
    def x():
        n=1
        while True:
            yield n
            n += 1
    it = x()
    def count():
        return next(it)
    return count

counterA = createCounter()
print(counterA(), counterA(), counterA(), counterA(), counterA(),counterA())    
    
    
    








































