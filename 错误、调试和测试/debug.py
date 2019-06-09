#调试
def foo(s):
    n = int(s)
    print('>>> n = %d' %n)
    return 10 / n
def main():
    foo('0')

#main()

"""
用print()最大的坏处是将来还得删掉它，想想程序里到处都是print()，运行结果也会包含很多垃圾信息。
所以，我们又有第二种方法。
"""

#断言
"""
凡是用print()来辅助查看的地方，都可以用断言（assert）来替代：
"""

def foo(s):
    n = int(s)
    assert n != 0, 'n is zero!'
    return 10 / n

def main():
    foo('0')
#main()

"""
程序中如果到处充斥着assert，和print()相比也好不到哪去。不过，启动Python解释器时可以用-O参数
来关闭assert：
关闭后，你可以把所有的assert语句当成pass来看。
"""

#logging
"""
把print()替换为logging是第3种方式，和assert比，logging不会抛出错误，而且可以输出到文件：

logging.info()就可以输出一段文本。运行，发现除了ZeroDivisionError，没有任何信息。怎么回事？

别急，在import logging之后添加一行配置再试试：
"""

import logging
logging.basicConfig(level=logging.INFO)

s = '0'
n = int(s)
logging.info('n = %d' % n)
#print(10 / n)

"""
这就是logging的好处，它允许你指定记录信息的级别，有debug，info，warning，error等几个级别，
当我们指定level=INFO时，logging.debug就不起作用了。同理，指定level=WARNING后，debug和info就不起作用了。这样一来，你可以放心地输出不同级别的信息，也不用删除，最后统一控制输出哪个级别的信息。

logging的另一个好处是通过简单的配置，一条语句可以同时输出到不同的地方，比如console和文件。
"""

#pdb
"""
第4种方式是启动Python的调试器pdb，让程序以单步方式运行，可以随时查看运行状态。我们先准备好程序：
"""
# err.py
s = '0'
n = int(s)
#print(10 / n)


#pdb.set_trace()
"""
这种通过pdb在命令行调试的方法理论上是万能的，但实在是太麻烦了，如果有一千行代码，要运行到第999行得敲多少命令啊。还好，我们还有另一种调试方法。
"""
# err.py
import pdb

s = '0'
n = int(s)
pdb.set_trace() # 运行到这里会自动暂停
print(10 / n)

#这个方式比直接启动pdb单步调试效率要高很多，但也高不到哪去。


#IDE
"""
如果要比较爽地设置断点、单步执行，就需要一个支持调试功能的IDE。目前比较好的Python IDE有：

Visual Studio Code：https://code.visualstudio.com/，需要安装Python插件。

PyCharm：http://www.jetbrains.com/pycharm/

另外，Eclipse加上pydev插件也可以调试Python程序。
"""





