
import asyncio
import json
from typing import Callable, Coroutine

from websockets import client

from dubious.raw import Payload

GATEWAY_URI = "wss://gateway.discord.gg/?v=9&encoding=json"

class Gateway:
    def __init__(self, uri: str):
        self.uri = uri

        self.sendQ: asyncio.Queue[Payload] = asyncio.Queue()
        self.recvQ: asyncio.Queue[Payload] = asyncio.Queue()
        self.started = False
        self.ws: client.WebSocketClientProtocol = None
    
    async def start(self):
        self.ws = await client.connect(self.uri)
        loop = asyncio.get_running_loop()
        loop.create_task(self.loopClosed())
        loop.create_task(self.loopRecv())
        loop.create_task(self.loopSend())
    
    async def loopClosed(self):
        await self.ws.wait_closed()
        print("websocket closed\n" + f"  code: {self.ws.close_code}" + "\n" + f"  reason: {self.ws.close_reason}")
    
    async def loopRecv(self):
        data = await self.ws.recv()
        payload: Payload = json.loads(data)
        print(f"R: {payload}")
        await self.recvQ.put(payload)

    async def loopSend(self):
        payload = await self.sendQ.get()
        data = json.dumps(payload)
        print(f"S: {data}")
        await self.ws.send(data)
    
    async def recv(self):
        return await self.recvQ.get()
    
    async def send(self, payload: Payload):
        await self.sendQ.put(payload)
