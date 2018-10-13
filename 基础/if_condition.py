
age = 3
if age>=18:
    print('your age is upper',age)
elif age>=6:
    print('you are in school eh?',age)
else:
    print('your age is under',age,'good time play play play')

#if判断条件还可以简写，比如写：
#只要x是非零数值、非空字符串、非空list等，就判断为True，否则为False。

if True:
    print('hello python')

if 0:
    print('ok??')#not work!

#input()返回的数据类型是str，str不能直接和整数比较，必须先把str转换成整数。
#Python提供了int()函数来完成这件事情：
#如果输入字符串列入abc，会使int()函数报错，如何检查并捕获程序运行期的错误呢？
#后面的错误和调试会讲到。
birthday = input('birth:');
birthday = int(birthday)
if birthday>=2000:
    print('oh you are 00后!')
elif birthday>=1990:
    print('oh you are 90后!')
else:
    print('oh your are old!')
