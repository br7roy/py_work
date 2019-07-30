# -*- coding: utf-8 -*-
"""基金数据获取函数：sql接口"""

import MySQLdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.parser import parse

'''
def execSql(sql):
    db = MySQLdb.connect("10.0.29.79", "yunying", "u=DdgLskLg", "winddb", charset='utf8' )
    cursor = db.cursor()    #创建一个游标对象
    cursor.execute(sql)    #执行SQL语句，注意这里不返回结果，只是执行而已
    res = cursor.fetchall()    #fetchall方法返回所有匹配的元组，给出一个大元组（每个元素还是一个元组）
    db.close()
    return res

'''


# 行业指数映射，默认为中信行业
def industryMap(indusType='CI'):
    if indusType == 'CI':
        indus = {'石油石化': 'CI005001.WI', '煤炭': 'CI005002.WI', '有色金属': 'CI005003.WI',
                 '钢铁': 'CI005005.WI', '基础化工': 'CI005006.WI', '建筑': 'CI005007.WI', '建材': 'CI005008.WI',
                 '轻工制造': 'CI005009.WI', '机械': 'CI005010.WI', '电力设备': 'CI005011.WI', '国防军工': 'CI005012.WI',
                 '汽车': 'CI005013.WI', '商贸零售': 'CI005014.WI', '餐饮旅游': 'CI005015.WI', '家电': 'CI005016.WI',
                 '纺织服装': 'CI005017.WI', '医药': 'CI005018.WI', '食品饮料': 'CI005019.WI', '农林牧渔': 'CI005020.WI',
                 '银行': 'CI005021.WI', '非银行金融': 'CI005022.WI', '房地产': 'CI005023.WI', '交通运输': 'CI005024.WI',
                 '电子元器件': 'CI005025.WI', '通信': 'CI005026.WI', '计算机': 'CI005027.WI', '传媒': 'CI005028.WI',
                 '电力及公用事业': 'CI005004.WI', '综合': 'CI005029.WI'}
    else:
        pass
    return indus


def fundClassMap(classify='windFirst'):
    fundClassMap_1 = {'股票型基金': '2001010100000000', '混合型基金': '2001010200000000', '债券型基金': '2001010300000000',
                      '货币市场型基金': '2001010400000000', '另类投资基金': '2001010600000000', '国际(QDII)基金': '2001010800000000'}

    fundClassMap_2 = {'国际(QDII)债券型基金': '2001010803000000', '中长期纯债型基金': '2001010301000000',
                      '被动指数型基金': '2001010102000000', '股票多空基金': '2001010601000000',
                      '偏股混合型基金': '2001010201000000', '偏债混合型基金': '2001010203000000',
                      '混合债券型二级基金': '2001010304000000', '平衡混合型基金': '2001010202000000',
                      '混合债券型一级基金': '2001010303000000', '商品型基金': '2001010607000000',
                      'REITs基金': '2001010605000000', '短期纯债型基金': '2001010302000000',
                      '普通股票型基金': '2001010101000000', '增强指数型债券基金': '2001010306000000',
                      '国际(QDII)股票型基金': '2001010801000000', '灵活配置型基金': '2001010204000000',
                      '国际(QDII)混合型基金': '2001010802000000', '被动指数型债券基金': '2001010305000000',
                      '增强指数型基金': '2001010103000000', '国际(QDII)另类投资基金': '2001010804000000'}
    if classify == 'windFirst':
        return fundClassMap_1
    elif classify == 'windSecond':
        return fundClassMap_2


def execSql(sql):
    db = MySQLdb.connect("10.0.30.59", "yanjs", "123123", "fof", charset='utf8')
    cursor = db.cursor()  # 创建一个游标对象
    cursor.execute(sql)  # 执行SQL语句
    res = cursor.fetchall()  # 返回所有匹配的元组
    db.close()
    return res


'''
def execSql(sql):
    db = MySQLdb.connect("10.0.29.79", "yunying", "u=DdgLskLg", "winddb", charset='utf8' )
    cursor = db.cursor()    #创建一个游标对象
    cursor.execute(sql)    #执行SQL语句，注意这里不返回结果，只是执行而已
    res = cursor.fetchall()    #fetchall方法返回所有匹配的元组，给出一个大元组（每个元素还是一个元组）
    db.close()
    return res

'''


# 填补中间空值
def fillna_mid(fundData):
    if fundData.ndim == 1:
        fundData = pd.DataFrame(fundData)
    for symbol in fundData.columns:
        fundPriceData = fundData[symbol].copy()
        tmp = fundPriceData.dropna(axis=0)
        if len(tmp) > 0:
            firstDate = tmp.index[0]
            lastDate = tmp.index[-1]
            fundPriceData = fundPriceData[firstDate:lastDate].fillna(method='ffill')
            fundData.loc[firstDate:lastDate, symbol] = fundPriceData
    return fundData if fundData.shape[1] > 1 else fundData.iloc[:, 0]


