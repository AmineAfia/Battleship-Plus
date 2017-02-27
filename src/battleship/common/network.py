from typing import Tuple, Dict, List, Callable
import logging
import inspect
import asyncio.streams
from asyncio import Event, StreamReader, StreamWriter
from .protocol import ProtocolMessage, ProtocolMessageType, parse_from_stream
from common.constants import ErrorCode


# Opens one connection to a server, thus internally has one reader and one writer.
# Sends protocol messages using the internal writer, listens for incoming messages and
# calls a callback for the message
class BattleshipClient:

    def __init__(self, loop, msg_callback, closed_callback):
        if not inspect.iscoroutinefunction(msg_callback):
            raise TypeError("msg_callback must be a coroutine")
        self.msg_callback = msg_callback
        self.closed_callback = closed_callback
        self.server = None
        self.port = None
        self.loop = loop
        self.reader = None
        self.writer = None
        self.receiving_task = None
        self.answer_received = Event()
        self.last_msg_was_error = False
        self.last_error = ErrorCode.UNKNOWN
        self.connected = False

    async def _internal_msg_callback(self, msg):
        if msg.type == ProtocolMessageType.ERROR:
            self.last_msg_was_error = True
            self.last_error = msg.parameters["error_code"]
        else:
            self.last_msg_was_error = False
            self.last_error = ErrorCode.UNKNOWN
        await self.msg_callback(msg)
        self.answer_received.set()

    async def connect(self, server, port):
        self.server = server
        self.port = port
        logging.info("Trying login on server {}:{}".format(server, port))
        try:
            self.reader, self.writer = await asyncio.streams.open_connection(
                self.server, self.port, loop=self.loop)
        except ConnectionRefusedError as e:
            # just pass the exception, but we want to do some book keeping as well
            raise e
        self.connected = True
        self.receiving_task = self.loop.create_task(parse_from_stream(self.reader, self.writer,
                                                                      self._internal_msg_callback))
        self.receiving_task.add_done_callback(self._internal_closed_callback)

    async def send(self, msg: ProtocolMessage):
        await msg.send(self.writer)

    async def send_and_wait_for_answer(self, msg: ProtocolMessage):
        await self.send(msg)
        await self.answer_received.wait()
        self.answer_received.clear()

    def _internal_closed_callback(self, task):
        self.closed_callback()
        self.connected = False

    def close(self):
        self.writer.close()
        # TODO: should we call the closed_callback here? No, because close is called from outside, they can decide this themselves.


class BattleshipServer:

    def __init__(self, ip: str, port: int, loop, client_connected_callback) -> None:
        self.ip: str = ip
        self.port: int = port
        self.loop = loop
        self.client_connected_callback = client_connected_callback
        self.server = None
        # TODO: what's the type of StreamReader and StreamWriter?
        self.clients: Dict[asyncio.Task, Tuple[StreamReader, StreamWriter]] = {}

    def _accept_client(self, client_reader: StreamReader, client_writer: StreamWriter) -> None:
        """
        This method accepts a new client connection and creates a Task
        to handle this client.  self.clients is updated to keep track
        of the new client.
        """

        async def internal_msg_callback(msg: ProtocolMessage) -> None:
            await external_msg_callback(msg)

        def internal_client_done(task) -> None:
            # can't use await here, because we are not in a coroutine
            self.loop.create_task(external_disconnected_callback())
            #await external_disconnected_callback()
            del self.clients[task]

        # start a new Task to handle this specific client connection
        # TODO: huh, shouldn't I use loop.create_task?
        task = asyncio.Task(parse_from_stream(client_reader, client_writer, internal_msg_callback))
        self.clients[task] = (client_reader, client_writer)
        external_msg_callback, external_disconnected_callback = self.client_connected_callback(client_reader,
                                                                                               client_writer)
        if not inspect.iscoroutinefunction(external_msg_callback):
            raise TypeError("msg_callback must be a coroutine")

        task.add_done_callback(internal_client_done)

    def start(self) -> None:
        """
        Starts the TCP server, so that it listens on the specified port.
        For each client that connects, the accept_client method gets
        called.  This method runs the loop until the server sockets
        are ready to accept connections.
        """
        self.server = self.loop.run_until_complete(
            asyncio.streams.start_server(self._accept_client,
                                         self.ip, self.port,
                                         loop=self.loop))

    def stop(self) -> None:
        """
        Stops the TCP server, i.e. closes the listening socket(s).
        This method runs the loop until the server sockets are closed.
        """
        if self.server is not None:
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.server = None
