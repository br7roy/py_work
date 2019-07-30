# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
import json
import simplejson
from rest_framework import viewsets
from rest_framework.views import APIView

from util.exception.biz_error_handler import Error


def hello(request):
    ctx = {}
    ctx['hello'] = 'hello world'
    ctx['c1'] = '0'
    ctx['c2'] = '0'

    ctx['lines'] = (1, 2, 3, 4, 5)
    ctx['section'] = 'sitenews'
    return render(request, 'hello.html', ctx)


# def page_not_found(request,Exception):
#     return render_to_response('404.html')


class CBV(APIView):
    '''
    def dispatch(self, request, *args, **kwargs):
        format = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
        print("dispatch......")
        try:
            res = super(CBV, self).dispatch(request, *args, **kwargs)
        except Exception as ex:
            # 全局日志异常处理
            import logging
            logger = logging.getLogger('hbec_fof')
            logger.warning(
                'Exception accrue method is (%s): %s', request.method, request.path,
                extra={'status_code': 500, 'request': request}
            )
            logger.exception('Exception is:', exc_info=ex)

            para = {'code': 999, 'msg': 'sysError'}
            ms0 = json.dumps(para)
            ms1 = simplejson.dumps(para)
            import sys
            para['msg'] = ex.args[0]

            from django.http import JsonResponse

            return HttpResponse(JsonResponse(para), content_type="application/json")
        return res
    '''

    def get(self, request):
        import logging
        logger = logging.getLogger("py_server")
        logger.info('记录日志成功。')

        pa = 1 / 0
        print(pa)
        # if 1 == 1:
        #     raise Exception("i made a exception.")
        return render(request, 'cbv.html')

    def post(selfs, request):
        return HttpResponse('cbv.get')


# 测试异常
class ErrorView(APIView):
    '''
        retrieve:
            Return a user instance.

        list:
            Return all users,ordered by most recent joined.

        create:
            Create a new user.

        delete:
            Remove a existing user.

        partial_update:
            Update one or more fields on a existing user.

        update:
            Update a user.
    '''

    def get(self, request):
        raise Error("参数错误")


# 测试API文档框架


class ConditionCompute(viewsets.ModelViewSet):
    '''
        retrieve:
            Return a user instance.

        list:
            Return all users,ordered by most recent joined.

        create:
            Create a new user.

        delete:
            Remove a existing user.

        partial_update:
            Update one or more fields on a existing user.

        update:
            Update a user.
    '''
    pass


def get(request, id):
    '''
        vote doc
    :param request:
    :return:
    '''
    get = request.GET
    nameval = request.GET['name']

    print(nameval)

    return None
