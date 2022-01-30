"""

Интерфейсы взаимодействия с лобби.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg
from loguru import logger

from base import Button, WidgetsGroup, Group, Label, Anchor, Text
from base.events import ButtonClickEvent
from database.field_types import Resolution
from game.character import characters
from utils import load_image, DropMenu, InfoAlert

if ty.TYPE_CHECKING:
    from network import NetworkClient
    from game.player import Player
    from game.character import Character


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

        self.player = player

        super(PlayerWidget, self).__init__(
            parent,
            x=0,
            y=y,
        )

        self.icon = Label(
            self,
            x=0,
            y=0,
            width=icon_size,
            height=icon_size,
            anchor=Anchor.center,
            sprite=load_image(
                f"icon_{player.icon}.png",
                namespace=os.environ["USER_ICONS_PATH"],
                size=(icon_size - 2, icon_size - 2),
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

        if player.character is not ...:
            self.set_character()

    def set_status(self) -> None:
        self.status.text = "Готов" if self.player.ready else "Не готов..."

    def set_character(self) -> None:
        icon_size = int(os.environ["icon_size"])
        self.icon.sprite = load_image(
            self.player.character.icon,
            namespace=os.environ["CHARACTERS_PATH"],
            size=(icon_size, icon_size),
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


class CharacterButton(WidgetsGroup):
    def __init__(
        self, parent: CharactersMenu, y: int, character: Character, character_id: int
    ):
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])

        self.pressed = False
        self.character_id = character_id

        super(CharacterButton, self).__init__(parent, x=0, y=y)

        self.icon = Label(
            self,
            x=0,
            y=lambda obj: round(self.rect.height / 2 - obj.rect.height / 2),
            width=icon_size,
            height=icon_size,
            sprite=load_image(
                character.icon,
                namespace=os.environ["CHARACTERS_PATH"],
                size=(icon_size, icon_size),
            ),
        )

        self.name = Label(
            self,
            x=self.icon.rect.right + 10,
            y=lambda obj: round(self.rect.height / 2 - obj.rect.height / 2),
            text=character.name,
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

    def handle_event(self, event: pg.event.Event) -> None:
        super(CharacterButton, self).handle_event(event)
        if self.enabled:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    rect = self.get_global_rect()
                    if rect.collidepoint(event.pos):
                        self.pressed = True
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_LEFT:
                    if self.pressed:
                        self.pressed = False
                        rect = self.get_global_rect()
                        if rect.collidepoint(event.pos):
                            event = ButtonClickEvent(self)  # noqa
                            event.post()


class CharactersMenu(WidgetsGroup):
    def __init__(self, parent: Lobby):
        font_size = int(os.environ["font_size"])
        icon_size = int(os.environ["icon_size"])

        super(CharactersMenu, self).__init__(parent, x=0, y=0, padding=20)

        self.label = Label(
            self,
            x=0,
            y=0,
            text="Выбор персонажа",
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

        self.characters = []
        for i, character in enumerate(characters):
            self.characters.append(
                CharacterButton(
                    self,
                    y=self.label.rect.bottom + icon_size * i + 10 * (i + 1),
                    character=character,
                    character_id=i,
                )
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
        self._players: list[PlayerWidget] = []
        self.buttons: Buttons = ...
        self.characters_menu = CharactersMenu(self)

        self.network_client.on_ready(
            callback=lambda uid: self.on_set_ready(uid, status=True)
        )
        self.network_client.on_no_ready(
            callback=lambda uid: self.on_set_ready(uid, status=False)
        )
        self.network_client.on_character_selection(callback=self.on_character_selection)

        self.info_alert = InfoAlert(
            parent, parent_size=resolution, width=int(resolution.width * 0.5)
        )

    def on_set_ready(self, uid: int, status: True | False) -> None:
        widgets = [widget for widget in self._players if widget.player.uid == uid]
        if len(widgets):
            widget = widgets[0]
            self.network_client.room.get_by_uid(uid).ready = True
            if uid == self.network_client.user.uid:
                self.buttons.ready_button.text = widget.status.text
            widget.player.ready = status
            widget.set_status()

    def on_character_selection(self, uid: int, character_id: int) -> None:
        widgets = [widget for widget in self._players if widget.player.uid == uid]
        if len(widgets):
            widget = widgets[0]
            player = self.network_client.room.get_by_uid(uid)
            player.select_character(character_id)
            widget.set_character()

    def init(self) -> None:
        """
        Обновляем лобби.
        """
        if self.players is not ...:
            self.remove(self.players)
            self._players.clear()
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
            y = player_widget.rect.bottom + 20
            self._players.append(player_widget)

        self.buttons = Buttons(self)

    def handle_event(self, event: pg.event.Event) -> None:
        super(Lobby, self).handle_event(event)
        if event.type == ButtonClickEvent.type:
            if self.buttons is not ...:
                if event.obj == self.buttons.ready_button:
                    player = self.network_client.room.get_by_uid(
                        self.network_client.user.uid
                    )
                    if player.character is ...:
                        self.info_alert.show_message("Вы не выбрали персонажа")
                    else:
                        if player.is_owner:
                            player.ready = True
                            self.start_game()
                        else:
                            if not player.ready:
                                self.network_client.ready()
                            else:
                                self.network_client.no_ready()
            if event.obj in self.characters_menu.characters:
                player = self.network_client.room.get_by_uid(
                    self.network_client.user.uid
                )
                if (
                    player.character is ...
                    or player.character.name != event.obj.name.text
                ):
                    logger.opt(colors=True).info(
                        f"Выбран персонаж: <y>{event.obj.name.text}</y>"
                    )
                    self.network_client.select_character(event.obj.character_id)

    def start_game(self) -> None:
        if not all(widget.player.ready for widget in self._players):
            self.info_alert.show_message("Не все игроки готовы")
        else:
            self.network_client.start_game()
