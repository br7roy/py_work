import logging

from bunch import Bunch
from django.http import JsonResponse
from rest_framework.decorators import api_view

from fof.model.model import OfflineTaskModel
from fof.service import logic_processor
from fof.service import offline_value_service
from util import uuid_util
from util.bus_const import TaskModel
from util.exception.biz_error_handler import Error
from util.sys_constants import LOGGER_NAME, OffLineView, convert_to_dict
from util.thread_tool import ThreadTool

logger = logging.getLogger(LOGGER_NAME)


@api_view(['POST'])
def intervalYield(request):
    """
    离线计算区间收益率

    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.qujianshouyilv, offline_value_service.interval_yield, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, model)

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def volatility(request):
    """
    离线计算年化波动率
    :param request:
    :return:
    """

    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.nianhuabodonglv, offline_value_service.volatility, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def sharpeRatio(request):
    """
    离线计算夏普比率
    :param request:
    :return:
    """

    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.xiapubilv, offline_value_service.sharpe_ratio, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def maximum_drawdown(request):
    """
    离线计算最大回撤
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.zuidahuiche, offline_value_service.maximum_drawdown, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def calmar_ratio(request):
    """
    离线计算卡玛比率
    :param request:
    :return:
    """

    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.kamabilv, offline_value_service.calmar_ratio, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def information_ratio(request):
    """
    离线计算信息比率
    :param request:
    :return:
    """

    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.xinxibilv, offline_value_service.information_ratio, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def other_indicator(request):
    """
    离线计算其他指标
    :param request:
        : indicatorId: 指标Id
    :return:
    """

    req = request.data

    try:
        bun = Bunch(req)

        indicatorId = bun.indicatorId
    except:
        raise Error("indicatorId 不能为空")

    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.qitazhibiao, offline_value_service.other_indicator, request, uuid,
                             extVal=indicatorId)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))