# %%基金数据
# 根据基金类型名称，获取基金代码（含已清算基金）
def getData_fundSymbols(fundType=None, classify='windFirst', status=1):
    # fundType:基金类型，可以是单个基金类型，也可以是多个基金类型 ,当为空值时，代表全部标的
    # classsify:基金分类基本，windFirst，windSecond
    # status代表基金存续状态，0为全部基金，涵盖已清算，1为仅当前处于运行的基金

    # 若输出为非None值，将基金类型转为对应的类型代码
    if fundType:
        fundClass = fundClassMap(classify)
        if type(fundType) is str:
            fundType = [fundType]
            # 兼容代码，若输入名称缺少基金二字，则自动补全
        tmp = []
        for m in fundType:
            if '基金' not in m:
                tmp.append(m + '基金')
            else:
                tmp.append(m)
        fundType = tmp

        # 将基金类型名称转为基金类型代码
        fundType = [fundClass[m] for m in fundType]
        # 统一格式
        if type(fundType) is list and len(fundType) == 1:
            fundType = fundType[0]

    if status == 0:  # 全部基金
        if not fundType:
            sql = 'select F_INFO_WINDCODE from ChinaMutualFundDescription'
        else:
            sql = 'select F_INFO_WINDCODE,S_INFO_SECTOR,S_INFO_SECTORENTRYDT from chinamutualfundsector \
            where left(s_info_sector,6)="200101" order by F_INFO_WINDCODE,S_INFO_SECTORENTRYDT'

    else:  # 当前存续的基金
        if not fundType:
            sql = 'select F_INFO_WINDCODE from ChinaMutualFundDescription where f_info_status=101001000'
        else:
            if type(fundType) == str:
                if classify == 'windFirst':  # 一级分类
                    sql = 'select f_info_windcode from chinamutualfunddescription \
                    where f_info_windcode in (select F_INFO_WINDCODE from chinamutualfundsector \
                    where left(s_info_sector,8)=' + fundType[:8] + ' and CUR_SIGN=1) \
                    and f_info_status=101001000'
                else:
                    sql = 'select f_info_windcode from chinamutualfunddescription \
                    where f_info_windcode in (select F_INFO_WINDCODE from chinamutualfundsector \
                    where left(s_info_sector,10)=' + fundType[:10] + ' and CUR_SIGN=1) \
                    and f_info_status=101001000'
            else:
                if classify == 'windFirst':  # 一级分类
                    tmp = []
                    for m in fundType:
                        tmp.append(m[:8])
                    sql = 'select f_info_windcode from chinamutualfunddescription \
                    where f_info_windcode in (select F_INFO_WINDCODE from chinamutualfundsector \
                    where left(s_info_sector,8) in ' + str(tuple(tmp)) + ' and CUR_SIGN=1) \
                    and f_info_status=101001000'
                else:
                    tmp = []
                    for m in fundType:
                        tmp.append(m[:10])
                    sql = 'select f_info_windcode from chinamutualfunddescription \
                    where f_info_windcode in (select F_INFO_WINDCODE from chinamutualfundsector \
                    where left(s_info_sector,10) in ' + str(tuple(tmp)) + ' and CUR_SIGN=1) \
                    and f_info_status=101001000'

    res = execSql(sql)

    # 若包含已清算基金，则需要单独处理
    if status == 0 and fundType:
        tmp1 = dict()
        for r in res:
            tmp1[r[0]] = [r[1], r[2]]
        tmp = []
        if classify == 'windFirst':
            if type(fundType) is str:
                fundType = [fundType[:8]]
            else:
                fundType = [m[:8] for m in fundType]
            for symbol in tmp1:
                if tmp1[symbol][0][:8] in fundType:
                    tmp.append(symbol)
        elif classify == 'windSecond':
            if type(fundType) is str:
                fundType = [fundType[:10]]
            else:
                fundType = [m[:10] for m in fundType]
            for symbol in tmp1:
                if tmp1[symbol][0][:10] in fundType:
                    tmp.append(symbol)
    else:
        tmp = [m[0] for m in res]

    return list(set(tmp))


# 获取基金信息数据，基金信息涵盖基金代码，基金简称，成立日期以及基金类型
def getData_fundInformation(fundSymbols, infoType='basic'):
    # infoType:basic或windSecond
    # 统一格式
    if type(fundSymbols) is list and len(fundSymbols) == 1:
        fundSymbols = fundSymbols[0]

    # 基本信息
    if infoType == 'basic':
        fundClass = fundClassMap()

        if type(fundSymbols) == str:
            sql = 'select d.F_INFO_WINDCODE, d.F_INFO_FULLNAME,d.F_INFO_SETUPDATE,\
            concat(left(s.S_INFO_SECTOR,8),"00000000") idcode,s.CUR_SIGN \
            from chinamutualfunddescription d \
            join chinamutualfundsector s on d.F_INFO_WINDCODE=s.F_INFO_WINDCODE \
            where d.F_INFO_WINDCODE="' + fundSymbols + '" and s.S_INFO_SECTOR like "200101%" \
            order by s.CUR_SIGN'
        else:
            sql = 'select d.F_INFO_WINDCODE, d.F_INFO_FULLNAME,d.F_INFO_SETUPDATE,\
            concat(left(s.S_INFO_SECTOR,8),"00000000") idcode,s.CUR_SIGN \
            from chinamutualfunddescription d \
            join chinamutualfundsector s on d.F_INFO_WINDCODE=s.F_INFO_WINDCODE \
            where d.F_INFO_WINDCODE in' + str(tuple(fundSymbols)) + 'and s.S_INFO_SECTOR like "200101%" \
            order by s.CUR_SIGN'

        res = execSql(sql)
        tmp = dict()
        for i in range(len(res)):
            tmp1 = dict()
            tmp1['SEC_NAME'] = res[i][1]
            tmp1['FUND_SETUPDATE'] = parse(res[i][2]) if res[i][2] else None
            for key in fundClass:
                if fundClass[key] == res[i][3]:
                    tmp1['FUND_INVESTTYPE'] = key
            tmp[res[i][0]] = tmp1
        tmp = pd.DataFrame(tmp).T

        # 所属wind二级分类
    elif infoType == 'windSecond':
        fundClass = fundClassMap(classify='windSecond')
        if type(fundSymbols) == str:
            sql = 'select d.F_INFO_WINDCODE,concat(left(s.S_INFO_SECTOR,10),"000000") idcode,s.CUR_SIGN\
            from chinamutualfunddescription d \
            join chinamutualfundsector s on d.F_INFO_WINDCODE=s.F_INFO_WINDCODE \
            where d.F_INFO_WINDCODE="' + fundSymbols + '" and s.S_INFO_SECTOR like "200101%" \
            order by s.CUR_SIGN'
        else:
            sql = 'select d.F_INFO_WINDCODE,concat(left(s.S_INFO_SECTOR,10),"000000") idcode,s.CUR_SIGN \
            from chinamutualfunddescription d \
            join chinamutualfundsector s on d.F_INFO_WINDCODE=s.F_INFO_WINDCODE \
            where d.F_INFO_WINDCODE in' + str(tuple(fundSymbols)) + 'and s.S_INFO_SECTOR like "200101%" \
            order by s.CUR_SIGN'

        res = execSql(sql)
        tmp = dict()
        for r in res:
            for key in fundClass:
                if fundClass[key] == r[1]:
                    tmp[r[0]] = key
        tmp = pd.Series(tmp, name='windSecond')
    else:
        pass
    return tmp


