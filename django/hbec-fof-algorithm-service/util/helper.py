from util.bus_const import INDEX_NAME_CODE_CACHE
from util.exception.biz_error_handler import Error


def get_indicator_id(taskName):
    indi_id = INDEX_NAME_CODE_CACHE[taskName] if taskName in INDEX_NAME_CODE_CACHE.keys() else None
    if not indi_id:
        raise Error("指标不存在:{}".format(taskName))
    return indi_id
