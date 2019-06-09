classmates = ['michael','Bob','Terry']
print(classmates)
#变量classmates就是一个list。用len()函数可以获得list元素的个数：
print('length:',len(classmates))
#用索引来访问list中每一个位置的元素，记得索引是从0开始的：
print(classmates[1])
#list是一个可变的有序表，所以，可以往list中追加元素到末尾：
classmates.append('Jack');
print(classmates)
#也可以把元素插入到指定的位置，比如索引号为2的位置：
classmates.insert(2,'Tim')
print(classmates)
#要删除list末尾的元素，用pop()方法：
classmates.pop();
print(classmates)
#要删除指定位置的元素，用pop(i)方法，其中i是索引位置：
classmates.pop(0)
print(classmates)
#要把某个元素替换成别的元素，可以直接赋值给对应的索引位置：
classmates[0] = 'Marry';
print(classmates)
#list里面的元素的数据类型也可以不同，比如：
L = ['Apple', 123, True]
#list元素也可以是另一个list，比如：
s = ['python', 'java', ['asp', 'php'], 'scheme']
print(s[2][0])
#如果一个list中一个元素也没有，就是一个空的list，它的长度为0：
L = []
print(len(L))
