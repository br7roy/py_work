import pika
import sys
sys.path.append("D:\\workspace\\hbec-fof-algorithm-service\\hbec_fof_algorithm_service\\util\\uuid_util")

from util import uuid_util
from util.bus_const import TaskModel
from fof.model.model import OfflineTaskModel
from fof.service import logic_processor
from fof.service import offline_value_service
import threading
import json
import ctypes
import inspect



from concurrent.futures import ThreadPoolExecutor
import time

# credentials = pika.PlainCredentials('guest','guest')
# connection = pika.BlockingConnection(pika.ConnectionParameters(host="192.168.30.61",credentials=credentials,heartbeat=0))
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost",heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue="offline_task_queue")

def monical(ch,method):
    #模拟100%cpu
    print("起子线程")
    time1 = time.time()
    flag = True
    while flag:
        time2 = time.time()
        span = time2 - time1
        if span > 10:
            flag = False
    print("退出任务")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def _async_raise(tid, exctype):
 """raises the exception, performs cleanup if needed"""
 tid = ctypes.c_long(tid)
 if not inspect.isclass(exctype):
  exctype = type(exctype)
 res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
 if res == 0:
  raise ValueError("invalid thread id")
 elif res != 1:
  # """if it returns a number greater than one, you're in trouble,
  # and you should call it again with exc=NULL to revert the effect"""
  ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
  raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    print("停止子线程")
    _async_raise(thread.ident, SystemExit)


def kill_func(worker):
     print("killer starter")
     time.sleep(30)
     print("do killer")
     #开始杀掉worker
     stop_thread(worker)

#处理已死的线程，帮助反馈给rabbitmq
def deal_deaded(ch,method):
    print("thread has deaded,I am send deaded message to rabbitmq")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def thread_func(ch,method,body,model):
    #logic_processor.doLogic(model,)
    # 手动应答
    print("[X] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# def heart_beat(worker,ch,method):
#     while True:
#         time.sleep(30)
#         print("检测是否计算线程死掉")
#         if not worker.is_alive():
#             deal_deaded(ch, method)
#             break

def callback(ch,method,properties,body):
   # print("[X] Received %r" % (body.decode('utf-8'),))
    message = body.decode('utf-8')
    jsonobj = json.loads(message)
    task_model_name = jsonobj["mn"]
    task_service_name = jsonobj["sn"]
    task_service_file = jsonobj["sf"]


    indicatorId = ""
    if ("indicator_id" in jsonobj):
        indicatorId = jsonobj["indicator_id"]

    print("准备执行service层%r" % task_service_name)
    uuid = uuid_util.gen_uuid()
    task_model_name = getattr(TaskModel,task_model_name)
    service_class_name  = __import__(task_service_file)
    off_line_service = getattr(service_class_name,task_service_name)
    if indicatorId == "":
        model = OfflineTaskModel(task_model_name, off_line_service, "", uuid)
    else:
        model = OfflineTaskModel(task_model_name, off_line_service, "", uuid,indicatorId, "1")
    #启动长时间的任务线程执行
    # worker = threading.Thread(target=thread_func, args=(ch, method, body,model))
    logic_processor.doLogic(model)
    # time1 = time.time()
    # flag = True
    # while flag:
    #     time2 = time.time()
    #     span = time2 - time1
    #     if span > 28800:
    #         flag = False
    # print("退出任务")
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # worker = threading.Thread(target=monical, args=(ch, method))
    # worker.start()

    #启动模拟到时间杀死工作线程的线程
    # killer = threading.Thread(target=kill_func,args=(worker,))
    # killer.start()
    #p.submit(logic_processor.doLogic(model,)).add_done_callback(task_futre)

    #启动心跳线程，检测是否死掉
    # heart = threading.Thread(target=heart_beat,args=(worker,ch,method))
    # heart.start()

    # target = threading.Thread()
    # target.start()
    # while target.is_alive():
    #     time.sleep(1)
    #     connection.process_data_events()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="offline_task_queue",on_message_callback=callback)

print("Waiting for messages")
channel.start_consuming()
