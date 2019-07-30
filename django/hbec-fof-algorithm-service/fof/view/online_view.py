import logging

from bunch import Bunch
from django.http import JsonResponse
from rest_framework.decorators import api_view

from fof.algorithm.template_singleIndexScore import compScore
from fof.model.model import OnlineTaskModel
from fof.service.online_service import multipleIndicatorValue
from util.exception.biz_error_handler import Error
from util.sys_constants import LOGGER_NAME, convert_to_dict, ComposeScoreView, enchance_dict

logger = logging.getLogger(LOGGER_NAME)


@api_view(['POST'])
def comprehensive(request):
    """
    实时计算综合评分
    :param request:
    {
    "fundBeans": [
        {
            "fundId": "1",
            "indicatorValue": [
                "0",
                "1",
                "2",
                "3",
                "4"
            ]
        },
        {
            "fundId": "2",
            "indicatorValue": [
                "0",
                "1",
                "2",
                "3",
                "4"
            ]
        },
        {
            "fundId": "3",
            "indicatorValue": [
                "0",
                "1",
                "2",
                "3",
                "4"
            ]
        },
        {
            "fundId": "4",
            "indicatorValue": [
                "0",
                "1",
                "2",
                "3",
                "4"
            ]
        },
        {
            "fundId": "5",
            "indicatorValue": [
                "0",
                "1",
                "2",
                "3",
                "4"
            ]
        }
    ],
    "weightList": [
        "1",
        "3",
        "5",
        "7",
        "9"
    ]
}
    :return
    {
    "code": "000",
    "msg": "ok",
    "score": [
        {
            "fundId": "1",
            "score": "1.0"
        },
        {
            "fundId": "2",
            "score": "2.0"
        },
        {
            "fundId": "3",
            "score": "3.0"
        },
        {
            "fundId": "4",
            "score": "4.0"
        },
        {
            "fundId": "5",
            "score": "5.0"
        }
    ]
}
    :return:
    """
    try:
        req = request.data
        # 计算综合打分
        sb = req['fundBeans']
        ws = req['weightList']
    except Exception as e:
        raise Error("请求参数格式错误，请确认 fundBeans,weightList")
    rr = [{"fundId": i['fundId'],
           "score": str(round(compScore({'factorScores': i['indicatorValue'], 'factorWeights': ws}), 2))}
          for i in sb]

    view = ComposeScoreView(rr)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def multiple_value(request):
    """
    实时的以多个基金多个指标值任意时间为条件的价值计算
    :param request:

{
    "fundCodes": [        {
            "001105.OF": "000906.SH"
        },
        {
            "002205.OF": "000906.SH"
        }],
    "startDate": "20100101",
    "endDate": "20180930",
    "indicators": ["1","2","3"]
}
{
    "output": [
        [
            "1",
            {
                "000001.OF": "0.11158127854784183",
                "001050.OF": ""
            }
        ],
        [
            "2",
            {
                "000001.OF": "-0.21151628503283265",
                "001050.OF": ""
            }
        ],
        [
            "3",
            {
                "000001.OF": "0.16420355957661825",
                "001050.OF": ""
            }
        ]
    ],
    "code": "000",
    "msg": "ok"
}
    :return:
    """
    try:
        req = request.data
        m = Bunch(req)
        indicators = m.indicators  # 指标ID
        fundCodes = m.fundCodes  # 基金代码,index集合   [ { "001105.OF": "000906.SH" }, { "002205.OF": "000906.SH" } ]
        startDate = m.startDate
        endDate = m.endDate
    except Exception as e:
        raise Error("请求参数错误, 请查看接口文档,%s" % str(e))

    mod = OnlineTaskModel(indicators, fundCodes, startDate, endDate)

    data = multipleIndicatorValue(mod)

    return JsonResponse(enchance_dict(data))
