"""

Меню клиента.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg

from base import Button, WidgetsGroup, Group
from base.events import ButtonClickEvent
from database.field_types import Resolution, ALLOWED_RESOLUTION
from lobby import Lobby, LobbyInvite
from settings_alert import Settings
from social import Social
from utils import InfoAlert

if ty.TYPE_CHECKING:
    from network import NetworkClient


class MenuButtons(WidgetsGroup):
    def __init__(self, parent: MenuScreen):
        super(MenuButtons, self).__init__(
            parent,
            x=0,
            y=lambda obj: parent.resolution[1] - obj.rect.height,
            padding=20,
        )

        self.create_lobby_button = Button(
            self,
            x=0,
            y=0,
            width=int(parent.resolution[0] * 0.15),
            text="Создать лобби",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color(0, 0, 0, 50),
            font=pg.font.Font(None, MenuScreen.font_size),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: (
                self.disable(),
                parent.network_client.create_lobby(
                    callback=lambda: (parent.open_lobby())
                ),
            ),
        )

        self.settings_button = Button(
            self,
            x=0,
            y=lambda btn: self.create_lobby_button.rect.y + 20 + btn.rect.h,
            width=int(parent.resolution[0] * 0.15),
            text="Настройки",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color(0, 0, 0, 50),
            font=pg.font.Font(None, MenuScreen.font_size),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: parent.setting.show(),
        )

        self.exit_button = Button(
            self,
            x=0,
            y=lambda btn: self.settings_button.rect.y + 20 + btn.rect.h,
            width=int(parent.resolution[0] * 0.15),
            text="Выйти",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color(0, 0, 0, 50),
            font=pg.font.Font(None, MenuScreen.font_size),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: parent.terminate(),
        )


class MenuScreen(Group):
    resolution = Resolution.converter(os.environ["resolution"])

    # TODO: нужно полностью перейти на os.environ
    font_size = 20
    icon_size = 25

    def __init__(self, network_client: NetworkClient = None):
        super(MenuScreen, self).__init__()
        self.network_client = (
            self.network_client if hasattr(self, "network_client") else network_client
        )

        self.__class__.font_size = int(
            20 * (1 + ALLOWED_RESOLUTION.index(self.resolution) * 0.4)
        )  # Масштабируем размер текста в зависимости от размера окна
        os.environ["font_size"] = str(self.__class__.font_size)

        self.__class__.icon_size = int(
            25 * (1 + ALLOWED_RESOLUTION.index(self.resolution) * 0.4)
        )  # Масштабируем размер текста в зависимости от размера окна
        os.environ["icon_size"] = str(self.__class__.icon_size)

        # Если выставлено максимально возможное разрешение, открываем окно в полный экран
        if self.resolution >= Resolution.converter(os.environ["MAX_RESOLUTION"]):
            self.screen = pg.display.set_mode(self.resolution, pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode(self.resolution)

        self.buttons = MenuButtons(self)
        self.lobby = Lobby(self, network_client)
        self.social = Social(self, self.network_client)
        self.setting = Settings(self)

        self.info_alert = InfoAlert(
            self,
            parent_size=self.resolution,
            width=int(self.resolution.width * 0.5),
        )

        self.running = True
        self.lobby_invite: LobbyInvite = ...

        # Подключаем обработчики событий
        self.network_client.on_lobby_invite(callback=self.on_lobby_invite)
        self.network_client.on_joining_the_lobby(callback=self.lobby.init)
        self.network_client.on_leaving_the_lobby(
            callback=lambda msg: (self.lobby.init(), self.info_alert.show_message(msg))
        )
        self.network_client.on_error(callback=self.info_alert.show_message)

    def on_lobby_invite(self, msg: str, room_id: int) -> None:
        """
        Приглашение в лобби.
        :param msg: Сообщение.
        :param room_id: ID лобби.
        """
        if self.lobby_invite is not ...:  # Удаляем старое приглашение
            self.remove(self.lobby_invite)
            self.lobby_invite: LobbyInvite = ...
        self.lobby_invite = LobbyInvite(self.social, msg, room_id)

    def open_lobby(self) -> None:
        """
        Скрывает кнопки меню и открывает лобби.
        """
        self.buttons.hide(),
        self.buttons.disable(),
        self.lobby.init(),
        self.lobby.show(),
        self.lobby.enable(),

    def exec(self) -> ty.NoReturn:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                elif event.type == ButtonClickEvent.type:
                    # Обработка нажатий на кнопки
                    if self.lobby_invite is not ...:
                        # Обработка взаимодействия с приглашением в лобби
                        if event.obj == self.lobby_invite.cancel:
                            self.remove(self.lobby_invite)  # Удаляем приглашение
                            self.lobby_invite: LobbyInvite = ...
                        elif event.obj == self.lobby_invite.accept:
                            self.remove(self.lobby_invite)  # Удаляем приглашение
                            self.network_client.join_lobby(
                                self.lobby_invite.room_id,
                                success_callback=self.open_lobby,
                                fail_callback=lambda msg: self.info_alert.show_message(
                                    msg
                                ),
                            )  # Присоединяемся к лобби
                            self.lobby_invite: LobbyInvite = ...
                    if self.lobby.buttons is not ...:
                        # Обработка кнопок в лобби
                        if event.obj == self.lobby.buttons.leave_lobby_button:
                            self.network_client.leave_lobby()
                            self.lobby.disable()
                            self.lobby.hide()
                            self.buttons.show()
                            self.buttons.enable()

                self.handle_event(event)
            self.render()

    def render(self) -> None:
        self.screen.fill("white")
        self.draw(self.screen)

        pg.display.flip()

    def terminate(self) -> None:
        self.running = False
