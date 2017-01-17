import sys
from common.constants import Constants
from common.protocol import ProtocolConfig, ProtocolMessage, ProtocolMessageType, ProtocolMessageParameters, ProtocolField, parse_from_stream

import asyncio
import asyncio.streams


class MyServer:

    next_client_id = 1

    def __init__(self):
        self.server = None  # encapsulates the server sockets

        # this keeps track of all the clients that connected to our
        # server.  It can be useful in some cases, for instance to
        # kill client connections or to broadcast some data to all
        # clients...
        self.clients = {} # task -> (reader, writer)

    def _accept_client(self, client_reader, client_writer):
        """
        This method accepts a new client connection and creates a Task
        to handle this client.  self.clients is updated to keep track
        of the new client.
        """

        client_id = MyServer.next_client_id
        MyServer.next_client_id += 1
        print("< [{}] client connected".format(client_id))

        def msg_callback(msg: ProtocolMessage):
            print("< [{}] {}".format(client_id, msg))

        # start a new Task to handle this specific client connection
        task = asyncio.Task(parse_from_stream(client_reader, client_writer, msg_callback))
        self.clients[task] = (client_reader, client_writer)

        def client_done(task):
            print("< [{}] client disconnected".format(client_id))
            del self.clients[task]

        task.add_done_callback(client_done)

    def start(self, loop):
        """
        Starts the TCP server, so that it listens on the specified port.
        For each client that connects, the accept_client method gets
        called.  This method runs the loop until the server sockets
        are ready to accept connections.
        """
        self.server = loop.run_until_complete(
            asyncio.streams.start_server(self._accept_client,
                                         Constants.SERVER_IP, Constants.SERVER_PORT,
                                         loop=loop))

    def stop(self, loop):
        """
        Stops the TCP server, i.e. closes the listening socket(s).
        This method runs the loop until the server sockets are closed.
        """
        if self.server is not None:
            self.server.close()
            loop.run_until_complete(self.server.wait_closed())
            self.server = None


def main():
    print("Starting server on {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))

    loop = asyncio.get_event_loop()

    # creates a server and starts listening to TCP connections
    server = MyServer()

    server.start(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nReceived SIGINT, terminating …")
        pass

    # TODO: make this cleaner, run_until_complete inside the server object feels strange
    server.stop(loop)
    #loop.run_until_complete(server.wait_closed())
    loop.close()
    print("Bye.")


if __name__ == '__main__':
    sys.exit(main())
