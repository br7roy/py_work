import datetime
import logging

import pandas as pd

from conf import mysqlops
from conf.data_source import MysqlConf
from conf.mysqlops import del_data
from fof.algorithm.getData_sql import getData_fundInformation
from fof.algorithm.template_singleIndexScore import getPublicData, indexScore_fund
from fof.model.model import OfflineTaskModel
from util import uuid_util, bus_const
from util.bus_const import n_cycle_tp, INDEX_CODE_NAME_CACHE, marketIndex
from util.date_util import formatDate2yyyymmdd
from util.exception.biz_error_handler import Error
from util.helper import get_indicator_id
from util.num_util import transformFloatIfAvaliable, transformString2Decimal
from util.sys_constants import LOGGER_NAME

log = logging.getLogger(LOGGER_NAME)


def interval_yield(model: OfflineTaskModel):
    if del_data('fof_return') == False:
        raise Error("删除历史数据失败，任务结束")

    indicatorInfo = model.taskModel
    taskName = indicatorInfo.value[0]

    indiId = get_indicator_id(taskName)

    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    updatedType = []
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    for symbol in fundSymbols:
        allIndicators = []
        fundType = fundClass_1[symbol]
        if fundType not in updatedType:
            for cycle in n_cycle_tp:
                btParms = {'indexName': taskName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                           'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                op = self.output
                val = op['factorValue']
                allIndicators.append(val)
                updatedType.append(fundType)
        df = pd.DataFrame(allIndicators).fillna(bus_const.blank)
        cols = df.columns.tolist()
        for col in cols:
            res = df[col]
            lst = res.values.tolist()

            lst = [transformFloatIfAvaliable(l) for l in lst]

            objId = uuid_util.gen_uuid()
            lst.insert(0, str(objId))
            lst.insert(1, str(indiId))
            lst.insert(2, col)
            date = formatDate2yyyymmdd()
            lst.insert(3, str(date))
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst.append("sys")
            lst.append(datetime.datetime.now())

            tp = tuple(lst)
            sql = "INSERT INTO fof_return (`OBJECT_ID`, `INDICATOR_ID`, `S_INFO_WINDCODE`, `TRADE_DT`, `THISYEAR_VALUE`, `QUARTER_VALUE`, `HALFYEAR_VALUE`, `YEAR_VALUE`, `TWOYEA_VALUE`, `THREEYEAR_VALUE`, `FIVEYEAR_VALUE`, `N1_VALUE`, `N2_VALUE`,  `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`, `DELETE_FLAG`) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,0)"

            mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
        allIndicators.clear()


def volatility(model: OfflineTaskModel):
    # 离线计算年化波动率
    if del_data('fof_variance') == False:
        raise Error("删除历史数据失败，任务结束")

    indicatorInfo = model.taskModel
    taskName = indicatorInfo.value[0]

    indiId = get_indicator_id(taskName)

    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    halfs = indicatorInfo.value[1]
    for half in halfs:
        updatedType = []
        allIndicators = []
        for symbol in fundSymbols:
            fundType = fundClass_1[symbol]
            if fundType not in updatedType:
                for cycle in n_cycle_tp:
                    btParms = {'indexName': taskName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                               'marketIndex': '',
                               'otherPar': half}
                    self = indexScore_fund(btParms, fundAdjNav, 'auto')
                    op = self.output
                    val = op['factorValue']
                    allIndicators.append(val)
                    updatedType.append(fundType)
            df = pd.DataFrame(allIndicators).fillna(bus_const.blank)
            cols = df.columns.tolist()
            for col in cols:
                res = df[col]
                lst = res.values.tolist()
                lst = [transformFloatIfAvaliable(l) for l in lst]

                objId = uuid_util.gen_uuid()
                lst.insert(0, str(objId))
                lst.insert(1, str(indiId))
                lst.insert(2, str(col))
                date = formatDate2yyyymmdd()
                lst.insert(3, str(date))
                lst.insert(4, transformString2Decimal(half))
                lst.append("sys")
                lst.append(datetime.datetime.now())
                lst.append("sys")
                lst.append(datetime.datetime.now())

                tp = tuple(lst)
                sql = "INSERT INTO fof_variance (`OBJECT_ID`, `INDICATOR_ID`, `J_WINDCODE`, `TRADE_DT`, `F_WEIGHT`, `THISYEAR_VALUE`, `QUARTER_VALUE`, `HALFYEAR_VALUE`, `YEAR_VALUE`, `TWOYEA_VALUE`, `THREEYEAR_VALUE`, `FIVEYEAR_VALUE`, `N1_VALUE`, `N2_VALUE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`, `DELETE_FLAG`) VALUES ( %s, %s, %s, %s, %s, %s, %s,%s, %s, %s,  %s, %s, %s, %s, %s, %s, %s,%s,0)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
            allIndicators.clear()


def sharpe_ratio(model: OfflineTaskModel):
    # 离线计算夏普比率
    if del_data('fof_sharpratio') == False:
        raise Error("删除历史数据失败，任务结束")

    indicatorInfo = model.taskModel
    taskName = indicatorInfo.value[0]
    indiId = get_indicator_id(taskName)
    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    updatedType = []
    # try:
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    for symbol in fundSymbols:
        allIndicators = []
        # symbolInfo = getData_fundInformation(symbol)
        # if 'FUND_INVESTTYPE' not in symbolInfo.keys():
        #     continue
        # fundType = symbolInfo['FUND_INVESTTYPE'][0]
        fundType = fundClass_1[symbol]
        if fundType not in updatedType:
            for cycle in n_cycle_tp:
                btParms = {'indexName': taskName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                           'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                op = self.output
                val = op['factorValue']
                allIndicators.append(val)
                updatedType.append(fundType)
        df = pd.DataFrame(allIndicators).fillna(bus_const.blank)
        cols = df.columns.tolist()
        for col in cols:
            res = df[col]
            lst = res.values.tolist()
            lst = [transformFloatIfAvaliable(l) for l in lst]

            objId = uuid_util.gen_uuid()
            lst.insert(0, str(objId))
            lst.insert(1, str(indiId))
            lst.insert(2, str(col))
            date = formatDate2yyyymmdd()
            lst.insert(3, str(date))
            lst.insert(4, indicatorInfo.value[1])
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst.append("sys")
            lst.append(datetime.datetime.now())
            tp = tuple(lst)
            sql = "INSERT INTO fof_sharpratio (`OBJECT_ID`, `INDICATOR_ID`, `J_WINDCODE`, `TRADE_DT`, `F_WEIGHT`, `THISYEAR_VALUE`, `QUARTER_VALUE`, `HALFYEAR_VALUE`, `YEAR_VALUE`, `TWOYEA_VALUE`, `THREEYEAR_VALUE`, `FIVEYEAR_VALUE`, `N1_VALUE`, `N2_VALUE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`, `DELETE_FLAG`) VALUES ( %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s,  %s, %s, %s, %s, %s,%s,0)"
            mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
        allIndicators.clear()
    # except Exception as e:
    #     print("===lst:", lst, "cycle:", cycle, "symbol:", symbol)
    #     log.exception(e)
    #     raise Error(e)


def maximum_drawdown(model: OfflineTaskModel):
    if del_data('fof_maxdrawdown') == False:
        raise Error("删除历史数据失败，任务结束")
    # 离线计算最大回撤
    indicatorInfo = model.taskModel
    taskName = indicatorInfo.value[0]
    indiId = get_indicator_id(taskName)
    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    updatedType = []
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    for symbol in fundSymbols:
        allIndicators = []
        fundType = fundClass_1[symbol]
        if fundType not in updatedType:
            for cycle in n_cycle_tp:
                btParms = {'indexName': taskName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                           'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                op = self.output
                val = op['factorValue']
                allIndicators.append(val)
                updatedType.append(fundType)
        df = pd.DataFrame(allIndicators).fillna(bus_const.blank)
        cols = df.columns.tolist()
        for col in cols:
            res = df[col]
            lst = res.values.tolist()

            lst = [transformFloatIfAvaliable(l) for l in lst]

            objId = uuid_util.gen_uuid()
            lst.insert(0, str(objId))
            lst.insert(1, str(indiId))
            lst.insert(2, col)
            date = formatDate2yyyymmdd()
            lst.insert(3, str(date))
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst.append("sys")
            lst.append(datetime.datetime.now())

            tp = tuple(lst)
            sql = "INSERT INTO fof_maxdrawdown (`OBJECT_ID`, `INDICATOR_ID`, `J_WINDCODE`, `TRADE_DT`, `THISYEAR_VALUE`, `QUARTER_VALUE`, `HALFYEAR_VALUE`, `YEAR_VALUE`, `TWOYEA_VALUE`, `THREEYEAR_VALUE`, `FIVEYEAR_VALUE`, `N1_VALUE`, `N2_VALUE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`, `DELETE_FLAG`) VALUES ( %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,  %s, %s, %s,0)"

            mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
        allIndicators.clear()


def calmar_ratio(model: OfflineTaskModel):
    # 离线计算卡玛比率
    if del_data('fof_calmaratio') == False:
        raise Error("删除历史数据失败，任务结束")
    indicatorInfo = model.taskModel
    taskName = indicatorInfo.value[0]
    indiId = get_indicator_id(taskName)
    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    updatedType = []
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    for symbol in fundSymbols:
        allIndicators = []
        fundType = fundClass_1[symbol]
        if fundType not in updatedType:
            for cycle in n_cycle_tp:
                btParms = {'indexName': taskName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                           'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                op = self.output
                val = op['factorValue']
                allIndicators.append(val)
                updatedType.append(fundType)
        df = pd.DataFrame(allIndicators).fillna(bus_const.blank)
        cols = df.columns.tolist()
        for col in cols:
            res = df[col]
            lst = res.values.tolist()

            lst = [transformFloatIfAvaliable(l) for l in lst]

            objId = uuid_util.gen_uuid()
            lst.insert(0, str(objId))
            lst.insert(1, str(indiId))
            lst.insert(2, col)
            date = formatDate2yyyymmdd()
            lst.insert(3, str(date))
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst.append("sys")
            lst.append(datetime.datetime.now())

            tp = tuple(lst)
            sql = "INSERT INTO fof_calmaratio (`OBJECT_ID`, `INDICATOR_ID`, `J_WINDCODE`, `TRADE_DT`, `THISYEAR_VALUE`, `QUARTER_VALUE`, `HALFYEAR_VALUE`, `YEAR_VALUE`, `TWOYEA_VALUE`, `THREEYEAR_VALUE`, `FIVEYEAR_VALUE`, `N1_VALUE`, `N2_VALUE`,  `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`, `DELETE_FLAG`) VALUES ( %s, %s, %s, %s, %s, %s, %s,%s, %s, %s,%s,%s, %s, %s, %s, %s, %s,0)"

            mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
        allIndicators.clear()


def information_ratio(model: OfflineTaskModel):
    # 离线计算信息比率

    if del_data('fof_inforatio') == False:
        raise Error("删除历史数据失败，任务结束")

    # sql = "delete from fof_inforatio "
    # mysqlops.fetch_one(MysqlConf.DB.fof, sql)
    indicatorInfo = model.taskModel
    taskName = indicatorInfo.value[0]
    indiId = get_indicator_id(taskName)
    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    updatedType = []
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    for symbol in fundSymbols:
        allIndicators = []
        fundType = fundClass_1[symbol]
        if fundType not in updatedType:
            for cycle in n_cycle_tp:
                btParms = {'indexName': taskName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                           'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                op = self.output
                val = op['factorValue']
                allIndicators.append(val)
                updatedType.append(fundType)
        df = pd.DataFrame(allIndicators).fillna(bus_const.blank)
        cols = df.columns.tolist()
        for col in cols:
            res = df[col]
            dd = res.values.tolist()

            lst = [transformFloatIfAvaliable(l) for l in dd]

            objId = uuid_util.gen_uuid()
            lst.insert(0, str(objId))
            lst.insert(1, str(indiId))
            lst.insert(2, col)
            date = formatDate2yyyymmdd()
            lst.insert(3, str(date))

            # idxVal = None
            # try:
            #     idxVal = CODE_INDEX_CACHE[col]
            # except:
            #     # 缓存没有查一次数据库
            #     sql = "SELECT s_info_windcode,s_info_indexwindcode  FROM chinamutualfundbenchmark where S_INFO_WINDCODE = '{}'".format(
            #         col)
            #     res = mysqlops.fetchmany(MysqlConf.DB.fof, sql)
            #     if res and 's_info_indexwindcode' in res and res['s_info_indexwindcode'] is not None:
            #         idxVal = res['s_info_indexwindcode'].decode()

            lst.insert(4, indicatorInfo.value[1])  # 比较基准wind代码
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst.append("sys")
            lst.append(datetime.datetime.now())

            tp = tuple(lst)
            sql = "INSERT INTO fof_inforatio (`OBJECT_ID`, `INDICATOR_ID`, `J_WINDCODE`, `TRADE_DT`, `B_WINDCODE`, `THISYEAR_VALUE`, `QUARTER_VALUE`, `HALFYEAR_VALUE`, `YEAR_VALUE`, `TWOYEA_VALUE`, `THREEYEAR_VALUE`, `FIVEYEAR_VALUE`, `N1_VALUE`, `N2_VALUE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`, `DELETE_FLAG`) VALUES ( %s, %s, %s, %s, %s, %s, %s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,0)"
            mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
        allIndicators.clear()


def other_indicator(model: OfflineTaskModel):
    # 离线计算其他指标

    indicatorInfo = model.taskModel

    indicatorId = model.extVal

    if del_data(sqlPa="delete from fof_index_value where INDICATOR_ID = '%s'" % indicatorId) == False:
        raise Error("删除历史数据失败，任务结束")

    if indicatorId not in INDEX_CODE_NAME_CACHE.keys():
        raise Error("指标id不存在:{}".format(indicatorId))

    indexName = INDEX_CODE_NAME_CACHE[indicatorId]

    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    updatedType = []
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    for symbol in fundSymbols:
        allIndicators = []
        fundType = fundClass_1[symbol]
        if fundType not in updatedType:
            for cycle in n_cycle_tp:
                btParms = {'indexName': indexName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                           'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                op = self.output
                val = op['factorValue']
                allIndicators.append(val)
                updatedType.append(fundType)
        df = pd.DataFrame(allIndicators).fillna(bus_const.blank)
        cols = df.columns.tolist()
        for col in cols:
            res = df[col]
            lst = res.values.tolist()
            lst = [transformFloatIfAvaliable(l) for l in lst]
            objId = uuid_util.gen_uuid()
            lst.insert(0, str(objId))
            lst.insert(1, str(indicatorId))
            lst.insert(2, col)
            date = formatDate2yyyymmdd()
            lst.insert(3, str(date))
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst.append("sys")
            lst.append(datetime.datetime.now())

            tp = tuple(lst)
            sql = "INSERT INTO fof_index_value (`OBJECT_ID`, `INDICATOR_ID`, `J_WINDCODE`, `TRADE_DT`, `THISYEAR_VALUE`, `QUARTER_VALUE`, `HALFYEAR_VALUE`, `YEAR_VALUE`, `TWOYEA_VALUE`, `THREEYEAR_VALUE`, `FIVEYEAR_VALUE`, `N1_VALUE`, `N2_VALUE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`, `DELETE_FLAG`) VALUES ( %s, %s, %s, %s, %s, %s,%s,%s,  %s,%s, %s, %s, %s, %s, %s, %s, %s,0)"

            mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
        allIndicators.clear()
