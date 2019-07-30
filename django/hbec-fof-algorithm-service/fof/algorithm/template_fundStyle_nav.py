# -*- coding: utf-8 -*-
"""
基金净值风格划分模型
批量生成基金成立以来的净值风格回归结果
本模型批量生成的结果存放于output_all中
output_all按基金名称存放各个基金净值划分结果
共有3个字段，落库字段为symbol以及regStat，第三个字段cycle是为了实时计算之方便，离线入库无需存入该字段
regStat存放了按区间划分的每期大小盘回归结果，涵盖起始时间，结束时间，大盘系数，小盘系数以及拟合优度R2

考虑到服务器的承载能力，该程序前期可每周更新，后续服务器运载能力加大，可改为每日更新

该模块还支持实时交互，cycle按照既定格式输入即可，格式为:'20120101,20181231'

"""
import pandas as pd
import numpy as np
import scipy.stats as st 
from datetime import datetime,timedelta
from dateutil.parser import parse
from scipy.optimize import  minimize
from sklearn import linear_model

from conf import mysqlops
from conf.data_source import MysqlConf
from fof.algorithm.getData_sql import  *

#单个基金风格计算夏普模型类函数
from util import uuid_util
from util.num_util import transformFloatIfAvaliable4


class fundStyle_nav:
     def __init__(self,btParms):
        self.symbol=btParms['symbol']       #基金名称
        self.cycle=btParms['cycle']         #当为数字时，以年为单位
        self.largeCapBench='000903.SH'
        self.smallCapBench='000852.SH'
        self.period=20*6                   #区间长度划分
        #加载函数
        try:
            self.genrPeriod()
            self.getDataFromDb()
            self.genrNavStyle()
            self.genrOutput()
        except:
            self.output={"symbol":self.symbol,'cycle':self.cycle,'regStat':[]}
            self.output_json={"symbol":self.symbol,'cycle':self.cycle,'regStat':''}
            

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
                else:
                    self.startDate=tmp[0][0]
                self.startDate=datetime.strftime(self.startDate+timedelta(90),'%Y%m%d') #剔除3个月建仓期  
            else:
                cycle=int(eval(self.cycle)*365)
                self.startDate=datetime.strftime(parse(self.endDate)-timedelta(cycle),'%Y%m%d')    
        #调整startDate最早可追溯日期
        self.startDate=datetime.strftime(max(parse(self.startDate),datetime(2005,1,4)),'%Y%m%d')
           
     #从数据库获取回测中要用到的数据
     def getDataFromDb(self): 
        startDate=self.startDate
        endDate=self.endDate
        symbol=self.symbol
        largeCapBench=getData_marketIndex(self.largeCapBench, startDate, endDate)
        smallCapBench=getData_marketIndex(self.smallCapBench, startDate, endDate)
        fundNav=getData_fundHistoryData('adjNav', symbol, startDate, endDate).dropna()
        
        self.largeCapBench=largeCapBench
        self.smallCapBench=smallCapBench
        self.fundNav=fundNav
    
     #净值风格计算
     def genrNavStyle(self):
        #数据导入
        largeCapBench=self.largeCapBench
        smallCapBench=self.smallCapBench
        fundNav=self.fundNav
        
        #sharpe模型每期回归结果
        largeCapBenchReturn=largeCapBench.pct_change().dropna()
        smallCapBenchReturn=smallCapBench.pct_change().dropna()
        fundReturn=fundNav.pct_change().dropna()
        largeCapBenchReturn=largeCapBenchReturn.reindex(fundReturn.index,method='ffill')
        smallCapBenchReturn=smallCapBenchReturn.reindex(fundReturn.index,method='ffill')
        #将区间拆解为N段，依次计算
        regPeriod=list(range(len(fundReturn)-1,-1,-self.period+1))
        tmp=[]
        for i in range(len(regPeriod)-1):
            xWeight,tStas=self.sharpeModel(fundReturn[regPeriod[i+1]:regPeriod[i]+1],
            largeCapBenchReturn[regPeriod[i+1]:regPeriod[i]+1],smallCapBenchReturn[regPeriod[i+1]:regPeriod[i]+1])
            tmp.append({"startDate":fundReturn[regPeriod[i+1]:regPeriod[i]+1].index[0],
                        "endDate":fundReturn[regPeriod[i+1]:regPeriod[i]+1].index[-1],
                        "largeCoeff":xWeight[0],"smallCoeff":xWeight[1],'R2':tStas[-1]})
        self.regStat=pd.DataFrame(tmp,columns=['startDate','endDate','largeCoeff','smallCoeff','R2'])
        if len(self.regStat)==0:
            self.regStat=[]
            
     def genrOutput(self):
         self.output={"symbol":self.symbol,'cycle':self.cycle,'regStat':self.regStat}
         if len(self.regStat)>0:
             tmp=self.regStat.copy()
             tmp['startDate']=[datetime.strftime(m,'%Y%m%d') for m in tmp['startDate']]
             tmp['endDate']=[datetime.strftime(m,'%Y%m%d') for m in tmp['endDate']]
             regStat=[]
             for row in tmp.index:
                 regStat.append(tmp.loc[row].astype(str).to_dict())
         else:
            regStat=''
         self.output_json={"symbol":self.symbol,'cycle':self.cycle,'regStat':regStat}
         
         
     #sharpe模型
     @staticmethod 
     def sharpeModel(ySeries,xSeries1,xSeries2):
        fun=lambda x: (np.std(ySeries-x[0]*xSeries1-x[1]*xSeries2))**2
        cons1 = ({'type': 'eq', 'fun': lambda x: 1 - sum(x)})
        bnds = []
        for i in range(0, 2):
            bnds.append((0, 1))
        initial=[0.5]*2
        res = minimize(fun,initial, method='SLSQP', bounds=bnds, constraints=[cons1],options={'ftol': 1e-10})
        xWeight=list(res.x)
        #显著性检验:t统计量
        clf = linear_model.LinearRegression()
        sigma=np.std(ySeries-xWeight[0]*xSeries1-xWeight[1]*xSeries2)
        clf.fit(xSeries2.values.reshape(-1, 1),xSeries1.values.reshape(-1, 1))#x,y
        sigma1=np.std(xSeries1-clf.coef_[0]*xSeries2)
        tStas1=clf.coef_[0]*sigma1*np.sqrt(len(xSeries1)-2-1)/sigma # xSeries1系数t统计量
        clf.fit(xSeries1.values.reshape(-1, 1),xSeries2.values.reshape(-1, 1))#x,y
        sigma2=np.std(xSeries2-clf.coef_[0]*xSeries1)
        tStas2=clf.coef_[0]*sigma2*np.sqrt(len(xSeries2)-2-1)/sigma # xSeries2系数t统计量
        p1=2*(1-st.t.cdf(abs(float(tStas1)),len(xSeries1)-2-1))#求p值,t统计量，自由度n-k-1,系数1是否不等于0
        p2=2*(1-st.t.cdf(abs(float(tStas1)),len(xSeries1)-2-1))
        #回归拟合优度
        y_true=ySeries.copy()
        y_pred= xWeight[0]*xSeries1+xWeight[1]*xSeries2
        if (((y_true - y_true.mean())**2).sum()/(len(xSeries1)-1))!=0:
            r2=max(0,1-(((y_pred - y_true)**2).sum()/(len(xSeries1)-2))/(((y_true - y_true.mean())**2).sum()/(len(xSeries1)-1)))
        else:
            r2=0
        return xWeight,[float(tStas1),float(tStas2),p1,p2,r2]      
        



