#调用函数
abs(-200)
max(2,100)
#数据类型转换
print(int("123"))
print(int(15.88))
print(float(12.22))
print(float("12.55"))
print(str(1.23))
print(bool(0))#False
print(bool(1))
print(bool(2))
print(bool(3))
print(bool(4))
a = abs#函数名其实就是指向一个函数对象的引用，完全可以把函数名赋给一个变量，相当于给这个函数起了一个“别名”：
print(a(-900))

#利用Python内置的hex()函数把一个整数转换成十六进制表示的字符串：
b = hex
print(b(18))
