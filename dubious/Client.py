
from __future__ import annotations

import asyncio
import sys
from typing import Callable, Coroutine, Optional

from dubious.Gateway import Gateway
import dubious.raw as raw
from dubious.types import User, Application


class Handler:
    def __init__(self, func: Callable[[raw.Payload], Coroutine]):
        self.func = func
        



class Client:
    def __init__(self, token: str, intents: int, gateway: Gateway):
        # The client's secret.
        self.token = token
        # The intents for the client.
        self.intents = intents
        # The connection to the websocket through which to recieve and request information.
        self.gateway = gateway

        # The time between heartbeats in milliseconds.
        self.beatTime: Optional[int] = None
        # Starts as true for the first heartbeat.
        self.beatAcked = asyncio.Event()
        # Whether or not the heartbeat loop is active.
        self.beating = asyncio.Event()
        # The last sequence number gotten with a recieved payload.
        self.sequence: Optional[int] = None

        # Whether or not the Client has recieved the Ready event.
        self.ready = asyncio.Event()
        # The version of the gateway api being used.
        self.gatewayVersion: Optional[int] = None
        self.user: Optional[User] = None
        self.sessionID: Optional[str] = None
        self.application: Optional[Application] = None
        self.rawGuilds: Optional[list[raw.UnavailableGuild]] = None

        self.handlers = {
            1: [self.onBeat],
            10: [self.onHello],
            11: [self.onBeatAck],
            "READY": [self.onReady],
            "RESUMED": [self.onResumed],
            "RECONNECT": [self.onReconnect],
            "INVALID_SESSION": [],
            "APPLICATION_COMMAND_CREATE": [],
        }

        self.beatAcked.set()
    
    def handler(self, event: str):
        """ Decorator to add event handlers to the Client. """
    
    def addHandler(self, event: str, handler: Callable[[raw.Payload], Coroutine]):
        if not event in self.handlers:
            raise NotImplementedError()
        self.handlers[event].append(handler)

    async def start(self):
        """ Starts the listen loop and the beat loop for the Client.
            Starts the Gateway's loops.
            Runs the asyncio loop forever. """
        loop = asyncio.get_running_loop()
        loop.create_task(self.loopRecv())
        loop.create_task(self.loopBeat())
        await self.gateway.start()
        loop.run_forever()
    
    async def loopRecv(self):
        while True:
            payload = await self.gateway.recv()
            op = payload["op"]
            t = payload["t"]
            self.sequence = payload["s"] if payload["s"] != None else self.sequence
            d = payload["d"]
            if t:
                handler = self.handlers.get(t)
            else:
                handler = self.handlers.get(op)
            if handler:
                await handler(d)
            else:
                raise NotImplementedError()
        
    async def loopBeat(self):
        while True:
            await self.beating.wait()
            print("beating")
            await asyncio.sleep(self.beatTime / 1000)
            if self.beatAcked.is_set():
                await self.sendBeat()
                self.beatAcked.clear()
            else:
                await self.reconnect()
    
    async def onBeat(self, _):
        """ Callback for opcode 1. """
        await self.sendBeat()
    
    async def onConnectionLost(self, _):
        """ Callback for opcode 9. """
        await self.reconnect()
    
    async def onHello(self, payload: raw.Hello):
        """ Callback for opcode 10.
            Sets the heartbeat interval and unblocks the heartbeat loop.
            Sends a heartbeat payload, then waits to send an identify payload."""
        self.beatTime = payload["heartbeat_interval"]
        self.beating.set()
        await self.sendBeat()
        await asyncio.sleep(3)
        await self.sendIdentify()

    async def onBeatAck(self, _):
        """ Callback for opcode 11.
            Sets a flag that the last heartbeat was acknowledged. """
        self.beatAcked.set()
    
    async def onReady(self, payload: raw.Ready):
        """ Callback for event READY.
            Stores the client's User object, the session ID, the client's Application object, and the incomplete Guild objects.
            Sets the ready flag. """
        self.gatewayVersion = payload["v"]
        self.user = User(payload["user"])
        self.sessionID = payload["session_id"]
        self.application = Application(payload["application"])
        self.rawGuilds = payload["guilds"]
        self.ready.set()
    
    async def onResumed(self, _):
        """ Callback for event RESUMED.
            Sets the ready flag. """
        self.ready.set()
    
    async def onReconnect(self, _):
        """ Callback for event RECONNECT.
            Calls the reconnect routine. """
        await self.reconnect()
    
    async def sendBeat(self):
        """ Sends a heartbeat payload. """
        await self.gateway.send({
            "op": 1,
            "d": self.sequence
        })
    
    async def sendIdentify(self):
        """ Sends an identify payload. """
        await self.gateway.send({
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
        })
    
    async def reconnect(self):
        """ Clears the ready flag.
            Restarts the gateway's websocket connection.
            Sends a reconnect payload. """

        self.ready.clear()
        await self.gateway.restart()
        
        await self.gateway.send({
            "op": 6,
            "d": {
                "token": self.token,
                "session_id": self.sessionID,
                "seq": self.sequence
            }
        })
