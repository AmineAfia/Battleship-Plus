from .client import Client
from common.constants import ErrorCode, GameOptions
from common.protocol import ProtocolMessage, ProtocolMessageType, ProtocolConfig, NumShips
from common.states import ClientConnectionState
from common.GameController import GameController


class ServerLobbyController:

    next_game_id = 1

    def __init__(self):
        # users: username -> client
        self.users = {}
        # user_game: username -> game_id
        self.user_gid = {}
        # clients: client_id -> client
        self.clients = {}
        # games: game_id -> [[username1, game_controller1], [username2, game_controller2]]
        self.games = {}

    def add_client(self, client):
        self.clients[client.id] = client

    async def remove_client(self, client):
        if not client.username == "":
            # we first delete the user, so they don't receive DELETE msgs and such
            try:
                del self.users[client.username]
            except KeyError:
                # then the user is already logged out
                pass

            # TODO: end all games of the user, according to their state
            game_ids_to_delete = []
            for game_id, [[username1, game_controller1], [username2, game_controller2]] in self.games.items():
                # TODO: this only affects games the user started, beware, if it's a game in progress, the other user wins or something like that
                if username1 == client.username:
                    game_ids_to_delete.append(game_id)
                    await self.send_delete_game(game_id)
            for game_id in game_ids_to_delete:
                del self.games[game_id]

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

    async def send_delete_game(self, game_id):
        del_msg = ProtocolMessage.create_single(ProtocolMessageType.DELETE_GAME, {"game_id": game_id})
        await self.msg_to_all(del_msg)

    # Handling of not being logged in has to be done outside of this function
    async def handle_msg(self, client, msg: ProtocolMessage):

        if msg.type == ProtocolMessageType.LOGIN:
            await self.handle_login(client, msg)

        elif msg.type == ProtocolMessageType.LOGOUT:
            await self.handle_logout(client, msg)

        elif msg.type == ProtocolMessageType.CHAT_SEND:
            await self.handle_chat_send(client, msg)

        elif msg.type == ProtocolMessageType.CREATE_GAME:
            await self.handle_create_game(client, msg)

        elif msg.type == ProtocolMessageType.CANCEL:
            await self.handle_cancel(client, msg)

    async def handle_login(self, client, msg):
        params = msg.parameters
        answer: ProtocolMessage = None
        if client.state is not ClientConnectionState.NOT_CONNECTED:
            answer = ProtocolMessage.create_error(ErrorCode.ILLEGAL_STATE_ALREADY_LOGGED_IN)
            self.print_client(client, "Client already logged in")
        else:
            login_successful = self.login_user(params["username"], client)
            if not login_successful:
                answer = ProtocolMessage.create_error(ErrorCode.PARAMETER_USERNAME_ALREADY_EXISTS)
                self.print_client(client, "User name already exists")
            else:
                client.state = ClientConnectionState.GAME_SELECTION
                #self.users[username].state = ClientConnectionState.GAME_SELECTION
                client.username = params["username"]
                self.users[client.username] = client
                self.print_client(client, "Client successfully logged in with '{}'".format(client.username))
                await self.send_games_to_user(client)
        if answer is not None:
            print("> [{}] {}".format(client.id, answer))
            await answer.send(client.writer)

    async def handle_logout(self, client, msg):
        client.state = ClientConnectionState.NOT_CONNECTED
        del self.users[client.username]
        self.print_client(client, "Client '{}' logged out".format(client.username))
        # TODO: end all games of the user

    async def handle_chat_send(self, client, msg):
        params = msg.parameters
        answer: ProtocolMessage = None
        text, recipient = params["text"], params["username"]
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

    async def handle_create_game(self, client, msg):
        game_id = ServerLobbyController.next_game_id
        ServerLobbyController.next_game_id += 1

        game_controller = await GameController.create_from_msg(msg, game_id, client, client.username)
        if game_controller is not None:
            client.state = ClientConnectionState.GAME_CREATED
            self.user_gid[client.username] = game_id
            self.games[game_id] = [[client.username, game_controller], [None, None]]
            # and send the game to all users
            msg = game_controller.to_game_msg()
            await self.msg_to_all(msg)

    async def handle_cancel(self, client, msg):
        if client.state == ClientConnectionState.GAME_CREATED:
            game_id = self.user_gid[client.username]
            del self.user_gid[client.username]
            del self.games[game_id]
            client.state = ClientConnectionState.GAME_SELECTION
            await self.send_delete_game(game_id)
        else:
            # TODO: well, thanks RFC, there is no error message for this
            pass

    async def handle_get_games(self, client, msg):
        await self.send_games_to_user(client, msg)

    async def send_games_to_user(self, client):
        repeating_parameters = []
        for game_id, [[username1, game_controller1], [_, _]] in self.games.items():
            parameters = {"game_id": game_id, "username": username1, "board_size": game_controller1.length,
                          "num_ships": NumShips(game_controller1.ships), "round_time": game_controller1.round_time,
                          "options": game_controller1.options}
            repeating_parameters.append(parameters)
        # TODO: remove dummy game
        dummy = {"game_id": 42, "username": "foo", "board_size": 10,
                 "num_ships": NumShips([1,2,3,4,5]), "round_time": 25,
                 "options": GameOptions.PASSWORD}
        dummy2 = {"game_id": 43, "username": "bar", "board_size": 8,
                 "num_ships": NumShips([1,2,5,4,5]), "round_time": 30,
                 "options": 0}
        repeating_parameters.append(dummy)
        repeating_parameters.append(dummy2)
        msg = ProtocolMessage.create_repeating(ProtocolMessageType.GAMES, repeating_parameters)
        await client.send(msg)
