from __future__ import annotations

import typing as ty

import pygame as pg

from .label import Label
from ..anchor import Anchor

if ty.TYPE_CHECKING:
    from ..types import CordFunction
    from ..group import Group


class Text(Label):
    def __init__(
        self,
        parent: Group,
        name: str = None,
        *,
        x: int | CordFunction,
        y: int | CordFunction,
        width: int,
        height: int | CordFunction | None = None,
        text: str | None = None,
        padding: int = 0,
        color: pg.Color = pg.Color(255, 255, 255),
        background: pg.Color | None = None,
        font: pg.font.Font = pg.font.Font(None, 20),
        anchor: Anchor = Anchor.left,
        border_color: pg.Color = pg.Color(255, 255, 255),
        border_width: int = 0,
        soft_split: True | False = False
    ):
        """
        Виджет многострочного текста.
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
        :param padding: Отступы от границ виджета.
        :param color: Цвет текста.
        :param background: Цвет фона.
        :param font: Шрифт.
        :param anchor: Привязка к краю или центру.
        :param border_color: Цвет обводки виджета.
        :param border_width: Ширина обводки.
        :param soft_split: True - Переносит текст не разрывая слова.
        """

        self._soft_split = soft_split
        super(Text, self).__init__(
            parent,
            name,
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            padding=padding,
            color=color,
            background=background,
            font=font,
            anchor=anchor,
            border_color=border_color,
            border_width=border_width,
        )

    def _render_text(self) -> pg.Surface:
        # Разделяет текст на строки, которые не выходят за рамку родительского виджета
        text = self.text.splitlines()
        lines = []
        for line in text:
            if self.font.size(line)[0] <= self.width:
                lines.append(self.font.render(line, True, self.color))
            else:
                if self._soft_split:
                    words = line.split()
                    _line = words[0]
                    for word in words[1:]:
                        if self.font.size(_line + " " + word)[0] > self.width:
                            lines.append(self.font.render(_line, True, self.color))
                            _line = ""
                        _line += " " + word
                        _line = _line.strip()
                    if len(_line):
                        lines.append(self.font.render(_line, True, self.color))
                else:
                    _line = line[0]
                    for char in line:
                        if self.font.size(_line + char)[0] > self.width:
                            lines.append(self.font.render(_line, True, self.color))
                            _line = ""
                        _line += char
                    if len(_line):
                        lines.append(self.font.render(_line, True, self.color))

        image = pg.Surface(
            (
                max(line.get_width() for line in lines),
                sum(line.get_height() for line in lines),
            )
        )
        y = 0
        for line in lines:
            x = Anchor.prepare(
                obj=line.get_rect(),
                container=image.get_rect(),
                anchor=self.anchor,
            )[0]
            image.blit(
                source=line,
                dest=(x, y),
            )
            y += line.get_height()

        return image
