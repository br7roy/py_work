# -*- coding: utf-8 -*-
"""
风险因子业绩归因模块
结果存放于output中，所有生成的结果均需入库，其中holdingTye代表归因采用的是重仓股数据还是全部持仓数据
singleAttr代表单期归因结果，dataFrame格式，columns分别为：style-风格因子归因，industry-行业因子归因，idiosyn-特质因子归因
fundRet-基金当月收益率;
multiAttr代表多期归因结果，即所选cycle下的最终归因结果，涵盖9个风格因子，1个特质因子以及29个行业因子的归因收益

本程序更新频率与template_fundFactorExposure.py文件更新频率一致，即：
重仓股数风格暴露数据，于每季结束后的第一个月的15日开始运行本程序，按日更新，运行至该月末
全部持仓数据，于每年的8月21日~8月31日，以及3月21日~3月31日运行
"""

import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from dateutil.parser import parse
from fof.algorithm.getData_sql import *

#本模块的公共数据
def publicData_riskModel():
    #行业指数 
    stockSymbol=getData_stockConstitue('aStock')
    stockIndus=getData_stockInformation(stockSymbol) #股票对应中信一级行业
    indusCodeList=list(set(stockIndus.values()))
    
    indusClose=[]
    indusCodes=industryMap('CI')
    for name in indusCodeList:
        indusCode=indusCodes[name]
        tmp=getData_marketIndex(indusCode,'2010/1/1',datetime.today(),'月')
        indusClose.append(tmp)
    indusClose=pd.concat(indusClose,axis=1,sort=True)
    indusClose.fillna(method='ffill',inplace=True) #填充nan值，避免报错
    indusClose.columns=indusCodeList
    indusReturn=indusClose.pct_change().dropna()
    
    stockIndus=pd.Series(stockIndus) #股票行业属性
    
    #因子暴露度数据
    factorList=['beta','earning','growth','leverage','liquidity','momentum','size','value','volatility']
    factorExposure={}
    for factor in factorList:
        data=getData_factorExposure(factor,startDate='2010/1/1',endDate=datetime.today())
        factorExposure[factor]=data
        
    #因子收益率
    factorReturn=getData_factorReturn(factorList).reindex(indusClose.index)
    return stockIndus,indusReturn,factorExposure,factorReturn
    


