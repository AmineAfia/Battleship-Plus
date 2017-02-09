import sys
import asyncio
import asyncio.streams
from common.constants import Constants, ErrorCode
from common.network import BattleshipServer
from common.protocol import ProtocolMessage, ProtocolMessageType, ProtocolConfig
from common.states import ClientConnectionState, GameState
from server.lobby import ServerLobbyController
from server.client import Client


def main():
    loop = asyncio.get_event_loop()

    lobby_ctrl = ServerLobbyController()

    msgs_for_lobby_controller = [ProtocolMessageType.LOGIN, ProtocolMessageType.LOGOUT, ProtocolMessageType.CHAT_SEND,
                                 ProtocolMessageType.GET_GAMES, ProtocolMessageType.CREATE_GAME, ProtocolMessageType.CANCEL,
                                 ProtocolMessageType.PLACE, ProtocolMessageType.ABORT, ProtocolMessageType.MOVE,
                                 ProtocolMessageType.SHOOT, ProtocolMessageType.JOIN]

    # This gets called whenever a new client connects. The parameter `client`
    # is of type BattleshipServerClient and holds a unique id, the reader and the writer.
    # and it has a send method that sends a ProtocolMessage
    # This callback has to return two other callbacks, one for messages and one for the
    # event that the client disconnects.
    # The idea is that these two callbacks are defined inside the client_connected function,
    # because then they implicitly have access to objects created inside client_connected,
    # for example a GameController.
    def client_connected(client_reader, client_writer):

        client = Client(reader=client_reader, writer=client_writer)
        lobby_ctrl.add_client(client)

        async def client_disconnected():
            print("< [{}] client disconnected".format(client.id))
            await lobby_ctrl.remove_client(client)

        async def msg_callback(msg: ProtocolMessage):
            nonlocal client
            print("< [{}] {}".format(client.id, msg))

            answer: ProtocolMessage = None

            # No other command is permitted if the client is not logged in
            if client.state is ClientConnectionState.NOT_CONNECTED and msg.type is not ProtocolMessageType.LOGIN:
                answer = ProtocolMessage.create_error(ErrorCode.ILLEGAL_STATE_NOT_LOGGED_IN)

            elif msg.type in msgs_for_lobby_controller:
                await lobby_ctrl.handle_msg(client, msg)

            # If we have a direct answer, send it here
            if answer is not None:
                await client.send(answer)

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
