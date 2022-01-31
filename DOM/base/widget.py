"""

Описание базового виджета.

"""

from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod

import pygame as pg
from loguru import logger

from .object import Object

if ty.TYPE_CHECKING:
    from .group import Group


class BaseWidget(Object, ABC):
    def __init__(
        self, parent: Group | None, name: str = None, *, hidden: True | False = False
    ):
        """
        Базовый виджет.
        :param parent: Объект, которому принадлежит данный объект.
        :param name: Название объекта.
        :param hidden: Будет ли виджет скрыт.
        """
        Object.__init__(self, parent, name, hidden=hidden)

        self.rect: pg.Rect = self._get_rect()
        self.image: pg.Surface = self._render()

    @abstractmethod
    def _get_rect(self) -> pg.Rect:
        """
        Метод должен быть определен в классе-наследнике.
        :return: Объект pg.Rect, описывающий геометрию виджета и его положение в группе.
        """

    @abstractmethod
    def _render(self) -> pg.Surface:
        """
        Метод должен быть определен в классе-наследнике.
        :return: Изображение виджета.
        """

    def update(self, *args, **kwargs) -> None:
        """
        Обновляет виджет.
        """
        logger.opt(colors=True).trace(f"update {self}")
        self.rect = self._get_rect()
        self.image = self._render()

    def handle_event(self, event: pg.event.Event) -> None:
        """
        Метод может быть определен в классе-наследнике.
        Обрабатывает событие.
        """
        pass

    def draw(self, surface: pg.Surface) -> None:
        """
        Отображает виджет.
        :param surface: Поверхность.
        """
        if not self.hidden:
            surface.blit(self.image, self.rect)

    def get_global_rect(self) -> pg.Rect:
        """
        :return: Экземпляр pg.Rect описывающий положение виджета в окне.
        """
        rect = self.rect.copy()
        if self.parent and hasattr(self.parent, "get_global_rect"):
            parent_rect: pg.Rect = self.parent.get_global_rect()
            padding = self.parent.padding if hasattr(self.parent, "padding") else 0
            border_width = (
                self.parent.border_width if hasattr(self.parent, "border_width") else 0
            )
            rect.x += parent_rect.x + padding + border_width
            rect.y += parent_rect.y + padding + border_width

        return rect
