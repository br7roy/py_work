# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd

import json
from scipy.optimize import minimize


# 均方差模型求解类函数
class mvModel:
    def __init__(self, assetVariable, risklessReturn, riskAssetReturn, assetStd, assetCorr, assetBounds, assetCons,
                 opFunType):
        self.assetVariable = assetVariable  # 资产名称及变量名称映射字典
        self.risklessReturn = risklessReturn  # 无风险利率
        self.riskAssetReturn = riskAssetReturn  # 风险资产预期收益率
        self.assetStd = assetStd  # 资产波动率
        self.assetCorr = assetCorr  # 资产相关系数
        self.assetBounds = assetBounds  # 资产上下界约束
        self.assetCons = assetCons  # 资产组合约束
        self.opFunType = opFunType  # 优化函数类型

        self.generateAssetSymbol()
        self.generateExpectReturn()
        self.generateCovMatrix()
        self.generateOpOutput()

    # 生成资产名称序列，list格式，并按照x0，x1...的顺序排序
    def generateAssetSymbol(self):
        symbolList = pd.Series(self.assetVariable)
        symbolList = symbolList.sort_values()
        self.assetSymbol = list(symbolList.index)

    # 转换预期收益成数值型,并加入现金资产的收益率,list格式
    def generateExpectReturn(self):
        tmp = []
        for symbol in self.assetSymbol:
            if symbol != "现金":
                tmp.append(eval(self.riskAssetReturn[symbol]))
        tmp[0:0] = [eval(self.risklessReturn)]
        self.assetReturn = tmp

    # 转化std成数值型，list格式
    def transformStd(self):
        tmp = []
        for symbol in self.assetSymbol:
            if symbol != "现金":
                tmp.append(eval(self.assetStd[symbol]))
        return tmp

    # 转化Corr为DataFrame格式，数值型
    def transformCorr(self):
        assetCorr = pd.DataFrame(self.assetCorr, index=self.assetSymbol[1:])
        assetCorr = assetCorr[self.assetSymbol[1:]]
        assetCorr = assetCorr.apply(pd.to_numeric)  # 批量转成数值型
        return assetCorr

    # 计算协方差矩阵
    def generateCovMatrix(self):
        assetStd = self.transformStd()
        assetCorr = self.transformCorr()
        covMatrix = []
        for i in range(len(assetStd)):
            for j in range(len(assetStd)):
                covMatrix.append(assetCorr.iloc[i, j] * assetStd[i] * assetStd[j])
        covMatrix = np.array(covMatrix).reshape(len(assetCorr), len(assetCorr))
        self.covMatrix = covMatrix

    # 生成资产上下界约束
    def generateBounds(self):
        tmp = []
        for symbol in self.assetSymbol:
            tmp1 = (eval(self.assetBounds[symbol][0]), eval(self.assetBounds[symbol][1]))
            tmp.append(tmp1)
        tmp = tuple(tmp)
        return tmp

    # 生成资产组合约束
    def generateCons(self):
        targetCons = []
        if len(self.assetCons) > 0:
            if len(self.assetCons) == 1:
                assetCons0 = self.assetCons["0"][1]
                tmp0 = {'type': self.assetCons["0"][0], 'fun': lambda x: eval(assetCons0)}
                targetCons.append(tmp0)
            elif len(self.assetCons) == 2:
                assetCons0 = self.assetCons["0"][1]
                assetCons1 = self.assetCons["1"][1]
                tmp0 = {'type': self.assetCons["0"][0], 'fun': lambda x: eval(assetCons0)}
                tmp1 = {'type': self.assetCons["1"][0], 'fun': lambda x: eval(assetCons1)}
                targetCons.append(tmp0)
                targetCons.append(tmp1)
            elif len(self.assetCons) == 3:
                assetCons0 = self.assetCons["0"][1]
                assetCons1 = self.assetCons["1"][1]
                assetCons2 = self.assetCons["2"][1]
                tmp0 = {'type': self.assetCons["0"][0], 'fun': lambda x: eval(assetCons0)}
                tmp1 = {'type': self.assetCons["1"][0], 'fun': lambda x: eval(assetCons1)}
                tmp2 = {'type': self.assetCons["2"][0], 'fun': lambda x: eval(assetCons2)}
                targetCons.append(tmp0)
                targetCons.append(tmp1)
                targetCons.append(tmp2)
            elif len(self.assetCons) == 4:
                assetCons0 = self.assetCons["0"][1]
                assetCons1 = self.assetCons["1"][1]
                assetCons2 = self.assetCons["2"][1]
                assetCons3 = self.assetCons["3"][1]
                tmp0 = {'type': self.assetCons["0"][0], 'fun': lambda x: eval(assetCons0)}
                tmp1 = {'type': self.assetCons["1"][0], 'fun': lambda x: eval(assetCons1)}
                tmp2 = {'type': self.assetCons["2"][0], 'fun': lambda x: eval(assetCons2)}
                tmp3 = {'type': self.assetCons["3"][0], 'fun': lambda x: eval(assetCons3)}
                targetCons.append(tmp0)
                targetCons.append(tmp1)
                targetCons.append(tmp2)
                targetCons.append(tmp3)
            elif len(self.assetCons) == 5:
                assetCons0 = self.assetCons["0"][1]
                assetCons1 = self.assetCons["1"][1]
                assetCons2 = self.assetCons["2"][1]
                assetCons3 = self.assetCons["3"][1]
                assetCons3 = self.assetCons["4"][1]
                tmp0 = {'type': self.assetCons["0"][0], 'fun': lambda x: eval(assetCons0)}
                tmp1 = {'type': self.assetCons["1"][0], 'fun': lambda x: eval(assetCons1)}
                tmp2 = {'type': self.assetCons["2"][0], 'fun': lambda x: eval(assetCons2)}
                tmp3 = {'type': self.assetCons["3"][0], 'fun': lambda x: eval(assetCons3)}
                tmp4 = {'type': self.assetCons["4"][0], 'fun': lambda x: eval(assetCons4)}
                targetCons.append(tmp0)
                targetCons.append(tmp1)
                targetCons.append(tmp2)
                targetCons.append(tmp3)
                targetCons.append(tmp4)

        # 添加额外约束条件
        if list(self.opFunType.keys())[0] == "组合风险约束":
            covMatrix = self.covMatrix
            tmp1 = {'type': 'ineq', 'fun': lambda x: (eval(self.opFunType[list(self.opFunType.keys())[0]])) ** 2
                                                     - np.dot(np.dot(x[1:], covMatrix), x[1:])}
            targetCons.append(tmp1)
        elif list(self.opFunType.keys())[0] == "组合收益约束":
            tmp1 = {'type': 'ineq', 'fun': lambda x: np.sum(self.assetReturn * x) -
                                                     eval(self.opFunType[list(self.opFunType.keys())[0]])}
            targetCons.append(tmp1)

        return targetCons

    # 生成模型的初始权重
    def generateX0(self):
        x0 = [1 / len(self.assetSymbol)] * len(self.assetSymbol)
        x0 = tuple(x0)
        return x0

    # 最优化计算
    def generateOpOutput(self):
        covMatrix = self.covMatrix
        assetReturn = self.assetReturn
        targetBounds = self.generateBounds()
        targetCons = self.generateCons()
        x0 = self.generateX0()

        # 定义目标函数
        if list(self.opFunType.keys())[0] == "组合风险约束":
            def targetFun(x):
                tmp = np.sum(assetReturn * x)
                return -tmp
        elif list(self.opFunType.keys())[0] == "组合收益约束":
            def targetFun(x):
                tmp = np.dot(np.dot(x[1:], covMatrix), x[1:]) + x[0] * 0
                return tmp
        elif list(self.opFunType.keys())[0] == "风险厌恶系数":
            def targetFun(x):
                tmp = np.sum(assetReturn * x) - 0.5 * eval(self.opFunType[list(self.opFunType.keys())[0]]) * \
                      np.dot(np.dot(x[1:], covMatrix), x[1:])
                return -tmp

        from scipy.optimize import minimize
        if len(targetCons) > 0:
            res = minimize(targetFun, x0, method='SLSQP', bounds=targetBounds, constraints=targetCons)
        else:
            res = minimize(targetFun, x0, method='SLSQP', bounds=targetBounds)

        self.opOutput = ['{:.4f}'.format(m) for m in res.x]
        self.porfolioReturn = '{:.4f}'.format(np.sum(res.x * assetReturn))
        self.porfolioRisk = '{:.4f}'.format(np.sqrt(np.dot(np.dot(res.x[1:], covMatrix), res.x[1:])))


