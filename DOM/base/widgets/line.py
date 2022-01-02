from __future__ import annotations

import typing as ty
from inspect import isfunction

import pygame as pg

from ..widget import BaseWidget

if ty.TYPE_CHECKING:
    from ..types import CordFunction
    from ..group import Group


class Line(BaseWidget):
    def __init__(
        self,
        parent: Group,
        *,
        x: int | CordFunction,
        y: int | CordFunction,
        width: int,
        height: int,
        color: pg.Color = pg.Color(255, 255, 255),
    ):
        """
        Виджет однострочного текста.
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
        :param color: Цвет текста.
        """

        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._color = color

        super(Line, self).__init__(parent)

    def _get_rect(self) -> pg.Rect:
        self.rect = pg.Rect(0, 0, self.width, self.height)
        self.rect.x, self.rect.y = self.x, self.y
        return self.rect

    def _render(self) -> pg.Surface:
        image = pg.Surface(self.rect.size, pg.SRCALPHA, 32).convert_alpha()
        pg.draw.rect(image, self.color, image.get_rect())
        return image

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
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value

    @property
    def color(self) -> pg.Color:
        return self._color

    @color.setter
    def color(self, value: pg.Color):
        self._color = value
