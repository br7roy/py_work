#!/usr/bin/python
# -*- coding: utf-8 -*-

import getopt
import shutil
import sys
from datetime import datetime
from getopt import GetoptError

base_dir = '/vol/paff_capct_id318868_vol1/msap/pafMerchantAss/'
now = datetime.now()
curdt = now.strftime('%Y%m%d')
path = '/vol/paff_capct_id318868_vol1/msap/pafMerchantAss/' + curdt
fpath = path + '*'
length = len(sys.argv)


def show_usage():
    print("""
    Usage: tpp  <command> [args]
                -s    查看是否生成绩效文件 ,不输入则默认当日
                -d    删除文件夹的绩效文件 ,不输入则默认当日
                eg:tpp -s 20180909  查看2018年9月9日的文件目录
                eg:tpp -d 20180909   删除2018年9月9日的文件目录
        """)
    sys.exit()


try:
    opts, args = getopt.getopt(sys.argv[1:], 'dd:ss:h', ['help', 'del',
                                                         'show='])
except GetoptError as ignore:
    show_usage()


# print(sys.argv[1:])


def do_del(path):
    if path is '':
        print('is none')
        shutil.rmtree(fpath)
    else:
        shutil.rmtree(base_dir + path + '*')


def do_show(path):
    pass


# noinspection PyUnboundLocalVariable
for opt_name, opt_value in opts:
    print('hello')
    if opt_name in ('-h', '--help'):
        show_usage()
    if opt_name in ('-d', '--delete'):
        d_path = opt_value
        print("[*] delete run ", d_path)
        do_del(d_path)
        sys.exit(1)
    if opt_name in ('-s', '--show'):
        s_path = opt_value
        print("[*] show is ", s_path)
        do_show(s_path)
        # do something
        sys.exit(1)
    else:
        show_usage()


def check():
    if opts.__len__() == 0:
        show_usage()


if __name__ == '__main__':
    check()
