"""

Модуль, работающий с сервером DOM.

"""

from __future__ import annotations

import atexit
import os
import typing as ty
from dataclasses import dataclass

import requests
import socketio  # noqa
from loguru import logger

from game import Room, Player
from game.room import Move


class UserStatus(ty.NamedTuple):
    text: str
    color: str


@dataclass
class User:
    """
    Модель пользователя.
    """

    uid: int
    username: str
    icon: int  # ID иконки
    friends: list[int]
    friend_requests: list[int]
    status: UserStatus

    def __post_init__(self):
        if self.status == 0:
            self.status = UserStatus("Не в сети", "gray")
        elif self.status == 1:
            self.status = UserStatus("В сети", "green")
        elif self.status == 2:
            self.status = UserStatus("В лобби", "#0ACBE6")
        elif self.status == 3:
            self.status = UserStatus("Играет", "#0ACBE6")


class NetworkClient:
    sio = socketio.Client()

    def __init__(self):
        self.user: User = ...
        self.room: Room = ...

    def init(self) -> None:
        """
        Устанавливает соединение между клиентом и сервером.
        """
        logger.debug(f"Подключение к серверу: {os.environ['HOST']}")
        self.__class__.sio.connect(os.environ["HOST"], wait_timeout=10)
        self.connect_handlers()
        atexit.register(self.disconnect)

    # ===== LOGIN =====

    def login(
        self,
        username: str,
        password: str,
        success_callback: ty.Callable[[], ...],
        fail_callback: ty.Callable[[str], ...],
    ) -> None:
        """
        Метод для авторизации пользователя.
        :param username: Имя пользователя.
        :param password: Пароль.
        :param success_callback: Обработчик успешной авторизации.
        :param fail_callback: Обработчик ошибки авторизации.
        """
        # Подключаем обработчик
        self.sio.on(
            "login",
            lambda response: self._on_auth(
                response,
                success_callback,
                fail_callback,
            ),
        )
        # Отправляем запрос к серверу
        logger.opt(colors=True).debug(f"Авторизация - <g>{username}</g>")
        self.sio.emit("login", dict(username=username, password=password))

    def signup(
        self,
        username: str,
        password: str,
        success_callback: ty.Callable[[], ...],
        fail_callback: ty.Callable[[str], ...],
    ) -> None:
        """
        Метод для регистрации пользователя.
        :param username: Имя пользователя.
        :param password: Пароль.
        :param success_callback: Обработчик успешной авторизации.
        :param fail_callback: Обработчик ошибки регистрации.
        """
        self.sio.on(
            "signup",
            lambda response: self._on_auth(
                response,
                success_callback,
                fail_callback,
            ),
        )
        logger.opt(colors=True).debug(f"Регистрация - <g>{username}</g>")
        self.sio.emit("signup", dict(username=username, password=password))

    def _on_auth(
        self,
        response: dict[str, ...],
        success_callback: ty.Callable[[], ...],
        fail_callback: ty.Callable[[str], ...],
    ) -> None:
        """
        Обработчик авторизации.
        :param response: Ответ от сервера.
        :param success_callback: Обработчик успешной авторизации.
        :param fail_callback: Обработчик ошибки авторизации.
        """
        if response.get("status") == "ok":
            self.user = User(**response["user"])
            logger.opt(colors=True).info(f"Авторизован - <g>{self.user.username}</g>")
            success_callback()
        else:
            logger.opt(colors=True).debug(
                f"Ошибка авторизации: <y>{response['msg']}</y>"
            )
            fail_callback(response["msg"])

    # ===== FRIENDS =====

    def send_friend_request(
        self,
        username: str,
        success_callback: ty.Callable[[], ...],
        fail_callback: ty.Callable[[str], ...],
    ) -> None:
        self.sio.on(
            "send friend request",
            lambda response: (
                (
                    lambda: (
                        logger.opt(colors=True).info(
                            f"Пользователю <y>{username}</y> отправлен запрос дружбы"
                        ),
                        success_callback(),
                    )
                )
                if response.get("status") == "ok"
                else (lambda: fail_callback(response.get("msg", "Ошибка")))
            )(),
        )
        self.sio.emit("send friend request", dict(username=username))

    def on_friend_request(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "friend request",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Запрос дружбы от <y>{response['user']['username']}</y>"
                ),
                callback(),
            ),
        )

    def delete_friend_request(self, user: User) -> None:
        self.sio.emit("delete friend request", dict(uid=user.uid))
        logger.opt(colors=True).info(
            f"Запрос дружбы от <y>{user.username}</y> отклонен"
        )

    def add_friend(self, uid: int) -> None:
        self.sio.emit("add friend", dict(uid=uid))

    def on_add_friend(self, callback: ty.Callable[[User], ...]) -> None:
        self.sio.on(
            "add friend",
            lambda response: (
                logger.opt(colors=True).info(
                    f"<y>{response['user']['username']}</y> добавлен в друзья"
                ),
                callback(User(**response["user"])),
            ),
        )

    def delete_friend(self, uid: int) -> None:
        self.sio.emit("delete friend", dict(uid=uid))

    def on_delete_friend(self, callback: ty.Callable[[User], ...]) -> None:
        self.sio.on(
            "delete friend",
            lambda response: (
                logger.opt(colors=True).info(
                    f"<y>{response['user']['username']}</y> удален из друзей"
                ),
                callback(User(**response["user"])),
            ),
        )

    def on_change_user_status(self, callback: ty.Callable[[User], ...]) -> None:
        self.sio.on(
            "change user status", lambda response: callback(User(**response["user"]))
        )

    # ===== LOBBY =====

    # === CREATE LOBBY ===

    def create_lobby(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "create lobby", lambda response: self._on_create_lobby(response, callback)
        )
        self.sio.emit("create lobby")

    def _on_create_lobby(
        self, response: dict[str, int], callback: ty.Callable[[], ...]
    ) -> None:
        self.room = Room(response["room_id"])
        self.room.join(self.user, is_owner=True)
        logger.opt(colors=True).info(f"Создана комната <y>{self.room.room_id}</y>")
        callback()

    # === LOBBY INVITES ===

    def send_invite(self, user: User, fail_callback: ty.Callable[[str], ...]) -> None:
        if self.room is not ...:
            self.sio.on(
                "send invite",
                lambda response: fail_callback(response.get("msg", "Ошибка")),
            )
            self.sio.emit(
                "send invite",
                dict(uid=user.uid, room_id=self.room.room_id),
                callback=lambda: logger.opt(colors=True).info(
                    f"Пользователю {user.username} отправлено приглашение в группу"
                ),
            )

    def on_lobby_invite(self, callback: ty.Callable[[str, int], ...]) -> None:
        self.sio.on(
            "lobby invite",
            lambda response: (
                logger.opt(colors=True).info(
                    f"{response.get('msg')} "
                    f"<y>room_id</y>=<c>{response.get('room_id')}</c>"
                ),
                callback(response.get("msg"), response.get("room_id")),
            ),
        )

    # === JOINING THE LOBBY ===

    def join_lobby(
        self,
        room_id: int,
        success_callback: ty.Callable[[], ...],
        fail_callback: ty.Callable[[str], ...],
    ) -> None:
        self.sio.on(
            "join lobby",
            lambda response: self._on_join_lobby(
                response, success_callback, fail_callback
            ),
        )
        self.sio.emit("join lobby", dict(room_id=room_id))

    def _on_join_lobby(
        self,
        response: dict[str, ...],
        success_callback: ty.Callable[[], ...],
        fail_callback: ty.Callable[[str], ...],
    ) -> None:
        if response.get("status") == "ok":
            self.room = Room(response["room_id"])
            for i, player in enumerate(response["users"]):
                self.room.join(Player(**player, is_owner=i == 0))
            logger.opt(colors=True).info(
                f"Вы присоединились в лобби <y>{self.room.room_id}</y>"
            )
            success_callback()
        else:
            fail_callback(response.get("msg", "Ошибка"))

    def on_joining_the_lobby(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "joining the lobby",
            lambda response: (
                (
                    self.room.join(User(**response["user"]))
                    if not self.room.get_by_uid(response["user"]["uid"])
                    else ...
                )
                if self.room is not ...
                else ...,
                logger.opt(colors=True).info(
                    f"<y>{response['user']['username']}</y> "
                    "присоединился к вашей группе"
                ),
                callback(),
            ),
        )

    # === LEAVING THE LOBBY ===

    def leave_lobby(self) -> None:
        self.sio.emit(
            "leave lobby",
            dict(room_id=self.room.room_id),
        )
        self.room: Room = ...

    def on_leaving_the_lobby(self, callback: ty.Callable[[str], ...]) -> None:
        self.sio.on(
            "leaving the lobby",
            lambda response: (
                self.room.leave(response["uid"]),
                callback(response["msg"]),
            ),
        )

    # === SELECT CHARACTER ===

    def select_character(self, character_id: int) -> None:
        self.sio.emit(
            "select character",
            dict(room_id=self.room.room_id, character_id=character_id),
        )

    def on_character_selection(self, callback: ty.Callable[[int, int], ...]) -> None:
        self.sio.on(
            "character selection",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Пользователь <y>{response['uid']}</y> выбрал персонажа: "
                    f"<y>{response['character_id']}</y>"
                ),
                callback(response["uid"], response["character_id"]),
            ),
        )

    # === SET READY ===

    def ready(self) -> None:
        self.sio.emit("ready", dict(room_id=self.room.room_id))

    def on_ready(self, callback: ty.Callable[[int], ...]) -> None:
        self.sio.on(
            "ready",
            lambda response: (
                logger.opt(colors=True).info(f"Игрок <y>{response['uid']}</y> готов"),
                callback(response["uid"]),
            ),
        )

    def no_ready(self) -> None:
        self.sio.emit("no ready", dict(room_id=self.room.room_id))

    def on_no_ready(self, callback: ty.Callable[[int], ...]) -> None:
        self.sio.on(
            "no ready",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Игрок <y>{response['uid']}</y> еще не готов"
                ),
                callback(response["uid"]),
            ),
        )

    # ==== GAME =====

    # === START GAME ===

    def start_game(self) -> None:
        self.sio.emit("start game", dict(room_id=self.room.room_id))

    def on_loading_game(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "loading game",
            lambda *response: (logger.info("Загрузка уровня"), callback()),
        )

    def on_start_game(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "start game",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Уровень <y>{response['lvl']}</y> загружен"
                ),
                self.room.init_lvl(**response),
                callback(),
            ),
        )

    # === GAME UPDATES ===

    def on_update_players(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "update players",
            lambda response: (
                list(
                    map(
                        lambda player: self.room.update_player(player),
                        response["players"],
                    )
                ),
                callback(),
            ),
        )

    # === ITEMS ===

    def buy_item(self, item_index: int, fail_callback: ty.Callable[[str], ...]) -> None:
        self.sio.on("buy item", lambda response: fail_callback(response.get("msg")))
        self.sio.emit(
            "buy item", dict(room_id=self.room.room_id, item_index=item_index)
        )

    def on_buying_an_item(self, callback: ty.Callable[[int, Player], ...]) -> None:
        self.sio.on(
            "buying an item",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Игрок <y>{response['player']['username']}</y> купил предмет "
                    f"<y>{self.room.shop[response['item_index']].name}</y>"
                ),
                self.room.shop.__setitem__(response["item_index"], None),
                self.room.update_player(response["player"]),
                callback(
                    response["item_index"],
                    self.room.get_by_uid(response["player"]["uid"]),
                ),
            ),
        )

    def remove_item(self, item_index: int) -> None:
        self.sio.emit(
            "remove item", dict(room_id=self.room.room_id, item_index=item_index)
        )

    def on_removing_an_item(self, callback: ty.Callable[[Player], ...]) -> None:
        self.sio.on(
            "removing an item",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Игрок <y>{response['player']['username']}</y> продал предмет "
                    f"<y>{response['item']['name']}</y>"
                ),
                self.room.update_player(response["player"]),
                callback(self.room.get_by_uid(response["player"]["uid"])),
            ),
        )

    # === MOVE ===

    def move(self, y: int, x: int, fail_callback: ty.Callable[[str], ...]) -> None:
        self.sio.on("move", lambda response: fail_callback(response.get("msg", "Err")))
        self.sio.emit("move", dict(room_id=self.room.room_id, y=y, x=x))

    def on_movement_player(self, callback: ty.Callable[[Player], ...]) -> None:
        self.__dict__["on_movement_player_callback"] = callback

    def on_movement_enemy(self, callback: ty.Callable[[], ...]) -> None:
        self.__dict__["on_movement_enemy_callback"] = callback

    def _on_movement(self, response: dict[str, ...]) -> None:
        if response.get("obj") == "p":
            logger.opt(colors=True).info(
                f"<y>{response['player']['username']}</y> move "
                f"<c>{response['player']['character']['pos']}</c> -> <c>{response['pos']}</c>"
            )
            self.room.update_player(response["player"])
            if callback := self.__dict__.get("on_movement_player_callback"):
                callback(self.room.get_by_uid(response["player"]["uid"]))
        elif response.get("obj") == "e":
            logger.opt(colors=True).info(
                f"enemy <y>{response['eid']}</y> move to <c>{response['pos']}</c>"
            )
            self.room.update_enemy(response["enemy"])
            if callback := self.__dict__.get("on_movement_enemy_callback"):
                callback()

    # === QUEUE ===

    def pass_move(self) -> None:
        self.sio.emit("pass move", dict(room_id=self.room.room_id))

    def on_set_queue(self, callback: ty.Callable[[str], ...]) -> None:
        self.sio.on(
            "set queue",
            lambda response: (
                logger.opt(colors=True).info(f"Ход передан <y>{response['queue']}</y>"),
                self.room.__setattr__("queue", response["queue"]),
                callback(response["queue"]),
            ),
        )

    # === ROLL THE DICE ===

    def roll_the_dice(self, fail_callback: ty.Callable[[str], ...]) -> None:
        self.sio.on(
            "roll the dice", lambda response: fail_callback(response.get("msg"))
        )
        self.sio.emit("roll the dice", dict(room_id=self.room.room_id))

    def on_rolling_the_dice(
        self, callback: ty.Callable[[list[tuple[int, int]]], ...]
    ) -> None:
        self.sio.on(
            "rolling the dice",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Игрок <y>{response['uid']}</y> кинул кость: "
                    f"<c>{response['movement']}</c> -> <c>{response['result']}</c>"
                ),
                self.room.__setattr__(
                    "move_data",
                    Move(response["uid"], response["result"], response["movement"]),
                ),
                callback(self.room.move_data.movement),
            ),
        )

    # === FIGHT ===

    def roll_the_fight_dice(self, fail_callback: ty.Callable[[str], ...]) -> None:
        self.sio.on(
            "roll the fight dice", lambda response: fail_callback(response.get("msg"))
        )
        self.sio.emit("roll the fight dice", dict(room_id=self.room.room_id))

    def on_rolling_the_fight_dice(
        self, callback: ty.Callable[[list[tuple[int, int]]], ...]
    ) -> None:
        self.sio.on(
            "rolling the fight dice",
            lambda response: (
                logger.opt(colors=True).info(
                    f"Игрок <y>{response['uid']}</y> кинул кость боя: "
                    f"<c>{response['movement']}</c> -> <c>{response['result']}</c>"
                ),
                list(
                    map(
                        lambda player: self.room.update_player(player),
                        response["players"],
                    )
                ),
                self.room.update_enemies(response["enemies"]),
                callback(response["movement"]),
            ),
        )

    def on_fight(self, callback: ty.Callable[[int], ...]) -> None:
        self.sio.on(
            "fight",
            lambda response: (
                logger.opt(colors=True).info(
                    f"fight user <y>{response['uid']}</y> and enemy <y>{response['eid']}</y>"
                ),
                callback(response["uid"]),
            ),
        )

    def on_end_fight(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "end fight",
            lambda response: (
                logger.opt(colors=True).info(f"all fights is over"),
                callback(),
            ),
        )

    # ===== TOOLS =====

    def disconnect(self) -> None:
        def _disconnect():
            self.sio.emit("logout", callback=self.sio.disconnect)

        if self.room is not ...:
            self.sio.on("leave lobby", lambda *_: _disconnect())
            self.leave_lobby()
        else:
            _disconnect()

        self.sio.wait()

    def get_user(self, uid: int) -> User:
        response = self._send_request("user", uid=uid)
        return User(**response)

    def update_user(self) -> None:
        self.user = self.get_user(self.user.uid)

    def on_error(self, callback: ty.Callable[[str], ...]) -> None:
        self.sio.on(
            "error",
            lambda response: (logger.error(response["msg"]), callback(response["msg"])),
        )

    def get_data_hash(self) -> str:
        return self._send_request("data_hash").get("data_hash", "")

    def get_data_links(self) -> dict[str, str]:
        return self._send_request("data_links", version=os.environ["VERSION"])

    @staticmethod
    def _send_request(namespace, **kwargs) -> dict:
        return requests.get(
            f"{os.environ['HOST']}/{namespace}?"
            + "&".join(f"{k}={v}" for k, v in kwargs.items())
        ).json()

    def connect_handlers(self) -> None:
        self.sio.on("movement", lambda response: self._on_movement(response))
