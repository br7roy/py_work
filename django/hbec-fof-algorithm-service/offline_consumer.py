import pika

from util import uuid_util
from util.bus_const import TaskModel
from fof.model.model import OfflineTaskModel
from fof.service import logic_processor
import json
import importlib
from util import bus_const

#初始化常量
bus_const.load_table_info()
credentials = pika.PlainCredentials('guest','guest')
# connection = pika.BlockingConnection(pika.ConnectionParameters(host="192.168.30.61",credentials=credentials,heartbeat=0))
connection = pika.BlockingConnection(pika.ConnectionParameters(host="10.0.30.215",credentials=credentials,heartbeat=0))
# connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost",heartbeat=0))
channel = connection.channel()
channel.queue_declare(queue="offline_task_queue",durable=True)
channel.queue_bind(exchange='offline_task_exchange',
                   queue='offline_task_queue',
                   routing_key='offline_task-routingKey')

#处理已死的线程，帮助反馈给rabbitmq
def deal_deaded(ch,method):
    print("thread has deaded,I am send deaded message to rabbitmq")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback(ch,method,properties,body):
   #print("[X] Received %r" % (body.decode('utf-8'),))
    message = body.decode('utf-8')
    #message = body.decode()
    jsonobj = json.loads(message)
    task_model_name = jsonobj["mn"]
    task_service_name = jsonobj["sn"]
    task_service_file = jsonobj["sf"]

    indicatorId = ""
    if ("indicator_id" in jsonobj):
        indicatorId = jsonobj["indicator_id"]
    print("准备执行service层%r的%r方法" % (task_service_file,task_service_name))
    uuid = uuid_util.gen_uuid()
    task_model_name = getattr(TaskModel,task_model_name)
    service_class_name = importlib.import_module('fof.service.' + task_service_file)
    off_line_service = getattr(service_class_name,task_service_name)
    if indicatorId == "":
        model = OfflineTaskModel(task_model_name, off_line_service, "", uuid)
    else:
        model = OfflineTaskModel(task_model_name, off_line_service, "", uuid,indicatorId, "1")
    logic_processor.doLogic(model,)
    print("消费完成")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue="offline_task_queue",on_message_callback=callback)

print("Waiting for messages")
channel.start_consuming()
