from typing import Optional, Dict, List, Tuple, Any
from .client import Client
from common.constants import ErrorCode, GameOptions, EndGameReason
from common.protocol import ProtocolMessage, ProtocolMessageType, ProtocolConfig, NumShips
from common.states import ClientConnectionState, GameState
from common.GameController import GameController
from random import randrange
from common.errorHandler.BattleshipError import BattleshipError


class ServerLobbyController:

    # we base some tests on the fact that game_id 0 does never exist…
    next_game_id = 1

    def __init__(self, loop):
        self.loop = loop
        # users: username -> client
        self.users: Dict[str, Client] = {}
        # user_game: username -> game_id
        self.user_gid: Dict[str, int] = {}
        # user_game_ctrl: username -> game_controller
        self.user_game_ctrl: Dict[str, GameController] = {}
        # clients: client_id -> client
        self.clients: Dict[int, Client] = {}
        # games: game_id -> [game_controller1, game_controller2]
        self.games: Dict[int, Tuple[GameController, Optional[GameController]]] = {}

    def add_client(self, client: Client):
        self.clients[client.id] = client

    async def remove_client(self, client: Client):
        await self.logout_user(client)
        del self.clients[client.id]

    def login_user(self, username: str, client: Client) -> bool:
        if username not in self.users:
            self.users[username] = client
            return True
        else:
            return False

    async def logout_user(self, client: Client):
        if not client.state == ClientConnectionState.NOT_CONNECTED:
            # we first delete the user, so they don't receive DELETE msgs and such
            try:
                client.state == ClientConnectionState.NOT_CONNECTED
                del self.users[client.username]
            except KeyError:
                # then the user is already logged out
                pass

            # end all games of the user, according to their state
            try:
                our_ctrl: GameController = self.user_game_ctrl[client.username]
            except KeyError:
                # then there is no game associated with the user
                return

            game_id: int = our_ctrl.game_id

            if our_ctrl.state == GameState.IN_LOBBY:
                await self.send_delete_game(game_id)

            elif our_ctrl.state in [GameState.WAITING, GameState.PLACE_SHIPS, GameState.YOUR_TURN, GameState.OPPONENTS_TURN]:
                other_ctrl: GameController = self.user_game_ctrl[our_ctrl.opponent_name]
                await self.end_game_with_reason(our_ctrl, other_ctrl, EndGameReason.SERVER_CLOSED_CONNECTION, EndGameReason.SERVER_CLOSED_CONNECTION)

            else:
                self.print_client(client, "Problem while deleting game: GameController is in an end state and should no longer exist")

            del self.games[game_id]
            del self.user_gid[client.username]
            del self.user_game_ctrl[client.username]

    def print_client(self, client: Client, text: str):
        print("  [{}] {}".format(client.id, text))

    async def msg_to_user(self, msg: ProtocolMessage, username: str):
        await self.users[username].send(msg)

    # send message to all logged in users
    async def msg_to_all(self, msg: ProtocolMessage):
        for username, user in self.users.items():
            await user.send(msg)

    # send message to all logged in users but the one mentioned in the last parameter
    async def msg_to_all_but_one(self, msg: ProtocolMessage, except_username: str):
        for username, user in self.users.items():
            if not username == except_username:
                await user.send(msg)

    async def send_delete_game(self, game_id: int):
        del_msg: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.DELETE_GAME, {"game_id": game_id})
        await self.msg_to_all(del_msg)

    async def handle_msg(self, client: Client, msg: ProtocolMessage):

        # No other command is permitted if the client is not logged in
        if client.state is ClientConnectionState.NOT_CONNECTED and msg.type is not ProtocolMessageType.LOGIN:
            answer: ProtocolMessage = ProtocolMessage.create_error(ErrorCode.ILLEGAL_STATE_NOT_LOGGED_IN)
            await client.send(answer)

        elif msg.type == ProtocolMessageType.LOGIN:
            await self.handle_login(client, msg)

        elif msg.type == ProtocolMessageType.LOGOUT:
            await self.handle_logout(client, msg)

        elif msg.type == ProtocolMessageType.CHAT_SEND:
            await self.handle_chat_send(client, msg)

        elif msg.type == ProtocolMessageType.GET_GAMES:
            await self.handle_get_games(client, msg)

        elif msg.type == ProtocolMessageType.CREATE_GAME:
            await self.handle_create_game(client, msg)

        # handle_cancel handles the case when the user has not created a game
        elif msg.type == ProtocolMessageType.CANCEL:
            await self.handle_cancel(client, msg)

        elif msg.type == ProtocolMessageType.JOIN:
            await self.handle_join(client, msg)

        # all the following messages are only valid when playing
        elif not client.state == ClientConnectionState.PLAYING:
            answer = ProtocolMessage.create_error(ErrorCode.ILLEGAL_STATE_NOT_IN_GAME)
            await client.send(answer)

        elif msg.type == ProtocolMessageType.PLACE:
            await self.handle_place(client, msg)

        elif msg.type == ProtocolMessageType.ABORT:
            await self.handle_abort(client, msg)

        elif msg.type == ProtocolMessageType.MOVE:
            await self.handle_move(client, msg)

        elif msg.type == ProtocolMessageType.SHOOT:
            await self.handle_shoot(client, msg)

    async def handle_login(self, client: Client, msg: ProtocolMessage):
        params: Dict[str, Any] = msg.parameters
        answer: Optional[ProtocolMessage] = None
        if client.state is not ClientConnectionState.NOT_CONNECTED:
            answer = ProtocolMessage.create_error(ErrorCode.ILLEGAL_STATE_ALREADY_LOGGED_IN)
            self.print_client(client, "Client already logged in")
        else:
            login_successful: bool = self.login_user(params["username"], client)
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

    async def handle_logout(self, client: Client, msg: ProtocolMessage):
        await self.logout_user(client)
        self.print_client(client, "Client '{}' logged out".format(client.username))

    async def handle_chat_send(self, client: Client, msg: ProtocolMessage):
        params: Dict[str, Any] = msg.parameters
        answer: Optional[ProtocolMessage] = None
        forward: ProtocolMessage

        text: str = params["text"]
        recipient: str = params["username"]

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

    async def handle_create_game(self, client: Client, msg: ProtocolMessage):
        game_id: int = ServerLobbyController.next_game_id
        ServerLobbyController.next_game_id += 1

        game_controller: GameController = await GameController.create_from_msg(game_id, client, self.loop, msg, client.username)

        if game_controller is not None:
            print("game controller is not None")
            client.state = ClientConnectionState.GAME_CREATED
            self.user_gid[client.username] = game_id
            self.games[game_id] = (game_controller, None)
            self.user_game_ctrl[client.username] = game_controller
            # and send the game to all users
            game_msg: ProtocolMessage = game_controller.to_game_msg()
            await self.msg_to_all(game_msg)
        else:
            print("Fail in Creation of Game Controller")

    async def handle_cancel(self, client: Client, msg: ProtocolMessage):
        if client.state == ClientConnectionState.GAME_CREATED:
            game_id: int = self.user_gid[client.username]
            del self.user_gid[client.username]
            del self.user_game_ctrl[client.username]
            del self.games[game_id]
            client.state = ClientConnectionState.GAME_SELECTION
            await self.send_delete_game(game_id)
        else:
            msg_error: ProtocolMessage = ProtocolMessage.create_error(ErrorCode.PARAMETER_UNKNOWN_GAME_ID)
            await client.send(msg_error)

    async def handle_get_games(self, client: Client, msg: ProtocolMessage):
        await self.send_games_to_user(client)

    async def handle_join(self, client: Client, msg: ProtocolMessage):
        answer: Optional[ProtocolMessage] = None

        game_id: int = msg.parameters["game_id"]

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
            game_controller1: GameController = self.games[game_id][0]
            game_controller1.opponent_name = client.username
            game_controller1.state = GameState.PLACE_SHIPS

            client1: Client = self.games[game_id][0].client

            game_controller2: GameController = GameController.create_from_existing_for_opponent(game_controller1, client)
            game_controller2.state = GameState.PLACE_SHIPS

            self.games[game_id] = (self.games[game_id][0], game_controller2)

            self.user_gid[client.username] = game_id
            # this is already done for the other user

            self.user_game_ctrl[client.username] = game_controller2

            # set client states
            client.state = ClientConnectionState.PLAYING
            client1.state = ClientConnectionState.PLAYING

            # send startgame messages
            await client.send(game_controller2.to_start_game_msg())
            await client1.send(game_controller1.to_start_game_msg())

            # inform the other users the game is no longer available
            await self.send_delete_game(game_id)

        if answer is not None:
            await client.send(answer)

    async def handle_place(self, client: Client, msg: ProtocolMessage):
        our_ctrl: GameController = self.user_game_ctrl[client.username]
        other_ctrl: GameController = self.user_game_ctrl[our_ctrl.opponent_name]

        try:
            our_ctrl.run(msg)
        except BattleshipError as e:
            # TODO: maybe check if it's not an internal error
            answer: ProtocolMessage = ProtocolMessage.create_error(e.error_code)
            await client.send(answer)
            return
        except Exception as e:
            raise e

        # notify the other
        msg_placed: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.PLACED)
        await other_ctrl.client.send(msg_placed)

        # if both are on waiting, the game can start
        if our_ctrl.state == GameState.WAITING and other_ctrl.state == GameState.WAITING:
            # who starts?
            starting_ctrl: GameController
            waiting_ctrl: GameController
            (starting_ctrl, waiting_ctrl) = (our_ctrl, other_ctrl) if randrange(2) == 1 else (other_ctrl, our_ctrl)

            youstart: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.YOUSTART)
            await starting_ctrl.client.send(youstart)
            starting_ctrl.state = GameState.YOUR_TURN
            starting_ctrl.timeout_counter = 0
            starting_ctrl.start_timeout(self.handle_timeout)

            youwait: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.WAIT)
            await waiting_ctrl.client.send(youwait)
            waiting_ctrl.state = GameState.OPPONENTS_TURN

            # TODO: fix this, should be merged with state
            starting_ctrl._game_started = True
            waiting_ctrl._game_started = True

    async def handle_abort(self, client: Client, msg: ProtocolMessage):
        our_ctrl: GameController = self.user_game_ctrl[client.username]
        other_ctrl: GameController = self.user_game_ctrl[our_ctrl.opponent_name]
        await self.end_game_with_reason(our_ctrl, other_ctrl, EndGameReason.OPPONENT_ABORT, EndGameReason.OPPONENT_ABORT)

    async def end_game_with_reason(self, our_ctrl: GameController, other_ctrl: GameController, our_reason: EndGameReason, other_reason: EndGameReason):
        our_ctrl.cancel_timeout()
        other_ctrl.cancel_timeout()

        del self.games[our_ctrl.game_id]
        del self.user_game_ctrl[our_ctrl.username]
        del self.user_game_ctrl[other_ctrl.username]
        del self.user_gid[our_ctrl.username]
        del self.user_gid[other_ctrl.username]

        self.users[our_ctrl.username].state = ClientConnectionState.GAME_SELECTION
        self.users[other_ctrl.username].state = ClientConnectionState.GAME_SELECTION

        await other_ctrl.client.send(ProtocolMessage.create_single(ProtocolMessageType.ENDGAME, {"reason": other_reason}))
        await our_ctrl.client.send(ProtocolMessage.create_single(ProtocolMessageType.ENDGAME, {"reason": our_reason}))

    async def handle_move(self, client: Client, msg: ProtocolMessage):
        our_ctrl: GameController = self.user_game_ctrl[client.username]
        other_ctrl: GameController = self.user_game_ctrl[our_ctrl.opponent_name]

        try:
            our_ctrl.run(msg)
        except BattleshipError as e:
            answer: ProtocolMessage = ProtocolMessage.create_error(e.error_code)
            await client.send(answer)
        except Exception as e:
            raise e

        our_ctrl.timeout_counter = 0
        our_ctrl.cancel_timeout()

        # change turns
        our_ctrl.state = GameState.OPPONENTS_TURN
        other_ctrl.state = GameState.YOUR_TURN

        # notify
        msg_moved: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.MOVED)
        await other_ctrl.client.send(msg_moved)
        await our_ctrl.client.send(msg_moved)

        other_ctrl.start_timeout(self.handle_timeout)

    async def handle_shoot(self, client: Client, msg: ProtocolMessage):
        our_ctrl: GameController = self.user_game_ctrl[client.username]
        other_ctrl: GameController = self.user_game_ctrl[our_ctrl.opponent_name]

        try:
            hit: bool = other_ctrl.run(msg)
        except BattleshipError as e:
            answer = ProtocolMessage.create_error(e.error_code)
            await client.send(answer)
        except Exception as e:
            raise e

        our_ctrl.timeout_counter = 0
        our_ctrl.cancel_timeout()

        if hit:
            sunk: bool = other_ctrl.ship_sunk_at_pos(msg.parameters["position"].horizontal, msg.parameters["position"].vertical)
            msg_hit: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.HIT, {"sunk": sunk, "position": msg.parameters["position"]})
            await other_ctrl.client.send(msg_hit)
            await our_ctrl.client.send(msg_hit)

            other_ctrl.start_timeout(self.handle_timeout)

            if other_ctrl.all_ships_sunk():
                await self.end_game_with_reason(our_ctrl, other_ctrl, EndGameReason.YOU_WON, EndGameReason.OPPONENT_WON)

        else:
            # change turns
            our_ctrl.state = GameState.OPPONENTS_TURN
            other_ctrl.state = GameState.YOUR_TURN

            msg_fail: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.FAIL, {"position": msg.parameters["position"]})
            await other_ctrl.client.send(msg_fail)
            await our_ctrl.client.send(msg_fail)

            other_ctrl.start_timeout(self.handle_timeout)

    async def handle_timeout(self, client: Client):
        our_ctrl: GameController = self.user_game_ctrl[client.username]
        other_ctrl: GameController = self.user_game_ctrl[our_ctrl.opponent_name]

        our_ctrl.timeout_counter += 1

        if our_ctrl.timeout_counter >= 3:
            await self.end_game_with_reason(our_ctrl, other_ctrl, EndGameReason.OPPONENT_WON, EndGameReason.OPPONENT_TIMEOUT)
            return

        msg_timeout: ProtocolMessage = ProtocolMessage.create_single(ProtocolMessageType.TIMEOUT)
        await our_ctrl.client.send(msg_timeout)
        await other_ctrl.client.send(msg_timeout)

        # change turns
        our_ctrl.state = GameState.OPPONENTS_TURN
        other_ctrl.state = GameState.YOUR_TURN

        other_ctrl.start_timeout(self.handle_timeout)

    async def send_games_to_user(self, client: Client):
        # TODO: the type annotation Any can be more exact
        repeating_parameters: List[Any] = []
        for game_id, (game_controller1, game_controller2) in self.games.items():
            parameters = {"game_id": game_id, "username": game_controller1.username, "board_size": game_controller1.length,
                          "num_ships": NumShips(game_controller1.ships), "round_time": game_controller1.round_time,
                          "options": game_controller1.options}
            repeating_parameters.append(parameters)
        # TODO: remove dummy game
        #dummy = {"game_id": 42, "username": "foo", "board_size": 10,
        #         "num_ships": NumShips([1,2,3,4,5]), "round_time": 25,
        #         "options": GameOptions.PASSWORD}
        #dummy2 = {"game_id": 43, "username": "bar", "board_size": 8,
        #         "num_ships": NumShips([1,2,5,4,5]), "round_time": 30,
        #         "options": 0}
        #repeating_parameters.append(dummy)
        #repeating_parameters.append(dummy2)
        msg: ProtocolMessage = ProtocolMessage.create_repeating(ProtocolMessageType.GAMES, repeating_parameters)
        await client.send(msg)