# 基金经理任职区间
def getData_fundManagerInfo(symbol, symbolType='fund'):
    # symbol:代码，一次只能指定一个基金标的或一个基金经理
    # symbolType：提取信息的模式，为'fund'或 'manager'
    if symbolType == 'fund':
        keys = 'F_INFO_FUNDMANAGER,F_INFO_MANAGER_STARTDATE,F_INFO_MANAGER_LEAVEDATE'
        sql = 'select %s from  chinamutualfundmanager where  F_INFO_WINDCODE = %s' % (keys, '"' + symbol + '"')
        res = execSql(sql)
        tmp1 = dict()
        for t in res:
            tmp1[t[0]] = [parse(t[1]), parse(t[2]) if t[2] else datetime.today()]
    else:
        sql = 'select F_INFO_WINDCODE,F_INFO_MANAGER_STARTDATE,F_INFO_MANAGER_LEAVEDATE \
             from chinamutualfundmanager  where F_INFO_FUNDMANAGER="' + symbol + '"'
        res = execSql(sql)
        tmp1 = dict()
        for t in res:
            tmp1[t[0]] = [parse(t[1]), parse(t[2]) if t[2] else datetime.today()]
    return tmp1


# 获取基金经理id,根据输入的基金经理名称及基金代码
def getData_fundManagerId(manager, symbol):
    sql = 'select F_INFO_FUNDMANAGER_ID from chinamutualfundmanager where \
    F_INFO_FUNDMANAGER="' + manager + '" and F_INFO_WINDCODE="' + symbol + '"'
    res = execSql(sql)
    return res[0][0] if len(res) > 0 else ''


# 获取全部基金经理任职信息
def getData_fundManagerInfo_all():
    sql = 'select F_INFO_FUNDMANAGER_ID,F_INFO_FUNDMANAGER,F_INFO_WINDCODE,F_INFO_MANAGER_STARTDATE,F_INFO_MANAGER_LEAVEDATE \
    from chinamutualfundmanager'
    tmp = []
    res = execSql(sql)
    for r in res:
        tmp.append(r)
    tmp = pd.DataFrame(tmp, columns=['managerId', 'manager', 'fund', 'startDate', 'endDate'])
    tmp.fillna(datetime.strftime(datetime.today(), '%Y%m%d'), inplace=True)
    return tmp


# 提取基金单位净值（日频，月频填充）、复权净值（日频）、基金季度份额（季频）、基金股票市值占比数据（季频）
def getData_fundHistoryData(dataType, fundSymbols, startDate, endDate=None):
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')
    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

        # 将长度为1的list格式转为str
    if type(fundSymbols) is list and len(fundSymbols) == 1:
        fundSymbols = fundSymbols[0]

    # 调取日频交易日序列
    tdays = getData_tradeDays(startDate, endDate, '日')

    # 基金单位净值
    if dataType == 'nav':
        # 为提高速度，单位净值仅提取月频数据
        if type(fundSymbols) == str:
            sql = 'select F_INFO_WINDCODE,PRICE_DATE,F_NAV_UNIT from fof_adjnav  where F_INFO_WINDCODE="' + fundSymbols + '" \
            and PRICE_DATE>="' + startDate + '" and PRICE_DATE<="' + endDate + '"'
        else:
            sql = 'select F_INFO_WINDCODE,PRICE_DATE,F_NAV_UNIT from fof_adjnav  where F_INFO_WINDCODE in' + str(
                tuple(fundSymbols)) + \
                  ' and PRICE_DATE>="' + startDate + '" and PRICE_DATE<="' + endDate + '"'

        res = execSql(sql)
        tmp = dict()
        mdays = getData_tradeDays(startDate, endDate, '月')
        mdays = [datetime.strftime(m, '%Y%m%d') for m in mdays]
        for r in res:
            if r[1] not in mdays:
                continue
            if r[1] in tmp.keys():
                tmp[r[1]].update({r[0]: float(r[2])})
            else:
                tmp[r[1]] = {r[0]: float(r[2])}
        tmp = pd.DataFrame(tmp).T
        tmp.index = [parse(m) for m in tmp.index]
        tmp.sort_index(inplace=True)
        tmp = tmp.reindex(tdays)
        tmp = fillna_mid(tmp)
        tmp.dropna(axis=0, how='all', inplace=True)  # 删除全部为Nan值数据
        if type(tmp) is pd.Series:
            return tmp
        else:
            return tmp if tmp.shape[1] > 1 else tmp.iloc[:, 0]

    # 基金复权净值
    elif dataType == 'adjNav':
        if type(fundSymbols) == str:
            sql = 'select F_INFO_WINDCODE,PRICE_DATE,ADJNAV from fof_adjnav  where F_INFO_WINDCODE="' + fundSymbols + '" \
            and PRICE_DATE>="' + startDate + '" and PRICE_DATE<="' + endDate + '"'
        else:
            sql = 'select F_INFO_WINDCODE,PRICE_DATE,ADJNAV from fof_adjnav  where F_INFO_WINDCODE in' + str(
                tuple(fundSymbols)) + \
                  ' and PRICE_DATE>="' + startDate + '" and PRICE_DATE<="' + endDate + '"'
        res = execSql(sql)
        tmp = dict()
        for r in res:
            if r[1] in tmp.keys():
                tmp[r[1]].update({r[0]: float(r[2])})
            else:
                tmp[r[1]] = {r[0]: float(r[2])}
        tmp = pd.DataFrame(tmp).T
        tmp.index = [parse(m) for m in tmp.index]
        tmp.sort_index(inplace=True)
        tmp = tmp.reindex(tdays)
        tmp = fillna_mid(tmp)
        tmp.dropna(axis=0, how='all', inplace=True)  # 删除全部为Nan值数据
        if type(tmp) is pd.Series:
            return tmp
        else:
            return tmp if tmp.shape[1] > 1 else tmp.iloc[:, 0]

    # 基金比较基准价格序列
    elif dataType == 'fundBench':
        if type(fundSymbols) == str:
            fundSymbols = fundSymbols.split('.')[0] + 'BI.WI'
            sql = 'select S_INFO_WINDCODE,TRADE_DT,S_DQ_CLOSE from chinamutualfundbenchmarkeod \
            where TRADE_DT>="' + startDate + '" and TRADE_DT<="' + endDate + '" and S_INFO_WINDCODE ="' + fundSymbols + '"'
        else:
            fundSymbols = [m.split('.')[0] + 'BI.WI' for m in fundSymbols]
            sql = 'select S_INFO_WINDCODE,TRADE_DT,S_DQ_CLOSE from chinamutualfundbenchmarkeod \
            where  TRADE_DT>="' + startDate + '" and TRADE_DT<="' + endDate + '" and S_INFO_WINDCODE in' + str(
                tuple(fundSymbols))

        res = execSql(sql)
        tmp = dict()
        for r in res:
            if r[1] in tmp.keys():
                tmp[r[1]].update({r[0]: r[2]})
            else:
                tmp[r[1]] = {r[0]: r[2]}
        tmp = pd.DataFrame(tmp).T
        tmp.index = [parse(m) for m in tmp.index]
        tmp.sort_index(inplace=True)
        if tmp.empty:
            return pd.Series()
        else:
            return tmp if tmp.shape[1] > 1 else tmp.iloc[:, 0]


    # 基金合计份额数据，单位为万份
    elif dataType == 'fundShare':
        if type(fundSymbols) == str:
            sql = 'select F_INFO_WINDCODE,CHANGE_DATE,FUNDSHARE_TOTAL from chinamutualfundshare \
            where CHANGE_DATE>="' + startDate + '" and CHANGE_DATE<="' + endDate + '" and F_INFO_WINDCODE ="' + fundSymbols + '"'
        else:
            sql = 'select F_INFO_WINDCODE,CHANGE_DATE,FUNDSHARE_TOTAL from chinamutualfundshare \
            where  CHANGE_DATE>="' + startDate + '" and  CHANGE_DATE<="' + endDate + '" and F_INFO_WINDCODE in' + str(
                tuple(fundSymbols))

        res = execSql(sql)

        tmp = dict()
        for r in res:
            if r[1] in tmp.keys():
                tmp[r[1]].update({r[0]: r[2]})
            else:
                tmp[r[1]] = {r[0]: r[2]}
        tmp = pd.DataFrame(tmp).T
        tmp.index = [parse(m) for m in tmp.index]
        tmp.sort_index(inplace=True)
        return tmp if tmp.shape[1] > 1 else tmp.iloc[:, 0]


    # 基金股票市值占比数据
    elif dataType == 'stockProportion':
        if type(fundSymbols) == str:
            sql = 'select S_INFO_WINDCODE,F_PRT_ENDDATE,F_PRT_STOCKTONAV  from chinamutualfundassetportfolio \
            where S_INFO_WINDCODE="' + fundSymbols + '" and F_PRT_ENDDATE>="' + startDate + '" and F_PRT_ENDDATE<="' + endDate + '"'
        else:
            sql = 'select S_INFO_WINDCODE,F_PRT_ENDDATE,F_PRT_STOCKTONAV  from chinamutualfundassetportfolio \
            where S_INFO_WINDCODE in' + str(
                tuple(fundSymbols)) + ' and F_PRT_ENDDATE>="' + startDate + '" and F_PRT_ENDDATE<="' + endDate + '"'
        res = execSql(sql)
        data = dict()
        for r in res:
            tmp = float(r[2]) if r[2] else None
            if r[1] in data.keys():
                data[r[1]].update({r[0]: tmp})
            else:
                data[r[1]] = {r[0]: tmp}
        data = pd.DataFrame(data).T
        data.index = [parse(m) for m in data.index]
        data.sort_index(inplace=True)
        return data if data.shape[1] > 1 else data.iloc[:, 0]


