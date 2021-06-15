
import asyncio
import json
from typing import Callable, Coroutine, Optional

from websockets import client

from dubious.raw import Payload

GATEWAY_URI = "wss://gateway.discord.gg/?v=9&encoding=json"

class Gateway:
    def __init__(self, uri: str):
        self.uri = uri

        self.sendQ: asyncio.Queue[Payload] = asyncio.Queue()
        self.recvQ: asyncio.Queue[Payload] = asyncio.Queue()
        self.started = asyncio.Event()
        self.ws: client.WebSocketClientProtocol = None
        self.closedTask: Optional[asyncio.Task] = None
        self.recvTask: Optional[asyncio.Task] = None
        self.sendTask: Optional[asyncio.Task] = None
    
    async def start(self):
        self.ws = await client.connect(self.uri)
        self.started.set()
        loop = asyncio.get_running_loop()
        self.closedTask = loop.create_task(self.loopClosed())
        self.recvTask = loop.create_task(self.loopRecv())
        self.sendTask = loop.create_task(self.loopSend())
    
    async def loopClosed(self):
        await self.ws.wait_closed()
        print("websocket closed\n" + f"  code: {self.ws.close_code}" + "\n" + f"  reason: {self.ws.close_reason}")
    
    async def loopRecv(self):
        while self.started.is_set():
            data = await self.ws.recv()
            payload: Payload = json.loads(data)
            print(f"R: {json.dumps(payload, indent=2)}")
            await self.recvQ.put(payload)

    async def loopSend(self):
        while self.started.is_set():
            payload = await self.sendQ.get()
            data = json.dumps(payload)
            print(f"S: {json.dumps(payload, indent=2)}")
            await self.ws.send(data)
    
    async def recv(self):
        return await self.recvQ.get()
    
    async def send(self, payload: Payload):
        await self.sendQ.put(payload)
    
    async def stop(self, code=1000):
        self.started.clear()
        await asyncio.wait_for(self.closedTask)
        await asyncio.wait_for(self.recvTask)
        await asyncio.wait_for(self.sendTask)
        await self.ws.close(code)

    async def restart(self):
        await self.stop()
        await asyncio.sleep(2)
        await self.start()
