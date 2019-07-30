import logging
from datetime import datetime

import pandas as pd

from conf import mysqlops
from conf.mysqlops import *
from fof.algorithm.ability_equityTiming import equityTimingAbility_manager
from fof.algorithm.ability_industryAlloction import industryAllocation_manager, getPublicDataAllocation
from fof.algorithm.ability_stockPicking import stockPickingAbility_manager, publicData_stockAndIndustry
from fof.algorithm.getData_sql import getData_fundManagerInfo_all, getData_fundSymbols
from fof.algorithm.template_fundFactorExposure import fundFactorExposure, publicData_stockFactor
from fof.algorithm.template_fundStyle_nav import fundStyle_nav
from fof.algorithm.template_fundTurnOver import fundTurnOver
from fof.algorithm.template_managerAnnualReturn import managerAnnualReturn
from fof.model.model import OfflineTaskModel
from util import uuid_util
from util.bus_const import blank
from util.num_util import transformFloatIfAvaliable, transformFloatIfAvaliable3
from util.num_util import transformFloatIfAvaliable4
from util.sys_constants import LOGGER_NAME

log = logging.getLogger(LOGGER_NAME)


def compute_manager_product(model: OfflineTaskModel):
    if not del_data('fof_manager_product'):
        raise Error("删除历史数据失败，任务结束")

    test = managerAnnualReturn()
    mgrDF = test.output.fillna("999999999.9999")
    # mgrDF.to_csv("C:\\Users\\futanghang\\Desktop\\nn.csv")
    # mgrDF = pd.read_csv("C:\\Users\\futanghang\\Desktop\\mgr.csv")
    for hls in mgrDF.values.tolist():
        objId = uuid_util.gen_uuid()
        ls = [transformFloatIfAvaliable3(l) for l in hls]
        lst = []
        lst.append(objId)
        lst.append(ls[0])
        lst.append(ls[1])
        lst.append(ls[2])
        lst.append(ls[5])
        lst.append(ls[3])
        lst.append(ls[4])
        lst.append(ls[6][0:-2])
        lst.append('sys')
        lst.append(datetime.now())
        lst.append("sys")
        lst.append(datetime.now())
        lst.append(0)
        sql = "insert into fof_manager_product values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # fs = sql % tuple(lst)
        mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(lst))


def equ_timing(model):
    if not del_data('fof_fund_timing'):
        raise Error("删除历史数据失败，任务结束")

    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)

    # 批量生成基金经理行业配置能力
    for i in range(len(managerInfo)):
        try:
            btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
            test = equityTimingAbility_manager(btParms)
            output = test.output
            timing = output['hisTiming']
            lst = timing.values.tolist()
            for ls in lst:
                ll = []
                id_ = uuid_util.gen_uuid()
                ll.append(id_)
                ll.append(output['symbol'])
                ll.append(output['managerId'])
                ll.append(output['manager'])
                ll.append(ls[0])  # start
                ll.append(ls[1])  # end
                ll.append(transformFloatIfAvaliable(ls[2]))  # RISING
                ll.append(transformFloatIfAvaliable(ls[3]))  # HOLDINGS_BEGIN
                ll.append(transformFloatIfAvaliable(ls[4]))  # HOLDINGS_END
                ll.append(transformFloatIfAvaliable(ls[5]))  # TIMING_RESULT
                ll.append(transformFloatIfAvaliable(ls[6]))  # HOLDINGS_RATIO
                ll.append(transformFloatIfAvaliable(output['winRatio']))
                ll.append(transformFloatIfAvaliable4(output['avgTimingContr']))
                ll.append("sys")
                ll.append(datetime.now())
                ll.append("sys")
                ll.append(datetime.now())
                sql = "INSERT INTO `fof`.`fof_fund_timing`(`OBJECT_ID`, `J_WINDCODE`, `MANAGER_ID`, `MANAGER_NAME`, `START_DATE`, `END_DATE`, `RISING`, `HOLDINGS_BEGIN`, `HOLDINGS_END`, `TIMING_RESULT`, `HOLDINGS_RATIO`,`TIMING_WIN_RATIO`,`AVG_CONTRIBUTION`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                insert_one(MysqlConf.DB.fof, sql, tuple(ll))
        except:
            pass


