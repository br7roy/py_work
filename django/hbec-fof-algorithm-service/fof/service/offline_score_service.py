import datetime

import pandas as pd

from conf import mysqlops
from conf.data_source import MysqlConf
from conf.mysqlops import del_data
from fof.algorithm.getData_sql import getData_fundInformation
from fof.algorithm.template_singleIndexScore import getPublicData, indexScore_fund
from fof.model.model import OfflineTaskModel
from util import uuid_util, bus_const
from util.bus_const import INDEX_CODE_NAME_CACHE, cycle_score, marketIndex
from util.date_util import formatDate2yyyymmdd
from util.exception.biz_error_handler import Error
from util.num_util import transformFloatIfAvaliable2, transformFloatIfAvaliable4


def indicator_score_rank(model: OfflineTaskModel):
    # 离线计算指标得分

    indicatorId = model.extVal
    if indicatorId not in INDEX_CODE_NAME_CACHE.keys():
        raise Error("指标id不存在:{}".format(indicatorId))

    if not del_data(sqlPa="delete from fof_index_score where INDICATOR_ID = '%s' " % indicatorId):
        raise Error("删除历史数据失败，任务结束")

    iName = INDEX_CODE_NAME_CACHE[indicatorId]

    # fundAdjNav = getPublicData(['股票型', '混合型'])
    fundAdjNav = getPublicData()
    fundSymbols = list(fundAdjNav.columns)
    updatedType = []
    fundClass_1 = pd.Series('混合型基金', index=fundSymbols)
    fundClass_tmp = getData_fundInformation(fundSymbols)['FUND_INVESTTYPE']
    fundClass_1[fundClass_tmp.index] = fundClass_tmp
    for symbol in fundSymbols:
        indicators = []
        ranks = []
        fundType = fundClass_1[symbol]
        if fundType not in updatedType:
            for cycle in cycle_score:
                btParms = {'indexName': iName, 'cycle': cycle, 'symbol': symbol, 'sample': '一级',
                           'marketIndex': '',
                           'otherPar': ''}
                self = indexScore_fund(btParms, fundAdjNav, 'auto')
                op = self.output
                score = op['factorScore']
                rank = op['factorRank']
                # 这个值是用来记录当前cycle及分类下参与排名的样本数量，因为前端显示的排名都是5 / 200
                # 这种形式，本意是要存入数据库的，但我跟平赞沟通过了，他说他们前端直接根据数据库里的数据处理即可，不用存这个字段了
                # sc = op['sampleCounts']
                # tp = score
                # for ti in tp.index:
                #     tp[ti] = str(sc)
                indicators.append(score)
                ranks.append(rank)
                ranks.append(pd.Series())  # 一级分类排名样本
                ranks.append(pd.Series())  # 二级分类排名一期不上，先做个空值
                ranks.append(pd.Series())  # 二级分类排名样本一期不上，先做个空值
                updatedType.append(fundType)

        indicators.extend(ranks)
        df = pd.DataFrame(indicators).fillna('9999999999999.0')
        cols = df.columns.tolist()
        for col in cols:
            res = df[col]  # [基金id,score,score,...]
            lst = res.values.tolist()
            lst = [transformFloatIfAvaliable2(l) for l in lst]
            objId = uuid_util.gen_uuid()
            lst.insert(0, str(objId))
            lst.insert(1, str(indicatorId))
            lst.insert(2, col)
            # lst.insert(2, list(map(lambda x: x[-2:] + x[:-2], [col]))[0])
            date = formatDate2yyyymmdd()
            lst.insert(3, str(date))
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst.append("sys")
            lst.append(datetime.datetime.now())
            lst = ['9999999999999.0' if type(ele) == pd.Series else ele for ele in lst]
            tp = tuple(lst)
            sql = "INSERT INTO fof_index_score VALUES ( %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s,%s,0)"
            mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
        indicators.clear()
        ranks.clear()
