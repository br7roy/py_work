# -*- coding: utf-8 -*-
"""
基金经理股票筛选能力
输出结果存放于类的output属性中，对应于基金经理选股能力前端要输出的模型原型
其中compareReturnIndustry为行业内选股收益与行业指数收益对比
excessReturnIndustry为基金经理任职期以来所投行业各期平均超额收益率，仅输出基金经理29个中信一级
行业中基金经理曾投过的行业
excessReturnQuarter为基金经理任职期以来各期选股超额收益率
mainStockReturn为基金经理历史所有个股收益统计

本程序已写成批量更新形式，最终的结果保存在output_all中，将该结果存执fof数据库即可，
若mainStockReturn为空，则结果无需存入数据库
请于每季结束后的第一个月的15日开始运行本程序，按日更新，运行至该月末
如1季度结束后，于4月15日~4月30日每日更新该数据

"""

from fof.algorithm.getData_sql import *

# 一次性获取公共数据


# 一次性获取公共数据
def publicData_stockAndIndustry():
    stockSymbol = getData_stockConstitue('aStock')
    info = getData_stockInformation(stockSymbol)
    stockIndus = pd.Series(info)  # 全部A股所属行业

    # 行业指数
    indusCodeList = list(set(stockIndus.dropna()))
    indusNet = []
    indusCodes = industryMap('CI')
    for name in indusCodeList:
        indusCode = indusCodes[name]
        tmp = getData_marketIndex(indusCode, '2002/1/1', datetime.today())
        indusNet.append(tmp)
    indusNet = pd.concat(indusNet, axis=1, sort=True)
    indusNet.fillna(method='ffill', inplace=True)  # 填充nan值，避免报错
    indusNet.columns = indusCodeList

    # 计算季度行业指数与股票收益率
    quarterList = getData_tradeDays('2002/1/1', datetime.today(), '季')
    quarterList_2 = pd.date_range('2002/1/1', datetime.today(), freq='Q')
    indusRet = indusNet.reindex(quarterList).pct_change()
    stockData = getData_stockHistoryData('close_B', list(stockIndus.index), '2002/1/1', datetime.today(), '季')
    stockRet = stockData.reindex(quarterList).pct_change()
    indusRet.index = quarterList_2
    stockRet.index = quarterList_2

    # 剔除缺失行业分类或收益率的标的
    publicSymbols = list(set(stockIndus.index) & set(stockRet.columns))
    stockIndus = stockIndus.reindex(publicSymbols)
    stockRet = stockRet.reindex(publicSymbols, axis=1)

    # 计算各行业分季度个股收益率分位数
    crIndus = {}
    for indusCode in indusCodeList:
        tmp = []
        for i in range(1, len(quarterList_2)):
            tmp.append(indusConstitueReturn(stockIndus, stockRet, indusCode, quarterList_2[i]))
        tmp = pd.concat(tmp, axis=1, sort=True)
        crIndus[indusCode] = tmp
    return stockIndus, stockRet, indusRet, crIndus


def indusConstitueReturn(stockIndus, stockRet, indusCode, execDate):
    quantileRet = pd.Series(index=['25分位数', '50分位数', '75分位数'], name=execDate)
    stockList = list(stockIndus[stockIndus == indusCode].index)
    ret = stockRet.loc[execDate, stockList]
    r1 = ret.quantile(0.25)
    r2 = ret.quantile(0.50)
    r3 = ret.quantile(0.75)
    quantileRet[:] = [r1, r2, r3]
    return quantileRet