def industry_config_indust(model):
    if del_data('fof_fund_stock_industry') == False:
        raise Error("删除历史数据失败，任务结束")

    # sql = "delete from fof_fund_stock_industry "
    # mysqlops.fetch_one(MysqlConf.DB.fof, sql)

    # 离线计算基金经理行业配置能力
    # 为提高运行速度，公共数据一次性提取，并作为参数传入要调用的类
    stockIndus, indusNet = getPublicDataAllocation()

    # 批量生成基金经理任职区间信息
    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可
    '''

    # 批量生成基金经理行业配置能力
    for i in range(len(managerInfo)):
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        try:
            test = industryAllocation_manager(btParms, stockIndus, indusNet)
            output = test.output
            distributeDF = output['alloDistribute']  # fof_fund_stock_industry
            # for i in stockIndus.index:
            # print(i, "====", stockIndus[i])
            # fof_fund_stock_industry
            # sWindCode = i  # 玩的股票代码
            # indsName = stockIndus[i]  # 行业名称?
            wCode = output['symbol']  # 基金代码
            for index in distributeDF.index:
                res = distributeDF.loc[index]
                for si in res.index:
                    indus = index  # 中信行业名称
                    dt_ = si  # 时间
                    profit = res[si]  # 配置收益得分
                    id_ = uuid_util.gen_uuid()  # objId
                    lst = []
                    lst.append(id_)
                    lst.append(wCode)
                    lst.append(output['managerId'])
                    lst.append(output['manager'])
                    lst.append(dt_._short_repr.replace("-", ""))
                    lst.append(indus)
                    lst.append(transformFloatIfAvaliable4(profit))
                    lst.append("sys")
                    lst.append(datetime.now())
                    lst.append("sys")
                    lst.append(datetime.now())

                    ls = [transformFloatIfAvaliable4(i) for i in lst]
                    sql = "INSERT INTO `fof`.`fof_fund_stock_industry`(`OBJECT_ID`, `J_WINDCODE`, `MANAGER_ID`,`MANAGER_NAME`,`TRADE_DT`,  `INDUSTRY_NAME`, `STOCK_RATE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (  %s, %s,%s, %s,  %s, %s, %s, %s,%s, %s, %s)"
                    mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))
        except:
            pass


def industry_config_score(model):
    # sql = "delete from fof_fund_industry_score "
    # mysqlops.fetch_one(MysqlConf.DB.fof, sql)
    if not del_data('fof_fund_industry_score'):
        raise Error("删除历史数据失败，任务结束")

    # 为提高运行速度，公共数据一次性提取，并作为参数传入要调用的类
    stockIndus, indusNet = getPublicDataAllocation()

    # 批量生成基金经理任职区间信息
    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可
    '''

    # 批量生成基金经理行业配置能力
    for i in range(len(managerInfo)):
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        try:
            test = industryAllocation_manager(btParms, stockIndus, indusNet)
            output = test.output
            scoreDF = output['alloScore']  # fof_fund_industry_score
            for j, v in scoreDF.items():
                sVal = v  # 配置占股票市值比
                dt_ = j  # 时间
                id_ = uuid_util.gen_uuid()  # objId
                wCode = output['symbol']  # 基金代码
                lst = []
                lst.append(id_)
                lst.append(wCode)
                lst.append(output['managerId'])
                lst.append(output['manager'])
                lst.append(dt_._short_repr.replace("-", ""))
                lst.append(transformFloatIfAvaliable4(sVal))
                lst.append("sys")
                lst.append(datetime.now())
                lst.append("sys")
                lst.append(datetime.now())
                sql = "INSERT INTO `fof`.`fof_fund_industry_score`(`OBJECT_ID`, `J_WINDCODE`,  `MANAGER_ID`,`MANAGER_NAME`,`TRADE_DT`,  `RETURN_SCORE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(lst))
        except:
            pass


