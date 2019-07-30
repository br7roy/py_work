# -*- coding: utf-8 -*-
"""
基金经理股票择时能力评价模型
类名：equityTimingAbility_manager
输入参数：btParms涵盖两个key，基金代码symbol以及基金经理manager
输出结果：output，字典格式，后续可能会根据需求加入其它
key1个为hisTiming,key2位根据输入的基金代码与基金经理名称返回的基金经理id
hisTiming各字段说明：
'startDate'-起始日期，'endDate'-结束日期，'marketRet'-市场涨跌幅，'initialPosition'-期初仓位
'endRealPosition'-期末实际仓位,'timingEval'-择时胜负评价，'timingContr'-择时贡献度
当output中的hisTiming返回为空DataFrame时，说明择时能力评价不适用于该基金，可不存入数据库
output中存储的还有winRatio和avgTimingContr两个字段，这两个字段目前设计的页面前端不需要展示
可以先不入库

本程序已写成批量更新形式，最终的结果保存在output_all中，将该结果存执fof数据库即可，
若alloScore为空，则结果无需存入数据库
请于每季结束后的第一个月的15日开始运行本程序(即基金季报发布)，按日更新，运行至该月末
如1季度结束后，于4月15日~4月30日每日更新该数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.parser import parse
from fof.algorithm.getData_sql import *
from util import uuid_util
from util.num_util import transformFloatIfAvaliable


class equityTimingAbility:
    def __init__(self, btParms):
        self.symbol = btParms['symbol']  # 基金代码
        self.startDate = btParms['startDate']  # 起始日期
        self.endDate = btParms['endDate']  # 结束日期
        self.marketIndex = '000906.SH'  # 宽基指数
        self.marketThreashold = 0.10  # 市场涨跌幅阈值
        self.positionThreashold = 0.10  # 仓位变动阈值

        # 加载函数,写成类的私有函数形式，避免前端调用时意外篡改
        self.__transformDataType()
        self.__getDataFromDb()
        self.__timingEval()
        self.__timingContr()
        self.__generateOutput()

    # 将前端拿到的json格式数据批量转换成该类中需要的数据格式
    def __transformDataType(self):
        try:
            self.startDate = datetime.strftime(parse(self.startDate), '%Y%m%d')
        except:
            self.startDate = datetime.strftime(self.startDate, '%Y%m%d')
        try:
            self.endDate = datetime.strftime(parse(self.endDate), '%Y%m%d')
        except:
            self.endDate = datetime.strftime(self.endDate, '%Y%m%d')

    # 从数据库获取模型中要用到的数据，此处以华宝金工团队自建的mongoddb数据库为例
    def __getDataFromDb(self):
        # 基准指数
        benchmark = getData_marketIndex(self.marketIndex, self.startDate, self.endDate)
        self.benchmark = benchmark
        # 权益持仓占比
        stockProportion = getData_fundHistoryData('stockProportion', self.symbol, self.startDate, self.endDate)
        self.stockProportion = stockProportion / 100
        if stockProportion.empty:
            stockProportion = pd.Series(0, index=stockProportion.index, name=self.symbol)
        else:
            stockProportion = stockProportion.fillna(0)

    # 择时结果评价
    def __timingEval(self):
        # 根据基金披露的权益持仓确立起始日期
        quarterList1 = getData_tradeDays(self.stockProportion.index[0] - timedelta(10),
                                         self.stockProportion.index[-1] + timedelta(10), '季')
        benchmark1 = self.benchmark.reindex(quarterList1)
        benchRet = benchmark1.pct_change()
        stockProportion1 = self.stockProportion
        stockProportion1.index = benchmark1.index
        stockProportion_real = stockProportion1.copy()  # 股票期末真实仓位
        timingEval = pd.Series(index=benchmark1.index, name='timingEval')
        posMean = stockProportion1.mean()
        posStd = stockProportion1.std()
        for i in range(1, len(benchmark1)):
            pt = stockProportion1[i - 1] * (1 + benchRet[i]) / (
                        stockProportion1[i - 1] * (1 + benchRet[i]) + 1 - stockProportion1[i - 1])
            stockProportion_real[i] = stockProportion1[i] - pt + stockProportion1[i - 1]
            if abs(benchRet[i]) > self.marketThreashold:
                if benchRet[i] > self.marketThreashold and stockProportion1[i] > posMean + posStd and stockProportion1[
                    i - 1] > posMean + posStd:
                    timingEval[i] = 1
                elif benchRet[i] > self.marketThreashold and stockProportion_real[i] - stockProportion1[
                    i - 1] > self.positionThreashold:
                    timingEval[i] = 1
                elif benchRet[i] < -self.marketThreashold and stockProportion1[i] < posMean - posStd and \
                        stockProportion1[i - 1] < posMean - posStd:
                    timingEval[i] = 1
                elif benchRet[i] < -self.marketThreashold and stockProportion_real[i] - stockProportion1[
                    i - 1] < -self.positionThreashold:
                    timingEval[i] = 1
                elif benchRet[i] > self.marketThreashold and stockProportion1[i] < posMean - posStd and \
                        stockProportion1[i - 1] < posMean - posStd:
                    timingEval[i] = -1
                elif benchRet[i] > self.marketThreashold and stockProportion_real[i] - stockProportion1[
                    i - 1] < -self.positionThreashold:
                    timingEval[i] = -1
                elif benchRet[i] < -self.marketThreashold and stockProportion1[i] > posMean + posStd and \
                        stockProportion1[i - 1] > posMean + posStd:
                    timingEval[i] = -1
                elif benchRet[i] < -self.marketThreashold and stockProportion_real[i] - stockProportion1[
                    i - 1] > self.positionThreashold:
                    timingEval[i] = -1
                else:
                    timingEval[i] = 0
            else:
                timingEval[i] = np.nan

        self.timingEval = timingEval
        self.sp = stockProportion1
        self.stockProportion_real = stockProportion_real  # 股票真实仓位
        self.benchmark1 = benchmark1  # 比较基准的季度价格序列
        self.benchRet = benchRet

    # 择时贡献率
    def __timingContr(self):
        benchRet = self.benchmark1.pct_change()
        timingContr = pd.Series(index=self.benchmark1.index, name='timingContr')
        for i in range(1, len(timingContr)):
            timingContr[i] = (self.sp[i] + self.sp[i - 1]) * benchRet[i] / 2
        self.timingContr = timingContr

    # 生成结果，json格式
    def __generateOutput(self):
        hisTiming = []
        for i in range(1, len(self.timingEval)):
            if not pd.isnull(self.timingEval[i]):
                tmp = {}
                t1 = self.timingEval.index[i - 1]
                t2 = self.timingEval.index[i]
                tmp['startDate'] = t1.strftime('%Y%m%d')
                tmp['endDate'] = t2.strftime('%Y%m%d')
                tmp['marketRet'] = self.benchRet[t2]
                tmp['initialPosition'] = self.sp.loc[t1]
                tmp['endRealPosition'] = self.stockProportion_real.loc[t2]
                tmp['timingEval'] = self.timingEval[i]
                tmp['timingContr'] = self.timingContr[i]
                hisTiming.append(tmp)

        hisTiming = pd.DataFrame(hisTiming, columns=['startDate', 'endDate', 'marketRet',
                                                     'initialPosition', 'endRealPosition', 'timingEval', 'timingContr'])
        hisTiming.dropna(inplace=True)
        if hisTiming.empty:
            hisTiming = pd.DataFrame()

        tmp = hisTiming['timingEval']
        if len(tmp) == 0:
            winRatio = np.nan
        else:
            if len(tmp[tmp != 0]) > 0:
                winRatio = len(tmp[tmp > 0]) / (len(tmp[tmp != 0]))
            else:
                winRatio = 0
        output = {'hisTiming': hisTiming, 'winRatio': winRatio, 'avgTimingContr': hisTiming['timingContr'].mean()}
        self.output = output


# 基金经理择时能力
class equityTimingAbility_manager:
    def __init__(self, btParms):
        self.manager = btParms['manager']
        self.symbol = btParms['symbol']
        self.genrOutput()

    # 获取基金经理的任职区间
    def getPeriod(self):
        managerPeriod = getData_fundManagerInfo(self.symbol)[self.manager]
        startDate = datetime.strftime(managerPeriod[0] + timedelta(95), '%Y%m%d')
        endDate = datetime.strftime(managerPeriod[1], '%Y%m%d')
        return {'symbol': self.symbol, 'startDate': startDate, 'endDate': endDate}

    # 调取基金择时类
    def genrOutput(self):
        managerId = getData_fundManagerId(self.manager, self.symbol)
        btParms_spec = self.getPeriod()
        if (parse(btParms_spec['endDate']) - parse(btParms_spec['startDate'])).days < 150:
            output = {'hisTiming': pd.DataFrame(), 'winRatio': np.nan, 'avgTimingContr': np.nan}
        else:
            eta = equityTimingAbility(btParms_spec)
            output = eta.output
            output = output
        output.update({'managerId': managerId, 'manager': self.manager, 'symbol': self.symbol})
        self.output = output


if __name__ == '__main__':

    # 批量生成基金经理任职区间信息
    '''
    首次存入数据库时需要全部运行，后续更新维护时只需更新在任基金经理信息即可
    '''
    managerInfo = getData_fundManagerInfo_all()

    # 批量生成基金经理行业配置能力
    output_all = []
    for i in range(len(managerInfo)):
        try:
            # if i < 10:
            btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
            print(i)
            test = equityTimingAbility_manager(btParms)
            output = test.output
            timing = output['hisTiming']
            lst = timing.values.tolist()
            for ls in lst:
                print(ls)
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
                ll.append("sys")
                ll.append(datetime.now())
                ll.append("sys")
                ll.append(datetime.now())
                sql = "INSERT INTO `fof`.`fof_fund_timing`(`OBJECT_ID`, `J_WINDCODE`, `MANAGER_ID`, `MANAGER_NAME`, `START_DATE`, `END_DATE`, `RISING`, `HOLDINGS_BEGIN`, `HOLDINGS_END`, `TIMING_RESULT`, `HOLDINGS_RATIO`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                from conf.mysqlops import *
                insert_one(MysqlConf.DB.fof, sql, tuple(ll))
        except Exception as e:
            print(e)
            output={'managerId':managerInfo.loc[i,'managerId'],'symbol':managerInfo.loc[i,'fund'],
                    'manager':managerInfo.loc[i,'manager'],
                    'hisTiming':pd.DataFrame(),'winRatio':np.nan,'avgTimingContr':np.nan}
            # output_all.append(output)
    # fof_fund_timing

    # print(output_all)

    '''
    #基金择时能力评价
    btParms={'symbol':'000001.OF',
             'startDate':'2014/02/26',
             'endDate':'2018/11/16',
             }
   
    self=equityTimingAbility(btParms)
    output1=self.output
    print(self.output)
    
    

    #基金经理择时能力评价
    btParms={'symbol':'000527.OF','manager':'史博'}
    self=equityTimingAbility_manager(btParms)
    output=self.output
    print(output)
    '''
