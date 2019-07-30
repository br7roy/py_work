# -*- coding: utf-8 -*-
"""
基金单指标排序打分模块
"""
import pandas as pd
import numpy as np
import copy
from datetime import datetime, timedelta
from dateutil.parser import parse
from fof.algorithm.perEvalFunction import *
from fof.algorithm.getData_sql import *


# 单一基金标的单评价指标打分类模块
from util.bus_const import INDEX_CODE_NAME_CACHE


class indexPerVal:
    def __init__(self, btParms):
        self.indexName = btParms['indexName']  # 指标名称
        self.symbol = btParms['symbol']
        self.cycle = btParms['cycle']  # 指标回看周期长度,当为数字时以年为单位
        self.marketIndex = btParms['marketIndex']  # 市场指数，默认为''
        self.otherPar = btParms['otherPar']  # 其他需要指定的参数,字符串或list格式

        # 加载函数
        try:
            self.transformDataType()
            self.genrPeriod()
            self.getDataFromDb()
            self.genrFactorValue()
            self.genrOutput()
        except:
            # raise ValueError('wrong!')
            output_1 = {'factorValue': np.nan}
            output_1.update(
                {'cycle': self.cycle, 'indexName': self.indexName})
            self.output = output_1

            output_2 = {'factorValue': ''}
            output_2.update(
                {'cycle': self.cycle, 'indexName': self.indexName})
            self.output_json = output_2

    # 此处可以将从前端拿到的json格式数据批量转换成该类中需要的数据格式
    def transformDataType(self):
        if self.otherPar:
            if type(self.otherPar) == str:
                self.otherPar = [eval(self.otherPar)]
            else:
                self.otherPar = [eval(x) for x in self.otherPar]

    def genrPeriod(self):
        # 若cycle设定是起始日期格式
        if ',' in self.cycle:
            self.startDate = self.cycle.split(',')[0]
            self.endDate = self.cycle.split(',')[1]
        # 若cycle设定的不是起始日期格式
        else:
            tdays = getData_tradeDays(datetime.today() - timedelta(365 * 4), datetime.today(), '日')
            self.endDate = datetime.strftime(datetime.today(), '%Y%m%d')
            if self.cycle == '今年以来':
                self.startDate = datetime.strftime([m for m in tdays
                                                    if m <= datetime(datetime.today().year - 1, 12, 31)][-1], '%Y%m%d')
            elif self.cycle == '去年':
                self.startDate = datetime.strftime([m for m in tdays
                                                    if m <= datetime(datetime.today().year - 2, 12, 31)][-1], '%Y%m%d')
                self.endDate = datetime.strftime(datetime(datetime.today().year - 1, 12, 31), '%Y%m%d')
            elif self.cycle == '前年':
                self.startDate = datetime.strftime([m for m in tdays
                                                    if m <= datetime(datetime.today().year - 3, 12, 31)][-1], '%Y%m%d')
                self.endDate = datetime.strftime(datetime(datetime.today().year - 2, 12, 31), '%Y%m%d')
            else:
                cycle = round(eval(self.cycle) * 365)
                self.startDate = datetime.strftime(parse(self.endDate) - timedelta(cycle), '%Y%m%d')

    # 从数据库获取回测中要用到的数据
    def getDataFromDb(self):
        # 提取symbol对应的收盘价或复权净值数据
        try:
            tmp = getData_fundHistoryData('adjNav', self.symbol, self.startDate, self.endDate)
        except:
            tmp = getData_marketIndex(self.symbol, self.startDate, self.endDate)

        fundData_0 = tmp
        # 若指标需要输入市场基准数据，则提取
        marketIndexData = None
        if self.marketIndex:
            marketIndexData = getData_marketIndex(self.marketIndex, self.startDate, self.endDate)

        self.fundData_0 = pd.DataFrame(fundData_0)
        self.fundData = [self.fundData_0, self.fundData_0, self.fundData_0]
        # 市场指数数据
        self.marketIndexData = marketIndexData

    def genrFactorValue(self):
        # 根据startDate与endDate转换成交易日频的cycle
        cycle_T = len(self.fundData[0]) - 1
        factorValue = dict()
        execDate = self.fundData[0].index[-1]
        for symbol in list(self.fundData[0].columns):
            factorValue[symbol] = performanceEval(self.indexName, self.fundData, symbol, cycle_T,
                                                  self.marketIndexData, self.otherPar, execDate)

        factorValue = pd.Series(factorValue, name=self.indexName)
        self.factorValue = factorValue

    def genrOutput(self):

        # python格式结果
        output_batch = {'factorValue': self.factorValue}
        output_batch.update({'cycle': self.cycle, 'indexName': self.indexName})
        output_batch_python = copy.deepcopy(output_batch)

        # 结果转成json，便于前端调用
        factorValue = self.factorValue.copy()
        factorValue.fillna('', inplace=True)
        output_batch_python['factorValue'] = factorValue.astype(str).to_dict()

        self.output = output_batch
        self.output_json = output_batch_python


def exTractVal(indicator, fundCodes, startDate, endDate):
    iName = INDEX_CODE_NAME_CACHE[indicator]
    btParms = {'indexName': iName, 'cycle': startDate + "," + endDate, 'symbol': fundCodes,
               'marketIndex': '000906.SH', 'otherPar': '0.05'}

    self = indexPerVal(btParms)
    output = self.output
    output_json = self.output_json
    # print(output_json)
    return output_json['factorValue']

if __name__ == '__main__':
    INDEX_CODE_NAME_CACHE={"1":"信息比率","2":"夏普比率","3":"最大回撤"}
    # indicator, fundCodes, startDate, endDate
    indicators = ['1', '2', '3']
    fundCodes = ['001050.OF', '000001.OF']
    startDate = '20100101'
    endDate = '20180930'

    btParms = {'indexName': '信息比率', 'cycle': startDate+","+endDate, 'symbol': fundCodes,
               'marketIndex': '000906.SH', 'otherPar': '0.05'}
    # btParms = {'indexName': '区间收益率', 'cycle': '20100101,20180930', 'symbol': ['000906.SH'], 'marketIndex': '000906.SH',
    #            'otherPar': '0.05'}
    # 这个函数提供多指标 多基金计算
    rr = [ exTractVal(indicator,fundCodes,startDate,endDate) for indicator in indicators if indicator  in INDEX_CODE_NAME_CACHE]

    print(rr)







    #
    # self = indexPerVal(btParms)
    # output = self.output
    # output_json = self.output_json
    # print(output_json)
    # # output_all.append(output)
