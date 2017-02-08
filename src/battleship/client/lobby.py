import asyncio
from common.states import ClientConnectionState
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import ErrorCode
from common.game import GameLobbyData


class ClientLobbyController:
    def __init__(self, client, loop):
        self.username = ""
        self.state = ClientConnectionState.NOT_CONNECTED
        self.client = client
        self.loop = loop
        self.games = {}

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

    async def handle_games(self, msg):
        # clear the list of games as we are just receiving a new one
        # TODO: but only clear on the first GAMES message
        self.games = {}

        self.state = ClientConnectionState.CONNECTED

        for params in msg.repeating_parameters:
            game = GameLobbyData(params["game_id"], params["username"], params["board_size"], params["num_ships"], params["round_time"], params["options"])
            self.games[params["game_id"]] = game

    async def handle_game(self, msg):
        game = GameLobbyData(params.game_id, params.username, params.board_size, params.num_ships, params.round_time, params.options)
        self.games[params.game_id] = game

    async def handle_msg(self, msg):
        pass
