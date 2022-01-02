"""

Виджет настроек клиента.

"""

from __future__ import annotations

import typing as ty

import pygame as pg

from base import Button, WidgetsGroup, Alert, Label
from base.events import ButtonClickEvent
from database.field_types import ALLOWED_RESOLUTION

if ty.TYPE_CHECKING:
    from menu import MenuScreen


class Settings(Alert):
    def __init__(self, parent: MenuScreen):
        super(Settings, self).__init__(
            parent,
            parent_size=parent.resolution,
            width=int(parent.resolution[0] * 0.6),
            height=int(parent.resolution[1] * 0.8),
            padding=20,
            background=pg.Color("black"),
            fogging=100,
        )

        self._parent = parent

        self.exit_btn = Button(
            self,
            x=0,
            y=0,
            text=" X ",
            padding=5,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, int(parent.font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
            callback=lambda event: self.hide(),
        )

        self.resolution_setting = ResolutionSetting(
            self,
            y=self.exit_btn.rect.bottom + 30,
            font_size=parent.font_size,
            resolution=str(parent.resolution),
        )

        self.parent.update()

    def handle_event(self, event: pg.event.Event) -> None:
        super(Settings, self).handle_event(event)
        if event.type == ButtonClickEvent.type:
            if event.obj == self.resolution_setting.btn_low:
                self._parent.change_resolution(
                    ALLOWED_RESOLUTION[
                        ALLOWED_RESOLUTION.index(self._parent.resolution) - 1
                    ]
                )
            elif event.obj == self.resolution_setting.btn_up:
                self._parent.change_resolution(
                    ALLOWED_RESOLUTION[
                        ALLOWED_RESOLUTION.index(self._parent.resolution) + 1
                    ]
                )


class ResolutionSetting(WidgetsGroup):
    """
    Настройки разрешения.
    """

    def __init__(self, parent: Settings, y: int, font_size: int, resolution: str):
        super(ResolutionSetting, self).__init__(parent, x=0, y=y)

        self.label = Label(
            self,
            x=0,
            y=0,
            text="Разрешение:",
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

        self.btn_low = Button(
            self,
            x=self.label.rect.right + 20,
            y=0,
            text=" < ",
            padding=2,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, int(font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
        )

        self.resolution = Label(
            self,
            x=self.btn_low.rect.right + 10,
            y=lambda obj: round(self.btn_low.rect.height / 2 - obj.rect.height / 2),
            text=str(resolution),
            color=pg.Color("red"),
            font=pg.font.Font(None, font_size),
        )

        self.btn_up = Button(
            self,
            x=self.resolution.rect.right + 10,
            y=0,
            text=" > ",
            padding=2,
            color=pg.Color("red"),
            active_background=pg.Color("#171717"),
            font=pg.font.Font(None, int(font_size * 0.7)),
            border_color=pg.Color("red"),
            border_width=2,
        )