# 提取指定交易日处于暂停申购或暂停大额申购状态的基金列表
def getData_fundStatus(status, tradeDate):
    if type(tradeDate) is not str:
        tradeDate = datetime.strftime(tradeDate, '%Y%m%d')
    else:
        tradeDate = datetime.strftime(parse(tradeDate), '%Y%m%d')

    if status == '暂停申购':
        sql = 'select S_INFO_WINDCODE from ChinaMutualFundSuspendPchRedm \
            where F_INFO_SUSPCHSTARTDT<="' + tradeDate + '" and ( F_INFO_REPCHDT>"' + tradeDate + \
              '" or F_INFO_REPCHDT is null ) and F_INFO_PURCHASEUPLIMIT is null'
    elif status == '暂停大额申购':
        sql = 'select S_INFO_WINDCODE from ChinaMutualFundSuspendPchRedm \
            where F_INFO_SUSPCHSTARTDT<="' + tradeDate + '" and ( F_INFO_REPCHDT>"' + tradeDate + \
              '" or F_INFO_REPCHDT is null ) and F_INFO_PURCHASEUPLIMIT is not null'
    res = execSql(sql)
    tmp = [r[0] for r in res]
    return tmp


# 基金持股信息数据
def getData_fundSecHoldingData(dataType, fundSymbol, reportDate):
    # dataType代表要获取的基金数据名称,str格式;fundSymbol代表基金名称，str格式，仅支持单个基金标的
    if type(reportDate) is not str:
        reportDate = datetime.strftime(reportDate, '%Y%m%d')
    else:
        reportDate = datetime.strftime(parse(reportDate), '%Y%m%d')

    # 重仓股数据
    if dataType == 'mainStockHolding':
        sql = 'select S_INFO_STOCKWINDCODE,F_PRT_STKVALUE,F_PRT_STKQUANTITY from ChinaMutualFundStockPortfolio \
        where S_INFO_WINDCODE="' + fundSymbol + '" and \
        F_PRT_ENDDATE="' + reportDate + '" and datediff(ANN_DATE,F_PRT_ENDDATE)<31'
    # 全部持股数据
    elif dataType == 'allStockHolding':
        sql = 'select S_INFO_STOCKWINDCODE,F_PRT_STKVALUE,F_PRT_STKQUANTITY from ChinaMutualFundStockPortfolio \
        where S_INFO_WINDCODE="' + fundSymbol + '" and \
        F_PRT_ENDDATE="' + reportDate + '"'
    else:
        sql = ''
    res = execSql(sql)
    data = []
    for r in res:
        data.append(r)
    data = pd.DataFrame(data, columns=['股票代码', '持股市值', '持股数量'], dtype=float)
    return data


