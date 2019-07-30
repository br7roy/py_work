# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.parser import parse

from HelloWorld.util.cusFundfunction import *
from . import *

# 基金单指标测试模板
'''
输出测试结果，及回测净值曲线

'''


# 输入变量均为单字符串或list字符串格式，便于前端开发
class generateFundFactor:
    def __init__(self, indexName, backCycle, testSample, startDate, endDate, rebalanceFrequency, tradeStatus,
                 existYears, scaleThreshold, benchMark='000906SH', groupingNumber='5',
                 commission_subscribe='0.001', commission_redeem='0.005',
                 marketIndex=None, otherPar=None):

        self.indexName = indexName  # 测评指标名称
        self.backCycle = backCycle  # 指标回看周期长度
        self.testSample = testSample  # 回测样本，为基金类型,str或list格式
        self.startDate = startDate  # 回测起始开始日期，字符串格式
        self.endDate = endDate  # 回测结束日期，字符串格式
        self.rebalanceFrequency = rebalanceFrequency  # 换仓频率，支持：month，quarter，semiyear，year以及基金季报披露日换仓，字符串
        self.benchMark = benchMark  # 指定比较基准，str格式，为基准名称
        self.groupingNumber = groupingNumber  # 分档测试档数,一般选取2,3,5,10
        self.commission_subscribe = commission_subscribe  # 基金申购费率
        self.commission_redeem = commission_redeem  # 基金赎回费率

        # --以下三个参数为回测样本清洗要设定的参数
        self.tradeStatus = tradeStatus  # "0"代表所有当天存续的标的，"1"代表剔除当天暂停大额申购及暂停申购标的，"2"代表剔除当天暂停申购标的
        self.existYears = existYears  # 基金存续年限
        self.scaleThreshold = scaleThreshold  # 基金规模阈值，单位为万元
        # 可选参数定
        self.marketIndex = marketIndex
        self.otherPar = otherPar

        # 加载函数，自动运行生成结果
        self.transformDataType()
        self.getDataFromDb()
        self.generateTestDate()
        self.generateFactor()
        self.generateFactorEvaluation()

        self.tradePlot()

    # 此处可以将从前端拿到的json格式数据批量转换成该类中需要的数据格式
    def transformDataType(self):
        # 转格式
        self.startDate = parse(self.startDate)
        self.endDate = parse(self.endDate)
        self.tradeStatus = eval(self.tradeStatus)
        self.existYears = eval(self.existYears)
        self.scaleThreshold = eval(self.scaleThreshold)
        self.backCycle = eval(self.backCycle)
        self.groupingNumber = eval(self.groupingNumber)
        self.commission_subscribe = eval(self.commission_subscribe)
        self.commission_redeem = eval(self.commission_redeem)

        if self.otherPar:
            self.otherPar = eval(self.otherPar)

    # 从数据库获取回测中要用到的数据，此处以华宝金工团队自建的mongoddb数据库为例
    def getDataFromDb(self):
        # 基金测试样本名称
        if type(self.testSample) == str:
            self.testSample = [self.testSample]
        fundSymbols = []
        for sample in self.testSample:
            tmp = getData_fundSymbols(sample)
            fundSymbols.extend(tmp)

            # 剔除非A类份额
        fundSymbols = cleanSymbols_notA(fundSymbols)
        # 基金每日状态数据
        fundStatus = getData_fundHistoryData('fundStatus', fundSymbols, self.startDate - timedelta(365 * 3),
                                             self.endDate)
        # 基金单位净值数据
        fundNav = getData_fundHistoryData('nav', fundSymbols, self.startDate - timedelta(365 * 3), self.endDate)
        # 基金复权净值数据
        fundAdjNav = getData_fundHistoryData('adjNav', fundSymbols, self.startDate - timedelta(365 * 3), self.endDate)
        # 基金份额数据
        fundShares_tmp = getData_fundHistoryData('fundShare', fundSymbols, self.startDate - timedelta(365 * 3),
                                                 self.endDate)
        fundShares_tmp = fundShares_tmp.resample("D").pad()
        fundShares = fundShares_tmp.reindex(fundNav.index)
        # 比较基准数据
        benchData = getData_marketIndex(self.benchMark, self.startDate - timedelta(365 * 3), self.endDate)
        # 提取评价指标需要输入的基金类数据
        indexInformation = self.setIndexInformation()
        inputDataType = indexInformation[self.indexName]['fundDataType']
        if type(inputDataType) == str:
            inputDataType = [inputDataType]

        i = -1
        for myData in inputDataType:
            i = i + 1
            tmp = getData_fundHistoryData(myData, fundSymbols, self.startDate - timedelta(365 * 3), self.endDate)
            if i == 0:
                fundData_0 = tmp
            elif i == 1:
                fundData_1 = tmp
            else:
                fundData_2 = tmp

        # 若指标需要输入市场基准数据，则提取
        marketIndexData = None
        if self.marketIndex:
            marketIndexData = getData_marketIndex(self.marketIndex, self.startDate - timedelta(365 * 3), self.endDate)

        # 仅保留数据全的基金
        if len(inputDataType) == 1:
            publicSymbols = list(set(fundNav.columns) & set(fundStatus.columns) & set(fundShares.columns)
                                 & set(fundData_0.columns))
            self.fundData_0 = fundData_0[publicSymbols]
            self.fundData_1 = fundData_0[publicSymbols]
            self.fundData_2 = fundData_0[publicSymbols]

        elif len(inputDataType) == 2:
            publicSymbols = list(set(fundNav.columns) & set(fundStatus.columns) & set(fundShares.columns)
                                 & set(fundData_0.columns) & set(fundData_1.columns))
            self.fundData_0 = fundData_0[publicSymbols]
            self.fundData_1 = fundData_1[publicSymbols]
            self.fundData_2 = fundData_0[publicSymbols]

        else:
            publicSymbols = list(set(fundNav.columns) & set(fundStatus.columns) & set(fundShares.columns)
                                 & set(fundData_0.columns) & set(fundData_1.columns) & set(fundData_2.columns))
            self.fundData_0 = fundData_0[publicSymbols]
            self.fundData_1 = fundData_1[publicSymbols]
            self.fundData_2 = fundData_2[publicSymbols]

        self.fundNav = fundNav[publicSymbols]
        self.fundAdjNav = fundAdjNav[publicSymbols]
        self.fundStatus = fundStatus[publicSymbols]
        self.fundShares = fundShares[publicSymbols]
        self.fundData = [self.fundData_0, self.fundData_1, self.fundData_2]
        # 比较基准数据
        self.benchData = benchData
        # 市场指数数据
        self.marketIndexData = marketIndexData

        # 生成测试日期序列

    def generateTestDate(self):
        tdays = list(self.fundNav[self.startDate:].index)  # 生成交易日期序列
        rebalanceDays = []
        if self.rebalanceFrequency == 'month':
            for i in range(1, len(tdays)):
                if tdays[i].month != tdays[i - 1].month:
                    rebalanceDays.append(tdays[i - 1])
        elif self.rebalanceFrequency == 'quarter':
            for i in range(1, len(tdays)):
                if tdays[i].month != tdays[i - 1].month and tdays[i - 1].month % 3 == 0:
                    rebalanceDays.append(tdays[i - 1])
        elif self.rebalanceFrequency == 'semiyear':
            for i in range(1, len(tdays)):
                if tdays[i].month != tdays[i - 1].month and tdays[i - 1].month % 6 == 0:
                    rebalanceDays.append(tdays[i - 1])
        elif self.rebalanceFrequency == 'year':
            for i in range(1, len(tdays)):
                if tdays[i].month != tdays[i - 1].month and tdays[i - 1].month % 12 == 0:
                    rebalanceDays.append(tdays[i - 1])
        elif self.rebalanceFrequency == 'fundQuarter':
            for i in range(1, len(tdays)):
                if tdays[i].month not in [1, 4, 7, 10] and tdays[i - 1].month in [1, 4, 7, 10]:
                    rebalanceDays.append(tdays[i - 1])

        # 删除不在开始结束日期区间内的日期
        for i in range(len(rebalanceDays) - 1, -1, -1):
            diffTime0 = rebalanceDays[i] - self.startDate
            diffTime1 = rebalanceDays[i] - self.endDate
            if diffTime0.days < 0 or diffTime1.days > 0:
                rebalanceDays.pop(i)
        self.rebalanceDays = rebalanceDays  # 测试日期
        self.tdays = tdays[tdays.index(rebalanceDays[0]):]  # 交易日期
        print('因子测评日期序列生成完毕')

    def generateFactor(self):
        # 把计算指标过程中会用到的各项数据进行去类化，以使得代码简洁
        rebalanceDays = self.rebalanceDays
        tdays = self.tdays
        fundNav = self.fundNav
        fundAdjNav = self.fundAdjNav
        fundStatus = self.fundStatus
        fundStatus.fillna('未成立', inplace=True)
        fundShares = self.fundShares
        # -----生成指标
        # 按rebalanceDays循环，数据存于factorValue矩阵中
        factorValue = pd.DataFrame(np.nan, index=rebalanceDays, columns=fundNav.columns,
                                   dtype=float)  # 存放样本基金在每个rebalanceDays的指标值的矩阵
        for i in range(len(factorValue)):
            executeDate = factorValue.index[i]
            executeDateIndex = list(fundNav.index).index(executeDate)  # executeDate 在交易日序列中所处的位置
            invalidSample = []  # 记录无效样本
            fundName = list(self.fundNav.columns)
            # 生成本期无效样本
            for symbol in fundName:
                # 上市时间小于n,利用nan类型数据的特殊性质
                if pd.isna(fundAdjNav.loc[fundAdjNav.index[executeDateIndex - max(int(self.existYears * 244),
                                                                                  self.backCycle)], symbol]):
                    invalidSample.append(symbol)
                    # 规模小于阈值
                elif fundShares.loc[factorValue.index[i], symbol] * fundNav.loc[
                    factorValue.index[i], symbol] < self.scaleThreshold:
                    invalidSample.append(symbol)
                # 当天暂停申购
                else:
                    if self.tradeStatus == 1 and '开放申购' not in fundStatus.loc[factorValue.index[i], symbol]:
                        invalidSample.append(symbol)
                    elif self.tradeStatus == 2 and '开放申购' not in fundStatus.loc[factorValue.index[i], symbol] \
                            and '暂停大额申购' not in fundStatus.loc[factorValue.index[i], symbol]:
                        invalidSample.append(symbol)
                    elif self.tradeStatus == 0 and '申购' not in fundStatus.loc[factorValue.index[i], symbol]:
                        invalidSample.append(symbol)

            # 重新对各期基金的因子值进行赋值
            for symbol in fundName:
                if symbol not in invalidSample:
                    factorValue.loc[executeDate, symbol] = self.performanceEval(symbol, executeDate)
        self.factorValue = factorValue
        print('因子指标值生成完毕')

    def generateFactorEvaluation(self):
        factorValue = self.factorValue
        icSeries = pd.Series(index=factorValue.index[1:])

        # ---计算ic类指标
        # 生成IC序列
        print('开始计算IC类指标')
        for i in range(1, len(factorValue)):
            fundReturn = self.fundAdjNav.loc[factorValue.index[i]] / self.fundAdjNav.loc[factorValue.index[i - 1]] - 1
            tmp = pd.concat([factorValue.iloc[i - 1], fundReturn], axis=1)
            tmp = tmp.dropna()
            icSeries[i - 1] = tmp.corr(method='spearman').iloc[0, 1]

        avgIc = icSeries.mean()  # 平均IC
        avgAbsIc = icSeries.abs().mean()  # ic绝对值的平均值
        avgPositiveIc = icSeries[icSeries > 0].mean()  # ic正值的平均值
        positiveIcRatio = len(icSeries[icSeries > 0]) / len(icSeries)  # IC为正的比率
        ir = icSeries.mean() / icSeries.std()  # ir
        tStatistic = ir * np.sqrt(len(icSeries) - 1)

        # --计算分档排序类指标
        print('开始计算分档测评指标')
        gradingReturn = pd.DataFrame(index=factorValue.index[1:],
                                     columns=list(range(self.groupingNumber)))  # 存放分档收益率统计的矩阵
        firstGradingSymbolArray = {}.fromkeys(list(factorValue.index[1:]))  # 存放每期筛选出来的第一档基金的代码，dictionary格式
        for i in range(1, len(factorValue)):  # 按基金筛选日期循环
            # 根据i-1期的指标值，划分为groupingNumber档
            tmpFactorValue = copy.deepcopy(factorValue.iloc[i - 1].dropna())  # 临时存放基金测评指标的某行值,采用拷贝模式，避免改动源数据
            # 生成分档阈值
            quantileSeries = [1 - x / 100 for x in
                              range(int(100 / self.groupingNumber), 101, int(100 / self.groupingNumber))]
            quantileValue = []  # 分档阈值
            for j in range(len(quantileSeries)):
                quantileValue.append(tmpFactorValue.quantile(quantileSeries[j]))

            gradingSymbol = []  # 当期分档基金代码

            # 采用循环对基金进行分档
            j = 0
            while 1:
                if j == 0:
                    tmpSymbol = list(tmpFactorValue[tmpFactorValue >= quantileValue[j]].index)
                    gradingSymbol.append(tmpSymbol)
                    tmpFactorValue.drop(tmpSymbol, inplace=True)  # 删除已分组的基金
                else:
                    tmpSymbol = list(tmpFactorValue[tmpFactorValue >= quantileValue[j]].index)
                    tmpSymbol = list(set(tmpSymbol) - set(gradingSymbol[j - 1]))
                    gradingSymbol.append(tmpSymbol)
                    tmpFactorValue.drop(tmpSymbol, inplace=True)  # 删除已分组的基金
                j = j + 1
                if j == len(quantileValue):
                    break

            # 计算每档下期收益率
            tmp = []
            for j in range(len(gradingSymbol)):
                fundReturn = self.fundAdjNav.loc[factorValue.index[i], gradingSymbol[j]] / \
                             self.fundAdjNav.loc[factorValue.index[i - 1], gradingSymbol[j]] - 1
                tmp.append(fundReturn.mean())  # 计算分档收益率
            gradingReturn.iloc[i - 1] = tmp  # 分档收益率
            firstGradingSymbolArray[factorValue.index[i]] = gradingSymbol[0]  # 把每期位于排名第1档的基金代码保存

        # -->生成第一档组合的累积净值序列
        # 生成历史持仓
        hisWeights = pd.DataFrame()
        for key in firstGradingSymbolArray:
            rowWeights = pd.DataFrame(1 / len(firstGradingSymbolArray[key]), index=[key],
                                      columns=firstGradingSymbolArray[key])
            hisWeights = pd.concat([hisWeights, rowWeights], sort=True)
        # 生成历史回测净值
        firstGradingNetvalue = portfolioBackTest(self.fundAdjNav[hisWeights.columns], hisWeights,
                                                 (self.commission_subscribe + self.commission_redeem) / 2, 0.10)

        # --生成分档测评指标
        # 多空组合平均超额收益率：第一档减最后一档
        # 计算历次换手率,简便起见，仅计算第一档组合的换手率
        fundTurnOverRate = pd.Series(index=factorValue.index[1:])  # 换手率数值
        for i in range(len(firstGradingSymbolArray)):
            if i == 0:
                fundTurnOverRate[i] = 1
            else:
                tmp = len(set(firstGradingSymbolArray[factorValue.index[i]]) - set(
                    firstGradingSymbolArray[factorValue.index[i + 1]])) / \
                      len(firstGradingSymbolArray[factorValue.index[i]])
                fundTurnOverRate[i] = tmp

                # 计算分档累积收益率,考虑换手率与交易费用
        gradingCumReturn = []
        for j in range(len(gradingReturn.columns)):
            cumReturn = 1
            for i in range(len(gradingReturn)):
                cumReturn = cumReturn * (
                            1 + gradingReturn.iloc[i, j] - (self.commission_subscribe + self.commission_redeem) *
                            fundTurnOverRate[i])
            gradingCumReturn.append(cumReturn - 1)

            # 计算指标：平均换手率
        avgTurnOverRate = fundTurnOverRate[1:].mean()
        # 计算指标：平均换手率,中位数统计
        medianTurnOverRate = fundTurnOverRate[1:].median()
        # 计算指标：多空组合累积收益率差
        winAndLossExtraCumReturn = gradingCumReturn[0] - gradingCumReturn[-1]
        # 计算指标：相较基准超额收益率
        extraCumReturn = firstGradingNetvalue[-1] - self.benchData[firstGradingNetvalue.index[-1]] / self.benchData[
            firstGradingNetvalue.index[0]]
        # 计算指标：分档累积收益率秩IC
        gradingRankIC = pd.DataFrame([range(self.groupingNumber), gradingCumReturn]).T.corr(method='spearman').iloc[
                            0, 1] * -1
        # 计算年化区间
        yearlength = (firstGradingNetvalue.index[-1].year - firstGradingNetvalue.index[0].year) + \
                     (firstGradingNetvalue.index[-1].month - firstGradingNetvalue.index[0].month) / 12
        # 计算指标：多空组合年化累积收益率差
        annualWinAndLossECR = (1 + winAndLossExtraCumReturn) ** (1 / yearlength) - 1
        # 计算指标：相较基准年化超额收益率
        annualECR = (1 + extraCumReturn) ** (1 / yearlength) - 1

        # 输出测评结果
        self.fundFactorEvaluation = pd.Series(
            [avgIc, avgAbsIc, avgPositiveIc, positiveIcRatio, ir, tStatistic, gradingRankIC, avgTurnOverRate,
             medianTurnOverRate, extraCumReturn, winAndLossExtraCumReturn, annualECR, annualWinAndLossECR],
            index=['avgIc', 'avgAbsIc', 'avgPositiveIc', 'positiveIcRatio', 'ir', 'tStatistic', 'gradingRankIC',
                   'avgTurnOverRate', 'medianTurnOverRate', 'excessCumReturn_benchMark', 'excessCumReturn_winAndLoss',
                   'excessAnnualReturn_benchMark', 'excessAnnualReturn_winAndLoss'],
            name=self.indexName)
        self.firstGradingSymbolArray = firstGradingSymbolArray
        self.gradingReturn = gradingReturn
        self.firstGradingNetvalue = firstGradingNetvalue
        self.fundTurnOverRate = fundTurnOverRate
        print('指标测试完毕,Congratulations!')

    def tradePlot(self):
        firstGradingNetvalue = self.firstGradingNetvalue
        firstGradingNetvalue.name = self.indexName
        # 生成基准指数净值序列
        benchMarkNetvalue = pd.Series(index=firstGradingNetvalue.index, name=self.benchMark, dtype=float)
        benchMarkNetvalue = self.benchData[firstGradingNetvalue.index].copy()
        benchMarkNetvalue = benchMarkNetvalue / benchMarkNetvalue[0]
        data_plot = pd.concat([firstGradingNetvalue, benchMarkNetvalue], axis=1)

        plt.close('all')
        from matplotlib.font_manager import FontProperties
        font = FontProperties(
            fname=r"C:\Windows\WinSxS\amd64_microsoft-windows-font-truetype-simsun_31bf3856ad364e35_10.0.17134.1_none_e089ab61d8d9374e\simsun.ttc",
            size=14)  # 设定数据格式
        # font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=14) #设定数据格式
        fig1 = plt.figure(facecolor=(1, 1, 1))
        ax1 = fig1.add_subplot(111)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('netvalue')
        dd = data_plot.plot(ax=ax1, grid=1)
        print(dd)
        plt.show(dd)
        # plt.show()
        plt.legend(prop=font, loc='best')

    def setIndexInformation(self):
        indexInformation = {'年化收益率': {'function': 'annualReturn', 'fundDataType': 'adjNav'},
                            '夏普比率': {'function': 'annualReturn', 'fundDataType': 'adjNav'},
                            '股票仓位波动率': {'function': 'stockProportionVol', 'fundDataType': 'stockProportion'},
                            '贝塔': {'function': 'beta', 'fundDataType': 'adjNav'},
                            }
        return indexInformation

    # 整合成一个函数
    def performanceEval(self, symbol, executeDate):
        if self.indexName == '年化收益率':
            data = self.fundData[0][symbol]
            cycle = self.backCycle
            return annualReturn(data, cycle, executeDate)
        elif self.indexName == '夏普比率':
            data = self.fundData[0][symbol]
            cycle = self.backCycle
            risklessReturn = self.otherPar[0]
            return sharpe(data, cycle, risklessReturn, executeDate)
        elif self.indexName == '波动率':
            data = self.fundData[0][symbol]
            cycle = self.backCycle
            halfLifePeriodParam = self.otherPar[0]
            return halfDecayStd(data, cycle, halfLifePeriodParam, executeDate)
        elif self.indexName == '最大回撤':
            cycle = self.backCycle
            return maxdown(data, cycle, executeDate)
        elif self.indexName == '卡玛比率':
            cycle = self.backCycle
            return calmar(data, cycle, executeDate)
        elif self.indexName == '股票仓位波动率':
            cycle = self.backCycle
            return calmar(data, cycle, executeDate)
        elif self.indexName == '贝塔':
            data = self.fundData[0][symbol]
            cycle = self.backCycle
            marketIndexData = self.marketIndexData
            return beta(data, cycle, marketIndexData, executeDate)


if __name__ == '__main__':
    import time

    # 记录起始时间
    start_time = time.time()
    # 生成因子值
    self = generateFundFactor('贝塔', '120', '普通股票型基金', '2014/1/1', '2018/12/31', 'fundQuarter', '2', '1', '5000',
                              '000906SH', marketIndex='000300SH')
    factorValue = self.factorValue
    fundFactorEvaluation = self.fundFactorEvaluation
    firstGradingNetvalue = self.firstGradingNetvalue
    print(fundFactorEvaluation)
    # 计算时间差值
    seconds, minutes, hours = int(time.time() - start_time), 0, 0
    # 可视化打印
    hours = seconds // 3600
    minutes = (seconds - hours * 3600) // 60
    seconds = seconds - hours * 3600 - minutes * 60
    print("\n  Complete time cost {:>02d}:{:>02d}:{:>02d}".format(hours, minutes, seconds))
