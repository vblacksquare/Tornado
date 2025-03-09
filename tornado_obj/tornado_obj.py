
from loguru import logger
import time
import asyncio
import typing

from speeedy import Speeedy


class TornadoItem:
    def __init__(
        self,
        id: int,
        callback: typing.Callable,
        value_callback: typing.Callable,
    ):

        self.speeedy = Speeedy()
        self.log = logger.bind(classname=self.__class__.__name__)

        self.id = id
        self.value_id = None
        self.delay = None

        self.value_callback = value_callback
        self.callback = callback

        self.task_created = 0
        self.task: asyncio.Task = None

    async def __do(
        self
    ):
        try:
            await asyncio.sleep(self.delay)

            self.task_created = time.time()
            await self.value_callback(value_id=self.value_id)
            self.speeedy.add()

            await self.callback(self)

        except Exception as err:
            self.log.exception(err)

    async def do(
        self,
        value_id: int,
        delay: float = 0.0
    ):

        try:
            self.value_id = value_id
            self.delay = delay

            dif = time.time() - self.task_created
            if dif < 1.0:
                timeout = 1.0 - dif
                await asyncio.sleep(timeout)

            if self.task:
                await self.__do()

            else:
                self.task = asyncio.create_task(self.__do())

        except Exception as err:
            self.log.exception(err)

    async def drop(
        self
    ):
        if self.task:
            self.task.cancel()
            self.task = None


class Tornado:
    def __init__(
        self,
        length: int = 0,
        callback: typing.Callable = lambda x: x,
        per_one: int = None
    ):

        self.log = logger.bind(classname=self.__class__.__name__)

        self.__length = length
        self.__per_one = per_one if per_one else self.__length

        self.__callback = callback

        self.__main_task = None

        self.__values = []
        self.__queue: list[TornadoItem] = []

    @property
    def speeedies(self) -> list[Speeedy]:
        return [item.speeedy for item in self.__queue]

    @property
    def length(self):
        return self.__length

    @property
    def per_one(self):
        return self.__per_one

    async def set_length(self, value: int):
        self.__length = value
        await self.__drop()
        await self.__update_queue()

    async def set_per_one(self, value: int):
        self.__per_one = value
        await self.__drop()
        await self.__update_queue()

    async def add_item(self, value):
        try:
            await self.__drop()
            self.__values.append(value)
            await self.__update_queue()

        except Exception as err:
            self.log.exception(err)

    async def del_item(self, by_value: str, func: typing.Callable = None):
        def default_func(x):
            return x

        if func is None:
            func = default_func

        try:
            await self.__drop()

            for i, value in enumerate(self.__values):
                if func(value) == by_value:
                    del self.__values[i]
                    break

            await self.__update_queue()

        except Exception as err:
            self.log.exception(err)

    async def __drop(self):
        try:
            for item in self.__queue:
                await item.drop()

        except Exception as err:
            self.log.exception(err)

    async def __update_queue(self):
        try:
            if not len(self.__values):
                self.log.warning(f"Can't update with no values")
                return

            self.__queue = [
                TornadoItem(
                    id=i,
                    callback=self.__completed_item,
                    value_callback=self.__value_callback
                )
                for i in range(self.__length)
            ]

            added_values = {}

            for item in self.__queue:
                j = item.id % len(self.__values)
                k = item.id // len(self.__values)

                if j not in added_values:
                    added_values.update({j: 0})

                if added_values[j] == self.__per_one:
                    continue

                await item.do(
                    value_id=j,
                    delay=(len(self.__values) / self.__per_one) * k
                )
                added_values[j] += 1

        except Exception as err:
            self.log.exception(err)

    async def __value_callback(self, value_id: str):
        try:
            await self.__callback(self.__values[value_id])

        except Exception as err:
            self.log.exception(err)

    async def __completed_item(self, queue_item: TornadoItem):
        await queue_item.do(
            value_id=(queue_item.value_id + 1) % len(self.__values)
        )
