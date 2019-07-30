import configparser

# 读取配置文件
CONF_PATH = 'F:/project/py_projects/research/quickstart/conf.ini'
cf = configparser.ConfigParser()
cf.read(CONF_PATH)  # 读取配置文件


# secs = cf.sections()  # 获取文件中所有的section(一个配置文件中可以有多个配置，如数据库相关的配置，邮箱相关的配置，每个section由[]包裹，即[section])，并以列表的形式返回
# print(secs)
#
# options = cf.options("mysql")  # 获取某个section名为Mysql-Database所对应的键
# print(options)
# items = cf.items("mysql")  # 获取section名为Mysql-Database所对应的全部键值对
# print(items)
#
# options = cf.options("redis")  # 获取某个section名为Mysql-Database所对应的键
# print(options)
# items = cf.items("redis")  # 获取section名为Mysql-Database所对应的全部键值对
# print(items)

class MysqlConf:
    def __init__(self):
        items = cf.items("mysql")
        res = dict(items)
        self.host = res['mysql_host']
        self.user = res['mysql_user']
        self.pwd = res['mysql_pwd']
        self.db = res['mysql_db']
        self.charset = res['mysql_charset']
        self.pool_num = res['mysql_pool_num']

    def __str__(self) -> str:
        return "mysql info:{" + self.host + "," + self.user + "," + self.pwd + "," \
               + self.db + "," + self.charset + "," + self.pool_num + "}"


class RedisConf:
    def __init__(self):
        items = cf.items("mysql")
        res = dict(items)
        self.host = res['redis_host']
        self.max_connection = res['redis_max_connections']

    def __str__(self) -> str:
        return "redis info:{" + self.host + "," + self.port + "}"


mysqlConf = MysqlConf()
redisConf = RedisConf()

# [mysql]
MYSQL_HOST = mysqlConf.host
MYSQL_USER = mysqlConf.user
MYSQL_PWD = mysqlConf.pwd
MYSQL_DB = mysqlConf.db
MYSQL_CHARSET = mysqlConf.charset
MYSQL_POOL_NUM = mysqlConf.pool_num

# [redis]
REDIS_HOST = redisConf.host
REDIS_MAX_CONNECTION = redisConf.max_connection


if __name__ == '__main__':
    pass
