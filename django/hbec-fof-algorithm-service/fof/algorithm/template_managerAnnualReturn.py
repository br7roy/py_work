# -*- coding: utf-8 -*-
"""
基金经理分析系列类模块
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.parser import parse
from fof.algorithm.getData_sql import *
from fof.algorithm.perEvalFunction import *


# 基金经理任职期年化回报率，批量计算,实例化类后调取类的属性output即可
class managerAnnualReturn:
    def __init__(self):
        self.getDataFromDb()
        self.getAnnualReturn()
        self.getOtherInfo()

    def getDataFromDb(self):
        # 基金经理任职期数据
        self.managerInfo = getData_fundManagerInfo_all()
        # 获取全部基金的历史复权净值数据
        symbolList = list(set(self.managerInfo['fund'].tolist()))
        self.fundNav = getData_fundHistoryData('adjNav', symbolList, '2000/1/1')

    def getAnnualReturn(self):
        managerInfo = self.managerInfo
        tmp = []
        for m in self.managerInfo.index:
            try:
                data = self.fundNav[managerInfo.loc[m, 'fund']]
                startDate = parse(managerInfo.loc[m, 'startDate'])
                endDate = parse(managerInfo.loc[m, 'endDate'])
                tmp.append(self.annualReturn(data, startDate, endDate))
            except:
                tmp.append(np.nan)
        managerInfo['annualReturn'] = tmp
        self.output = managerInfo

    def getOtherInfo(self):
        output = self.output
        tmp = output.loc[output['endDate'] == datetime.strftime(datetime.today(), '%Y%m%d')]
        symbolList = list(set(tmp['fund'].values))
        # 获取最新的基金净值数据
        fundNav = getData_fundSpecDateData('nav', symbolList, datetime.today())
        fundShare = getData_fundSpecDateData('fundShare_unit', symbolList, datetime.today())
        fundScale = fundNav * fundShare * 10000
        # 特殊货币型基金规模调整，除以100
        specSymbols = ['511880.SH', '003816.OF', '004473.OF']
        for symbol in fundScale.index:
            if symbol in specSymbols:
                fundScale[symbol] = fundScale[symbol] / 100

        # 补充最新规模数据
        tmp = []
        for m in output.index:
            try:
                tmp.append(fundScale[output.loc[m, 'fund']])
            except:
                tmp.append(np.nan)
        output['fundScale'] = tmp

        # 补充最新净值数据
        tmp = []
        for m in output.index:
            try:
                tmp.append(fundNav[output.loc[m, 'fund']])
            except:
                tmp.append(np.nan)
        output['fundNav'] = tmp

        self.output = output

    @staticmethod
    def annualReturn(data, startDate, endDate):
        data = data[startDate:endDate].dropna()
        if len(data) == 0:
            return np.nan
        return (data[-1] / data[0]) ** (242 / (len(data) - 1)) - 1


if __name__ == '__main__':
    '''
    批量运行基金经理任职期年化收益率，
    若endDate为今天，则该产品为基金经理正任职的产品，
    若不为今天，则为历史任职产品  
    基金规模单位为元，若产品已到期，则基金为np.nan
    程序运行较慢，大概需要20~30分钟
    主要是调取所有基金的历史复权净值数据过慢，该数据以后写入redis后
    会提升很多
    '''
    self = managerAnnualReturn()
    managerReturn = self.output
    print(managerReturn.loc[5])

