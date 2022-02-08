from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod

if ty.TYPE_CHECKING:
    from ..player import Player


class BaseBoss(ABC):
    def __init__(self):
        self.hp = self.base_hp
        self.pos: tuple[int, int] = (0, 0)  # y, x

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return: Название класса.
        """

    @property
    @abstractmethod
    def base_hp(self) -> int:
        """
        :return: Базовое хп.
        """

    @abstractmethod
    def first_skill(
        self, field: list[list[True | False]], players: list[Player]
    ) -> None:
        pass

    @abstractmethod
    def second_skill(
        self, field: list[list[True | False]], players: list[Player]
    ) -> None:
        pass

    @abstractmethod
    def third_skill(
        self, field: list[list[True | False]], players: list[Player]
    ) -> None:
        pass

    @abstractmethod
    def fourth_skill(
        self, field: list[list[True | False]], players: list[Player]
    ) -> None:
        pass

    def hit(
        self, cords: list[tuple[int, int]], players: list[Player], damage: int
    ) -> None:
        for cord in cords:
            for player in [p for p in players if p.character.pos == cord]:
                player.character.on_hit(damage)

    def on_hit(self, damage: int) -> None:
        self.hp -= damage
