#使用枚举类
"""
当我们需要定义常量时，一个办法是用大写变量通过整数来定义，例如月份：

JAN = 1
FEB = 2
MAR = 3
...
NOV = 11
DEC = 12
好处是简单，缺点是类型是int，并且仍然是变量。

更好的方法是为这样的枚举类型定义一个class类型，然后，每个常量都是class的一个唯一实例。
Python提供了Enum类来实现这个功能：
"""
from enum import Enum
Month = Enum('Month', ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'))

for name in Month:
    print(name)
    
for name , member in Month.__members__.items():
    print(name,'=>',member,',',member.value)

from enum import Enum , unique

@unique
class Weekday(Enum):
    Sun=0 #sun的value值被设定为0
    Mon=1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6

"""
@unique装饰器可以帮助我们检查保证没有重复值。

访问这些枚举类型可以有若干种方法：
"""

day1=Weekday.Mon
print(day1)
print(Weekday.Tue)
print(Weekday['Tue'])
print(Weekday.Tue.value)
print(day1 == Weekday.Mon)
print(day1==Weekday.Tue)
print(Weekday(1))
print(day1==Weekday(1))
#Weekday(7)

#可见，既可以用成员名称引用枚举常量，又可以直接根据value的值获得枚举常量。
"""
练习

把Student的gender属性改造为枚举类型，可以避免使用字符串：
"""

class Gender(Enum):
    Male = 0
    Female = 1

class Student(object):
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
#one
#Gender = Enum('Gender',('Male','Female'))

#two
@unique
class Gender(Enum):
    Male = 0
    Female = 1

# 测试:
bart = Student('Bart', Gender.Male)
if bart.gender == Gender.Male:
    print('测试通过!')
else:
    print('测试失败!')

















