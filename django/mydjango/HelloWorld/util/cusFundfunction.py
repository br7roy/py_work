# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pymongo
import re
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import datetime, timedelta
from dateutil.parser import parse


# %%MongoDb数据库数据获取函数
def connectMongo(location='cloud'):
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


# 获取市场指数数据
def getData_marketIndex(code, startDate, endDate=None, convertFreq=None):
    # code:str或list格式，当为list时，表示支持提取多列数据
    # convertFreq:转换频率，None或"m"，m表示转换为自然月的月频
    client = connectMongo()
    coll = client["fundDatabase"]['benchMark']
    if not endDate:
        endDate = datetime.today()
    if type(startDate) == str:
        startDate = parse(startDate)
    if type(endDate) == str:
        endDate = parse(endDate)

    if type(code) == str:
        code = [code]
    condition1 = {"tradeDate": {"$gte": startDate, "$lt": endDate + timedelta(1)}}
    condition2 = {"_id": 0, "tradeDate": 1}
    for code_ in code:
        condition2[code_] = 1

    tmp = []
    for document in coll.find(condition1, condition2):
        tmp.append(document)
    tmp = pd.DataFrame(tmp)
    tmp.set_index("tradeDate", inplace=True)
    tmp.sort_index(inplace=True)
    tmp.fillna(method='ffill', inplace=True)
    if len(tmp.columns) == 1:
        tmp = tmp.iloc[:, 0]
    else:
        tmp = tmp[code]
    # 是否转换为月频数据
    if convertFreq:
        tmp = tmp.resample("D").pad()[0:]
        tmp = tmp.resample("M").asfreq()[0:]
        tmp.dropna(inplace=True)
    return tmp


# 获取交易日期序列
def getData_tradeDays(startDate, endDate=None, frequency='月', exchange='上海证券交易所'):
    # frequency可选参数:日，周，月，季，半年，年；exchange可选参数：上海证券交易所，香港交易所
    client = connectMongo()
    db = client['fundDatabase']
    coll = db['tradeDays']
    if not endDate:
        endDate = datetime.today()
    if type(startDate) == str:
        startDate = parse(startDate)
    if type(endDate) == str:
        endDate = parse(endDate)
    condition1 = {"交易所": exchange, "frequency": frequency}
    condition2 = {"_id": 0, "data": 1}
    tmp = []
    for document in coll.find(condition1, condition2):
        tmp.append(document)
    tmp = tmp[0]['data']

    for myDay in tmp:
        if (myDay - startDate).days >= 0:
            myIndex1 = tmp.index(myDay)
            break
    for myDay in tmp:
        if myDay == tmp[-1]:
            myIndex2 = tmp.index(myDay) + 1
        if (myDay - endDate).days == 0:
            myIndex2 = tmp.index(myDay) + 1
            break
        if (myDay - endDate).days > 0:
            myIndex2 = tmp.index(myDay)
            break

    return tmp[myIndex1:myIndex2]


# 获取基金代码
def getData_fundSymbols(fundType):
    # fundType:基金类型，可以是单个基金类型，也可以是多个基金类型
    if type(fundType) == str:
        fundType = [fundType]
    client = connectMongo()
    coll = client['fundDatabase']['fundInformation']
    fundSymbol = []
    condition1 = {'FUND_INVESTTYPE': {'$in': fundType}}
    condition2 = {'_id': 0}
    for document in coll.find(condition1, condition2):
        fundSymbol.append(document)
    fundSymbol = pd.DataFrame(fundSymbol)
    fundSymbol.set_index("fundCode", inplace=True)
    return list(fundSymbol.index)


# 获取基金信息
def getData_fundInformation(fundSymbols):
    # fundSymbols:基金代码列表
    if type(fundSymbols) == str:
        fundSymbols = [fundSymbols]
    client = connectMongo()
    coll = client['fundDatabase']['fundInformation']
    fundInformation = []
    condition1 = {'fundCode': {'$in': fundSymbols}}
    condition2 = {'_id': 0}
    for document in coll.find(condition1, condition2):
        fundInformation.append(document)
    fundInformation = pd.DataFrame(fundInformation)
    fundInformation.set_index("fundCode", inplace=True)
    return fundInformation


