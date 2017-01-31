import sys
import asyncio
from common.GameController import GameController
from common.constants import Orientation, Direction, Constants
from common.protocol import ProtocolMessage, ProtocolMessageType
from common.network import BattleshipClient
from frontend.welcome import Welcome
from frontend.lobby.login import Login
from frontend.lobby.lobby import Lobby
from frontend.lobby.create import CreateGame
from frontend.lobby.join import Join
from frontend.lobby.waitting import Waiting
from frontend.game.battle import Battle
from common.errorHandler.BattleshipError import BattleshipError
from client.lobby import ClientLobbyController
from common.states import ClientConnectionState


def main():
    # print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))

    network_loop = asyncio.get_event_loop()

    async def msg_callback(msg: ProtocolMessage):
        print("< {}".format(msg))
        if msg.type == ProtocolMessageType.ERROR:
            pass
        # elif msg.type == ProtocolMessageType.GAMES:
        #     if lobby_controller.state == ClientConnectionState.NOT_CONNECTED:
        #         battleship_client.waiting.set()
        #     await lobby_controller.handle_msg(msg)
        else:
            lobby_controller.state = ClientConnectionState.CONNECTED
            pass
        battleship_client.answer_received.set()

    def closed_callback():
        print("< server closed connection".format())

    battleship_client = BattleshipClient(Constants.SERVER_IP, Constants.SERVER_PORT, network_loop, msg_callback,
                                         closed_callback)

    network_loop.run_until_complete(asyncio.ensure_future(battleship_client.connect()))

    game_id = 1
    game_controller = GameController(game_id, battleship_client)
    lobby_controller = ClientLobbyController(battleship_client)

    welcome = Welcome(game_controller, lobby_controller, network_loop)
    welcome.main_welcome()

    while lobby_controller.state == ClientConnectionState.NOT_CONNECTED:
        login = Login(game_controller, lobby_controller, network_loop)
        login.login_main()

    create_game = Lobby(game_controller, lobby_controller, network_loop)
    create_game.lobby_main()

    create_game = CreateGame(game_controller, lobby_controller, network_loop)
    create_game.create_game()

    # TODO: was esc pressed?
    join_battle = Join(game_controller, lobby_controller, network_loop)
    join_battle.join_main()

    # TODO: esc or normal continuation?
    go_to_game = Waiting(game_controller, lobby_controller, network_loop)
    # TODO: is this foo nedded in waiting_main?
    go_to_game.waiting_main("")

    battle_sessions = Battle(game_controller, lobby_controller, network_loop)
    battle_sessions.battle_main()

    # TODO: why does "You win" appear twice?

    print("almost dead")

    network_loop.run_forever()

    print("Bye.")


if __name__ == '__main__':
    sys.exit(main())
