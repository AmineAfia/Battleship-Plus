from .client import Client
from common.constants import ErrorCode, GameOptions
from common.protocol import ProtocolMessage, ProtocolMessageType, ProtocolConfig, NumShips
from common.states import ClientConnectionState
from common.GameController import GameController


class ServerLobbyController:
    def __init__(self):
        self.users = {}
        self.clients = {}
        # Games: game_id -> [[username1, game_controller1], [username2, game_controller2]]
        self.games = {}

    def add_client(self, client):
        self.clients[client.id] = client

    def remove_client(self, client):
        # TODO: end all games of the user
        if not client.username == "":
            del self.users[client.username]
        del self.clients[client.id]

    def login_user(self, username, client: Client) -> bool:
        if username not in self.users:
            self.users[username] = client
            return True
        else:
            return False

    def print_client(self, client, text):
        print("  [{}] {}".format(client.id, text))

    async def msg_to_user(self, msg, username):
        await self.users[username].send(msg)

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
                    await self.send_games_to_user(client.username)

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

    async def send_games_to_user(self, username):
        repeating_parameters = []
        for game_id, [[username1, game_controller1], [_, _]] in self.games.items():
            parameters = {"game_id": game_id, "username": username1, "board_size": game_controller1.length,
                          "num_ships": game_controller1.ships, "round_time": game_controller1.round_time,
                          "options": game_controller1.options}
            repeating_parameters.append(parameters)
        # TODO: remove dummy game
        dummy = {"game_id": 42, "username": "foo", "board_size": 10,
                 "num_ships": NumShips([1,2,3,4,5]), "round_time": 25,
                 "options": GameOptions.PASSWORD}
        repeating_parameters.append(dummy)
        msg = ProtocolMessage.create_repeating(ProtocolMessageType.GAMES, repeating_parameters)
        await self.msg_to_user(msg, username)
