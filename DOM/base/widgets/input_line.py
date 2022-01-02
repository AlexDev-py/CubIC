from __future__ import annotations

import typing as ty

import pygame as pg

from .label import Label
from ..anchor import Anchor

if ty.TYPE_CHECKING:
    from ..types import CordFunction
    from ..text_filters import BaseTextFilter
    from ..group import Group


class InputLine(Label):
    def __init__(
        self,
        parent: Group,
        *,
        x: int | CordFunction,
        y: int | CordFunction,
        width: int | CordFunction | None = None,
        height: int | CordFunction | None = None,
        text: str | None = None,
        padding: int = 0,
        color: pg.Color = pg.Color(255, 255, 255),
        inactive_background: pg.Color | None = None,
        active_background: pg.Color | None = None,
        font: pg.font.Font = pg.font.Font(None, 20),
        anchor: Anchor = Anchor.left,
        inactive_border_color: pg.Color = pg.Color("gray"),
        active_border_color: pg.Color = pg.Color("black"),
        border_width: int = 5,
        text_filter: BaseTextFilter | None = None,
    ):
        """
        Виджет для ввода однострочного текста.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
         родителем которых является Group.
        :param x: Координата x.
        :type x: Число или функция вычисляющая координату.
        :param y: Координата y.
        :type y: Число или функция вычисляющая координату.
        :param width: Ширина виджета.
        :type width: Число или функция вычисляющая ширину.
        :param height: Высота виджета.
        :type height: Число или функция вычисляющая высоту.
        :param text: Текст.
        :param padding: Отступы от границ виджета.
        :param color: Цвет текста.
        :param inactive_background: Цвет фона в обычном состоянии.
        :param active_background: Цвет фона при нажатии.
        :param font: Шрифт.
        :param anchor: Привязка к краю или центру.
        :param inactive_border_color: Цвет обводки виджета в обычном состоянии.
        :param active_border_color: Цвет обводки виджета при нажатии.
        :param border_width: Ширина обводки.
        :param text_filter: Фильтры, которые применятся к вводимому тексту.
        """
        super(InputLine, self).__init__(
            parent,
            x=x,
            y=y,
            width=width,
            height=height,
            text=text or "",
            padding=padding,
            color=color,
            background=inactive_background,
            font=font,
            anchor=anchor,
            border_color=inactive_border_color,
            border_width=border_width,
        )

        self._inactive_background = inactive_background
        self._active_background = active_background
        self._inactive_border_color = inactive_border_color
        self._active_border_color = active_border_color
        self._text_filter = text_filter
        self._active = False

    def handle_event(self, event: pg.event.Event) -> None:
        if self.enabled:
            # При нажатии на виджет, активируется ввод
            if event.type == pg.MOUSEBUTTONDOWN:
                self.active = self.get_global_rect().collidepoint(event.pos)
            elif event.type == pg.KEYDOWN and self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = self._text[:-1]
                else:
                    if self._text_filter:
                        if not self._text_filter.validate(self._text + event.unicode):
                            return
                    self._text += event.unicode

    @property
    def active(self) -> True | False:
        return self._active

    @active.setter
    def active(self, value: True | False):
        self._active = value
        self.background = (
            self._active_background if value else self._inactive_background
        )
        self.border_color = (
            self._active_border_color if value else self._inactive_border_color
        )


class PasswordInputLine(InputLine):
    """
    Виджет для ввода пароля.
    """

    @property
    def text(self) -> str:
        return "*" * len(self._text)

    @text.setter
    def text(self, value: str):
        self._text = value

    def value(self) -> str:
        return self._text
