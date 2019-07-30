#!/usr/bin/env bash
#生成表
# 创建表结构 不带模块名就是指定settings.py当中INSTALLED_APPS中指定的所有app
python manage.py migrate
# 让 Django 知道我们在我们的模型有一些变更
python manage.py makemigrations TestModel
# 重新初始化
python manage.py migrate --fake-initial
# 创建表结构
python manage.py migrate TestModel
# 自动执行数据库迁移并同步管理你的数据库结构的命令
python manage.py sqlmigrate TestModel 0001

# 查看数据库中的表生成对应的Python代码
python manage.py inspectdb
