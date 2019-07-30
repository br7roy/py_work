# -*- coding: utf-8 -*-
"""
基金单指标排序打分模块
批量生产各类指标不同周期下的指标值、排名与打分
其中，任职以来、成立以来指标更新较慢，这两个指标可以周的频率进行更新
其余指标于每日晚上10点之后更新

"""
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
import copy
from datetime import datetime, timedelta
from dateutil.parser import parse
from fof.algorithm.perEvalFunction import *
from fof.algorithm.getData_sql import *


# 综合打分函数
def compScore(btParms):
    '''
    factorScores,各个指标打分结果，list格式，list中每个子元素为json格式
    factorWeights：各指标权重，list格式，list中各子元素为str格式
    '''
    factorScores = btParms['factorScores']
    factorScores = [pd.Series(m).astype(float) for m in factorScores]
    factorWeights = [eval(m) for m in btParms['factorWeights']]
    tmp = 0
    for j in range(len(factorScores)):
        tmp1 = factorScores[j] * factorWeights[j]
        tmp = tmp + tmp1
    tmp.name = 'fundScore'
    tmp.dropna(inplace=True)
    tmp = tmp.astype(float).to_dict()
    return tmp[0]


# 一次性获取全部基金2002年以来的复权净值数据
def getPublicData(dataType=None):
    fundSymbols = getData_fundSymbols(dataType)
    fundAdjNav = getData_fundHistoryData('adjNav', fundSymbols, '2002/1/1', datetime.today())
    # 删除数据严重缺失的交易日，避免数据更新频率不一致导致模块运行失败
    while 1:
        length = len(fundAdjNav)
        for col in fundAdjNav.index[-30:]:
            if len(fundAdjNav.loc[col].dropna()) / len(fundAdjNav.loc[col]) < 0.90:
                fundAdjNav.drop(col, inplace=True)
        if len(fundAdjNav) == length:
            break
    fundAdjNav.fillna(method='ffill', inplace=True)
    return fundAdjNav


