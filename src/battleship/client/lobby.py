from common.states import ClientConnectionState
from common.network import BattleshipClient
from common.protocol import ProtocolMessage, ProtocolMessageType


class ClientLobbyController:
    def __init__(self, client):
        self.username = ""
        self.state = ClientConnectionState.NOT_CONNECTED
        self.client = client

    async def try_login(self, username):
        msg = ProtocolMessage.create_single(ProtocolMessageType.LOGIN, {"username": username})
        await self.client.send(msg)
        # TODO: timeouts
        await self.client.answer_received.wait()
        self.client.answer_received.clear()

    async def handle_msg(self, msg):
        pass