# 获取基金交易数据
def getData_fundHistoryData(dataType, fundSymbols, startDate, endDate=None):
    # dataType代表要获取的基金数据名称,str格式；fundSymbols代表基金名称，lsit格式
    client = connectMongo()
    db = client['fundDatabase']
    coll = db[dataType]
    if not endDate:
        endDate = datetime.today()
    if type(startDate) == str:
        startDate = parse(startDate)
    if type(endDate) == str:
        endDate = parse(endDate)
    if type(fundSymbols) == str:
        fundSymbols = [fundSymbols]

    typeList_1 = ['adjNav', 'nav', 'fundStatus']
    typeList_2 = ['cbProportion', 'stockProportion', 'fundShare', 'holderNumber', 'institutionHoldingRatio']

    if dataType in typeList_1:
        condition1 = {"tradeDate": {"$gte": startDate, "$lt": endDate + timedelta(1)}}
        condition2 = {}.fromkeys(fundSymbols, 1)
        condition2['tradeDate'] = 1
        condition2['_id'] = 0
        tmp = []
        for document in coll.find(condition1, condition2):
            tmp.append(document)
        fundData = pd.DataFrame(tmp)
        fundData.set_index('tradeDate', inplace=True)
        fundData.sort_index(inplace=True)
        # 补齐中间的nan值
        for symbol in fundData.columns:
            fundPriceData = fundData[symbol].copy()
            tmp = fundPriceData.dropna(axis=0)
            firstDate = tmp.index[0]
            lastDate = tmp.index[-1]
            fundPriceData = fundPriceData[firstDate:lastDate].fillna(method='ffill')
            fundData.loc[firstDate:lastDate, symbol] = fundPriceData
    elif dataType in typeList_2:
        condition1 = {"reportDate": {"$gte": startDate, "$lt": endDate + timedelta(1)}}
        condition2 = {}.fromkeys(fundSymbols, 1)
        condition2['reportDate'] = 1
        condition2['_id'] = 0
        tmp = []
        for document in coll.find(condition1, condition2):
            tmp.append(document)
        fundData = pd.DataFrame(tmp)
        fundData.set_index('reportDate', inplace=True)
        fundData.sort_index(inplace=True)
    else:
        raise ValueError('输入的基金数据名称不正确，请核对')
    fundData.sort_index(inplace=True)
    if fundData.shape[1] == 1:
        fundData = fundData.iloc[:, 0]
    return fundData


# 获取基金的持仓标的数据
def getData_fundSecHoldingData(dataType, fundSymbol, reportDate):
    # dataType代表要获取的基金数据名称,str格式;fundSymbol代表基金名称，str格式，仅支持单个基金标的
    typeList = ['mainStockHoldingInformation', 'allStockHoldingInformation', 'mainBondHoldingInformation']
    if dataType not in typeList:
        raise ValueError("基金数据名称输入有误")
    client = connectMongo()
    db = client['fundDatabase']
    coll = db[dataType]
    if type(reportDate) == str:
        reportDate = parse(reportDate)

    condition1 = {"报告期": {"$gte": reportDate, "$lt": reportDate + timedelta(1)}, "代码": fundSymbol}
    condition2 = {"_id": 0}
    tmp = []
    for document in coll.find(condition1, condition2):
        tmp.append(document)
    if len(tmp) == 0:  # 如果找不到数据，有可能该基金是lof或etf，重新提取
        if fundSymbol[0] == '5':
            fundSymbol = fundSymbol[:-2] + 'SH'
        else:
            fundSymbol = fundSymbol[:-2] + 'SZ'
        condition1 = {"报告期": {"$gte": reportDate, "$lt": reportDate + timedelta(1)}, "代码": fundSymbol}
        condition2 = {"_id": 0}
        for document in coll.find(condition1, condition2):
            tmp.append(document)

    fundData = pd.DataFrame(tmp)
    return fundData


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


# %%基金样本清洗函数
# 提取非A类份额基金
def cleanSymbols_notA(fundSymbols):
    fundInformation = getData_fundInformation(fundSymbols)
    fundNames = fundInformation['SEC_NAME'].copy()
    nameList = [re.findall(name[:-1] + '[B-Z]', name) for name in fundNames]
    nameList = [i[0] for i in nameList if i != []]
    nameList = list(set(fundNames.tolist()) - set(nameList))
    tmp = []
    for symbol in fundSymbols:
        if fundNames[symbol] in nameList:
            tmp.append(symbol)
    return tmp


