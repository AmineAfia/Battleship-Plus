from .client import Client
from common.constants import ErrorCode
from common.protocol import ProtocolMessage, ProtocolMessageType, ProtocolConfig
from common.states import ClientConnectionState


class ServerLobbyController:
    def __init__(self):
        self.users = {}
        self.clients = {}
        self.games = {}

    def add_client(self, client):
        self.clients[client.id] = client

    def remove_client(self, client):
        # TODO: end all games of the user
        del self.clients[client.id]

    def login_user(self, username, client: Client) -> bool:
        if username not in self.users:
            self.users[username] = client
            return True
        else:
            return False

    def print_client(self, client, text):
        print("  [{}] {}".format(client.id, text))

    async def msg_to_user(self, msg, user):
        await self.users[user].send(msg)

    # send message to all logged in users
    async def msg_to_all(self, msg):
        for username, user in self.users.items():
            await user.send(msg)

    async def handle_msg(self, client, msg: ProtocolMessage):

        answer: ProtocolMessage = None

        if msg.type == ProtocolMessageType.LOGIN:
            if client.state is not ClientConnectionState.NOT_CONNECTED:
                answer = ProtocolMessage.create_error(ErrorCode.ILLEGAL_STATE_ALREADY_LOGGED_IN)
                self.print_client(client, "Client already logged in")
            else:
                login_successful = self.login_user(msg.parameters["username"], client)
                if not login_successful:
                    answer = ProtocolMessage.create_error(ErrorCode.PARAMETER_USERNAME_ALREADY_EXISTS)
                    self.print_client(client, "User name already exists")
                else:
                    client.state = ClientConnectionState.CONNECTED
                    client.username = msg.parameters["username"]
                    self.users[client.username] = client
                    self.print_client(client, "Client successfully logged in with '{}'".format(client.username))

        elif msg.type == ProtocolMessageType.LOGOUT:
            client.state = ClientConnectionState.NOT_CONNECTED
            del self.users[client.username]
            self.print_client(client, "Client '{}' logged out".format(client.username))
            # TODO: end all games of the user

        elif msg.type == ProtocolMessageType.CHAT_SEND:
            text = msg.parameters["text"]
            recipient = msg.parameters["username"]
            if len(text) > ProtocolConfig.CHAT_MAX_TEXT_LENGTH:
                answer = ProtocolMessage.create_error(ErrorCode.SYNTAX_MESSAGE_TEXT_TOO_LONG)
                self.print_client(client, "Max text length exceeded")
            elif recipient not in self.users:
                answer = ProtocolMessage.create_error(ErrorCode.PARAMETER_USERNAME_DOES_NOT_EXIST)
                self.print_client(client, "Chat error: username '{}' does not exist".format(recipient))
            else:
                forward = ProtocolMessage.create_single(ProtocolMessageType.CHAT_RECV,
                                                        {"sender": client.username, "recipient": recipient,
                                                         "text": text})
                await self.msg_to_user(forward, recipient)
                self.print_client(client, "Forwarding chat message to '{}'".format(recipient))

        if answer is not None:
            print("> [{}] {}".format(client.id, answer))
            await answer.send(client.writer)
