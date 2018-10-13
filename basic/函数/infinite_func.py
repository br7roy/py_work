#递归函数
#在函数内部，可以调用其他函数。如果一个函数在内部调用自身本身，这个函数就是递归函数。
#计算阶乘n! = 1 x 2 x 3 x ... x n

def infinite(arg):
    if arg==1:
        return 1
    else:
        return arg*infinite(arg-1)


print(infinite(3))

#解决递归调用栈溢出的方法是通过尾递归优化
#尾递归是指，在函数返回的时候，调用自身本身
#并且，return语句不能包含表达式。
#这样，编译器或者解释器就可以把尾递归做优化，
#使递归本身无论调用多少次，都只占用一个栈帧，不会出现栈溢出的情况。

def fact(arg):
    return depth_fact(arg,1)


def depth_fact(arg,product):
    if arg ==1:
        return product
    return depth_fact(arg-1,arg*product)

print(fact(3))



#Python标准的解释器没有针对尾递归做优化，任何递归函数都存在栈溢出的问题。
