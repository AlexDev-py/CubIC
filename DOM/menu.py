from __future__ import annotations

import os
import typing as ty

import pygame as pg
from loguru import logger

from base import Button, WidgetsGroup, Group, Label, Anchor, Line
from database.field_types import Resolution, ALLOWED_RESOLUTION
from settings_alert import Settings
from utils import load_image

if ty.TYPE_CHECKING:
    from network import User, NetworkClient


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
            callback=lambda event: print("create lobby"),
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


class UserWidget(WidgetsGroup):
    def __init__(self, parent: Social, y: int, user: User):
        super(UserWidget, self).__init__(
            parent,
            x=0,
            y=y,
            padding=20,
        )

        self.icon = Label(
            self,
            x=0,
            y=0,
            width=50,
            height=50,
            anchor=Anchor.center,
            sprite=load_image(rf"icons\icon_{user.icon}.png", (45, 45)),
        )

        self.username = Label(
            self,
            x=self.icon.rect.right + 30,
            y=0,
            text=user.username,
            color=pg.Color("red"),
            font=pg.font.Font(None, MenuScreen.font_size),
        )

        self.status = Label(
            self,
            x=self.icon.rect.right + 30,
            y=self.username.rect.bottom + 5,
            text="оффлайн",
            color=pg.Color("gray"),
            font=pg.font.Font(None, int(MenuScreen.font_size / 2)),
        )


class Social(WidgetsGroup):
    def __init__(self, parent: MenuScreen):
        super(Social, self).__init__(
            parent,
            x=lambda obj: parent.resolution[0] - obj.rect.width,
            y=0,
            width=int(parent.resolution[0] * 0.2),
            height=parent.resolution[1],
            border_color=pg.Color("red"),
            border_width=5,
        )

        self.user = UserWidget(self, y=0, user=parent.network_client.user)
        self.line = Line(
            self,
            x=0,
            y=self.user.rect.bottom,
            width=self.rect.width,
            height=5,
            color=pg.Color("red"),
        )

        self.friends_label = Label(
            self,
            x=lambda obj: round(self.rect.width / 2 - obj.rect.width / 2),
            y=self.line.rect.botom,
            text="Друзья",
            color=pg.Color("red"),
            font=pg.font.Font(None, int(MenuScreen.font_size * 0.8)),
        )

        self.friends = [...]


class MenuScreen(Group):
    resolution = Resolution.converter(os.environ["resolution"])
    font_size = 20

    def __init__(self, network_client: NetworkClient):
        super(MenuScreen, self).__init__()
        self.network_client = network_client

        self.__class__.font_size = int(
            20 * (1 + ALLOWED_RESOLUTION.index(self.resolution) * 0.4)
        )  # Масштабируем размер текста в зависимости от размера окна

        # Если выставлено максимально возможное разрешение, открываем окно в полный экран
        if self.resolution >= Resolution.converter(os.environ["MAX_RESOLUTION"]):
            self.screen = pg.display.set_mode(self.resolution, pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode(self.resolution)

        self.buttons = MenuButtons(self)
        self.social = Social(self)
        self.setting = Settings(self)

        self.running = True

    def exec(self) -> ty.NoReturn:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.terminate()
                self.handle_event(event)
            self.render()

    def render(self) -> None:
        self.screen.fill("white")
        self.draw(self.screen)

        pg.display.flip()

    def terminate(self) -> None:
        self.running = False

    def change_resolution(self, resolution: Resolution) -> None:
        """
        Изменяет разрешение окна.
        :param resolution: Новое разрешение.
        """
        logger.opt(colors=True).debug(
            "Изменение разрешения "
            f"<y>{str(self.resolution)}</y> -> <c>{str(resolution)}</c>"
        )
        self.__class__.resolution = resolution

        self.__init__(self.network_client)
        self.setting.show()

        if ALLOWED_RESOLUTION.index(resolution) == 0:
            self.setting.resolution_setting.btn_low.disable()
        elif ALLOWED_RESOLUTION.index(resolution) == len(ALLOWED_RESOLUTION) - 1:
            self.setting.resolution_setting.btn_up.disable()
        else:
            self.setting.resolution_setting.btn_low.enable()
            self.setting.resolution_setting.btn_up.enable()
