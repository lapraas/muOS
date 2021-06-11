
from __future__ import annotations

import asyncio
import inspect
import json
import sys
from typing import Callable, Coroutine, Optional, TypedDict, Union

import websockets

from dubious.raw import RawApplication, Hello, Ready, RawSnowflake, UnavailableGuild, RawUser

aloop = asyncio.get_event_loop()

class Snowflake:
    def __init__(self, raw: RawSnowflake):
        self.value = int(raw)
        self.timestamp = (self.value >> 22) + 1420070400000
        self.workerID = (self.value & 0x3E0000) >> 17
        self.processID = (self.value & 0x1F000) >> 12
        self.increment = self.value & 0xFFF

class User:
    def __init__(self, raw: RawUser):
        self.id = Snowflake(raw["id"])
        self.username = raw["username"]
        self.discriminator = raw["discriminator"]
        self.avatar = raw["avatar"]
        self.isBot = raw["bot"]
        self.system = raw["system"]
        self.usesTwoFactor = raw["mfa_enabled"]
        self.locale = raw["locale"]
        self.isVerified = raw["verified"]
        self.email = raw["email"]
        self.flags = raw["flags"]
        self.premiumType = raw["premium_type"]
        self.publicFlags = raw["public_flags"]

class Application:
    def __init__(self, raw: RawApplication):
        self.id = Snowflake(raw["id"])
        self.name = raw["name"]
        self.icon = raw["icon"]
        self.description = raw["description"]
        self.isPublic = raw["bot_public"]
        self.requiresAuth = raw["bot_require_code_grant"]
        self.owner = User(raw["owner"])

_Op = Union[int, str]
_Callback = Callable[[dict], Coroutine]
_Handlers = dict[_Op, _Callback]
class Requester:

    def __init__(self, gateway: str):
        self.gateway = gateway
        self.ws = None
        # The queue that controls when things get sent.
        self.queue = asyncio.Queue()
        self.handlers: _Handlers = {}
    
    def addHandler(self, op: _Op, cb: _Callback):
        self.handlers[op] = cb
    
    async def start(self):
        """ Starts the loops. """

        async with websockets.connect(self.gateway) as ws:
            loop = asyncio.get_event_loop()
            self.ws = ws
            loop.create_task(self.recvLoop())
            loop.create_task(self.sendLoop())
            loop.run_forever()
    
    async def recvLoop(self):
        """ Loop for recieving json payloads from the websocket. """

        while True:
            if self.ws.closed:
                raise Exception(f"fuck, {self.ws.close_code}")
            print("waiting to recieve")
            res = await asyncio.wait_for(self.ws.recv(), timeout=10)
            payload = json.loads(res)
            print(f"recieved {payload}")
            op = payload["op"]
            d = payload["d"]
            if op == 0:
                t = payload["t"]
                await self._handle(t, d)
            else:
                await self._handle(op, d)

    async def sendLoop(self):
        """ Loop for sending json payloads to the websocket. """

        while True:
            payload = await self.queue.get()
            print(f"sending  {payload}")
            await self.ws.send(json.dumps(payload))
    
    async def _handle(self, op: Union[str, int], payload: dict):
        if not op in self.handlers:
            raise Exception("Unimplemented op")
        else:
            cb = self.handlers[op]
            await cb(payload)
    
    async def add(self, payload):
        await self.queue.put(payload)

class Client:
    def __init__(self, *, token: str, intents: int, req: Requester):
        # The client's secret.
        self.token = token
        # The intents for the client.
        self.intents = intents
        # The connection to the websocket through which to recieve and request information.
        self.req = req

        self.req.addHandler(10, self.onHello)
        #self.req.addHandler(11, self.onHelloAck)
        self.req.addHandler("READY", self.onReady)

        # The time between heartbeats in milliseconds.
        self.beatTime: Optional[int] = None
        # Whether or not a HeartbeatAck event has been recieved since the last heartbeat.
        # Starts as true for the first heartbeat.
        self.beatAcked = True
        # Whether or not the heartbeat loop is active.
        self.beating = False
        # Whether or not the connection has been temporarily closed and heartbeats have stopped.
        self.paused = True

        # Whether or not the Client has recieved the Ready event.
        self.ready = False
        # The version of the gateway api being used.
        self.gatewayVersion: Optional[int] = None
        self.user: Optional[User] = None
        self.sessionID: Optional[str] = None
        self.application: Optional[Application] = None
        self.guildIDs: Optional[list[UnavailableGuild]] = None
    
    async def start(self):
        await self.req.start()

    async def startHeartbeat(self, heartbeatTime: int):
        """ Starts the heartbeat loop. """

        self.beatTime = heartbeatTime
        if self.beating:
            raise Exception("beat called")
        await self.req.add({
            "op": 1,
            "d": None
        })
        asyncio.get_event_loop().create_task(self.beat())
    
    async def beat(self):
        """ The heartbeat loop.
            Adds a Heartbeat payload to the queue every heartbeat interval if the client's connection isn't paused,
            otherwise it adds a Resume payload to the queue every second.
            When a heartbeat happens and the last heartbeat wasn't acknowledged, the loop sets the paused flag."""
        self.beating = True
        while True:
            if not self.beatAcked:
                self.paused = True
            else:
                self.beatAcked = False
                await asyncio.sleep(self.beatTime / 1000)
                await self.send({
                    "op": 1,
                    "d": None
                })
            if self.paused and self.ready:
                await asyncio.sleep(1)
                await self.send({
                    "op": 6,
                    
                })

    def identify(self):
        return {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "dubious",
                    "$device": "dubious"
                }
            }
        }
    
    async def onHello(self, payload: Hello):
        """ Handles the Hello payload.
            Starts the heartbeat loop and sends the identify payload. """
        await self.startHeartbeat(payload["heartbeat_interval"])
        await asyncio.sleep(5)
        await self.req.add(self.identify())
    
    def onHelloAck(self):
        """ Handles the Heartbeat Ack payload.
            Sets the internal flag that the last heartbeat has been acknowledged. """
        print("beat acked")
        self.beatAcked = True
    
    async def onReady(self, payload: Ready):
        """ Handles the Ready event.
            Sets all of the variables that come with the event's payload. """
        self.gatewayVersion = payload["v"]
        self.user = User(payload["user"])
        self.guildIDs = payload["guilds"]
        self.ready = True

