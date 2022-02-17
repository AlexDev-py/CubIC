from __future__ import annotations

import typing as ty

import pygame as pg
from loguru import logger

from .widgets_group import WidgetsGroup

if ty.TYPE_CHECKING:
    from ..types import CordFunction
    from ..group import Group


class Alert(WidgetsGroup):
    def __init__(
        self,
        parent: Group,
        name: str = None,
        *,
        parent_size: tuple[int, int],
        width: int | CordFunction | None = None,
        height: int | CordFunction | None = None,
        padding: int = 0,
        background: pg.Color | None = None,
        border_color: pg.Color = pg.Color(255, 255, 255),
        border_width: int = 0,
        fogging: int = 0,
    ):
        """
        Виджет диалогового окна.
        :param parent: Объект к которому принадлежит виджет.
        :type parent: Объект класса, родителем которого является Group.
        :param name: Название объекта.
        :param parent_size: Размеры родительского виджета
        :param width: Ширина виджета.
        :type width: Число или функция вычисляющая ширину.
        :param height: Высота виджета.
        :type height: Число или функция вычисляющая высоту.
        :param padding: Отступы от границ виджета.
        :param background: Цвет фона.
        :param border_color: Цвет обводки виджета.
        :param border_width: Ширина обводки.
        :param fogging: Затемнение фона.
        :type fogging: Целое число от 0 до 255.
        """
        if not (0 <= fogging <= 255):
            raise ValueError("fogging и transparency должны быть в отрезке от 0 до 255")

        self._tab = WidgetsGroup(
            parent,
            f"{name}-Tab",
            x=0,
            y=0,
            width=parent_size[0],
            height=parent_size[1],
            background=pg.Color(0, 0, 0, fogging),
            hidden=True,
        )
        self._tab.disable()

        super(Alert, self).__init__(
            self._tab,
            name,
            x=lambda obj: round(self._tab.rect.width / 2 - obj.rect.width / 2),
            y=lambda obj: round(self._tab.rect.height / 2 - obj.rect.height / 2),
            width=width,
            height=height,
            padding=padding,
            background=background,
            border_color=border_color,
            border_width=border_width,
        )

    def show(self) -> None:
        """
        Отображает диалоговее окно.
        """
        logger.opt(colors=True).debug(f"Диалог <y>{self}</y> открыт")
        self._tab.show()
        self._tab.enable()
        for widget in self._tab.parent.objects:
            if widget != self._tab:
                widget.disable()

    def hide(self) -> None:
        """
        Скрывает диалоговое окно.
        """
        logger.opt(colors=True).debug(f"Диалог <y>{self}</y> закрыт")
        self._tab.hide()
        for widget in self._tab.parent.objects:
            if widget != self._tab:
                widget.enable()
        self._tab.disable()
