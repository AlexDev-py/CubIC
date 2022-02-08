from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod

if ty.TYPE_CHECKING:
    from ..items import Item


class FightingStyle:
    range_fight = "range"
    melee_fight = "melee"


class BaseCharacter(ABC):
    def __init__(self):
        self.items: list[Item | None] = [None] * 8
        self.coins = 0
        self.pos: tuple[int, int] = (0, 0)  # y, x

        self._calculate_additional_params()

        self.hp = self.max_hp

    def _calculate_additional_params(self) -> None:
        self.additional_damage: int = 0
        self.additional_attack_range: int = 0
        self.additional_max_hp: int = 0
        self.additional_armor: int = 0
        self.additional_move_speed: int = 0
        self.additional_life_abduction: int = 0
        for item in self.items:
            if item:
                for field, value in item.description.items():
                    self.__dict__[f"additional_{field}"] += int(value)

    def buy_item(self, item: Item) -> True | str:
        if None in self.items:
            if item.group is None or not any(
                item.group == (obj.group if obj else False) for obj in self.items
            ):
                if self.coins >= item.price:
                    self.coins -= item.price
                    self.items[self.items.index(None)] = item
                    if "max_hp" in item.description:
                        self.hp += int(item.description["max_hp"])
                    self._calculate_additional_params()
                    return True
                return "Недостаточно монет"
            return "У вас уже есть похожий предмет"
        return "Нет места в инвентаре"

    def remove_item(self, index: int) -> None:
        item = self.items[index]
        if item:
            self.coins += round(item.price / 2)
            self.items[index] = None

    def to_dict(self) -> dict:
        return dict(
            coins=self.coins,
            name=self.name,
            damage=self.damage,
            attack_range=self.attack_range,
            max_hp=self.max_hp,
            hp=self.hp,
            armor=self.armor,
            move_speed=self.move_speed,
            life_abduction=self.life_abduction,
            items=[(item.to_dict() if item else None) for item in self.items],
        )

    def on_hit(self, damage: int) -> None:
        damage -= self.armor
        if damage < 0:
            damage = 0

        self.hp -= damage

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return: Название класса.
        """

    @property
    @abstractmethod
    def fighting_style(self) -> str:
        """
        :return: Стиль боя. FightingStyle.
        """

    @property
    @abstractmethod
    def base_damage(self) -> int:
        """
        :return: Базовый урон
        """

    @property
    @abstractmethod
    def base_attack_range(self) -> int:
        """
        :return: Базовая дальность атаки.
        """

    @property
    @abstractmethod
    def base_max_hp(self) -> int:
        """
        :return: Базовое хп.
        """

    @property
    @abstractmethod
    def base_armor(self) -> int:
        """
        :return: Базовая броня.
        """

    @property
    @abstractmethod
    def base_move_speed(self) -> int:
        """
        :return: Базовая скорость перемещения.
        """

    @property
    @abstractmethod
    def base_life_abduction(self) -> int:
        """
        :return: Базовое вытягивание жизни
        """

    @property
    def damage(self) -> int:
        return self.base_damage + self.additional_damage

    @property
    def attack_range(self) -> int:
        return self.base_attack_range + self.additional_attack_range

    @property
    def max_hp(self) -> int:
        return self.base_max_hp + self.additional_max_hp

    @property
    def armor(self) -> int:
        return self.base_armor + self.additional_armor

    @property
    def move_speed(self) -> int:
        return self.base_move_speed + self.additional_move_speed

    @property
    def life_abduction(self) -> int:
        return self.base_life_abduction + self.additional_life_abduction
