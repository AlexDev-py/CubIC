from __future__ import annotations

import math
import typing as ty
from dataclasses import dataclass
from inspect import isfunction

import pygame as pg

from base.events import BaseEvent
from base.group import Group
from base.widget import BaseWidget
from utils import load_image

if ty.TYPE_CHECKING:
    from base.types import CordFunction

    SpeedFunction = ty.Callable[[Dice], float]  # noqa


@dataclass(eq=False)
class DiceMovingStop(BaseEvent):
    """
    Событие остановки вращения кости.
    """

    obj: Dice


TOP = "top"
LEFT = "left"
FRONT = "front"
BACK = "back"
RIGHT = "right"
BOTTOM = "bottom"


class Dice(BaseWidget):
    def __init__(
        self,
        parent: Group | None,
        name: str = None,
        *,
        speed: float | SpeedFunction,
        x: int | CordFunction,
        y: int | CordFunction,
        width: int,
        files_namespace: str,
    ):
        """
        Виджет кости.
        Реализует визуализацию вращения кости.
        :param parent: Объект к которому принадлежит виджет.
        :param name: Название объекта.
        :param speed: Скорость вращения.
        :param x: Координата x.
        :type x: Число или функция вычисляющая координату.
        :param y: Координата y.
        :type y: Число или функция вычисляющая координату.
        :param width: Ширина виджета.
        :type width: Число или функция вычисляющая ширину.
        :param files_namespace: Окружение, в котором находятся изображения граней.
        """
        self._x = x
        self._y = y
        self._width = width
        self._speed = speed

        self.facets = [
            load_image(f"{i}.png", namespace=files_namespace, size=(width, width))
            for i in [1, 2, 3, 3, 2, 4]
        ]  # Изображения граней
        # Триггер движения
        # [True, False, False, False] - right move
        # [False, True, False, False] - left move
        # [False, False, True, False] - down move
        # [False, False, False, Top] - up move
        self.rotations_triggers = [False, False, False, False]
        self.counters = [0, 0]  # Показатели поворота

        self.graph = [
            [4, 1, 3, 2],
            [0, 5, 3, 2],
            [4, 1, 0, 5],
            [4, 1, 5, 0],
            [5, 0, 3, 2],
            [1, 4, 3, 2],
        ]
        self.visible_images = [0]
        self.move_stack = []  # Хранилище движений

        self.rect = self._get_rect()
        self._re_corners()
        self.visible_corners = [self.all_corners[0].copy()]
        self.image = self._render()

        self.in_move = False

        super(Dice, self).__init__(parent, name)

    def _restart(self) -> None:
        self.visible_images = [0]
        self.rotations_triggers = [False, False, False, False]
        self._re_corners()
        self.visible_corners = [self.all_corners[0].copy()]
        self.counters = [0, 0]
        self.move_stack.clear()

    def _re_corners(self) -> None:
        ul, ur, dl, dr = (
            [10, 10],
            [self.width + 10, 10],
            [10, self.width + 10],
            [self.width + 10, self.width + 10],
        )
        self.all_corners = [
            [ul.copy(), dl.copy(), dr.copy(), ur.copy()],
            [ul.copy(), dl.copy(), dl.copy(), ul.copy()],
            [ur.copy(), dr.copy(), dr.copy(), ur.copy()],
            [ul.copy(), ul.copy(), ur.copy(), ur.copy()],
            [dl.copy(), dl.copy(), dr.copy(), dr.copy()],
        ]

    def move_left(self) -> None:
        self.visible_corners.append(self.all_corners[2].copy())
        self.rotations_triggers[1] = True

    def move_right(self) -> None:
        self.visible_corners.append(self.all_corners[1].copy())
        self.rotations_triggers[0] = True

    def move_up(self) -> None:
        self.visible_corners.append(self.all_corners[4].copy())
        self.rotations_triggers[3] = True

    def move_down(self) -> None:
        self.visible_corners.append(self.all_corners[3].copy())
        self.rotations_triggers[2] = True

    def update(self) -> ty.Optional[True]:
        if not hasattr(self, "rotations_triggers"):
            return

        if self.rotations_triggers[0]:
            if self.counters[0] < self.width / 2:
                self.visible_corners[0][2][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][3][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][0][0] += 1 * self.speed
                self.visible_corners[0][1][0] += 1 * self.speed
                self.visible_corners[1][0][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][1][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][2][0] += 1 * self.speed
                self.visible_corners[1][3][0] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.width / 2 <= self.counters[0] < self.width:
                self.visible_corners[0][2][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][3][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][0][0] += 1 * self.speed
                self.visible_corners[0][1][0] += 1 * self.speed
                self.visible_corners[1][0][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][1][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][2][0] += 1 * self.speed
                self.visible_corners[1][3][0] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.width:
                self.rotations_triggers[0] = False
                self.visible_corners = self.visible_corners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._re_corners()
        elif self.rotations_triggers[1]:
            if self.counters[0] < self.width / 2:
                self.visible_corners[0][0][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][1][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][2][0] -= 1 * self.speed
                self.visible_corners[0][3][0] -= 1 * self.speed
                self.visible_corners[1][2][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][3][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][0][0] -= 1 * self.speed
                self.visible_corners[1][1][0] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.width / 2 <= self.counters[0] < self.width:
                self.visible_corners[0][0][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][1][0] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][2][0] -= 1 * self.speed
                self.visible_corners[0][3][0] -= 1 * self.speed
                self.visible_corners[1][2][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][3][0] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][0][0] -= 1 * self.speed
                self.visible_corners[1][1][0] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.width:
                self.rotations_triggers[1] = False
                self.visible_corners = self.visible_corners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._re_corners()
        elif self.rotations_triggers[2]:
            if self.counters[0] < self.width / 2:
                self.visible_corners[0][1][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][2][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][0][1] += 1 * self.speed
                self.visible_corners[0][3][1] += 1 * self.speed
                self.visible_corners[1][0][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][3][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][1][1] += 1 * self.speed
                self.visible_corners[1][2][1] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.width / 2 <= self.counters[0] < self.width:
                self.visible_corners[0][1][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][2][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][0][1] += 1 * self.speed
                self.visible_corners[0][3][1] += 1 * self.speed
                self.visible_corners[1][0][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][3][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][1][1] += 1 * self.speed
                self.visible_corners[1][2][1] += 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.width:
                self.rotations_triggers[2] = False
                self.visible_corners = self.visible_corners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._re_corners()
        elif self.rotations_triggers[3]:
            if self.counters[0] < self.width / 2:
                self.visible_corners[0][0][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][3][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][1][1] -= 1 * self.speed
                self.visible_corners[0][2][1] -= 1 * self.speed
                self.visible_corners[1][1][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][2][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][0][1] -= 1 * self.speed
                self.visible_corners[1][3][1] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.width / 2 <= self.counters[0] < self.width:
                self.visible_corners[0][0][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][3][1] += (math.sqrt(2) - 1) * self.speed
                self.visible_corners[0][1][1] -= 1 * self.speed
                self.visible_corners[0][2][1] -= 1 * self.speed
                self.visible_corners[1][1][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][2][1] -= (math.sqrt(2) - 1) * self.speed
                self.visible_corners[1][0][1] -= 1 * self.speed
                self.visible_corners[1][3][1] -= 1 * self.speed
                self.counters[0] += 1 * self.speed
            if self.counters[0] >= self.width:
                self.rotations_triggers[3] = False
                self.visible_corners = self.visible_corners[1::]
                self.visible_images = self.visible_images[1::]
                self.counters[0] = 0
                self._re_corners()
        elif (
            self.rotations_triggers == [False, False, False, False]
            and len(self.move_stack) > 0
        ):
            self.next_moving()

        if any(self.rotations_triggers):
            self.in_move = True
            super(Dice, self).update()
            return True

        if not len(self.move_stack):
            if self.in_move:
                self.in_move = False
                DiceMovingStop(self).post()

    def move_from_list(self, data: list[tuple[int, int]]) -> None:
        """
        Вращение кости по данным с сервера.
        :param data: Список команд.
        """
        self._restart()
        stacks = [
            [True, False, False, False],
            [False, True, False, False],
            [False, False, True, False],
            [False, False, False, True],
        ]

        self.move_stack = [[stacks[i[0]], i[1]] for i in data]

    def next_moving(self) -> None:
        current = self.move_stack.pop(0)
        self.visible_images.append(current[-1] - 1)
        current = current[0]
        if current[0]:
            self.move_right()
        if current[1]:
            self.move_left()
        if current[2]:
            self.move_down()
        if current[3]:
            self.move_up()

    def _get_rect(self) -> pg.Rect:
        self.rect = pg.Rect(0, 0, self.width + 20, self.width + 20)
        self.rect.x, self.rect.y = self.x, self.y
        return self.rect

    def _render(self) -> pg.Surface:
        image = pg.Surface(self.rect.size, pg.SRCALPHA, 32).convert_alpha()
        for i in range(len(self.visible_corners)):
            polygon = self.visible_corners[i]
            dsize = (
                round(abs(polygon[0][0] - polygon[2][0])) + 1,
                round(abs(polygon[0][1] - polygon[2][1])) + 1,
            )
            image.blit(
                pg.transform.scale(self.facets[self.visible_images[i]], dsize),
                polygon[0],
            )
        return image

    @property
    def speed(self) -> float:
        return self._speed(self) if isfunction(self._speed) else self._speed

    @speed.setter
    def speed(self, value: float | SpeedFunction):
        self._speed = value

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
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value
