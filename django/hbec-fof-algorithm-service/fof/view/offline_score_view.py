import logging

from bunch import Bunch
from django.http import JsonResponse
from rest_framework.decorators import api_view

from fof.model.model import OfflineTaskModel
from fof.service import logic_processor
from fof.service import offline_score_service
from util import uuid_util
from util.bus_const import TaskModel
from util.exception.biz_error_handler import Error
from util.sys_constants import LOGGER_NAME, OffLineView, convert_to_dict
from util.thread_tool import ThreadTool

logger = logging.getLogger(LOGGER_NAME)


@api_view(['POST'])
def indicator_score_rank(request, format=None):
    """
    指标打分
    :param request:
           indicatorId    ： 指标id
           {"indicatorId": "1"}
    :return:
    """

    req = request.data
    logger.info("req:", req)

    try:
        m = Bunch(req)
        indicatorId = m.indicatorId
    except Exception as ae:
        raise Error("参数验证异常", ae)

    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.zhibiaodafen, offline_score_service.indicator_score_rank, request, uuid,
                             indicatorId, "1")

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))
