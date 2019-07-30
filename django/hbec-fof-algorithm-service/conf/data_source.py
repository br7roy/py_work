import configparser

import MySQLdb
# from DBUtils.SimplePooledDB import PooledDB
from DBUtils import PooledDB
from MySQLdb.cursors import DictCursor

# from conf.connection import create_connection_pool
from util.sys_constants import CONF_PATH

cf = configparser.ConfigParser()
cf.read(CONF_PATH)  # 读取配置文件

items = cf.items("mysql")
res = dict(items)

# mysqlConf = MysqlConf()
# [mysql]
MYSQL_HOST = res['mysql_host']
MYSQL_PORT = res['mysql_port']
MYSQL_USER = res['mysql_user']
MYSQL_PWD = res['mysql_pwd']
MYSQL_CHARSET = res['mysql_charset']

# 万德数据源
WIND_MYSQL_DB = res['wind_mysql_db']
WIND_MYSQL_POOL_NUM = res['wind_mysql_pool_num']
WIND_MIN_CACHED = res['wind_min_cached']  # 最小空闲连接
WIND_MAX_CACHED = res['wind_max_cached']  # 最大空闲连接
WIND_MAX_SHARED = res['wind_max_shared']  # 最大共享连接

# FOF数据源
FOF_MYSQL_DB = res['fof_mysql_db']
FOF_MYSQL_POOL_NUM = res['fof_mysql_pool_num']
FOF_MIN_CACHED = res['fof_min_cached']  # 最小空闲连接
FOF_MAX_CACHED = res['fof_max_cached']  # 最大空闲连接
FOF_MAX_SHARED = res['fof_max_shared']  # 最大共享连接


class MysqlConf:
    from enum import Enum

    DB = Enum('tp', ('fof', 'wind'))

    __wind_pool = None
    __fof_pool = None

    def __init__(self):
        self.host = MYSQL_HOST
        self.port = MYSQL_PORT
        self.user = MYSQL_USER
        self.pwd = MYSQL_PWD
        self.charset = MYSQL_CHARSET
        # self.wind_db = WIND_MYSQL_DB
        # self.wind_pool_num = WIND_MYSQL_POOL_NUM
        # self.wind_min_cached = WIND_MIN_CACHED
        # self.wind_max_cached = WIND_MAX_CACHED
        # self.wind_max_shared = WIND_MAX_SHARED
        self.fof_db = FOF_MYSQL_DB
        self.fof_pool_num = FOF_MYSQL_POOL_NUM
        self.fof_min_cached = FOF_MIN_CACHED
        self.fof_max_cached = FOF_MAX_CACHED
        self.fof_max_shared = FOF_MAX_SHARED
        # MysqlConf.__wind_pool = self.create_connection_pool(MysqlConf.DB.wind)
        MysqlConf.__fof_pool = self.create_connection_pool(MysqlConf.DB.fof)

    def create_connection_pool(self, dbtype):
        try:
            if dbtype is None or dbtype not in MysqlConf.DB:
                pass
            if dbtype is MysqlConf.DB.wind:
                pass
                # pool = PooledDB.PooledDB(MySQLdb, user=self.user, passwd=self.pwd, host=self.host,
                #                          port=int(self.port), db=self.wind_db, charset=self.charset,
                #                          cursorclass=DictCursor,
                #                          mincached=int(self.wind_min_cached), maxcached=int(self.wind_max_cached),
                #                          maxshared=int(self.wind_max_shared),
                #                          maxconnections=int(self.wind_pool_num), use_unicode=False)
                # return pool
            else:
                pool = PooledDB.PooledDB(MySQLdb, user=self.user, passwd=self.pwd, host=self.host,
                                         port=int(self.port), db=self.fof_db, charset=self.charset,
                                         cursorclass=DictCursor,
                                         mincached=int(self.fof_min_cached), maxcached=int(self.fof_max_cached),
                                         maxshared=int(self.fof_max_shared),
                                         maxconnections=int(self.fof_pool_num), use_unicode=False)
                return pool

        except Exception as e:
            raise Exception('conn datasource Excepts,%s!!!(%s).' % (self, str(e)))

    @staticmethod
    def get_connection(dbname):
        conn = None
        if dbname is MysqlConf.DB.wind:
            conn = MysqlConf.get_wind_conn()
        elif dbname is MysqlConf.DB.fof:
            conn = MysqlConf.get_fof_conn()
        else:
            pass
        return conn

    @staticmethod
    def get_wind_conn():
        global pl
        if MysqlConf.__wind_pool is None:
            pl = MysqlConf().create_connection_pool(MysqlConf.DB.wind)
        else:
            pl = MysqlConf.__wind_pool
        return pl.connection()

    @staticmethod
    def get_fof_conn():
        global pl
        if MysqlConf.__fof_pool is None:
            pl = MysqlConf().create_connection_pool(MysqlConf.DB.fof)
        else:
            pl = MysqlConf.__fof_pool
        return pl.connection()

    def __str__(self) -> str:
        return "mysql info:{" + self.host + "," + self.user + "," + "," \
                + self.fof_db + "," + self.fof_pool_num + "}"


class RedisConf:
    def __init__(self):
        items = cf.items("redis")
        res = dict(items)
        self.host = res['redis_host']
        self.max_connection = res['redis_max_connections']

    def __str__(self) -> str:
        return "redis info:{" + self.host + "," + self.max_connection + "}"


redisConf = RedisConf()

# [redis]
REDIS_HOST = redisConf.host
REDIS_MAX_CONNECTION = redisConf.max_connection

if __name__ == '__main__':
    pass
