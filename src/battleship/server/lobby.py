from .client import Client
from common.constants import ErrorCode, GameOptions, EndGameReason
from common.protocol import ProtocolMessage, ProtocolMessageType, ProtocolConfig, NumShips
from common.states import ClientConnectionState, GameState
from common.GameController import GameController
from random import randrange


class ServerLobbyController:

    # we base some tests on the fact that game_id 0 does never exist…
    next_game_id = 1

    def __init__(self):
        # users: username -> client
        self.users = {}
        # user_game: username -> game_id
        self.user_gid = {}
        # user_game_ctrl: username -> game_controller
        self.user_game_ctrl = {}
        # clients: client_id -> client
        self.clients = {}
        # games: game_id -> [game_controller1, game_controller2]
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
            game_id_to_delete = 0
            for game_id, [game_controller1, game_controller2] in self.games.items():
                # TODO: this only affects games the user started, beware, if it's a game in progress, the other user wins or something like that
                if game_controller1.username == client.username:
                    game_id_to_delete = game_id
                    await self.send_delete_game(game_id)
                    break

            if not game_id_to_delete == 0:
                del self.games[game_id_to_delete]
                del self.user_gid[client.username]
                del self.user_game_ctrl[client.username]

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

    # send message to all logged in users but the one mentioned in the last parameter
    async def msg_to_all_but_one(self, msg, except_username):
        for username, user in self.users.items():
            if not username == except_username:
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

        elif msg.type == ProtocolMessageType.GET_GAMES:
            await self.handle_get_games(client, msg)

        elif msg.type == ProtocolMessageType.JOIN:
            await self.handle_join(client, msg)

        elif msg.type == ProtocolMessageType.PLACE:
            await self.handle_place(client, msg)

        elif msg.type == ProtocolMessageType.ABORT:
            await self.handle_abort(client, msg)

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
        # check if the message is for all users
        elif recipient == "":
            forward = ProtocolMessage.create_single(ProtocolMessageType.CHAT_RECV,
                                                    {"sender": client.username, "recipient": "",
                                                     "text": text})
            await self.msg_to_all_but_one(forward, client.username)
            self.print_client(client, "Forwarding chat message to all logged in users but {}".format(client.username))

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
            self.games[game_id] = [game_controller, None]
            self.user_game_ctrl[client.username] = game_controller
            # and send the game to all users
            msg = game_controller.to_game_msg()
            await self.msg_to_all(msg)

    async def handle_cancel(self, client, msg):
        if client.state == ClientConnectionState.GAME_CREATED:
            game_id = self.user_gid[client.username]
            del self.user_gid[client.username]
            del self.user_game_ctrl[client.username]
            del self.games[game_id]
            client.state = ClientConnectionState.GAME_SELECTION
            await self.send_delete_game(game_id)
        else:
            # TODO: well, thanks RFC, there is no error message for this
            pass

    async def handle_get_games(self, client, msg):
        await self.send_games_to_user(client, msg)

    async def handle_join(self, client, msg):
        answer: ProtocolMessage = None

        game_id = msg.parameters["game_id"]

        # there is no available game with the specified game_ID (error code 104)
        if not game_id in self.games.keys():
            answer = ProtocolMessage.create_error(ErrorCode.PARAMETER_UNKNOWN_GAME_ID)

        # the message lacks the password parameter although a password is required (error code 105)
        elif self.games[game_id][0].options == GameOptions.PASSWORD and not "password" in msg.parameters:
            answer = ProtocolMessage.create_error(ErrorCode.PARAMETER_PASSWORD_REQUIRED)

        # a password is required for the game, but the given password is incorrect (error code 106)
        elif self.games[game_id][0].options == GameOptions.PASSWORD and not msg.parameters["password"] == self.games[game_id][0].password:
            answer = ProtocolMessage.create_error(ErrorCode.PARAMETER_INVALID_PASSWORD)

        # the user wants to join his own game (error code 107)
        elif self.games[game_id][0].username == client.username:
            answer = ProtocolMessage.create_error(ErrorCode.PARAMETER_ILLEGAL_JOIN)

        # the game has already started (error code 8)
        elif not self.games[game_id][0].state == GameState.IN_LOBBY:
            answer = ProtocolMessage.create_error(ErrorCode.ILLEGAL_STATE_GAME_ALREADY_STARTED)

        # Everything ok, let them play
        else:
            # setup a game_controller for the other one
            game_controller1 = self.games[game_id][0]
            game_controller1.opponent_name = client.username
            game_controller1.state = GameState.PLACE_SHIPS

            client1 = self.games[game_id][0].client

            game_controller2 = GameController.create_from_existing_for_opponent(game_controller1, client)
            game_controller2.state = GameState.PLACE_SHIPS

            self.games[game_id][1] = game_controller2

            self.user_gid[client.username] = game_id
            # this is already done for the other user

            self.user_game_ctrl[client.username] = game_controller2

            # set client states
            client.state = ClientConnectionState.PLAYING
            client1.state = ClientConnectionState.PLAYING

            # send startgame messages
            await client.send(game_controller2.to_start_game_msg())
            await client1.send(game_controller1.to_start_game_msg())


        if answer is not None:
            await client.send(answer)

    async def handle_place(self, client, msg):
        # get the game controller for this client
        # TODO: catch fail (user not playing)

        our_ctrl = self.user_game_ctrl[client.username]
        other_ctrl = self.user_game_ctrl[our_ctrl.opponent_name]

        try:
            our_ctrl.run(msg)
        except BattleshipError as e:
            # TODO: maybe check if it's not an internal error
            answer = ProtocolMessage.create_error(e.error_code)
            await client.send(answer)
        except Exception as e:
            raise e

        # notify the other
        msg = ProtocolMessage.create_single(ProtocolMessageType.PLACED)
        await other_ctrl.client.send(msg)

        # if both are on waiting, the game can start
        if our_ctrl.state == GameState.WAITING and other_ctrl.state == GameState.WAITING:
            # who starts?
            starting_ctrl, waiting_ctrl = our_ctrl, other_ctrl if randrange(2) == 1 else other_ctrl, our_ctrl

            youstart = ProtocolMessage.create_single(ProtocolMessageType.YOUSTART)
            await starting_ctrl.client.send(youstart)
            starting_ctrl.state = GameState.YOUR_TURN

            youwait = ProtocolMessage.create_single(ProtocolMessageType.WAIT)
            await waiting_ctrl.client.send(youwait)
            waiting_ctrl.state = GameState.OPPONENTS_TURN

            # TODO: fix this, should be merged with state
            starting_ctrl._game_started = True
            waiting_ctrl._game_started = True

    async def handle_abort(self, client, msg):
        our_ctrl = self.user_game_ctrl[client.username]
        other_ctrl = self.user_game_ctrl[our_ctrl.opponent_name]

        del self.games[our_ctrl.game_id]
        del self.user_game_ctrl[our_ctrl.username]
        del self.user_game_ctrl[other_ctrl.username]
        del self.user_gid[our_ctrl.username]
        del self.user_gid[other_ctrl.username]

        self.users[our_ctrl.username].state = ClientConnectionState.GAME_SELECTION
        self.users[other_ctrl.username].state = ClientConnectionState.GAME_SELECTION

        msg = ProtocolMessage.create_single(ProtocolMessageType.ENDGAME, {"reason": EndGameReason.OPPONENT_ABORT})
        await other_ctrl.client.send(msg)
        await our_ctrl.client.send(msg)

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
