
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
                self.log.debug(f"Waiting {round(timeout, 1)} seconds to make task 1/s")
                await asyncio.sleep(1.0 - dif)

            self.log.debug(f"Created task with {value_id} and delay {delay}")
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
        length: int,
        callback: typing.Callable
    ):

        self.log = logger.bind(classname=self.__class__.__name__)

        self.__length = length
        self.__callback = callback

        self.__main_task = None

        self.__values = []
        self.__queue: list[TornadoItem] = [
            TornadoItem(
                id=i,
                callback=self.__completed_item,
                value_callback=self.__value_callback
            )
            for i in range(self.__length)
        ]

    @property
    def speeedies(self):
        return [item.speeedy for item in self.__queue]

    async def add_item(self, value):
        try:
            await self.__drop()
            self.__values.append(value)
            await self.__update_queue()

            self.log.debug(f"Added new value -> {value}")

        except Exception as err:
            self.log.exception(err)

    async def del_item(self, value_id: str):
        try:
            await self.__drop()
            await self.__update_queue()

            self.log.debug(f"Removed value -> {value_id}")

        except Exception as err:
            self.log.exception(err)

    async def __drop(self):
        try:
            for item in self.__queue:
                await item.drop()

            self.log.debug(f"Dropped {len(self.__queue)} queue items")

        except Exception as err:
            self.log.exception(err)

    async def __update_queue(self):
        try:
            if not len(self.__values):
                self.log.warning(f"Can't update with no values")
                return

            for item in self.__queue:
                j = item.id % len(self.__values)
                k = item.id // len(self.__values)

                await item.do(
                    value_id=j,
                    delay=(len(self.__values) / self.__length) * k
                )

            self.log.debug(f"Updated {len(self.__queue)} queue items with {len(self.__values)} values")

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
