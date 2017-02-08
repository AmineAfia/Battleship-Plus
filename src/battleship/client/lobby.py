import asyncio
from common.states import ClientConnectionState
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType
from common.errorHandler.BattleshipError import BattleshipError
from common.constants import ErrorCode


class ClientLobbyController:
    def __init__(self, client, loop):
        self.username = ""
        self.state = ClientConnectionState.NOT_CONNECTED
        self.client = client
        self.loop = loop

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

    async def handle_msg(self, msg):
        pass
