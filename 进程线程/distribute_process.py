# 分布式进程
"""
在Thread和Process中，应当优选Process，因为Process更稳定，而且，
Process可以分布到多台机器上，而Thread最多只能分布到同一台机器的多个CPU上。

Python的multiprocessing模块不但支持多进程，其中managers子模块
还支持把多进程分布到多台机器上。一个服务进程可以作为调度者，将任务分布到其他多个进程中，
依靠网络通信。由于managers模块封装很好，不必了解网络通信的细节，就可以很容易地编
写分布式多进程程序。

举个例子：如果我们已经有一个通过Queue通信的多进程程序在同一台机器上运行，现在，由于
处理任务的进程任务繁重，希望把发送任务的进程和处理任务的进程分布到两台机器上。怎么用分布
式进程实现？

原有的Queue可以继续使用，但是，通过managers模块把Queue通过网络暴露出去，
就可以让其他机器的进程访问Queue了。

我们先看服务进程，服务进程负责启动Queue，把Queue注册到网络上，然后往Queue
里面写入任务：
"""
import random, time, queue

# 发送任务的队列：
task_queue = queue.Queue()
# 接受结果的队列：
result_queue = queue.Queue()


# 从BaseManager继承的QueueManager
class QueueManager(BaseManager):
    pass


# 把两个Queue都注册到网络上，callable参数关联了Queue对象：
QueueManager.register('get_task_queue', callable(lambda: task_queue))
QueueManager.register('get_result_queue', callable(lambda: result_queue))

# 绑定端口5000
manager = QueueManager(address=('', 5000), authkey = b'abc')

# 启动Queue:
manager.start()

# 获得通过网络访问的Queue对象
task = manager.get_task_queue()
result = manager.get_result_queue()

# 放几个任务进去
for i in range(100):
    n = random.randint(0,10000)
    print('Put task %d ...' % n)
    task.put(n)

# 从result队列读取结果：
print('Try get results...')
for i  in range(100):
    r = result.get(timeout=10)
    print('Result: %s' % r)

# 关闭
manager.shutdown()
print('master exit.')






















