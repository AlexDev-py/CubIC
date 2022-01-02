"""

Интерфейс авторизации и регистрации.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg

from base import (
    Group,
    Alert,
    Text,
    Button,
    Label,
    WidgetsGroup,
    InputLine,
    Anchor,
    PasswordInputLine,
)
from base.text_filters import LengthTextFilter, AlphabetTextFilter
from utils import FinishStatus, check_password

if ty.TYPE_CHECKING:
    from network import NetworkClient
    from base.types import CordFunction
    from base.text_filters import BaseTextFilter


class InputBox(WidgetsGroup):
    def __init__(
        self,
        parent: Group,
        *,
        x: int | CordFunction,
        y: int | CordFunction,
        description: str,
        width: int | CordFunction | None = None,
        height: int | CordFunction | None = None,
        text: str | None = None,
        padding: int = 0,
        color: pg.Color = pg.Color(255, 255, 255),
        inactive_background: pg.Color | None = None,
        active_background: pg.Color | None = None,
        font: pg.font.Font = pg.font.Font(None, 20),
        anchor: Anchor = Anchor.left,
        inactive_border_color: pg.Color = pg.Color(255, 255, 255),
        active_border_color: pg.Color = pg.Color(255, 255, 255),
        border_width: int = 0,
        text_filter: BaseTextFilter | None = None,
        password: True | False = False,
    ):
        super(InputBox, self).__init__(parent, x=x, y=y)

        self.description = Label(
            self,
            x=0,
            y=0,
            text=description,
            color=color,
            font=font,
        )

        self.input_line = (InputLine if not password else PasswordInputLine)(
            self,
            x=0,
            y=self.description.rect.bottom + 5,
            width=width,
            height=height,
            text=text,
            padding=padding,
            color=color,
            inactive_background=inactive_background,
            active_background=active_background,
            font=font,
            anchor=anchor,
            inactive_border_color=inactive_border_color,
            active_border_color=active_border_color,
            border_width=border_width,
            text_filter=text_filter,
        )


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
            password=True,
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
            fail_callback=lambda msg: (parent.error_alert.show_error(msg)),
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
            text_filter=LengthTextFilter(30)
            & AlphabetTextFilter(
                ["_", "-"], nums=True, eng=True, rus=True, ignore_case=True
            ),
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
            password=True,
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
            password=True,
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
            parent.error_alert.show_error("Пароли не совпадают")
            return
        if not check_password(password):
            parent.error_alert.show_error("Пароль слишком легкий")
            return

        self.disable()
        parent.network_client.signup(
            username=login,
            password=password,
            success_callback=lambda: parent.auth(login, password),
            fail_callback=lambda msg: (parent.error_alert.show_error(msg)),
        )


class ErrorAlert(Alert):
    """
    Виджет, для отображения ошибки авторизации.
    """

    def __init__(self, parent: AuthScreen):
        super(ErrorAlert, self).__init__(
            parent,
            parent_size=parent.SIZE,
            padding=20,
            background=pg.Color("black"),
            fogging=100,
        )

        self._text = Text(
            self,
            x=0,
            y=0,
            width=int(parent.SIZE[0] * 0.9),
            text="err",
            color=pg.Color("red"),
            font=pg.font.Font(None, 30),
            soft_split=True,
        )

        self.continue_button = Button(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=lambda obj: self._text.rect.bottom + 20,
            text="ок",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, 25),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.hide(),
        )

    def show_error(self, text: str) -> None:
        self._text.text = text
        self.show()


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

        self.error_alert = ErrorAlert(self)
        if error:
            self.error_alert.show_error(error)

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
