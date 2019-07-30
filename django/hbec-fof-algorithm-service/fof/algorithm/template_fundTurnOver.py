# -*- coding: utf-8 -*-
"""
基金换手率模块
一次生成所有权益类基金自成立以来的换手率（时间区间统一设定为2002年起来），结果存放于类的output属性中
该程序于每半年进行一次更新
请于每年的3月20日~3月31日以及8月20日~8月31日更新
由于程序运行量不大，若更新时间配置麻烦，可设定为每日更新
"""

import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from dateutil.parser import parse
from fof.algorithm.getData_sql import *



class fundTurnOver:
    def __init__(self,btParms):
        self.symbol=btParms['symbol']        #基金代码，支持传入多个基金
        self.startDate=btParms['startDate']  #起始日期
        self.endDate=btParms['endDate']      #结束日期
       

        #加载函数,写成类的私有函数形式，避免前端调用时意外篡改
        self.transformDataType()
        self.getDataFromDb()
        self.generateOutput()
        
    #将前端拿到的json格式数据批量转换成该类中需要的数据格式   
    def transformDataType(self):
        try:
            self.startDate=datetime.strftime(parse(self.startDate),'%Y%m%d')
        except:
            self.startDate=datetime.strftime(self.startDate,'%Y%m%d') 
        try:
            self.endDate=datetime.strftime(parse(self.endDate),'%Y%m%d')
        except:
            self.endDate=datetime.strftime(self.endDate,'%Y%m%d')
            
        
    #从数据库获取模型中要用到的数据，此处以华宝金工团队自建的mongoddb数据库为例   
    def getDataFromDb(self):
        turnOver=getData_fundTurnOver(self.symbol,self.startDate,self.endDate)
        #剔除数据缺失标的
        while 1:
            length=len(turnOver)
            for key in turnOver:
                if len(turnOver[key])==0:
                    turnOver.pop(key)
                    break
            if len(turnOver)==length:
                break
        self.turnOver=turnOver
        
    #生成结果，json格式
    def generateOutput(self):
       self.output=self.turnOver


if __name__=='__main__':
    fundSymbols=getData_fundSymbols(['股票型','混合型'])
    #fundSymbols=fundSymbols[0:100] #生产环境删除此句

    btParms={'symbol':fundSymbols,'startDate':'20020101','endDate':datetime.strftime(datetime.today(),'%Y%m%d')}
    self=fundTurnOver(btParms)
    output=self.output
    
    

   
   
    
  
    
    
        