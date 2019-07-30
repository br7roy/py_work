"""
业务常量模块
本模块包含：
1.计算函数需要的基本常量（不对前端暴露的）：回看时间长度，回看结束时间
2.定义计算处理过程中用到的Indicator枚举：该枚举包括最终再fof_task表中task_name的存放之
3.填充pandas计算结果集类型为Nan的常量
4.任务表的状态枚举：每一次进行批量计算任务时作为fof_task表中task_status字段的存放值
5.缓存加载：系统启动加载数据库必要缓存数据，使用 CODE_INDEX_CACHE 进行读取

"""
import logging
from datetime import date
from enum import Enum

from conf import mysqlops
from conf.data_source import MysqlConf
from util.date_util import getQunian, getQiannian, comparetime
from util.sys_constants import LOGGER_NAME

log = logging.getLogger(LOGGER_NAME)


class TaskModel(Enum):
    qujianshouyilv = '区间收益率', None
    xiapubilv = '夏普比率', '0.035'
    nianhuabodonglv = '年化波动率', ('0', '0.5', '0.33', '0.67')
    zuidahuiche = '最大回撤', None
    kamabilv = '卡玛比率', None
    xinxibilv = '信息比率', '000906.SH'
    qitazhibiao = '其他指标', '0.035'
    zhibiaodafen = '指标打分', None
    jinglichanpin = '基金经理产品', None
    jingliNengli = '基金经理股票择时能力评价模型', None
    jingliPeizhiNengli_stock = '基金经理行业配置能力-fof_fund_stock_industry', None
    jingliPeizhiNengli_score = '基金经理行业配置能力-fof_fund_industry_score', None
    jingliPeizhiNengli_avgscore = '基金经理行业配置能力-fof_fund_industry_avgscore', None
    jingliShaixuanNengli_return_total = '基金经理股票筛选能力-fof_fund_excess_return_total', None
    jingliShaixuanNengli_return_weight = '基金经理股票筛选能力-fof_fund_excess_return_weight', None
    jingliShaixuanNengli_return = '基金经理股票筛选能力-fof_fund_main_stock_return', None
    jingliShaixuanNengli_return_his = '基金经理股票筛选能力-fof_fund_main_stock_return_his', None
    jinglifengge_profit_style = '基金经理风格分析-fof_fundnav_style', None
    jinglifengge_hand_change_rate = '基金经理风格分析-fof_fund_stock_porfolio', None
    jinglifengge_holding_stype_main = '基金经理风格分析持仓风格10大-fof_fund_tentop_stock_style', None
    jinglifengge_holding_stype_all = '基金经理风格分析持仓风格全部-fof_fund_stock_style', None
    stockexpousre = '因子库导入-fof_stockexpousre', None
    stockRiskSingle = '风险因子业绩归因模块 fof_single_attr_riskmodel', None
    stockRiskMultiple = '风险因子业绩归因模块 fof_multi_attr_riskmodel', None


marketIndex = '000906.SH'

otherPa = '0.035'

blank = '9999999999999.999999'


class TaskStatus(Enum):
    accept = '0', '已接受'
    ok = '1', '成功'
    fail = '2', '失败'


# 回看时间 今年以来，3个月，6个月，最近1年，最近2年，最近3年，最近5年 ,这个顺序不能乱和插入表中字段相关
n_cycle_tp = ('今年以来', '3/12', '6/12', '1', '2', '3', '5', '去年', '前年')
n2_cycle_tp = ('今年以来', '3/12', '6/12', '1', '2', '3', '5', '去年', '前年', '任职以来', '成立以来')

cycle_score = ('今年以来', '3/12', '6/12', '1', '2', '3', '5')

CODE_INDEX_CACHE = {}
CODE_UPDTIME_CACHE = {}
INDEX_CODE_NAME_CACHE = {}
INDEX_NAME_CODE_CACHE = {}


def load_cache():
    load_table_info()


def load_table_info():
    log.info("load data from mysql start")
    log.info("starting load data from mysql ,table name %s", 'chinamutualfundbenchmark')
    sql = "SELECT s_info_windcode,s_info_indexwindcode  FROM chinamutualfundbenchmark "
    res = mysqlops.fetchmany(MysqlConf.DB.fof, sql)
    for n in res:
        wc = n['s_info_windcode']
        index = n['s_info_indexwindcode']
        CODE_INDEX_CACHE.setdefault(wc.decode() if wc else None, index.decode() if index else None)
    log.info("starting load data from mysql ,table name %s", 'chinamutualfunddescription')

    sql = "SELECT F_INFO_WINDCODE,F_INFO_SETUPDATE FROM chinamutualfunddescription"

    res = mysqlops.fetchmany(MysqlConf.DB.fof, sql)

    for i in res:
        code = i['F_INFO_WINDCODE']
        upd = i['F_INFO_SETUPDATE']
        nowtime = date.today()
        if upd:
            upd = comparetime(str(nowtime).replace("-", ""), upd.decode())
        CODE_UPDTIME_CACHE.setdefault(code.decode() if code else None, upd)

    sql = "select fi.INDICATOR_CODE,fi.INDICATOR_NAME from fof_index fi"
    res = mysqlops.fetchmany(MysqlConf.DB.fof, sql)
    log.info("starting load data from mysql ,table name %s", 'fof_index')
    for i in res:
        code = i['INDICATOR_CODE']
        name = i['INDICATOR_NAME']
        INDEX_CODE_NAME_CACHE.setdefault(code.decode() if code else None, name.decode() if name else None)
    INDEX_NAME_CODE_CACHE.update({(v, k) for k, v in INDEX_CODE_NAME_CACHE.items()})

    log.info("load data from mysql done")
