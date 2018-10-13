#偏函数


def int2(x,base=10):
    return int(x,base)

print(int2('1000'))

#使用偏函数
import functools

'''
用N进制转换
'''

int2 = functools.partial(int, base=2)

print(int2('111'))

#相当于：

kw = { 'base': 2 }
int('10010', **kw)


'''
选取最大值
'''

max2 = functools.partial(max,10)

print(max2(5, 6, 7))

#相当于
args = (10, 5, 6, 7)
max(*args)






