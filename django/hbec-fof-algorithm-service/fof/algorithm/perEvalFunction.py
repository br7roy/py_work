# -*- coding: utf-8 -*-

"""
业绩评价相关函数
为避免自定义的函数与其他函数命名产生重叠，业绩评价类函数均以perEval开头，即performanceEvaluation的缩写
由于该系列函数不仅用于前端显示，还用于其他模块的计算，如基金综合筛选，组合回测模块等
当该系列函数中有以_开头的，表明该函数仅用于其他业绩评价指标的计算，不直接暴露给前端交互
为便于批量计算，该系列函数均不涉及数据库交互，需要在计算时先另从数据库提取数据，然后带入函数中
为便于非python语言调取该系列函数，额外设定了一个参数：dataType，可选项为'python','json',
当选项为python时，价格序列输入格式为pd.Series格式,输出为float格式
当为json时：价格序列输入为json格式,{'2010/1/4':'1.01','2010/1/5':'1.07','2010/1/6':''},空值用空字符串表示；其他
单值参数设定为字符串格式，如cycle设定为'120',risklessReturn设定为'0.035'
输出格式转换为json,其中当无计算结果时，输出为空值；结果形式为{'output':'0.37'}
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from datetime import datetime
from dateutil.parser import parse
from scipy.stats import norm
from fof.algorithm.getData_sql import *


# 根据基金类型缺省配置marketIndex
def getIndexMap(classify='windFirst'):
    marketIndexMap_windFirst = {'股票型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                '混合型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                '债券型基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                '货币市场型基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                '另类投资基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                '国际(QDII)基金': {'type': 'fundIndex', 'code': 'H11026.CSI'}}

    marketIndexMap_windSecond = {'国际(QDII)债券型基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '中长期纯债型基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '被动指数型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                 '股票多空基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '偏股混合型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                 '偏债混合型基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '混合债券型二级基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '平衡混合型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                 '混合债券型一级基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '商品型基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 'REITs基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '短期纯债型基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '普通股票型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                 '增强指数型债券基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '国际(QDII)股票型基金': {'type': 'fundIndex', 'code': 'H11026.CSI'},
                                 '灵活配置型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                 '国际(QDII)混合型基金': {'type': 'fundIndex', 'code': 'H11026.CSI'},
                                 '被动指数型债券基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'},
                                 '增强指数型基金': {'type': 'stockIndex', 'code': '000906.SH'},
                                 '国际(QDII)另类投资基金': {'type': 'bondIndex', 'code': 'CBA00301.CS'}}
    if classify == 'windFirst':
        return marketIndexMap_windFirst
    else:
        return marketIndexMap_windSecond


# json格式的输入数据转为pd.Series
def _jsonToSerise(data):
    data = pd.Series(data)
    data = pd.to_numeric(data, errors='ignore')
    data.index = [parse(m) for m in data.index]
    data.sort_index(inplace=True)
    return data


# 年化收益率,中间函数，仅用于计算其他指标，不暴露给前端
def perEval_annualReturn(priceSeries, cycle, execDate='', dataType='python'):
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        cycle = eval(cycle)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        endIndex = cycle + 1
        output = (priceSeries[-1] / priceSeries[-endIndex]) ** (242 / (endIndex - 1)) - 1  # 1年交易日按照242天计算，下同
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# 区间收益率
# 输入示例：priceSeries={'2010/1/4':'1.01','2010/1/5':'1.07','2010/1/6':''}
# 输出示例：{'output':'0.20'}
def perEval_periodReturn(priceSeries, cycle, execDate='', dataType='python'):
    '''
    priceSeries代表价格序列，在函数外部通过数据库调取，前端客户实际输入的是基金的代码，如'000001.OF'，下同
    priceSeries序列长度随意，但必须大于cycle,为了提高运算速度同时也避免意外报错，priceSerie长度可以设定为cycle+10
    cycle代表回看天数，字符串格式，数据源自于前端客户输入，下同
    exceDate代表执行日期，字符串格式，当为空时，自动设定为priceSeries序列的日期升序排列的最后日期，下同
    dataType代表输入输出数据格式，若为json，则该参数值设定为'json'
    '''
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        cycle = eval(cycle)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        endIndex = cycle + 1
        output = (priceSeries[-1] / priceSeries[-endIndex]) - 1
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# 夏普比率
def perEval_sharpe(priceSeries, cycle, risklessReturn, execDate='', dataType='python'):
    # risklessReturn代表无风险收益率，字符串格式，默认为‘0.035’，该参数在1.0版本中可以不暴露给前端，后续版本中会改进无风险利率指定方法
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        cycle = eval(cycle)
        risklessReturn = eval(risklessReturn)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        # 计算年化收益率
        myReturn = perEval_annualReturn(priceSeries, cycle)
        # 计算年化波动率
        priceSeries = priceSeries.pct_change()[-cycle:]
        myStd = priceSeries.std()
        # 计算夏普比率
        if myStd == 0:
            output = np.nan
        else:
            output = (myReturn - risklessReturn) / (myStd * np.sqrt(242))

    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# 年化波动率
def perEval_annualVolatility(priceSeries, cycle, halfLifePeriodParam, execDate='', dataType='python'):
    # halfLifePeriod为半衰期参数取值，字符串格式，一般为‘1/3’，‘1/2’,‘2/3’，‘0’；默认为‘0’，当为‘0’时，表示无半衰期加权
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        cycle = eval(cycle)
        halfLifePeriodParam = eval(halfLifePeriodParam)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        returnArray = priceSeries.pct_change()[-cycle:]
        if halfLifePeriodParam == 0:
            output = returnArray.std() * np.sqrt(242)
        else:
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
                output = np.sqrt(np.sum(tmp * halfLifeWeight) * 242)
            except:
                output = np.nan

    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output

    # 最大回撤


def perEval_maxdown(priceSeries, cycle, execDate='', dataType='python'):
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        cycle = eval(cycle)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna().values
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        endIndex = cycle + 1
        priceSeries = priceSeries[-endIndex:]
        i = np.argmax((np.maximum.accumulate(priceSeries) - priceSeries) / np.maximum.accumulate(priceSeries))  # 结束位置
        if i == 0:
            output = 0
        else:
            j = np.argmax(priceSeries[:i])  # 开始位置
            output = (priceSeries[i] - priceSeries[j]) / priceSeries[j]

    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output

    # 卡玛比率


def perEval_calmar(priceSeries, cycle, execDate='', dataType='python'):
    # 计算年化收益率
    myReturn = perEval_annualReturn(priceSeries, cycle, execDate, dataType)
    # 计算最大回撤
    drawDown = perEval_maxdown(priceSeries, cycle, execDate, dataType)

    if dataType == 'json':
        try:
            return {'output': str(eval(myReturn['output']) / eval(drawDown['output']) * (-1))}
        except:
            return {'output': ''}
    else:
        return -myReturn / drawDown if drawDown != 0 else np.nan


# 信息比率
def perEval_informationRatio(priceSeries, cycle, marketIndexData, execDate='', dataType='python'):
    '''
    marketIndexData代表计算指标需要用到的基准指数数据，通过数据库调取
    前端客户实际输入的为基准指数代码，1.0版本该参数可以不暴露出来，系统默认配置
    若基金为股票型基金，则基准指定为中证800指数(000906.SH)，若为债券型基金，则指定为中债总财富指数(CBA00301.CS)
    '''
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        marketIndexData = _jsonToSerise(marketIndexData)
        cycle = eval(cycle)

    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        endIndex = cycle + 1
        # 计算IR
        y = priceSeries.pct_change()[-endIndex:].dropna()
        x = marketIndexData.pct_change().reindex(y.index, method='ffill')
        x = sm.add_constant(x)
        alpha = sm.OLS(y.values, x.values).fit().params[0]  # 0，a，-1，b
        extradaysReturn = y - marketIndexData.pct_change()[y.index]
        if extradaysReturn.std() == 0:
            output = np.nan
        else:
            output = alpha / extradaysReturn.std()
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output

    # beta系数


def perEval_beta(priceSeries, cycle, marketIndexData, execDate='', dataType='python'):
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        marketIndexData = _jsonToSerise(marketIndexData)
        cycle = eval(cycle)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    marketIndexData = marketIndexData.reindex(priceSeries.index, method='ffill')
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        # 基准指数方差
        marketVar = marketIndexData.pct_change()[-cycle:].var()
        # 计算beta
        x = priceSeries.pct_change()[-cycle:].dropna()
        y = marketIndexData.pct_change().reindex(x.index, method='ffill')
        output = np.cov(x, y)[0, 1] / marketVar
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# 在险价值
def perEval_VaR(priceSeries, cycle, confidenceLevel, execDate='', dataType='python'):
    # confidenceLevel：置信水平，默认设定为‘0.05’,其他可选参数:‘0.01’，‘0.10’
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        cycle = eval(cycle)
        confidenceLevel = eval(confidenceLevel)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        # 用期望收益作为分布的均值
        myReturn = perEval_annualReturn(priceSeries, cycle)
        # 样本标准差
        normFun = norm()
        sigma = priceSeries.pct_change()[-cycle:].std() * np.sqrt(242)
        alphaValue = normFun.ppf(1 - confidenceLevel)
        output = alphaValue * sigma - myReturn
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# M平方，总风险调整收益指标
def perEval_M2(priceSeries, cycle, marketIndexData, risklessReturn, execDate='', dataType='python'):
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        marketIndexData = _jsonToSerise(marketIndexData)
        cycle = eval(cycle)
        risklessReturn = eval(risklessReturn)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    marketIndexData = marketIndexData.reindex(priceSeries.index, method='ffill')
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        # 计算基金区间内收益率均值
        myReturn = priceSeries.pct_change()[-cycle:].mean() * 242
        # 计算基金日频波动率
        myStd = (priceSeries.pct_change()[-cycle:]).std() * np.sqrt(242)
        # 计算市场组合收益率均值
        marketReturn = marketIndexData.pct_change()[-cycle:].mean() * 242
        # 计算市场组合日频波动率
        marketStd = (marketIndexData.pct_change()[-cycle:]).std() * np.sqrt(242)
        # 计算M2
        if myStd == 0:
            output = np.nan
        else:
            output = marketStd / myStd * (myReturn - risklessReturn) - marketReturn + risklessReturn
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# 索提诺比率
def perEval_sortino(priceSeries, cycle, minimumAcceptableReturn, execDate='', dataType='python'):
    # minimumAcceptableReturn：为最小可接受收益率，当无输入时，默认为无风险收益率，设定为0.035

    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        cycle = eval(cycle)
        minimumAcceptableReturn = eval(minimumAcceptableReturn)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        # 计算年化收益率
        myReturn = perEval_annualReturn(priceSeries, cycle)
        # 计算下行波动率
        returntmp = priceSeries.pct_change()[-cycle:].dropna()
        returntmp[returntmp > minimumAcceptableReturn / 242] = minimumAcceptableReturn / 242
        mystdDown = np.sqrt(pow(returntmp - minimumAcceptableReturn / 242, 2).sum() / len(returntmp)) * np.sqrt(242)
        # 计算索提诺比率
        if mystdDown == 0:
            output = np.nan
        else:
            output = (myReturn - minimumAcceptableReturn) / mystdDown
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# 特雷诺比率
def perEval_treynor(priceSeries, cycle, marketIndexData, risklessReturn, execDate='', dataType='python'):
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        marketIndexData = _jsonToSerise(marketIndexData)
        cycle = eval(cycle)
        risklessReturn = eval(risklessReturn)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    marketIndexData = marketIndexData.reindex(priceSeries.index, method='ffill')
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        # 计算基金年化收益率
        myReturn = perEval_annualReturn(priceSeries, cycle)
        # 市场组合的年化波动率
        marketVar = marketIndexData.pct_change()[-cycle:].var()
        # 计算beta
        x = priceSeries.pct_change()[-cycle:].dropna()
        y = marketIndexData.pct_change()[x.index]
        mybeta = np.cov(x, y)[0, 1] / marketVar
        # 计算特雷诺比率
        if mybeta == 0:
            output = np.nan
        else:
            output = (myReturn - risklessReturn) / mybeta
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# 詹森值
def perEval_jensen(priceSeries, cycle, marketIndexData, execDate='', dataType='python'):
    if dataType == 'json':
        priceSeries = _jsonToSerise(priceSeries)
        marketIndexData = _jsonToSerise(marketIndexData)
        cycle = eval(cycle)
    if not execDate:
        execDate = priceSeries.index[-1]
    if type(execDate) == str:
        execDate = parse(execDate)
    priceSeries = priceSeries[:execDate].dropna()
    marketIndexData = marketIndexData.reindex(priceSeries.index, method='ffill')
    if len(priceSeries) <= cycle:
        output = np.nan
    else:
        # 计算alpha
        y = priceSeries.pct_change()[-cycle:].dropna()
        x = marketIndexData.pct_change()[y.index]
        x = sm.add_constant(x)
        output = sm.OLS(y.values, x.values).fit().params[0]  # 0，a，-1，b
    if dataType == 'json':
        return {'output': ''} if pd.isnull(output) else {'output': str(output)}
    else:
        return output


# %% 基金指标信息设定函数（该函数仅用于其他底层模型的计算，不暴露给前端）
def setIndexInformation():
    indexInformation = {'年化收益率': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '区间收益率': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '夏普比率': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '年化波动率': {'fundDataType': 'adjNav', 'sortMode': 'ascend'},
                        '信息比率': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '贝塔系数': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '卡玛比率': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '最大回撤': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '在险价值': {'fundDataType': 'adjNav', 'sortMode': 'ascend'},
                        '索提诺比率': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '特雷诺比率': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        '詹森值': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        'M平方': {'fundDataType': 'adjNav', 'sortMode': 'descend'},
                        }
    return indexInformation


# 基金评价指标批量计算统一函数（该函数仅用于其他底层模型的计算，不暴露给前端）
def performanceEval(indexName, fundData, symbol, cycle, marketIndexData, otherPar, execDate):
    if indexName == '年化收益率':
        data = fundData[0][symbol]
        return perEval_annualReturn(data, cycle, execDate)
    elif indexName == '区间收益率':
        data = fundData[0][symbol]
        return perEval_periodReturn(data, cycle, execDate)
    elif indexName == '夏普比率':
        data = fundData[0][symbol]
        risklessReturn = otherPar[0]
        return perEval_sharpe(data, cycle, risklessReturn, execDate)
    elif indexName == '年化波动率':
        data = fundData[0][symbol]
        halfLifePeriodParam = otherPar[0]
        return perEval_annualVolatility(data, cycle, halfLifePeriodParam, execDate)
    elif indexName == '最大回撤':
        data = fundData[0][symbol]
        return perEval_maxdown(data, cycle, execDate)
    elif indexName == '卡玛比率':
        data = fundData[0][symbol]
        return perEval_calmar(data, cycle, execDate)
    elif indexName == '贝塔系数':
        data = fundData[0][symbol]
        return perEval_beta(data, cycle, marketIndexData, execDate)
    elif indexName == '信息比率':
        data = fundData[0][symbol]
        return perEval_informationRatio(data, cycle, marketIndexData, execDate)
    elif indexName == '在险价值':
        data = fundData[0][symbol]
        confidenceLevel = otherPar[0]
        return perEval_VaR(data, cycle, confidenceLevel, execDate)
    elif indexName == '索提诺比率':
        data = fundData[0][symbol]
        minimumAcceptableReturn = otherPar[0]
        return perEval_sortino(data, cycle, minimumAcceptableReturn, execDate)
    elif indexName == '特雷诺比率':
        data = fundData[0][symbol]
        risklessReturn = otherPar[0]
        return perEval_treynor(data, cycle, marketIndexData, risklessReturn, execDate)
    elif indexName == '詹森值':
        data = fundData[0][symbol]
        return perEval_jensen(data, cycle, marketIndexData, execDate)
    elif indexName == 'M平方':
        data = fundData[0][symbol]
        risklessReturn = otherPar[0]
        return perEval_M2(data, cycle, marketIndexData, risklessReturn, execDate)


if __name__ == '__main__':
    data = getData_fundHistoryData('adjNav', '000001.OF', '2017/1/1', datetime.today())
    data1 = data.astype(str)
    data1.index = [datetime.strftime(m, '%Y/%m/%d') for m in data1.index]
    data_json = data1.to_dict()
    marketIndexData = getData_marketIndex('000906.SH', '2017/1/1', datetime.today())
    marketIndexData1 = marketIndexData.astype(str)
    marketIndexData1.index = [datetime.strftime(m, '%Y/%m/%d') for m in marketIndexData1.index]
    marketIndexData_json = marketIndexData1.to_dict()

    # 年化收益率
    res_periodReturn_python = perEval_annualReturn(data, 120)
    res_periodReturn_json = perEval_annualReturn(data_json, '120', dataType='json')

    # 区间收益率
    res_periodReturn_python = perEval_periodReturn(data, 120)
    res_periodReturn_json = perEval_periodReturn(data_json, '120', dataType='json')
    # 夏普比率
    res_sharpe_python = perEval_sharpe(data, 242, 0.035)
    res_sharpe_json = perEval_sharpe(data_json, '242', '0.035', dataType='json')
    # 年化波动率
    res_vol_python = perEval_annualVolatility(data, 242, 0, execDate='')
    res_vol_json = perEval_annualVolatility(data_json, '242', '0', execDate='', dataType='json')
    # 最大回撤
    res_maxdown_python = perEval_maxdown(data, 242, execDate='')
    res_maxdown_json = perEval_maxdown(data_json, '242', execDate='', dataType='json')
    # 卡玛比率
    res_calmar_python = perEval_calmar(data, 242, execDate='')
    res_calmar_json = perEval_calmar(data_json, '242', execDate='', dataType='json')
    # 信息比率
    res_ir_python = perEval_informationRatio(data, 242, marketIndexData, execDate='')
    res_ir_json = perEval_informationRatio(data_json, '242', marketIndexData_json, execDate='', dataType='json')
    # beta
    res_beta_python = perEval_beta(data, 242, marketIndexData, execDate='')
    res_beta_json = perEval_beta(data_json, '242', marketIndexData_json, execDate='', dataType='json')
    # VaR
    res_var_python = perEval_VaR(data, 242, 0.05, execDate='')
    res_var_json = perEval_VaR(data_json, '242', '0.05', execDate='', dataType='json')
    # M2
    res_m2_python = perEval_M2(data, 242, marketIndexData, 0.035, execDate='')
    res_m2_json = perEval_M2(data_json, '242', marketIndexData_json, '0.035', execDate='', dataType='json')
    # sortino
    res_sortino_python = perEval_sortino(data, 242, 0.035, execDate='')
    res_sortino_json = perEval_sortino(data_json, '242', '0.035', execDate='', dataType='json')
    # 特雷诺
    res_treynor_python = perEval_treynor(data, 242, marketIndexData, 0.035, execDate='')
    res_treynor_json = perEval_treynor(data_json, '242', marketIndexData_json, '0.035', execDate='', dataType='json')
    # 詹森值
    res_jensen_python = perEval_jensen(data, 242, marketIndexData, execDate='')
    res_jensen_json = perEval_jensen(data_json, '242', marketIndexData_json, execDate='', dataType='json')

    print('res_periodReturn_json is %s' % res_periodReturn_json)
    print('res_sharpe_json is %s' % res_sharpe_json)
    print('res_vol_json is %s' % res_vol_json)
    print('res_maxdown_json is %s' % res_maxdown_json)
    print('res_calmar_json is %s' % res_calmar_json)
    print('res_ir_json is %s' % res_ir_json)
    print('res_beta_json is %s' % res_beta_json)
    print('res_var_json is %s' % res_var_json)
    print('res_m2_json is %s' % res_m2_json)
    print('res_sortino_json is %s' % res_sortino_json)
    print('res_treynor_json is %s' % res_treynor_json)
    print('res_jensen_json is %s' % res_jensen_json)


















