# 使用同步方式编写异步功能
import time
import asyncio


@asyncio.coroutine  # 标志协程的装饰器
def taskIO_1():
    print('开始运行IO任务1...')
    yield from asyncio.sleep(2)  # 假设该任务耗时2s
    print('IO任务1已完成，耗时2s')
    return taskIO_1.__name__


@asyncio.coroutine  # 标志协程的装饰器
def taskIO_2():
    print('开始运行IO任务2...')
    yield from asyncio.sleep(3)  # 假设该任务耗时3s
    print('IO任务2已完成，耗时3s')
    return taskIO_2.__name__


@asyncio.coroutine  # 标志协程的装饰器
def main():  # 调用方
    tasks = [taskIO_1(), taskIO_2()]  # 把所有任务添加到task中
    done, pending = yield from asyncio.wait(tasks)  # 子生成器
    for r in done:  # done和pending都是一个任务，所以返回结果需要逐个调用result()
        print('协程无序返回值：' + r.result())


from django.views import View
import asyncio
import time
from django.http import JsonResponse


class TestAsyncioView(View):
    def get(self, request, *args, **kwargs):
        """
        利用asyncio和async await关键字（python3.5之前使用yield）实现协程
        """
        start_time = time.time()
        loop = asyncio.new_event_loop()  # 或 loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        self.loop = loop
        try:
            results = loop.run_until_complete(self.gather_tasks())
        finally:
            loop.close()
        end_time = time.time()
        return JsonResponse({'results': results, 'cost_time': (end_time - start_time)})

    async def gather_tasks(self):
        """
         也可以用回调函数处理results
        task1 = self.loop.run_in_executor(None, self.io_task1, 2)
        future1 = asyncio.ensure_future(task1)
        future1.add_done_callback(callback)

        def callback(self, future):
            print("callback:",future.result())
        """
        tasks = (
            self.make_future(self.io_task1, 2),
            self.make_future(self.io_task2, 2)
        )
        results = await asyncio.gather(*tasks)
        return results

    async def make_future(self, func, *args):
        future = self.loop.run_in_executor(None, func, *args)
        response = await future
        return response

    """
    # python3.5之前无async await写法
    import types
    @types.coroutine
    # @asyncio.coroutine  # 这个也行
    def make_future(self, func, *args):
        future = self.loop.run_in_executor(None, func, *args)
        response = yield from future
        return response
    """

    def io_task1(self, sleep_time):
        time.sleep(sleep_time)
        return 66

    def io_task2(self, sleep_time):
        time.sleep(sleep_time)
        return 77

from django.views import View
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestThreadView(View):
    def get(self, request, *args, **kargs):
        start_time = time.time()
        future_set = set()
        tasks = (self.io_task1, self.io_task2)
        with ThreadPoolExecutor(len(tasks)) as executor:
            for task in tasks:
                future = executor.submit(task, 2)
                future_set.add(future)
        for future in as_completed(future_set):
            error = future.exception()
            if error is not None:
                raise error
        results = self.get_results(future_set)
        end_time = time.time()
        return JsonResponse({'results': results, 'cost_time': (end_time - start_time)})

    def get_results(self, future_set):
        """
        处理io任务执行结果，也可以用future.add_done_callback(self.get_result)
        def get(self, request, *args, **kargs):
            start_time = time.time()
            future_set = set()
            tasks = (self.io_task1, self.io_task2)
            with ThreadPoolExecutor(len(tasks)) as executor:
                for task in tasks:
                    future = executor.submit(task, 2).add_done_callback(self.get_result)
                    future_set.add(future)
            for future in as_completed(future_set):
                error = future.exception()
                print(dir(future))
                if error is not None:
                    raise error
            self.results = results = []
            end_time = time.time()
            return JsonResponse({'results': results, 'cost_time': (end_time - start_time)})

        def get_result(self, future):
            self.results.append(future.result())
        """
        results = []
        for future in future_set:
            results.append(future.result())
        return results

    def io_task1(self, sleep_time):
        time.sleep(sleep_time)
        return 10

    def io_task2(self, sleep_time):
        time.sleep(sleep_time)
        return 66

# if __name__ == '__main__':
#     start = time.time()
#     loop = asyncio.get_event_loop()  # 创建一个事件循环对象loop
#     try:
#         loop.run_until_complete(main())  # 完成事件循环，直到最后一个任务结束
#     finally:
#         loop.close()  # 结束事件循环
#     print('所有IO任务总耗时%.5f秒' % float(time.time() - start))

def search_area(request):
    prints = PrintThread()
    prints.start()

    return retrieve(request, 'Area', 'areasearche.html', [{'name': 'areaname', 'mode': 'contains'}])

##通过thread 实现django中
import threading
import time
class PrintThread(threading.Thread):
    def run(self):
        print("start.... %s" % (self.getName(),))

        for i in range(30):
            time.sleep(1)
            print(i)
        print("end.... %s" % (self.getName(),))







