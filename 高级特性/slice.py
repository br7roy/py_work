#切片
L = ['Michael', 'Sarah', 'Tracy', 'Bob', 'Jack']
#取前N个元素


def getEle(arg):
    var = []
    cnt = 0
    for value in L:
        if arg>len(L):
            raise ParamError('too big')
        if cnt<arg:
            cnt+=1
            var.append(value)
    return var

print(getEle(5))
H=slice(L,2)
print(H)

#对这种经常取指定索引范围的操作，用循环十分繁琐
#因此，Python提供了切片（Slice）操作符，能大大简化这种操作
print(L[0:3])#取前3个元素
#L[0:3]表示，从索引0开始取，直到索引3为止，但不包括索引3。即索引0，1，2，正好是3个元素。
print(L[:3])#如果第一个索引是0，还可以省略：
#从索引1开始，取出2个元素出来
print(L[1:3])
#倒数切片
print(L[-2:])#取最后2个元素
print(L[-2:-1])#取倒数第二个元素
#记住倒数第一个元素的索引是-1。



list=list(range(100))
print(list)

#前10个数，每两个取一个
print(list[:10:2])
#所有数，每5个取一个：
print(list[::5])
#甚至什么都不写，只写[:]就可以原样复制一个list：
print(list[:])
#tuple也是一种list，唯一区别是tuple不可变。因此，tuple也可以用切片操作，只是操作的结果仍是tuple：
print((0,1,2,3,4,5)[:3])
#字符串'xxx'也可以看成是一种list，每个元素就是一个字符。因此，字符串也可以用切片操作，只是操作结果仍是字符串：
print('ABCDEFG'[:3])
print('ABCDEFG'[::2])
