from __future__ import annotations

import typing as ty
from enum import Enum

if ty.TYPE_CHECKING:
    import pygame as pg


class Anchor(Enum):
    """
    Привязка контента к краям или центу контейнера.
    """

    left = "left"
    right = "right"
    center = "center"

    @classmethod
    def prepare(
        cls, obj: pg.Rect, container: pg.Rect, anchor: Anchor, padding: None | int = 0
    ) -> tuple[int, int]:
        """
        Выполняет расчет координат объекта, учитывая атрибут anchor.
        :param obj: Объект, для которого высчитываются координаты.
        :param container: Контейнер, в который будет помещен объект.
        :param anchor: Привязка.
        :param padding: Отступы от краев контейнера.
        :return: Координаты объекта.
        """
        match anchor:
            case Anchor.left:
                x = container.x + padding
            case Anchor.center:
                x = container.x + round(container.width / 2) - round(obj.width / 2)
            case _:
                x = container.right - obj.width - padding

        y = container.y + round(container.height / 2) - round(obj.height / 2) + 1

        return x, y
