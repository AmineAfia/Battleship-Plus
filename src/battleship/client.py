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

    create_lobby = Lobby(game_controller, lobby_controller, loop)
    create_lobby.lobby_main()

    if lobby_controller.is_joining_game is False:
        create_game = CreateGame(game_controller, lobby_controller, loop)
        create_game.create_game()

    # TODO: was esc pressed?
    join_battle = Join(game_controller, lobby_controller, loop)
    join_battle.join_main()

    # TODO: esc or normal continuation?
    go_to_game = Waiting(game_controller, lobby_controller, loop)
    # TODO: is this foo nedded in waiting_main?
    go_to_game.waiting_main("")

    battle_sessions = Battle(game_controller, lobby_controller, loop)
    battle_sessions.battle_main()

    # TODO: why does "You win" appear twice? --> you start two clients and one of them still have his loop running(connected).
    os.system('cls' if os.name == 'nt' else 'clear')

    print("almost dead")
    #loop.run_forever()
    print("Bye.")

    # ITS ONLY FOR DEBUGGING THE GAMECONTROLER
    try:
        #CREATE THE BATTLEFIELD
        length = 10
        ships = [0, 0, 0, 1, 1]
        cmd = ["create", length, ships]
        msg = ProtocolMessage.create_single(ProtocolMessageType.CREATE_GAME,
                                            {"board_size": 10, "num_ships": NumShips(ships),
                                             "round_time": 25, "options": GameOptions.PASSWORD,
                                             "password": "foo"})

        game_controller = GameController.create_from_msg(1, None, loop, msg, "yoloswag")
        #game_controller.run(msg)
        #PLACE THE SHIPS
        x_pos = 0
        y_pos = 0
        orientation = Orientation.EAST
        x_pos2 = 0
        y_pos2 = 3
        orientation2 = Orientation.EAST
        ship_id = game_controller.get_next_ship_id_to_place()
        ship_type = game_controller.get_ship_type_by_id(ship_id)
        print(game_controller.ships_not_placed)
        print("next ship to place: {}, ship type:  {}".format(ship_id, ship_type))
        msg = ProtocolMessage.create_single(ProtocolMessageType.PLACE,
                                            {"ship_positions": ShipPositions([
                       ShipPosition(Position(y_pos, x_pos), orientation),
                       ShipPosition(Position(y_pos2, x_pos2), orientation2)])})
        game_controller.run(msg)
        game_controller.start_game()
        # MOVE YOUR SHIP
        ship_id = 2
        direction = Direction.EAST
        msg = ProtocolMessage.create_single(ProtocolMessageType.MOVE,
                                            { "ship_id": 1, "direction": Direction.EAST,
                                                "turn_counter": 0 })
        game_controller.run(msg)
        #STRIKE FROM ENEMY = SHOOT
        x_pos = 0
        y_pos = 0
        msg = ProtocolMessage.create_single(ProtocolMessageType.SHOOT,
                                            { "ship_position": ShipPosition(Position(y_pos, x_pos), orientation)
                                                                            ,"turn_counter": 1})
        game_controller.run(msg)
        print(game_controller.get_all_ship_states())
        #SHOOT AT ENEMY BATTLEFIELD
        x_pos = 0
        y_pos = 0
        game_controller.shoot(x_pos, y_pos)
        print(game_controller.all_ships_sunk())
        #ABORT
        msg = ProtocolMessage.create_single(ProtocolMessageType.ABORT,
                                            {"turn_counter": 0 })
        game_controller.run(msg)

    except BattleshipError as e:
        print("{}".format(e))


if __name__ == '__main__':
    sys.exit(main())