def industry_config_avgscore(model):
    if not del_data('fof_fund_industry_avgscore'):
        raise Error("删除历史数据失败，任务结束")

    # 为提高运行速度，公共数据一次性提取，并作为参数传入要调用的类
    stockIndus, indusNet = getPublicDataAllocation()

    # 批量生成基金经理任职区间信息
    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)

    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可
    '''

    # 批量生成基金经理行业配置能力
    for i in range(len(managerInfo)):
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        try:
            test = industryAllocation_manager(btParms, stockIndus, indusNet)
            output = test.output
            scoreDF = output['alloScore']  # fof_fund_stock_industry
            distributeDF = output['alloDistribute']  # fof_fund_industry_score
            evaluationDF = output['alloEvaluation']  # fof_fund_industry_avgscore
            rdf = evaluationDF.T
            for index in rdf.index:
                res = rdf.loc[index]
                indus = index  # 中信行业名称
                dt_ = '123'  # 时间
                score = res['平均配置得分']  # 配置收益得分
                bili = res['平均配置比例']
                zhanbi = res['配置次数占比']
                # id_ = uuid_util.gen_uuid()  # objId
                wCode = output['symbol']  # 基金代码
                lst = []
                id_ = uuid_util.gen_uuid()  # objId
                lst.append(id_)
                lst.append(wCode)
                lst.append(output['managerId'])
                lst.append(output['manager'])
                # lst.append(dt_._short_repr.replace("-", ""))
                lst.append(indus)
                lst.append(transformFloatIfAvaliable4(bili))
                lst.append(transformFloatIfAvaliable4(score))
                lst.append(transformFloatIfAvaliable4(zhanbi))
                lst.append("sys")
                lst.append(datetime.now())
                lst.append("sys")
                lst.append(datetime.now())
                sql = "INSERT INTO `fof`.`fof_fund_industry_avgscore`(`OBJECT_ID`, `J_WINDCODE`,  `MANAGER_ID`,`MANAGER_NAME`, `INDUSTRY_NAME`, `AVG_PERCENT`, `AVG_SCORE`, `AVG_TIMES`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s,  %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(lst))


        except:
            pass


# 筛选能力

def return_total(model):
    if not del_data('fof_fund_excess_return_total'):
        raise Error("删除历史数据失败，任务结束")

    # fof_fund_excess_return_total
    # 一次性调取需要用到的公共数据
    # logic_return_total()
    # 一次性调取需要用到的公共数据
    stockIndus, stockRet, indusRet, crIndus = publicData_stockAndIndustry()
    # 批量生成基金经理任职区间信息
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可.
    选股能力仅针对于股票型与混合型基金
    '''
    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)

    output_all = []
    for i in range(len(managerInfo)):
        # if i<5: #生产环境下删除该句，输入前100个仅为调试使用
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        try:
            test = stockPickingAbility_manager(btParms, stockIndus, stockRet, indusRet, crIndus)
            output = test.output
            # output['compareReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\compareReturnIndustry.csv")
            # output['excessReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnIndustry.csv")
            # output['excessReturnQuarter'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnQuarter.csv")
            # output['mainStcokReturn'].to_csv("c:\\users\\futanghang\\desktop\\mainStcokReturn.csv")
            pdict = output['excessReturnIndustry']
            for k, v in pdict.items():
                # k 行业，v 值
                indus = k
                val = v
                id_ = uuid_util.gen_uuid()  # objId
                wCode = output['symbol']  # 基金Wind代码
                managerName = output['manager']  # 基金经理名称

                managerId = output['managerId']  # 基金经理id

                lst = []
                lst.append(id_)
                lst.append(wCode)
                lst.append(managerId)
                lst.append(managerName)
                lst.append(indus)
                lst.append(val)
                lst.append("sys")
                lst.append(datetime.now())
                lst.append("sys")
                lst.append(datetime.now())
                ls = [transformFloatIfAvaliable4(i) for i in lst]
                sql = "INSERT INTO `fof`.`fof_fund_excess_return_total`(`OBJECT_ID`, `J_WINDCODE`, `MANAGER_ID`, `MANAGER_NAME`, `INDUSTRY_NAME`, `INDUSTRY_RETURN`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))
        except:
            output = {'managerId': managerInfo.loc[i, 'managerId'], 'symbol': managerInfo.loc[i, 'fund'],
                      'manager': managerInfo.loc[i, 'manager'], 'excessReturnQuarter': [],
                      'excessReturnIndustry': [],
                      'compareReturnIndustry': {}, 'mainStcokReturn': []}
        output_all.append(output)


