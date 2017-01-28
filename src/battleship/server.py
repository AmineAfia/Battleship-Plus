import sys
import asyncio
import asyncio.streams
from common.constants import Constants
from common.network import BattleshipServer, BattleshipServerClient
from common.protocol import ProtocolMessage, ProtocolMessageType


def main():
    loop = asyncio.get_event_loop()

    def client_connected(client):

        def client_disconnected():
            print("< [{}] client disconnected".format(client.id))

        async def msg_callback(msg: ProtocolMessage):
            print("< [{}] {}".format(client.id, msg))
            answer: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.CHAT_RECV,
                                                                    {"sender": "sender", "recipient": "recipient",
                                                                     "text": "fuck. you."})
            print("> [{}] {}".format(client.id, answer))
            await answer.send(client.writer)

        print("< [{}] client connected".format(client.id))
        return msg_callback, client_disconnected

    server = BattleshipServer(Constants.SERVER_IP, Constants.SERVER_PORT, loop, client_connected)

    print("Starting server on {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))
    server.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nReceived SIGINT, terminating …")
        pass

    server.stop()
    loop.close()
    print("Bye.")


if __name__ == '__main__':
    sys.exit(main())
