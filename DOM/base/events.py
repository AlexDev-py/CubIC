"""

События, для общения между виджетами.

"""

from __future__ import annotations

import typing as ty
from dataclasses import dataclass
from inspect import isclass

import pygame as pg
from pygame.event import EventType

if ty.TYPE_CHECKING:
    from .widgets.button import Button


class BaseEvent:
    type: int = -1
    events: dict[ty.Type[BaseEvent], int] = {}
    # {<Класс события>: <тип события>, ...}

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Создание нового события.
        """
        if cls not in cls.events:
            if not len(cls.events):
                cls.events[cls] = pg.USEREVENT
            else:
                cls.events[cls] = max(cls.events.values()) + 1
            cls.type = cls.events[cls]

    def post(self) -> None:
        """
        Отправляет событие.
        """
        pg.event.post(pg.event.Event(self.type, self.__dict__))

    @classmethod
    def __eq__(cls, other: ...) -> True | False:
        """
        Сравнение экземпляра класса, с другим объектом.
        :param other: Другой объект.
        :return: True или False.
        """
        # Сравнение с числом
        if isinstance(other, int):
            return other == cls.type
        # Сравнение с событием
        elif isinstance(other, (EventType, BaseEvent)) or (
            isclass(other) and issubclass(other, BaseEvent)
        ):
            return other.type == cls.type
        return False


@dataclass(eq=False)
class ButtonClickEvent(BaseEvent):
    """
    Событие нажатия на кнопку.
    """

    obj: Button  # Нажатая кнопка
