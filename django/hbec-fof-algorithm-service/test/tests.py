#!/usr/bin/python3
# -*- coding:utf-8 -*-


import json
from enum import Enum

import MySQLdb
from django.conf import settings
from django.core.cache import cache

from conf import mysqlops
from conf.data_source import MysqlConf
from fof.algorithm.template_fundComprehensiveScore import compScore2
from util.date_util import comparetime
from util.sys_constants import LOGGER_NAME


def read(user_name):
    key = 'user_id_of_' + user_name
    value = cache.get(key)
    if value is None:
        data = None
    else:
        data = json.loads(value)
    return data


def write(user_name):
    key = 'user_id_of_' + user_name
    cache.set(key, json.dumps("tomasLee"), 365 * 24 * 60 * 60)


def execSql(sql):
    db = MySQLdb.connect("127.0.0.1", "root", "root", "fund", charset='utf8')
    cursor = db.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    db.close()
    return res


def doquery(i):
    res = mysqlops.fetch_one(MysqlConf.DB.wind, sql)
    print(res)
    return res
    # import logging
    # logger = logging.getLogger(LOGGER_NAME)
    # logger.info(i)


def run_cache():
    settings.configure()
    conf = MysqlConf()

    sql = "SELECT s_info_windcode,s_info_indexwindcode  FROM chinamutualfundbenchmark "
    res = mysqlops.fetchmany(MysqlConf.DB.fof, sql)
    for n in res:
        wc = n['s_info_windcode'].decode()
        index = n['s_info_indexwindcode'].decode()
        cache.setdefault(wc, index)
        print('wind ma%s' % wc)
        print('index %s' % index)


def do():
    import time
    from util.date_util import compute_time
    from fof.algorithm.template_fundComprehensiveScore import compScore
    req = {}.fromkeys([i for i in range(1, 1000)], [99, 90, 92])

    start_time = time.time()
    res = []

    for k in req:
        btParms = dict()
        btParms['factorScores'] = req[k]
        btParms['factorWeights'] = ['0.30', '0.50', '0.20']
        fundScore = compScore(btParms)
        res.append((k, fundScore))

    var = list(map(
        lambda key: (key, res.append(compScore({'factorScores': req[key], 'factorWeights': ['0.30', '0.50', '0.20']}))),
        req.keys()))[0]
    rr = [(i, compScore({'factorScores': req[i], 'factorWeights': ['0.30', '0.50', '0.20']})) for i in req]
    hours, minutes, seconds = compute_time(start_time)

    print('耗时：%s' % "{:>02d}:{:>02d}:{:>02d}".format(hours, minutes, seconds))

    print(res)
    print(len(res))


def do2():
    btParms = dict()
    btParms['factorScores'] = [99, 0, 90, 93]
    btParms['factorWeights'] = ['0.15', '0.15', '0.20', '0.50']
    fundScore = compScore2(btParms)

    pass


if __name__ == '__main__':
    pass
#     str = {
#     "time": "1",
#     "indicators": [
#         {
#             "interval": ""
#         },
#         {
#             "max": ""
#         },
#         {
#             "year": "0.3"
#         },
#         {
#             "shape": ""
#         }
#     ]
# }
# run_cache()
# settings.configure()
# print(write('123'))
# print(read('123'))
# res = execSql(sql)
# print(res)
# from conf import data_source

# settings.configure()
# conf = MysqlConf()
# from conf import mysqlops, data_source

# sql = "select * from ashareguarantee limit 3"
# # import threading
# #
# # for i in range(1000):
# #     threading.Thread(target=doquery, name='asnyc', args=(i,)).start()

# from concurrent.futures import ThreadPoolExecutor,as_completed

# executor = ThreadPoolExecutor(max_workers=5)
# tasks = [executor.submit(doquery, sql) for i in range(10)]

# for feature in as_completed(tasks):
#     data = feature.result()
#     print('query result {}s'.format(data))

# DB = Enum('tp', ('fof', 'wind'))
#
# print(DB.fof)
# print(DB.wind)
