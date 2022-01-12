"""

Интерфейсы взаимодействия с лобби.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg

from base import Button, WidgetsGroup, Group, Label, Anchor, Text
from database.field_types import Resolution
from utils import load_image, DropMenu

if ty.TYPE_CHECKING:
    from network import NetworkClient
    from game.player import Player


class LobbyInvite(DropMenu):
    def __init__(self, parent: WidgetsGroup, msg: str, room_id: int):
        """
        Приглашение в лобби.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param msg: Сообщение.
        :param room_id: ID лобби.
        """
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])

        self.room_id = room_id

        super(LobbyInvite, self).__init__(
            parent,
            width=int(resolution.width * 0.3),
            padding=20,
            background=pg.Color("gray"),
        )

        self.msg = Text(
            self,
            x=0,
            y=0,
            width=self.width - self.padding * 2,
            text=msg,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
            soft_split=True,
        )

        self.accept = Button(
            self,
            x=0,
            y=self.msg.rect.bottom + 20,
            text="Принять",
            padding=3,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
            active_background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=3,
        )

        self.cancel = Button(
            self,
            x=self.accept.rect.right + 5,
            y=self.msg.rect.bottom + 20,
            text=" Х ",
            padding=3,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
            active_background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=3,
        )

        self.open((0, 0))  # Показываем виджет в верхнем левом углу

    def handle_event(self, event: pg.event.Event) -> None:
        """
        Отключаем активацию по нажатию на определенный виджет.
        :param event:
        :return:
        """
        WidgetsGroup.handle_event(self, event)


class PlayerWidget(WidgetsGroup):
    def __init__(self, parent: WidgetsGroup, player: Player, y: int):
        """
        Виджет игрока в лобби.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param player: Игрок.
        :param y: Координата Y.
        """
        icon_size = int(os.environ["icon_size"])
        font_size = int(os.environ["font_size"])

        super(PlayerWidget, self).__init__(
            parent,
            x=0,
            y=y,
            padding=10,
        )

        self.icon = Label(
            self,
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            anchor=Anchor.center,
            sprite=load_image(
                rf"icons\icon_{player.icon}.png",
                (icon_size - 2, icon_size - 2),
            ),
        )

        self.username = Label(
            self,
            x=self.icon.rect.w + 10,
            y=lambda obj: round(self.rect.height / 2 - obj.rect.height - 2),
            text=player.username,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

        self.status = Label(
            self,
            x=self.icon.rect.w + 10,
            y=round(self.rect.height / 2 + 2),
            text="Лидер" if player.is_owner else "Не готов...",
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )


class Buttons(WidgetsGroup):
    def __init__(self, parent: Lobby):
        font_size = int(os.environ["font_size"])

        super(Buttons, self).__init__(
            parent,
            x=lambda obj: round(parent.rect.w / 2 - obj.rect.w / 2),
            y=lambda obj: parent.rect.height - obj.rect.height,
            padding=20,
        )

        self.leave_lobby_button = Button(
            self,
            x=0,
            y=0,
            text=" Х ",
            padding=3,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
            active_background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=3,
        )

        is_owner = parent.network_client.room.get_by_uid(
            parent.network_client.user.uid
        ).is_owner
        self.ready_button = Button(
            self,
            x=self.leave_lobby_button.rect.w + 10,
            y=0,
            text="Начать игру" if is_owner else "Готов",
            padding=3,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
            active_background=pg.Color("gray"),
            border_color=pg.Color("red"),
            border_width=3,
        )


class Lobby(WidgetsGroup):
    def __init__(self, parent: Group, network_client: NetworkClient):
        """
        Интерфейс лобби.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param network_client: ...
        """
        resolution = Resolution.converter(os.environ["resolution"])

        self.network_client = network_client

        super(Lobby, self).__init__(
            parent,
            x=0,
            y=0,
            width=int(resolution.width * 0.8),
            height=resolution.height,
            hidden=True,
        )
        self.disable()

        self.players: WidgetsGroup = ...
        self.buttons: Buttons = ...

    def init(self) -> None:
        """
        Обновляем лобби.
        """
        if self.players is not ...:
            self.remove(self.players)
        if self.buttons is not ...:
            self.remove(self.buttons)

        self.players = WidgetsGroup(
            self,
            x=lambda obj: self.rect.width - obj.rect.width,
            y=0,
            padding=20,
        )

        y = 0
        for player in self.network_client.room.players:
            player_widget = PlayerWidget(self.players, player, y)
            y = player_widget.rect.bottom + 10

        self.buttons = Buttons(self)
