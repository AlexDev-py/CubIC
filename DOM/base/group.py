"""

Описание группы объектов.

"""

from __future__ import annotations

from abc import ABC

import pygame as pg

from .object import Object


class Group(Object, ABC):
    def __init__(self, parent: Group | None = None, *, hidden: True | False = False):
        """
        Группа объектов.
        :param parent: Объект, которому принадлежит данный объект.
        :param hidden: Будет ли группа скрыта.
        """
        Object.__init__(self, parent, hidden=hidden)

        self._widgets: list[Object] = []

    def add(self, *objects: Object) -> None:
        """
        Добавляет объекты в группу.
        :param objects: Объекты.
        """
        for widget in objects:
            if isinstance(widget, Object):
                if widget not in self._widgets:
                    self._widgets.append(widget)
                    if not isinstance(widget, Group):
                        self.update()  # Обновляем группу
                        if self.parent:
                            parent = self.parent
                            while parent.parent is not None:
                                parent = parent.parent
                            parent.update()

    def remove(self, obj: Object) -> None:
        """
        Удаляет объект из группы.
        :param obj: Объект.
        """
        if obj in self._widgets:
            self._widgets.remove(obj)

    def update(self, *args, **kwargs) -> None:
        """
        Обновляет все объекты в группе.
        """
        for widget in self._widgets:
            widget.update(*args, **kwargs)

    def draw(self, surface: pg.Surface) -> None:
        """
        Отображает все виджеты, входящие в группу.
        :param surface: Поверхность.
        """
        if not self.hidden:
            for widget in self._widgets:
                widget.draw(surface)

    def handle_event(self, event: pg.event.Event) -> None:
        """
        Отправляет событие всем виджетам в группе.
        :param event: Событие.
        """
        if self.enabled:
            for widget in self._widgets:
                widget.handle_event(event)

    @property
    def widgets(self) -> list[Object]:
        return self._widgets
