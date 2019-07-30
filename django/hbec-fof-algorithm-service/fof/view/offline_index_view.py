import logging

from django.http import JsonResponse
from rest_framework.decorators import api_view

from fof.model.model import OfflineTaskModel
from fof.service import logic_processor, offline_index_service
from util import uuid_util
from util.bus_const import TaskModel
from util.sys_constants import LOGGER_NAME, OffLineView, convert_to_dict
from util.thread_tool import ThreadTool

logger = logging.getLogger(LOGGER_NAME)


@api_view(["GET", "POST"])
def stockexpousre(request):
    """
    导入因子库
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.stockexpousre, offline_index_service.stockexpousre, request, uuid)
    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(["GET", "POST"])
def risk_single(request):
    """
    风险因子业绩归因模块 fof_single_attr_riskmodel

    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.stockRiskSingle, offline_index_service.risk_single, request, uuid)
    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(["GET", "POST"])
def risk_multiple(request):
    """
    风险因子业绩归因模块 fof_multi_attr_riskmodel

    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()
    model = OfflineTaskModel(TaskModel.stockRiskMultiple, offline_index_service.risk_multiple, request, uuid)
    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))
