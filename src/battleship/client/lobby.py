import asyncio
from typing import Any
from common.states import ClientConnectionState
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import ErrorCode
from common.game import GameLobbyData
from common.GameController import GameController


class ClientLobbyController:
    def __init__(self, client, game_controller, loop):
        self.username = ""
        self.state = ClientConnectionState.NOT_CONNECTED
        self.client = client
        self.loop = loop
        self.games = {}
        self.game_controller = game_controller
        self.ui_game_callback = None
        self.ui_delete_game_callback = None
        self.ui_chat_recv_callback = None
        self.ui_start_game_callback = None
        self.ui_placed_callback = None
        self.ui_abort_callback = None
        self.ui_youstart_callback = None
        self.ui_wait_callback = None
        self.ui_hit_callback = None
        self.ui_fail_callback = None
        self.ui_moved_callback = None
        self.ui_timeout_callback = None
        self.ui_endgame_callback = None
        self.is_joining_game = False

    async def try_login(self, server, port, username):
        if not self.client.connected:
            await self.client.connect(server, port)

        if username.strip() == "":
            raise BattleshipError(ErrorCode.PARAMETER_INVALID_USERNAME)

        msg = ProtocolMessage.create_single(ProtocolMessageType.LOGIN, {"username": username})
        await self.client.send_and_wait_for_answer(msg)

        # TODO: timeouts
        if self.client.last_msg_was_error:
            raise BattleshipError(self.client.last_error)

    # the default value for the username means the message is sent to everyone
    async def send_chat(self, username, text):
        msg = ProtocolMessage.create_single(ProtocolMessageType.CHAT_SEND, {"username": username, "text": text})
        await self.client.send(msg)

    async def send_place(self):
        msg = self.game_controller.get_place_msg()
        await self.client.send_and_wait_for_answer(msg)

        # TODO: timeouts
        if self.client.last_msg_was_error:
            raise BattleshipError(self.client.last_error)

    async def send_join(self, game_id: int, password: str=""):
        params: Dict[str, Any] = {"game_id": game_id}
        if not password == "":
            params["password"] = password
        msg: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.JOIN, params)
        await self.client.send_and_wait_for_answer(msg)

        # TODO: timeouts
        if self.client.last_msg_was_error:
            raise BattleshipError(self.client.last_error)

    async def handle_chat_recv(self, msg):
        self.ui_chat_recv_callback(msg.parameters["sender"], msg.parameters["recipient"], msg.parameters["text"])

    async def handle_games(self, msg):
        # clear the list of games as we are just receiving a new one
        # TODO: but only clear on the first GAMES message
        self.games = {}

        self.state = ClientConnectionState.CONNECTED

        # TODO: fix this. Why is the [{}] in an empty message?
        if not msg.repeating_parameters == [] or not msg.repeating_parameters == [{}]:
            for params in msg.repeating_parameters:
                # TODO: this is a dirty hack.
                if not "game_id" in params.keys():
                    continue
                game = GameLobbyData(params["game_id"], params["username"], params["board_size"], params["num_ships"], params["round_time"], params["options"])
                self.games[params["game_id"]] = game

    async def handle_game(self, msg):
        # check if this is our game
        # TODO: we could check if we actually sent a game…
        params = msg.parameters
        if params["username"] == self.username:
            self.game_controller.game_id = params["game_id"]
        # if it's a game from someone else, add it to the list of games
        else:
            game = GameLobbyData(params["game_id"], params["username"], params["board_size"], params["num_ships"], params["round_time"], params["options"])
            self.games[params["game_id"]] = game
            if self.ui_game_callback is not None:
                self.ui_game_callback(game)

    async def handle_delete_game(self, msg):
        params = msg.parameters
        # TODO: what to do with a game that is already started?
        try:
            del self.games[params["game_id"]]
            if self.ui_delete_game_callback is not None:
                self.ui_delete_game_callback(params["game_id"])
        except KeyError:
            # then the game did not exist, so what.
            pass

    async def handle_start_game(self, msg):
        pass

    async def handle_placed(self, msg):
        pass

    async def handle_youstart(self, msg):
        pass

    async def handle_wait(self, msg):
        pass

    async def handle_hit(self, msg):
        pass

    async def handle_fail(self, msg):
        pass

    async def handle_moved(self, msg):
        pass

    async def handle_timeout(self, msg):
        pass

    async def handle_endgame(self, msg):
        pass

    async def handle_msg(self, msg):
        pass
