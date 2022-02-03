"""

Описание группы объектов.

"""

from __future__ import annotations

from abc import ABC

import pygame as pg
from loguru import logger

from .object import Object
from .widget import BaseWidget


class Group(Object, ABC):
    def __init__(
        self,
        parent: Group | None = None,
        name: str = None,
        *,
        hidden: True | False = False,
    ):
        """
        Группа объектов.
        :param parent: Объект, которому принадлежит данный объект.
        :param name: Название объекта.
        :param hidden: Будет ли группа скрыта.
        """
        Object.__init__(self, parent, name, hidden=hidden)

        self._objects: list[Object] = []

    def add(self, *objects: Object) -> None:
        """
        Добавляет объекты в группу.
        :param objects: Объекты.
        """
        for obj in objects:
            if isinstance(obj, Object):
                if obj not in self._objects:
                    logger.opt(colors=True).trace(f"adding {obj} to {self}")
                    obj.parent = self
                    self._objects.append(obj)
                    obj.update()
        parent = self
        while parent:
            if isinstance(parent, BaseWidget):
                BaseWidget.update(parent)
            else:
                parent.update()
            parent = parent.parent

    def remove(self, *objects: Object) -> None:
        """
        Удаляет объекты из группы.
        :param objects: Объекты.
        """
        for obj in objects:
            if obj in self._objects:
                logger.opt(colors=True).trace(f"removing {obj} from {self}")
                self._objects.remove(obj)
        self.update()

    def update(self, *args, **kwargs) -> None:
        """
        Обновляет все объекты в группе.
        """
        logger.opt(colors=True).trace(f"update {self}")
        for widget in self._objects:
            if not isinstance(widget, Group):
                widget.update(*args, **kwargs)

    def draw(self, surface: pg.Surface) -> None:
        """
        Отображает все виджеты, входящие в группу.
        :param surface: Поверхность.
        """
        if not self.hidden:
            for widget in self._objects:
                widget.draw(surface)

    def handle_event(self, event: pg.event.Event) -> None:
        """
        Отправляет событие всем виджетам в группе.
        :param event: Событие.
        """
        if self.enabled:
            for obj in self._objects:
                obj.handle_event(event)

    @property
    def objects(self) -> list[Object]:
        return self._objects
