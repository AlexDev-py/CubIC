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
            self.status = UserStatus("Играет", "#0ACBE6")


class NetworkClient:
    sio = socketio.Client()

    def __init__(self):
        self.user: User = ...
        self.room_id: int = ...

    def init(self) -> None:
        """
        Устанавливает соединение между клиентом и сервером.
        """
        logger.debug(f"Подключение к серверу: {os.environ['HOST']}")
        self.__class__.sio.connect(os.environ["HOST"], wait_timeout=5)
        atexit.register(self.__class__.sio.disconnect)

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
            "friend request",
            lambda response: (
                (
                    lambda: (
                        success_callback(),
                        logger.opt(colors=True).info(
                            f"Пользователю <y>{username}</y> отправлен запрос дружбы"
                        ),
                    )
                )
                if response.get("status") == "ok"
                else (lambda: fail_callback(response.get("msg", "Ошибка")))
            )(),
        )
        self.sio.emit("friend request", dict(username=username))

    def delete_friend_request(self, user: User, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "delete friend request",
            lambda resp: (
                callback(),
                logger.opt(colors=True).info(
                    f"Запрос дружбы от <y>{user.username}</y> отклонен"
                ),
            ),
        )
        self.sio.emit("delete friend request", dict(uid=user.uid))

    def add_friend(self, user: User, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "add friend",
            lambda resp: (
                callback(),
                logger.opt(colors=True).info(
                    f"<y>{user.username}</y> добавлен в друзья"
                ),
            ),
        )
        self.sio.emit("add friend", dict(uid=user.uid))

    def delete_friend(self, user: User, callback: ty.Callable[[], ...]) -> None:
        self.sio.on(
            "delete friend",
            lambda resp: (
                callback(),
                logger.opt(colors=True).info(
                    f"<y>{user.username}</y> удален из друзей"
                ),
            ),
        )
        self.sio.emit("delete friend", dict(uid=user.uid))

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
        self.room_id = response.get("room_id", ...)
        if self.room_id is not ...:
            logger.opt(colors=True).info(f"Создана комната <y>{self.room_id}</y>")
            callback()

    # === LOBBY INVITES ===

    def send_invite(self, user: User, fail_callback: ty.Callable[[str], ...]) -> None:
        if self.room_id is not ...:
            self.sio.on(
                "send invite",
                lambda response: fail_callback(response.get("msg", "Ошибка")),
            )
            self.sio.emit(
                "send invite",
                dict(uid=user.uid, room_id=self.room_id),
                callback=lambda: logger.opt(colors=True).info(
                    f"Пользователю {user.username} отправлено приглашение в группу"
                ),
            )

    def on_lobby_invite(self, callback: ty.Callable[[str, int], ...]) -> None:
        self.sio.on(
            "lobby_invite",
            lambda response: (
                callback(response.get("msg"), response.get("room_id")),
                logger.opt(colors=True).info(
                    f"{response.get('msg')} "
                    f"<y>room_id</y>=<c>{response.get('room_id')}</c>"
                ),
            ),
        )

    # === JOINING THE LOBBY ===

    def join_lobby(
        self,
        room_id: int,
        success_callback: ty.Callable[[list[User]], ...],
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
        success_callback: ty.Callable[[list[User]], ...],
        fail_callback: ty.Callable[[str], ...],
    ) -> None:
        if response.get("status") == "ok":
            self.room_id = response["room_id"]
            logger.opt(colors=True).info(
                f"Вы присоединились в лобби <y>{self.room_id}</y>"
            )
            success_callback([User(**data) for data in response.get("users", ())])
        else:
            fail_callback(response.get("msg", "Ошибка"))

    def on_joining_the_lobby(self, callback: ty.Callable[[User], ...]) -> None:
        self.sio.on(
            "joining the lobby",
            lambda response: (
                callback(User(**response["user"])),
                logger.opt(colors=True).info(
                    f"<y>{response['user']['username']}</y> "
                    "присоединился к вашей группе"
                ),
            ),
        )

    # === LEAVING THE LOBBY ===

    def leave_lobby(self, callback: ty.Callable[[], ...]) -> None:
        self.sio.emit(
            "leave lobby", dict(room_id=self.room_id), callback=lambda *_: callback()
        )

    def on_leaving_the_lobby(self, callback: ty.Callable[[str, int], ...]) -> None:
        self.sio.on(
            "leaving the lobby",
            lambda response: callback(response["msg"], response["uid"]),
        )

    # ===== TOOLS =====

    def get_user(self, uid: int) -> User:
        response = self._send_request("user", uid=uid)
        return User(**response)

    def update_user(self) -> None:
        self.user = self.get_user(self.user.uid)

    @staticmethod
    def _send_request(namespace, **kwargs) -> dict:
        return requests.get(
            f"{os.environ['HOST']}/{namespace}?"
            + "&".join(f"{k}={v}" for k, v in kwargs.items())
        ).json()