class stockPicking:
    def __init__(self, btParms, stockIndus, stockRet, indusRet, crIndus):
        self.symbol = btParms['symbol']  # 基金代码
        self.startDate = btParms['startDate']  # 起始日期
        self.endDate = btParms['endDate']  # 结束日期
        self.stockIndus = stockIndus
        self.stockRet = stockRet
        self.indusRet = indusRet
        self.crIndus = crIndus

        # 加载函数
        self.transformDataType()
        self.getDataFromDb()
        self.excessReturn_quarter()
        self.excessReturn_industry()
        self.compareReturn_industry()
        self.mainStcokReturn()
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

    # 计算各季度选股超额收益率
    def excessReturn_quarter(self):
        # 采用每期的期初持仓
        if len(self.allfundHolding.columns) > 1:
            erQuarter = pd.Series(index=list(self.allfundHolding.columns), name='ER')
            for i in range(1, self.allfundHolding.shape[1]):
                quarter = self.allfundHolding.columns[i]
                tmp = pd.DataFrame(self.allfundHolding.iloc[:, i - 1].dropna())
                # 剔除数据缺失的持仓标的
                indexList = list(set(tmp.index).intersection(set(self.stockRet.columns)))
                tmp = tmp.reindex(indexList)
                if len(tmp) > 0:
                    tmp['weight'] = tmp.iloc[:, 0] / (tmp.iloc[:, 0].sum())
                    tmp['indusCode'] = self.stockIndus[list(tmp.index)].values
                    tmp['et'] = self.stockRet.loc[quarter, list(tmp.index)].values
                    tmp['rt'] = self.indusRet.loc[quarter, list(tmp['indusCode'])].values
                    erQuarter[i] = (tmp['weight'] * (tmp['et'] - tmp['rt'])).sum()
            self.erQuarter = erQuarter.dropna()
        else:
            self.erQuarter = []

    # 分行业计算各期平均超额收益率
    def excessReturn_industry(self):
        # 单期超额收益率的简单平均，若某期在某行业上无个股配置，则求均值时剔除该期
        if len(self.allfundHolding.columns) > 1:
            erIndus = pd.DataFrame(index=list(self.indusRet.columns), columns=list(self.allfundHolding.columns))
            for i in range(1, self.allfundHolding.shape[1]):
                quarter = self.allfundHolding.columns[i]
                tmp = pd.DataFrame(self.allfundHolding.iloc[:, i - 1].dropna())
                # 剔除数据缺失标的
                indexList = list(set(tmp.index).intersection(set(self.stockRet.columns)))
                tmp = tmp.reindex(indexList)
                if len(tmp) > 0:
                    tmp['indusCode'] = self.stockIndus[list(tmp.index)].values
                    tmp['et'] = self.stockRet.loc[quarter, list(tmp.index)].values
                    tmp['rt'] = self.indusRet.loc[quarter, list(tmp['indusCode'])].values
                    tmp['er'] = tmp['et'] - tmp['rt']
                    for j, res in tmp.groupby('indusCode'):
                        res1 = res.copy()
                        res1['weight'] = res1.iloc[:, 0] / (res1.iloc[:, 0].sum())
                        erIndus.loc[j, quarter] = (res1['weight'] * res1['er']).sum()
            erIndus.dropna(how='all', inplace=True)
            self.erIndus = erIndus
        else:
            self.erIndus = []

    # 分行业各期选股收益与行业成分股收益比较
    def compareReturn_industry(self):
        compareReturn = dict()
        if len(self.allfundHolding.columns) > 1:
            # 调取基金统计区间的行业成分股分位数收益率数据
            quarterList = self.allfundHolding.columns
            for indus in self.erIndus.index:
                compareReturn_single = pd.DataFrame(np.nan, index=self.erIndus.columns[1:],
                                                    columns=['选股收益率', '25分位数', '50分位数', '75分位数'])
                for myDate in compareReturn_single.index:
                    compareReturn_single.loc[myDate, '选股收益率'] = self.erIndus.loc[indus, myDate] + self.indusRet.loc[
                        myDate, indus]
                    compareReturn_single.loc[myDate, '25分位数'] = self.crIndus[indus].loc['25分位数', myDate]
                    compareReturn_single.loc[myDate, '50分位数'] = self.crIndus[indus].loc['50分位数', myDate]
                    compareReturn_single.loc[myDate, '75分位数'] = self.crIndus[indus].loc['75分位数', myDate]
                    compareReturn_single.dropna(inplace=True)
                compareReturn[indus] = compareReturn_single
        self.compareReturn = compareReturn

    # 历史各重仓股投资绩效统计
    def mainStcokReturn(self):
        # 个股各期持有权重采直接采用占基金净值比例即可，无需归一化
        # 均采用期初持仓数据计算本期收益率
        if len(self.allfundHolding.columns) > 1:
            holdingInfo = []
            for i in range(1, self.allfundHolding.shape[1]):
                quarter = self.allfundHolding.columns[i]
                tmp = pd.DataFrame(self.allfundHolding.iloc[:, i - 1].dropna())
                tmp['weight'] = tmp.iloc[:, 0] / (tmp.iloc[:, 0].sum())
                tmp['indusCode'] = self.stockIndus.reindex(list(tmp.index)).values
                tmp['et'] = self.stockRet.loc[quarter].reindex(list(tmp.index)).values
                tmp['rt'] = self.indusRet.loc[quarter].reindex(list(tmp['indusCode'])).values
                tmp['er'] = tmp['et'] - tmp['rt']
                tmp.index.name = 'stockCode'
                tmp = tmp.reset_index()
                holdingInfo.append(tmp)
            holdingInfo = pd.concat(holdingInfo, axis=0, sort=True)
            msReturn = pd.DataFrame(columns=['配置期数(季度)', '平均权重(%)', '所属行业', '持有季度平均收益(%)', '持有季度平均行业超额收益(%)'])
            for j, res in holdingInfo.groupby('stockCode'):
                msReturn.loc[j] = [len(res), res['weight'].mean(), res['indusCode'].values[0], res['et'].mean(),
                                   res['er'].mean()]

            # 添加股票名称
            stockName = pd.Series(np.nan, index=msReturn.index, name='stockName')
            stockName_tmp = pd.Series(getData_stockInformation(list(msReturn.index), 'stockName'))
            stockName[stockName_tmp.index] = stockName_tmp
            msReturn = pd.concat([msReturn, stockName], axis=1, sort=True)
            self.msReturn = msReturn
        else:
            self.msReturn = []

    # 生成结果
    def generateOutput(self):
        try:
            self.output = {'excessReturnQuarter': self.erQuarter, 'excessReturnIndustry': self.erIndus.mean(axis=1),
                           'compareReturnIndustry': self.compareReturn, 'mainStcokReturn': self.msReturn}
        except:
            self.output = {'excessReturnQuarter': self.erQuarter, 'excessReturnIndustry': [],
                           'compareReturnIndustry': self.compareReturn, 'mainStcokReturn': self.msReturn}


