import os
import datetime

# 系统错误返回码
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYSTEM_ERROR_CODE = 999
SYSTEM_ERROR_MSG='系统异常'
# 项目名
PROJECT_NAME = 'py_server'
# 日志路径
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
