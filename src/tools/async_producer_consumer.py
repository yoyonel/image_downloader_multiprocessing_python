"""
from: https://github.com/yoyonel/asyncio_producer_consumer/blob/master/src/yoyonel/async_producer_consumer/async_producer_consumer.py
"""
import asyncio
import logging
from asyncio import Future, Queue
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict

logger = logging.getLogger(__name__)


@dataclass(frozen=True, init=True, unsafe_hash=False, repr=False, eq=False)
class ASyncProducerConsumer(object):
    @dataclass(frozen=True, init=True, unsafe_hash=False, repr=False, eq=False)
    class ProducerConsumer(object):
        future: Future
        queue: asyncio.Queue

    __producers_consumers: Dict = field(default_factory=dict)

    def add(self,
            name: str,
            queue: asyncio.Queue,
            func_consumer: Callable[..., Awaitable]):
        """

        :param name:
        :param queue:
        :param func_consumer:
        :return:
        """
        future_on_consumer = asyncio.ensure_future(func_consumer())
        self.__producers_consumers[name] = self.ProducerConsumer(
            future=future_on_consumer,
            queue=queue,
        )

    async def join(self):
        for producer_consumer in self.__producers_consumers.values():
            await producer_consumer.queue.join()

    def cancel(self):
        for producer_consumer in self.__producers_consumers.values():
            producer_consumer.future.cancel()


def request_for_cancelling_all_tasks(loop):
    """

    https://stackoverflow.com/questions/37417595/graceful-shutdown-of-asyncio-coroutines

    :param loop:
    :return:
    """
    # Optionally show a message if the shutdown may take a while
    logger.info("[{}] Attempting graceful shutdown ⌛".format(id(loop)))

    # Do not show `asyncio.CancelledError` exceptions during shutdown
    # (a lot of these may be generated, skip this if you prefer to see them)
    def shutdown_exception_handler(_loop, context):
        if "exception" not in context or not isinstance(context["exception"],
                                                        asyncio.CancelledError):
            _loop.default_exception_handler(context)

    loop.set_exception_handler(shutdown_exception_handler)

    # Handle shutdown gracefully by waiting for all tasks to be cancelled
    tasks = asyncio.gather(*asyncio.Task.all_tasks(loop=loop), loop=loop,
                           return_exceptions=True)
    tasks.add_done_callback(lambda t: loop.stop())
    tasks.cancel()


async def do_shutdown(loop):
    """

    https://pythonexample.com/code/asyncio-cancel-all-tasks/

    :param loop:
    :return:
    """
    tasks = [
        task
        for task in asyncio.all_tasks()
        if task is not asyncio.current_task()
    ]
    list(map(lambda task: task.cancel(), tasks))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info(
        'finished awaiting cancelled tasks, results: {0}'.format(results))
    loop.stop()


async def generic_consumer(
        queue_input: Queue,
        queue_output: Queue,
        func_apply_on_item: Callable,
        loop=None,
):
    while True:
        # wait for an item from the producer
        item = await queue_input.get()
        #
        try:
            item_processed = func_apply_on_item(item)
        except Exception as e:
            if loop is None:
                loop = asyncio.get_event_loop()
            loop.call_exception_handler({
                'message': 'Exception occurred in Consumer function apply',
                'exception': e,
            })
        else:
            await queue_output.put(item_processed)
        finally:
            queue_input.task_done()


async def async_consumer(
        queue_input: Queue,
        queue_output: Queue,
        async_func_apply_on_item: Callable,
        loop=None,
):
    while True:
        # wait for an item from the producer
        item = await queue_input.get()
        #
        try:
            item_processed = await async_func_apply_on_item(item)
        except Exception as e:
            if loop is None:
                loop = asyncio.get_event_loop()
            loop.call_exception_handler({
                'message': 'Exception occurred in Consumer function apply',
                'exception': e,
            })
        else:
            await queue_output.put(item_processed)
        finally:
            queue_input.task_done()
