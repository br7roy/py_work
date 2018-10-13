#使用__slots__
class Student(object):
    pass
    

s=Student()
'''
给实例绑定一个属性：
'''
s.name="mike"        
print(s.name)
Student.name="hello"
print(Student.name)
del s.name
print(s.name)
del Student.name
print(hasattr(Student,'name'))

'''
给实例绑定一个方法：
'''
#定义一个方法
def set_age(self,age):
    self.age=age
    
from types import MethodType

s.set_age=MethodType(set_age,s)
s.set_age(25)
print(s.age)

'''
给一个实例绑定方法，对另一个实例是不起作用的
'''
s2=Student()
#s2.set_age(22)
'''
为了给所有实例都绑定方法，可以给class绑定方法：
'''
def set_score(self,score):
    self.score=score
Student.set_score=set_score

'''
给class绑定方法后，所有实例均可调用：
'''

s2.set_score(100)
print(s2.score)
s.set_score(77)
print(s.score)


'''
通常情况下，上面的set_score方法可以直接定义在class中，
但动态绑定允许我们在程序运行的过程中动态给class加上功能，这在静态语言中很难实现。
'''

'''
使用__slots__(插槽)
'''
"""
但是，如果我们想要限制实例的属性怎么办？比如，只允许对Student实例添加name和age属性。
为了达到限制的目的，Python允许在定义class的时候
定义一个特殊的__slots__变量，来限制该class实例能添加的属性：
"""
class Student(object):
    __slots__=('name','age')

s=Student()
s.name='mike'
s.age='30'
#s.score=100 绑定属性失败

try:
    s.score=100
except AttributeError as e:
    #raise AttributeError('score not allow')
    print('score not allow')
    
'''
使用__slots__要注意，__slots__定义的属性仅对当前类实例起作用，对继承的子类是不起作用的
'''

class GraduateStudent(Student):
    pass
g=GraduateStudent()        
g.score=100     #不起作用
print(g.score)

'''
除非在子类中也定义__slots__，这样，
子类实例允许定义的属性就是自身的__slots__加上父类的__slots__
'''

class GraduateStudent(Student):
    __slots__=('ambition','life')# 用tuple定义允许绑定的属性名称

g=GraduateStudent()
g.name='gg'
g.age=33
#g.ambition='big'
#g.score=100
    
    





