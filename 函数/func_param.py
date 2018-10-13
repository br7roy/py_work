#函数参数

#默认参数
def defaultExp(param,args=0):
    print(param,args)
defaultExp('hello','100')


#计算a2 + b2 + c2 + ……。
def calc(arg):
    sum = 0
    for val in arg:
        sum+=val*val
    return sum

list = [1,2,3,4,5,6,7]
print(calc(list))

#可变参数
def calc2(*arg):
    sum = 0
    for val in arg:
        sum+=val*val
    return sum
print(calc2(1,2,3,4,5))


#如果已经有一个list或者tuple，要调用一个可变参数怎么办？可以这样做：
print(calc2(list[0],list[1],list[2],list[3],list[4],list[5],list[6]))
#或者
print(calc2(*list))
#list表示把list这个list的所有元素作为可变参数传进去。这种写法相当有用，而且很常见。

#关键字参数
def person(name,age,**kw):
    print('name',name,'age',age,'other',kw)
#person('Michael',30,*['hehe','haha'])
person('Allen',26,**{'hello':'hehe','heihei':'123'})
