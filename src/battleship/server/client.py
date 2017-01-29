from common.states import ClientConnectionState
from common.protocol import ProtocolMessage


class Client:

    next_client_id = 0

    def __init__(self, username="", state=ClientConnectionState.NOT_CONNECTED, reader=None, writer=None):
        self.username = username
        self.state = state
        self.reader = reader
        self.writer = writer
        self.id = Client.next_client_id
        Client.next_client_id += 1

    async def send(self, msg: ProtocolMessage):
        print("> [{}] {}".format(self.id, msg))
        await msg.send(self.writer)
