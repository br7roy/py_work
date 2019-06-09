#Map Reduce
def f(arg):
    return arg * arg;

#Map
print(list(map(f,[1,2,3,4,5,6,7,8,9])))

#把序列[1, 3, 5, 7, 9]变换成整数13579
from functools import reduce
def r(x,y):
    return x*10+y

print(reduce(r,[1,3,5,7,9]))

#把str 转为int
c={'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9}
def char2num(arg):
    return c.get(arg)
print(reduce(r,map(char2num,"321098876")))

#str2int的函数:
def str2int(s):
    def fn(x,y):
        return x*10 + y
    def char2num(arg):
        return c[arg]
    return reduce(fn,map(char2num,s))

print(str2int('123123123'))

#使用lambda
def str2int(s):
    return reduce(lambda x,y : x*10+y,map(char2num,s))

print(str2int('098098789709'))


'''
练习:利用map()函数，把用户输入的不规范的英文名字，变为首字母大写，其他小写的规范名字
'''

c=['adam', 'LISA', 'barT']
def p(param):
    n = 0
    L=''
    for i in param:
        if n==0:
            L+=(i.upper())
        else:
            L+=(i.lower())
        n+=1
    return L
print(list(map(p,c)))

'''
Python提供的sum()函数可以接受一个list并求和，请编写一个prod()函数，可以接受一个list并利用reduce()求积
'''
c=[1,2,3,4,5]

def prod(x,y):
    return x*y
from functools import reduce

print(reduce(lambda x,y:x*y,c))

'''
利用map和reduce编写一个str2float函数，把字符串'123.456'转换成浮点数123.456
'''
def str2float(arg):
    return reduce(lambda x, y:x+y/1000,map(int,arg.split('.')))

print(str2float('123.456'))
d = str2float('123.456')
print(isinstance(d,float))

'''
利用map和reduce编写一个str2float函数，把字符串'123.456'转换成浮点数123.456
'''









