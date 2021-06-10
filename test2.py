
import asyncio

import nest_asyncio
nest_asyncio.apply()

import dubious

async def callback(a, b, c):
    print(a, b, c)

g = dubious.Gateway(dubious.GATEWAY_URI, callback)
asyncio.get_event_loop().run_until_complete(g.start())