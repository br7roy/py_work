#生成器
'''
通过列表生成式，我们可以直接创建一个列表。但是，受到内存限制，列表容量肯定是有限的。
而且，创建一个包含100万个元素的列表，不仅占用很大的存储空间，如果我们仅仅需要访问前面几个元素，
那后面绝大多数元素占用的空间都白白浪费了。
所以，如果列表元素可以按照某种算法推算出来，那我们是否可以在循环的过程中不断推算出后续的元素呢？
这样就不必创建完整的list，从而节省大量的空间。在Python中，这种一边循环一边计算的机制，
称为生成器：generator。
要创建一个generator，有很多种方法。第一种方法很简单，只要把一个列表生成式的[]改成()，就创建了一个generator：
'''
L = [x * x for x in range(10)]
print(L)#list
g = (x * x for x in range(10))
print(g)#一个生成器,使用next()获得下一个返回值

n = 0
a=[]
for b in g:
    a.append(b)
print(a)

def fib(max):
    n,a,b = 0,0,1;
    while n<max:
        yield b
        a,b = b,a+b
        n+=1
    return 'done'
#要把fib函数变成generator，只需要把print(b)改为yield b就可以了
#如果一个函数定义中包含yield关键字，那么这个函数就不再是一个普通函数，而是一个generator：
d= fib(10)



def odd():
    print('step 1')
    yield 1
    print('step 2')
    yield(3)
    print('step 3')
    yield(5)
o = odd()
print(next(o))
print(next(o))
print(next(o))
#print(next(o))#
'''
可以看到，odd不是普通函数，而是generator，在执行过程中，遇到yield就中断，下次又继续执行。执行3次yield后，已经没有yield可以执行了，所以，第4次调用next(o)就报错。

回到fib的例子，我们在循环过程中不断调用yield，就会不断中断。当然要给循环设置一个条件来退出循环，不然就会产生一个无限数列出来。

同样的，把函数改成generator后，我们基本上从来不会用next()来获取下一个返回值，而是直接使用for循环来迭代：
'''
print([f for f in d])#迭代器一旦使用for循环以后数据就消失了，貌似只能使用一次，类似与java stream??

#但是用for循环调用generator时，发现拿不到generator的return语句的返回值。如果想要拿到返回值，必须捕获StopIteration错误，返回值包含在StopIteration的value中：
g = fib(6)
while True:
     try:
         x = next(g)
         print('g:', x)
     except StopIteration as e:
         print('Generator return value:', e.value)
         break

 #总结
 '''
 迭代器一旦使用for循环以后数据就消失了，貌似只能使用一次，类似与java stream??
 '''

 #练习 杨辉三角

 