#基金业绩归因模型
class attribution_riskModel: 
    def __init__(self,btParms,stockIndus,indusReturn,factorExposure,factorReturn):
        self.symbol=btParms['symbol']       #基金名称
        self.cycle=btParms['cycle'] #计算风格的起始日期
        self.holdingType=btParms['holdingType']    #归因数据类型,重仓股、全部持仓
        
        self.stockIndus=stockIndus
        self.indusReturn=indusReturn
        self.factorExposure=factorExposure
        self.factorReturn=factorReturn
        
        #加载函数
        try:
            self.genrPeriod()
            self.getDataFromDb()
            self.generateSingleAttribution()
            self.generateMultAttribution()
            self.generateOutput()
        except:
            self.output={'singleAttr':[],'multiAttr':[]}
            self.output.update({'symbol':self.symbol,'cycle':self.cycle,'holdingType':self.holdingType})
       
    #生成日期区间
    def genrPeriod(self):
        #若cycle设定是起始日期格式
        if ',' in self.cycle:
           self.startDate=self.cycle.split(',')[0]
           self.endDate=self.cycle.split(',')[1]
        #若cycle设定的不是起始日期格式    
        else:
            self.endDate=datetime.strftime(datetime.today(),'%Y%m%d')
            if self.cycle=='成立以来':
                fundInfo=getData_fundInformation(self.symbol)
                startDate=fundInfo.loc[self.symbol,'FUND_SETUPDATE']
                if startDate<parse('20100101'):
                    self.startDate='20100101'
                else:
                    self.startDate=datetime.strftime(startDate,'%Y%m%d')     
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
 
    #从数据库获取模型中要用到的数据，
    def getDataFromDb(self):
        #提取基金净值数据
        fundNav=getData_fundHistoryData('adjNav',self.symbol,self.startDate,self.endDate)
        self.fundNav=fundNav
        
        #生成季度交易日与自然日
        wdays_Q=pd.date_range(self.startDate,parse(self.endDate)+timedelta(15),freq='Q')
        if self.holdingType=='allStockHolding':
            wdays_Q=[m for m in wdays_Q if m.month in (6,12)]
           
        self.fundHolding_all=[]
        if len(wdays_Q)>0:
            #提取基金持仓数据
            fundHolding_all={}
            for execDate in wdays_Q:
                fundHolding=getData_fundSecHoldingData(self.holdingType,self.symbol,execDate)[['股票代码','持股市值']]
                #剔除不在股票因子范围内标的一级缺少行业分类的标的
                fundHolding=fundHolding.set_index('股票代码')
                fundHolding=fundHolding.loc[set(fundHolding.index) & set(self.factorExposure['growth'].columns)
                            & set(self.stockIndus.index)]
                if len(fundHolding)>0:
                    fundHolding_all[execDate]=fundHolding
                    
        if len(fundHolding_all)>0:
            fundHolding_all_tmp=pd.concat(list(fundHolding_all.values()),axis=1,sort=True)
            #将有持仓数据的财报日生成交易日
            if self.holdingType=='mainStockHolding':
                tradeDays=convertDays(list(fundHolding_all.keys()),'季')
            else:
                tradeDays=convertDays(list(fundHolding_all.keys()),'半年')
            tradeDays.sort()
            fundHolding_all_tmp.columns=tradeDays
            fundHolding_all_tmp=fundHolding_all_tmp.fillna(0)
            self.fundHolding_all=fundHolding_all_tmp
        
        #生成月度自然日期
        tdays_M=getData_tradeDays(self.fundHolding_all.columns[0],self.fundHolding_all.columns[-1],'月')
        #月度持仓
        monthPosition=pd.DataFrame(np.nan,index=self.fundHolding_all.index,columns=tdays_M)
        monthPosition[self.fundHolding_all.columns]=self.fundHolding_all 
        #按月分配个股市值变动
        for i in range(len(monthPosition)):
            tmp=monthPosition.iloc[i].copy()
            icounter=0
            tmp1=[]
            while 1:
                icounter+=1
                if pd.isnull(tmp[icounter]):
                    tmp1.append(tmp.index[icounter])
                else:
                    startIndex=list(tmp.index).index(tmp1[0])-1
                    endIndex=list(tmp.index).index(tmp1[-1])+1
                    stockValue=(tmp[endIndex]-tmp[startIndex])/(len(tmp1)+1)
                    for j in range(1,len(tmp1)+1):
                        tmp[startIndex+j]=tmp[startIndex+j-1]+stockValue 
                    tmp1=[]  
                if icounter==len(tmp)-1:
                    monthPosition.iloc[i]=tmp
                    break 
        monthPositionRatio=monthPosition/(monthPosition.sum(axis=0))
        self.monthPositionRatio=monthPositionRatio.T
        
    #单期归因
    def generateSingleAttribution(self):
        #生成一个存放各期归因结果的大矩阵
        col=list(self.indusReturn.columns)+list(self.factorReturn.columns)
        exposure=pd.DataFrame(index=self.monthPositionRatio.index,columns=col)
        
        for i in range(len(self.monthPositionRatio)):
            tmp_month=self.monthPositionRatio.index[i]
            tmp_weight=self.monthPositionRatio.iloc[i]
            tmp_indus=self.stockIndus[list(tmp_weight.index)]
            tmp_factors=self.factorExposure
            #行业因子暴露度
            for j in range(self.indusReturn.shape[1]):
                indus_name=exposure.columns[j]
                exposure.iloc[i,j]=tmp_weight[tmp_indus[tmp_indus==indus_name].index].sum()
            #风格因子暴露度
            for k in range(self.indusReturn.shape[1],exposure.shape[1]):
                style_name=exposure.columns[k]
                myFactor=tmp_factors[style_name].loc[tmp_month].replace(9999,np.nan)
                myFactor.fillna(myFactor.median(),inplace=True)
                exposure.iloc[i,k]=(myFactor*tmp_weight).sum()
        exposure=exposure.shift(1)
        facRet=pd.concat([self.indusReturn,self.factorReturn],axis=1).loc[exposure.index]
        singleAttribution=exposure*facRet
        self.singleAttr=singleAttribution.dropna().copy()
        self.fundRet=self.fundNav.reindex(self.monthPositionRatio.index).pct_change().reindex(self.singleAttr.index).dropna()
        self.singleAttr['特质因子']=self.fundRet-self.singleAttr.sum(axis=1) #加入特质因子
    
    #跨期归因
    def generateMultAttribution(self):
        fundRet=self.fundRet
        self.singleAttr=self.singleAttr.reindex(fundRet.index)
        k1=np.log(fundRet+1)/fundRet
        r=(fundRet+1).cumprod()[-1]-1
        k2=np.log(1+r)/r
        k3=k1/k2
        multiAttribution=self.singleAttr.mul(k3,axis=0).dropna()
        multiAttribution=pd.DataFrame(multiAttribution.iloc[:-1].sum(axis=0),columns=['multiAttr'])
        multiAttribution['factorType']=['行业']*self.indusReturn.shape[1]+\
                                        ['风格']*(len(multiAttribution)-self.indusReturn.shape[1])
        self.multiAttr=multiAttribution
    
    
    #生成归因结果
    def generateOutput(self):
        #pthon格式输出结果
        singleAttr=pd.DataFrame(index=self.singleAttr.index,columns=['style','industry','idiosyn','fundRet'])
        for i in range(len(singleAttr)):
            singleAttr.iloc[i,0]=self.singleAttr.iloc[i,self.singleAttr.shape[1]-10:-1].sum()
            singleAttr.iloc[i,1]=self.singleAttr.iloc[i,0:self.singleAttr.shape[1]-10].sum()
            singleAttr.iloc[i,3]=self.fundRet[i]
            singleAttr.iloc[i,2]=singleAttr.iloc[i,3]-singleAttr.iloc[i,0]-singleAttr.iloc[i,1]
            
       
        self.output={'singleAttr':singleAttr,'multiAttr':self.multiAttr}
        self.output.update({'symbol':self.symbol,'cycle':self.cycle,'holdingType':self.holdingType})
        