if __name__ == '__main__':
    # 类中需要的变量均从前端获取，约定以json格式传递给后端
    assetVariable = {"现金": "x[0]", "沪深300": "x[1]", "大盘指数(申万)": "x[2]", "中债-总财富(总值)指数": "x[3]"}
    risklessReturn = "0.035"
    riskAssetReturn = {"沪深300": " -0.0938", "大盘指数(申万)": " -0.0877", "中债-总财富(总值)指数": " 0.0899"}
    assetStd = {"沪深300": "0.2084", "大盘指数(申万)": "0.2102", "中债-总财富(总值)指数": "0.0190"}
    assetCorr = {"沪深300": ["1.0", "0.998", "-0.2491"], "大盘指数(申万)": ["0.998", "1.0", "-0.2482"],
                 "中债-总财富(总值)指数": ["-0.2491", "-0.2482", "1.0"]}
    assetBounds = {"现金": ["0", "1"], "沪深300": ["0", "1"], "大盘指数(申万)": ["0", "1"], "中债-总财富(总值)指数": ["0", "1"]}
    assetCons = {"0": ["eq", "1-x[0]-x[1]-x[2]-x[3]"]}
    opFunType = {"风险厌恶系数": "3"}
    test = mvModel(assetVariable, risklessReturn, riskAssetReturn, assetStd, assetCorr, assetBounds, assetCons,
                   opFunType)

    # 均值方差模型计算结果，传递给前端
    print('优化结果是:%s' % test.opOutput)
    print('组合预期收益是:%s' % test.porfolioReturn)
    print('组合预期风险是:%s' % test.porfolioRisk)
