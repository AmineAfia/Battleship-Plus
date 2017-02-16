from asyncio import StreamWriter, StreamReader
from common.states import ClientConnectionState
from common.protocol import ProtocolMessage


class Client:

    next_client_id: int = 0

    def __init__(self, username="", state=ClientConnectionState.NOT_CONNECTED, reader=None, writer=None):
        self.username: str = username
        self.game_id: int = 0
        self.state: ClientConnectionState = state
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer
        self.id: int = Client.next_client_id
        Client.next_client_id += 1

    async def send(self, msg: ProtocolMessage):
        print("> [{}] {}".format(self.id, msg))
        await msg.send(self.writer)
