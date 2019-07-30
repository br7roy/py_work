import json
import logging
import time

from django.utils.deprecation import MiddlewareMixin

from conf.data_source import MysqlConf
from util.bus_const import load_cache
from util.date_util import compute_time
from util.exception.biz_error_handler import Error, make_error_response
from util.sys_constants import LOGGER_NAME, SYSTEM_ERROR_CODE, SYSTEM_ERROR_MSG
from util.thread_tool import ThreadTool

log = logging.getLogger(LOGGER_NAME)


class ServerEventAware(MiddlewareMixin):
    def __init__(self, get_response=None):
        log.info("starting create database pool.")
        conf = MysqlConf()
        log.info("\r\n"
                 "database pool created.\r\n"
                 "Using :\r\n"
                 "from conf import mysqlops,\r\n"
                 + str(conf))

        ThreadTool()

        load_cache()

        super().__init__(get_response)

    def process_request(self, request):
        start = time.time()
        param = ''
        if request.method != 'GET' and request.method != 'POST':
            raise Error("请求方法不支持")
        if request.method == 'GET':
            param = json.dumps(request.GET)
        if request.method == 'POST':
            param = json.dumps(request.POST)
            if param == '{}' or param == None:
                param = request.body.decode()
            # try:
            #     param = json.loads(request.body.decode('utf-8'))
            # except ValueError as e:
            #     param = str(request.body, 'utf-8')
        self.start = start
        log.info("requestInfo: method:[%s],url:[%s],param:[%s]", request.method, request.path_info, param)

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        # no view, RESTFUL only
        pass

    def process_response(self, request, response):
        hours, minutes, seconds = compute_time(self.start)
        log.info("responseInfo:%s cost:%s", str(response.content, 'utf-8'),
                 "{:>02d}:{:>02d}:{:>02d}".format(hours, minutes, seconds))
        return response

    def process_exception(self, request, exc):

        if exc is None:
            return

        if type(exc) is Error:
            return exc.get_response()
        else:
            log.exception("\r\n" + SYSTEM_ERROR_MSG)
            return make_error_response(SYSTEM_ERROR_CODE, None, exception=exc)