# 基金经理选股能力评价
class stockPickingAbility_manager:
    def __init__(self, btParms, stockIndus, stockRet, indusRet, crIndus):
        self.manager = btParms['manager']
        self.symbol = btParms['symbol']
        self.stockIndus = stockIndus
        self.stockRet = stockRet
        self.indusRet = indusRet
        self.crIndus = crIndus
        self.genrOutput()

    # 获取基金经理的任职区间
    def getPeriod(self):
        managerPeriod = getData_fundManagerInfo(self.symbol)[self.manager]
        startDate = datetime.strftime(managerPeriod[0] + timedelta(95), '%Y%m%d')
        endDate = datetime.strftime(managerPeriod[1], '%Y%m%d')
        return {'symbol': self.symbol, 'startDate': startDate, 'endDate': endDate}

    # 调取基金选股能力的类
    def genrOutput(self):
        managerId = getData_fundManagerId(self.manager, self.symbol)
        btParms = self.getPeriod()
        if (parse(btParms['endDate']) - parse(btParms['startDate'])).days < 90:
            self.output = {'excessReturnQuarter': [], 'excessReturnIndustry': [],
                           'compareReturnIndustry': {}, 'mainStcokReturn': []}
        else:
            eta = stockPicking(btParms, self.stockIndus, self.stockRet, self.indusRet, self.crIndus)
            self.output = eta.output
        self.output.update({'managerId': managerId, 'manager': self.manager, 'symbol': self.symbol})


if __name__ == '__main__':

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
        if i < 100:  # 生产环境删除该句
            btParms = {'symbol': managerInfo.loc[i, 'fund'], 'manager': managerInfo.loc[i, 'manager']}
            print(i)
            try:
                test = stockPickingAbility_manager(btParms, stockIndus, stockRet, indusRet, crIndus)
                output = test.output
            except:
                output = {'managerId': managerInfo.loc[i, 'managerId'], 'symbol': managerInfo.loc[i, 'fund'],
                          'manager': managerInfo.loc[i, 'manager'], 'excessReturnQuarter': [],
                          'excessReturnIndustry': [],
                          'compareReturnIndustry': {}, 'mainStcokReturn': []}
            output_all.append(output)

    '''
    btParms={'symbol':'000001.OF',
             'startDate':'2016/12/27',
             'endDate':'2018/12/27',
             }

    btParms={'symbol':'001236.OF',
             'manager':'王俊',
             }

   self=stockPickingAbility_manager(btParms,stockIndus,stockRet,indusRet,crIndus) 

    date1=datetime.now()
    self=stockPicking(btParms,stockIndus,stockRet,indusRet,crIndus)
    output=self.output
    date2=datetime.now()
    diff=date2-date1
    print(diff.seconds)
    print(self.output)
    '''