# 获取指定日期的基金数据，如单位净值,若本日数据为空，则用上交易日数据替代
def getData_fundSpecDateData(dataType, fundSymbols, execDate):
    try:
        execDate = datetime.strftime(parse(execDate), '%Y%m%d')
    except:
        execDate = datetime.strftime(execDate, '%Y%m%d')

    endDate = execDate
    # 指定日单位净值数据
    if dataType == 'nav':
        startDate = datetime.strftime(parse(execDate) - timedelta(30), '%Y%m%d')
        if type(fundSymbols) == str:
            sql = 'select F_INFO_WINDCODE,PRICE_DATE,F_NAV_UNIT from fof_adjnav  where F_INFO_WINDCODE="' + fundSymbols + '" \
            and PRICE_DATE>="' + startDate + '" and PRICE_DATE<="' + endDate + '"'
        else:
            sql = 'select F_INFO_WINDCODE,PRICE_DATE,F_NAV_UNIT from fof_adjnav  where F_INFO_WINDCODE in' + str(
                tuple(fundSymbols)) + \
                  ' and PRICE_DATE>="' + startDate + '" and PRICE_DATE<="' + endDate + '"'

        res = execSql(sql)
        tmp = dict()
        for r in res:
            if r[1] in tmp.keys():
                tmp[r[1]].update({r[0]: float(r[2])})
            else:
                tmp[r[1]] = {r[0]: float(r[2])}
        tmp = pd.DataFrame(tmp).T
        tmp.index = [parse(m) for m in tmp.index]
        tmp.sort_index(inplace=True)
        tmp.fillna(inplace=True, method='ffill')
        tmp = tmp.iloc[-1]
        return tmp

    # 指定日合并份额数据
    elif dataType == 'fundShare_total':
        startDate = datetime.strftime(parse(execDate) - timedelta(180), '%Y%m%d')
        if type(fundSymbols) == str:
            sql = 'select F_INFO_WINDCODE,CHANGE_DATE,F_UNIT_TOTAL from chinamutualfundshare \
            where CHANGE_DATE>="' + startDate + '" and CHANGE_DATE<="' + endDate + '" and F_INFO_WINDCODE ="' + fundSymbols + '"'
        else:
            sql = 'select F_INFO_WINDCODE,CHANGE_DATE,F_UNIT_TOTAL from chinamutualfundshare \
            where  CHANGE_DATE>="' + startDate + '" and  CHANGE_DATE<="' + endDate + '" and F_INFO_WINDCODE in' + str(
                tuple(fundSymbols))
        res = execSql(sql)

        tmp = dict()
        for r in res:
            if r[1] in tmp.keys():
                tmp[r[1]].update({r[0]: float(r[2])})
            else:
                tmp[r[1]] = {r[0]: float(r[2])}
        tmp = pd.DataFrame(tmp).T
        tmp.index = [parse(m) for m in tmp.index]
        tmp.sort_index(inplace=True)
        tmp = tmp.fillna(method='ffill').iloc[-1]
        return tmp

        # 指定日单独份额数据
    elif dataType == 'fundShare_unit':
        startDate = datetime.strftime(parse(execDate) - timedelta(180), '%Y%m%d')
        if type(fundSymbols) == str:
            sql = 'select F_INFO_WINDCODE,CHANGE_DATE,FUNDSHARE from chinamutualfundshare \
            where CHANGE_DATE>="' + startDate + '" and CHANGE_DATE<="' + endDate + '" and F_INFO_WINDCODE ="' + fundSymbols + '"'
        else:
            sql = 'select F_INFO_WINDCODE,CHANGE_DATE,FUNDSHARE from chinamutualfundshare \
            where  CHANGE_DATE>="' + startDate + '" and  CHANGE_DATE<="' + endDate + '" and F_INFO_WINDCODE in' + str(
                tuple(fundSymbols))
        res = execSql(sql)

        tmp = dict()
        for r in res:
            if r[1] in tmp.keys():
                tmp[r[1]].update({r[0]: float(r[2])})
            else:
                tmp[r[1]] = {r[0]: float(r[2])}
        tmp = pd.DataFrame(tmp).T
        tmp.index = [parse(m) for m in tmp.index]
        tmp.sort_index(inplace=True)
        tmp = tmp.fillna(method='ffill').iloc[-1]
        return tmp

    # 基金换手率