def return_weight(model):
    if not del_data('fof_fund_excess_return_weight'):
        raise Error("删除历史数据失败，任务结束")
    # fof_fund_excess_return_weight
    # 一次性调取需要用到的公共数据
    stockIndus, stockRet, indusRet, crIndus = publicData_stockAndIndustry()
    # 批量生成基金经理任职区间信息
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可.
    选股能力仅针对于股票型与混合型基金
    '''
    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)

    output_all = []
    for i in range(len(managerInfo)):
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        try:
            test = stockPickingAbility_manager(btParms, stockIndus, stockRet, indusRet, crIndus)
            output = test.output
            # output['compareReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\compareReturnIndustry.csv")
            # output['excessReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnIndustry.csv")
            # output['excessReturnQuarter'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnQuarter.csv")
            # output['mainStcokReturn'].to_csv("c:\\users\\futanghang\\desktop\\mainStcokReturn.csv")
            dda = output['excessReturnQuarter']
            for k, v in dda.items():
                # k time，v ：value

                wCode = output['symbol']  # 基金Wind代码
                managerName = output['manager']  # 基金经理名称

                managerId = output['managerId']  # 基金经理id

                id_ = uuid_util.gen_uuid()  # objId
                lst = []
                lst.append(id_)
                lst.append(wCode)
                lst.append(managerId)
                lst.append(managerName)
                lst.append(k._short_repr.replace("-", ""))
                lst.append(v)
                lst.append("sys")
                lst.append(datetime.now())
                lst.append("sys")
                lst.append(datetime.now())
                ls = [transformFloatIfAvaliable4(i) for i in lst]
                sql = "INSERT INTO `fof`.`fof_fund_excess_return_weight`(`OBJECT_ID`, `J_WINDCODE`, `MANAGER_ID`, `MANAGER_NAME`, `TRADE_DT`, `EXCESS_RETURN`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))
        except Exception as e:
            pass


def return_(model):
    if not del_data('fof_fund_main_stock_return'):
        raise Error("删除历史数据失败，任务结束")
    # fof_fund_main_stock_return
    # logic_return_()
    # 一次性调取需要用到的公共数据
    stockIndus, stockRet, indusRet, crIndus = publicData_stockAndIndustry()
    # 批量生成基金经理任职区间信息
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可.
    选股能力仅针对于股票型与混合型基金
    '''
    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)

    output_all = []
    for i in range(len(managerInfo)):
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        try:
            test = stockPickingAbility_manager(btParms, stockIndus, stockRet, indusRet, crIndus)
            output = test.output
            # output['compareReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\compareReturnIndustry.csv")
            # output['excessReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnIndustry.csv")
            # output['excessReturnQuarter'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnQuarter.csv")
            # output['mainStcokReturn'].to_csv("c:\\users\\futanghang\\desktop\\mainStcokReturn.csv")
            pdict = output['compareReturnIndustry']
            for k in pdict:
                df = pdict[k]
                for index in df.index:
                    dt_ = index  # dt
                    di = df.loc[index].to_dict()
                    xuangushouyilv = di['选股收益率']
                    ershiwufenweishu = di['25分位数']
                    wushifenweishu = di['50分位数']
                    qishiwufenweishuy = di['75分位数']

                    wCode = output['symbol']  # 基金Wind代码
                    managerName = output['manager']  # 基金经理名称

                    managerId = output['managerId']  # 基金经理id

                    id_ = uuid_util.gen_uuid()  # objId
                    lst = []
                    lst.append(id_)
                    lst.append(wCode)
                    lst.append(managerId)
                    lst.append(managerName)
                    lst.append(dt_._short_repr.replace("-", ""))
                    lst.append(k)
                    lst.append(ershiwufenweishu)
                    lst.append(wushifenweishu)
                    lst.append(qishiwufenweishuy)
                    lst.append(xuangushouyilv)
                    lst.append("sys")
                    lst.append(datetime.now())
                    lst.append("sys")
                    lst.append(datetime.now())
                    ls = [transformFloatIfAvaliable4(i) for i in lst]
                    sql = "INSERT INTO `fof`.`fof_fund_main_stock_return`(`OBJECT_ID`, `J_WINDCODE`, `MANAGER_ID`, `MANAGER_NAME`, `TRADE_DT`, `INDUSTRY_NAME`, `25_POINTS`, `50_POINTS`, `75_POINTS`, `INDUSTRY_RETURN`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))
        except Exception as e:
            pass


