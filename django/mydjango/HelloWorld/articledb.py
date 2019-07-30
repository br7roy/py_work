# -*- coding: utf-8 -*-

from django.http import HttpResponse

from TestModel.models import *
import random


def testdb(request):
    # 数据库插入

    res = Reporter.objects.all()
    print(res)
    r = Reporter(full_name='John Smith')
    r.save()
    id = r.id
    print(id)
    r2 = Reporter.objects.all()
    print(r.full_name)

    rr = Reporter.objects.get(id=1)
    print(rr)
    r2 = Reporter.objects.get(full_name__startswith='John')



    return HttpResponse("<p>数据添加成功！</p>")

def insertdb(request):
    # 获取所有行数据 == select *
    list = Test.objects.all()
    # 获取符合条件的数据
    res2 = Test.objects.filter(id=1)
    # 获取单个对象
    res3 = Test.objects.get(id=1)
    # 限制返回数据 == offset 0 limit 2;
    Test.objects.order_by('name')[0:2]
    # 排序
    Test.objects.order_by('id')

    # 连锁使用
    Test.objects.filter(name='rod').order_by("id")

    resp1 = ""
    resp = ""
    # 输出所有内容
    for text in list:
        resp1 += text.name + ""
    resp = resp1
    return HttpResponse("<p>" + resp + "</p>")


# 修改数据可以使用 save() 或 update():
def updatedb(request):
    # 修改其中一个id=1的name字段，再save，相当于SQL中的UPDATE
    test = Test.objects.get(id=1)
    test.name = 'Google'
    test.save()

    # 另外一种方式
    # Test.objects.filter(id=1).update(name='Google')

    # 修改所有的列
    # Test.objects.all().update(name='Google')

    return HttpResponse("<p>修改成功</p>")


# 删除
def deletedb(request):
    # 删除id=2的数据
    test = Test(id=2)
    test.delete()

    # 第二种方式
    Test.objects.filter(id=1).delete()

    # 全部闪光
    Test.objects.all().delete()
    return HttpResponse("<p>删除成功</p>")
