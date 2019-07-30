from conf.data_source import MysqlConf
from util.exception.biz_error_handler import Error


def fetch_one(dbname, sql):
    connection = MysqlConf.get_connection(dbname)
    cur = connection.cursor()
    cur.execute(sql)
    res = cur.fetchone()
    cur.close()
    del cur
    del connection
    return res


def fetchmany(dbname, sql, size=65535):
    connection = MysqlConf.get_connection(dbname)
    cur = connection.cursor()
    cur.execute(sql)
    res = cur.fetchmany(size)
    del cur
    del connection
    return res


def fetchall(dbname, sql):
    connection = MysqlConf.get_connection(dbname)
    cur = connection.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    del cur
    del connection
    return res


def insert_one(dbname, sql, args):
    connection = MysqlConf.get_connection(dbname)
    cur = connection.cursor()
    cur.execute(sql, args)
    connection.commit()
    del cur
    del connection
    return 1


def del_data(tname=None, sqlPa=None):
    connection = MysqlConf.get_connection(MysqlConf.DB.fof)
    cur = connection.cursor()
    try:
        if sqlPa:
            sql = sqlPa
        else:
            sql = 'delete from %s' % tname
        cur.execute(sql)
        connection.commit()
    except:
        print('删除表数据失败 %s' % tname)
        connection.rollback()
        connection.close()
        return False
    connection.close()
    return True
