"""

Интерфейс авторизации и регистрации.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg

from base import Group, Button, Label, WidgetsGroup, InputBox
from utils import FinishStatus, check_password, NickTextFilter, InfoAlert

if ty.TYPE_CHECKING:
    from network import NetworkClient


class Login(WidgetsGroup):
    """
    Интерфейс авторизации.
    """

    def __init__(self, parent: AuthScreen):
        super(Login, self).__init__(
            parent, x=0, y=0, width=parent.SIZE[0], height=parent.SIZE[1], padding=20
        )

        self.label = Label(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2 - 20),
            y=int(parent.SIZE[1] * 0.2),
            text="Авторизация",
            color=pg.Color("red"),
            font=pg.font.Font(None, 40),
        )

        self.login = InputBox(
            self,
            x=0,
            y=self.label.rect.bottom + 40,
            description="Имя пользователя",
            width=self.rect.width * 0.9,
            color=pg.Color("red"),
            padding=5,
            font=pg.font.Font(None, 30),
            inactive_border_color=pg.Color("gray"),
            active_border_color=pg.Color("black"),
            border_width=5,
        )

        self.password = InputBox(
            self,
            x=0,
            y=self.login.rect.bottom + 30,
            description="Пароль",
            width=self.rect.width * 0.9,
            color=pg.Color("red"),
            padding=5,
            font=pg.font.Font(None, 30),
            inactive_border_color=pg.Color("gray"),
            active_border_color=pg.Color("black"),
            border_width=5,
            is_password=True,
        )

        self.auth_button = Button(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2) - 20,
            y=self.password.rect.bottom + 30,
            text="Войти",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, 25),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.auth(parent),
        )

        self.auth_button = Button(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2) - 20,
            y=self.auth_button.rect.bottom + 5,
            text="зарегистрироваться",
            padding=5,
            color=pg.Color("blue"),
            callback=lambda event: parent.show_signup_group(),
        )

    def auth(self, parent: AuthScreen) -> None:
        """
        Попытка авторизации пользователя
        :param parent:
        """
        if not (login := self.login.input_line.text):
            self.login.input_line.active = True
            return
        if not (password := self.password.input_line.value()):
            self.password.input_line.active = True
            return

        self.disable()
        parent.network_client.login(
            username=login,
            password=password,
            success_callback=lambda: parent.auth(login, password),
            fail_callback=lambda msg: (parent.error_alert.show_message(msg)),
        )


class Signup(WidgetsGroup):
    """
    Интерфейс регистрации.
    """

    def __init__(self, parent: AuthScreen):
        super(Signup, self).__init__(
            parent, x=0, y=0, width=parent.SIZE[0], height=parent.SIZE[1], padding=20
        )

        self.label = Label(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2 - 20),
            y=int(parent.SIZE[1] * 0.1),
            text="Регистрация",
            color=pg.Color("red"),
            font=pg.font.Font(None, 40),
        )

        self.login = InputBox(
            self,
            x=0,
            y=self.label.rect.bottom + 40,
            description="Имя пользователя",
            width=self.rect.width * 0.9,
            color=pg.Color("red"),
            padding=5,
            font=pg.font.Font(None, 30),
            inactive_border_color=pg.Color("gray"),
            active_border_color=pg.Color("black"),
            border_width=5,
            text_filter=NickTextFilter,
        )

        self.password = InputBox(
            self,
            x=0,
            y=self.login.rect.bottom + 30,
            description="Пароль",
            width=self.rect.width * 0.9,
            color=pg.Color("red"),
            padding=5,
            font=pg.font.Font(None, 30),
            inactive_border_color=pg.Color("gray"),
            active_border_color=pg.Color("black"),
            border_width=5,
            is_password=True,
        )

        self.password2 = InputBox(
            self,
            x=0,
            y=self.password.rect.bottom + 30,
            description="Повторите пароль",
            width=self.rect.width * 0.9,
            color=pg.Color("red"),
            padding=5,
            font=pg.font.Font(None, 30),
            inactive_border_color=pg.Color("gray"),
            active_border_color=pg.Color("black"),
            border_width=5,
            is_password=True,
        )

        self.auth_button = Button(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2) - 20,
            y=self.password2.rect.bottom + 30,
            text="Создать аккаунт",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, 25),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.auth(parent),
        )

        self.auth_button = Button(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2) - 20,
            y=self.auth_button.rect.bottom + 5,
            text="авторизоваться",
            padding=5,
            color=pg.Color("blue"),
            callback=lambda event: parent.show_login_group(),
        )

    def auth(self, parent: AuthScreen) -> None:
        """
        Попытка регистрации пользователя.
        :param parent:
        """
        if not (login := self.login.input_line.text):
            self.login.input_line.active = True
            return
        if not (password := self.password.input_line.value()):
            self.password.input_line.active = True
            return
        if not (password2 := self.password2.input_line.value()):
            self.password2.input_line.active = True
            return
        if password != password2:
            parent.error_alert.show_message("Пароли не совпадают")
            return
        if not check_password(password):
            parent.error_alert.show_message("Пароль слишком легкий")
            return

        self.disable()
        parent.network_client.signup(
            username=login,
            password=password,
            success_callback=lambda: parent.auth(login, password),
            fail_callback=lambda msg: (parent.error_alert.show_message(msg)),
        )


class AuthScreen(Group):
    SIZE = (450, 550)

    def __init__(self, network_client: NetworkClient, error: str = ""):
        super(AuthScreen, self).__init__()

        self.network_client = network_client

        self.screen = pg.display.set_mode(self.SIZE)
        pg.display.set_caption("DOM Auth")

        self.login_group = Login(self)
        self.signup_group = Signup(self)
        self.show_login_group()

        self.error_alert = InfoAlert(self, self.SIZE, int(self.SIZE[0] * 0.9))
        if error:
            self.error_alert.show_message(error)

        self.running = True
        self.finish_status: str = FinishStatus.close

    def show_login_group(self) -> None:
        """
        Отображает интерфейс авторизации.
        """
        self.signup_group.disable()
        self.signup_group.hide()
        self.login_group.enable()
        self.login_group.show()

    def show_signup_group(self) -> None:
        """
        Отображает интерфейс регистрации.
        """
        self.login_group.disable()
        self.login_group.hide()
        self.signup_group.enable()
        self.signup_group.show()

    def auth(self, login: str, password: str) -> None:
        """
        Завершает авторизацию пользователя.
        Сохраняет данные от аккаунта.
        :param login: Имя пользователя.
        :param password: Пароль.
        """
        with open(os.environ["AUTH_PATH"], "w", encoding="utf-8") as file:
            file.write(f"{login}\n{password}")

        self.finish_status = FinishStatus.ok
        self.terminate()

    def exec(self) -> str:
        """
        :return: FinishStatus.
        """
        while self.running:  # Цикл окна
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                self.handle_event(event)
            self.render()
        return self.finish_status

    def render(self) -> None:
        """
        Отрисовка интерфейса.
        """
        self.screen.fill("white")
        self.draw(self.screen)
        pg.display.flip()

    def terminate(self) -> None:
        """
        Остановка приложения.
        """
        self.running = False