# 单一基金标的单评价指标打分类模块
class indexScore_fund:
    def __init__(self, btParms, fundAdjNav, updateMode='auto', indexType='stockIndex'):
        self.indexName = btParms['indexName']  # 指标名称
        self.symbol = btParms['symbol']
        self.cycle = btParms['cycle']  # 指标回看周期长度,当为数字时以年为单位
        self.sample = btParms['sample']  # 打分排序样本，输入值为一级，二级，或自定义指定基金标的池
        self.marketIndex = btParms['marketIndex']  # 市场指数，默认为''
        self.otherPar = btParms['otherPar']  # 其他需要指定的参数,字符串或list格式，默认为''
        # 其他参数，后台配置
        self.fundAdjNav = fundAdjNav  # 导入所有基金的历史净值数据
        self.updateMode = updateMode  # 更新模型，可选参数为,'auto','one','batch',默认为'atuo',根据cycle值选择返回批量还是单一值
        self.indexType = indexType  # marketIndex类型，用于控制调取不同的sql函数

        # 加载函数
        try:
            self.transformDataType()
            self.genrPeriod()
            self.getDataFromDb()
            self.genrFactorValue()
            self.genrFactorScore()
            self.genrOutput()
        except:
            output_1 = {'factorValue': np.nan, 'factorScore': np.nan, 'factorRank': np.nan}
            output_1.update(
                {'rankMode': self.sample, 'symbol': self.symbol, 'cycle': self.cycle, 'indexName': self.indexName})
            self.output = output_1

            output_2 = {'factorValue': '', 'factorScore': '', 'factorRank': ''}
            output_2.update(
                {'rankMode': self.sample, 'symbol': self.symbol, 'cycle': self.cycle, 'indexName': self.indexName})
            self.output_json = output_2

    # 此处可以将从前端拿到的json格式数据批量转换成该类中需要的数据格式
    def transformDataType(self):

        # 生成基金类型与基金标的池
        if self.sample == '一级':
            fundInfo = getData_fundInformation(self.symbol)
            # 避免查不到数据报错
            if len(fundInfo) == 0:
                fundClass = '混合型基金'
            else:
                fundClass = fundInfo['FUND_INVESTTYPE'][0]
            self.fundSymbols = getData_fundSymbols(fundClass, classify='windFirst', status=1)  # 基金样本

        elif self.sample == '二级':
            fundInfo = getData_fundInformation(self.symbol, 'windSecond')
            if len(fundInfo) == 0:
                fundClass = '灵活配置型基金'
            else:
                fundClass = fundInfo[self.symbol]
            self.fundSymbols = getData_fundSymbols(fundClass, classify='windSecond', status=1)  # 基金样本

        # 若输入的marketIndex为空，则采用默认方法生成marketIndex与indexType
        if not self.marketIndex:
            if self.sample == '一级':
                indexMap = getIndexMap(classify='windFirst')
            else:
                indexMap = getIndexMap(classify='windSecond')
            try:
                self.marketIndex = indexMap[fundClass]['code']
                self.indexType = indexMap[fundClass]['type']
            except:
                self.marketIndex = indexMap[fundClass + '基金']['code']
                self.indexType = indexMap[fundClass + '基金']['type']

        # 设置otherPar
        if not self.otherPar:
            self.otherPar = [0.035]
        else:
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
            if self.cycle == '成立以来':
                fundInfo = getData_fundInformation(self.symbol)
                startDate = fundInfo.loc[self.symbol, 'FUND_SETUPDATE']
                self.startDate = datetime.strftime(startDate, '%Y%m%d')
            elif self.cycle == '任职以来':
                managerInfo = getData_fundManagerInfo(self.symbol)
                tmp = []
                for key in managerInfo.keys():
                    if (managerInfo[key][-1] - datetime.today()).days >= -1:  # 避免更新数据时跳过0点时报错
                        tmp.append(managerInfo[key])
                # 如果是多基金经理管理，则取最远的日期作为startDate
                if len(tmp) > 1:
                    tmp1 = [m[0] for m in tmp]
                    tmp1.sort()
                    self.startDate = tmp1[0]
                else:
                    self.startDate = tmp[0][0]
                self.startDate = datetime.strftime(self.startDate + timedelta(90), '%Y%m%d')  # 剔除3个月建仓期
            elif self.cycle == '今年以来':
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
        # 基金测试样本代码列表，支持1级分类，2级分类以及自定义样本
        if self.sample in ['一级', '二级']:
            fundSymbols = self.fundSymbols
        else:
            fundSymbols = self.sample

            # 剔除复权净值数据缺失样本
        fundSymbols = list(set(fundSymbols).intersection(set(self.fundAdjNav.columns)))

        # 提取评价指标需要输入的基金类数据
        indexInformation = setIndexInformation()
        inputDataType = indexInformation[self.indexName]['fundDataType']
        if type(inputDataType) == str:
            inputDataType = [inputDataType]
        i = -1
        for myData in inputDataType:
            i = i + 1
            if myData == 'adjNav':
                tmp = self.fundAdjNav.loc[self.startDate:self.endDate, fundSymbols]
                # 剔除无效数据（净值全部相等数据，采用std判断,或全部为NaN数据）
                tmp1 = tmp.std()
                tmp.drop(tmp1[tmp1 == 0].index, axis=1, inplace=True)
                tmp.dropna(axis=1, how='all', inplace=True)
                # 填充最后一行空值，避免由于该基金净值暂时尚未披露引致的指标计算值为nan
                tmp2 = tmp.copy()
                tmp2.fillna(method='ffill', inplace=True)
                tmp.iloc[-1] = tmp2.iloc[-1]

            else:
                tmp = getData_fundHistoryData(myData, fundSymbols, self.startDate, self.endDate)
            if i == 0:
                fundData_0 = tmp
            elif i == 1:
                fundData_1 = tmp
            else:
                fundData_2 = tmp

        # 若指标需要输入市场基准数据，则提取
        if self.indexType == 'stockIndex':
            marketIndexData = getData_marketIndex(self.marketIndex, self.startDate, fundData_0.index[-1])
        elif self.indexType == 'bondIndex':
            marketIndexData = getData_bondIndex(self.marketIndex, self.startDate, fundData_0.index[-1])
        elif self.indexType == 'fundIndex':
            marketIndexData = getData_fundIndex(self.marketIndex, self.startDate, fundData_0.index[-1])

            # 统一处理基金数据
        if len(inputDataType) == 1:
            self.fundData_0 = fundData_0
            self.fundData_1 = fundData_0
            self.fundData_2 = fundData_0

        elif len(inputDataType) == 2:
            self.fundData_0 = fundData_0
            self.fundData_1 = fundData_1
            self.fundData_2 = fundData_0
        else:
            self.fundData_0 = fundData_0
            self.fundData_1 = fundData_1
            self.fundData_2 = fundData_2

        self.fundData = [self.fundData_0, self.fundData_1, self.fundData_2]
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
        factorValue.dropna(inplace=True)  # 剔除nan值
        self.factorValue = factorValue

    def genrFactorScore(self):
        # 根据指标排序模式，生成打分
        indexInformation = setIndexInformation()
        sortMode = indexInformation[self.indexName]['sortMode']
        if sortMode == 'descend':
            self.factorScore = self.factorValue.rank(ascending=True, pct=True) * 100
        else:
            self.factorScore = self.factorValue.rank(ascending=False, pct=True) * 100
        self.factorRank = pd.Series(range(1, len(self.factorScore) + 1),
                                    index=self.factorScore.sort_values(ascending=False).index, name=self.indexName)

    def genrOutput(self):

        # python格式结果
        output_batch = {'factorValue': self.factorValue, 'factorScore': self.factorScore, 'factorRank': self.factorRank,
                        'sampleCounts': len(self.factorValue)}
        output_batch.update({'rankMode': self.sample, 'cycle': self.cycle, 'indexName': self.indexName})
        factorValue = self.factorValue.reindex([self.symbol])[0]
        factorScore = self.factorScore.reindex([self.symbol])[0]
        factorRank = self.factorRank.reindex([self.symbol])[0]
        output_one = {'factorValue': factorValue, 'factorScore': factorScore, 'factorRank': factorRank,
                      'sampleCounts': len(self.factorValue)}
        output_one.update(
            {'rankMode': self.sample, 'symbol': self.symbol, 'cycle': self.cycle, 'indexName': self.indexName})

        output_batch_python = copy.deepcopy(output_batch)
        output_one_python = copy.deepcopy(output_one)

        if self.updateMode == 'auto':
            if np.sum([m in self.cycle for m in ['成立以来', '任职以来', ',']]) > 0:
                self.output = output_one_python
            else:
                self.output = output_batch_python
        elif self.updateMode == 'one':
            self.output = output_one_python
        else:
            self.output = output_batch_python

        # 结果转成json，便于前端调用
        output_batch['factorValue'] = output_batch['factorValue'].astype(str).to_dict()
        output_batch['factorScore'] = output_batch['factorScore'].astype(str).to_dict()
        output_batch['factorRank'] = output_batch['factorRank'].astype(str).to_dict()

        output_one['factorValue'] = '' if pd.isnull(output_one['factorValue']) else str(output_one['factorValue'])
        output_one['factorScore'] = '' if pd.isnull(output_one['factorScore']) else str(output_one['factorScore'])
        output_one['factorRank'] = '' if pd.isnull(output_one['factorRank']) else str(output_one['factorRank'])

        if self.updateMode == 'auto':
            if np.sum([m in self.cycle for m in ['成立以来', '任职以来', ',']]) > 0:
                self.output_json = output_one
            else:
                self.output_json = output_batch
        elif self.updateMode == 'one':
            self.output_json = output_one
        else:
            self.output_json = output_batch


