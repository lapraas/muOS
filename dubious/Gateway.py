
import asyncio
import json
from typing import Callable, Coroutine

from websockets import client

from dubious.raw import Payload

GATEWAY_URI = "wss://gateway.discord.gg/?v=9&encoding=json"

class Gateway:
    def __init__(self, uri: str, callback: Callable[[int, str, dict], Coroutine]):
        self.uri = uri
        self.callback = callback

        self.queue: asyncio.Queue[Payload] = asyncio.Queue()
        self.started = False
        self.ws: client.WebSocketClientProtocol = None
    
    async def start(self):
        self.ws = await client.connect(self.uri)
        loop = asyncio.get_running_loop()
        loop.create_task(self.loopClosed())
        loop.create_task(self.loopRecv())
        loop.create_task(self.loopSend())
        loop.run_forever()
    
    async def loopClosed(self):
        await self.ws.wait_closed()
        print("websocket closed\n" + f"  code: {self.ws.close_code}" + "\n" + f"  reason: {self.ws.close_reason}")
    
    async def loopRecv(self):
        data = await self.ws.recv()
        payload: Payload = json.loads(data)
        await self.callback(payload["op"], payload["t"], payload["d"])

    async def loopSend(self):
        payload = await self.queue.get()
        data = json.dumps(payload)
        await self.ws.send(data)
