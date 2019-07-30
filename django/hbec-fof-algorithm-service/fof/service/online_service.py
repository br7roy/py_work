"""
这个文件处理实时任务
1.实时计算综合打分
2.实时计算多指标多基金任意起止时间的收益计算
"""
from fof.algorithm.template_indexPerVal import indexPerVal
from fof.model.model import OnlineTaskModel
from util.bus_const import INDEX_CODE_NAME_CACHE


def exTractVal(indicator, fundCodes, startDate, endDate):
    dd = {}
    for f in fundCodes:
        for k, v in f.items():
            if v not in dd.keys():
                dd.update({v: [k]})
            else:
                dd[v].append(k)

    iName = INDEX_CODE_NAME_CACHE[indicator]

    res = {}
    for mIdx, symbols in dd.items():
        btParms = {'indexName': iName, 'cycle': startDate + "," + endDate, 'symbol': symbols,
                   'marketIndex': mIdx, 'otherPar': '0.05'}
        self = indexPerVal(btParms)
        output_json = self.output_json
        value_ = output_json['factorValue']
        vv = {}.fromkeys(symbols, '')
        if value_ is None or value_ == '':
            continue
        else:
            vv.update({k: v if v else {} for k, v in value_.items()})
        res.update(vv)

    return {"indicator": indicator, "value": res}


def multipleIndicatorValue(model: OnlineTaskModel):
    indicators = model.indicators
    fundCodes = model.fundCodes
    startDate = model.startDate
    endDate = model.endDate

    rr = [exTractVal(indicator, fundCodes, startDate, endDate) for indicator in indicators if
          indicator in INDEX_CODE_NAME_CACHE]

    return {"output": rr}
