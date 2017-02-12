from typing import Optional, List
import sys
import asyncio
import asyncio.streams
from asyncio import Event
from common.constants import Constants, ErrorCode
from common.network import BattleshipServer, BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType, ProtocolConfig
from common.states import ClientConnectionState, GameState
from server.lobby import ServerLobbyController
from server.client import Client


def main():
    loop = asyncio.get_event_loop()

    messages: List[ProtocolMessage] = []
    test_msg: ProtocolMessage = None
    test_msg_received: Event = Event()

    def server_client_connected(client_reader, client_writer):
        nonlocal test_msg, test_msg_received

        client = Client(reader=client_reader, writer=client_writer)

        async def server_client_disconnected():
            print("< [{}] client disconnected".format(client.id))

        async def server_msg_callback(msg: ProtocolMessage):
            nonlocal client, test_msg
            if not msg == test_msg:
                print("\nFailure for the following two messages (sent/received):")
                print("\t> {}".format(test_msg))
                print("\t< {}".format(msg))
            else:
                #print("Success for the following message:")
                #print("\t  {}".format(msg))
                pass
            test_msg_received.set()
            #print("< [{}] {}".format(client.id, msg))

        print("< [{}] client connected".format(client.id))
        return server_msg_callback, server_client_disconnected

    server = BattleshipServer(Constants.SERVER_IP, Constants.SERVER_PORT, loop, server_client_connected)
    print("Starting server on {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))
    server.start()

    async def client():
        nonlocal test_msg, test_msg_received

        async def client_msg_callback(msg: ProtocolMessage):
            print("< {}".format(msg))

        def client_closed_callback():
            print("< server closed connection".format())

        battleship_client = BattleshipClient(loop, client_msg_callback, client_closed_callback)
        await battleship_client.connect(Constants.SERVER_IP, Constants.SERVER_PORT)

        for i in range(2000):
            for msg_type in list(ProtocolMessageType):
                test_msg = ProtocolMessage.random_from_type(msg_type)
                try:
                    await battleship_client.send(test_msg)
                except Exception as e:
                    print("Was trying to send the following message:")
                    print("{}".format(test_msg))
                    raise e
                await test_msg_received.wait()
                test_msg_received.clear()
            #print(".")


    try:
        #loop.run_forever()
        #tasks = []
        #for i in range(num_clients):
        task = asyncio.ensure_future(client())
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        print("\nReceived SIGINT, terminating …")
        pass

    server.stop()
    loop.close()
    print("Bye.")


if __name__ == '__main__':
    sys.exit(main())
