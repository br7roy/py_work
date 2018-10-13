#多重继承

class Animal(object):
    pass

# 大类:
class Mammal(Animal):
    pass

class Bird(Animal):
    pass

# 各种动物:
class Dog(Mammal):
    pass

class Bat(Mammal):
    pass

class Parrot(Bird):
    pass

class Ostrich(Bird):
    pass
    
class Runable(object):
    pass
    
class Runnable(object):
    def run(self):
        print('running')
class Fly(object):
    def fly(self):
        print('flying')

#狗既是动物又会跑
class Dog(Animal,Runnable):
    def __init__(self,name):
        self.name=name
d=Dog("wangcai")
print(d.name)
print(d.run())

'''
通过多重继承，一个子类就可以同时获得多个父类的所有功能。
'''
'''
MixIn
在设计类的继承关系时，通常，主线都是单一继承下来的，例如，Ostrich继承自Bird。
但是，如果需要“混入”额外的功能，通过多重继承就可以实现，比如，让Ostrich除了继承自Bird外，
再同时继承Runnable。这种设计通常称之为MixIn。
'''

'''
MixIn的目的就是给一个类增加多个功能，这样，在设计类的时候，我们优先考虑通过多重继承来组合多个MixIn的功能，
而不是设计多层次的复杂的继承关系。

Python自带的很多库也使用了MixIn。举个例子，Python自带了TCPServer和UDPServer这两类网络服务，
而要同时服务多个用户就必须使用多进程或多线程模型，这两种模型由ForkingMixIn和ThreadingMixIn提供。
通过组合，我们就可以创造出合适的服务来。
'''


#比如，编写一个多进程模式的TCP服务
class MyTCPServer(TCPServer,ForkingMixIn):
    pass
    
    
#编写一个多线程模式的UDP服务
class MyUDPServer(TCPServer,ForkingMixIn):
    pass
    
#如果你打算搞一个更先进的协程模型，可以编写一个CoroutineMixIn










    












        


        
        