def getData_fundTurnOver(fundSymbols, startDate, endDate):
    # 转换日期格式
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')
    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

        # 将长度为1的list格式转为str
    if type(fundSymbols) is list and len(fundSymbols) == 1:
        fundSymbols = fundSymbols[0]
    # sql语句
    if type(fundSymbols) is str:
        sql = 'select c.S_INFO_WINDCODE,c.S_INFO_REPORTPERIOD,sum(c.F_TRADE_STOCKAM) as amt,a.F_PRT_STOCKVALUE \
            from chinamutualfundseattrading as c join chinamutualfundassetportfolio as a \
            on c.S_INFO_WINDCODE=a.S_INFO_WINDCODE and c.S_INFO_REPORTPERIOD=a.F_PRT_ENDDATE \
            group by c.S_INFO_WINDCODE,c.S_INFO_REPORTPERIOD \
            having c.S_INFO_REPORTPERIOD>="' + startDate + '" and c.S_INFO_REPORTPERIOD<="' + endDate + '"  \
            and c.S_INFO_WINDCODE = "' + fundSymbols + \
              '" order by c.S_INFO_WINDCODE,c.S_INFO_REPORTPERIOD'
    else:
        sql = 'select c.S_INFO_WINDCODE,c.S_INFO_REPORTPERIOD,sum(c.F_TRADE_STOCKAM) as amt,a.F_PRT_STOCKVALUE \
            from chinamutualfundseattrading as c join chinamutualfundassetportfolio as a \
            on c.S_INFO_WINDCODE=a.S_INFO_WINDCODE and c.S_INFO_REPORTPERIOD=a.F_PRT_ENDDATE \
            group by c.S_INFO_WINDCODE,c.S_INFO_REPORTPERIOD \
            having c.S_INFO_REPORTPERIOD>="' + startDate + '" and c.S_INFO_REPORTPERIOD<="' + endDate + '"  \
            and c.S_INFO_WINDCODE in ' + str(tuple(fundSymbols)) + \
              ' order by c.S_INFO_WINDCODE,c.S_INFO_REPORTPERIOD'
    res = execSql(sql)
    tmp = dict()  # 按基金代码作为字典
    for r in res:
        if r[0] in tmp.keys():
            tmp1 = tmp[r[0]]
            tmp1.append([r[1], r[2], r[3]])
            tmp[r[0]] = tmp1
        else:
            tmp[r[0]] = [[r[1], r[2], r[3]]]
    for key in tmp:
        tmp1 = pd.DataFrame(tmp[key], columns=['startDate', 'amt', 'marketValue'])
        tmp1.dropna(axis=0, inplace=True)
        tmp1[['amt', 'marketValue']] = tmp1[['amt', 'marketValue']].apply(pd.to_numeric, errors='ignore')
        tmp1['marketValue'] = tmp1['marketValue'].replace(0, np.nan)
        tmp1.set_index('startDate', inplace=True)
        tmp1.dropna(inplace=True)
        tmp1['avgValue'] = tmp1['marketValue'].rolling(2).mean()
        tmp1['turnOver'] = tmp1['amt'] / tmp1['avgValue'] / 2  # 双边换手率转为单边
        tmp1.index = [parse(m) for m in tmp1.index]
        tmp1.replace(float('inf'), np.nan, inplace=True)
        tmp1.dropna(axis=0, inplace=True)
        for i in range(len(tmp1.index)):
            if tmp1.index[i].month == 6:
                tmp1['turnOver'][i] = tmp1['turnOver'][i] * 2
        tmp[key] = tmp1['turnOver']

    return tmp


# %%股票因子暴露度数据

# 获取因子暴露度数据
def getData_factorExposure(factorName, symbolList=None, startDate=None, endDate=None):
    # symbolList:list格式或字符串格式，当为None时，提取所有股票值
    # startDate:字符串或datetime格式，为None时表示从最开始的数据提取
    # endDate：字符串或datetime格式，为None是表示提取至最新数据
    if not startDate:
        startDate = datetime.strftime(datetime(2005, 1, 1), '%Y%m%d')
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')
    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

    if not symbolList:
        symbolList = getData_stockConstitue('aStock')
    if type(symbolList) is list and len(symbolList) == 1:
        symbolList = symbolList[0]

    if type(symbolList) is str:
        sql = 'select S_WINDCODE,TRADE_DT,FACTOR_VALUE from fof_stockexpousre where \
        S_WINDCODE="' + symbolList + '" and TRADE_DT>="' + startDate + '" and TRADE_DT<="' + \
              endDate + '" and INDICATOR_CODE="' + factorName + '"'
    else:
        sql = 'select S_WINDCODE,TRADE_DT,FACTOR_VALUE from fof_stockexpousre where \
        S_WINDCODE in ' + str(tuple(symbolList)) + ' and TRADE_DT>="' + startDate + '" and TRADE_DT<="' + \
              endDate + '" and INDICATOR_CODE="' + factorName + '"'

    res = execSql(sql)
    tmp = dict()
    for r in res:
        if r[1] in tmp.keys():
            tmp[r[1]].update({r[0]: float(r[2])})
        else:
            tmp[r[1]] = {r[0]: float(r[2])}
    tmp = pd.DataFrame(tmp).T
    tmp.index = [parse(m) for m in tmp.index]
    tmp.sort_index(inplace=True)
    return tmp


# 获取因子收益率数据
def getData_factorReturn(factorName=None, startDate=None, endDate=None):
    # factorName:因子名称,当设定为None时，提取所有因子，支持多个因子同时提取，采用list格式
    # startDate:字符串或datetime格式，为None时表示从最开始的数据提取
    # endDate：字符串或datetime格式，为None是表示提取至最新数据
    if not startDate:
        startDate = datetime.strftime(datetime(2005, 1, 1), '%Y%m%d')
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')
    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

    if not factorName:
        factorName = ['beta', 'earning', 'growth', 'leverage', 'liquidity',
                      'momentum', 'size', 'value', 'volatility']

    if type(factorName) is str:
        sql = 'select INDICATOR_CODE,TRADE_DT,FACTOR_VALUE  from fof_factorreturn \
        where INDICATOR_CODE="' + factorName + '"  and TRADE_DT>="' + startDate + \
              '" and TRADE_DT<="' + endDate + '"'
    else:
        sql = 'select INDICATOR_CODE,TRADE_DT,FACTOR_VALUE  from fof_factorreturn \
        where INDICATOR_CODE in ' + str(tuple(factorName)) + ' and TRADE_DT>="' + startDate + \
              '" and TRADE_DT<="' + endDate + '"'

    res = execSql(sql)
    tmp = dict()
    for r in res:
        if r[1] in tmp.keys():
            tmp[r[1]].update({r[0]: float(r[2])})
        else:
            tmp[r[1]] = {r[0]: float(r[2])}
    tmp = pd.DataFrame(tmp).T
    tmp.index = [parse(m) for m in tmp.index]
    tmp.sort_index(inplace=True)
    return tmp


