"""hbec_fof_algorithm_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
# 导入辅助函数get_schema_view
from rest_framework.schemas import get_schema_view
# 导入两个类
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

from fof.view import offline_value_view, offline_score_view, online_view, offline_manager_view, offline_index_view

router = routers.DefaultRouter()
# 利用辅助函数引入所导入的两个类
schema_view = get_schema_view(title='算法系统接口文档', renderer_classes=[SwaggerUIRenderer, OpenAPIRenderer])

urlpatterns = [
    url(r'^$', schema_view),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # 离线计算指标评价
    # 区间收益率
    path(r'offline/value/intervalYield', offline_value_view.intervalYield),
    # 年华波动率
    path(r'offline/value/volatility', offline_value_view.volatility),
    # 夏普比率
    path(r'offline/value/sharpeRatio', offline_value_view.sharpeRatio),
    # 最大回撤
    path(r'offline/value/maximumDrawdown', offline_value_view.maximum_drawdown),
    # 卡玛比率
    path(r'offline/value/calmarRatio', offline_value_view.calmar_ratio),
    # 信息比率
    path(r'offline/value/informationRatio', offline_value_view.information_ratio),
    # 其他指标
    path(r'offline/value/otherIndicator', offline_value_view.other_indicator),

    # 离线计算指标打分和排名
    path(r'offline/score/indicatorScoreRank', offline_score_view.indicator_score_rank),

    # 离线计算基金经理股票择时能力评价
    path(r'offline/manager/equityTiming', offline_manager_view.equ_timing),

    # 离线计算基金经理行业配置能力-权益类基金单季十大重仓股配置分布
    path(r'offline/manager/industryConfigurationCapability/industry', offline_manager_view.industry_config_indust),
    path(r'offline/manager/industryConfigurationCapability/score', offline_manager_view.industry_config_score),
    path(r'offline/manager/industryConfigurationCapability/avgscore', offline_manager_view.industry_config_avgscore),

    # 基金经理股票筛选能力
    path(r'offline/manager/stockScreeningAbility/returnTotal', offline_manager_view.return_total),
    path(r'offline/manager/stockScreeningAbility/returnWeight', offline_manager_view.return_weight),
    path(r'offline/manager/stockScreeningAbility/return', offline_manager_view.return_),
    path(r'offline/manager/stockScreeningAbility/returnHis', offline_manager_view.return_his),

    # 基金净值风格划分
    path(r'offline/manager/styleAnalyze/NetValue', offline_manager_view.net_value),
    # 能力分析-持股集中度、换手率
    path(r'offline/manager/styleAnalyze/handTurnoverRate', offline_manager_view.hand_turn_over),
    # 能力分析-持仓风格10大重仓因子
    path(r'offline/manager/styleAnalyze/holdingStyleMain', offline_manager_view.holding_style_main),
    # 能力分析-持仓风格全部持仓因子
    path(r'offline/manager/styleAnalyze/holdingStyleAll', offline_manager_view.holding_style_all),

    # 风险因子业绩归因模块 fof_single_attr_riskmodel
    path(r'offline/index/riskSingle', offline_index_view.risk_single),
    # 风险因子业绩归因模块 fof_multi_attr_riskmodel
    path(r'offline/index/riskMultiple', offline_index_view.risk_multiple),


    # 基金经理产品
    path(r'offline/manager/managerProduct', offline_manager_view.compute_manager_product),
    # 导入因子库
    path(r'offline/index/stockexpousre', offline_index_view.stockexpousre),













    # 实时


    # 实时计算综合评分
    path(r'online/score/comprehensive', online_view.comprehensive),

    # 实时的以多个基金多个指标值任意时间为条件的价值计算
    path(r'online/value/multipleFundIndicator', online_view.multiple_value),



]
