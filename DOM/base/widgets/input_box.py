"""

Интерфейс авторизации и регистрации.

"""

from __future__ import annotations

import typing as ty

import pygame as pg

from .input_line import InputLine, PasswordInputLine
from .label import Label
from .widgets_group import WidgetsGroup
from ..anchor import Anchor

if ty.TYPE_CHECKING:
    from ..group import Group
    from ..types import CordFunction
    from ..text_filters import BaseTextFilter


class InputBox(WidgetsGroup):
    def __init__(
        self,
        parent: Group,
        name: str = None,
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
        is_password: True | False = False,
    ):
        super(InputBox, self).__init__(parent, name, x=x, y=y)

        self.description = Label(
            self,
            x=0,
            y=0,
            text=description,
            color=color,
            font=font,
        )

        self.input_line = (InputLine if not is_password else PasswordInputLine)(
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