# %%股票市场数据
# 股票历史价格、成交数据
def getData_stockHistoryData(dataType, stockSymbols, startDate, endDate=None, frequency='日'):
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')

    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

    if type(stockSymbols) is list and len(stockSymbols) == 1:
        stockSymbols = stockSymbols[0]

    typeList_1 = {'close_B': 'S_DQ_ADJCLOSE', 'close': 'S_DQ_CLOSE', 'amt': 'S_DQ_AMOUNT'}
    typeList_2 = {'pe': 'S_VAL_PE_TTM', 'pb': 'S_VAL_PB_NEW', 'ps': 'S_VAL_PS'}

    if dataType in typeList_1:
        key = typeList_1[dataType]
        if type(stockSymbols) is str:
            sql = 'select S_INFO_WINDCODE,TRADE_DT,' + key + ' from ashareeodprices \
            where TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and S_INFO_WINDCODE="' + stockSymbols + '"'
        else:
            sql = 'select S_INFO_WINDCODE,TRADE_DT,' + key + ' from ashareeodprices \
            where  TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and S_INFO_WINDCODE in ' + str(
                tuple(stockSymbols))
    else:
        key = typeList_2[dataType]
        if type(stockSymbols) is str:
            sql = 'select S_INFO_WINDCODE,TRADE_DT,' + key + ' from ashareeodderivativeindicator \
            where TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and S_INFO_WINDCODE="' + stockSymbols + '"'
        else:
            sql = 'select S_INFO_WINDCODE,TRADE_DT,' + key + ' from ashareeodderivativeindicator \
            where  TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and S_INFO_WINDCODE in ' + str(
                tuple(stockSymbols))

    res = execSql(sql)
    tmp = dict()
    for r in res:
        if r[1] in tmp.keys():
            tmp[r[1]].update({r[0]: float(r[2])})
        else:
            tmp[r[1]] = {r[0]: float(r[2])}
    tmp = pd.DataFrame(tmp).T
    tmp.index = [parse(m) for m in tmp.index]
    tmp.sort_index(inplace=True)
    tdays = getData_tradeDays(startDate, endDate, frequency)
    tmp = tmp.reindex(tdays)
    if tmp.shape[1] == 1:
        tmp = tmp.iloc[:.0]
    return tmp


# 股票基本信息数据
def getData_stockInformation(stockSymbols, info='industry_CI'):
    # 将长度为1的list格式转为str
    if type(stockSymbols) is list and len(stockSymbols) == 1:
        stockSymbols = stockSymbols[0]

    if info == 'industry_CI':  # 所属行业,默认为中信
        if type(stockSymbols) is str:
            sql = 'select S_INFO_WINDCODE,INDUSTRIESCODE,INDUSTRIESNAME from \
            ashareindustriesclasscitics  join ashareindustriescode on \
            left(CITICS_IND_CODE,4) = left(INDUSTRIESCODE,4) and right(INDUSTRIESCODE,6)="000000" \
            and S_INFO_WINDCODE ="' + stockSymbols + '"'
        else:
            sql = 'select S_INFO_WINDCODE,INDUSTRIESCODE,INDUSTRIESNAME from \
            ashareindustriesclasscitics  join ashareindustriescode on \
            left(CITICS_IND_CODE,4) = left(INDUSTRIESCODE,4) and right(INDUSTRIESCODE,6)="000000" \
            and S_INFO_WINDCODE in ' + str(tuple(stockSymbols))
        res = execSql(sql)
        tmp = dict()
        for r in res:
            tmp[r[0]] = r[2]

    elif info == 'setUpDate':  # 上市日期
        pass
    elif info == 'stockName':  # 股票名称
        if type(stockSymbols) is str:
            sql = 'select S_INFO_WINDCODE,S_INFO_NAME from asharedescription \
            where S_INFO_WINDCODE ="' + stockSymbols + '"'
        else:
            sql = 'select S_INFO_WINDCODE,S_INFO_NAME from asharedescription \
            where S_INFO_WINDCODE in' + str(tuple(stockSymbols))
        res = execSql(sql)
        tmp = dict()
        for r in res:
            tmp[r[0]] = r[1]

    return tmp


# 获取指定交易日某板块的的成分股股票名称
def getData_stockConstitue(sectorSymbol, tradeDate=None):
    # sectorSymbol:股票成分代码，str格式；tradeDate：交易日期,除st及全部A股板块外，仅支持月频数据
    # 支持提取st板块股票，设定sectorSymbol为‘stStock’
    # 支持提取目前数据库存储的全部A股代码，sectorSymbol设为‘aStock’
    if not tradeDate:
        tradeDate = datetime.strftime(datetime.today(), '%Y%m%d')
    try:
        tradeDate = datetime.strftime(parse(tradeDate), '%Y%m%d')
    except:
        tradeDate = datetime.strftime(tradeDate, '%Y%m%d')

        # 提取全部A股成分股
    if sectorSymbol == 'aStock':
        sql = 'select S_INFO_WINDCODE from asharedescription where S_INFO_LISTDATE is not null'
        res = execSql(sql)
        tmp = [r[0] for r in res]
        return tmp
    # 提取行业所属成分股
    else:
        pass


# %%市场指数数据
# 股票市场指数
def getData_marketIndex(symbol, startDate, endDate=None, frequency='日'):
    # 获取指数数据
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')

    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

    if type(symbol) is list and len(symbol) == 1:
        symbol = symbol[0]

    # 宽基指数
    sql_1 = 'select TRADE_DT,S_DQ_CLOSE from aindexeodprices where \
    TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and S_INFO_WINDCODE="' + symbol + '"'

    # 行业指数
    sql_2 = 'select TRADE_DT,S_DQ_CLOSE from aindexindustrieseodcitics where \
    S_INFO_WINDCODE="' + symbol + '" and TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '"'

    res = execSql(sql_1)
    if len(res) == 0:
        res = execSql(sql_2)
    data = dict()
    for r in res:
        data[parse(r[0])] = float(r[1])
    data = pd.Series(data, name=symbol)
    data.sort_index(inplace=True)
    data.fillna(method='ffill', inplace=True)
    tradeDays = getData_tradeDays(data.index[0], data.index[-1], frequency)
    data = data.reindex(tradeDays, method='ffill')
    return data


# 债券市场指数
def getData_bondIndex(symbol, startDate, endDate=None, frequency='日'):
    # 获取指数数据
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')

    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

    if type(symbol) is list and len(symbol) == 1:
        symbol = symbol[0]

    if type(symbol) is str:
        sql = 'select S_INFO_WINDCODE,TRADE_DT,S_DQ_CLOSE from cbindexeodprices where \
        TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and \
        S_INFO_WINDCODE="' + symbol + '"'
    else:
        sql = 'select S_INFO_WINDCODE,TRADE_DT,S_DQ_CLOSE from cbindexeodprices where \
        TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and \
        S_INFO_WINDCODE in ' + str(tuple(symbol))

    res = execSql(sql)
    tmp = dict()
    for r in res:
        if r[1] in tmp.keys():
            tmp[r[1]].update({r[0]: float(r[2])})
        else:
            tmp[r[1]] = {r[0]: float(r[2])}
    tmp = pd.DataFrame(tmp).T
    tmp.index = [parse(m) for m in tmp.index]
    tmp.sort_index(inplace=True)
    tdays = getData_tradeDays(tmp.index[0], tmp.index[-1], frequency)
    tmp = tmp.reindex(tdays, method='ffill')
    if tmp.shape[1] == 1:
        tmp = tmp.iloc[:, 0]
    return tmp


