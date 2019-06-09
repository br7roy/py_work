#SET
#set和dict类似，也是一组key的集合，但不存储value。
#由于key不能重复，所以，在set中，没有重复的key。
#要创建一个set，需要提供一个list作为输入集合：
hahlist=[1,2,3,3,5,66,66]
hahaset =set(hahlist)
for val in hahaset:
    print('setParam:',val)
    pass

#通过add(key)方法可以添加元素到set中，可以重复添加，但不会有效果：
hahaset.add(66)

#通过remove(key)方法可以删除元素：
print(hahaset)
hahaset.remove(66)
print(hahaset)

#set可以看成数学意义上的无序和无重复元素的集合
#因此，两个set可以做数学意义上的交集、并集等操作：
heiheiset = set([3,5,7,8,10])
print(heiheiset)
#交集&
print(hahaset&heiheiset)
#并集|
print(hahaset|heiheiset)


#set和dict的唯一区别仅在于没有存储对应的value，但是，set的原理和dict一样，
#所以，同样不可以放入可变对象，因为无法判断两个可变对象是否相等，
#也就无法保证set内部“不会有重复元素”。试试把list放入set，看看是否会报错。

#heiheiset.add([1,2,3])无法放入list

#再议不可变对象

#上面我们讲了，str是不变对象，而list是可变对象。

#对于可变对象，比如list，对list进行操作，list内部的内容是会变化的，比如：
hahlist.sort();
print(hahlist)

#而对于不可变对象，比如str，对str进行操作呢：
str = 'abc';
print(str.replace('a','A'))#replace方法创建了一个新字符串'Abc'并返回
print(str)#这个值还是没变
