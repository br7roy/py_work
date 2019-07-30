import configparser
import datetime
import json
import os

# 系统错误返回码

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配置文件路径
CONF_PATH = BASE_DIR + '/hbec-fof-conf.ini'
cf = configparser.ConfigParser()
cf.read(CONF_PATH)  # 读取配置文件

items = cf.items("flag")
res = dict(items)

OPEN_PREVENT_DUPLICATION = res['allow_duplicate']

SYSTEM_SUCCESS_CODE = '000'
SYSTEM_SUCCESS_MSG = 'ok'
SYSTEM_ERROR_CODE = '999'
SYSTEM_ERROR_MSG = '系统异常'

# 项目名
PROJECT_NAME = 'py_server'
# 日志存储路径
LOG_PATH = os.path.join(BASE_DIR, 'logs/')
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# 日志前綴
LOG_PREFIX = 'py_server'
# logger name
LOGGER_NAME = 'py_server'
# 日志後綴
LOG_SUFFIX = '_%s.log'
# 时间格式
TIME_FORMAT_PATTERN = (datetime.datetime.now().strftime('%Y-%m-%d'))
# 日志格式
LOG_PATTERN = '%(levelname)s %(asctime)s %(thread)d %(threadName)s %(filename)s %(funcName)s %(lineno)d: %(message)s'

SUCCESS_RESP = {'code': SYSTEM_SUCCESS_CODE, 'message': SYSTEM_SUCCESS_MSG}


def convert_to_dict(obj):
    d = {}
    if obj is None:
        return d
    d.update(obj.__dict__)
    return d


def enchance_dict(ob):
    if ob is None:
        return ob
    ob.update(ok.__dict__)
    return ob


class BaseView:
    def __init__(self):
        self.code = SYSTEM_SUCCESS_CODE
        self.message = SYSTEM_SUCCESS_MSG

    def __str__(self) -> str:
        return "code:" + self.code + "msg:" + self.message


class OffLineView(BaseView):
    def __init__(self, jobId):
        super().__init__()
        self.jobId = jobId

    def __str__(self) -> str:
        return '离线返回jobId %s' % self.jobId


class ComposeScoreView(BaseView):

    def __init__(self, score):
        super().__init__()
        self.score = score


def json_dump(obj):
    return json.dumps(obj, default=convert_to_dict)


ok = BaseView()