if __name__=='__main__':
    
    
    # fundSymbols=getData_fundSymbols(['股票型','混合型'])
    fundSymbols=['000001.OF']
    # fundSymbols=fundSymbols[0:20] #生产环境删除此句
    output_all=[]
    for symbol in fundSymbols:
        btParms={'symbol':symbol,'cycle':'成立以来'} #离线入库时cycle设定为"成立以来"即可
        test=fundStyle_nav(btParms)
        output=test.output
        tmp = output['regStat']
        if tmp is None or len(tmp) == 0:
            continue
        for idx in tmp.index:
            di = tmp.loc[idx].to_dict()
            startDate = di['startDate']
            endDate = di['endDate']
            largeCoe = di['largeCoeff']
            smallCoe = di['smallCoeff']
            r2 = di['R2']

            lst = []
            id_ = uuid_util.gen_uuid()  # objId
            lst.append(id_)
            lst.append(output['symbol'])
            lst.append(startDate)
            lst.append(endDate)
            lst.append(largeCoe)
            lst.append(smallCoe)
            lst.append(r2)
            lst.append("sys")
            lst.append(datetime.now())
            lst.append("sys")
            lst.append(datetime.now())
            ll = [transformFloatIfAvaliable4(j) for j in lst]
            sql = "INSERT INTO `fof`.`fof_fundnav_style`(`OBJECT_ID`, `J_WINDCODE`, `START_DATE`, `END_DATE`, `LARGE_COEFFICIENTS`, `SMALL_COEFFICIENTS`,`R2`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
            mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(ll))

    
    
    '''
    实时交互demo
    btParms={'symbol':'000001.OF','cycle':'20120101,20190331'}
    test=fundStyle_nav(btParms)
    output_json=test.output_json
    print(output_json)
    '''

    
  
    
    
        