if __name__=='__main__':
    stockIndus,indusReturn,factorExposure,factorReturn=publicData_riskModel()
    
    
    #批量运行
    '''
    跨期归因结果需要存储多个周期值
    单期归因结果仅存储成立以来的值即可
    跨期归因和单期归因可以用两张表来存储数据
    '''
    output_all_mainStockHolding=[]
    output_all_allStockHolding=[]
    
    fundSymbols=getData_fundSymbols(['股票型','混合型'])
    fundSymbols=fundSymbols[0:5]
    cycleList=['1','2','3','5','成立以来']
    holdingTypeList=['mainStockHolding','allStockHolding']
    i=0
    for holdingType in holdingTypeList:
        for symbol in fundSymbols:
            for cycle in cycleList:
                i+=1
                print(i)
                btParms={'symbol':symbol,'cycle':cycle,'holdingType':holdingType}
                self=attribution_riskModel(btParms,stockIndus,indusReturn,factorExposure,factorReturn)
                output=self.output
                if holdingType=='mainStockHolding':
                    output_all_mainStockHolding.append(output)
                else:
                    output_all_allStockHolding.append(output)
                
                     
    
    '''
    #单基金调试代码
    btParms={'symbol':'000001.OF',
             'cycle':'成立以来',
             'holdingType':'allStockHolding'
             }
    
    self=attribution_riskModel(btParms,stockIndus,indusReturn,factorExposure,factorReturn)
    output=self.output
    print(self.output['singleAttr'])
    print(self.output['multiAttr'])
    '''
        