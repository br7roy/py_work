from django.http import JsonResponse
from util import sys_constants

'''
统一异常处理
'''


class Error(Exception):

    def __init__(self, message=u'服务器异常', e=None, code=sys_constants.SYSTEM_ERROR_CODE):
        self.code = code
        self.message = message
        self.exception = e

    def sys_error(self, code=sys_constants.SYSTEM_ERROR_CODE,
                  message=u'服务器异常'):
        self.code = code
        self.message = message

    def __unicode__(self):
        return u'[Error] %d: %s' % (self.code, self.message)

    def get_response(self):
        return make_error_response(self.code, self.message, self.exception)


def make_error_response(code, message, exception):
    msg = ''
    if message:
        msg += message
    if exception:
        msg += str(exception)
    err = {
        'code': code,
        'message': msg
    }
    return JsonResponse(err, json_dumps_params={'ensure_ascii': False})
