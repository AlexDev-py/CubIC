"""

Виджет настроек клиента.

"""

from __future__ import annotations

import os
import typing as ty

import pygame as pg
from loguru import logger

from base import Button, WidgetsGroup, Alert, Label
from base.events import ButtonClickEvent
from database import Config
from database.field_types import ALLOWED_RESOLUTION, Resolution

if ty.TYPE_CHECKING:
    from base.group import Group


class Settings(Alert):
    def __init__(self, parent: Group):
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])
        font = os.environ.get("font")

        super(Settings, self).__init__(
            parent,
            "SettingsAlert",
            parent_size=resolution,
            width=int(resolution.width * 0.6),
            height=int(resolution.height * 0.8),
            padding=20,
            background=pg.Color("black"),
            fogging=100,
        )

        self.exit_btn = Button(
            self,
            f"{self.name}-ExitButton",
            x=0,
            y=0,
            text=" X ",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(font, int(font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.hide(),
        )

        self.resolution_setting = ResolutionSetting(
            self, y=self.exit_btn.rect.bottom + 30
        )

    def handle_event(self, event: pg.event.Event) -> None:
        super(Settings, self).handle_event(event)
        if event.type == ButtonClickEvent.type:
            # Обработка нажатий кнопок
            if event.obj == self.resolution_setting.btn_low:
                self.change_resolution(
                    ALLOWED_RESOLUTION[
                        ALLOWED_RESOLUTION.index(
                            Resolution.converter(os.environ["resolution"])
                        )
                        - 1
                    ]
                )
            elif event.obj == self.resolution_setting.btn_up:
                self.change_resolution(
                    ALLOWED_RESOLUTION[
                        ALLOWED_RESOLUTION.index(
                            Resolution.converter(os.environ["resolution"])
                        )
                        + 1
                    ]
                )

    def change_resolution(self, resolution: Resolution) -> None:
        """
        Изменяет разрешение окна.
        :param resolution: Новое разрешение.
        """
        logger.opt(colors=True).debug(
            "Изменение разрешения "
            f"<y>{str(Resolution.converter(os.environ['resolution']))}</y> "
            f"-> <c>{str(resolution)}</c>"
        )

        Config.update(resolution=resolution)
        self.init_interface_size()

        self._tab.parent.__init__()

    @classmethod
    def init_interface_size(cls) -> None:
        """
        Обновление размеров интерфейса в зависимости от разрешения окна.
        """
        resolution = Resolution.converter(os.environ["resolution"])

        os.environ["font_size"] = str(
            int(13 * (1 + ALLOWED_RESOLUTION.index(resolution) * 0.4))
        )  # Масштабируем размер текста в зависимости от размера окна

        os.environ["icon_size"] = str(
            int(25 * (1 + ALLOWED_RESOLUTION.index(resolution) * 0.4))
        )  # Масштабируем размер иконок в зависимости от размера окна

        os.environ["buttons_size"] = str(
            int(30 * (1 + ALLOWED_RESOLUTION.index(resolution) * 0.4))
        )  # Масштабируем размер кнопок в зависимости от размера окна


class ResolutionSetting(WidgetsGroup):
    """
    Настройки разрешения.
    """

    def __init__(self, parent: Settings, y: int):
        resolution = Resolution.converter(os.environ["resolution"])
        font_size = int(os.environ["font_size"])
        font = os.environ.get("font")

        super(ResolutionSetting, self).__init__(parent, "ResolutionSettings", x=0, y=y)

        self.title = Label(
            self,
            f"{self.name}-TitleLabel",
            x=0,
            y=0,
            text="Разрешение:",
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
        )

        self.btn_low = Button(
            self,
            f"{self.name}-ButtonLow",
            x=self.title.rect.right + 20,
            y=0,
            text=" < ",
            padding=2,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(font, int(font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
        )

        self.resolution = Label(
            self,
            f"{self.name}-ResolutionLabel",
            x=self.btn_low.rect.right + 10,
            y=lambda obj: round(self.btn_low.rect.height / 2 - obj.rect.height / 2),
            text=str(resolution),
            color=pg.Color("red"),
            font=pg.font.Font(font, font_size),
        )

        self.btn_up = Button(
            self,
            f"{self.name}-ButtonUp",
            x=self.resolution.rect.right + 10,
            y=0,
            text=" > ",
            padding=2,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(font, int(font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
        )

        # Скрываем кнопки
        if ALLOWED_RESOLUTION.index(resolution) == 0:
            self.btn_low.disable()
            self.btn_low.hide()
        elif ALLOWED_RESOLUTION.index(resolution) == len(ALLOWED_RESOLUTION) - 1:
            self.btn_up.disable()
            self.btn_up.hide()

        self.update()
