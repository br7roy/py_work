#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys

base_dir = '/vol/paff_capct_id318868_vol1/msap/pafMerchantAss/'
now = datetime.now()
curdt = now.strftime('%Y%m%d')
length = len(sys.argv)


def showusage():
    print("Usage: she  <COMMAND>")
    print("  show [20180909]       查看是否生成绩效文件 ,不输入[]则默认当日")
    print("  eg:she show 20180909  查看2018年9月9日的文件目录")
    print("  del [20180909]        删除文件夹的绩效文件 ,不输入[]则默认当日")
    print("  eg:she del 20180909   删除2018年9月9日德文件目录")


pass


def do_show(cmd1, cmd2):
    pass


def do_del(cmd1, cmd2):
    pass


def do_logic(cmd1, cmd2):
    if cmd1 == 'show':
        do_show(cmd1, cmd2)
    elif cmd1 == 'del':
        do_del(cmd1, cmd2)
    else:
        showusage()
    pass


def show():
    print('len %s' % length)
    if length > 3 or length == 1:
        print(curdt)
        showusage()
    else:
        cmd1 = sys.argv[1]
        cmd2 = sys.argv[2]
        do_logic(cmd1, cmd2)


if __name__ == '__main__':
    show()

"""
如果想对python脚本传参数，python中对应的argc, argv(c语言的命令行参数)是什么呢？
需要模块：sys
参数个数：len(sys.argv)
脚本名：    sys.argv[0]
参数1：     sys.argv[1]
参数2：     sys.argv[2]

test.py

import sys
print "脚本名：", sys.argv[0]
for i in range(1, len(sys.argv)):
    print "参数", i, sys.argv[i]


>>>python test.py hello world
"""
