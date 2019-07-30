import logging
import time

from conf import mysqlops
from conf.data_source import MysqlConf
from fof.algorithm.perEvalFunction import *
from fof.model.model import OfflineTaskModel
from util.bus_const import TaskStatus
from util.date_util import compute_time
from util.exception.biz_error_handler import Error
from util.sys_constants import LOGGER_NAME, OPEN_PREVENT_DUPLICATION

log = logging.getLogger(LOGGER_NAME)


def doLogic(model: OfflineTaskModel):
    #model = model[0]
    model = model
    start_time = time.time()
    taskType = model.taskType
    uuid = model.uuid
    taskModel = model.taskModel
    func = model.func

    if model.extVal is not None:
        res = mysqlops.fetch_one(MysqlConf.DB.fof,
                                 "select indicator_name from fof_index where indicator_code ='" + model.extVal + "'")
        if res is None:
            raise Error("指标id不存在:{}".format(model.extVal))

        taskName = res['indicator_name'].decode("utf-8")
        model.otherIndexName = taskName
    else:
        taskName = taskModel.value[0]

    if OPEN_PREVENT_DUPLICATION == 'False' : # 如果开启了任务防重就做判断拦截
        sql = "select task_status " \
              "from fof_task " \
              "where DATE(UPDATE_TIME) = CURRENT_DATE() " \
              "AND task_name='{}' " \
              "AND task_type='{}' " \
              "AND task_status in (0,1)" \
            .format(taskName, taskType)
        res = mysqlops.fetch_one(MysqlConf.DB.fof, sql)
        if res:
            log.warning("taskName:{},taskType:{},今天的任务处理状态为{},不需要再做处理".format(taskName, taskType, res))
            return

    sql = "INSERT INTO fof_task VALUES ( %s, %s, %s, %s,%s ,%s,%s)"
    tp = (
        uuid, taskName, taskType, TaskStatus.accept.value[0], "", datetime.now(), datetime.now())
    mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)
    log.info("taskType:%s,taskName:%s,开始 查询流水号:%s" % (taskType, taskName, uuid))
    try:
        func(model)
    except Exception as e:
        log.exception("未知异常:\n")
        sql = "update fof_task set task_status=%s,error_msg = %s,update_time = %s   where task_id = %s"
        tp = (TaskStatus.fail.value[0], str(e), datetime.now(), uuid)
        mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)

        hours, minutes, seconds = compute_time(start_time)

        log.error("taskType:%s,taskName:%s,出错 %s,查询流水号:%s,耗时: %s" % (
            taskType, taskName, e, uuid, "{:>02d}:{:>02d}:{:>02d}".format(hours, minutes, seconds)))
        return
    sql = "update fof_task set task_status=%s,update_time = %s   where task_id = %s"
    tp = (TaskStatus.ok.value[0], datetime.now(), uuid)
    mysqlops.insert_one(MysqlConf.DB.fof, sql, tp)

    hours, minutes, seconds = compute_time(start_time)
    log.info("taskType:%s,taskName:%s,成功,查询流水号:%s,耗时: %s" % (
        taskType, taskName, uuid, "{:>02d}:{:>02d}:{:>02d}".format(hours, minutes, seconds)))

