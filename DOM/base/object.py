"""

Описание базового объекта.

"""

from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod

from loguru import logger

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
    def __init__(
        self,
        parent: Group | None,
        name: str = None,
        *,
        hidden: True | False = False,
    ):
        """
        Базовый объект.
        :param parent: Объект, которому принадлежит данный объект.
        :param name: Название объекта.
        :param hidden: Будет ли объект скрыт.
        """

        self._name = name
        self.__parent = parent
        self._hidden = hidden
        self._enabled = True  # Активен ли объект

        logger.opt(colors=True).trace(f"Инициализация {self}")

        # Добавляем этот объект в группу.
        if parent is not None:
            parent.add(self)

    def show(self) -> None:
        """
        Снимает скрытие с объекта.
        """
        self._hidden = False
        logger.opt(colors=True).trace(f"show {self}")

    def hide(self) -> None:
        """
        Скрывает объект.
        """
        self._hidden = True
        logger.opt(colors=True).trace(f"hide {self}")

    @property
    def hidden(self) -> True | False:
        return self._hidden

    def enable(self) -> None:
        """
        Включает объект.
        """
        self._enabled = True
        logger.opt(colors=True).trace(f"enable {self}")

    def disable(self) -> None:
        """
        Выключает объект.
        """
        self._enabled = False
        logger.opt(colors=True).trace(f"disable {self}")

    @property
    def enabled(self) -> True | False:
        return self._enabled

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str | None):
        logger.opt(colors=True).trace(f"{self} -> <c>{value}</c>")
        self._name = value

    @property
    def parent(self) -> Group | None:
        return self.__parent

    @parent.setter
    def parent(self, parent: Group | None):
        self.__parent = parent

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
            logger.opt(colors=True).trace(
                "{self} <le>{key}</le>=<y>{value}</y>", self=self, key=key, value=value
            )
            super(Object, self).__setattr__(key, value)
            (self.parent or self).update()
            return
        super(Object, self).__setattr__(key, value)

    def __repr__(self):
        return f"<y>{self.__class__.__name__}</y> - <c>{self.name}</c>"
