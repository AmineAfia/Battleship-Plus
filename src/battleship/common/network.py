import inspect
import asyncio.streams
from .protocol import ProtocolMessage, parse_from_stream


# Opens one connection to a server, thus internally has one reader and one writer.
# Sends protocol messages using the internal writer, listens for incoming messages and
# calls a callback for the message
class BattleshipClient:
    def __init__(self, server, port, loop, msg_callback, closed_callback):
        if not inspect.iscoroutinefunction(msg_callback):
            raise TypeError("msg_callback must be a coroutine")
        self.msg_callback = msg_callback
        self.closed_callback = closed_callback
        self.server = server
        self.port = port
        self.loop = loop
        self.reader = None
        self.writer = None
        self.receiving_task = None

    async def connect(self):
        self.reader, self.writer = await asyncio.streams.open_connection(
            self.server, self.port, loop=self.loop)
        self.receiving_task = asyncio.Task(parse_from_stream(self.reader, self.writer, self.msg_callback))
        self.receiving_task.add_done_callback(self._server_closed_connection())

    async def send(self, msg: ProtocolMessage):
        await msg.send(self.writer)

    def _server_closed_connection(self):
        self.closed_callback()

    def close(self):
        self.writer.close()
