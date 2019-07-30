# -*- coding: utf-8 -*-
"""
基金经理行业配置能力
行业采用中信一级行业分类
类industryAllocationAbility_manager为基金经理的行业配置能力考查，输入参数为btParms涵盖基金名称与基金经理
输出结果存放于output中，为一个字典，其中alloDistribute为基金经理任职期以来（剔除建仓期3个月）各季行业配置比例，
中信一级共29个行业，但不是所有行业该基金经理历史上都会有配置，故alloDistribute的columns仅为历史曾经配置过的行业
alloEvaluation为任职期以来，基金经理在各行业上的配置绩效统计，涵盖平均配置比例、平均配置得分以及配置次数占比
alloScore为基金经理任职期以来各期配置得分;managerId为基金经理id值

本程序已写成批量更新形式，最终的结果保存在output_all中，将该结果存执fof数据库即可，
若alloScore为空，则结果无需存入数据库
请于每季结束后的第一个月的15日开始运行本程序，按日更新，运行至该月末
如1季度结束后，于4月15日~4月30日每日更新该数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.parser import parse

from conf import mysqlops
from conf.data_source import MysqlConf
from fof.algorithm.getData_sql import *

# 一次性获取公共数据
from util import uuid_util
from util.num_util import transformFloatIfAvaliable4


def getPublicDataAllocation():
    # 调取所有股票所属行业
    stockSymbol = getData_stockConstitue('aStock')
    info = getData_stockInformation(stockSymbol)
    stockIndus = pd.Series(info)

    # 调取中信行业指数数据
    indusNameList = list(pd.Series(list(set(stockIndus))).dropna())
    indusNet = []
    indusCodes = industryMap('CI')  # 把中信一级行业名称转为代码
    for name in indusNameList:
        indusCode = indusCodes[name]
        tmp = getData_marketIndex(indusCode, '2002/1/1', datetime.today())
        indusNet.append(tmp)
    indusNet = pd.concat(indusNet, axis=1)
    indusNet.columns = indusNameList  # 将行业代码转为行业名称
    indusNet.fillna(method='ffill', inplace=True)  # 填充nan值，避免报错
    return stockIndus, indusNet


# 基金行业配置能力考查
class industryAllocation:
    def __init__(self, btParms, stockIndus, indusNet):
        self.symbol = btParms['symbol']  # 基金代码
        self.startDate = btParms['startDate']  # 起始日期
        self.endDate = btParms['endDate']  # 结束日期
        self.stockIndus = stockIndus
        self.indusNet = indusNet

        self.transformDataType()
        self.getDataFromDb()
        self.alloScore_all()
        self.alloDistribute_all()
        self.alloEvaluation_indus_all()
        self.generateOutput()

    # 将前端拿到的json格式数据批量转换成该类中需要的数据格式
    def transformDataType(self):
        # 为能够兼容sql语句，startDate与endDate统一转成特定字符串格式
        # 对应mongodb的系列getData函数中，涉及日期的输入参数支持datetime与字符串两种格式
        # 故使用getData系列函数中，无需再转换日期格式
        try:
            self.startDate = datetime.strftime(parse(self.startDate), '%Y%m%d')
        except:
            self.startDate = datetime.strftime(self.startDate, '%Y%m%d')
        try:
            self.endDate = datetime.strftime(parse(self.endDate), '%Y%m%d')
        except:
            self.endDate = datetime.strftime(self.endDate, '%Y%m%d')

    # 从数据库获取模型中要用到的数据
    def getDataFromDb(self):
        indusNet = self.indusNet
        stockIndus = self.stockIndus
        # 调取基金持仓数据
        quarterList = pd.date_range(self.startDate, self.endDate, freq='Q')
        allfundHolding = []
        realQuarterList = []  # 真实可取到的基金财报数据
        for i in range(len(quarterList)):
            quarter = quarterList[i]
            fundHolding = getData_fundSecHoldingData('mainStockHolding', self.symbol, quarter)[['股票代码', '持股市值']]
            fundHolding = fundHolding.set_index('股票代码')
            if len(fundHolding) > 0:
                allfundHolding.append(fundHolding)
                realQuarterList.append(quarter)

        if len(allfundHolding) > 0:
            allfundHolding = pd.concat(allfundHolding, axis=1, sort=True)
            allfundHolding.columns = realQuarterList
            self.allfundHolding = allfundHolding
        else:
            self.allfundHolding = pd.DataFrame()

        # 调取交易日频的季度交易日期序列
        if len(realQuarterList) > 0:
            self.quarterList1 = getData_tradeDays(realQuarterList[0] - timedelta(10), realQuarterList[-1], '季')
            self.quarterList2 = pd.date_range(realQuarterList[0], realQuarterList[-1], freq='Q')

    # 计算单季度行业配置比例
    def alloDistribute_single(self, execDate):
        # 计算结果可采用return形式，供类中的all系列函数调用
        # 若某行业无配置，则比例设定为0
        fundHolding = pd.DataFrame(self.allfundHolding[execDate].dropna())
        fundHolding['weight'] = fundHolding.iloc[:, 0] / (fundHolding.iloc[:, 0].sum())
        # 若某标的物行业对应分类，则设定为综合
        try:
            fundHolding['indus'] = self.stockIndus[fundHolding.index].values
        except:
            fundHolding['indus'] = '综合'
        singleDistribute = fundHolding.groupby('indus')['weight'].sum()
        return singleDistribute

    # 计算单季度行业配置得分，采用每期的期初持仓
    def alloScore_single(self, execDate):
        # 计算结果可采用return形式，供类中的all系列函数调用
        # 配置打分区间采用range(1,len(indusCounts)+1)形式，从而可以更换至其他行业分类，如中信一级行业
        quarterList1 = self.quarterList1
        quarterList2 = self.quarterList2
        indusNetQuarter = self.indusNet.loc[quarterList1]
        indusNetQuarter.index = quarterList2
        indusRetQuarter = indusNetQuarter.pct_change()
        quarterList = list(self.allfundHolding.columns)
        idx = quarterList.index(execDate)
        lastquarter = quarterList[idx - 1]
        ret = indusRetQuarter.loc[execDate].sort_values(ascending=True)
        score = pd.Series(list(range(1, len(ret) + 1)), index=ret.index)
        weight = self.alloDistribute_single(lastquarter)
        singleScore = (score[weight.index] * weight).sum()
        return singleScore

    # 计算历史各期行业配置比例
    def alloDistribute_all(self):
        # 将单季度计算的行业配置分布转为各行业历史各期行业配置比例，若某期某行业没有配置，则设为0
        allDistribute = []
        if len(self.allfundHolding.columns) > 1:
            quarterList = list(self.allfundHolding.columns)
            for execDate in quarterList:
                singleDistribute = self.alloDistribute_single(execDate)
                allDistribute.append(singleDistribute)
            allDistribute = pd.concat(allDistribute, axis=1, sort=True)
            allDistribute.columns = quarterList
        self.allDistribute = allDistribute

    # 计算历史各期行业配置得分,采用上季持仓与当季收益计算得分
    def alloScore_all(self):
        allScore = []
        if len(self.allfundHolding.columns) > 1:
            quarterList = list(self.allfundHolding.columns)
            allScore = pd.Series(index=quarterList, name='allScore')
            for i in range(1, len(quarterList)):
                singleScore = self.alloScore_single(quarterList[i])
                allScore[i] = singleScore
        self.allScore = allScore

    # 从单个行业视角，计算单个行业历史各期的平均配置比例，平均配置收益得分以及配置期数占比
    def alloEvaluation_indus_all(self):
        '''
        配置期数占比：历史配置期数累计除以财报期数
        平均配置比例：统计历史上当配置该基金时，平均配置的比例
        平均配置收益得分：按照该行业历史曾有配置的各期配置权重进行加权计算配置得分
        '''
        if len(self.allfundHolding.columns) > 1:
            quarterList1 = self.quarterList1
            quarterList2 = self.quarterList2
            indusNetQuarter = self.indusNet.loc[quarterList1]
            indusNetQuarter.index = quarterList2
            indusRetQuarter = indusNetQuarter.pct_change()
            scoreMatrix = pd.DataFrame(index=indusRetQuarter.index, columns=indusRetQuarter.columns)
            for i in range(1, len(scoreMatrix)):
                tmpQuarter = scoreMatrix.index[i]
                ret = indusRetQuarter.iloc[i].sort_values(ascending=True)
                scoreMatrix.loc[tmpQuarter, list(ret.index)] = list(range(1, len(ret) + 1))
            allEvaluation = []
            weight = self.allDistribute
            for j in range(scoreMatrix.shape[1]):
                try:
                    industry = scoreMatrix.columns[j]
                    evaluation = pd.Series(index=['平均配置得分', '平均配置比例', '配置次数占比'], name=industry)
                    alloNum = len(weight.loc[industry].dropna()) / len(weight.columns)
                    alloRatio = weight.loc[industry].dropna().mean()
                    # 平均配置得分
                    weight_new = weight.iloc[:, 0:-1]
                    weight_new.columns = weight.columns[1:]  # 临时权重，列名与区间收益率的列对应
                    stdwei = weight_new.loc[industry].dropna() / (weight_new.loc[industry].dropna().sum())
                    alloScore = (stdwei * (scoreMatrix[industry])).sum()
                    evaluation[:] = [alloScore, alloRatio, alloNum]
                    allEvaluation.append(evaluation)
                except:
                    continue
            allEvaluation = pd.concat(allEvaluation, axis=1)
            allEvaluation = allEvaluation.dropna(axis=1)
            self.allEvaluation = allEvaluation
        else:
            self.allEvaluation = []

    # 生成结果
    def generateOutput(self):
        try:
            self.allDistribute.fillna(0, inplace=True)  # 缺失值填空0
            self.output = {'alloDistribute': self.allDistribute, 'alloScore': self.allScore.dropna(),
                           'alloEvaluation': self.allEvaluation}
        except:
            self.output = {'alloDistribute': [], 'alloScore': [], 'alloEvaluation': []}


# 基金经理行业配置能力
class industryAllocation_manager:
    def __init__(self, btParms, stockIndus, indusNet):
        self.manager = btParms['manager']
        self.symbol = btParms['symbol']
        self.stockIndus = stockIndus
        self.indusNet = indusNet
        self.genrOutput()

    # 获取基金经理的任职区间
    def getPeriod(self):
        managerPeriod = getData_fundManagerInfo(self.symbol)[self.manager]
        startDate = datetime.strftime(managerPeriod[0] + timedelta(90), '%Y%m%d')
        endDate = datetime.strftime(managerPeriod[1], '%Y%m%d')
        return {'symbol': self.symbol, 'startDate': startDate, 'endDate': endDate}

    # 调取基金行业配置能力类
    def genrOutput(self):
        managerId = getData_fundManagerId(self.manager, self.symbol)
        btParms = self.getPeriod()
        if (parse(btParms['endDate']) - parse(btParms['startDate'])).days < 60:
            self.output = {'managerId': managerId, 'alloDistribute': [], 'alloScore': [], 'alloEvaluation': []}
        else:
            eta = industryAllocation(btParms, self.stockIndus, self.indusNet)
            output = eta.output
            output.update({'managerId': managerId, 'manager': self.manager, 'symbol': self.symbol})
            self.output = output


if __name__ == '__main__':

    # 离线计算基金经理行业配置能力
    # 为提高运行速度，公共数据一次性提取，并作为参数传入要调用的类
    stockIndus, indusNet = getPublicDataAllocation()

    # 批量生成基金经理任职区间信息
    managerInfo = getData_fundManagerInfo_all()
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可
    '''

    # 批量生成基金经理行业配置能力
    for i in range(len(managerInfo)):
        btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
        print(i)
        try:
            test = industryAllocation_manager(btParms, stockIndus, indusNet)
            output = test.output
            scoreDF = output['alloScore']  # fof_fund_stock_industry
            # for i in stockIndus.index:
            # print(i, "====", stockIndus[i])
            # fof_fund_stock_industry
            # sWindCode = i  # 玩的股票代码
            # indsName = stockIndus[i]  # 行业名称?
            wCode = output['symbol']  # 基金代码
            for i, v in scoreDF.items():
            # for idx in scoreDF.index:
                _dt = i  #
                id_ = uuid_util.gen_uuid()  # objId
                sVal = v  # 配置占股票市值比
                lst = []
                lst.append(id_)
                lst.append(wCode)
                lst.append(_dt._short_repr.replace("-", ""))
                # lst.append(sWindCode)
                # lst.append(indsName)#?没有行业
                lst.append(sVal)
                lst.append("sys")
                lst.append(datetime.now())
                lst.append("sys")
                lst.append(datetime.now())

                ls = [transformFloatIfAvaliable4(i) for i in lst]
                sql = "INSERT INTO `fof`.`fof_fund_stock_industry`(`OBJECT_ID`, `J_WINDCODE`, `TRADE_DT`,   `STOCK_RATE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (  %s, %s,  %s, %s, %s, %s, %s, %s)"
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ls))
        except Exception as  e:
            output = {'managerId': managerInfo.loc[i, 'managerId'], 'symbol': managerInfo.loc[i, 'fund'],
                      'manager': managerInfo.loc[i, 'manager'],
                      'alloDistribute': [], 'alloScore': [], 'alloEvaluation': []}

    '''
    #基金行业配置能力
    btParms={'symbol':'003131.OF',
             'startDate':'20160927',
             'endDate':'20171107',
             }
    self=industryAllocation(btParms,stockIndus,indusNet)
    output=self.output
    

    #-->计算基金经理任职期以来的行业配置能力，输入参数为基金名称以及基金经理名称
    btParms={'symbol':'000577.OF','manager':'陈一峰'}
    self=industryAllocation_manager(btParms,stockIndus,indusNet)
    output=self.output
    print(output)
    
    btParms={'symbol':'270048.OF','manager':'张芊'}
    self=industryAllocation_manager(btParms,stockIndus,indusNet)
    output=self.output
    print(output)
    '''
