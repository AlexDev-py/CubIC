from __future__ import annotations

import typing as ty
from inspect import isfunction

import pygame as pg

from ..anchor import Anchor
from ..widget import BaseWidget

if ty.TYPE_CHECKING:
    from ..types import CordFunction
    from ..group import Group


class Label(BaseWidget):
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
        background: pg.Color | None = None,
        font: pg.font.Font = pg.font.Font(None, 20),
        anchor: Anchor = Anchor.left,
        border_color: pg.Color = pg.Color(255, 255, 255),
        border_width: int = 0,
    ):
        """
        Виджет однострочного текста.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
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
        :param background: Цвет фона.
        :param font: Шрифт.
        :param anchor: Привязка к краю или центру.
        :param border_color: Цвет обводки виджета.
        :param border_width: Ширина обводки.
        """
        if sprite is None and text is None:
            raise ValueError(
                "В Label должен быть передан хотя-бы 1 из параметров: text, sprite"
            )

        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._text = text
        self._sprite = sprite
        self._padding = padding
        self._color = color
        self._background = background
        self._font = font
        self._anchor = anchor
        self._border_color = border_color
        self._border_width = border_width

        self._rendered_text = self._render_text()

        super(Label, self).__init__(parent, name)

    def _get_rect(self) -> pg.Rect:
        self.rect = pg.Rect(
            0,
            0,
            self.padding * 2
            + (
                (
                    self._rendered_text.get_width()
                    if self.text is not None
                    else self.sprite.get_width()
                )
                if self.width is None or isfunction(self._width)
                else self.width
            )
            + self.border_width * 2,
            self.padding * 2
            + (
                (
                    self._rendered_text.get_height()
                    if self.text is not None
                    else self.sprite.get_height()
                )
                if self.height is None or isfunction(self._height)
                else self.height
            )
            + self.border_width * 2,
        )

        self.rect.width = self.width or self.rect.width
        self.rect.height = self.height or self.rect.height
        self.rect.x, self.rect.y = self.x, self.y
        return self.rect

    def _render(self) -> pg.Surface:
        image = pg.Surface(self.rect.size, pg.SRCALPHA, 32).convert_alpha()
        if self.background:
            pg.draw.rect(image, self.background, image.get_rect())
        if self.border_width:
            rect = image.get_rect().copy()
            rect.width -= int(self.border_width / 2)
            rect.height -= int(self.border_width / 2)
            pg.draw.rect(image, self._border_color, rect, self.border_width)
        if self.sprite:
            image.blit(source=self.sprite, dest=self.sprite.get_rect())
        if self.text:
            image.blit(
                source=self._rendered_text,
                dest=Anchor.prepare(
                    obj=self._rendered_text.get_rect(),
                    container=image.get_rect(),
                    anchor=self.anchor,
                    padding=self.padding + (self.border_width // 2),
                ),
            )

        return image

    def update(self, *args, **kwargs) -> None:
        self._rendered_text = self._render_text()
        super(Label, self).update(*args, **kwargs)

    def _render_text(self) -> pg.Surface:
        return self.font.render(self.text, True, self.color)

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
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    @property
    def sprite(self) -> pg.Surface:
        return self._sprite

    @sprite.setter
    def sprite(self, value: pg.Surface | None):
        self._sprite = value

    @property
    def padding(self) -> int:
        return self._padding

    @padding.setter
    def padding(self, value: int):
        self._padding = value

    @property
    def color(self) -> pg.Color:
        return self._color

    @color.setter
    def color(self, value: pg.Color):
        self._color = value

    @property
    def background(self) -> pg.Color:
        return self._background

    @background.setter
    def background(self, value: pg.Color):
        self._background = value

    @property
    def font(self) -> pg.font.Font:
        return self._font

    @font.setter
    def font(self, value: pg.font.Font):
        self._font = value

    @property
    def anchor(self) -> Anchor:
        return self._anchor

    @anchor.setter
    def anchor(self, value: Anchor):
        self._anchor = value

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
