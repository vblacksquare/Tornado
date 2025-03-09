# Tornado
Just a small lib implementing obj for a tasks.

## Usage
```python
import asyncio
from tornado_obj import Tornado


async def callback(value):
    print(f"Its my value {value} that I am getting 1 time per second")


async def main():
    tornado = Tornado(callback=callback, length=1000, per_one=1)
    await tornado.add_item(0)
    await tornado.del_item(0)
    
    await tornado.add_item({"id": 1})
    
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
```
