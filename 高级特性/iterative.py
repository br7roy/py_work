#迭代
from collections import Iterable
d = {'a': 1, 'b': 2, 'c': 3}
for value in d:
    print(d.get(value))

for k,v in d.items():
    print(k,v)


print(isinstance('abc',Iterable))#str是否可迭代True
print(isinstance([1,2,3],Iterable))#list是否可以迭代True
print(isinstance(123,Iterable))#整数是否可以迭代 False

#Python内置的enumerate函数可以把一个list变成索引-元素对，这样就可以在for循环中同时迭代索引和元素本身：
for index,value in enumerate([1,2,3,4,5]):
    print(index,value)
#上面的for循环里，同时引用了两个变量，在Python里是很常见的，比如下面的代码：
for x, y in [(1, 1), (2, 4), (3, 9)]:
     print(x, y)

#练习，请使用迭代查找一个list中最小和最大值，并返回一个tuple：
def findMaxAndMin(arg):
    min = 0
    max = 0
    for value in arg:
        if value<min:
             min = value
        if value> max:
            max = value

    return (min, max)

def findMinAndMax(L):
        if L!=[]:
            max=min=L[0]
            for i in L:
                if i < min:
                    min = i
                if i > max:
                    max =i
            return (min,max)
        else:
             return(None,None)
print(findMaxAndMin([1,2,3,4,5,123,333,21]))
print(findMinAndMax([1,2,3,4,5,123,333,21]))