if __name__ == '__main__':

    '''以下语句设定为模块级全局变量，仅需运行一次'''
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    # 基金一级分类
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp

    # 基金二级分类
    fundClass_2 = pd.Series('灵活配置型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols, 'windSecond')
    fundClass_2[fundClass_tmp.index] = fundClass_tmp

    # --以下程序运行时，更改indexName
    indexName = '夏普比率'  # 依次更换指标,波动率指标需要另行设定otherPar

    # cycleList=['3/12','6/12','1','2','3','5','去年','前年','今年以来','任职以来','成立以来']
    cycleList = ['3/12', '6/12']
    creatVar = locals()
    for cycle in cycleList:
        print(cycle)
        output_all = []
        # 任职以来，成立以来这两个cycle设定，output每次只能产生一个基金，需要按基金标的进行循环计算
        if cycle in ['任职以来', '成立以来']:
            for symbol in fundSymbols:
                btParms = {'indexName': indexName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级', 'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                output = self.output
                output_all.append(output)

        # 其他cycle均支持批量计算，同一类标的仅计算一次即可
        else:
            updatedType = []
            for symbol in fundSymbols:
                btParms = {'indexName': indexName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级', 'marketIndex': '',
                           'otherPar': ''}

                # 基金分类数据有缺失，为避免报错，缺失数据自动补全
                if btParms['sample'] == '一级':
                    fundClass = fundClass_1[symbol]
                elif btParms['sample'] == '二级':
                    fundClass = fundClass_2[symbol]

                # 同类基金仅更新一次
                if fundClass not in updatedType:
                    self = indexScore_fund(btParms, fundAdjNav, 'auto')
                    output = self.output
                    output_all.append(output)
                    updatedType.append(fundClass)
        creatVar['output_all_' + cycle] = output_all

    '''
    btParms={'indexName':'夏普比率','cycle':'6/12','symbol':'000001.OF','sample':'一级','marketIndex':'',
             'otherPar':''}
    self=indexScore_fund(btParms,fundAdjNav,'auto')
    output=self.output
    output_all.append(output)
    '''





