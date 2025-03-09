# Tornado
Just a small lib implementing obj for a tasks.

## Usage
```python
import asyncio
from tornado import Tornado


async def callback(value):
    print("Its my value that I am getting 1 time per second")


async def main():
    tornado = Tornado()
    await tornado.add_item(0)
    await tornado.del_item(0)
    
    await tornado.add_item({"id": 1})
    await tornado.del_item(1, lambda x: x['id'])


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
```
