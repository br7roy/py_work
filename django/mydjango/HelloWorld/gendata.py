# -*- coding: utf-8 -*-
from .util import template_fundFactorEvaluation
from TestModel.models import Data
from django.http import HttpResponse


def gendata(request):
    res = template_fundFactorEvaluation.generateFundFactor('贝塔', '120', '普通股票型基金', '2014/1/1', '2018/12/31',
                                                           'fundQuarter', '2', '1', '5000',
                                                           '000906SH', marketIndex='000300SH')
    fundFactorEvaluation = res.fundFactorEvaluation
    for i in fundFactorEvaluation.iteritems():
        print(i)

    Data(avgIc=fundFactorEvaluation.values[0], avgAbsIc=fundFactorEvaluation.values[1],
         avgPositiveIc=fundFactorEvaluation.values[2], positiveIcRatio=fundFactorEvaluation.values[3],
         ir=fundFactorEvaluation.values[4], tStatistic=fundFactorEvaluation.values[5],
         gradingRankIC=fundFactorEvaluation.values[6], avgTurnOverRate=fundFactorEvaluation.values[7],
         medianTurnOverRate=fundFactorEvaluation.values[8], excessCumReturn_benchMark=fundFactorEvaluation.values[9],
         excessCumReturn_winAndLoss=fundFactorEvaluation.values[10],
         excessAnnualReturn_benchMark=fundFactorEvaluation.values[11],
         excessAnnualReturn_winAndLoss=fundFactorEvaluation.values[12]) \
        .save()
    print("save good")
    return HttpResponse("<h1>成功</h1>")