# %%快速回测函数
def portfolioBackTest(priceData, targetWeight, tradeCommission=0, rebalanceThreshold=0.10, isTradeCost=False,
                      endDate=None):
    '''
    组合策略快速回测模板
    换仓价格以调仓日收盘价为准
    组合策略回测返回的净值序列从首个调仓日开始，截至输入的资产价格序列的最后一个交易日或endDate
    priceData代表价格序列，dataframe格式，为组合策略中会用到的所有资产价格序列，货币基金采用货币指数代替
    targetWeight为DataFrame格式，index为调仓日，columns为目标持仓标的，当不持有某标的时，权重设为0
    price与targetWeight的columns必须一致，但顺序可以不一致
    tradeCommission为交易费率，单边费率，采用字典、series或单一数值（int,float）格式，columns必须与price一致
    当指定是单一数值时，则自动设定所有涉及调仓的基金统一按此费率
    截止日期可以不指定，默认为价格序列的最后一个交易日，若指定，可以是字符串或datetime格式
    isTradeCost:是否返回历次交易的手续费率，默认不返回
    '''

    # 初始化回测截止日期
    if not endDate:
        endDate = priceData.index[len(priceData) - 1]
    if type(endDate) == str:
        endDate = parse(endDate)

        # 判断调仓日期是否超出价格序列范围
    if targetWeight.index[0] < priceData.index[0] or targetWeight.index[-1] > priceData.index[-1]:
        raise ValueError(u'输入的调仓日期超出价格序列范围，请核对！')

        # 判断回测截止日期是否超出价格序列范围
    if endDate > priceData.index[-1]:
        raise ValueError(u'输入的截止日期超出价格序列范围，请核对！')

        # 判断price与targetWeight的columns是否一致
    if len(set(priceData.columns) - set(targetWeight.columns)) > 0 or len(
            set(targetWeight.columns) - set(priceData.columns)) > 0:
        raise ValueError(u'资产价格序列与目标权重序列标的不一致，请核对！')

        # 转换交易费率格式
    if type(tradeCommission) == dict:
        tradeCommission = pd.Series(tradeCommission)
    elif type(tradeCommission) == int or type(tradeCommission) == float:  # 若手续费率设定为单一数值，则转成series格式，且全部基金按此费率计算
        tradeCommission = pd.Series(tradeCommission, index=priceData.columns)
    else:
        pass

    # 生成自定义基准指数序列
    startIndex = list(priceData.index).index(targetWeight.index[0]) - 1
    if startIndex < 0:
        startIndex = 0
    endIndex = list(priceData.index).index(endDate)
    priceData = priceData.iloc[startIndex:endIndex + 1]

    # 处理价格缺失数据
    price = priceData.fillna(method='ffill')
    price = price.fillna(method='bfill')

    netvalue = pd.Series(1, index=price.index, dtype=float, name='portfolio')
    costDic = {}  # 存储历次交易成本
    for i in range(len(netvalue)):
        if i > 0:
            try:  # 加入try，以保证生成的组合净值回测起始日为1
                tmp = price.loc[netvalue.index[i]]
                tmp.fillna(0, inplace=True)
                netvalue[i] = sum(tmp * position) + cash
            except:
                pass
        # 调仓日再平衡，重新生成持仓数量，并按照交易佣金扣减已计算的当日净值
        if netvalue.index[i] in targetWeight.index:
            weight = targetWeight.loc[netvalue.index[i]].copy()
            weight.fillna(0, inplace=True)
            if weight.sum() < 1:
                cashWeight = 1 - weight.sum()
            else:
                cashWeight = 0
            indexTmp = list(targetWeight.index).index(netvalue.index[i])
            if indexTmp == 0:  # 首次建仓
                tradeCost = np.sum(netvalue[i] * weight * tradeCommission)
                netvalue[i] = netvalue[i] - tradeCost
                position = netvalue[i] * weight / price.loc[netvalue.index[i]]
                position.fillna(0, inplace=True)
                cash = netvalue[i] * cashWeight
            else:
                tradeCost = 0
                actualWeight = price.loc[netvalue.index[i - 1]] * position / np.sum(
                    price.loc[netvalue.index[i - 1]] * position)
                actualWeight.fillna(0, inplace=True)
                for m in weight.index:
                    if actualWeight[m] == 0 or weight[m] == 0:
                        tradeCost += abs(actualWeight[m] - weight[m]) * netvalue[i - 1] * tradeCommission[m]
                    elif abs(actualWeight[m] / weight[m] - 1) > rebalanceThreshold:
                        tradeCost += abs(actualWeight[m] - weight[m]) * netvalue[i - 1] * tradeCommission[m]

                netvalue[i] = netvalue[i] - tradeCost
                position = netvalue[i] * weight / price.loc[netvalue.index[i]]
                position.fillna(0, inplace=True)
                cash = netvalue[i] * cashWeight
            costDic[netvalue.index[i]] = tradeCost / netvalue[i]

    if isTradeCost:
        return netvalue, costDic
    else:
        return netvalue


# %%基金业绩评价函数
# 年化收益率
def annualReturn(priceSeries, cycle, executeDate=None):
    if not executeDate:
        executeDate = priceSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    priceSeries = priceSeries[:executeDate]
    endIndex = min(cycle + 1, len(priceSeries))
    return (priceSeries[-1] / priceSeries[-endIndex]) ** (244 / (endIndex - 1)) - 1  # 1年交易日按照244天计算


# 夏普比率
def sharpe(priceSeries, cycle, risklessReturn, executeDate=None):
    if not executeDate:
        executeDate = priceSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    priceSeries = priceSeries[:executeDate]
    endIndex = min(cycle, len(priceSeries))
    # 计算年化收益率
    myReturn = annualReturn(priceSeries, cycle)
    # 计算年化波动率
    priceSeries = priceSeries.pct_change()[-endIndex:]
    # 计算夏普比率
    return (myReturn - risklessReturn) / priceSeries.std() / np.sqrt(244)


