import sys
import os
import asyncio
import argparse
from common.GameController import GameController
from common.constants import Orientation, Direction, Constants, GameOptions
from common.protocol import ProtocolMessage, ProtocolMessageType, ShipPositions, Position, Positions, ShipPosition, NumShips
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
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", help="server IP", type=str, default=Constants.SERVER_IP)
    parser.add_argument("-p", "--port", help="server port", type=int, default=Constants.SERVER_PORT)
    args = parser.parse_args()

    Constants.SERVER_IP = args.ip
    Constants.SERVER_PORT = args.port

    loop = asyncio.get_event_loop()

    async def msg_callback(msg: ProtocolMessage):
        print("< {}".format(msg))
        if msg.type == ProtocolMessageType.ERROR:
            pass
        elif msg.type == ProtocolMessageType.GAMES:
            await lobby_controller.handle_games(msg)
        elif msg.type == ProtocolMessageType.GAME:
            await lobby_controller.handle_game(msg)
        elif msg.type == ProtocolMessageType.DELETE_GAME:
            await lobby_controller.handle_delete_game(msg)
        elif msg.type == ProtocolMessageType.CHAT_RECV:
            await lobby_controller.handle_chat_recv(msg)
        elif msg.type == ProtocolMessageType.HIT:
            await lobby_controller.handle_hit(msg)
        elif msg.type == ProtocolMessageType.WAIT:
            await lobby_controller.handle_wait(msg)
        elif msg.type == ProtocolMessageType.YOUSTART:
            await lobby_controller.handle_youstart(msg)
        elif msg.type == ProtocolMessageType.TIMEOUT:
            await lobby_controller.handle_timeout(msg)
        elif msg.type == ProtocolMessageType.FAIL:
            await lobby_controller.handle_fail(msg)
        elif msg.type == ProtocolMessageType.ENDGAME:
            await lobby_controller.handle_endgame(msg)
        elif msg.type == ProtocolMessageType.MOVED:
            await lobby_controller.handle_moved(msg)
        elif msg.type == ProtocolMessageType.STARTGAME: # and lobby_controller.is_joining_game is False:
             await lobby_controller.handle_start_game(msg)
        # TODO: add the other types
        else:
            pass

    def closed_callback():
        print("< server closed connection".format())

    battleship_client = BattleshipClient(loop, msg_callback, closed_callback)

    game_id = 1
    game_controller = GameController(game_id, battleship_client, loop)
    lobby_controller = ClientLobbyController(battleship_client, game_controller, loop)

    welcome = Welcome(game_controller, lobby_controller, loop)
    welcome.main_welcome()

    while lobby_controller.state == ClientConnectionState.NOT_CONNECTED:
        login = Login(game_controller, lobby_controller, loop)
        login.login_main()

    while not lobby_controller.quit_client:
        create_lobby = Lobby(game_controller, lobby_controller, loop)
        create_lobby.lobby_main()

        if lobby_controller.is_joining_game is False:
            create_game = CreateGame(game_controller, lobby_controller, loop)
            create_game.create_game()

            # TODO: esc or normal continuation?
            go_to_game = Waiting(game_controller, lobby_controller, loop)
            # TODO: is this foo nedded in waiting_main?
            go_to_game.waiting_main("")

        join_battle = Join(game_controller, lobby_controller, loop)
        join_battle.join_main()

        battle_sessions = Battle(game_controller, lobby_controller, loop)
        battle_sessions.battle_main()

        # reset lobby and game controller
        game_controller.reset_for_client()
        lobby_controller.reset()

    # TODO: go back to lobby, send GET_GAMES

    # TODO: why does "You win" appear twice? --> you start two clients and one of them still have his loop running(connected).

if __name__ == '__main__':
    sys.exit(main())
