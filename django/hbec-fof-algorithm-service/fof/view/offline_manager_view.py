import logging

from bunch import Bunch
from django.http import JsonResponse
from rest_framework.decorators import api_view

from fof.model.model import OfflineTaskModel
from fof.service import logic_processor, manager_service
from fof.service import offline_score_service
from util import uuid_util
from util.bus_const import TaskModel
from util.exception.biz_error_handler import Error
from util.sys_constants import LOGGER_NAME, OffLineView, convert_to_dict
from util.thread_tool import ThreadTool

logger = logging.getLogger(LOGGER_NAME)


@api_view(['POST'])
def compute_manager_product(request, format=None):
    """
    计算基金经理管理的产品信息
    :param request:
    :return:
    """

    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jinglichanpin, manager_service.compute_manager_product, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def equ_timing(request):
    """
    基金经理股票择时能力评价模型
    请于每季结束后的第一个月的15日开始运行本程序(即基金季报发布)，按日更新，运行至该月末
    如1季度结束后，于4月15日~4月30日每日更新该数据
    :param request:
    :return:
    """

    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliNengli, manager_service.equ_timing, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def industry_config_indust(request):
    """
    离线计算基金经理行业配置能力
    :keyword 表 fof_fund_stock_industry
    请于每季结束后的第一个月的15日开始运行本程序(即基金季报发布)，按日更新，运行至该月末
    如1季度结束后，于4月15日~4月30日每日更新该数据
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliPeizhiNengli_stock, manager_service.industry_config_indust, request, uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def industry_config_score(request):
    """
    离线计算基金经理行业配置能力
    :keyword 表 fof_fund_industry_score
    请于每季结束后的第一个月的15日开始运行本程序(即基金季报发布)，按日更新，运行至该月末
    如1季度结束后，于4月15日~4月30日每日更新该数据
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliPeizhiNengli_score, manager_service.industry_config_score, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def industry_config_avgscore(request):
    """
    离线计算基金经理行业配置能力
    :keyword 表 fof_fund_industry_avgscore
    请于每季结束后的第一个月的15日开始运行本程序(即基金季报发布)，按日更新，运行至该月末
    如1季度结束后，于4月15日~4月30日每日更新该数据
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliPeizhiNengli_avgscore, manager_service.industry_config_avgscore, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


# 筛选能力

@api_view(['POST'])
def return_total(request):
    """
    基金经理股票筛选能力
    table: fof_fund_excess_return_total
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliShaixuanNengli_return_total, manager_service.return_total, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def return_weight(request):
    """
    基金经理股票筛选能力
    fof_fund_excess_return_weight
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliShaixuanNengli_return_weight, manager_service.return_weight, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def return_(request):
    """
    基金经理股票筛选能力
    table:  fof_fund_main_stock_return
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliShaixuanNengli_return, manager_service.return_, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def return_his(request):
    """
    基金经理股票筛选能力
    table:  fof_fund_main_stock_return_his
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jingliShaixuanNengli_return_his, manager_service.return_his, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


@api_view(['POST'])
def net_value(request):
    """
    基金净值风格划分        fof_fundnav_style
    考虑到服务器的承载能力，该程序前期可每周更新，后续服务器运载能力加大，可改为每日更新
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jinglifengge_profit_style, manager_service.net_value, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))

@api_view(['POST'])
def hand_turn_over(request):
    """
    能力分析-持股集中度、换手率  fof_fund_stock_porfolio


    该程序于每半年进行一次更新
    请于每年的3月20日~3月31日以及8月20日~8月31日更新
    由于程序运行量不大，若更新时间配置麻烦，可设定为每日更新
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jinglifengge_hand_change_rate, manager_service.hand_turn_over, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))

@api_view(["POST"])
def holding_style_main(request):
    """
    风格分析-持仓风格   fof_fund_tentop_stock_style

    重仓股数风格暴露数据，请于每季结束后的第一个月的15日开始运行本程序，按日更新，运行至该月末
    全部持仓数据，请于每年的8月21日~8月31日，以及3月21日~3月31日运行
    :param request:
    :return:
    """
    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jinglifengge_holding_stype_main, manager_service.holding_style_main, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))


def holding_style_all(request):
    """
        风格分析 - 持仓风格
    fof_fund_stock_style
    :param request:
    :return:
    """

    uuid = uuid_util.gen_uuid()

    model = OfflineTaskModel(TaskModel.jinglifengge_holding_stype_all, manager_service.holding_style_all, request,
                             uuid)

    ThreadTool.pool.submit(logic_processor.doLogic, (model,))

    view = OffLineView(uuid)

    return JsonResponse(convert_to_dict(view))