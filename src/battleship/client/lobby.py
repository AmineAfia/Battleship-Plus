import asyncio
import logging
from typing import Any, Callable, Optional, List
from common.states import ClientConnectionState
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType, Position, Positions, ProtocolConfig
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import ErrorCode, EndGameReason
from common.game import GameLobbyData
from common.GameController import GameController


class Callback:
    def __init__(self, name: ProtocolMessageType) -> None:
        self._name: ProtocolMessageType = name
        self._wait_until_set = asyncio.Event()
        self._callback: Optional[Callable] = None

    def clear(self):
        self._wait_until_set.clear()
        self._callback = None

    @property
    def name(self):
        return self._name

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, callback: Callable):
        self._callback = callback
        self._wait_until_set.set()

    async def call(self, *args):
        await self._wait_until_set.wait()
        self.callback(*args)


class ClientLobbyController:
    def __init__(self, client, game_controller, loop):
        self.username = ""
        self.state = ClientConnectionState.NOT_CONNECTED
        self.client = client
        self.loop = loop
        self.games = {}
        self.game_controller = game_controller
        self.quit_client = False
        self.is_joining_game = False
        self.is_cancelling_game = False
        self.is_first_start = True

        self._callback_names: List[ProtocolMessageType] = [ProtocolMessageType.GAME,
                                ProtocolMessageType.DELETE_GAME,
                                ProtocolMessageType.CHAT_RECV,
                                ProtocolMessageType.STARTGAME,
                                ProtocolMessageType.YOUSTART,
                                ProtocolMessageType.WAIT,
                                ProtocolMessageType.TIMEOUT,
                                ProtocolMessageType.FAIL,
                                ProtocolMessageType.PLACED,
                                ProtocolMessageType.ABORT,
                                ProtocolMessageType.HIT,
                                ProtocolMessageType.MOVED,
                                ProtocolMessageType.ENDGAME]
        self._callbacks: Dict[ProtocolMessageType, Callback] = {}
        for callback_name in self._callback_names:
            self._callbacks[callback_name] = Callback(callback_name)

    def set_callback(self, name: ProtocolMessageType, callback: Callable) -> None:
        self._callbacks[name].callback = callback

    def clear_callback(self, name: ProtocolMessageType) -> None:
        self._callbacks[name].clear()

    async def call_callback(self, name: ProtocolMessageType, *args):
        await self._callbacks[name].call(*args)

    def prepare_for_next(self):
        self.games = {}
        self.quit_client = False
        self.is_joining_game = False
        self.is_cancelling_game = False
        self.is_first_start = False
        for callback in self._callbacks.values():
            callback.clear()

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

    async def send_get_games(self):
        msg = ProtocolMessage.create_single(ProtocolMessageType.GET_GAMES)
        self.games = {}
        await self.client.send_and_wait_for_answer(msg)

        # TODO: timeouts
        if self.client.last_msg_was_error:
            raise BattleshipError(self.client.last_error)

    # the default value for the username means the message is sent to everyone
    async def send_chat(self, username, text):
        if len(text) > ProtocolConfig.CHAT_MAX_TEXT_LENGTH:
            offset = 0
            while offset < len(text):
                next_text = text[offset:offset+ProtocolConfig.CHAT_MAX_TEXT_LENGTH]
                offset += ProtocolConfig.CHAT_MAX_TEXT_LENGTH
                msg = ProtocolMessage.create_single(ProtocolMessageType.CHAT_SEND, {"username": username, "text": next_text})
                await self.client.send(msg)
        else:
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

    async def send_shoot(self, x_pos, y_pos):
        msg = self.game_controller.get_shoot_msg(x_pos, y_pos)
        await self.client.send_and_wait_for_answer(msg)

        # TODO: timeouts
        if self.client.last_msg_was_error:
            raise BattleshipError(self.client.last_error)

    async def send_move(self, ship_id, direction):
        msg = self.game_controller.get_move_msg(ship_id, direction)
        await self.client.send_and_wait_for_answer(msg)

        #TODO timeouts
        if self.client.last_msg_was_error:
            raise  BattleshipError(self.client.last_error)

    async def send_abort(self):
        msg = ProtocolMessage.create_single(ProtocolMessageType.ABORT)
        await self.client.send_and_wait_for_answer(msg)

    async def send_cancel(self):
        msg = ProtocolMessage.create_single(ProtocolMessageType.CANCEL)
        await self.client.send_and_wait_for_answer(msg)

        # TODO: timeouts
        if self.client.last_msg_was_error:
            raise BattleshipError(self.client.last_error)

    async def handle_chat_recv(self, msg):
        self.ui_chat_recv_callback(msg.parameters["sender"], msg.parameters["recipient"], msg.parameters["text"])

    async def handle_games(self, msg):
        # Because the GAMES message is the implicit confirmation that the login was successful
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
            await self.call_callback(ProtocolMessageType.GAME, game)

    async def handle_delete_game(self, msg):
        params = msg.parameters
        try:
            del self.games[params["game_id"]]
            await self.call_callback(ProtocolMessageType.DELETE_GAME, params["game_id"])
        except KeyError:
            # then the game did not exist, so what.
            pass

    async def handle_youstart(self, msg):
        self.game_controller.run(msg)
        await self.call_callback(ProtocolMessageType.YOUSTART)

    async def handle_wait(self, msg):
        self.game_controller.run(msg)
        await self.call_callback(ProtocolMessageType.WAIT)

    async def handle_timeout(self, msg):
        self.game_controller.run(msg)
        await self.call_callback(ProtocolMessageType.TIMEOUT)

    async def handle_hit(self, msg):
        self.game_controller.run(msg)
        sunk: bool = msg.parameters["sunk"]
        position: Position = msg.parameters["position"]
        await self.call_callback(ProtocolMessageType.HIT, sunk, position)

    async def handle_fail(self, msg):
        self.game_controller.run(msg)
        position: Position = msg.parameters["position"]
        await self.call_callback(ProtocolMessageType.FAIL, position)

    async def handle_moved(self, msg):
        try:
            self.game_controller.run(msg)
            positions: Positions = msg.parameters
            await self.call_callback(ProtocolMessageType.MOVED, positions)
        except Exception as e:
            logging.error(str(type(e)))

    async def handle_start_game(self, msg):
        self.game_controller.run(msg)
        await self.call_callback(ProtocolMessageType.STARTGAME)

    async def handle_placed(self, msg):
        self.game_controller.run(msg)
        await self.call_callback(ProtocolMessageType.PLACED)

    async def handle_endgame(self, msg):
        self.game_controller.run(msg)
        await self.call_callback(ProtocolMessageType.ENDGAME, msg.parameters["reason"])

    async def handle_msg(self, msg):
        pass
