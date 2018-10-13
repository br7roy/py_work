#coding=UTF-8
counter = 100
mile = 1.12
string = "string"
print counter #整形
print mile #浮点
print string #字符串

'''
标准数据类型
Python3 中有六个标准的数据类型：
Number（数字）
String（字符串）
List（列表）
Tuple（元组）
Sets（集合）
Dictionary（字典）
Python3 的六个标准数据类型中：
不可变数据（四个）：Number（数字）、String（字符串）、Tuple（元组）、Sets（集合）；
可变数据（两个）：List（列表）、Dictionary（字典）
'''
#Number（数字）
#Python3 支持 int、float、bool、complex（复数）。
a,b,c,d=5,5.00,True,4+3j

'''
String（字符串）
Python中的字符串用单引号(')或双引号(")括起来，同时使用反斜杠(\)转义特殊字符。
字符串的截取的语法格式如下：
索引值以 0 为开始值，-1 为从末尾的开始位置。
加号 (+) 是字符串的连接符， 星号 (*) 表示复制当前字符串，紧跟的数字为复制的次数。实例如下：

'''
str = 'Runoob'

print (str)          # 输出字符串
print (str[0:-1])    # 输出第一个到倒数第二个的所有字符
print (str[0])       # 输出字符串第一个字符
print (str[2:5])     # 输出从第三个开始到第五个的字符
print (str[2:])      # 输出从第三个开始的后的所有字符
print (str * 2)      # 输出字符串两次
print (str + "TEST") # 连接字符串

#Python 使用反斜杠(\)转义特殊字符，如果你不想让反斜杠发生转义，可以在字符串前面添加一个 r，表示原始字符串：
print('Ru\noob')
print(r'Ru\noob')
'''
另外，反斜杠(\)可以作为续行符，表示下一行是上一行的延续。也可以使用 \"\"\"...\"\"\" 或者 \'\'\'...\'\'\' 跨越多行。
注意，Python 没有单独的字符类型，一个字符就是长度为1的字符串。
'''
word = 'Python'
print(word[0], word[5])
