from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread
from typing import Optional, Callable, Any, Iterable, Mapping

from fof.model.model import OfflineTaskModel
from fof.service import offline_value_service
from util.thread_tool import ThreadTool


def runnable(request, **kwargs):
    try:
        print('run')
        if 1 == 1:
            raise Exception("test")
    except Exception as e:
        print(e)

    print(request, kwargs)


def r2(request):
    print('r2')
    print(request)


def r3(task, param, **kwargs):
    return ThreadTool.pool.submit(task, (param,), kwargs=kwargs)


def r5(model):
    print("r5")
    print(model)


class EnchanceThread(Thread):

    def __init__(self, group: None = ..., target: Optional[Callable[..., Any]] = ..., name: Optional[str] = ...,
                 args: Iterable = ..., kwargs: Mapping[str, Any] = ..., *, daemon: Optional[bool] = ...) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)


if __name__ == '__main__':
    # pool = ThreadPoolExecutor(max_workers=100, thread_name_prefix='async_thread_pool')
    ThreadTool()
    #
    # request = 123123
    # uuid = 3
    # pool.submit(runnable, (request,), uuid=uuid)

    # task = r3(runnable, request, uuid=uuid)

    model = OfflineTaskModel("区间收益率", r5, None, None)
    # r3(r5, model)

    # pool.submit(r5, (model,))
    ThreadTool.add_task(r5, model)
