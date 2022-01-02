from __future__ import annotations

import os
import typing as ty

import pygame as pg
from loguru import logger

from base import Button, WidgetsGroup, Group
from database.field_types import Resolution, ALLOWED_RESOLUTION
from settings_alert import Settings


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


class MenuScreen(Group):
    resolution = Resolution.converter(os.environ["resolution"])
    font_size = 20

    def __init__(self):
        super(MenuScreen, self).__init__()
        self.__class__.font_size = int(
            20 * (1 + ALLOWED_RESOLUTION.index(self.resolution) * 0.4)
        )  # Масштабируем размер текста в зависимости от размера окна

        # Если выставлено максимально возможное разрешение, открываем окно в полный экран
        if self.resolution >= Resolution.converter(os.environ["MAX_RESOLUTION"]):
            self.screen = pg.display.set_mode(self.resolution, pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode(self.resolution)

        self.buttons = MenuButtons(self)
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

        self.__init__()
        self.setting.show()

        if ALLOWED_RESOLUTION.index(resolution) == 0:
            self.setting.resolution_setting.btn_low.disable()
        elif ALLOWED_RESOLUTION.index(resolution) == len(ALLOWED_RESOLUTION) - 1:
            self.setting.resolution_setting.btn_up.disable()
        else:
            self.setting.resolution_setting.btn_low.enable()
            self.setting.resolution_setting.btn_up.enable()
