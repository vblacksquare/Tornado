# Tornado
Just a small lib implementing obj for a tasks.

## Usage
```python
import asyncio
from tornado import Tornado


async def main():
    tornado = Tornado()
    await tornado.add_item(0)
    await tornado.add_item()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
```
