# -*- coding: utf-8 -*-
"""
基金各期持仓暴露度计算模型
本模型最终生成两个结果，output
本程序已写成批量更新形式，最终的结果保存在output_mainStockHolding与allStockHolding中，将该结果存执fof数据库即可
前者代表按季更新的十大重仓股风格分析，后者代表按半年频率分析的全部持仓股风格分析
两个结果内部的结果与形式一样
离线落库时，仅落库symbol及hisExposure中字段即可,其他字段仅是为了辅助标识，便于拓展为实时功能，无需落库

hisExposure代表历史持仓风格分析
hisExposure中的key为财报时间，key对应的value为dataFarme格式，其中：
portExposure代表在各因子上的组合暴露度，portExposrueScore代表持仓组合在各个因子上的得分
当hisEposure无结果时，返回一个空list，此时可以不落库

重仓股数风格暴露数据，请于每季结束后的第一个月的15日开始运行本程序，按日更新，运行至该月末
全部持仓数据，请于每年的8月21日~8月31日，以及3月21日~3月31日运行
"""

import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from dateutil.parser import parse
from fof.algorithm.getData_sql import *




#一次性获取公共数据
def publicData_stockFactor():
    #提取因子数据
    tdays_Q=getData_tradeDays(startDate='20100101',endDate=datetime.today(),frequency='季')
    factorList=['beta','earning','leverage','liquidity','momentum','size','value','volatility','growth']
    factorExposure={}
    for factor in factorList:
        data=getData_factorExposure(factor,startDate='20100101',endDate=datetime.today())
        data=data.replace(9999,np.nan)
        data=data.reindex(list(set(data.index).intersection(set(tdays_Q))))
        data.sort_index(inplace=True)
        wdays_Q=pd.date_range(data.index[0],data.index[-1]+timedelta(15),freq='Q')
        data.index=wdays_Q #日期转为自然日，与持仓数据日期相对应
        factorExposure[factor]=data
    return factorExposure
    



class fundFactorExposure:
    def __init__(self,btParms,factorExposure):
        self.symbol=btParms['symbol']       #基金名称
        self.holdingType=btParms['holdingType'] #持仓类型
        self.factorExposure=factorExposure
        self.cycle='成立以来'      #当为数字时，以年为单位
       
        #加载函数
        try:
            self.genrPeriod()
            self.getDataFromDb()
            self.genrFundExposure()
            self.genrOutput()
        except:
            output={'symbol':self.symbol,'cycle':self.cycle,'holdingType':self.holdingType}
            output.update({'hisExposure':[]})
            self.output=output
  
        
    def genrPeriod(self):
        self.endDate=datetime.strftime(datetime.today(),'%Y%m%d')
        if self.cycle=='成立以来':
            fundInfo=getData_fundInformation(self.symbol)
            startDate=fundInfo.loc[self.symbol,'FUND_SETUPDATE']
            if startDate<parse('20100101'):
                self.startDate='20100101'
            else:
                self.startDate=datetime.strftime(startDate,'%Y%m%d') #剔除3个月建仓期    
        elif self.cycle=='任职以来':
            managerInfo=getData_fundManagerInfo(self.symbol)
            tmp=[]
            for key in managerInfo.keys():
                if (managerInfo[key][-1]-datetime.today()).days>=-1: #避免更新数据时跳过0点时报错
                    tmp.append(managerInfo[key])
            #如果是多基金经理管理，则取最远的日期作为startDate
            if len(tmp)>1:
                tmp1=[m[0] for m in tmp]
                tmp1.sort()
                self.startDate=tmp1[0]
            if self.startDate<parse('20100101'):
                self.startDate='20100101'
            else:
                self.startDate=datetime.strftime(self.startDate+timedelta(90),'%Y%m%d') 
        else:
            cycle=int(eval(self.cycle)*365)
            self.startDate=datetime.strftime(parse(self.endDate)-timedelta(cycle),'%Y%m%d')
        
    
    #从数据库获取模型中要用到的数据 
    def getDataFromDb(self):
        #生成季度交易日与自然日
        wdays_Q=pd.date_range(self.startDate,parse(self.endDate)+timedelta(15),freq='Q')
        if 'allStock' in self.holdingType:
            wdays_Q=[m for m in wdays_Q if m.month in (6,12)]
           
        self.fundHolding_all=[]
        if len(wdays_Q)>0:
            #提取基金持仓数据
            fundHolding_all={}
            for execDate in wdays_Q:
                if 'mainStock' in self.holdingType:
                    fundHolding=getData_fundSecHoldingData(self.holdingType,self.symbol,execDate)[['股票代码','持股市值']]    
                else:
                    fundHolding=getData_fundSecHoldingData(self.holdingType,self.symbol,execDate)[['股票代码','持股市值']]
                        
                #剔除不在股票因子范围内标的
                fundHolding=fundHolding.set_index('股票代码')
                fundHolding=fundHolding.loc[set(fundHolding.index).intersection(set(self.factorExposure['growth'].columns))]
                fundHolding['持股市值占比']=fundHolding.iloc[:,0]/(fundHolding.iloc[:,0].sum())
                fundHolding=fundHolding['持股市值占比']
                if len(fundHolding)>0:
                    fundHolding_all[execDate]=fundHolding
        if len(fundHolding_all)>0:
            self.fundHolding_all=fundHolding_all

    #暴露度计算
    def genrFundExposure(self):
        if len(self.fundHolding_all)>0:
            res_all=dict()
            #按有持仓数据的财报日循环
            for myDate in self.fundHolding_all.keys():
                position=self.fundHolding_all[myDate]
                res={}
                #按因子循环
                for factor in self.factorExposure.keys():
                    tmp=self.factorExposure[factor].loc[myDate].dropna()
                    consExposure=tmp.reindex(position.index) #组合成分股暴露度
                    consExposure.fillna(tmp.median(),inplace=True) # 组合成分股缺失值中位数填充
                    portExposure=(consExposure*position).sum() #组合暴露度
                    portQuantile=(tmp.values<=portExposure).sum()/len(tmp) #组合暴露度分位数
                    portExposureScore=portQuantile*100   # 组合暴露度得分
                    res[factor]={'portExposure':portExposure,'portExposureScore':portExposureScore}
                res_all[myDate]=pd.DataFrame(res).T
            self.res_all=res_all
        else:
            self.res_all=[]

    
    #生成结果
    def genrOutput(self):
        output={'symbol':self.symbol,'cycle':self.cycle,'holdingType':self.holdingType}
        output.update({'hisExposure':self.res_all})
        self.output=output 




if __name__=='__main__':
    
    #获取本模块公共数据
    factorExposure=publicData_stockFactor()

    output_allStockHolding=[]
    output_mainStockHolding=[]
    
    i=0
    fundSymbols=getData_fundSymbols(['股票型',' 混合型'])
    fundSymbols=fundSymbols[0:10] #生产环境删除此句
    typeList=['mainStockHolding','allStockHolding']
    #暴露度计算
    for holdingType in typeList:
        for symbol in fundSymbols:
            i+=1
            print(i)
            btParms={'symbol':symbol,'holdingType':holdingType}
            test=fundFactorExposure(btParms,factorExposure)
            output=test.output
            if holdingType=='mainStockHolding':
                output_mainStockHolding.append(output)
            else:
                output_allStockHolding.append(output)
    
    
    '''
    #单一标的测试代码
    btParms={'symbol':'001685.OF','holdingType':'mainStockHolding'}
    self=fundFactorExposure(btParms,factorExposure)
    output=self.output 
    '''
    

  

        