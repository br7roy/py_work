# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pymongo
from datetime import datetime, timedelta
from dateutil.parser import parse

from conf.data_source import MysqlConf
from util import uuid_util
from util.num_util import transformFloatIfAvaliable

'''
该系列程序主要用于从mongodb数据库调取股票因子相关数据
'''


# %%MongoDb数据库数据获取函数
def connectMongo(location='remote'):
    # location表示读取哪个数据库，本地或云端，本地：local,云端：cloud
    global client
    try:
        flag = client.HOST
        if location == 'local' and client.address[0] != 'localhost':
            client = pymongo.MongoClient('localhost', 27017)
        if location == 'cloud' and client.address[0] == 'localhost':
            client = pymongo.MongoClient('47.111.96.190', 27017)
            db_auth = client.admin
            db_auth.authenticate("hbQuant", "hbzq767")
    except:
        if location == 'local':
            client = pymongo.MongoClient('localhost', 27017)
        else:
            client = pymongo.MongoClient('47.111.96.190', 27017)
            db_auth = client.admin
            db_auth.authenticate("hbQuant", "hbzq767")
    return client


# %%获取股票因子数据
# 获取因子暴露度数据
def getData_factorExposure(factorName, symbolList=None, startDate=None, endDate=None):
    # symbolList:list格式或字符串格式，当为None时，提取所有股票值
    # startDate:字符串或datetime格式，为None时表示从最开始的数据提取
    # endDate：字符串或datetime格式，为None是表示提取至最新数据
    if not startDate:
        startDate = datetime(2005, 1, 1)
    if not endDate:
        endDate = datetime.today()
    if type(startDate) == str:
        startDate = parse(startDate)
    if type(endDate) == str:
        endDate = parse(endDate)
    if type(symbolList) == str:
        symbolList = [symbolList]

    client = connectMongo()
    db = client['factorDatabase']
    coll = db[factorName]
    condition1 = {"tradeDate": {"$gte": startDate, "$lt": endDate + timedelta(1)}}
    if symbolList:
        condition2 = {}.fromkeys(symbolList, 1)
        condition2['tradeDate'] = 1
        condition2['_id'] = 0
    else:
        condition2 = dict()
        condition2['_id'] = 0

    tmp = []
    for document in coll.find(condition1, condition2):
        tmp.append(document)
    tmp = pd.DataFrame(tmp)
    tmp.set_index('tradeDate', inplace=True)
    tmp.sort_index(inplace=True)
    if tmp.shape[1] == 1:
        tmp = tmp.iloc[:, 0]
    return tmp


# 获取因子收益率数据
def getData_factorReturn(factorName=None, startDate=None, endDate=None):
    # factorName:因子名称,当设定为None时，提取所有因子，支持多个因子同时提取，采用list格式
    # startDate:字符串或datetime格式，为None时表示从最开始的数据提取
    # endDate：字符串或datetime格式，为None是表示提取至最新数据
    if not startDate:
        startDate = datetime(2005, 1, 1)
    if not endDate:
        endDate = datetime.today()
    if type(startDate) == str:
        startDate = parse(startDate)
    if type(endDate) == str:
        endDate = parse(endDate)
    if type(factorName) == str:
        factorName = [factorName]

    client = connectMongo()
    db = client['factorDatabase']
    coll = db['factorReturn']
    condition1 = {"tradeDate": {"$gte": startDate, "$lt": endDate + timedelta(1)}}
    if factorName:
        condition2 = {}.fromkeys(factorName, 1)
        condition2['tradeDate'] = 1
        condition2['_id'] = 0
    else:
        condition2 = dict()
        condition2['_id'] = 0

    tmp = []
    for document in coll.find(condition1, condition2):
        tmp.append(document)
    tmp = pd.DataFrame(tmp)
    tmp.set_index('tradeDate', inplace=True)
    tmp.sort_index(inplace=True)
    if tmp.shape[1] == 1:
        tmp = tmp.iloc[:, 0]
    return tmp


if __name__ == '__main__':
    # factorName即为mongodb数据库相关collection的名字，一次仅支持传入一个因子值
    from conf import mysqlops
    fs = ['value',
          'size',
          'beta',
          'earning',
          # 'factorReturn',
          'growth',
          'leverage',
          'liquidity',
          'momentum',
          'nonlinear_size',
          'size',
          'volatility']
    sql = 'insert into ' \
          'fof_stockexpousre (OBJECT_ID,trade_dt,s_windcode,indicator_code,factor_value,CREATE_USER_ID,CREATE_TIME,UPDATE_USER_ID,UPDATE_TIME)' \
          'values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    for fName in fs:
        print('start indicator:%s' % fName)
        valueExp = getData_factorExposure(fName)
        valueExp = valueExp.fillna("9999.000000")

        di = valueExp.to_dict()
        for k in di:
            # print("K===%s" % k)
            for v in di.get(k):
                s = uuid_util.gen_uuid()
                lsd = []
                oid = s[:5] + '-' + s[5:9] + '-' + s[9:13] + '-' + s[13:18] + '-' + s[18:]
                lsd.append(oid)
                r = v._date_repr.replace("-", "")
                lsd.append(r)
                lsd.append(k[:-2] + "." + k[-2:])
                lsd.append(fName)
                lsd.append(transformFloatIfAvaliable(di.get(k).get(v)))
                lsd.append("sys")
                lsd.append(datetime.now())
                lsd.append("sys")
                lsd.append(datetime.now())
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(lsd))

    # sizeExp = getData_factorExposure('size')
    # 因子收益率可以一次性提取所有数据
    # factorReturn = getData_factorReturn()
