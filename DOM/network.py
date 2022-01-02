"""

Модуль, работающий с сервером DOM.

"""

from __future__ import annotations

import atexit
import os
import typing as ty
from dataclasses import dataclass

import socketio  # noqa
from loguru import logger


@dataclass
class User:
    """
    Модель пользователя.
    """

    uid: int
    username: str
    password: str
    icon: int  # ID иконки
    friends: list[int]  #


class NetworkClient:
    sio = socketio.Client()

    def __init__(self):
        self.user: User = ...

    def init(self) -> None:
        """
        Устанавливает соединение между клиентом и сервером.
        """
        logger.debug(f"Подключение к серверу: {os.environ['HOST']}")
        self.__class__.sio.connect(os.environ["HOST"], wait_timeout=5)
        self.connect_handlers()
        atexit.register(self.__class__.sio.disconnect)

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
        match response.get("status"):
            case "ok":
                self.user = User(**response["user"])
                logger.opt(colors=True).info(f"Авторизован - <g>{self.user.username}</g>")
                success_callback()
            case "fail":
                logger.opt(colors=True).debug(
                    f"Ошибка авторизации: <y>{response['msg']}</y>"
                )
                fail_callback(response["msg"])

    def connect_handlers(self) -> None:
        ...
