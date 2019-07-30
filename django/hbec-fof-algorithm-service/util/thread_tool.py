from concurrent.futures import ThreadPoolExecutor


class ThreadTool:
    pool = None
    '''
    需要更改，内置sdk使用的是无界队列
    
    https://blog.51cto.com/walkerqt/2317632
    '''

    def __init__(self) -> None:
        ThreadTool.pool = ThreadPoolExecutor(max_workers=100, thread_name_prefix='async_thread_pool')

        super().__init__()

    @staticmethod
    def add_task(task, param, **kwargs):
        ThreadTool.pool.submit(task, (param,), kwargs=kwargs)
