"""

Описание базового объекта.

"""

from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod

if ty.TYPE_CHECKING:
    import pygame as pg
    from .group import Group


FIELDS = [
    "_x",
    "_y",
    "_width",
    "_height",
    "_text",
    "_sprite",
    "_padding",
    "_font",
    "_border_width",
    "_color",
    "_background",
    "_anchor",
    "_border_color",
    "_inactive_background",
    "_active_background",
]  # Атрибуты, которые может содержать объект


class Object(ABC):
    def __init__(self, parent: Group | None, *, hidden: True | False = False):
        """
        Базовый объект.
        :param parent: Объект, которому принадлежит данный объект.
        :param hidden: Будет ли объект скрыт.
        """

        self.__parent = parent
        self._hidden = hidden
        self._enabled = True  # Активен ли объект

        # Добавляем этот объект в группу.
        if parent is not None:
            parent.add(self)

    def show(self) -> None:
        """
        Снимает скрытие с объекта.
        """
        self._hidden = False

    def hide(self) -> None:
        """
        Скрывает объект.
        """
        self._hidden = True

    @property
    def hidden(self) -> True | False:
        return self._hidden

    def enable(self) -> None:
        """
        Включает объект.
        """
        self._enabled = True

    def disable(self) -> None:
        """
        Выключает объект.
        """
        self._enabled = False

    @property
    def enabled(self) -> True | False:
        return self._enabled

    @property
    def parent(self) -> Group | None:
        return self.__parent

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """
        Метод должен быть определен в классе-наследнике.
        Обновляет объект.
        """

    @abstractmethod
    def handle_event(self, event: pg.event.Event) -> None:
        """
        Метод должен быть определен в классе-наследнике.
        Обрабатывает событие.
        :param event: Событие.
        """

    @abstractmethod
    def draw(self, surface: pg.Surface) -> None:
        """
        Метод должен быть определен в классе-наследнике.
        Отображает объект.
        :param surface: Поверхность.
        """

    def __setattr__(self, key: str, value: ...) -> None:
        """
        Изменение атрибута объекта.
        :param key: Название атрибута.
        :param value: Новое значение.
        """
        # Если это 1 из атрибутов объекта
        if key in self.__dict__ and key in FIELDS:
            super(Object, self).__setattr__(key, value)
            self.update()  # Обновляем этот объект
            # Изменение влияет на другие объекты
            parent = self.parent
            while parent.parent is not None:
                parent = parent.parent
            parent.update()
            return
        super(Object, self).__setattr__(key, value)
