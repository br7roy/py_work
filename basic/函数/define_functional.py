import math
#定义函数
#在Python中，定义一个函数要使用def语句，依次写出函数名、括号、括号中的参数和冒号:
#然后，在缩进块中编写函数体，函数的返回值用return语句返回。
def fname(arg):
    #数据类型检查
    if not isinstance(arg,(int,float)):
        raise TypeError('bad parameter!')
    if arg>=0:
        print('param 大于等于0',arg)
        return arg
    else:
        print('param 小于0',arg)
        return -arg;
#print(fname("123"))
print(fname(123))


#pass语句什么都不做，那有什么用？实际上pass可以用来作为占位符
#比如现在还没想好怎么写函数的代码，就可以先放一个pass，让代码能运行起来。
#空函数
def noop(arg):
    pass


#返回多个值
#函数可以返回多个值吗？答案是肯定的。
#比如在游戏中经常需要从一个点移动到另一个点，给出坐标、位移和角度，就可以计算出新的新的坐标：


def move(x,y,step,angle=0):
    nx = x + step * math.cos(angle)
    ny = y - step * math.sin(angle)
    return nx, ny
print(move(1,2,3))
x,y=move(1,2,3)
print(x,y)
#但其实这只是一种假象，Python函数返回的仍然是单一值：
#原来返回值是一个tuple！但是，在语法上，返回一个tuple可以省略括号，而多个变量可以同时接收一个tuple，
#按位置赋给对应的值，所以，Python的函数返回多值其实就是返回一个tuple，但写起来更方便

#小结

#定义函数时，需要确定函数名和参数个数；

#如果有必要，可以先对参数的数据类型做检查；

#函数体内部可以用return随时返回函数结果；

#函数执行完毕也没有return语句时，自动return None。

#函数可以同时返回多个值，但其实就是一个tuple。

def quadratic(a, b, c):
    if not (isinstance(a,(int,float))and isinstance(b,(int,float))and isinstance(c,(int,float))):
        raise TypeError('你输入的是错误的计算对象类型')
    if (b*b-4*a*c)>0:
        x1=(-b+math.sqrt(b*b-4*a*c))/(2*a)
        x2=(-b-math.sqrt(b*b-4*a*c))/(2*a)
        return x1,x2
    elif (b*b-4*a*c)==0:
        return -b/2*a
    else:
        return None

print(quadratic(5,8,3))

# 定义默认参数要牢记一点：默认参数必须指向不变对象！
def add_end(L=[None]):#L=[]这么定义是错的
    if L is None:
        L = []
    L.append('END')
    return L
#现在，无论调用多少次，都不会有问题：
print(add_end())
