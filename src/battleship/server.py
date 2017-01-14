import sys
from common.constants import Constants


import asyncio
import asyncio.streams


class MyServer:
    """
    This is just an example of how a TCP server might be potentially
    structured.  This class has basically 3 methods: start the server,
    handle a client, and stop the server.
    Note that you don't have to follow this structure, it is really
    just an example or possible starting point.
    """

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

        # start a new Task to handle this specific client connection
        task = asyncio.Task(self._handle_client(client_reader, client_writer))
        self.clients[task] = (client_reader, client_writer)

        def client_done(task):
            print("client task done:", task, file=sys.stderr)
            del self.clients[task]

        task.add_done_callback(client_done)

    @asyncio.coroutine
    def _handle_client(self, client_reader, client_writer):
        """
        This method actually does the work to handle the requests for
        a specific client.  The protocol is line oriented, so there is
        a main loop that reads a line with a request and then sends
        out one or more lines back to the client with the result.
        """
        while True:
            data = yield from client_reader.read()
            if not data:  # an empty string means the client disconnected
                break
            print("< {}".format(data))

            # This enables us to have flow control in our connection.
            yield from client_writer.drain()

    def start(self, loop):
        """
        Starts the TCP server, so that it listens on port 12345.
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
