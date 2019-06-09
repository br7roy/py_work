#tuple
#另一种有序列表叫元组：tuple。tuple和list非常类似
#但是tuple一旦初始化就不能修改，比如同样是列出同学的名字：
classmates = ('Michael', 'Bob', 'Tracy')
print(classmates)
#如果要定义一个空的tuple，可以写成()：
t=();
print(t)
#只有1个元素的tuple定义时必须加一个逗号,，来消除歧义：
singleTuple = (1,)
print (singleTuple)
#最后来看一个“可变的”tuple：
#Python在显示只有1个元素的tuple时，也会加一个逗号,，以免你误解成数学计算意义上的括号。

#最后来看一个“可变的”tuple：
#所谓不变指的是指向不变

t = ('a', 'b', ['A', 'B'])
print(t)
t[2][0] = 'X'
t[2][1] = 'Y'
print(t)
L = [
    ['Apple', 'Google', 'Microsoft'],
    ['Java', 'Python', 'Ruby', 'PHP'],
    ['Adam', 'Bart', 'Lisa']
]
# 打印Apple:
print(L[0][0])
# 打印Python:
print(L[1][1])
# 打印Lisa:
print(L[2][len(L[2])-1])
