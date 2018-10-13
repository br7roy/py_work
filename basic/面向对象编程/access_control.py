#访问限制
#!/usr/bin/bash

class Student(object):

    def __init__(self, name, score):
        self.__name = name
        self.__score = score

    def print_score(self):
        print('%s: %s' % (self.__name, self.__score))
    def set_score(self, score):
        if 0 <= score <= 100:
            self.__score = score
        else:
            raise ValueError('bad score')
    def get_name(self):
        return self.__name
    def get_score(self):
        return self.__score

'''
如果要让内部属性不被外部访问，可以把属性的名称前加上两个下划线__，在Python中，
实例的变量名如果以__开头，就变成了一个私有变量（private），只有内部可以访问，
外部不能访问，所以，我们把Student类改一改：
'''


"""最后注意下面的这种错误写法："""

bart = Student('Bart Simpson', 59)
print(bart.get_name())

bart.__name = 'New Name' # 设置__name变量！
print(bart.__name)

'''
表面上看，外部代码“成功”地设置了__name变量，但实际上这个__name变量和class内部的__name变量
不是一个变量！内部的__name变量已经被Python解释器自动改成了_Student__name，而外部代码给bart
新增了一个__name变量。不信试试：
'''

print(bart.get_name()) # get_name()内部返回self.__name











