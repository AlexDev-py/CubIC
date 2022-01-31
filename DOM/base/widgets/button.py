from __future__ import annotations

import typing as ty

import pygame as pg
from loguru import logger

from .label import Label
from ..anchor import Anchor
from ..events import ButtonClickEvent

if ty.TYPE_CHECKING:
    from ..types import CordFunction, ButtonCallback
    from ..group import Group


class Button(Label):
    def __init__(
        self,
        parent: Group,
        name: str = None,
        *,
        x: int | CordFunction,
        y: int | CordFunction,
        width: int | CordFunction | None = None,
        height: int | CordFunction | None = None,
        text: str | None = None,
        sprite: pg.Surface | None = None,
        padding: int = 0,
        color: pg.Color = pg.Color(255, 255, 255),
        inactive_background: pg.Color | None = None,
        active_background: pg.Color | None = None,
        font: pg.font.Font = pg.font.Font(None, 20),
        anchor: Anchor = Anchor.left,
        border_color: pg.Color = pg.Color(255, 255, 255),
        border_width: int = 0,
        callback: ButtonCallback | None = None,
    ):
        """
        Кнопка.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
         родителем которых является Group.
        :param name: Название объекта.
        :param x: Координата x.
        :type x: Число или функция вычисляющая координату.
        :param y: Координата y.
        :type y: Число или функция вычисляющая координату.
        :param width: Ширина виджета.
        :type width: Число или функция вычисляющая ширину.
        :param height: Высота виджета.
        :type height: Число или функция вычисляющая высоту.
        :param text: Текст.
        :param sprite: Картинка.
        :param padding: Отступы от границ виджета.
        :param color: Цвет текста.
        :param inactive_background: Цвет фона в обычном состоянии.
        :param active_background: Цвет фона при нажатии.
        :param font: Шрифт.
        :param anchor: Привязка к краю или центру.
        :param border_color: Цвет обводки виджета.
        :param border_width: Ширина обводки.
        :param callback: Функция - обработчик нажатия на кнопку.
        :type callback: Функция принимающая 1 позиционный аргумент -
         событие нажатия на кнопку (ButtonClickEvent) и возвращающая любое значение.
        """
        super(Button, self).__init__(
            parent,
            name,
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            sprite=sprite,
            padding=padding,
            color=color,
            background=inactive_background,
            font=font,
            anchor=anchor,
            border_color=border_color,
            border_width=border_width,
        )

        self._inactive_background = inactive_background
        self._active_background = active_background
        self._callback = callback
        self._pressed = False

    def handle_event(self, event: pg.event.Event) -> None:
        if self.enabled:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_LEFT:
                    rect = self.get_global_rect()
                    if rect.collidepoint(event.pos):
                        self.pressed = True
                        logger.opt(colors=True).trace(
                            f"Кнопка <y>{self.text}</y> нажата"
                        )
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_LEFT:
                    if self.pressed:
                        self.pressed = False
                        rect = self.get_global_rect()
                        if rect.collidepoint(event.pos):
                            logger.opt(colors=True).debug(
                                f"Кнопка <y>{self.text}</y> нажата"
                            )
                            event = ButtonClickEvent(self)
                            event.post()
                            if self.callback:
                                self.callback(event)

    @property
    def inactive_background(self) -> pg.Color:
        return self._inactive_background

    @inactive_background.setter
    def inactive_background(self, value: pg.Color):
        self._inactive_background = value

    @property
    def active_background(self) -> pg.Color:
        return self._active_background

    @active_background.setter
    def active_background(self, value: pg.Color):
        self._active_background = value

    @property
    def callback(self) -> ButtonCallback | None:
        return self._callback

    @callback.setter
    def callback(self, value: ButtonCallback | None):
        self._callback = value

    @property
    def pressed(self) -> True | False:
        return self._pressed

    @pressed.setter
    def pressed(self, value: True | False):
        self.background = self.active_background if value else self.inactive_background
        self._pressed = value