def return_his(request):
    if not del_data('fof_fund_main_stock_return_his'):
        raise Error("删除历史数据失败，任务结束")
    # fof_fund_main_stock_return_his
    # logic_return_his()
    # 一次性调取需要用到的公共数据
    stockIndus, stockRet, indusRet, crIndus = publicData_stockAndIndustry()
    # 批量生成基金经理任职区间信息
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可.
    选股能力仅针对于股票型与混合型基金
    '''
    managerInfo = getData_fundManagerInfo_all()
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    tmp = []
    for row in managerInfo.index:
        if managerInfo.loc[row, 'fund'] in fundSymbols:
            tmp.append(managerInfo.loc[row].to_dict())
    managerInfo = pd.DataFrame(tmp, columns=managerInfo.columns)

    for i in range(len(managerInfo)):
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        try:
            test = stockPickingAbility_manager(btParms, stockIndus, stockRet, indusRet, crIndus)
            output = test.output
            # output['compareReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\compareReturnIndustry.csv")
            # output['excessReturnIndustry'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnIndustry.csv")
            # output['excessReturnQuarter'].to_csv("c:\\users\\futanghang\\desktop\\excessReturnQuarter.csv")
            # output['mainStcokReturn'].to_csv("c:\\users\\futanghang\\desktop\\mainStcokReturn.csv")
            ddis = output['mainStcokReturn']
            ddis=ddis.fillna(blank)
            for idx in ddis.index:
                # idx 股票代码，dict ：columns values
                stockId = idx  # dt
                di = ddis.loc[idx].to_dict()
                peizhiqishu = di['配置期数(季度)']
                pingjunquanzhong = di['平均权重(%)']
                indust = di['所属行业']
                chiyoujidupingjunshouyi = di['持有季度平均收益(%)']
                chiyoujidupingjunhangyechaoeshouyi = di['持有季度平均行业超额收益(%)']
                stockName = di['stockName']

                wCode = output['symbol']  # 基金Wind代码
                managerName = output['manager']  # 基金经理名称

                managerId = output['managerId']  # 基金经理id

                id_ = uuid_util.gen_uuid()  # objId
                lst = []
                lst.append(id_)
                lst.append(wCode)
                lst.append(managerId)
                lst.append(managerName)
                lst.append(stockId)
                lst.append(stockName)
                lst.append(indust)
                lst.append(transformFloatIfAvaliable4(peizhiqishu))
                lst.append(transformFloatIfAvaliable4(pingjunquanzhong))
                lst.append(transformFloatIfAvaliable4(chiyoujidupingjunshouyi))
                lst.append(transformFloatIfAvaliable4(chiyoujidupingjunhangyechaoeshouyi))
                lst.append("sys")
                lst.append(datetime.now())
                lst.append("sys")
                lst.append(datetime.now())
                ls = [transformFloatIfAvaliable4(i) for i in lst]
                sql = "INSERT INTO `fof`.`fof_fund_main_stock_return_his`(`OBJECT_ID`, `J_WINDCODE`, `MANAGER_ID`, `MANAGER_NAME`, `G_WINDCODE`, `STOCK_NAME`,`INDUSTRY_NAME`, `HOLDING_PERIODS`, `AVG_WEIGHTS`, `AVG_RETURN`, `AVG_RETURN_QUARTER`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))
        except Exception as e:
            pass


def net_value(model):
    if not del_data('fof_fundnav_style'):
        raise Error("删除历史数据失败，任务结束")
    # 基金净值风格划分        fof_fundnav_style
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    # fundSymbols=fundSymbols[0:20] #生产环境删除此句
    output_all = []
    i = 0
    for symbol in fundSymbols:
        i += 1
        btParms = {'symbol': symbol, 'cycle': '成立以来'}  # 离线入库时cycle设定为"成立以来"即可
        test = fundStyle_nav(btParms)
        output = test.output
        tmp = output['regStat']
        if tmp is None or len(tmp) == 0:
            continue
        for idx in tmp.index:
            di = tmp.loc[idx].to_dict()
            startDate = di['startDate']
            endDate = di['endDate']
            largeCoe = di['largeCoeff']
            smallCoe = di['smallCoeff']
            r2 = di['R2']

            lst = []
            id_ = uuid_util.gen_uuid()  # objId
            lst.append(id_)
            lst.append(output['symbol'])
            lst.append(startDate)
            lst.append(endDate)
            lst.append(largeCoe)
            lst.append(smallCoe)
            lst.append(r2)
            lst.append("sys")
            lst.append(datetime.now())
            lst.append("sys")
            lst.append(datetime.now())
            ll = [transformFloatIfAvaliable4(j) for j in lst]
            sql = "INSERT INTO `fof`.`fof_fundnav_style`(`OBJECT_ID`, `J_WINDCODE`, `START_DATE`, `END_DATE`, `LARGE_COEFFICIENTS`, `SMALL_COEFFICIENTS`,`R2`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
            mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ll))


def hand_turn_over(model):
    # 能力分析 - 持股集中度、换手率
    # fof_fund_stock_porfolio

    if not del_data('fof_fund_stock_porfolio'):
        raise Error("删除历史数据失败，任务结束")

    fundSymbols = getData_fundSymbols(['股票型', '混合型'])

    btParms = {'symbol': fundSymbols, 'startDate': '20020101', 'endDate': datetime.strftime(datetime.today(), '%Y%m%d')}
    self = fundTurnOver(btParms)
    output = self.output
    for i in output:
        val = output[i]
        for k, v in val.items():
            dt = k  # 时间
            value = v  # 值
            symbo = i  # 基金
            id_ = uuid_util.gen_uuid()
            ls = []
            ls.append(id_)
            ls.append(symbo)
            ls.append(dt._short_repr.replace("-", ""))
            ls.append(transformFloatIfAvaliable3(value))
            ls.append("sys")
            ls.append(datetime.now())
            ls.append("sys")
            ls.append(datetime.now())
            sql = "INSERT INTO `fof`.`fof_fund_stock_porfolio`(`OBJECT_ID`, `J_WINDCODE`, `TRADE_DT`, `CHANGE_RATE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))


def holding_style_main(model):
    if not del_data('fof_fund_tentop_stock_style'):
        raise Error("删除历史数据失败，任务结束")

    # 获取本模块公共数据
    factorExposure = publicData_stockFactor()

    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    # fundSymbols = fundSymbols[0:10]  # 生产环境删除此句
    typeList = ['mainStockHolding', 'allStockHolding']
    # 暴露度计算
    # for holdingType in typeList:
    for symbol in fundSymbols:
        btParms = {'symbol': symbol, 'holdingType': 'mainStockHolding'}
        test = fundFactorExposure(btParms, factorExposure)
        output = test.output
        tmp = output['hisExposure']
        # if holdingType == 'mainStockHolding':
            # 10 top
        for time in tmp:
            val = tmp[time]
            for idx in val.index:
                di = val.loc[idx].to_dict()
                exp = di['portExposure']
                expscore = di['portExposureScore']
                ls = []
                ls.append(uuid_util.gen_uuid())
                ls.append(output['symbol'])
                ls.append(time._short_repr.replace("-", ""))
                ls.append(idx)
                ls.append(transformFloatIfAvaliable3(exp))
                ls.append(transformFloatIfAvaliable3(expscore))
                ls.append("sys")
                ls.append(datetime.now())
                ls.append("sys")
                ls.append(datetime.now())
                sql = "INSERT INTO `fof`.`fof_fund_tentop_stock_style`(`OBJECT_ID`, `J_WINDCODE`, `TRADE_DT`, `INDICATOR_NAME`, `EXPOSE_VALUE`, `EXPOSE_SCORE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))


def holding_style_all(model):
    if not del_data('fof_fund_stock_style'):
        raise Error("删除历史数据失败，任务结束")

    # 获取本模块公共数据
    factorExposure = publicData_stockFactor()

    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    # fundSymbols = fundSymbols[0:10]  # 生产环境删除此句
    typeList = ['mainStockHolding', 'allStockHolding']
    # 暴露度计算
    for symbol in fundSymbols:
        btParms = {'symbol': symbol, 'holdingType': 'allStockHolding'}
        test = fundFactorExposure(btParms, factorExposure)
        output = test.output
        tmp = output['hisExposure']
        # if holdingType != 'mainStockHolding':
        for time in tmp:
            val = tmp[time]
            for idx in val.index:
                di = val.loc[idx].to_dict()
                exp = di['portExposure']
                expscore = di['portExposureScore']
                ls = []
                ls.append(uuid_util.gen_uuid())
                ls.append(output['symbol'])
                ls.append(time._short_repr.replace("-", ""))
                ls.append(idx)
                ls.append(transformFloatIfAvaliable3(exp))
                ls.append(transformFloatIfAvaliable3(expscore))
                ls.append("sys")
                ls.append(datetime.now())
                ls.append("sys")
                ls.append(datetime.now())
                sql = "INSERT INTO `fof`.`fof_fund_stock_style`(`OBJECT_ID`, `J_WINDCODE`, `TRADE_DT`, `INDICATOR_NAME`, `EXPOSE_VALUE`, `EXPOSE_SCORE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))
