import json
import logging
from django.utils.deprecation import MiddlewareMixin
from util.exception.biz_error_handler import Error, make_error_response
from util.sys_constants import LOGGER_NAME, SYSTEM_ERROR_CODE, SYSTEM_ERROR_MSG

log = logging.getLogger(LOGGER_NAME)


class ServerEventAware(MiddlewareMixin):
    def __init__(self, get_response=None):
        log.info("------------------init")
        super().__init__(get_response)

    def process_request(self, request):
        param = ''
        if request.method != 'GET' and request.method != 'POST':
            raise Error("请求方法不支持")
        if request.method == 'GET':
            param = json.dumps(request.GET)
        if request.method == 'POST':
            param = json.loads(request.body.decode('utf-8'))
        log.info("requestInfo: method:[%s],url:[%s],param:[%s]", request.method, request.path_info, param)

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        # no view, RESTFUL only
        pass

    def process_response(self, request, response):
        log.info("responseInfo:%s", str(response.content, 'utf-8'))
        return response

    def process_exception(self, request, exc):

        if exc is None:
            return

        if type(exc) is Error:
            return exc.get_response()
        else:
            log.exception(SYSTEM_ERROR_MSG)
            return make_error_response(SYSTEM_ERROR_CODE, None, exception=exc)
