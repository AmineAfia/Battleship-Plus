"""
    This is the client module. It manages incoming messages from the server and manages the UI screens in order of execution.
"""
import sys
import os
import asyncio
import argparse
import logging
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
    """
        Main class for the client. It follows the following order:
        - The client picks an IP address, a port to connect to and a file to log his output
        - Gets a asyncio loop
        - Defines a callback that specifies handlers for each massage he receives
        - Defines a callback that specifies what to do when the connection is closed or lost
        - Instanciate BattleshipClient with the loop and defined callbacks.
          This makes the client now able to communicate with the server
        - Instanciate a GameController to use the controller's methods (RFC rules)
        - Instanciate a ClientLobbyController where the message handling/sending methods are implemented
        - Define the order/flow of rendering the screens
    """
    # Arguments Parser to indicate an IP address, Port and log file directly from a Terminal command
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", help="server IP", type=str, default=Constants.SERVER_IP)
    parser.add_argument("-p", "--port", help="server port", type=int, default=Constants.SERVER_PORT)
    parser.add_argument("-l", "--logfile", help="file for logs", type=argparse.FileType('w'), default='client.log')
    args = parser.parse_args()

    # Initiat the IP, port and logger for the client as well
    Constants.SERVER_IP = args.ip
    Constants.SERVER_PORT = args.port
    logging.basicConfig(filename=args.logfile.name, level=logging.DEBUG)

    # Get asyncio loop
    loop = asyncio.get_event_loop()
    # A flag to tell the client when to handle the CHAT messages
    in_lobby_or_battle = False

    # Specify handlers for all messages from the server
    async def msg_callback(msg: ProtocolMessage):
        logging.debug("< {}".format(msg))

        # if we receive a non error message, we take this as a hint that we are successfully logged in
        if lobby_controller.state is ClientConnectionState.NOT_CONNECTED and not msg.type == ProtocolMessageType.ERROR:
            lobby_controller.state = ClientConnectionState.CONNECTED

        if msg.type == ProtocolMessageType.ERROR:
            pass
        elif msg.type == ProtocolMessageType.GAMES:
            await lobby_controller.handle_games(msg)
        elif msg.type == ProtocolMessageType.GAME:
            await lobby_controller.handle_game(msg)
        elif msg.type == ProtocolMessageType.DELETE_GAME:
            await lobby_controller.handle_delete_game(msg)
        elif msg.type == ProtocolMessageType.CHAT_RECV:
            if in_lobby_or_battle is True:
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
        elif msg.type == ProtocolMessageType.STARTGAME:
            await lobby_controller.handle_start_game(msg)
        elif msg.type == ProtocolMessageType.PLACED:
            await lobby_controller.handle_placed(msg)
        elif msg.type == ProtocolMessageType.NONE:
            err: ProtocolMessage = ProtocolMessage.create_error(ErrorCode.UNKNOWN)
            await lobby_controller.client.send(err)
        # add the other types if needed
        else:
            pass

    # A callback to run when we close the connection with the server
    def closed_callback():
        logging.debug("< server closed connection".format())

    # Instance of BattleshipClient. The client can open a connection to the server with the arguments he passed
    battleship_client = BattleshipClient(loop, msg_callback, closed_callback)

    # Instance of GameController and ClientLobbyController for this client
    game_id = 1
    game_controller = GameController(game_id, battleship_client, loop)
    lobby_controller = ClientLobbyController(battleship_client, game_controller, loop)

    # render the first screen
    welcome = Welcome(game_controller, lobby_controller, loop)
    welcome.main_welcome()

    # Render the loging screen and stay in it till the client stats changes to CONNECTED
    while lobby_controller.state == ClientConnectionState.NOT_CONNECTED:
        login = Login(game_controller, lobby_controller, loop)
        login.login_main()
        del login

    # Render the lobby screen and keep comming back to it till the client quits the battleship+
    while not lobby_controller.quit_client:
        create_lobby = Lobby(game_controller, lobby_controller, loop)
        in_lobby_or_battle = True
        create_lobby.lobby_main()
        del create_lobby
        in_lobby_or_battle = False
        # Render the create game screen if the client is not joining a game
        if lobby_controller.is_joining_game is False:
            create_game = CreateGame(game_controller, lobby_controller, loop)
            create_game.create_game()
            del create_game
            # Render a waiting screen and keep it till the client cancels or somebody joins his game
            go_to_game = Waiting(game_controller, lobby_controller, loop)
            go_to_game.waiting_main("")
            del go_to_game
        # If somebody joins this clients game, render the join screen to place ships
        if not lobby_controller.is_cancelling_game:
            join_battle = Join(game_controller, lobby_controller, loop)
            in_lobby_or_battle = True
            join_battle.join_main()
            del join_battle
            in_lobby_or_battle = False
            # If nobody cancels render the battle screen and lets play! :)
            if not lobby_controller.received_cancel:
                battle_sessions = Battle(game_controller, lobby_controller, loop)
                battle_sessions.battle_main()
                del battle_sessions

        os.system('cls' if os.name == 'nt' else 'clear')

        # reset lobby and game controller
        game_controller.reset_for_client()
        lobby_controller.prepare_for_next()

        # TODO: CTRL+C should exit everything. Maybe a global QUIT_APP callback?

if __name__ == '__main__':
    sys.exit(main())
