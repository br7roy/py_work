#列表生成(List Comprehensions)
#Python内置的非常简单却强大的可以用来创建list的生成式
print(list(range(1,50)))

#方法一是循环：
L=[];
list = list(range(1,50))

for value in list:
    L.append(value*value);
print(L)

#列表生成式则可以用一行语句代替循环生成上面的list
print([value*value for value in list])
#还可以加过滤
print([value*value for value in list if value%2==0] )
#还可以使用两层循环，可以生成全排列：
L=[];
print([m+n for m in 'ABC' for n in 'XYZ'])

#列出当前目录下的所有文件和目录名，可以通过一行代码实现：
import os #导入os模块
print([d for d in os.listdir('.')]);# os.listdir可以列出文件和目录

#for循环其实可以同时使用两个甚至多个变量，比如dict的items()可以同时迭代key和value：
d = {'x': 'A', 'y': 'B', 'z': 'C' }
for k,v in d.items():
    print(k,v)

#因此，列表生成式也可以使用两个变量来生成list：

print([k+"="+v for k,v in d.items()]);

#把一个list中所有的字符串变成小写：
c = ['A','B','C']
print([v.lower() for v in c]);

#练习 转小写
L = ['Hello', 'World', 18, 'Apple', None]

print([s.lower() for s in L if isinstance(s,str)])