# 基金市场指数
def getData_fundIndex(symbol, startDate, endDate=None, frequency='日'):
    # 获取指数数据
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')

    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

    if type(symbol) is list and len(symbol) == 1:
        symbol = symbol[0]

    if type(symbol) is str:
        sql = 'select S_INFO_WINDCODE,TRADE_DT,SI_PCT_CHG/100+1  SI_INDEX_CHG from findexperformance where \
        TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and \
        S_INFO_WINDCODE="' + symbol + '" '
    else:
        sql = 'select S_INFO_WINDCODE,TRADE_DT,SI_PCT_CHG/100+1 SI_INDEX_CHG from findexperformance where \
        TRADE_DT >= "' + startDate + '" and TRADE_DT <="' + endDate + '" and \
        S_INFO_WINDCODE in' + str(tuple(symbol))

    res = execSql(sql)
    tmp = dict()
    for r in res:
        if r[1] in tmp.keys():
            tmp[r[1]].update({r[0]: float(r[2])})
        else:
            tmp[r[1]] = {r[0]: float(r[2])}
    tmp = pd.DataFrame(tmp).T
    tmp.index = [parse(m) for m in tmp.index]
    tmp.sort_index(inplace=True)
    tdays = getData_tradeDays(tmp.index[0], tmp.index[-1], frequency)
    tmp = tmp.reindex(tdays, method='ffill')
    if tmp.shape[1] == 1:
        tmp = tmp.iloc[:, 0]
    return tmp


# %%日期类函数
# 调取交易日日期，支持日频，月频，季频，半年频与年频
def getData_tradeDays(startDate, endDate=None, frequency='月'):
    if not endDate:
        endDate = datetime.strftime(datetime.today(), '%Y%m%d')
    if type(startDate) is not str:
        startDate = datetime.strftime(startDate, '%Y%m%d')
    else:
        startDate = datetime.strftime(parse(startDate), '%Y%m%d')
    if type(endDate) is not str:
        endDate = datetime.strftime(endDate, '%Y%m%d')
    else:
        endDate = datetime.strftime(parse(endDate), '%Y%m%d')

        # 将筛选的截止日期后推，避免月频以上数据最后一个日期选择不到
    endDate_1 = datetime.strftime(parse(endDate) + timedelta(15), '%Y%m%d')
    sql = 'select TRADE_DAYS from asharecalendar where S_INFO_EXCHMARKET="SSE" \
    and TRADE_DAYS between "' + startDate + '" and "' + endDate_1 + '" order by TRADE_DAYS asc'
    res = execSql(sql)
    data = []
    for r in res:
        data.append(parse(r[0]))

    if frequency == '日':
        tmp = data
    elif frequency == '月':
        tmp = []
        for i in range(1, len(data)):
            if data[i].month != data[i - 1].month:
                tmp.append(data[i - 1])
    elif frequency == '季':
        tmp = []
        for i in range(1, len(data)):
            if data[i].month != data[i - 1].month and data[i - 1].month % 3 == 0:
                tmp.append(data[i - 1])
    elif frequency == '半年':
        tmp = []
        for i in range(1, len(data)):
            if data[i].month != data[i - 1].month and data[i - 1].month % 6 == 0:
                tmp.append(data[i - 1])
    elif frequency == '年':
        tmp = []
        for i in range(1, len(data)):
            if data[i].month != data[i - 1].month and data[i - 1].month % 12 == 0:
                tmp.append(data[i - 1])

    return [m for m in tmp if m <= parse(endDate)]


# 交易日与自然日转换，默认为自然日转交易日
def convertDays(dateList, frequency='季', mode='w2t'):
    freqMap = {'月': 'M', '季': 'Q', '半年': 'M', '年': 'A-DEC'}
    if mode == 'w2t':
        tdays = getData_tradeDays(dateList[0] - timedelta(10), dateList[-1], frequency)
    else:
        tdays = list(pd.date_range(dateList[0], dateList[-1] + timedelta(10), freq=freqMap[frequency]))
        if frequency == '半年':
            tdays = [m for m in tdays if m.month in (6, 12)]

    tmp = []
    for m in dateList:
        tmp1 = [abs((n - m).days) for n in tdays]
        icounter = tmp1.index(np.min(tmp1))
        tmp.append(tdays[icounter])
    return tmp


if __name__ == '__main__':
    fundType = '股票型'
    fundSymbols = getData_fundSymbols(fundType)

    # 测试净值提取函数
    startDate = '2010/1/1'
    endDate = '2018/12/31'

    fundInfo = getData_fundInformation(fundSymbols)

    fundNav = getData_fundHistoryData('nav', fundSymbols, startDate, endDate)
    fundadjNav = getData_fundHistoryData('adjNav', fundSymbols, startDate, endDate)
    fundstockProportion = getData_fundHistoryData('stockProportion', fundSymbols, startDate, endDate)
    fundShares = getData_fundHistoryData('fundShare', fundSymbols, startDate, endDate)
    mainStockHolding = getData_fundSecHoldingData('mainStockHolding', '000001.OF', '2015/12/31')
    allStockHolding = getData_fundSecHoldingData('allStockHolding', '000001.OF', '2015/12/31')

    fundManager = getData_fundManagerInfo('000001.OF', symbolType='fund')  # 根据基金名称提取
    fundStatus = getData_fundStatus('暂停申购', '2018/12/31')
    tdays = getData_tradeDays('2012/1/1', '2019/5/13', frequency='日')
    mdays = getData_tradeDays('2012/1/1', '2019/5/13', frequency='月')








































