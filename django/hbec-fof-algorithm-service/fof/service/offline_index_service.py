from datetime import *

from conf.data_source import MysqlConf
from conf.mysqlops import del_data
from fof.algorithm.getData_sql import getData_fundSymbols
from fof.algorithm.stockFactor_mongo import getData_factorExposure
from fof.algorithm.template_attribution_riskModel import publicData_riskModel, attribution_riskModel
from util import uuid_util
from util.exception.biz_error_handler import Error
from util.num_util import transformFloatIfAvaliable, transformFloatIfAvaliable4
from conf import mysqlops


def stockexpousre(model):
    # factorName即为mongodb数据库相关collection的名字，一次仅支持传入一个因子值
    sql = "delete from fof_stockexpousre "
    mysqlops.fetch_one(MysqlConf.DB.fof, sql)

    if not del_data('fof_stockexpousre'):
        raise Error("删除历史数据失败，任务结束")

    fs = ['value',
          'size',
          'beta',
          'earning',
          # 'factorReturn',
          'growth',
          'leverage',
          'liquidity',
          'momentum',
          'nonlinear_size',
          'size',
          'volatility']
    sql = 'insert into ' \
          'fof_stockexpousre (OBJECT_ID,trade_dt,s_windcode,indicator_code,factor_value,CREATE_USER_ID,CREATE_TIME,UPDATE_USER_ID,UPDATE_TIME)' \
          'values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    for fName in fs:
        valueExp = getData_factorExposure(fName)
        valueExp = valueExp.fillna("9999.000000")

        di = valueExp.to_dict()
        for k in di:
            # print("K===%s" % k)
            for v in di.get(k):
                s = uuid_util.gen_uuid()
                lsd = []
                oid = s[:5] + '-' + s[5:9] + '-' + s[9:13] + '-' + s[13:18] + '-' + s[18:]
                lsd.append(oid)
                r = v._date_repr.replace("-", "")
                lsd.append(r)
                lsd.append(k[:-2] + "." + k[-2:])
                lsd.append(fName)
                lsd.append(transformFloatIfAvaliable(di.get(k).get(v)))
                lsd.append("sys")
                lsd.append(datetime.now())
                lsd.append("sys")
                lsd.append(datetime.now())
                mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(lsd))


def risk_single(model):
    # 风险因子业绩归因模块
    # fof_single_attr_riskmodel
    if not del_data('fof_single_attr_riskmodel'):
        raise Error("删除历史数据失败，任务结束")

    stockIndus, indusReturn, factorExposure, factorReturn = publicData_riskModel()

    # 批量运行
    '''
    跨期归因结果需要存储多个周期值
    单期归因结果仅存储成立以来的值即可
    跨期归因和单期归因可以用两张表来存储数据
    '''

    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    cycleList = ['成立以来']  # 这个程序跟之前的程序有一点特殊，就是多期归因要存多个周期的结果，单期归因只存成立以来的结果
    holdingTypeList = ['mainStockHolding', 'allStockHolding']
    for holdingType in holdingTypeList:
        for symbol in fundSymbols:
            for cycle in cycleList:
                btParms = {'symbol': symbol, 'cycle': cycle, 'holdingType': holdingType}
                self = attribution_riskModel(btParms, stockIndus, indusReturn, factorExposure, factorReturn)
                output = self.output
                tp = "1" if holdingType == 'mainStockHolding' else '2'  # 持仓类型
                param = output['singleAttr']
                if len(param) == 0:
                    continue
                for idx in param.index:
                    dt = idx  # time
                    di = param.loc[idx].to_dict()
                    style = di['style']  # 风格因子归因
                    industry = di['industry']  # 行业因子归因
                    idiosyn = di['idiosyn']  # 特质因子归因
                    fundRet = di['fundRet']  # 基金当月收益率
                    lsd = []
                    id_ = uuid_util.gen_uuid()
                    lsd.append(id_)
                    lsd.append(output['symbol'])
                    lsd.append(dt._short_repr.replace("-", ""))
                    lsd.append(tp)
                    lsd.append(style)
                    lsd.append(industry)
                    lsd.append(idiosyn)
                    lsd.append(fundRet)
                    lsd.append("sys")
                    lsd.append(datetime.now())
                    lsd.append("sys")
                    lsd.append(datetime.now())
                    lsd = [transformFloatIfAvaliable4(l) for l in lsd]
                    sql = 'INSERT INTO `fof`.`fof_single_attr_riskmodel`(`OBJECT_ID`, `S_INFO_WINDCODE`, `TRADE_DT`, `DATA_TYPE`, `STYLE`, `INDUSTRY`, `IDIOSYN`, `FUND_RETURN`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                    mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(lsd))


def risk_multiple(model):
    # 风险因子业绩归因模块
    # fof_multi_attr_riskmodel
    if not del_data('fof_multi_attr_riskmodel'):
        raise Error("删除历史数据失败，任务结束")

    stockIndus, indusReturn, factorExposure, factorReturn = publicData_riskModel()

    # 批量运行
    '''
    跨期归因结果需要存储多个周期值
    单期归因结果仅存储成立以来的值即可
    跨期归因和单期归因可以用两张表来存储数据
    '''
    # dataframe 周期类型和数据库周期类型映射关系
    cyleFormula = {'1': '1', '2': '2', '3': '3', '5': '4', '成立以来': '5'}
    fundSymbols = getData_fundSymbols(['股票型', '混合型'])
    cycleList = ['1', '2', '3', '5', '成立以来']
    holdingTypeList = ['mainStockHolding', 'allStockHolding']
    for holdingType in holdingTypeList:
        for symbol in fundSymbols:
            for cycle in cycleList:
                btParms = {'symbol': symbol, 'cycle': cycle, 'holdingType': holdingType}
                self = attribution_riskModel(btParms, stockIndus, indusReturn, factorExposure, factorReturn)
                output = self.output
                tp = "1" if holdingType == 'mainStockHolding' else '2'  # 持仓类型
                param = output['multiAttr']
                if len(param) == 0:
                    continue
                for idx in param.index:
                    di = param.loc[idx].to_dict()
                    indexName = idx  # 因子名称
                    indexType = di['factorType']  # 因子分类
                    indexAttr = di['multiAttr']  # 因子贡献收益
                    cyleTp = cyleFormula[cycle]  # 周期类型
                    lsd = []
                    id_ = uuid_util.gen_uuid()
                    lsd.append(id_)
                    lsd.append(output['symbol'])
                    lsd.append(tp)
                    lsd.append(cyleTp)
                    lsd.append(indexType)
                    lsd.append(indexName)
                    lsd.append(indexAttr)
                    lsd.append("sys")
                    lsd.append(datetime.now())
                    lsd.append("sys")
                    lsd.append(datetime.now())
                    lsd = [transformFloatIfAvaliable4(l) for l in lsd]

                    sql = 'INSERT INTO `fof`.`fof_multi_attr_riskmodel`(`OBJECT_ID`, `S_INFO_WINDCODE`, `DATA_TYPE`, `CYCLE_TYPE`, `FACTOR_TYPE`, `FACTOR_NAME`, `FACTOR_VALUE`, `CREATE_USER_ID`, `CREATE_TIME`, `UPDATE_USER_ID`, `UPDATE_TIME`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                    mysqlops.insert_one(MysqlConf.DB.fof, sql, tuple(lsd))
