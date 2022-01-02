from __future__ import annotations

import typing as ty
from inspect import isfunction

import pygame as pg

from ..group import Group
from ..widget import BaseWidget

if ty.TYPE_CHECKING:
    from ..types import CordFunction


class WidgetsGroup(Group, BaseWidget):
    def __init__(
        self,
        parent: Group,
        *,
        x: int | CordFunction,
        y: int | CordFunction,
        width: int | CordFunction | None = None,
        height: int | CordFunction | None = None,
        padding: int = 0,
        background: pg.Color | None = None,
        border_color: pg.Color = pg.Color(255, 255, 255),
        border_width: int = 0,
        hidden: True | False = False,
    ):
        """
        Виджет - группа.
        Объединяет несколько объектов.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param x: Координата x.
        :type x: Число или функция вычисляющая координату.
        :param y: Координата y.
        :type y: Число или функция вычисляющая координату.
        :param width: Ширина виджета.
        :type width: Число или функция вычисляющая ширину.
        :param height: Высота виджета.
        :type height: Число или функция вычисляющая высоту.
        :param padding: Отступы от границ виджета.
        :param background: Цвет фона.
        :param border_color: Цвет обводки виджета.
        :param border_width: Ширина обводки.
        :param hidden: Будет ли группа скрыта.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._padding = padding
        self._background = background
        self._border_color = border_color
        self._border_width = border_width

        Group.__init__(self, parent, hidden=hidden)
        BaseWidget.__init__(self, parent, hidden=hidden)

    def _get_rect(self) -> pg.Rect:
        widgets = [
            obj
            for obj in self.widgets
            if isinstance(obj, BaseWidget) and hasattr(obj, "rect")
        ]
        if widgets:
            top = min(widgets, key=lambda widget: widget.rect.top).rect.top
            bottom = max(widgets, key=lambda widget: widget.rect.bottom).rect.bottom
            left = min(widgets, key=lambda widget: widget.rect.left).rect.left
            right = max(widgets, key=lambda widget: widget.rect.right).rect.right
        else:
            top = bottom = left = right = 0

        self.rect = pg.Rect(
            0,
            0,
            +(
                (self.padding * 2 + right - left + self.border_width * 2)
                if self.width is None or isfunction(self._width)
                else self.width
            ),
            +(
                (self.padding * 2 + bottom - top + self.border_width * 2)
                if self.height is None or isfunction(self._height)
                else self.height
            ),
        )

        self.rect.width = self.width or self.rect.width
        self.rect.height = self.height or self.rect.height
        self.rect.x, self.rect.y = self.x, self.y
        return self.rect

    def _render(self) -> pg.Surface:
        size = tuple(
            n - self.padding * 2 - self.border_width * 2 for n in self.rect.size
        )
        bg_image = pg.Surface(self.rect.size, pg.SRCALPHA, 32).convert_alpha()
        content_image = pg.Surface(size, pg.SRCALPHA, 32).convert_alpha()

        if self.background:
            pg.draw.rect(bg_image, self.background, bg_image.get_rect())
        if self.border_width:
            rect = bg_image.get_rect().copy()
            rect.width -= int(self.border_width / 2)
            rect.height -= int(self.border_width / 2)
            pg.draw.rect(bg_image, self._border_color, rect, self.border_width)

        for widget in self.widgets:
            widget.draw(content_image)

        rect = bg_image.get_rect()
        rect.x = rect.y = self.padding + self.border_width
        bg_image.blit(content_image, rect)

        return bg_image

    def update(self, *args, **kwargs) -> None:
        if hasattr(self, "_widgets"):
            for widget in self.widgets:
                widget.update(*args, **kwargs)
            BaseWidget.update(self, *args, **kwargs)

    def draw(self, surface: pg.Surface) -> None:
        BaseWidget.draw(self, surface)

    @property
    def x(self) -> int:
        return self._x(self) if isfunction(self._x) else self._x

    @x.setter
    def x(self, value: int | CordFunction):
        self._x = value

    @property
    def y(self) -> int:
        return self._y(self) if isfunction(self._y) else self._y

    @y.setter
    def y(self, value: int | CordFunction):
        self._y = value

    @property
    def width(self) -> int | None:
        if isfunction(self._width):
            return self._width(self)
        return self._width

    @width.setter
    def width(self, value: int | CordFunction):
        self._width = value

    @property
    def height(self) -> int | None:
        if isfunction(self._height):
            return self._height(self)
        return self._height

    @height.setter
    def height(self, value: int | CordFunction):
        self._height = value

    @property
    def padding(self) -> int:
        return self._padding

    @padding.setter
    def padding(self, value: int):
        self._padding = value

    @property
    def background(self) -> pg.Color:
        return self._background

    @background.setter
    def background(self, value: pg.Color):
        self._background = value

    @property
    def border_color(self) -> pg.Color:
        return self._border_color

    @border_color.setter
    def border_color(self, value: pg.Color):
        self._border_color = value

    @property
    def border_width(self) -> int:
        return self._border_width

    @border_width.setter
    def border_width(self, value: int):
        self._border_width = value
