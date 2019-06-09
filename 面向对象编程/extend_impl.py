#继承多态
class Animal(object):
    pass

    def run(self):
        print('Animal is running')

class Dog(Animal):
    pass
    
    def run(arg):
        print('dog is running')
        return arg



class Cat(object):
    pass
    

bart = Dog()

bart.run()


b = Animal() # b是Animal类型
c = Dog() # c是Dog类型

#父类引用指向子类对象 多态
print(isinstance(c,Dog))
print(isinstance(c,Animal))


def run_twice(animal):
    animal.run()
    animal.run()
    
run_twice(Animal())

class Tortoise(Animal):
    def __init__(self):
        pass
    def run(self):
        print('Tortoise is running slow')
run_twice(Tortoise())

'''
静态语言 vs 动态语言

对于静态语言（例如Java）来说，如果需要传入Animal类型，则传入的对象必须是Animal类型或者它的子类，
否则，将无法调用run()方法。

对于Python这样的动态语言来说，则不一定需要传入Animal类型。我们只需要保证传入的对象有一个run()
方法就可以了
'''
class YeshengPig(object):
    """docstring for [object Object]."""
    def __init__(self):
        pass
    def run(self):
        print('yeshengPig is running!!!')

run_twice(YeshengPig())
        

        


        
        
        