# 年化波动率
def annualVolatility(priceSeries, cycle, executeDate=None):
    if not executeDate:
        executeDate = priceSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    priceSeries = priceSeries[:executeDate]
    endIndex = min(cycle, len(priceSeries))
    priceSeries = priceSeries.pct_change()[-endIndex:]
    return priceSeries.std() * np.sqrt(244)


def halfDecayStd(priceSeries, cycle, halfLifePeriodParam, executeDate=None):
    # halfLifePeriod为半衰期参数取值，一般为1/3，1/2,2/3，0；当为0时，表示无半衰期加权
    if not executeDate:
        executeDate = priceSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    priceSeries = priceSeries[:executeDate]
    endIndex = min(cycle, len(priceSeries))
    returnArray = priceSeries.pct_change()[-endIndex:]
    returnArray.dropna(inplace=True)
    if halfLifePeriodParam == 0:
        return returnArray.std() * np.sqrt(244)
    try:
        # --生成半衰期权重
        seriesLength = len(returnArray)
        halfLifePeriod = round(seriesLength * halfLifePeriodParam)
        lambdaValue = 0.5 ** (1 / halfLifePeriod)
        weightFactor = [lambdaValue ** (seriesLength - t) for t in range(seriesLength)]
        halfLifeWeight = list(np.array(weightFactor) / np.sum(weightFactor))
        halfLifeWeight.reverse()
        # --计算半衰期标准差
        tmp = (returnArray - returnArray.mean()) ** 2
        return np.sqrt(np.sum(tmp * halfLifeWeight) * 244)
    except:
        return np.nan


# 最大回撤
def maxdown(priceSeries, cycle, executeDate=None):
    if not executeDate:
        executeDate = priceSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    priceSeries = priceSeries[:executeDate].dropna().values
    endIndex = min(cycle + 1, len(priceSeries))
    priceSeries = priceSeries[-endIndex:]
    i = np.argmax((np.maximum.accumulate(priceSeries) - priceSeries) / np.maximum.accumulate(priceSeries))  # 结束位置
    if i == 0:
        return 0
    j = np.argmax(priceSeries[:i])  # 开始位置
    return (priceSeries[i] - priceSeries[j]) / priceSeries[j]


# calmar比率
def calmar(priceSeries, cycle, executeDate=None):
    # 计算年化收益率
    myReturn = annualReturn(priceSeries, cycle, executeDate)
    # 计算最大回撤
    drawDown = -maxdown(priceSeries, cycle, executeDate)
    return myReturn / drawDown


# 基金beta值
def beta(priceSeries, cycle, marketIndexData, executeDate=None):
    if not executeDate:
        executeDate = priceSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    priceSeries = priceSeries[:executeDate].dropna()
    endIndex = min(cycle, len(priceSeries))
    returnArray = priceSeries[-endIndex:].pct_change()
    indexReturn = marketIndexData[returnArray.index[0]:returnArray.index[-1]].pct_change()
    tmp = pd.concat([returnArray, indexReturn], axis=1)
    return tmp.cov().iloc[0, 1] / tmp.cov().iloc[1, 1]


# 信息比率
def informationRatio(priceSeries, cycle, marketIndexData, executeDate=None):
    if not executeDate:
        executeDate = priceSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    priceSeries = priceSeries[:executeDate].dropna()
    endIndex = min(cycle, len(priceSeries))
    y = priceSeries[-endIndex:].pct_change().dropna()
    x = marketIndexData.pct_change()[y.index]
    alpha = y.mean() - x.mean()
    e = (y - x).std()
    return alpha / e


# 股票仓位波动率
def stockProportionVol(stockProportionSeries, periodLength, executeDate=None):
    if not executeDate:
        executeDate = stockProportionSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    stockProportionSeries = stockProportionSeries[stockProportionSeries.index < executeDate + timedelta(1)]
    if (stockProportionSeries.dropna()) < periodLength:
        return np.nan
    return stockProportionSeries[-periodLength:].std()


# 股票仓位极差值
def stockProportionRange(stockProportionSeries, periodLength, executeDate=None):
    if not executeDate:
        executeDate = stockProportionSeries.index[-1]
    if type(executeDate) == str:
        executeDate = parse(executeDate)
    stockProportionSeries = stockProportionSeries[stockProportionSeries.index < executeDate + timedelta(1)]
    stockProportionSeries = stockProportionSeries[-periodLength:]
    if (stockProportionSeries.dropna()) < periodLength:
        return np.nan
    return stockProportionSeries.max() - stockProportionSeries.min()
